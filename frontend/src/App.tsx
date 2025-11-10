import { useState, useEffect } from 'react'
import './App.css'
import { SearchForm } from './components/SearchForm'
import { MaterialsList } from './components/MaterialsList'
import type { EarningsMaterial } from './types'

function App() {
  const [materials, setMaterials] = useState<EarningsMaterial[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [companyName, setCompanyName] = useState<string>('')
  const [currentStockCode, setCurrentStockCode] = useState<string>('')
  const [showFavorites, setShowFavorites] = useState(false)
  const [favorites, setFavorites] = useState<Array<{stock_code: string, company_name: string}>>([])
  const [isFavorite, setIsFavorite] = useState(false)
  const [marketCap, setMarketCap] = useState<number | null>(null)

  // 初回レンダリング時にお気に入りをロード
  useEffect(() => {
    loadFavorites()
  }, [])

  const loadFavorites = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/favorites')
      const data = await response.json()
      setFavorites(data.favorites || [])
    } catch (err) {
      console.error('お気に入りの読み込みに失敗しました', err)
    }
  }

  const toggleFavorite = async () => {
    if (!currentStockCode) return

    try {
      if (isFavorite) {
        // 削除
        await fetch(`http://localhost:5001/api/favorites/${currentStockCode}`, {
          method: 'DELETE'
        })
        setIsFavorite(false)
      } else {
        // 追加
        await fetch('http://localhost:5001/api/favorites', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ stock_code: currentStockCode })
        })
        setIsFavorite(true)
      }
      loadFavorites()
    } catch (err) {
      console.error('お気に入りの更新に失敗しました', err)
    }
  }

  const handleSearch = async (stockCode: string) => {
    setCurrentStockCode(stockCode)
    setLoading(true)
    setError(null)
    setMaterials([])
    setMarketCap(null)

    try {
      // 決算資料と時価総額を並行して取得
      const [earningsResponse, marketCapResponse] = await Promise.all([
        fetch(`http://localhost:5001/api/earnings/${stockCode}`),
        fetch(`http://localhost:5001/api/market-cap/${stockCode}`)
      ])

      if (!earningsResponse.ok) {
        const errorData = await earningsResponse.json()
        throw new Error(errorData.error || '決算資料の取得に失敗しました')
      }

      const data = await earningsResponse.json()
      setMaterials(data.materials)

      // 企業名を設定（最初の資料から取得）
      if (data.materials.length > 0) {
        setCompanyName(data.materials[0].company_name)
      }

      // 時価総額を設定
      if (marketCapResponse.ok) {
        const marketCapData = await marketCapResponse.json()
        setMarketCap(marketCapData.market_cap_oku)
      }

      // お気に入りに登録されているかチェック
      await loadFavorites()
      const isInFavorites = favorites.some(f => f.stock_code === stockCode)
      setIsFavorite(isInFavorites)
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期しないエラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📊 IR Note</h1>
        <p>証券コードで決算説明会資料を検索</p>
      </header>

      <main className="app-main">
        {showFavorites ? (
          <div className="favorites-list">
            <h2>お気に入り企業</h2>
            {favorites.length === 0 ? (
              <p>お気に入りに登録された企業はありません</p>
            ) : (
              <div className="favorites-grid">
                {favorites.map(fav => (
                  <div key={fav.stock_code} className="favorite-item">
                    <h3>{fav.company_name}</h3>
                    <button onClick={() => {
                      setShowFavorites(false)
                      handleSearch(fav.stock_code)
                    }}>
                      資料を見る
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            <SearchForm onSearch={handleSearch} loading={loading} favorites={favorites} />

            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}

            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>資料を取得中...</p>
              </div>
            )}

            {!loading && materials.length > 0 && (
              <div className="results">
                <div className="results-header">
                  <div className="company-info">
                    <h2>{companyName}</h2>
                    {marketCap && (
                      <p className="market-cap">
                        時価総額: {marketCap.toLocaleString()}億円
                      </p>
                    )}
                  </div>
                  <button
                    className={`favorite-button ${isFavorite ? 'active' : ''}`}
                    onClick={toggleFavorite}
                  >
                    {isFavorite ? '★ お気に入り登録済み' : '☆ お気に入りに追加'}
                  </button>
                </div>
                <p className="results-count">
                  {materials.length}件の資料が見つかりました
                </p>
                <MaterialsList materials={materials} />
              </div>
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2025 IR Note - 決算資料検索サービス</p>
      </footer>
    </div>
  )
}

export default App
