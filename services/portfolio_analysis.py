"""
Portfolio Analysis Service
Comprehensive portfolio risk and diversification analysis
"""

import numpy as np
import pandas as pd
from services.data_fetcher import StockDataFetcher
from services.risk_calculator import RiskCalculator

class PortfolioAnalyzer:
    """Analyzes portfolio-level risk and diversification"""
    
    def __init__(self):
        """Initialize portfolio analyzer"""
        self.data_fetcher = StockDataFetcher()
        self.risk_calc = RiskCalculator()
    
    def analyze_portfolio(self, holdings, risk_profile='Moderate'):
        """
        Comprehensive portfolio analysis
        
        Args:
            holdings: List of holding dictionaries from database
            risk_profile: User's risk profile (Conservative/Moderate/Aggressive)
        
        Returns:
            Dictionary with complete portfolio analysis
        """
        if not holdings:
            return self._empty_analysis()
        
        try:
            # Calculate basic portfolio metrics (convert to float to handle Decimal)
            total_invested = sum(float(h['quantity']) * float(h['purchase_price']) for h in holdings)
            total_current = sum(float(h['quantity']) * float(h['current_price'] or h['purchase_price']) for h in holdings)
            total_return = total_current - total_invested
            return_percentage = (total_return / total_invested * 100) if total_invested > 0 else 0
            
            # Asset allocation analysis
            asset_allocation = self._calculate_asset_allocation(holdings)
            
            # Sector exposure analysis
            sector_exposure = self._calculate_sector_exposure(holdings)
            
            # Diversification metrics
            diversification = self._calculate_diversification(holdings)
            
            # Concentration risk
            concentration_risk = self._calculate_concentration_risk(holdings)
            
            # Portfolio volatility and risk
            portfolio_risk = self._calculate_portfolio_risk(holdings)
            
            # Risk profile alignment
            profile_alignment = self._check_risk_profile_alignment(
                asset_allocation,
                diversification,
                portfolio_risk,
                risk_profile
            )
            
            # Portfolio health score (0-100)
            health_score = self._calculate_health_score(
                diversification,
                concentration_risk,
                profile_alignment,
                portfolio_risk
            )
            
            # Recommendations
            recommendations = self._generate_recommendations(
                asset_allocation,
                diversification,
                concentration_risk,
                profile_alignment,
                risk_profile
            )
            
            return {
                'total_invested': round(total_invested, 2),
                'total_current': round(total_current, 2),
                'total_return': round(total_return, 2),
                'return_percentage': round(return_percentage, 2),
                'asset_allocation': asset_allocation,
                'sector_exposure': sector_exposure,
                'diversification': diversification,
                'concentration_risk': concentration_risk,
                'portfolio_risk': portfolio_risk,
                'profile_alignment': profile_alignment,
                'health_score': round(health_score, 2),
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Error analyzing portfolio: {e}")
            return self._empty_analysis()
    
    def _calculate_asset_allocation(self, holdings):
        """Calculate asset allocation percentages"""
        total_value = sum(float(h['quantity']) * float(h['current_price'] or h['purchase_price']) for h in holdings)
        
        if total_value == 0:
            return {'Equity': 0, 'Debt': 0, 'Cash': 0, 'Other': 0}
        
        allocation = {'Equity': 0, 'Debt': 0, 'Cash': 0, 'Other': 0}
        
        for holding in holdings:
            value = float(holding['quantity']) * float(holding['current_price'] or holding['purchase_price'])
            asset_type = holding.get('asset_type', 'Equity')
            allocation[asset_type] = allocation.get(asset_type, 0) + value
        
        # Convert to percentages
        for asset_type in allocation:
            allocation[asset_type] = round((allocation[asset_type] / total_value) * 100, 2)
        
        return allocation
    
    def _calculate_sector_exposure(self, holdings):
        """Calculate sector-wise exposure"""
        total_value = sum(float(h['quantity']) * float(h['current_price'] or h['purchase_price']) for h in holdings)
        
        if total_value == 0:
            return {}
        
        sector_values = {}
        
        for holding in holdings:
            value = float(holding['quantity']) * float(holding['current_price'] or holding['purchase_price'])
            sector = holding.get('sector', 'Unknown')
            sector_values[sector] = sector_values.get(sector, 0) + value
        
        # Convert to percentages and sort
        sector_exposure = {
            sector: round((value / total_value) * 100, 2)
            for sector, value in sector_values.items()
        }
        
        # Sort by exposure (descending)
        sector_exposure = dict(sorted(sector_exposure.items(), key=lambda x: x[1], reverse=True))
        
        return sector_exposure
    
    def _calculate_diversification(self, holdings):
        """Calculate diversification metrics"""
        num_holdings = len(holdings)
        
        # Count unique sectors
        unique_sectors = len(set(h.get('sector', 'Unknown') for h in holdings))
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        total_value = sum(float(h['quantity']) * float(h['current_price'] or h['purchase_price']) for h in holdings)
        
        if total_value == 0:
            hhi = 1.0
        else:
            weights = [(float(h['quantity']) * float(h['current_price'] or h['purchase_price']) / total_value) for h in holdings]
            hhi = sum(w**2 for w in weights)
        
        # Diversification score (0-100, higher is better)
        # Based on number of holdings and HHI
        if num_holdings == 0:
            diversification_score = 0
        else:
            # Ideal HHI for a well-diversified portfolio is around 0.1
            hhi_score = max(0, (1 - hhi) * 100)
            holdings_score = min(num_holdings * 10, 50)  # Max 50 points for holdings count
            diversification_score = (hhi_score * 0.6) + (holdings_score * 0.4)
        
        return {
            'score': round(diversification_score, 2),
            'num_holdings': num_holdings,
            'num_sectors': unique_sectors,
            'hhi': round(hhi, 4),
            'status': self._get_diversification_status(diversification_score)
        }
    
    def _get_diversification_status(self, score):
        """Get diversification status label"""
        if score >= 70:
            return 'Well Diversified'
        elif score >= 50:
            return 'Moderately Diversified'
        elif score >= 30:
            return 'Poorly Diversified'
        else:
            return 'Highly Concentrated'
    
    def _calculate_concentration_risk(self, holdings):
        """Calculate concentration risk metrics"""
        total_value = sum(float(h['quantity']) * float(h['current_price'] or h['purchase_price']) for h in holdings)
        
        if total_value == 0:
            return {'max_single_stock': 0, 'top_3_concentration': 0, 'risk_level': 'Unknown'}
        
        # Calculate individual stock percentages
        stock_percentages = [
            (float(h['quantity']) * float(h['current_price'] or h['purchase_price']) / total_value * 100)
            for h in holdings
        ]
        stock_percentages.sort(reverse=True)
        
        max_single = stock_percentages[0] if stock_percentages else 0
        top_3 = sum(stock_percentages[:3]) if len(stock_percentages) >= 3 else sum(stock_percentages)
        
        # Risk level classification
        if max_single > 30:
            risk_level = 'High'
        elif max_single > 15:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'max_single_stock': round(max_single, 2),
            'top_3_concentration': round(top_3, 2),
            'risk_level': risk_level
        }
    
    def _calculate_portfolio_risk(self, holdings):
        """Calculate overall portfolio risk metrics"""
        try:
            # Fetch historical data for all holdings
            symbols = [h['stock_symbol'] for h in holdings]
            weights = []
            total_value = sum(float(h['quantity']) * float(h['current_price'] or h['purchase_price']) for h in holdings)
            
            returns_data = []
            
            for holding in holdings:
                symbol = holding['stock_symbol']
                weight = (float(holding['quantity']) * float(holding['current_price'] or holding['purchase_price'])) / total_value
                weights.append(weight)
                
                # Get historical data
                hist_data = self.data_fetcher.get_historical_data(symbol, period='6mo')
                if hist_data is not None and not hist_data.empty:
                    daily_returns = hist_data['Close'].pct_change().dropna()
                    returns_data.append(daily_returns)
            
            if not returns_data or len(returns_data) < 2:
                return {
                    'volatility': 0,
                    'risk_level': 'Unknown',
                    'var_95': 0
                }
            
            # Create aligned returns DataFrame
            min_length = min(len(r) for r in returns_data)
            aligned_returns = np.array([r.tail(min_length).values for r in returns_data])
            
            # Calculate portfolio returns
            portfolio_returns = np.dot(weights, aligned_returns)
            
            # Portfolio volatility
            volatility = np.std(portfolio_returns) * np.sqrt(252) * 100
            
            # VaR 95%
            var_95 = np.percentile(portfolio_returns, 5) * 100
            
            # Risk level
            if volatility < 15:
                risk_level = 'Low'
            elif volatility < 25:
                risk_level = 'Medium'
            else:
                risk_level = 'High'
            
            return {
                'volatility': round(volatility, 2),
                'risk_level': risk_level,
                'var_95': round(var_95, 2)
            }
            
        except Exception as e:
            print(f"Error calculating portfolio risk: {e}")
            return {
                'volatility': 0,
                'risk_level': 'Unknown',
                'var_95': 0
            }
    
    def _check_risk_profile_alignment(self, asset_allocation, diversification, portfolio_risk, risk_profile):
        """Check if portfolio aligns with user's risk profile"""
        issues = []
        is_aligned = True
        
        equity_pct = asset_allocation.get('Equity', 0)
        
        # Define thresholds based on risk profile
        thresholds = {
            'Conservative': {'max_equity': 40, 'min_diversification': 60, 'max_volatility': 15},
            'Moderate': {'max_equity': 70, 'min_diversification': 50, 'max_volatility': 25},
            'Aggressive': {'max_equity': 95, 'min_diversification': 40, 'max_volatility': 40}
        }
        
        profile_thresholds = thresholds.get(risk_profile, thresholds['Moderate'])
        
        # Check equity allocation
        if equity_pct > profile_thresholds['max_equity']:
            issues.append(f"Equity allocation ({equity_pct}%) exceeds {risk_profile} profile limit ({profile_thresholds['max_equity']}%)")
            is_aligned = False
        
        # Check diversification
        if diversification['score'] < profile_thresholds['min_diversification']:
            issues.append(f"Portfolio diversification ({diversification['score']}) is below recommended level ({profile_thresholds['min_diversification']})")
            is_aligned = False
        
        # Check volatility
        if portfolio_risk['volatility'] > profile_thresholds['max_volatility']:
            issues.append(f"Portfolio volatility ({portfolio_risk['volatility']}%) exceeds {risk_profile} profile limit ({profile_thresholds['max_volatility']}%)")
            is_aligned = False
        
        return {
            'is_aligned': is_aligned,
            'issues': issues,
            'alignment_score': 100 - (len(issues) * 25)  # Deduct 25 points per issue
        }
    
    def _calculate_health_score(self, diversification, concentration_risk, profile_alignment, portfolio_risk):
        """Calculate overall portfolio health score (0-100)"""
        score = 0
        
        # Diversification (30 points)
        score += (diversification['score'] / 100) * 30
        
        # Concentration risk (25 points)
        if concentration_risk['risk_level'] == 'Low':
            score += 25
        elif concentration_risk['risk_level'] == 'Medium':
            score += 15
        
        # Profile alignment (25 points)
        score += (profile_alignment['alignment_score'] / 100) * 25
        
        # Risk level (20 points)
        if portfolio_risk['risk_level'] == 'Low':
            score += 20
        elif portfolio_risk['risk_level'] == 'Medium':
            score += 12
        elif portfolio_risk['risk_level'] == 'High':
            score += 5
        
        return min(100, max(0, score))
    
    def _generate_recommendations(self, asset_allocation, diversification, concentration_risk, profile_alignment, risk_profile):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Diversification recommendations
        if diversification['num_holdings'] < 5:
            recommendations.append({
                'type': 'warning',
                'category': 'Diversification',
                'message': f'Your portfolio has only {diversification["num_holdings"]} holdings. Consider adding more stocks (aim for 8-12) to reduce risk.',
                'priority': 'High'
            })
        
        if diversification['num_sectors'] < 3:
            recommendations.append({
                'type': 'warning',
                'category': 'Sector Diversification',
                'message': f'Your portfolio is concentrated in {diversification["num_sectors"]} sector(s). Diversify across at least 4-5 sectors.',
                'priority': 'High'
            })
        
        # Concentration risk recommendations
        if concentration_risk['max_single_stock'] > 20:
            recommendations.append({
                'type': 'warning',
                'category': 'Concentration',
                'message': f'Your largest holding represents {concentration_risk["max_single_stock"]}% of your portfolio. Consider reducing to below 15%.',
                'priority': 'High'
            })
        
        # Profile alignment recommendations
        if not profile_alignment['is_aligned']:
            for issue in profile_alignment['issues']:
                recommendations.append({
                    'type': 'alert',
                    'category': 'Risk Profile',
                    'message': issue,
                    'priority': 'Medium'
                })
        
        # Asset allocation recommendations
        equity_pct = asset_allocation.get('Equity', 0)
        if equity_pct == 100:
            recommendations.append({
                'type': 'info',
                'category': 'Asset Allocation',
                'message': 'Your portfolio is 100% equity. Consider adding some debt instruments for stability.',
                'priority': 'Medium'
            })
        
        # General positive feedback
        if diversification['score'] >= 70 and profile_alignment['is_aligned']:
            recommendations.append({
                'type': 'success',
                'category': 'Overall',
                'message': 'Your portfolio is well-diversified and aligned with your risk profile. Good job!',
                'priority': 'Low'
            })
        
        return recommendations
    
    def _empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'total_invested': 0,
            'total_current': 0,
            'total_return': 0,
            'return_percentage': 0,
            'asset_allocation': {},
            'sector_exposure': {},
            'diversification': {},
            'concentration_risk': {},
            'portfolio_risk': {},
            'profile_alignment': {},
            'health_score': 0,
            'recommendations': []
        }
