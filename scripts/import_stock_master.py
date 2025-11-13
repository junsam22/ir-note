"""
株式マスターデータをSupabaseにインポートするスクリプト

使用方法:
    python scripts/import_stock_master.py

環境変数:
    SUPABASE_SERVICE_KEY: Supabase Service Role Key（推奨）
    または SUPABASE_KEY: Supabase Anon Key
"""
import json
import os
import sys
from supabase import create_client, Client

# 環境変数からSupabase接続情報を取得
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lvlqrnrsnuxqmxqvfyjd.supabase.co')

# Service Roleキーを優先的に使用（RLSをバイパスできる）
SUPABASE_KEY = os.getenv(
    'SUPABASE_SERVICE_KEY',
    os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2bHFybnJzbnV4cW14cXZmeWpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MjY5MjYsImV4cCI6MjA3ODQwMjkyNn0.S1krcgZVM0qiovk6ZxRSHaY3KLRWBfVw71h-qYwHnMw')
)

def import_stock_master():
    """株式マスターデータをSupabaseにインポート"""

    # Supabaseクライアントを初期化
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # JSONファイルを読み込む
    json_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'stock_master.json')

    print(f"Loading stock master data from: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        stock_data = json.load(f)

    print(f"Found {len(stock_data)} stocks to import")

    # バッチサイズ（Supabaseの制限に合わせる）
    batch_size = 1000
    total_imported = 0
    errors = []

    # バッチごとにインポート
    for i in range(0, len(stock_data), batch_size):
        batch = stock_data[i:i + batch_size]

        try:
            # upsertを使用して、既存データがある場合は更新
            response = supabase.table('stock_master').upsert(
                batch,
                on_conflict='code'
            ).execute()

            total_imported += len(batch)
            print(f"Imported batch {i//batch_size + 1}: {total_imported}/{len(stock_data)} stocks")

        except Exception as e:
            error_msg = f"Error importing batch {i//batch_size + 1}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)

    print(f"\n✅ Import completed!")
    print(f"Total imported: {total_imported}/{len(stock_data)} stocks")

    if errors:
        print(f"\n⚠️  Errors encountered:")
        for error in errors:
            print(f"  - {error}")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(import_stock_master())
