# 🚀 QUICK START GUIDE

## Fastest Way to Get Started

### 1. Prerequisites Check
```bash
# Check Python version (need 3.8+)
python --version

# Check MySQL is running
mysql --version
```

### 2. One-Line Setup (Windows PowerShell)
```powershell
# Navigate to project
cd "f:\PROJECT'S\AK(2)"

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install everything
pip install -r requirements.txt

# Download NLP data
python -m textblob.download_corpora
```

### 3. Database Setup
```bash
# Login to MySQL
mysql -u root -p

# Run this inside MySQL:
source database/schema.sql

# Or just run:
# mysql -u root -p < database/schema.sql
```

### 4. Configure Database
Edit `config.py` line 20-24:
```python
MYSQL_USER = 'root'          # Your username
MYSQL_PASSWORD = ''          # Your password
MYSQL_DATABASE = 'stock_risk_db'
```

### 5. Run Application
```bash
python app.py
```

### 6. Open Browser
```
http://127.0.0.1:5000
```

### 7. Login
```
Username: demo_user
Password: test123
```

---

## 🎯 First Steps After Login

1. **View Dashboard** - See your portfolio overview
2. **Create Portfolio** - Click "New Portfolio" button
3. **Add Stocks** - Add some stocks:
   - RELIANCE.NS (Reliance Industries)
   - TCS.NS (Tata Consultancy)
   - INFY.NS (Infosys)
4. **View Analysis** - Click on portfolio to see risk analysis
5. **Compare Stocks** - Compare multiple stocks side-by-side
6. **Analyze Individual Stock** - Click "Analyze" on any holding

---

## ⚡ Quick Test Scenario

```
1. Login with demo_user/test123
2. Open "My Investment Portfolio"
3. Click "Add Stock"
   - Symbol: RELIANCE.NS
   - Quantity: 10
   - Price: 2450
   - Date: 2024-01-15
4. Wait for analysis to load
5. View AI recommendation
6. Check portfolio health score
```

---

## 🐛 Common Issues & Quick Fixes

### "Module not found"
```bash
pip install [module-name]
```

### "MySQL connection failed"
- Check MySQL is running
- Verify credentials in config.py
- Ensure database exists

### "No data for stock"
- Use Indian stock symbols with .NS suffix
- Examples: RELIANCE.NS, TCS.NS, INFY.NS
- Check internet connection

### "Port 5000 in use"
Change in app.py:
```python
app.run(port=5001)
```

---

## 📱 Test Stock Symbols

**Quick Test Set:**
```
RELIANCE.NS  - Reliance Industries
TCS.NS       - Tata Consultancy
HDFCBANK.NS  - HDFC Bank
INFY.NS      - Infosys
ITC.NS       - ITC Limited
```

---

## 🔥 Pro Tips

1. **Fast Data Loading**: Stocks cache for 5 minutes
2. **Multiple Portfolios**: Create different risk profiles
3. **Compare Feature**: Maximum 5 stocks at once
4. **AI Explains**: Read the detailed reasoning
5. **Risk Profile**: Change in profile settings

---

## 📊 What to Expect

- **Load Time**: 5-10 seconds for stock analysis
- **Data Source**: Real stock prices from Yahoo Finance
- **Update Frequency**: Real-time on page load
- **Sentiment**: Sample news (educational demo)

---

## 🎓 Learning Path

**Day 1**: Setup and explore UI  
**Day 2**: Understand risk metrics  
**Day 3**: Study AI recommendation logic  
**Day 4**: Analyze portfolio code  
**Day 5**: Customize and enhance  

---

## 📚 Key Files to Study

```
app.py                     → Flask app structure
routes/stock_routes.py     → Stock analysis flow
services/ai_engine.py      → AI recommendation logic
services/risk_calculator.py → Risk metrics calculation
templates/portfolio.html   → Frontend integration
```

---

## 🛠️ Customization Ideas

1. Add more risk metrics
2. Integrate real news API
3. Add export to PDF
4. Create mobile app
5. Add email notifications
6. Implement backtesting
7. Add technical indicators

---

## ⚠️ Remember

- Educational purpose only
- Not financial advice
- Use demo data for testing
- Read disclaimer before use

---

## 🆘 Need Help?

1. Check README.md for detailed docs
2. Review code comments
3. Check troubleshooting section
4. Verify all dependencies installed

---

**Ready to Start? Run:** `python app.py`

🎉 **Happy Learning!**
