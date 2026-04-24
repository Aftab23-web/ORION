-- =====================================================
-- Migration Script: Add Terms and Conditions Support
-- Description: Adds terms_accepted and terms_accepted_at columns to users table
-- Date: 2025-12-30
-- =====================================================

USE stock_risk_db;

-- Add new columns to users table if they don't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS terms_accepted BOOLEAN DEFAULT FALSE AFTER is_active,
ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMP NULL AFTER terms_accepted;

-- Optional: If you want existing users to keep using the app without accepting terms again,
-- you can set terms_accepted to TRUE for existing users
-- Uncomment the following line if needed:
-- UPDATE users SET terms_accepted = TRUE, terms_accepted_at = NOW() WHERE created_at < NOW();

-- Verify the changes
DESCRIBE users;

SELECT 'Migration completed successfully!' AS Status;
