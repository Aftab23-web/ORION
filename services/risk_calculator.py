"""
Risk Calculator Service
Calculates various risk metrics for stocks and portfolios
"""

import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime

class RiskCalculator:
    """Calculates risk metrics for stocks and portfolios"""
    
    def __init__(self):
        """Initialize risk calculator with constants"""
        self.trading_days_per_year = 252
        self.risk_free_rate = 0.065  # 6.5% (approximate Indian risk-free rate)
    
    def calculate_stock_risk(self, historical_data, stock_info=None):
        """
        Calculate comprehensive risk metrics for a single stock
        
        Args:
            historical_data: DataFrame with historical price data
            stock_info: Dictionary with stock information
        
        Returns:
            Dictionary with risk metrics
        """
        if historical_data is None or historical_data.empty:
            return self._empty_metrics()
        
        try:
            # Calculate daily returns
            returns = historical_data['Close'].pct_change().dropna()
            
            if len(returns) < 30:  # Need minimum data points
                return self._empty_metrics()
            
            # Basic metrics
            current_price = historical_data['Close'].iloc[-1]
            avg_return = returns.mean()
            
            # Volatility (standard deviation of returns)
            volatility = returns.std()
            annualized_volatility = volatility * np.sqrt(self.trading_days_per_year) * 100
            
            # Risk level classification
            risk_level = self._classify_risk_level(annualized_volatility)
            
            # Maximum Drawdown
            max_drawdown = self._calculate_max_drawdown(historical_data['Close'])
            
            # Annual Return
            total_return = (current_price / historical_data['Close'].iloc[0] - 1)
            days = len(historical_data)
            annual_return = ((1 + total_return) ** (self.trading_days_per_year / days) - 1) * 100
            
            # Sharpe Ratio (risk-adjusted return)
            excess_returns = avg_return - (self.risk_free_rate / self.trading_days_per_year)
            sharpe_ratio = (excess_returns / volatility) * np.sqrt(self.trading_days_per_year) if volatility > 0 else 0
            
            # Value at Risk (VaR) - 95% confidence
            var_95 = np.percentile(returns, 5) * 100
            
            # Conditional Value at Risk (CVaR)
            cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100
            
            # Beta (if we have benchmark data - simplified to 1 for now)
            beta = stock_info.get('beta', 1.0) if stock_info else 1.0
            
            # Sortino Ratio (downside risk-adjusted return)
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() if len(downside_returns) > 0 else volatility
            sortino_ratio = (excess_returns / downside_std) * np.sqrt(self.trading_days_per_year) if downside_std > 0 else 0
            
            # Risk-Reward Ratio
            avg_gain = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
            avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 1
            risk_reward_ratio = avg_gain / avg_loss if avg_loss > 0 else 0
            
            # Loss Probability (percentage of negative return days)
            loss_probability = (returns < 0).sum() / len(returns)
            
            # Fundamental Health Score (simplified)
            fundamental_score = self._calculate_fundamental_score(stock_info) if stock_info else 50
            
            # Confidence Score (based on data quality)
            confidence_score = min(len(returns) / 252, 1.0)  # Higher with more data
            
            return {
                'current_price': round(current_price, 2),
                'volatility': round(volatility * 100, 2),
                'annualized_volatility': round(annualized_volatility, 2),
                'risk_level': risk_level,
                'max_drawdown': round(max_drawdown, 2),
                'annual_return': round(annual_return, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'sortino_ratio': round(sortino_ratio, 2),
                'var_95': round(var_95, 2),
                'cvar_95': round(cvar_95, 2),
                'beta': round(beta, 2),
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'loss_probability': round(loss_probability, 4),
                'fundamental_score': round(fundamental_score, 2),
                'confidence_score': round(confidence_score, 2),
                'total_days_analyzed': len(historical_data)
            }
            
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return self._empty_metrics()
    
    def _calculate_max_drawdown(self, prices):
        """
        Calculate maximum drawdown (largest peak-to-trough decline)
        
        Args:
            prices: Series of stock prices
        
        Returns:
            Maximum drawdown percentage
        """
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min() * 100
        return max_dd
    
    def _classify_risk_level(self, annualized_volatility):
        """
        Classify risk level based on volatility
        
        Args:
            annualized_volatility: Annualized volatility percentage
        
        Returns:
            Risk level string: 'Low', 'Medium', or 'High'
        """
        if annualized_volatility < 15:
            return 'Low'
        elif annualized_volatility < 30:
            return 'Medium'
        else:
            return 'High'
    
    def _calculate_fundamental_score(self, stock_info):
        """
        Calculate simplified fundamental health score (0-100)
        
        Args:
            stock_info: Dictionary with stock fundamental data
        
        Returns:
            Health score (0-100)
        """
        if not stock_info:
            return 50
        
        score = 50  # Start with neutral score
        
        # P/E Ratio (lower is better, up to a point)
        pe_ratio = stock_info.get('pe_ratio', 0)
        if pe_ratio > 0:
            if pe_ratio < 15:
                score += 10
            elif pe_ratio < 25:
                score += 5
            elif pe_ratio > 40:
                score -= 10
        
        # Market Cap (larger is generally more stable)
        market_cap = stock_info.get('market_cap', 0)
        if market_cap > 1_000_000_000_000:  # > 1 trillion
            score += 10
        elif market_cap > 100_000_000_000:  # > 100 billion
            score += 5
        
        # Dividend Yield (positive is good)
        div_yield = stock_info.get('dividend_yield', 0)
        if div_yield > 0.03:  # > 3%
            score += 10
        elif div_yield > 0.01:  # > 1%
            score += 5
        
        # Beta (closer to 1 is less volatile)
        beta = stock_info.get('beta', 1.0)
        if 0.8 <= beta <= 1.2:
            score += 10
        elif beta > 1.5:
            score -= 10
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))
    
    def _empty_metrics(self):
        """Return empty metrics structure"""
        return {
            'current_price': 0,
            'volatility': 0,
            'annualized_volatility': 0,
            'risk_level': 'Unknown',
            'max_drawdown': 0,
            'annual_return': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'var_95': 0,
            'cvar_95': 0,
            'beta': 1.0,
            'risk_reward_ratio': 0,
            'loss_probability': 0,
            'fundamental_score': 0,
            'confidence_score': 0,
            'total_days_analyzed': 0
        }
    
    def calculate_portfolio_correlation(self, holdings_data):
        """
        Calculate correlation matrix for portfolio holdings
        
        Args:
            holdings_data: Dictionary with symbol as key and price DataFrame as value
        
        Returns:
            Correlation matrix DataFrame
        """
        try:
            # Extract returns for each stock
            returns_dict = {}
            
            for symbol, df in holdings_data.items():
                if df is not None and not df.empty:
                    returns = df['Close'].pct_change().dropna()
                    returns_dict[symbol] = returns
            
            if not returns_dict:
                return None
            
            # Create DataFrame with aligned dates
            returns_df = pd.DataFrame(returns_dict)
            
            # Calculate correlation matrix
            correlation_matrix = returns_df.corr()
            
            return correlation_matrix
            
        except Exception as e:
            print(f"Error calculating correlation: {e}")
            return None
    
    def calculate_var_portfolio(self, returns, confidence_level=0.95):
        """
        Calculate Portfolio Value at Risk
        
        Args:
            returns: Series or array of portfolio returns
            confidence_level: Confidence level for VaR (default 95%)
        
        Returns:
            VaR value
        """
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return var
