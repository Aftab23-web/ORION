"""
AI Engine Service
RULE-BASED Explainable AI for stock recommendations
NO BLACK-BOX MODELS - Only transparent rule-based decision making
"""

import numpy as np
from datetime import datetime

class AIEngine:
    """
    Rule-Based AI Engine for Stock Recommendations
    
    This is NOT a black-box AI model. All decisions are based on
    transparent, explainable rules that can be audited and understood.
    
    EDUCATIONAL PURPOSE ONLY - NOT FINANCIAL ADVICE
    """
    
    def __init__(self):
        """Initialize AI engine with rule thresholds"""
        self.rules = {
            # Buy signal thresholds
            'buy': {
                'min_sharpe_ratio': 0.8,
                'max_volatility': 30,
                'min_return': 10,
                'max_drawdown': -25,
                'min_fundamental_score': 60,
                'min_risk_reward': 1.5
            },
            # Hold signal thresholds
            'hold': {
                'min_sharpe_ratio': 0.4,
                'max_volatility': 40,
                'min_return': 0,
                'max_drawdown': -35,
                'min_fundamental_score': 40,
                'min_risk_reward': 1.0
            },
            # Sell signals (anything worse than hold)
            'sell': {
                'criteria': 'Below hold thresholds or negative indicators'
            }
        }
    
    def generate_recommendation(self, stock_symbol, risk_metrics, user_risk_profile='Moderate'):
        """
        Generate rule-based stock recommendation with full explanation
        
        Args:
            stock_symbol: Stock ticker symbol
            risk_metrics: Dictionary with calculated risk metrics
            user_risk_profile: User's risk tolerance (Conservative/Moderate/Aggressive)
        
        Returns:
            Dictionary with recommendation and detailed explanation
        """
        
        # Rule-based scoring system
        buy_score = 0
        sell_score = 0
        hold_score = 0
        
        reasoning = []
        risk_factors = []
        opportunity_factors = []
        
        # Extract metrics
        sharpe_ratio = risk_metrics.get('sharpe_ratio', 0)
        volatility = risk_metrics.get('annualized_volatility', 0)
        annual_return = risk_metrics.get('annual_return', 0)
        max_drawdown = risk_metrics.get('max_drawdown', 0)
        fundamental_score = risk_metrics.get('fundamental_score', 50)
        risk_reward_ratio = risk_metrics.get('risk_reward_ratio', 0)
        risk_level = risk_metrics.get('risk_level', 'Medium')
        loss_probability = risk_metrics.get('loss_probability', 0.5)
        
        # ============================================
        # RULE 1: Sharpe Ratio Analysis
        # ============================================
        if sharpe_ratio >= self.rules['buy']['min_sharpe_ratio']:
            buy_score += 20
            opportunity_factors.append(f"Strong risk-adjusted returns (Sharpe: {sharpe_ratio:.2f})")
        elif sharpe_ratio >= self.rules['hold']['min_sharpe_ratio']:
            hold_score += 15
            reasoning.append(f"Moderate risk-adjusted returns (Sharpe: {sharpe_ratio:.2f})")
        else:
            sell_score += 15
            risk_factors.append(f"Poor risk-adjusted returns (Sharpe: {sharpe_ratio:.2f})")
        
        # ============================================
        # RULE 2: Volatility Check
        # ============================================
        volatility_limit = self._get_volatility_limit(user_risk_profile)
        
        if volatility <= volatility_limit * 0.7:
            buy_score += 15
            opportunity_factors.append(f"Low volatility ({volatility:.1f}%) - stable price action")
        elif volatility <= volatility_limit:
            hold_score += 10
            reasoning.append(f"Moderate volatility ({volatility:.1f}%) - acceptable for {user_risk_profile} profile")
        else:
            sell_score += 20
            risk_factors.append(f"High volatility ({volatility:.1f}%) - exceeds {user_risk_profile} profile threshold")
        
        # ============================================
        # RULE 3: Return Performance
        # ============================================
        if annual_return >= self.rules['buy']['min_return']:
            buy_score += 20
            opportunity_factors.append(f"Positive annual return ({annual_return:.1f}%)")
        elif annual_return >= self.rules['hold']['min_return']:
            hold_score += 15
            reasoning.append(f"Neutral to positive return ({annual_return:.1f}%)")
        else:
            sell_score += 15
            risk_factors.append(f"Negative annual return ({annual_return:.1f}%)")
        
        # ============================================
        # RULE 4: Maximum Drawdown
        # ============================================
        if max_drawdown >= self.rules['buy']['max_drawdown']:
            buy_score += 15
            opportunity_factors.append(f"Limited downside risk (Max DD: {max_drawdown:.1f}%)")
        elif max_drawdown >= self.rules['hold']['max_drawdown']:
            hold_score += 10
            reasoning.append(f"Moderate drawdown risk (Max DD: {max_drawdown:.1f}%)")
        else:
            sell_score += 20
            risk_factors.append(f"High drawdown risk (Max DD: {max_drawdown:.1f}%)")
        
        # ============================================
        # RULE 5: Fundamental Health
        # ============================================
        if fundamental_score >= self.rules['buy']['min_fundamental_score']:
            buy_score += 15
            opportunity_factors.append(f"Strong fundamentals (Score: {fundamental_score:.0f}/100)")
        elif fundamental_score >= self.rules['hold']['min_fundamental_score']:
            hold_score += 10
            reasoning.append(f"Moderate fundamentals (Score: {fundamental_score:.0f}/100)")
        else:
            sell_score += 15
            risk_factors.append(f"Weak fundamentals (Score: {fundamental_score:.0f}/100)")
        
        # ============================================
        # RULE 6: Risk-Reward Ratio
        # ============================================
        if risk_reward_ratio >= self.rules['buy']['min_risk_reward']:
            buy_score += 15
            opportunity_factors.append(f"Favorable risk-reward ratio ({risk_reward_ratio:.2f})")
        elif risk_reward_ratio >= self.rules['hold']['min_risk_reward']:
            hold_score += 10
            reasoning.append(f"Acceptable risk-reward ratio ({risk_reward_ratio:.2f})")
        else:
            sell_score += 10
            risk_factors.append(f"Unfavorable risk-reward ratio ({risk_reward_ratio:.2f})")
        
        # ============================================
        # RULE 7: Loss Probability
        # ============================================
        if loss_probability < 0.40:
            buy_score += 10
            opportunity_factors.append(f"Low loss probability ({loss_probability*100:.1f}%)")
        elif loss_probability < 0.50:
            hold_score += 5
            reasoning.append(f"Moderate loss probability ({loss_probability*100:.1f}%)")
        else:
            sell_score += 10
            risk_factors.append(f"High loss probability ({loss_probability*100:.1f}%)")
        
        # ============================================
        # RULE 8: Risk Profile Alignment
        # ============================================
        if not self._check_risk_profile_alignment(risk_level, user_risk_profile):
            sell_score += 15
            risk_factors.append(f"Stock risk level ({risk_level}) misaligned with your {user_risk_profile} profile")
        else:
            buy_score += 10
            opportunity_factors.append(f"Risk level aligned with your {user_risk_profile} profile")
        
        # ============================================
        # FINAL DECISION LOGIC
        # ============================================
        max_score = max(buy_score, sell_score, hold_score)
        
        if max_score == buy_score and buy_score >= 60:
            recommendation = 'Buy'
            confidence = min(buy_score / 100, 0.95)
            action_color = 'success'
        elif max_score == sell_score and sell_score >= 50:
            recommendation = 'Sell'
            confidence = min(sell_score / 100, 0.95)
            action_color = 'danger'
        else:
            recommendation = 'Hold'
            confidence = min(max(hold_score, 40) / 100, 0.85)
            action_color = 'warning'
        
        # ============================================
        # BUILD EXPLAINABLE OUTPUT
        # ============================================
        explanation = self._build_explanation(
            recommendation,
            buy_score,
            sell_score,
            hold_score,
            opportunity_factors,
            risk_factors,
            reasoning
        )
        
        # ============================================
        # EDUCATIONAL WARNINGS
        # ============================================
        warnings = [
            "⚠️ This is a RULE-BASED educational recommendation",
            "⚠️ NOT financial advice - do your own research",
            "⚠️ Past performance does NOT guarantee future results",
            f"⚠️ Recommendation based on {risk_metrics.get('total_days_analyzed', 0)} days of historical data"
        ]
        
        return {
            'recommendation': recommendation,
            'confidence': round(confidence, 2),
            'confidence_percentage': round(confidence * 100, 1),
            'action_color': action_color,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'hold_score': hold_score,
            'explanation': explanation,
            'opportunity_factors': opportunity_factors,
            'risk_factors': risk_factors,
            'general_reasoning': reasoning,
            'warnings': warnings,
            'rules_applied': len(opportunity_factors) + len(risk_factors) + len(reasoning),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_volatility_limit(self, risk_profile):
        """Get volatility limit based on risk profile"""
        limits = {
            'Conservative': 15,
            'Moderate': 25,
            'Aggressive': 40
        }
        return limits.get(risk_profile, 25)
    
    def _check_risk_profile_alignment(self, stock_risk_level, user_risk_profile):
        """Check if stock risk aligns with user profile"""
        alignment_matrix = {
            'Conservative': ['Low'],
            'Moderate': ['Low', 'Medium'],
            'Aggressive': ['Low', 'Medium', 'High']
        }
        
        allowed_levels = alignment_matrix.get(user_risk_profile, ['Medium'])
        return stock_risk_level in allowed_levels
    
    def _build_explanation(self, recommendation, buy_score, sell_score, hold_score, 
                          opportunity_factors, risk_factors, reasoning):
        """Build comprehensive human-readable explanation"""
        
        explanation = f"""
Based on transparent rule-based analysis, the AI recommends: **{recommendation}**

**Scoring Breakdown:**
- Buy Score: {buy_score}/100
- Hold Score: {hold_score}/100
- Sell Score: {sell_score}/100

**Why {recommendation}?**

"""
        
        if recommendation == 'Buy':
            explanation += "The analysis identified multiple positive factors:\n\n"
            for factor in opportunity_factors:
                explanation += f"✅ {factor}\n"
            
            if risk_factors:
                explanation += "\n**However, be aware of:**\n"
                for factor in risk_factors:
                    explanation += f"⚠️ {factor}\n"
        
        elif recommendation == 'Sell':
            explanation += "The analysis identified concerning risk factors:\n\n"
            for factor in risk_factors:
                explanation += f"❌ {factor}\n"
            
            if opportunity_factors:
                explanation += "\n**Positive aspects (not enough to overcome risks):**\n"
                for factor in opportunity_factors:
                    explanation += f"ℹ️ {factor}\n"
        
        else:  # Hold
            explanation += "The analysis suggests maintaining current position:\n\n"
            for item in reasoning:
                explanation += f"📊 {item}\n"
            
            if opportunity_factors:
                explanation += "\n**Positive factors:**\n"
                for factor in opportunity_factors:
                    explanation += f"✅ {factor}\n"
            
            if risk_factors:
                explanation += "\n**Risk factors:**\n"
                for factor in risk_factors:
                    explanation += f"⚠️ {factor}\n"
        
        explanation += "\n**Remember:** This is an educational tool using rule-based logic, not a sophisticated AI model."
        
        return explanation
    
    def simulate_event_impact(self, risk_metrics, event_type='market_crash'):
        """
        Simulate impact of market events on stock
        
        Educational feature to show how stocks might react to events
        
        Args:
            risk_metrics: Current risk metrics
            event_type: Type of event to simulate
        
        Returns:
            Dictionary with simulated impact
        """
        
        current_price = risk_metrics.get('current_price', 100)
        beta = risk_metrics.get('beta', 1.0)
        volatility = risk_metrics.get('annualized_volatility', 20)
        
        scenarios = {
            'market_crash': {
                'market_drop': -20,  # Market drops 20%
                'description': '20% Market Correction',
                'likelihood': 'Low (occurs every 3-5 years)'
            },
            'rate_hike': {
                'market_drop': -5,  # Market drops 5%
                'description': 'Interest Rate Hike',
                'likelihood': 'Medium (policy-dependent)'
            },
            'sector_boom': {
                'market_drop': 15,  # Market rises 15%
                'description': 'Sector Boom',
                'likelihood': 'Medium (cycle-dependent)'
            }
        }
        
        scenario = scenarios.get(event_type, scenarios['market_crash'])
        market_impact = scenario['market_drop']
        
        # Estimated stock impact = Market impact × Beta
        estimated_impact = market_impact * beta
        
        # Add volatility-based uncertainty
        best_case = estimated_impact + (volatility / 10)
        worst_case = estimated_impact - (volatility / 10)
        
        new_price_expected = current_price * (1 + estimated_impact / 100)
        new_price_best = current_price * (1 + best_case / 100)
        new_price_worst = current_price * (1 + worst_case / 100)
        
        return {
            'event': scenario['description'],
            'likelihood': scenario['likelihood'],
            'current_price': round(current_price, 2),
            'expected_impact_pct': round(estimated_impact, 2),
            'expected_price': round(new_price_expected, 2),
            'best_case_price': round(new_price_best, 2),
            'worst_case_price': round(new_price_worst, 2),
            'explanation': f"""
If a {scenario['description']} occurs (market moves {market_impact}%), 
this stock with beta {beta:.2f} is expected to move approximately {estimated_impact:.1f}%.

Given the stock's volatility ({volatility:.1f}%), the actual impact could range from 
{worst_case:.1f}% to {best_case:.1f}%.

This is a SIMPLIFIED SIMULATION for educational purposes only.
"""
        }
