"""
Stock Routes Blueprint
Handles individual stock analysis, risk metrics, and AI recommendations
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from datetime import datetime, date
from services.data_fetcher import StockDataFetcher
from services.risk_calculator import RiskCalculator
from services.ai_engine import AIEngine
from services.sentiment_analysis import SentimentAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# ==================== PERFORMANCE CACHE ====================
# Global cache to store complete stock analysis results
# Structure: {stock_symbol: {'data': {...}, 'timestamp': time.time()}}
STOCK_ANALYSIS_CACHE = {}
COMPARISON_CACHE = {}
CACHE_DURATION = 1200  # 20 minutes in seconds

def get_cached_analysis(symbol):
    """Get cached stock analysis if available and not expired"""
    if symbol in STOCK_ANALYSIS_CACHE:
        cached_data, timestamp = STOCK_ANALYSIS_CACHE[symbol]['data'], STOCK_ANALYSIS_CACHE[symbol]['timestamp']
        if time.time() - timestamp < CACHE_DURATION:
            print(f"✅ CACHE HIT: Using cached analysis for {symbol} (age: {int(time.time() - timestamp)}s)")
            return cached_data
        else:
            print(f"⏰ CACHE EXPIRED: Cache for {symbol} is {int(time.time() - timestamp)}s old (max: {CACHE_DURATION}s)")
            del STOCK_ANALYSIS_CACHE[symbol]
    return None

def cache_analysis(symbol, data):
    """Cache stock analysis data"""
    STOCK_ANALYSIS_CACHE[symbol] = {
        'data': data,
        'timestamp': time.time()
    }
    print(f"💾 CACHED: Stored analysis for {symbol}")

def get_cached_comparison(symbols_key):
    """Get cached comparison if available"""
    if symbols_key in COMPARISON_CACHE:
        cached_data, timestamp = COMPARISON_CACHE[symbols_key]['data'], COMPARISON_CACHE[symbols_key]['timestamp']
        if time.time() - timestamp < CACHE_DURATION:
            print(f"✅ CACHE HIT: Using cached comparison for {symbols_key}")
            return cached_data
        else:
            del COMPARISON_CACHE[symbols_key]
    return None

def cache_comparison(symbols_key, data):
    """Cache comparison data"""
    COMPARISON_CACHE[symbols_key] = {
        'data': data,
        'timestamp': time.time()
    }
    print(f"💾 CACHED: Stored comparison for {symbols_key}")
# ==========================================================

stock_bp = Blueprint('stock', __name__)

def get_db_connection():
    """Get database connection"""
    from app import get_db_connection as get_conn
    return get_conn()


@stock_bp.route('/analyze/<stock_symbol>')
def analyze_stock(stock_symbol):
    """Comprehensive stock risk analysis page"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    stock_symbol = stock_symbol.upper()
    
    # ========== ALWAYS FETCH FRESH PORTFOLIOS ==========
    portfolios = []
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT portfolio_id, portfolio_name FROM portfolios WHERE user_id = %s AND is_active = TRUE",
                (session['user_id'],)
            )
            portfolios = cursor.fetchall()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"⚠️ Error fetching portfolios: {e}")
    # ===================================================
    
    # ========== CHECK CACHE FIRST ==========
    cached = get_cached_analysis(stock_symbol)
    if cached:
        # Update portfolios with fresh data (not cached)
        cached['portfolios'] = portfolios
        flash(f'⚡ Lightning Fast! Loaded {stock_symbol} from cache (saved ~15-20 seconds)', 'success')
        return render_template('stock_analysis.html', **cached)
    # ========================================
    
    try:
        start_time = time.time()
        print(f"\n🔍 Analyzing {stock_symbol} (no cache, fetching fresh data)...")
        
        # Initialize services
        data_fetcher = StockDataFetcher()
        risk_calc = RiskCalculator()
        ai_engine = AIEngine()
        sentiment_analyzer = SentimentAnalyzer()
        
        # Fetch stock data with timeout monitoring
        stock_info = data_fetcher.get_stock_info(stock_symbol)
        if not stock_info or (time.time() - start_time) > 15:
            flash(f'Unable to fetch data for {stock_symbol}. Please check the symbol or try: RELIANCE.NS, TCS.NS, INFY.NS', 'error')
            return redirect(url_for('portfolio.dashboard'))
        
        historical_data = data_fetcher.get_historical_data(stock_symbol)
        if historical_data is None or historical_data.empty or (time.time() - start_time) > 20:
            flash(f'Insufficient historical data for {stock_symbol}. Try another stock symbol.', 'error')
            return redirect(url_for('portfolio.dashboard'))
        
        # Calculate risk metrics
        risk_metrics = risk_calc.calculate_stock_risk(historical_data, stock_info)
        
        # Get AI recommendation (fast - doesn't make external calls)
        ai_recommendation = ai_engine.generate_recommendation(
            stock_symbol,
            risk_metrics,
            session.get('risk_profile', 'Moderate')
        )
        
        # Perform sentiment analysis with timeout (can be slow)
        sentiment = None
        if (time.time() - start_time) < 22:
            try:
                sentiment = sentiment_analyzer.analyze_stock_sentiment(stock_symbol)
            except:
                sentiment = {
                    'overall_sentiment': 'Neutral',
                    'sentiment_score': 0,
                    'headlines': []
                }
        else:
            sentiment = {
                'overall_sentiment': 'Neutral',
                'sentiment_score': 0,
                'headlines': []
            }
        
        # Prepare chart data (last 90 days)
        chart_data = historical_data.tail(90)[['Close']].to_dict('records')
        chart_dates = historical_data.tail(90).index.strftime('%Y-%m-%d').tolist()
        
        # Save metrics to database
        save_stock_metrics(stock_symbol, risk_metrics)
        
        # Prepare template data (portfolios already fetched at start)
        template_data = {
            'stock_symbol': stock_symbol,
            'stock_info': stock_info,
            'risk_metrics': risk_metrics,
            'ai_recommendation': ai_recommendation,
            'sentiment': sentiment,
            'chart_data': chart_data,
            'chart_dates': chart_dates,
            'portfolios': portfolios,
            'today': date.today().isoformat()
        }
        
        # ========== CACHE THE RESULT ==========
        cache_analysis(stock_symbol, template_data)
        elapsed = time.time() - start_time
        print(f"✅ Analysis completed in {elapsed:.2f}s and cached for 20 minutes")
        # ======================================
        
        return render_template('stock_analysis.html', **template_data)
        
    except Exception as e:
        flash(f'Error analyzing stock: {str(e)}', 'error')
        return redirect(url_for('portfolio.dashboard'))


