import { useState, useEffect, type FormEvent } from 'react'
import './SearchForm.css'
import { API_BASE_URL } from '../config'

interface SearchFormProps {
  onSearch: (stockCode: string) => void
  loading: boolean
  favorites?: Array<{stock_code: string, company_name: string}>
}

interface SearchResult {
  code: string
  name: string
}

export const SearchForm = ({ onSearch, loading, favorites = [] }: SearchFormProps) => {
  const [query, setQuery] = useState('')
  const [inputError, setInputError] = useState<string | null>(null)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  // 企業名検索のデバウンス
  useEffect(() => {
    if (!query || /^\d{1,4}$/.test(query)) {
      setSearchResults([])
      setShowSuggestions(false)
      return
    }

    const timer = setTimeout(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/search?query=${encodeURIComponent(query)}`)
        const data = await response.json()
        setSearchResults(data.results || [])
        setShowSuggestions(true)
      } catch (err) {
        console.error('検索エラー:', err)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setInputError(null)
    setShowSuggestions(false)

    // 入力バリデーション
    if (!query) {
      setInputError('証券コードまたは企業名を入力してください')
      return
    }

    // 証券コード（4桁の数字）の場合
    if (/^\d{4}$/.test(query)) {
      onSearch(query)
      return
    }

    // "企業名 (証券コード)" の形式から証券コードを抽出
    const codeMatch = query.match(/\((\d{4})\)/)
    if (codeMatch) {
      onSearch(codeMatch[1])
      return
    }

    // 企業名の場合は検索結果から最初の証券コードを使用
    if (searchResults.length > 0) {
      onSearch(searchResults[0].code)
    } else {
      setInputError('該当する企業が見つかりませんでした')
    }
  }

  const handleSelectSuggestion = (code: string, name: string) => {
    setQuery(`${name} (${code})`)
    setShowSuggestions(false)
  }

  // お気に入り企業を表示（最大4件）
  const examples = favorites.slice(0, 4).map(fav => ({
    code: fav.stock_code,
    name: fav.company_name
  }))

  return (
    <div className="search-form-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <label htmlFor="search-query">証券コードまたは企業名</label>
          <div className="search-input-wrapper">
            <input
              id="search-query"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="例: 7203 または トヨタ"
              disabled={loading}
              className={inputError ? 'input-error' : ''}
              autoComplete="off"
            />
            {showSuggestions && searchResults.length > 0 && (
              <div className="suggestions">
                {searchResults.map((result) => (
                  <div
                    key={result.code}
                    className="suggestion-item"
                    onClick={() => handleSelectSuggestion(result.code, result.name)}
                  >
                    {result.name} ({result.code})
                  </div>
                ))}
              </div>
            )}
          </div>
          {inputError && <span className="error-text">{inputError}</span>}
        </div>

        <button type="submit" disabled={loading || !query}>
          {loading ? '検索中...' : '検索'}
        </button>
      </form>

      {examples.length > 0 && (
        <div className="examples">
          <p>お気に入り企業:</p>
          <div className="example-buttons">
            {examples.map((example) => (
              <button
                key={example.code}
                onClick={() => {
                  onSearch(example.code)
                }}
                className="example-button"
                disabled={loading}
              >
                {example.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
