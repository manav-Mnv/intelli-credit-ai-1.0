-- IntelliCredit AI — Supabase Schema
-- Run this in the Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT NOT NULL,
    industry TEXT,
    registration_number TEXT,
    cin TEXT,
    pan TEXT,
    address TEXT,
    website TEXT,
    contact_email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_type TEXT,
    file_size_bytes BIGINT,
    storage_path TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status TEXT DEFAULT 'uploaded',
    -- Status: uploaded | processing | completed | failed
    error_message TEXT,
    extracted_text TEXT,
    page_count INT
);

-- Financials table
CREATE TABLE IF NOT EXISTS financials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id),
    fiscal_year INT,
    revenue NUMERIC(20, 2),
    net_profit NUMERIC(20, 2),
    gross_profit NUMERIC(20, 2),
    ebitda NUMERIC(20, 2),
    total_debt NUMERIC(20, 2),
    total_equity NUMERIC(20, 2),
    total_assets NUMERIC(20, 2),
    total_liabilities NUMERIC(20, 2),
    current_assets NUMERIC(20, 2),
    current_liabilities NUMERIC(20, 2),
    cash_and_equivalents NUMERIC(20, 2),
    interest_expense NUMERIC(20, 2),
    -- Computed ratios
    debt_equity_ratio NUMERIC(10, 4),
    profit_margin NUMERIC(10, 4),
    current_ratio NUMERIC(10, 4),
    interest_coverage NUMERIC(10, 4),
    roe NUMERIC(10, 4),
    roce NUMERIC(10, 4),
    revenue_growth NUMERIC(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Risk scores table
CREATE TABLE IF NOT EXISTS risk_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    -- Component scores (0-100)
    financial_score NUMERIC(5, 2),
    ml_score NUMERIC(5, 2),
    nlp_score NUMERIC(5, 2),
    research_score NUMERIC(5, 2),
    -- Final
    overall_risk_score NUMERIC(5, 2),
    risk_grade TEXT,   -- Low | Medium | High | Critical
    default_probability NUMERIC(5, 4),
    risk_factors JSONB,  -- array of detected risk factors
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Research reports table
CREATE TABLE IF NOT EXISTS research_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    news_summary TEXT,
    news_risk_level TEXT,  -- Low | Medium | High
    news_articles JSONB,
    litigation_summary TEXT,
    litigation_risk_level TEXT,
    litigation_cases JSONB,
    industry_summary TEXT,
    industry_risk_level TEXT,
    industry_trends JSONB,
    overall_sentiment NUMERIC(5, 4),  -- -1 to 1
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CAM reports table
CREATE TABLE IF NOT EXISTS cam_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    -- Decision
    decision TEXT,           -- Approve | Approve with Conditions | Reject
    risk_score NUMERIC(5, 2),
    recommended_loan_amount NUMERIC(20, 2),
    interest_rate NUMERIC(5, 2),
    loan_tenor_months INT,
    -- Report sections
    executive_summary TEXT,
    company_overview TEXT,
    financial_analysis TEXT,
    risk_assessment TEXT,
    industry_outlook TEXT,
    loan_recommendation TEXT,
    conditions TEXT,
    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analyst_name TEXT DEFAULT 'IntelliCredit AI'
);

-- Row Level Security (optional, enable for production)
-- ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_company_id ON documents(company_id);
CREATE INDEX IF NOT EXISTS idx_financials_company_id ON financials(company_id);
CREATE INDEX IF NOT EXISTS idx_risk_scores_company_id ON risk_scores(company_id);
CREATE INDEX IF NOT EXISTS idx_research_reports_company_id ON research_reports(company_id);
CREATE INDEX IF NOT EXISTS idx_cam_reports_company_id ON cam_reports(company_id);
