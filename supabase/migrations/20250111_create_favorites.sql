-- Create favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(4) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stock_code)
);

-- Create index on stock_code for faster lookups
CREATE INDEX IF NOT EXISTS idx_favorites_stock_code ON favorites(stock_code);

-- Enable Row Level Security (RLS)
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (since we don't have authentication yet)
CREATE POLICY "Allow all operations on favorites" ON favorites
    FOR ALL
    USING (true)
    WITH CHECK (true);