@stock_bp.route('/search')
def search():
    """Stock search page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('stock_search.html')


@stock_bp.route('/api/search', methods=['POST'])
def api_search_stocks():
    """API endpoint to search for stock symbols"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400
        
        data_fetcher = StockDataFetcher()
        results = data_fetcher.search_stock_symbol(query)
        
        if not results:
            return jsonify({
                'results': [],
                'message': f'No stocks found for "{query}". Try: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS'
            })
        
        return jsonify({
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@stock_bp.route('/compare', methods=['GET', 'POST'])
def compare_stocks():
    """Compare multiple stocks side by side with AI recommendation"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        inputs = request.form.get('symbols', '').strip().split(',')
        inputs = [s.strip() for s in inputs if s.strip()]
        
        if len(inputs) < 2:
            flash('Please enter at least 2 stock symbols or names', 'error')
            return render_template('compare_stocks.html')
        
        if len(inputs) > 5:
            flash('Maximum 5 stocks can be compared', 'error')
            return render_template('compare_stocks.html')
        
        # ========== CHECK CACHE FIRST ==========
        cache_key = ','.join(sorted(inputs))  # Create consistent cache key
        cached = get_cached_comparison(cache_key)
        if cached:
            flash(f'⚡ Lightning Fast! Loaded comparison from cache (saved ~30-60 seconds)', 'success')
            return render_template('compare_stocks.html', **cached)
        # ========================================
        
        try:
            data_fetcher = StockDataFetcher()
            risk_calc = RiskCalculator()
            
            # Resolve stock names to symbols
            symbols = []
            failed_stocks = []
            
            for inp in inputs:
                # Auto-correct common mistakes
                inp_corrected = inp.replace('.NC', '.NS').replace('.nc', '.NS')
                
                # Check if it's already a symbol (contains .NS, .BO or is uppercase)
                if '.' in inp_corrected or inp_corrected.isupper():
                    symbols.append(inp_corrected.upper())
                else:
                    # Search for the stock by name
                    matches = data_fetcher.search_stock_symbol(inp_corrected.lower())
                    if matches:
                        symbols.append(matches[0]['symbol'])
                    else:
                        symbols.append(inp_corrected.upper())  # Try as symbol anyway
            
            comparison_data = []
            stock_details = []  # For AI recommendation
            
            # IMPROVED SEQUENTIAL PROCESSING: Fetch stocks one by one with proper delays
            def fetch_stock_data(symbol, attempt=1):
                """Fetch stock info and historical data with retry logic"""
                max_attempts = 3
                try:
                    print(f"\n🔄 Fetching {symbol} (Attempt {attempt}/{max_attempts})...")
                    start_time = time.time()
                    
                    # Add delay between requests to avoid rate limiting
                    if attempt == 1:
                        time.sleep(1)  # 1 second delay between different stocks
                    else:
                        time.sleep(2 * attempt)  # Longer delay for retries
                    
                    stock_info = data_fetcher.get_stock_info(symbol)
                    
                    if not stock_info:
                        if attempt < max_attempts:
                            print(f"⚠️ No info for {symbol}, retrying...")
                            return fetch_stock_data(symbol, attempt + 1)
                        print(f"❌ Failed to get info for {symbol} after {max_attempts} attempts")
                        return None, symbol
                    
                    print(f"✅ Got info for {symbol}: {stock_info.get('name')} @ ₹{stock_info.get('current_price')}")
                    
                    historical_data = data_fetcher.get_historical_data(symbol)
                    
                    if historical_data is None or historical_data.empty:
                        if attempt < max_attempts:
                            print(f"⚠️ No historical data for {symbol}, retrying...")
                            return fetch_stock_data(symbol, attempt + 1)
                        print(f"❌ Failed to get historical data for {symbol}")
                        return None, symbol
                    
                    elapsed = time.time() - start_time
                    print(f"✅ Successfully fetched {symbol} in {elapsed:.1f}s")
                    return (stock_info, historical_data), symbol
                    
                except Exception as e:
                    print(f"❌ Error fetching {symbol}: {str(e)}")
                    if attempt < max_attempts:
                        print(f"⚠️ Retrying {symbol}...")
                        return fetch_stock_data(symbol, attempt + 1)
                    return None, symbol
            
            # Sequential processing to avoid rate limiting
            print(f"\n📊 Comparing {len(symbols)} stocks: {', '.join(symbols)}")
            for symbol in symbols:
                result, sym = fetch_stock_data(symbol)
                
                if result:
                    stock_info, historical_data = result
                    risk_metrics = risk_calc.calculate_stock_risk(historical_data, stock_info)
                    
                    comparison_data.append({
                        'symbol': symbol,
                        'name': stock_info.get('name', symbol),
                        'current_price': stock_info.get('current_price', 0),
                        'sector': stock_info.get('sector', 'Unknown'),
                        'industry': stock_info.get('industry', 'Unknown'),
                        'metrics': risk_metrics,
                        'pe_ratio': stock_info.get('pe_ratio', 0),
                        'dividend_yield': stock_info.get('dividend_yield', 0),
                        'market_cap': stock_info.get('market_cap', 0)
                    })
                    
                    stock_details.append({
                        'symbol': symbol,
                        'name': stock_info.get('name', symbol),
                        'sector': stock_info.get('sector', 'Unknown'),
                        'current_price': stock_info.get('current_price', 0),
                        'pe_ratio': stock_info.get('pe_ratio', 0),
                        'dividend_yield': stock_info.get('dividend_yield', 0),
                        'annual_return': risk_metrics['annual_return'],
                        'volatility': risk_metrics['annualized_volatility'],
                        'sharpe_ratio': risk_metrics['sharpe_ratio'],
                        'max_drawdown': risk_metrics['max_drawdown'],
                        'beta': risk_metrics['beta'],
                        'risk_level': risk_metrics['risk_level'],
                        'fundamental_score': risk_metrics['fundamental_score']
                    })
                    print(f"✅ Added {symbol} to comparison")
                else:
                    failed_stocks.append(sym)
                    print(f"❌ Failed to fetch {sym}")
            
            print(f"\n📊 Comparison Results: {len(comparison_data)} successful, {len(failed_stocks)} failed")
            
            if not comparison_data:
                error_msg = f'Unable to fetch data for any stocks. This may be due to:'
                error_msg += '<br>• Yahoo Finance rate limiting (try again in 1-2 minutes)'
                error_msg += '<br>• Invalid stock symbols'
                error_msg += f'<br><br>Failed symbols: {", ".join(failed_stocks)}'
                error_msg += '<br><br>💡 Tips: Make sure to use correct NSE symbols (e.g., RELIANCE.NS, TCS.NS)'
                flash(error_msg, 'error')
                return render_template('compare_stocks.html')
            
            if failed_stocks:
                flash(f'⚠️ Could not fetch data for: {", ".join(failed_stocks)}. Successfully loaded {len(comparison_data)} stock(s).', 'warning')
            
            # Generate AI-based investment recommendation
            recommendation = _generate_investment_recommendation(stock_details)
            
            # Prepare template data
            template_data = {
                'comparison_data': comparison_data,
                'symbols': symbols,
                'recommendation': recommendation
            }
            
            # Cache the result
            cache_comparison(cache_key, template_data)
            
            return render_template('compare_stocks.html', **template_data)
            
        except Exception as e:
            flash(f'Error comparing stocks: {str(e)}', 'error')
            return render_template('compare_stocks.html')
    
    return render_template('compare_stocks.html')


def _generate_investment_recommendation(stock_details):
    """Generate AI-based investment recommendation with detailed reasoning"""
    if len(stock_details) < 2:
        return None
    
    # Scoring system for recommendation
    scores = []
    for stock in stock_details:
        score = 0
        reasons = []
        risks = []
        
        # Return score (25 points)
        if stock['annual_return'] > 20:
            score += 25
            reasons.append(f"Strong annual return of {stock['annual_return']:.2f}%")
        elif stock['annual_return'] > 10:
            score += 15
            reasons.append(f"Good annual return of {stock['annual_return']:.2f}%")
        elif stock['annual_return'] > 0:
            score += 5
            reasons.append(f"Positive return of {stock['annual_return']:.2f}%")
        else:
            risks.append(f"Negative return of {stock['annual_return']:.2f}%")
        
        # Risk level score (20 points)
        if stock['risk_level'] == 'Low':
            score += 20
            reasons.append("Low risk profile - suitable for conservative investors")
        elif stock['risk_level'] == 'Medium':
            score += 12
        else:
            risks.append("High risk - significant volatility")
        
        # Sharpe Ratio score (20 points) - Risk-adjusted returns
        if stock['sharpe_ratio'] > 1.5:
            score += 20
            reasons.append(f"Excellent risk-adjusted returns (Sharpe: {stock['sharpe_ratio']:.2f})")
        elif stock['sharpe_ratio'] > 1.0:
            score += 15
            reasons.append(f"Good risk-adjusted returns (Sharpe: {stock['sharpe_ratio']:.2f})")
        elif stock['sharpe_ratio'] > 0.5:
            score += 8
        else:
            risks.append(f"Poor risk-adjusted returns (Sharpe: {stock['sharpe_ratio']:.2f})")
        
        # Volatility score (15 points)
        if stock['volatility'] < 15:
            score += 15
            reasons.append("Low volatility - stable price movements")
        elif stock['volatility'] < 25:
            score += 10
        elif stock['volatility'] < 35:
            score += 5
        else:
            risks.append(f"High volatility ({stock['volatility']:.2f}%) - unstable prices")
        
        # Fundamental score (10 points)
        if stock['fundamental_score'] > 75:
            score += 10
            reasons.append(f"Strong fundamentals (Score: {stock['fundamental_score']:.0f}/100)")
        elif stock['fundamental_score'] > 60:
            score += 6
        elif stock['fundamental_score'] > 50:
            score += 3
        
        # Drawdown score (10 points)
        if stock['max_drawdown'] > -10:
            score += 10
            reasons.append("Limited downside risk")
        elif stock['max_drawdown'] > -20:
            score += 6
        elif stock['max_drawdown'] > -30:
            score += 3
        else:
            risks.append(f"Large historical drawdown ({stock['max_drawdown']:.2f}%)")
        
        # Dividend yield bonus
        if stock['dividend_yield'] and stock['dividend_yield'] > 0.02:
            score += 5
            reasons.append(f"Dividend yield of {stock['dividend_yield']*100:.2f}% provides passive income")
        
        # Beta consideration
        if 0.8 <= stock['beta'] <= 1.2:
            reasons.append("Moderate market correlation - balanced risk")
        elif stock['beta'] < 0.8:
            reasons.append("Lower market correlation - defensive stock")
        else:
            risks.append("High market correlation - amplifies market movements")
        
        scores.append({
            'stock': stock,
            'score': score,
            'reasons': reasons,
            'risks': risks
        })
    
    # Sort by score to find best stock
    scores.sort(key=lambda x: x['score'], reverse=True)
    best = scores[0]
    second_best = scores[1] if len(scores) > 1 else None
    
    # Determine investment strategy
    if best['score'] > 70:
        strategy = "Strong Buy"
        confidence = "High"
    elif best['score'] > 55:
        strategy = "Buy"
        confidence = "Moderate"
    elif best['score'] > 40:
        strategy = "Hold/Cautious Buy"
        confidence = "Low"
    else:
        strategy = "Consider Alternatives"
        confidence = "Very Low"
    
    # Generate comparative analysis
    comparison = ""
    if second_best:
        score_diff = best['score'] - second_best['score']
        if score_diff > 15:
            comparison = f"{best['stock']['symbol']} significantly outperforms {second_best['stock']['symbol']} by {score_diff:.0f} points."
        elif score_diff > 5:
            comparison = f"{best['stock']['symbol']} moderately outperforms {second_best['stock']['symbol']}."
        else:
            comparison = f"Both stocks are closely matched. Consider diversifying between them."
    
    return {
        'recommended_stock': best['stock']['symbol'],
        'recommended_name': best['stock']['name'],
        'score': best['score'],
        'strategy': strategy,
        'confidence': confidence,
        'reasons': best['reasons'],
        'risks': best['risks'],
        'comparison': comparison,
        'all_scores': scores
    }


@stock_bp.route('/search')
def search_stock():
    """Search for stocks by symbol or name"""
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    query = request.args.get('q', '').strip().upper()
    
    if not query or len(query) < 2:
        return jsonify({'success': False, 'message': 'Query too short'})
    
    # Popular Indian stocks (for quick search)
    popular_stocks = [
        {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
        {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services'},
        {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'},
        {'symbol': 'INFY.NS', 'name': 'Infosys'},
        {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever'},
        {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank'},
        {'symbol': 'SBIN.NS', 'name': 'State Bank of India'},
        {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel'},
        {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank'},
        {'symbol': 'ITC.NS', 'name': 'ITC Limited'},
    ]
    
    results = [
        stock for stock in popular_stocks 
        if query in stock['symbol'] or query in stock['name'].upper()
    ]
    
    return jsonify({'success': True, 'results': results[:10]})


def save_stock_metrics(stock_symbol, risk_metrics):
    """Save calculated risk metrics to database"""
    
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check if metrics exist for today
        today = date.today()
        cursor.execute(
            "SELECT metric_id FROM stock_metrics WHERE stock_symbol = %s AND calculation_date = %s",
            (stock_symbol, today)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing metrics
            cursor.execute(
                """UPDATE stock_metrics SET
                   current_price = %s,
                   annual_return = %s,
                   volatility = %s,
                   annualized_volatility = %s,
                   max_drawdown = %s,
                   risk_level = %s,
                   risk_reward_ratio = %s,
                   loss_probability = %s,
                   confidence_score = %s
                   WHERE metric_id = %s""",
                (
                    risk_metrics.get('current_price'),
                    risk_metrics.get('annual_return'),
                    risk_metrics.get('volatility'),
                    risk_metrics.get('annualized_volatility'),
                    risk_metrics.get('max_drawdown'),
                    risk_metrics.get('risk_level'),
                    risk_metrics.get('risk_reward_ratio'),
                    risk_metrics.get('loss_probability'),
                    risk_metrics.get('confidence_score'),
                    existing[0]
                )
            )
        else:
            # Insert new metrics
            cursor.execute(
                """INSERT INTO stock_metrics 
                   (stock_symbol, calculation_date, current_price, annual_return,
                    volatility, annualized_volatility, max_drawdown, risk_level,
                    risk_reward_ratio, loss_probability, confidence_score)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    stock_symbol,
                    today,
                    risk_metrics.get('current_price'),
                    risk_metrics.get('annual_return'),
                    risk_metrics.get('volatility'),
                    risk_metrics.get('annualized_volatility'),
                    risk_metrics.get('max_drawdown'),
                    risk_metrics.get('risk_level'),
                    risk_metrics.get('risk_reward_ratio'),
                    risk_metrics.get('loss_probability'),
                    risk_metrics.get('confidence_score')
                )
            )
        
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Error saving stock metrics: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@stock_bp.route('/api/price/<stock_symbol>')
def get_stock_price(stock_symbol):
    """API endpoint to get current stock price"""
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data_fetcher = StockDataFetcher()
        price_data = data_fetcher.get_current_price(stock_symbol.upper())
        
        if price_data:
            return jsonify({'success': True, 'data': price_data})
        else:
            return jsonify({'success': False, 'message': 'Unable to fetch price'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
