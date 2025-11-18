# IR Note - 決算資料検索サービス

🔗 **公開URL**: https://ir-note.vercel.app

証券コードまたは企業名を入力すると、その企業の決算説明会資料・決算短信・有価証券報告書を検索できるWebアプリケーションです。

## 主な機能

- 📊 **証券コード・企業名検索**: 4桁の証券コードまたは企業名で検索可能
- 📈 **時価総額表示**: リアルタイムの時価総額情報を表示（yfinance API連携）
- ⭐ **お気に入り機能**: よく見る企業をお気に入りに登録（Supabase連携）
- 📱 **レスポンシブデザイン**: PC・スマホ・タブレット対応
- 🔍 **企業名サジェスト**: 企業名の入力時に候補を表示

## 技術スタック

### フロントエンド
- React 18
- TypeScript
- Vite
- CSS3

### バックエンド
- Python 3.12+
- Flask 3.0
- Flask-CORS
- Supabase (データベース)
- yfinance (時価総額取得)

### インフラ・デプロイ
- Vercel (ホスティング)
- GitHub (バージョン管理)

## デプロイ環境

本番環境は Vercel にデプロイされています：
- **URL**: https://ir-note.vercel.app
- **自動デプロイ**: `main` ブランチへのプッシュで自動デプロイ
- **環境変数**: Vercel Dashboard で `SUPABASE_URL` と `SUPABASE_KEY` を設定

## ローカル開発

### 必要な環境
- Node.js 18以上
- Python 3.12以上

### クイックスタート

```bash
# プロジェクトルートで実行
./start.sh
```

このスクリプトがバックエンド（Flask）とフロントエンド（Vite）を自動的に起動します。

- フロントエンド: http://localhost:5173
- バックエンド: http://localhost:5001

### バックエンドのセットアップ

```bash
cd backend

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# サーバーの起動
python app.py
```

バックエンドは `http://localhost:5001` で起動します。

### フロントエンドのセットアップ

```bash
cd frontend

# 依存パッケージのインストール
npm install

# 開発サーバーの起動
npm run dev
```

フロントエンドは `http://localhost:5173` で起動します。

## 使い方

1. https://ir-note.vercel.app にアクセス
2. 証券コード（例: 7203）または企業名（例: トヨタ）を入力
3. 検索結果として企業名、時価総額、決算資料一覧が表示されます
4. お気に入りボタンで企業を登録すると、次回から簡単にアクセスできます

## API エンドポイント

### GET /api/health
ヘルスチェック用エンドポイント

### GET /api/search?query={query}
企業名または証券コードで検索

**パラメータ:**
- `query`: 検索キーワード（企業名の一部または証券コード）

**レスポンス例:**
```json
{
  "results": [
    { "code": "7203", "name": "トヨタ自動車" },
    { "code": "9984", "name": "ソフトバンクグループ" }
  ]
}
```

### GET /api/earnings/:stock_code
指定された証券コードの決算資料を取得

**パラメータ:**
- `stock_code`: 4桁の証券コード（例: 7203）

### GET /api/market-cap/:stock_code
指定された証券コードの時価総額を取得

### GET /api/favorites
お気に入り企業一覧を取得

### POST /api/favorites
お気に入りに企業を追加

**リクエストボディ:**
```json
{
  "stock_code": "7203"
}
```

### DELETE /api/favorites/:stock_code
お気に入りから企業を削除

## プロジェクト構成

```
ir-note/
├── api/                          # Vercel Serverless Functions
│   ├── index.py                  # エントリーポイント（backend/app.pyをインポート）
│   ├── earnings_scraper.py       # 決算資料取得ロジック
│   ├── company_ir_urls.py        # 企業IR URLマッピング
│   ├── stock_master.json         # 株式マスターデータ
│   └── requirements.txt          # Python依存パッケージ
├── backend/                      # バックエンドロジック
│   ├── app.py                    # Flaskアプリケーション（メイン）
│   ├── earnings_scraper.py       # 決算資料スクレイピング
│   ├── stock_master.json         # 株式マスターデータ（ローカル用）
│   └── requirements.txt          # Python依存パッケージ
├── frontend/                     # フロントエンドアプリケーション
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchForm.tsx         # 検索フォーム
│   │   │   ├── SearchForm.css
│   │   │   ├── MaterialsList.tsx      # 資料一覧表示
│   │   │   └── MaterialsList.css
│   │   ├── types.ts                   # TypeScript型定義
│   │   ├── config.ts                  # API設定
│   │   ├── App.tsx                    # メインアプリ
│   │   ├── App.css
│   │   └── main.tsx
│   ├── index.html                     # HTMLテンプレート（メタタグ含む）
│   ├── package.json
│   └── vite.config.ts                 # Vite設定（プロキシ含む）
├── vercel.json                   # Vercelデプロイ設定
├── start.sh                      # ローカル起動スクリプト
└── README.md
```

## 実装済み機能

### ✅ コア機能
- 🔍 **証券コード・企業名検索**: Supabaseの株式マスターデータから検索
- 📊 **決算資料表示**: 過去5年分の決算資料を年度別・四半期別に表示
- 💰 **時価総額表示**: yfinance APIを使用してリアルタイム時価総額を取得
- ⭐ **お気に入り機能**: Supabaseにお気に入り企業を保存・管理
- 💡 **サジェスト機能**: 企業名入力時に候補を表示
- 📱 **レスポンシブデザイン**: PC・タブレット・スマホ対応

### 🏗️ インフラ・デプロイ
- ☁️ **Vercel本番環境**: https://ir-note.vercel.app で公開中
- 🗄️ **Supabase統合**: 株式マスターとお気に入りをクラウドで管理
- 🚀 **自動デプロイ**: GitHubのmainブランチへのプッシュで自動デプロイ
- 🔒 **SEO最適化**: メタタグ・OGP・Twitter Card対応

## 注意事項

- 現在表示されているURLは実際の企業IRページのパターンに基づいていますが、すべてが有効なリンクとは限りません
- 実際のスクレイピングを有効にする場合は、各サービスの利用規約を確認し、適切なレート制限を設けてください
- Webスクレイピングは各サイトの構造変更により動作しなくなる可能性があります

## ライセンス

MIT License

## 作者

© 2025 IR Note
