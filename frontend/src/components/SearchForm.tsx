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
    console.log('🔍 handleSubmit呼び出し:', { query, loading, searchResultsLength: searchResults.length })
    
    setInputError(null)
    setShowSuggestions(false)

    // 入力バリデーション
    if (!query) {
      console.log('❌ クエリが空です')
      setInputError('証券コードまたは企業名を入力してください')
      return
    }

    // 証券コード（4桁の数字）の場合
    if (/^\d{4}$/.test(query)) {
      console.log('✅ 証券コードで検索:', query, 'onSearch関数:', typeof onSearch)
      onSearch(query)
      return
    }

    // "企業名 (証券コード)" の形式から証券コードを抽出
    const codeMatch = query.match(/\((\d{4})\)/)
    if (codeMatch) {
      console.log('✅ 企業名から証券コードを抽出:', codeMatch[1])
      onSearch(codeMatch[1])
      return
    }

    // 企業名の場合は検索結果から最初の証券コードを使用
    if (searchResults.length > 0) {
      console.log('✅ 検索結果から証券コードを使用:', searchResults[0].code)
      onSearch(searchResults[0].code)
    } else {
      console.log('❌ 検索結果が見つかりません。企業名検索を実行します。')
      // 企業名の場合は検索APIを呼び出す
      const searchUrl = `${API_BASE_URL}/search?query=${encodeURIComponent(query)}`
      console.log('📡 検索API呼び出し:', searchUrl)
      
      fetch(searchUrl)
        .then(response => {
          console.log('📥 検索APIレスポンス:', response.status, response.statusText)
          if (!response.ok) {
            throw new Error(`検索APIエラー: ${response.status} ${response.statusText}`)
          }
          return response.json()
        })
        .then(data => {
          console.log('📊 検索APIデータ:', data)
          if (data.results && data.results.length > 0) {
            console.log('✅ 検索APIから結果を取得:', data.results[0])
            onSearch(data.results[0].code)
          } else {
            console.log('❌ 検索結果が見つかりませんでした')
            setInputError('該当する企業が見つかりませんでした')
          }
        })
        .catch(err => {
          console.error('❌ 検索APIエラー:', err)
          const errorMessage = err instanceof Error 
            ? err.message 
            : typeof err === 'string' 
              ? err 
              : '検索中にエラーが発生しました'
          setInputError(`検索中にエラーが発生しました: ${errorMessage}`)
        })
    }
  }

  const handleSelectSuggestion = (code: string, name: string) => {
    setQuery(`${name} (${code})`)
    setShowSuggestions(false)
  }

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
    </div>
  )
}
