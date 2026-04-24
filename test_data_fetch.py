"""Test script to check if stock data fetching is working"""
from services.data_fetcher import StockDataFetcher

# Initialize fetcher
print("Initializing StockDataFetcher...")
df = StockDataFetcher()

# Test 1: Fetch RELIANCE.NS historical data
print("\n=== Test 1: Fetching Historical Data for RELIANCE.NS ===")
try:
    data = df.get_historical_data('RELIANCE.NS')
    if data is not None and not data.empty:
        print(f"✓ SUCCESS! Data shape: {data.shape}")
        print(f"✓ Latest 5 rows:")
        print(data.tail())
    else:
        print("✗ FAILED: No data returned")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test 2: Fetch TCS.NS historical data
print("\n=== Test 2: Fetching Historical Data for TCS.NS ===")
try:
    data = df.get_historical_data('TCS.NS')
    if data is not None and not data.empty:
        print(f"✓ SUCCESS! Data shape: {data.shape}")
        print(f"✓ Date range: {data.index[0]} to {data.index[-1]}")
    else:
        print("✗ FAILED: No data returned")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test 3: Get stock info
print("\n=== Test 3: Getting stock info for INFY.NS ===")
try:
    info = df.get_stock_info('INFY.NS')
    if info and 'current_price' in info:
        print(f"✓ SUCCESS!")
        print(f"  Name: {info.get('name', 'N/A')}")
        print(f"  Price: ₹{info.get('current_price', 'N/A')}")
        print(f"  Sector: {info.get('sector', 'N/A')}")
    else:
        print("✗ FAILED: No info returned")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test 4: Get current price
print("\n=== Test 4: Getting current price for HDFCBANK.NS ===")
try:
    price_data = df.get_current_price('HDFCBANK.NS')
    if price_data and isinstance(price_data, dict) and 'price' in price_data:
        print(f"✓ SUCCESS! Current price: ₹{price_data['price']}")
        print(f"  Daily change: {price_data.get('daily_change', 'N/A')} ({price_data.get('daily_change_pct', 'N/A')}%)")
    else:
        print("✗ FAILED: No price returned")
except Exception as e:
    print(f"✗ ERROR: {e}")

print("\n=== All tests completed ===")

