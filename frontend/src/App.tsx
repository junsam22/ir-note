import { useState, useEffect } from 'react'
import './App.css'
import { SearchForm } from './components/SearchForm'
import { MaterialsList } from './components/MaterialsList'
import type { EarningsMaterial } from './types'
import { API_BASE_URL } from './config'

function App() {
  const [materials, setMaterials] = useState<EarningsMaterial[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [companyName, setCompanyName] = useState<string>('')
  const [currentStockCode, setCurrentStockCode] = useState<string>('')
  const [favorites, setFavorites] = useState<Array<{stock_code: string, company_name: string}>>([])
  const [isFavorite, setIsFavorite] = useState(false)
  const [marketCap, setMarketCap] = useState<number | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)

  // 初回レンダリング時にお気に入りをロード
  useEffect(() => {
    loadFavorites()
  }, [])

  const loadFavorites = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/favorites`)
      if (!response.ok) {
        // エラー時は空配列を設定（お気に入り機能が使えない場合でもアプリは動作する）
        setFavorites([])
        return
      }
      const data = await response.json()
      setFavorites(data.favorites || [])
    } catch (err) {
      console.error('お気に入りの読み込みに失敗しました', err)
      // エラー時は空配列を設定
      setFavorites([])
    }
  }

  const toggleFavorite = async () => {
    if (!currentStockCode) return

    try {
      if (isFavorite) {
        // 削除
        await fetch(`${API_BASE_URL}/favorites/${currentStockCode}`, {
          method: 'DELETE'
        })
        setIsFavorite(false)
      } else {
        // 追加
        await fetch(`${API_BASE_URL}/favorites`, {
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
    console.log('🚀 handleSearch呼び出し:', stockCode, 'API_BASE_URL:', API_BASE_URL, '型:', typeof stockCode)
    
    if (!stockCode || typeof stockCode !== 'string') {
      console.error('❌ 無効なstockCode:', stockCode)
      setError('無効な証券コードです')
      return
    }
    
    setCurrentStockCode(stockCode)
    setLoading(true)
    setError(null)
    setMaterials([])
    setMarketCap(null)

    try {
      const earningsUrl = `${API_BASE_URL}/earnings/${stockCode}`
      const marketCapUrl = `${API_BASE_URL}/market-cap/${stockCode}`
      console.log('📡 APIリクエスト:', { earningsUrl, marketCapUrl })

      // 決算資料と時価総額を並行して取得
      let earningsResponse: Response
      let marketCapResponse: Response | null = null
      
      try {
        const responses = await Promise.allSettled([
          fetch(earningsUrl),
          fetch(marketCapUrl)
        ])
        
        // 決算資料のレスポンス
        if (responses[0].status === 'fulfilled') {
          earningsResponse = responses[0].value
        } else {
          const errorReason = responses[0].reason
          const errorMessage = errorReason instanceof Error 
            ? errorReason.message 
            : typeof errorReason === 'string' 
              ? errorReason 
              : 'ネットワークエラーまたはサーバーエラーが発生しました'
          console.error('❌ earnings API fetch error:', errorReason)
          throw new Error(`決算資料の取得に失敗しました: ${errorMessage}`)
        }
        
        // 時価総額のレスポンス（失敗しても続行）
        if (responses[1].status === 'fulfilled') {
          marketCapResponse = responses[1].value
        } else {
          console.warn('⚠️ market-cap API fetch error (無視):', responses[1].reason)
        }
      } catch (err) {
        console.error('❌ API fetch error:', err)
        throw err
      }

      console.log('📥 APIレスポンス:', {
        earningsStatus: earningsResponse.status,
        earningsOk: earningsResponse.ok,
        marketCapStatus: marketCapResponse?.status || 'N/A',
        marketCapOk: marketCapResponse?.ok || false
      })

      if (!earningsResponse.ok) {
        let errorMessage = '決算資料の取得に失敗しました'
        try {
          const errorData = await earningsResponse.json()
          errorMessage = errorData.error || errorMessage
          console.error('❌ 決算資料取得エラー:', errorData)
        } catch (parseError) {
          // JSONパースエラーの場合、ステータスコードから判断
          if (earningsResponse.status === 404) {
            errorMessage = '決算資料が見つかりませんでした'
          } else if (earningsResponse.status === 500) {
            errorMessage = 'サーバーエラーが発生しました。しばらく待ってから再度お試しください。'
          } else {
            errorMessage = `エラーが発生しました (ステータス: ${earningsResponse.status})`
          }
          console.error('❌ レスポンスパースエラー:', parseError, 'ステータス:', earningsResponse.status)
        }
        throw new Error(errorMessage)
      }

      const data = await earningsResponse.json()
      console.log('✅ 決算資料取得成功:', data.materials?.length, '件')
      setMaterials(data.materials)

      // 企業名を設定（最初の資料から取得）
      if (data.materials.length > 0) {
        setCompanyName(data.materials[0].company_name)
      }

      // 時価総額を設定
      if (marketCapResponse && marketCapResponse.ok) {
        try {
          const marketCapData = await marketCapResponse.json()
          setMarketCap(marketCapData.market_cap_oku)
        } catch (err) {
          console.warn('⚠️ 時価総額データのパースエラー:', err)
        }
      }

      // お気に入りに登録されているかチェック
      await loadFavorites()
      const isInFavorites = favorites.some(f => f.stock_code === stockCode)
      setIsFavorite(isInFavorites)
    } catch (err) {
      console.error('❌ 検索エラー:', err)
      console.error('❌ エラー詳細:', {
        message: err instanceof Error ? err.message : String(err),
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : typeof err
      })
      
      let errorMessage = '予期しないエラーが発生しました'
      if (err instanceof Error) {
        errorMessage = err.message
      } else if (typeof err === 'string') {
        errorMessage = err
      } else if (err && typeof err === 'object' && 'message' in err) {
        errorMessage = String(err.message)
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <button
          className="hamburger-menu"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="メニュー"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        <h1>IR Note</h1>
        <p>証券コードで決算説明会資料を検索</p>
      </header>

      {/* サイドメニュー */}
      <div className={`side-menu ${menuOpen ? 'open' : ''}`}>
        <div className="side-menu-overlay" onClick={() => setMenuOpen(false)}></div>
        <div className="side-menu-content">
          <div className="side-menu-header">
            <h2>メニュー</h2>
            <button className="close-button" onClick={() => setMenuOpen(false)}>×</button>
          </div>
          <div className="side-menu-body">
            <h3>お気に入り一覧</h3>
            {favorites.length === 0 ? (
              <p className="empty-message">お気に入りに登録された企業はありません</p>
            ) : (
              <ul className="favorites-menu-list">
                {favorites.map(fav => (
                  <li key={fav.stock_code}>
                    <button
                      onClick={() => {
                        setMenuOpen(false)
                        handleSearch(fav.stock_code)
                      }}
                    >
                      {fav.company_name}
                      <span className="stock-code">{fav.stock_code}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      <main className="app-main">
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
                <button
                  className={`favorite-button ${isFavorite ? 'active' : ''}`}
                  onClick={toggleFavorite}
                >
                  {isFavorite ? '★ お気に入り登録済み' : '☆ お気に入りに追加'}
                </button>
              </div>
            </div>
            <p className="results-count">
              {materials.length}件の資料が見つかりました
            </p>
            <MaterialsList materials={materials} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>©freakapp</p>
      </footer>
    </div>
  )
}

export default App
