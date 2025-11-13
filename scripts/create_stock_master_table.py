"""
Supabaseにstock_masterテーブルを作成するスクリプト
"""
import os
from supabase import create_client, Client

# Supabase接続情報
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lvlqrnrsnuxqmxqvfyjd.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2bHFybnJzbnV4cW14cXZmeWpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MjY5MjYsImV4cCI6MjA3ODQwMjkyNn0.S1krcgZVM0qiovk6ZxRSHaY3KLRWBfVw71h-qYwHnMw')

# マイグレーションSQL
MIGRATION_SQL = """
-- Enable trigram extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create stock_master table
CREATE TABLE IF NOT EXISTS stock_master (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(4) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(code)
);

-- Create index on code for faster lookups
CREATE INDEX IF NOT EXISTS idx_stock_master_code ON stock_master(code);

-- Create index on name for search functionality
CREATE INDEX IF NOT EXISTS idx_stock_master_name ON stock_master USING gin(name gin_trgm_ops);

-- Enable Row Level Security (RLS)
ALTER TABLE stock_master ENABLE ROW LEVEL SECURITY;

-- Create policy to allow read access for all (public data)
CREATE POLICY IF NOT EXISTS "Allow read access on stock_master" ON stock_master
    FOR SELECT
    USING (true);
"""

def create_table():
    """テーブルを作成"""
    print("Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("Executing migration SQL...")

    # Supabase Python SDKではDDL実行ができないため、
    # PostgRESTを使った実行やダッシュボードでの実行が必要
    print("\n⚠️  Supabase Python SDKではDDL（CREATE TABLE等）は実行できません。")
    print("\n以下のいずれかの方法でマイグレーションを実行してください：")
    print("\n【方法1】Supabaseダッシュボード（推奨）")
    print("1. https://supabase.com/dashboard/project/lvlqrnrsnuxqmxqvfyjd/sql/new を開く")
    print("2. 以下のSQLを貼り付けて実行\n")
    print(MIGRATION_SQL)
    print("\n【方法2】psqlコマンド")
    print("psql 'postgresql://postgres:[YOUR-PASSWORD]@db.lvlqrnrsnuxqmxqvfyjd.supabase.co:5432/postgres' < supabase/migrations/20250113_create_stock_master.sql")

    return 1

if __name__ == '__main__':
    create_table()
