import sys
sys.path.insert(0, r'F:\PROJECT\'S\AK(2)')
from services.data_fetcher import StockDataFetcher
from services.risk_calculator import RiskCalculator

print("\n🔍 Testing Compare Stocks with TCS and RELIANCE...\n")

data_fetcher = StockDataFetcher()
risk_calc = RiskCalculator()

# Test the inputs you entered
inputs = "TCS.NS,RELIANCE.NS".split(',')
symbols = [s.strip() for s in inputs if s.strip()]

print(f"Input symbols: {symbols}\n")

comparison_data = []

for symbol in symbols:
    print(f"Fetching {symbol}...")
    stock_info = data_fetcher.get_stock_info(symbol)
    historical_data = data_fetcher.get_historical_data(symbol)
    
    if stock_info and historical_data is not None and not historical_data.empty:
        print(f"✅ {symbol}: Price = ₹{stock_info.get('current_price')}, Name = {stock_info.get('name')}")
        risk_metrics = risk_calc.calculate_stock_risk(historical_data, stock_info)
        
        comparison_data.append({
            'symbol': symbol,
            'name': stock_info.get('name', symbol),
            'current_price': stock_info.get('current_price', 0),
            'metrics': risk_metrics
        })
    else:
        print(f"❌ {symbol}: Failed to fetch data")

print(f"\n📊 Total stocks fetched: {len(comparison_data)}")
for stock in comparison_data:
    print(f"   - {stock['symbol']}: {stock['name']}")

if len(comparison_data) == 2:
    print("\n✅ Both stocks fetched successfully!")
else:
    print(f"\n⚠️ Only {len(comparison_data)} stock(s) fetched")
