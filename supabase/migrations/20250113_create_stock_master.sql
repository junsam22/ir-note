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

-- Enable trigram extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable Row Level Security (RLS)
ALTER TABLE stock_master ENABLE ROW LEVEL SECURITY;

-- Create policy to allow read access for all (public data)
CREATE POLICY "Allow read access on stock_master" ON stock_master
    FOR SELECT
    USING (true);

-- Create policy to allow insert/update for service role only
CREATE POLICY "Allow insert/update for service role" ON stock_master
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');
