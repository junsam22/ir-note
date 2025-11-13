"""
Supabaseにstock_masterテーブルを作成するスクリプト（REST API経由）
"""
import os
import requests

# Supabase接続情報
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lvlqrnrsnuxqmxqvfyjd.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2bHFybnJzbnV4cW14cXZmeWpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MjY5MjYsImV4cCI6MjA3ODQwMjkyNn0.S1krcgZVM0qiovk6ZxRSHaY3KLRWBfVw71h-qYwHnMw')

# マイグレーションSQLを読み込む
migration_file = os.path.join(os.path.dirname(__file__), '..', 'supabase', 'migrations', '20250113_create_stock_master.sql')

def run_migration():
    """マイグレーションを実行"""

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Migration SQL:")
    print(sql)
    print("\n" + "="*60)

    # Supabase REST APIではSQLを直接実行できないため、
    # PostgreSQL関数を経由するか、ダッシュボードで実行する必要がある

    print("\n⚠️  SupabaseのREST APIではDDL（CREATE TABLE等）を直接実行できません。")
    print("\n以下の方法でマイグレーションを実行してください：")
    print("\n【推奨】Supabaseダッシュボード")
    print("1. https://supabase.com/dashboard/project/lvlqrnrsnuxqmxqvfyjd/sql/new を開く")
    print("2. 上記のSQLを貼り付けて実行ボタンをクリック")
    print("\nまたは、ブラウザで以下を開いてSQLを実行してください：")
    print(f"https://supabase.com/dashboard/project/lvlqrnrsnuxqmxqvfyjd/sql/new")

    return 0

if __name__ == '__main__':
    run_migration()
