-- =====================================================
-- ORION (Operational Risk and Investment Optimization Network)
-- MySQL Database Schema
-- =====================================================


-- Drop database if exists (BE CAREFUL IN PRODUCTION!)
DROP DATABASE IF EXISTS stock_risk_db;

-- Create database
CREATE DATABASE stock_risk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE stock_risk_db;

-- =====================================================
-- Table: users
-- Stores user authentication and profile information
-- =====================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    risk_profile ENUM('Conservative', 'Moderate', 'Aggressive') DEFAULT 'Moderate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    terms_accepted BOOLEAN DEFAULT FALSE,
    terms_accepted_at TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- =====================================================
-- Table: portfolios
-- Stores portfolio information for each user
-- =====================================================
CREATE TABLE portfolios (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    portfolio_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- =====================================================
-- Table: holdings
-- Stores individual stock holdings in each portfolio
-- =====================================================
CREATE TABLE holdings (
    holding_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    quantity DECIMAL(15, 4) NOT NULL,
    purchase_price DECIMAL(15, 2) NOT NULL,
    purchase_date DATE NOT NULL,
    current_price DECIMAL(15, 2),
    asset_type ENUM('Equity', 'Debt', 'Cash', 'Other') DEFAULT 'Equity',
    sector VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_stock_symbol (stock_symbol)
) ENGINE=InnoDB;

-- =====================================================
-- Table: stock_metrics
-- Stores calculated risk metrics for stocks
-- =====================================================
CREATE TABLE stock_metrics (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(20) NOT NULL,
    calculation_date DATE NOT NULL,
    
    -- Price and Return Metrics
    current_price DECIMAL(15, 2),
    daily_return DECIMAL(10, 6),
    weekly_return DECIMAL(10, 6),
    monthly_return DECIMAL(10, 6),
    annual_return DECIMAL(10, 6),
    
    -- Risk Metrics
    volatility DECIMAL(10, 6),
    annualized_volatility DECIMAL(10, 6),
    max_drawdown DECIMAL(10, 6),
    risk_level ENUM('Low', 'Medium', 'High'),
    
    -- Fundamental Metrics (Simplified)
    market_cap DECIMAL(20, 2),
    pe_ratio DECIMAL(10, 2),
    debt_to_equity DECIMAL(10, 2),
    fundamental_score DECIMAL(5, 2),
    
    -- AI/ML Metrics
    risk_reward_ratio DECIMAL(10, 4),
    loss_probability DECIMAL(5, 4),
    confidence_score DECIMAL(5, 4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_symbol_date (stock_symbol, calculation_date),
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_calculation_date (calculation_date)
) ENGINE=InnoDB;

-- =====================================================
-- Table: portfolio_metrics
-- Stores calculated risk metrics for entire portfolios
-- =====================================================
CREATE TABLE portfolio_metrics (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    calculation_date DATE NOT NULL,
    
    -- Portfolio Risk Metrics
    portfolio_volatility DECIMAL(10, 6),
    portfolio_return DECIMAL(10, 6),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 6),
    
    -- Diversification Metrics
    diversification_score DECIMAL(5, 2),
    correlation_risk DECIMAL(5, 4),
    concentration_risk DECIMAL(5, 4),
    
    -- Asset Allocation
    equity_percentage DECIMAL(5, 2),
    debt_percentage DECIMAL(5, 2),
    cash_percentage DECIMAL(5, 2),
    
    -- Portfolio Health
    health_score DECIMAL(5, 2),
    risk_score DECIMAL(5, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    UNIQUE KEY unique_portfolio_date (portfolio_id, calculation_date),
    INDEX idx_portfolio_id (portfolio_id)
) ENGINE=InnoDB;

-- =====================================================
-- Table: ai_recommendations
-- Stores AI-generated recommendations with explanations
-- =====================================================
CREATE TABLE ai_recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    recommendation_type ENUM('Buy', 'Hold', 'Sell') NOT NULL,
    confidence_level DECIMAL(5, 4),
    
    -- Explainable AI Fields
    reasoning TEXT NOT NULL,
    risk_factors TEXT,
    opportunity_factors TEXT,
    
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_recommendation_date (recommendation_date)
) ENGINE=InnoDB;

-- =====================================================
-- Table: market_sentiment
-- Stores sentiment analysis results
-- =====================================================
CREATE TABLE market_sentiment (
    sentiment_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(20) NOT NULL,
    analysis_date DATE NOT NULL,
    
    -- Sentiment Scores
    sentiment_score DECIMAL(5, 4),
    sentiment_label ENUM('Positive', 'Neutral', 'Negative'),
    
    -- News Analysis
    news_headline TEXT,
    news_source VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_analysis_date (analysis_date)
) ENGINE=InnoDB;

-- =====================================================
-- Table: audit_log
-- Stores system activity logs
-- =====================================================
CREATE TABLE audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action_type VARCHAR(50) NOT NULL,
    action_description TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- =====================================================
-- Insert Sample Data for Testing
-- =====================================================

-- Sample user (password: 'test123' - hashed with bcrypt)
-- Note: In production, use proper password hashing in application
INSERT INTO users (username, email, password_hash, full_name, risk_profile) VALUES
('demo_user', 'demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5XKM.zY8Cxvci', 'Demo User', 'Moderate');

-- Sample portfolio
INSERT INTO portfolios (user_id, portfolio_name, description) VALUES
(1, 'My Investment Portfolio', 'Diversified portfolio for long-term growth');

-- Sample holdings
INSERT INTO holdings (portfolio_id, stock_symbol, stock_name, quantity, purchase_price, purchase_date, asset_type, sector) VALUES
(1, 'RELIANCE.NS', 'Reliance Industries', 10, 2450.00, '2024-01-15', 'Equity', 'Energy'),
(1, 'TCS.NS', 'Tata Consultancy Services', 5, 3500.00, '2024-02-20', 'Equity', 'IT'),
(1, 'HDFCBANK.NS', 'HDFC Bank', 15, 1600.00, '2024-03-10', 'Equity', 'Finance'),
(1, 'INFY.NS', 'Infosys', 8, 1450.00, '2024-04-05', 'Equity', 'IT');

-- =====================================================
-- Useful Views
-- =====================================================

-- View: Portfolio Summary
CREATE VIEW v_portfolio_summary AS
SELECT 
    p.portfolio_id,
    p.user_id,
    p.portfolio_name,
    COUNT(h.holding_id) AS total_holdings,
    SUM(h.quantity * h.purchase_price) AS total_invested,
    SUM(h.quantity * COALESCE(h.current_price, h.purchase_price)) AS current_value
FROM portfolios p
LEFT JOIN holdings h ON p.portfolio_id = h.portfolio_id
WHERE p.is_active = TRUE
GROUP BY p.portfolio_id, p.user_id, p.portfolio_name;

-- View: User Risk Profile Summary
CREATE VIEW v_user_risk_summary AS
SELECT 
    u.user_id,
    u.username,
    u.risk_profile,
    COUNT(DISTINCT p.portfolio_id) AS total_portfolios,
    COUNT(h.holding_id) AS total_holdings
FROM users u
LEFT JOIN portfolios p ON u.user_id = p.user_id
LEFT JOIN holdings h ON p.portfolio_id = h.portfolio_id
WHERE u.is_active = TRUE
GROUP BY u.user_id, u.username, u.risk_profile;

-- =====================================================
-- Stored Procedures
-- =====================================================

DELIMITER $$

-- Procedure: Get Portfolio Performance
CREATE PROCEDURE sp_get_portfolio_performance(IN p_portfolio_id INT)
BEGIN
    SELECT 
        h.stock_symbol,
        h.stock_name,
        h.quantity,
        h.purchase_price,
        h.current_price,
        (h.quantity * h.purchase_price) AS invested_amount,
        (h.quantity * COALESCE(h.current_price, h.purchase_price)) AS current_value,
        ((COALESCE(h.current_price, h.purchase_price) - h.purchase_price) / h.purchase_price * 100) AS return_percentage
    FROM holdings h
    WHERE h.portfolio_id = p_portfolio_id
    ORDER BY h.stock_symbol;
END$$

DELIMITER ;

-- =====================================================
-- End of Schema
-- =====================================================

SELECT 'Database schema created successfully!' AS status;
