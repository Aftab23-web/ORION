"""
Sentiment Analysis Service
NLP-based sentiment analysis using TextBlob
Analyzes market sentiment from news and text
"""

from textblob import TextBlob
import random
from datetime import datetime, timedelta

class SentimentAnalyzer:
    """
    Sentiment Analysis using Natural Language Processing
    
    Uses TextBlob for simple sentiment analysis
    Educational demonstration of NLP in finance
    """
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        # Sample news headlines for demonstration
        # In production, these would come from news APIs
        self.sample_headlines = {
            'positive': [
                "{} reports strong quarterly earnings, beats expectations",
                "{} announces new product launch, stock rallies",
                "{} receives upgrade from analysts, target price raised",
                "Institutional investors increase stake in {}",
                "{} shows strong growth in key metrics",
                "{} expands into new markets, investors optimistic",
                "{} announces strategic partnership with industry leader",
                "Analysts bullish on {}'s future prospects"
            ],
            'negative': [
                "{} misses earnings estimates, shares tumble",
                "{} faces regulatory challenges, investor concern grows",
                "{} reports declining revenue, outlook uncertain",
                "Analysts downgrade {}, cite market headwinds",
                "{} struggles with competition, market share drops",
                "{} announces job cuts, restructuring plans",
                "Insider selling increases at {}",
                "{} faces lawsuit, legal troubles mount"
            ],
            'neutral': [
                "{} announces board meeting scheduled",
                "{} maintains market position, no major changes",
                "{} releases quarterly update, in line with expectations",
                "{} confirms dividend payment date",
                "Trading volume for {} remains stable",
                "{} participates in industry conference",
                "{} updates corporate governance policies",
                "{} files routine regulatory documents"
            ]
        }
    
    def analyze_stock_sentiment(self, stock_symbol, num_headlines=5):
        """
        Analyze sentiment for a stock
        
        Args:
            stock_symbol: Stock ticker symbol
            num_headlines: Number of sample headlines to analyze
        
        Returns:
            Dictionary with sentiment analysis results
        """
        
        # Generate sample headlines (in production, fetch from news API)
        headlines = self._generate_sample_headlines(stock_symbol, num_headlines)
        
        # Analyze each headline
        headline_sentiments = []
        total_polarity = 0
        total_subjectivity = 0
        
        for headline in headlines:
            sentiment = self._analyze_text(headline['text'])
            headline['sentiment'] = sentiment
            headline_sentiments.append(headline)
            total_polarity += sentiment['polarity']
            total_subjectivity += sentiment['subjectivity']
        
        # Calculate aggregate sentiment
        avg_polarity = total_polarity / len(headlines) if headlines else 0
        avg_subjectivity = total_subjectivity / len(headlines) if headlines else 0
        
        # Classify overall sentiment
        sentiment_label = self._classify_sentiment(avg_polarity)
        sentiment_icon = self._get_sentiment_icon(sentiment_label)
        
        # Generate sentiment explanation
        explanation = self._generate_sentiment_explanation(
            sentiment_label, 
            avg_polarity, 
            avg_subjectivity,
            stock_symbol
        )
        
        return {
            'stock_symbol': stock_symbol,
            'overall_sentiment': sentiment_label,
            'sentiment_icon': sentiment_icon,
            'avg_polarity': round(avg_polarity, 3),
            'avg_subjectivity': round(avg_subjectivity, 3),
            'sentiment_score': round((avg_polarity + 1) * 50, 1),  # Scale to 0-100
            'headlines': headline_sentiments,
            'explanation': explanation,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'disclaimer': '⚠️ Sentiment based on sample headlines - Educational purpose only'
        }
    
    def _analyze_text(self, text):
        """
        Analyze sentiment of a text using TextBlob
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with polarity and subjectivity
        """
        try:
            blob = TextBlob(text)
            
            return {
                'polarity': blob.sentiment.polarity,  # -1 (negative) to 1 (positive)
                'subjectivity': blob.sentiment.subjectivity,  # 0 (objective) to 1 (subjective)
                'polarity_label': self._classify_sentiment(blob.sentiment.polarity)
            }
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {
                'polarity': 0,
                'subjectivity': 0,
                'polarity_label': 'Neutral'
            }
    
    def _classify_sentiment(self, polarity):
        """
        Classify sentiment based on polarity score
        
        Args:
            polarity: Polarity score (-1 to 1)
        
        Returns:
            Sentiment label
        """
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _get_sentiment_icon(self, sentiment_label):
        """Get icon for sentiment"""
        icons = {
            'Positive': '😊',
            'Neutral': '😐',
            'Negative': '😟'
        }
        return icons.get(sentiment_label, '😐')
    
    def _generate_sample_headlines(self, stock_symbol, num_headlines):
        """
        Generate sample headlines for demonstration
        
        In production, this would fetch real news from APIs like:
        - News API
        - Alpha Vantage News
        - Financial news RSS feeds
        
        Args:
            stock_symbol: Stock ticker
            num_headlines: Number of headlines to generate
        
        Returns:
            List of headline dictionaries
        """
        headlines = []
        
        # Remove exchange suffix for better readability
        company_name = stock_symbol.split('.')[0]
        
        # Generate mix of sentiments (weighted random)
        sentiment_distribution = ['positive'] * 3 + ['negative'] * 2 + ['neutral'] * 3
        
        for i in range(num_headlines):
            sentiment_type = random.choice(sentiment_distribution)
            template = random.choice(self.sample_headlines[sentiment_type])
            
            headline = {
                'text': template.format(company_name),
                'source': random.choice(['Economic Times', 'Bloomberg', 'Reuters', 'Business Standard', 'MoneyControl']),
                'date': (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d'),
                'expected_sentiment': sentiment_type
            }
            
            headlines.append(headline)
        
        return headlines
    
    def _generate_sentiment_explanation(self, sentiment_label, polarity, subjectivity, stock_symbol):
        """Generate human-readable explanation of sentiment analysis"""
        
        explanation = f"""
**Market Sentiment Analysis for {stock_symbol}**

**Overall Sentiment:** {sentiment_label}
**Sentiment Polarity:** {polarity:.3f} (range: -1 to +1)
**Subjectivity:** {subjectivity:.3f} (range: 0 to 1)

**What does this mean?**

"""
        
        if sentiment_label == 'Positive':
            explanation += """
The recent news and market chatter around this stock is generally positive. 
This suggests:
- Favorable market perception
- Positive news flow
- Potential bullish sentiment among investors

**Note:** Positive sentiment doesn't guarantee price increase. Always verify with fundamental and technical analysis.
"""
        elif sentiment_label == 'Negative':
            explanation += """
The recent news and market chatter shows concerning signals.
This suggests:
- Unfavorable market perception
- Negative news flow
- Potential bearish sentiment among investors

**Note:** Negative sentiment might be temporary or overblown. Do thorough research before making decisions.
"""
        else:
            explanation += """
The market sentiment is balanced with no strong directional bias.
This suggests:
- Neutral market perception
- Mixed news flow
- Wait-and-watch approach from investors

**Note:** Neutral sentiment often precedes major moves. Stay alert for new developments.
"""
        
        if subjectivity > 0.7:
            explanation += "\n⚠️ **High subjectivity** indicates opinions and emotions rather than facts. Exercise caution."
        elif subjectivity < 0.3:
            explanation += "\n✅ **Low subjectivity** indicates fact-based reporting, which is generally more reliable."
        
        explanation += "\n\n**Educational Note:** This sentiment analysis is based on TextBlob NLP. It's a simplified demonstration and should not be the sole basis for investment decisions."
        
        return explanation
    
    def analyze_custom_text(self, text):
        """
        Analyze sentiment of custom text
        
        Useful for analyzing:
        - Earnings call transcripts
        - Company announcements
        - Financial reports
        - Social media posts
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment analysis results
        """
        sentiment = self._analyze_text(text)
        
        return {
            'text_preview': text[:200] + '...' if len(text) > 200 else text,
            'polarity': sentiment['polarity'],
            'subjectivity': sentiment['subjectivity'],
            'sentiment_label': sentiment['polarity_label'],
            'sentiment_icon': self._get_sentiment_icon(sentiment['polarity_label']),
            'word_count': len(text.split()),
            'character_count': len(text)
        }
    
    def compare_sentiment_trends(self, stock_symbol, periods=['1d', '1w', '1m']):
        """
        Compare sentiment trends over time
        
        Educational feature showing how sentiment changes
        
        Args:
            stock_symbol: Stock ticker
            periods: Time periods to analyze
        
        Returns:
            Trend analysis
        """
        # Simulate trend data (in production, use historical news)
        trends = {}
        
        for period in periods:
            # Generate sample sentiment for period
            sample_polarity = random.uniform(-0.5, 0.5)
            
            trends[period] = {
                'polarity': round(sample_polarity, 3),
                'sentiment': self._classify_sentiment(sample_polarity),
                'confidence': random.uniform(0.6, 0.9)
            }
        
        # Determine trend direction
        if len(periods) >= 2:
            if trends[periods[-1]]['polarity'] > trends[periods[0]]['polarity']:
                trend_direction = 'Improving'
            elif trends[periods[-1]]['polarity'] < trends[periods[0]]['polarity']:
                trend_direction = 'Deteriorating'
            else:
                trend_direction = 'Stable'
        else:
            trend_direction = 'Insufficient data'
        
        return {
            'stock_symbol': stock_symbol,
            'trends': trends,
            'trend_direction': trend_direction,
            'note': 'Simulated trend data for educational purposes'
        }
