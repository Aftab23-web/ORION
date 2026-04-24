"""
Configuration file for ORION (Operational Risk and Investment Optimization Network)
Contains all application settings and constants
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Secret Key (Change this in production!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'root'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'stock_risk_db'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # API Keys for Stock Data
    TWELVE_DATA_API_KEY = os.environ.get('TWELVE_DATA_API_KEY') or 'BPD7BN3HQWV8B2ZZ'
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY') or 'BPD7BN3HQWV8B2ZZ'
    FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY') or 'd5991m1r01qnj71iir3gd5991m1r01qnj71iir40'
    
    # Application Settings
    APP_NAME = 'ORION'
    APP_VERSION = '1.0.0'
    
    # Risk Profile Thresholds
    RISK_PROFILES = {
        'Conservative': {
            'max_equity_percentage': 40,
            'max_single_stock_percentage': 5,
            'max_volatility': 15,
            'min_diversification': 10
        },
        'Moderate': {
            'max_equity_percentage': 70,
            'max_single_stock_percentage': 10,
            'max_volatility': 25,
            'min_diversification': 7
        },
        'Aggressive': {
            'max_equity_percentage': 95,
            'max_single_stock_percentage': 20,
            'max_volatility': 40,
            'min_diversification': 5
        }
    }
    
    # Risk Level Thresholds (based on annualized volatility %)
    VOLATILITY_THRESHOLDS = {
        'Low': (0, 15),
        'Medium': (15, 30),
        'High': (30, 100)
    }
    
    # Stock Data Settings
    DEFAULT_BENCHMARK = '^NSEI'  # NIFTY 50
    DATA_PERIOD = '1y'  # 1 year of historical data
    
    # AI/ML Settings
    MIN_DATA_POINTS = 30  # Minimum days of data required for analysis
    CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for AI suggestions
    
    # Sentiment Analysis
    SENTIMENT_POSITIVE_THRESHOLD = 0.1
    SENTIMENT_NEGATIVE_THRESHOLD = -0.1
    
    # Educational Disclaimers
    DISCLAIMER_TEXT = """
    ⚠️ EDUCATIONAL PURPOSE ONLY ⚠️
    
    This application is designed for educational and analytical purposes only.
    
    - NOT financial advice
    - NOT investment recommendations
    - NOT suitable for real trading decisions
    - Past performance does NOT guarantee future results
    - All calculations are simplified for learning purposes
    
    Always consult a qualified financial advisor before making investment decisions.
    """

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MYSQL_DATABASE = 'stock_risk_db_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
