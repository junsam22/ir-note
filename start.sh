#!/bin/bash

# IR Note ローカル起動スクリプト

echo "🚀 IR Note を起動します..."

# バックエンドの起動
echo "📦 バックエンドを起動中..."
cd backend
if [ ! -d "venv" ]; then
    echo "仮想環境が見つかりません。作成します..."
    python3 -m venv venv
fi

source venv/bin/activate

# 依存パッケージのインストール確認
if ! python -c "import flask" 2>/dev/null; then
    echo "依存パッケージをインストール中..."
    pip install -r requirements.txt
fi

# バックエンドをバックグラウンドで起動（ポート5001を使用）
PORT=5001 python app.py &
BACKEND_PID=$!
echo "✅ バックエンドが起動しました (PID: $BACKEND_PID)"
echo "   バックエンド: http://localhost:5001"

# フロントエンドの起動
echo "🎨 フロントエンドを起動中..."
cd ../frontend

# 依存パッケージのインストール確認
if [ ! -d "node_modules" ]; then
    echo "依存パッケージをインストール中..."
    npm install
fi

# フロントエンドを起動
echo "✅ フロントエンドが起動しました"
echo "   フロントエンド: http://localhost:5173"
echo ""
echo "⚠️  終了するには Ctrl+C を押してください"

# シグナルハンドラー
trap "echo ''; echo '🛑 サーバーを停止しています...'; kill $BACKEND_PID 2>/dev/null; exit" INT TERM

# フロントエンドをフォアグラウンドで起動（これによりスクリプトが実行中になる）
npm run dev

