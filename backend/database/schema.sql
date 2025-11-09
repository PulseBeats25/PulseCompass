-- PulseCompass Database Schema for Supabase
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Users table
CREATE TABLE users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Companies table
CREATE TABLE companies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    sector VARCHAR(100),
    market_cap BIGINT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transcripts table with embeddings
CREATE TABLE transcripts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    quarter VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    raw_text TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI embedding dimension
    summary JSONB,
    integrity_score INTEGER CHECK (integrity_score >= 0 AND integrity_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, quarter, year)
);

-- Financial data table
CREATE TABLE financials (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    period TIMESTAMP WITH TIME ZONE NOT NULL,
    raw_data JSONB NOT NULL,
    metrics JSONB NOT NULL,
    traffic_lights JSONB NOT NULL,
    -- Key metrics as separate columns for easier querying
    revenue DECIMAL(15,2),
    net_profit DECIMAL(15,2),
    eps DECIMAL(10,2),
    roe DECIMAL(5,2),
    roce DECIMAL(5,2),
    debt_equity DECIMAL(5,2),
    pe_ratio DECIMAL(8,2),
    ev_ebitda DECIMAL(8,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, period)
);

-- Portfolio table
CREATE TABLE portfolio (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    buy_price DECIMAL(10,2) NOT NULL CHECK (buy_price > 0),
    buy_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, company_id)
);

-- Watchlist table
CREATE TABLE watchlist (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, company_id)
);

-- Analysis results table
CREATE TABLE analysis_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL, -- 'transcript', 'financial', 'combined'
    investor_views JSONB,
    recommendation JSONB,
    valuation JSONB,
    risk_factors JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_transcripts_company_id ON transcripts(company_id);
CREATE INDEX idx_transcripts_embedding ON transcripts USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_financials_company_id ON financials(company_id);
CREATE INDEX idx_financials_period ON financials(period DESC);
CREATE INDEX idx_portfolio_user_id ON portfolio(user_id);
CREATE INDEX idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX idx_analysis_company_id ON analysis_results(company_id);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Portfolio policies
CREATE POLICY "Users can view own portfolio" ON portfolio
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own portfolio" ON portfolio
    FOR ALL USING (auth.uid() = user_id);

-- Watchlist policies
CREATE POLICY "Users can view own watchlist" ON watchlist
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own watchlist" ON watchlist
    FOR ALL USING (auth.uid() = user_id);

-- Public read access for companies, transcripts, financials, and analysis
CREATE POLICY "Public read access for companies" ON companies
    FOR SELECT USING (true);

CREATE POLICY "Public read access for transcripts" ON transcripts
    FOR SELECT USING (true);

CREATE POLICY "Public read access for financials" ON financials
    FOR SELECT USING (true);

CREATE POLICY "Public read access for analysis" ON analysis_results
    FOR SELECT USING (true);

-- Functions for semantic search
CREATE OR REPLACE FUNCTION match_transcripts(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.78,
    match_count INT DEFAULT 5,
    company_filter UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    company_id UUID,
    quarter VARCHAR,
    year INTEGER,
    summary JSONB,
    integrity_score INTEGER,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.company_id,
        t.quarter,
        t.year,
        t.summary,
        t.integrity_score,
        1 - (t.embedding <=> query_embedding) AS similarity
    FROM transcripts t
    WHERE 
        (company_filter IS NULL OR t.company_id = company_filter)
        AND 1 - (t.embedding <=> query_embedding) > match_threshold
    ORDER BY t.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Insert sample data
INSERT INTO companies (name, ticker, sector) VALUES
    ('Exicom Tele-Systems Limited', 'EXICOM', 'Technology'),
    ('Kaynes Technology India Limited', 'KAYNES', 'Technology');

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transcripts_updated_at BEFORE UPDATE ON transcripts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financials_updated_at BEFORE UPDATE ON financials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolio_updated_at BEFORE UPDATE ON portfolio
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_updated_at BEFORE UPDATE ON analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
