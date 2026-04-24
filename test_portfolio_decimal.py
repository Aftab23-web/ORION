"""Test portfolio calculations with Decimal values"""
from decimal import Decimal
from services.portfolio_analysis import PortfolioAnalyzer

# Mock holdings with Decimal values (like from MySQL)
holdings = [
    {
        'holding_id': 1,
        'stock_symbol': 'RELIANCE.NS',
        'quantity': Decimal('10'),
        'purchase_price': Decimal('2500.50'),
        'current_price': Decimal('2650.00'),
        'sector': 'Energy',
        'asset_type': 'Equity'
    },
    {
        'holding_id': 2,
        'stock_symbol': 'TCS.NS',
        'quantity': Decimal('5'),
        'purchase_price': Decimal('3200.00'),
        'current_price': Decimal('3450.75'),
        'sector': 'Technology',
        'asset_type': 'Equity'
    },
    {
        'holding_id': 3,
        'stock_symbol': 'INFY.NS',
        'quantity': Decimal('8'),
        'purchase_price': Decimal('1500.00'),
        'current_price': Decimal('1621.60'),
        'sector': 'Technology',
        'asset_type': 'Equity'
    }
]

print("Testing portfolio analysis with Decimal values...")
print("=" * 60)

# Test 1: Basic calculations
print("\nTest 1: Basic Portfolio Calculations")
try:
    total_invested = sum(float(h['quantity']) * float(h['purchase_price']) for h in holdings)
    total_current = sum(float(h['quantity']) * float(h['current_price']) for h in holdings)
    print(f"✓ Total Invested: ₹{total_invested:,.2f}")
    print(f"✓ Total Current: ₹{total_current:,.2f}")
    print(f"✓ Total Return: ₹{total_current - total_invested:,.2f}")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test 2: Portfolio Analyzer
print("\nTest 2: Portfolio Analyzer")
try:
    analyzer = PortfolioAnalyzer()
    result = analyzer.analyze_portfolio(holdings, 'Moderate')
    
    if result:
        print(f"✓ Analysis completed successfully")
        print(f"  Total Invested: ₹{result['total_invested']:,.2f}")
        print(f"  Total Current: ₹{result['total_current']:,.2f}")
        print(f"  Return: {result['return_percentage']:.2f}%")
        print(f"  Health Score: {result['health_score']}/100")
        print(f"  Diversification: {result['diversification']['status']}")
    else:
        print("✗ No analysis result")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("All tests completed!")
