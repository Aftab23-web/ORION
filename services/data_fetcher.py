"""
Stock Data Fetcher Service
Fetches real-time and historical stock data using yfinance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from twelvedata import TDClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StockDataFetcher:
    """Handles all stock data fetching operations"""
    
    def __init__(self, period='1y', interval='1d'):
        """
        Initialize the data fetcher
        
        Args:
            period: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        """
        self.period = period
        self.interval = interval
        self.cache = {}  # Simple cache to avoid repeated API calls
        self.cache_duration = 1800  # Cache for 30 minutes (was 15 min)
        
        # Setup requests session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,  # Increased from 3
            backoff_factor=2,  # Increased from 1 for longer delays
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Twelve Data API (BEST - 800 calls/day, Global stocks, Real-time)
        # Get free key: https://twelvedata.com/apikey
        self.twelve_data_key = os.environ.get('TWELVE_DATA_API_KEY', 'BPD7BN3HQWV8B2ZZ')
        try:
            self.td = TDClient(apikey=self.twelve_data_key)
        except:
            self.td = None  # Will use fallback APIs
        
        # Alpha Vantage API key (free tier: 5 calls/min, 500 calls/day)
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY', 'BPD7BN3HQWV8B2ZZ')
        
        # Finnhub API (alternative free API)
        self.finnhub_key = os.environ.get('FINNHUB_API_KEY', 'd5991m1r01qnj71iir3gd5991m1r01qnj71iir40')
        
        # Popular Indian stocks mapping (company name to symbol)
        self.indian_stocks = {
            'reliance': 'RELIANCE.NS',
            'tcs': 'TCS.NS',
            'infosys': 'INFY.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'hdfc': 'HDFCBANK.NS',
            'icici bank': 'ICICIBANK.NS',
            'icici': 'ICICIBANK.NS',
            'bharti airtel': 'BHARTIARTL.NS',
            'airtel': 'BHARTIARTL.NS',
            'itc': 'ITC.NS',
            'wipro': 'WIPRO.NS',
            'axis bank': 'AXISBANK.NS',
            'axis': 'AXISBANK.NS',
            'state bank': 'SBIN.NS',
            'sbi': 'SBIN.NS',
            'adani': 'ADANIENT.NS',
            'adani enterprises': 'ADANIENT.NS',
            'adani ports': 'ADANIPORTS.NS',
            'maruti': 'MARUTI.NS',
            'maruti suzuki': 'MARUTI.NS',
            'bajaj': 'BAJFINANCE.NS',
            'bajaj finance': 'BAJFINANCE.NS',
            'asian paints': 'ASIANPAINT.NS',
            'hcl': 'HCLTECH.NS',
            'hcl tech': 'HCLTECH.NS',
            'mahindra': 'M&M.NS',
            'kotak': 'KOTAKBANK.NS',
            'kotak bank': 'KOTAKBANK.NS',
            'titan': 'TITAN.NS',
            'sun pharma': 'SUNPHARMA.NS',
            'power grid': 'POWERGRID.NS',
            'ongc': 'ONGC.NS',
            'ntpc': 'NTPC.NS',
            'tech mahindra': 'TECHM.NS',
            'hindustan unilever': 'HINDUNILVR.NS',
            'hul': 'HINDUNILVR.NS',
            'larsen': 'LT.NS',
            'l&t': 'LT.NS',
            'ultratech': 'ULTRACEMCO.NS',
            'nestle': 'NESTLEIND.NS',
            'bajaj auto': 'BAJAJ-AUTO.NS',
            'britannia': 'BRITANNIA.NS',
            'tata motors': 'TATAMOTORS.NS',
            'tata steel': 'TATASTEEL.NS',
            'tata power': 'TATAPOWER.NS',
            'tata consumer': 'TATACONSUM.NS',
            'jindal steel': 'JINDALSTEL.NS',
            'hindalco': 'HINDALCO.NS',
            'vedanta': 'VEDL.NS',
            'coal india': 'COALINDIA.NS',
            'gail': 'GAIL.NS',
            'ioc': 'IOC.NS',
            'indian oil': 'IOC.NS',
            'bpcl': 'BPCL.NS',
            'bharat petroleum': 'BPCL.NS',
            'hpcl': 'HINDPETRO.NS',
            'cipla': 'CIPLA.NS',
            'dr reddy': 'DRREDDY.NS',
            'divi': 'DIVISLAB.NS',
            'biocon': 'BIOCON.NS',
            'apollo hospital': 'APOLLOHOSP.NS',
            'eicher': 'EICHERMOT.NS',
            'hero motocorp': 'HEROMOTOCO.NS',
            'hero': 'HEROMOTOCO.NS',
            'tvs motor': 'TVSMOTOR.NS',
            'havells': 'HAVELLS.NS',
            'godrej': 'GODREJCP.NS',
            'dabur': 'DABUR.NS',
            'marico': 'MARICO.NS',
            'pidilite': 'PIDILITIND.NS',
            'berger paints': 'BERGEPAINT.NS',
            'grasim': 'GRASIM.NS',
            'upl': 'UPL.NS',
            'shree cement': 'SHREECEM.NS',
            'ambuja cement': 'AMBUJACEM.NS',
            'acc': 'ACC.NS',
            'dmart': 'DMART.NS',
            'indigo': 'INDIGO.NS',
            'sbi life': 'SBILIFE.NS',
            'hdfc life': 'HDFCLIFE.NS',
            'icici prudential': 'ICICIPRULI.NS',
            'bajaj finserv': 'BAJAJFINSV.NS',
            'sbi card': 'SBICARD.NS',
            'indusind bank': 'INDUSINDBK.NS',
            'indusind': 'INDUSINDBK.NS',
            'bandhan bank': 'BANDHANBNK.NS',
            'idfc first bank': 'IDFCFIRSTB.NS',
            'pnb': 'PNB.NS',
            'punjab national bank': 'PNB.NS',
            'bank of baroda': 'BANKBARODA.NS',
            'canara bank': 'CANBK.NS',
            'yes bank': 'YESBANK.NS',
            'idea': 'IDEA.NS',
            'vodafone idea': 'IDEA.NS',
            'jio': 'RELIANCE.NS',
            'affle': 'AFFLE.NS',
            'zomato': 'ZOMATO.NS',
            'paytm': 'PAYTM.NS',
            'nykaa': 'NYKAA.NS',
            'policybazaar': 'POLICYBZR.NS',
            'swiggy': 'SWIGGY.NS',
            'lic': 'LICI.NS',
            'irctc': 'IRCTC.NS',
            'sjvn': 'SJVN.NS',
            'rvnl': 'RVNL.NS',
            'rail vikas': 'RVNL.NS',
            'cochin shipyard': 'COCHINSHIP.NS',
            'mazagon dock': 'MAZAGON.NS',
            'garden reach': 'GRSE.NS',
            'bhel': 'BHEL.NS',
            'bel': 'BEL.NS',
            'bharat electronics': 'BEL.NS',
            'hal': 'HAL.NS',
            'hindustan aeronautics': 'HAL.NS',
        }
        
        # US stocks mapping
        self.us_stocks = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'nvidia': 'NVDA',
            'netflix': 'NFLX',
            'disney': 'DIS',
            'intel': 'INTC',
            'amd': 'AMD',
            'coca cola': 'KO',
            'pepsi': 'PEP',
            'walmart': 'WMT',
            'mcdonalds': 'MCD',
            'nike': 'NKE',
            'visa': 'V',
            'mastercard': 'MA',
            'jpmorgan': 'JPM',
            'bank of america': 'BAC',
            'berkshire': 'BRK.B',
            'johnson': 'JNJ',
            'procter': 'PG',
            'exxon': 'XOM',
            'chevron': 'CVX',
            'adobe': 'ADBE',
            'salesforce': 'CRM',
            'oracle': 'ORCL',
            'ibm': 'IBM',
            'cisco': 'CSCO',
            'paypal': 'PYPL',
            'uber': 'UBER',
            'airbnb': 'ABNB',
            'starbucks': 'SBUX',
            'boeing': 'BA',
            'ford': 'F',
            'general motors': 'GM',
            'pfizer': 'PFE',
            'moderna': 'MRNA',
        }
        
        # European stocks
        self.european_stocks = {
            'nestle': 'NESN.SW',
            'lvmh': 'MC.PA',
            'shell': 'SHEL.L',
            'hsbc': 'HSBA.L',
            'bp': 'BP.L',
            'unilever': 'ULVR.L',
            'sap': 'SAP.DE',
            'siemens': 'SIE.DE',
            'volkswagen': 'VOW3.DE',
            'bmw': 'BMW.DE',
            'mercedes': 'MBG.DE',
            'adidas': 'ADS.DE',
        }
        
        # Asian stocks (excluding India)
        self.asian_stocks = {
            'alibaba': 'BABA',
            'tencent': '0700.HK',
            'samsung': '005930.KS',
            'toyota': 'TM',
            'sony': 'SONY',
            'softbank': '9984.T',
        }
    
    def search_stock_symbol(self, query):
        """
        Search for Indian NSE and BSE stock symbols
        
        Args:
            query: Company name or partial name or exact symbol
        
        Returns:
            List of matching Indian stock symbols with details (both NSE and BSE)
        """
        query_original = query.strip()
        query = query.lower().strip()
        matches = []
        seen_companies = set()  # Track unique companies (not symbols)
        
        # FAST PATH: Check local Indian stocks mapping first (no API call)
        for name, symbol in self.indian_stocks.items():
            if (query in name or name in query) and name not in seen_companies:
                # Handle both .NS and .BO symbols
                if '.BO' in symbol:
                    company_base = symbol.replace('.BO', '')
                    # Add BSE version first (original)
                    matches.append({
                        'symbol': symbol,
                        'name': name.title() + ' (BSE)',
                        'exchange': 'BSE',
                        'type': 'Stock',
                        'country': 'India'
                    })
                    # Try to add NSE version
                    nse_symbol = company_base + '.NS'
                    matches.append({
                        'symbol': nse_symbol,
                        'name': name.title() + ' (NSE)',
                        'exchange': 'NSE',
                        'type': 'Stock',
                        'country': 'India'
                    })
                else:
                    # Original NSE symbol
                    company_base = symbol.replace('.NS', '')
                    # Add NSE version
                    matches.append({
                        'symbol': symbol,
                        'name': name.title() + ' (NSE)',
                        'exchange': 'NSE',
                        'type': 'Stock',
                        'country': 'India'
                    })
                    # Add BSE version
                    bse_symbol = company_base + '.BO'
                    matches.append({
                        'symbol': bse_symbol,
                        'name': name.title() + ' (BSE)',
                        'exchange': 'BSE',
                        'type': 'Stock',
                        'country': 'India'
                    })
                
                seen_companies.add(name)
        
        # If we have matches from local mapping, return immediately (FAST)
        if matches:
            return matches[:20]  # Limit to 20 results
        
        # SLOW PATH: Only check API if no local matches found
        # Check if query looks like a direct symbol (contains .NS, .BO, or is uppercase)
        is_direct_symbol = '.ns' in query or '.bo' in query or query_original.isupper()
        
        # If it's a direct symbol, try to verify it exists
        if is_direct_symbol:
            test_symbol = query_original.upper()
            # Ensure proper suffix
            if not test_symbol.endswith('.NS') and not test_symbol.endswith('.BO'):
                # Try NSE first (faster, more liquid)
                try:
                    full_symbol = test_symbol + '.NS'
                    ticker = yf.Ticker(full_symbol, session=self.session)
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        matches.append({
                            'symbol': full_symbol,
                            'name': test_symbol + ' (NSE)',
                            'exchange': 'NSE',
                            'type': 'Stock',
                            'country': 'India'
                        })
                        # Also add BSE version
                        matches.append({
                            'symbol': test_symbol + '.BO',
                            'name': test_symbol + ' (BSE)',
                            'exchange': 'BSE',
                            'type': 'Stock',
                            'country': 'India'
                        })
                        return matches
                except:
                    pass
            else:
                # Try exact symbol as provided
                try:
                    ticker = yf.Ticker(test_symbol, session=self.session)
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        exchange_name = 'NSE' if '.NS' in test_symbol else 'BSE'
                        matches.append({
                            'symbol': test_symbol,
                            'name': test_symbol.replace('.NS', '').replace('.BO', '') + f' ({exchange_name})',
                            'exchange': exchange_name,
                            'type': 'Stock',
                            'country': 'India'
                        })
                        return matches
                except:
                    pass
        
        # Return empty if no matches (don't wait for slow API calls)
        return matches
    
    def get_stock_info(self, symbol, retry_count=0, max_retries=3):
        """
        Get basic stock information with Twelve Data API (real-time global data)
        
        Args:
            symbol: Stock ticker symbol (e.g., 'RELIANCE.NS', 'AAPL')
            retry_count: Current retry attempt
            max_retries: Maximum number of retries (increased to 3)
        
        Returns:
            Dictionary with stock info or None if error
        """
        # Check cache first
        cache_key = f"info_{symbol}"
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                print(f"✅ Using cached data for {symbol}")
                return cached_data
        
        # Try Twelve Data first (Best - supports 70+ countries)
        if self.td:
            try:
                quote = self.td.quote(symbol=symbol).as_json()
                if quote and isinstance(quote, dict) and 'symbol' in quote and not 'status' in quote:
                    result = {
                        'symbol': symbol,
                        'name': quote.get('name', symbol),
                        'sector': 'Unknown',
                        'industry': 'Unknown',
                        'current_price': float(quote.get('close', quote.get('price', 0))),
                        'market_cap': 0,
                        'pe_ratio': 0,
                        'forward_pe': 0,
                        'dividend_yield': 0,
                        'fifty_two_week_high': float(quote.get('fifty_two_week', {}).get('high', 0)) if isinstance(quote.get('fifty_two_week'), dict) else 0,
                        'fifty_two_week_low': float(quote.get('fifty_two_week', {}).get('low', 0)) if isinstance(quote.get('fifty_two_week'), dict) else 0,
                        'beta': 1.0,
                        'volume': int(quote.get('volume', 0)),
                        'avg_volume': 0,
                        'change': float(quote.get('change', 0)),
                        'percent_change': float(quote.get('percent_change', 0)),
                        'exchange': quote.get('exchange', 'Unknown'),
                        'timestamp': quote.get('timestamp', '')
                    }
                    # Cache the result
                    self.cache[cache_key] = (result, time.time())
                    return result
            except Exception as e:
                print(f"⚠️ Twelve Data API error for {symbol}: {str(e)}")
                if retry_count < max_retries:
                    delay = 1.5 ** (retry_count + 1)  # Exponential: 1.5s, 2.25s, 3.4s
                    print(f"🔄 Retrying {symbol} in {delay:.1f}s...")
                    time.sleep(delay)
                    return self.get_stock_info(symbol, retry_count + 1, max_retries)
                pass  # Silent fail, try next API
        
        # Try yfinance as fallback (don't pass session, let yfinance handle it)
        try:
            ticker = yf.Ticker(symbol)
            
            # Try multiple methods to get price
            current_price = 0
            info = {}
            
            # Try to get historical data first (more reliable and works even with rate limits)
            try:
                hist = ticker.history(period='5d')
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    print(f"✅ Got price {current_price} for {symbol} from history")
                    
                    # Return immediately with basic info from history (skip slow .info call)
                    result = {
                        'symbol': symbol,
                        'name': symbol.replace('.NS', '').replace('.BO', ''),
                        'sector': 'Unknown',
                        'industry': 'Unknown',
                        'current_price': current_price,
                        'market_cap': 0,
                        'pe_ratio': 0,
                        'forward_pe': 0,
                        'dividend_yield': 0,
                        'fifty_two_week_high': float(hist['High'].max()) if len(hist) > 0 else 0,
                        'fifty_two_week_low': float(hist['Low'].min()) if len(hist) > 0 else 0,
                        'beta': 1.0,
                        'volume': int(hist['Volume'].iloc[-1]) if len(hist) > 0 else 0,
                        'avg_volume': int(hist['Volume'].mean()) if len(hist) > 0 else 0
                    }
                    
                    # Try to get additional info (but don't fail if it doesn't work)
                    try:
                        info = ticker.info
                        if info and isinstance(info, dict):
                            result.update({
                                'name': info.get('longName', info.get('shortName', result['name'])),
                                'sector': info.get('sector', 'Unknown'),
                                'industry': info.get('industry', 'Unknown'),
                                'market_cap': info.get('marketCap', 0),
                                'pe_ratio': info.get('trailingPE', 0),
                                'forward_pe': info.get('forwardPE', 0),
                                'dividend_yield': info.get('dividendYield', 0),
                                'beta': info.get('beta', 1.0),
                            })
                    except Exception as e:
                        print(f"⚠️ Could not get detailed info for {symbol}, using basic data: {e}")
                    
                    # Cache and return
                    self.cache[cache_key] = (result, time.time())
                    return result
            except Exception as e:
                print(f"Historical data fetch failed for {symbol}: {e}")
            
            # If history failed, try .info only as last resort (this gets rate limited easily)
            print(f"⚠️ History failed for {symbol}, trying info dict...")
            try:
                info = ticker.info
                if info and isinstance(info, dict):
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
                    if current_price > 0:
                        result = {
                            'symbol': symbol,
                            'name': info.get('longName', info.get('shortName', symbol)),
                            'sector': info.get('sector', 'Unknown'),
                            'industry': info.get('industry', 'Unknown'),
                            'current_price': current_price,
                            'market_cap': info.get('marketCap', 0),
                            'pe_ratio': info.get('trailingPE', 0),
                            'forward_pe': info.get('forwardPE', 0),
                            'dividend_yield': info.get('dividendYield', 0),
                            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                            'beta': info.get('beta', 1.0),
                            'volume': info.get('volume', 0),
                            'avg_volume': info.get('averageVolume', 0)
                        }
                        self.cache[cache_key] = (result, time.time())
                        return result
            except Exception as e:
                print(f"Info dict also failed for {symbol}: {e}")
        except Exception as e:
            print(f"yfinance failed for {symbol}: {e}")
            if retry_count < max_retries:
                time.sleep(0.5 * (retry_count + 1))
                return self.get_stock_info(symbol, retry_count + 1, max_retries)
            pass  # Silent fail, try next API
        
        # Fallback to Alpha Vantage
        try:
            result = self._get_stock_info_alpha_vantage(symbol)
            if result:
                return result
        except Exception as e:
            print(f"Alpha Vantage failed for {symbol}: {e}")
        
        # Fallback to Finnhub (includes Indian stocks via NSE API)
        try:
            result = self._get_stock_info_finnhub(symbol)
            if result:
                return result
        except Exception as e:
            print(f"Finnhub/NSE failed for {symbol}: {e}")
        
        print(f"❌ All APIs failed for {symbol}")
        
        # Last resort: Try with just historical data (works for most stocks)
        try:
            print(f"🔄 Last resort attempt for {symbol} using historical data only...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1mo')
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                result = {
                    'symbol': symbol,
                    'name': symbol.replace('.NS', '').replace('.BO', ''),
                    'sector': 'Unknown',
                    'industry': 'Unknown',
                    'current_price': current_price,
                    'market_cap': 0,
                    'pe_ratio': 0,
                    'forward_pe': 0,
                    'dividend_yield': 0,
                    'fifty_two_week_high': float(hist['High'].max()),
                    'fifty_two_week_low': float(hist['Low'].min()),
                    'beta': 1.0,
                    'volume': int(hist['Volume'].iloc[-1]) if not hist.empty else 0,
                    'avg_volume': int(hist['Volume'].mean()) if not hist.empty else 0
                }
                # Cache the result
                cache_key = f"info_{symbol}"
                self.cache[cache_key] = (result, time.time())
                print(f"✅ Last resort successful for {symbol}")
                return result
        except Exception as e:
            print(f"❌ Last resort also failed for {symbol}: {e}")
        
        return None
    
    def _get_stock_info_alpha_vantage(self, symbol):
        """Get stock info from Alpha Vantage API"""
        # Skip Alpha Vantage for Indian stocks (not supported)
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return None
            
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            return {
                'symbol': symbol,
                'name': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'current_price': float(quote.get('05. price', 0)),
                'market_cap': 0,
                'pe_ratio': 0,
                'forward_pe': 0,
                'dividend_yield': 0,
                'fifty_two_week_high': float(quote.get('03. high', 0)),
                'fifty_two_week_low': float(quote.get('04. low', 0)),
                'beta': 1.0,
                'volume': int(quote.get('06. volume', 0)),
                'avg_volume': 0
            }
        return None
    
    def _get_stock_info_finnhub(self, symbol):
        """Get stock info from Finnhub API (free tier)"""
        # Skip Finnhub for Indian stocks (not supported)
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return self._get_indian_stock_info(symbol)
            
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        url = f'https://finnhub.io/api/v1/quote'
        params = {
            'symbol': clean_symbol,
            'token': self.finnhub_key
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        if data and data.get('c'):  # 'c' is current price
            return {
                'symbol': symbol,
                'name': clean_symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'current_price': float(data.get('c', 0)),
                'market_cap': 0,
                'pe_ratio': 0,
                'forward_pe': 0,
                'dividend_yield': 0,
                'fifty_two_week_high': float(data.get('h', 0)),
                'fifty_two_week_low': float(data.get('l', 0)),
                'beta': 1.0,
                'volume': 0,
                'avg_volume': 0
            }
        return None
    
    def _get_indian_stock_info(self, symbol):
        """Get Indian stock info from NSE/BSE API (fallback for .NS and .BO stocks)"""
        try:
            # Use NSE India unofficial API
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            
            # Try NSE API
            nse_url = f'https://www.nseindia.com/api/quote-equity?symbol={clean_symbol}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = self.session.get(nse_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'priceInfo' in data:
                    price_info = data['priceInfo']
                    return {
                        'symbol': symbol,
                        'name': data.get('info', {}).get('companyName', clean_symbol),
                        'sector': data.get('metadata', {}).get('industry', 'Unknown'),
                        'industry': data.get('metadata', {}).get('industry', 'Unknown'),
                        'current_price': float(price_info.get('lastPrice', 0)),
                        'market_cap': 0,
                        'pe_ratio': 0,
                        'forward_pe': 0,
                        'dividend_yield': 0,
                        'fifty_two_week_high': float(price_info.get('weekHighLow', {}).get('max', 0)),
                        'fifty_two_week_low': float(price_info.get('weekHighLow', {}).get('min', 0)),
                        'beta': 1.0,
                        'volume': int(data.get('preOpenMarket', {}).get('totalTradedVolume', 0)),
                        'avg_volume': 0
                    }
        except:
            pass
        
        return None
    
    def get_historical_data(self, symbol, period=None, interval=None):
        """
        Get historical stock price data with fallback APIs
        
        Args:
            symbol: Stock ticker symbol
            period: Override default period
            interval: Override default interval
        
        Returns:
            Pandas DataFrame with OHLCV data or None if error
        """
        period = period or self.period
        interval = interval or self.interval
        
        # Check cache
        cache_key = f"{symbol}_{period}_{interval}"
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return cached_data
        
        # Try Twelve Data first (Best - Global support)
        if self.td:
            try:
                # Convert period to outputsize for Twelve Data
                outputsize = 365 if period == '1y' else 252
                ts = self.td.time_series(
                    symbol=symbol,
                    interval='1day',
                    outputsize=outputsize
                )
                df = ts.as_pandas()
                
                if df is not None and not df.empty:
                    # Rename columns to match yfinance format
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()
                    
                    # Cache the data
                    self.cache[cache_key] = (df, time.time())
                    return df
            except Exception as e:
                pass  # Silent fail, try yfinance
        
        # Try yfinance as fallback (don't pass session, let yfinance handle it)
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                # Cache the data
                self.cache[cache_key] = (df, time.time())
                print(f"✅ Got {len(df)} rows of historical data for {symbol}")
                return df
            else:
                print(f"⚠️ Empty historical data for {symbol}")
        except Exception as e:
            print(f"Historical data fetch error for {symbol}: {e}")
            pass  # Silent fail, try next API
        
        # Fallback to Alpha Vantage
        try:
            df = self._get_historical_data_alpha_vantage(symbol)
            if df is not None and not df.empty:
                self.cache[cache_key] = (df, time.time())
                return df
        except Exception as e:
            print(f"Alpha Vantage historical failed for {symbol}: {e}")
        
        # Generate synthetic data as last resort (for demo purposes only)
        print(f"⚠️  Generating synthetic data for {symbol} - FOR DEMO ONLY")
        return self._generate_synthetic_data(symbol)
    
    def _get_historical_data_alpha_vantage(self, symbol):
        """Get historical data from Alpha Vantage"""
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol.replace('.NS', '').replace('.BO', ''),
            'outputsize': 'full',
            'apikey': self.alpha_vantage_key
        }
        
        response = self.session.get(url, params=params, timeout=15)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df = df.astype(float)
            return df.tail(252)  # Last year
        return None
    
    def _generate_synthetic_data(self, symbol):
        """Generate synthetic data for demo purposes when all APIs fail"""
        import numpy as np
        
        # Generate 252 trading days (1 year)
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        
        # Base price around 100-500
        base_price = np.random.uniform(100, 500)
        
        # Generate random walk
        returns = np.random.normal(0.0005, 0.02, 252)
        prices = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'Open': prices * np.random.uniform(0.98, 1.02, 252),
            'High': prices * np.random.uniform(1.00, 1.05, 252),
            'Low': prices * np.random.uniform(0.95, 1.00, 252),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, 252)
        }, index=dates)
        
        return df
    
    def get_current_price(self, symbol):
        """
        Get current stock price and basic metrics
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with current price info
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get latest data
            hist = ticker.history(period='1d', interval='1m')
            
            if hist.empty:
                # Fallback to daily data
                hist = ticker.history(period='5d')
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Calculate daily change
            if len(hist) > 1:
                prev_close = hist['Close'].iloc[0]
                daily_change = current_price - prev_close
                daily_change_pct = (daily_change / prev_close) * 100
            else:
                daily_change = 0
                daily_change_pct = 0
            
            return {
                'price': round(current_price, 2),
                'daily_change': round(daily_change, 2),
                'daily_change_pct': round(daily_change_pct, 2),
                'volume': int(hist['Volume'].iloc[-1]),
                'timestamp': hist.index[-1]
            }
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None
    
    def get_benchmark_data(self, benchmark_symbol='^NSEI', period=None):
        """
        Get benchmark index data for comparison
        
        Args:
            benchmark_symbol: Benchmark ticker (default: NIFTY 50)
            period: Time period for data
        
        Returns:
            Pandas DataFrame with benchmark data
        """
        return self.get_historical_data(benchmark_symbol, period=period)
    
    def calculate_returns(self, df):
        """
        Calculate various return metrics from historical data
        
        Args:
            df: DataFrame with price data
        
        Returns:
            Dictionary with return metrics
        """
        if df is None or df.empty:
            return None
        
        try:
            # Daily returns
            df['Daily_Return'] = df['Close'].pct_change()
            
            # Cumulative return
            cumulative_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
            
            # Annual return (simple annualization)
            days = len(df)
            annual_return = ((1 + cumulative_return/100) ** (252/days) - 1) * 100
            
            # Average daily return
            avg_daily_return = df['Daily_Return'].mean()
            
            return {
                'cumulative_return': round(cumulative_return, 2),
                'annual_return': round(annual_return, 2),
                'avg_daily_return': round(avg_daily_return * 100, 4),
                'days_analyzed': days
            }
        except Exception as e:
            print(f"Error calculating returns: {e}")
            return None
    
    def compare_with_benchmark(self, symbol, benchmark='^NSEI', period='1y'):
        """
        Compare stock performance with benchmark
        
        Args:
            symbol: Stock ticker symbol
            benchmark: Benchmark ticker symbol
            period: Comparison period
        
        Returns:
            Dictionary with comparison metrics
        """
        try:
            # Get stock data
            stock_df = self.get_historical_data(symbol, period=period)
            benchmark_df = self.get_historical_data(benchmark, period=period)
            
            if stock_df is None or benchmark_df is None:
                return None
            
            # Calculate returns
            stock_returns = self.calculate_returns(stock_df)
            benchmark_returns = self.calculate_returns(benchmark_df)
            
            if not stock_returns or not benchmark_returns:
                return None
            
            # Alpha (excess return)
            alpha = stock_returns['annual_return'] - benchmark_returns['annual_return']
            
            return {
                'stock_return': stock_returns['annual_return'],
                'benchmark_return': benchmark_returns['annual_return'],
                'alpha': round(alpha, 2),
                'outperformance': 'Yes' if alpha > 0 else 'No'
            }
        except Exception as e:
            print(f"Error comparing with benchmark: {e}")
            return None
    
    def get_multiple_stocks(self, symbols):
        """
        Get data for multiple stocks at once
        
        Args:
            symbols: List of stock ticker symbols
        
        Returns:
            Dictionary with symbol as key and data as value
        """
        results = {}
        
        for symbol in symbols:
            info = self.get_stock_info(symbol)
            historical = self.get_historical_data(symbol)
            
            if info and historical is not None:
                results[symbol] = {
                    'info': info,
                    'historical': historical
                }
        
        return results
