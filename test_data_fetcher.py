import sys
sys.path.insert(0, r'F:\PROJECT\'S\AK(2)')
from services.data_fetcher import StockDataFetcher

print("\n🔍 Testing Stock Data Fetcher...\n")

# Test 1: US Stock
print("1. Testing AAPL (US Stock)...")
df = StockDataFetcher()
result = df.get_stock_info('AAPL')
if result:
    print(f"   ✅ Success! Price: ${result.get('current_price')}, Name: {result.get('name')}")
else:
    print("   ❌ Failed")

# Test 2: Indian Stock  
print("\n2. Testing RELIANCE.NS (Indian Stock)...")
result2 = df.get_stock_info('RELIANCE.NS')
if result2:
    print(f"   ✅ Success! Price: ₹{result2.get('current_price')}, Name: {result2.get('name')}")
else:
    print("   ❌ Failed")

# Test 3: Historical Data
print("\n3. Testing Historical Data for AAPL...")
hist = df.get_historical_data('AAPL')
if hist is not None and not hist.empty:
    print(f"   ✅ Success! Got {len(hist)} days of data")
    print(f"   Latest Close: ${hist['Close'].iloc[-1]:.2f}")
else:
    print("   ❌ Failed")

print("\n✅ Testing Complete!\n")
