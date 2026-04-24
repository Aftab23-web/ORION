# 📊 ORION (Operational Risk and Investment Optimization Network)

## ⚠️ IMPORTANT DISCLAIMER
**THIS PROJECT IS FOR EDUCATIONAL PURPOSES ONLY**

- NOT financial advice
- NOT for real trading
- NOT investment recommendations
- Use at your own risk

Always consult qualified financial advisors before making investment decisions.

---

## 🎯 Project Overview

A comprehensive full-stack web application that demonstrates:
- **Data Science & AI**: Risk analysis, predictive modeling, sentiment analysis
- **Web Development**: Flask, MySQL, RESTful architecture
- **Financial Analysis**: Portfolio management, stock risk metrics
- **Machine Learning**: Rule-based explainable AI system
- **NLP**: Sentiment analysis using TextBlob

### Key Features

✅ **User Authentication**
- Secure registration and login
- Risk profile selection (Conservative/Moderate/Aggressive)
- Session management

✅ **Portfolio Management**
- Create multiple portfolios
- Add/remove stock holdings
- Real-time price updates via yfinance
- Portfolio performance tracking

✅ **Stock Risk Analysis**
- Volatility calculation
- Maximum drawdown
- Sharpe & Sortino ratios
- Value at Risk (VaR)
- Risk-reward ratio
- Fundamental health score

✅ **Portfolio Risk Analysis**
- Overall portfolio risk score
- Asset allocation analysis
- Sector exposure
- Diversification metrics
- Correlation analysis
- Concentration risk assessment
- Portfolio health score (0-100)

✅ **AI Recommendations**
- Rule-based Buy/Hold/Sell signals
- Explainable AI with detailed reasoning
- Risk profile alignment
- Confidence scores
- Educational warnings

✅ **Market Sentiment Analysis**
- NLP-based sentiment scoring
- News headline analysis (demo)
- Positive/Neutral/Negative classification

✅ **Visualizations**
- Interactive price charts (Chart.js)
- Asset allocation pie charts
- Sector exposure bar charts

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**
- **Flask 2.3.3** - Web framework
- **MySQL** - Database
- **SQLAlchemy** - ORM (optional)

### Data & AI
- **yfinance** - Stock data fetching
- **Pandas & NumPy** - Data manipulation
- **scikit-learn** - ML utilities
- **TextBlob** - NLP sentiment analysis
- **SciPy** - Statistical calculations

### Frontend
- **HTML5 & CSS3**
- **Tailwind CSS** - UI framework
- **JavaScript (Vanilla)** - Client-side logic
- **Chart.js** - Data visualization

### Security
- **bcrypt** - Password hashing
- **Flask-Session** - Session management

---

## 📁 Project Structure

```
project-root/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
│
├── database/
│   └── schema.sql                  # MySQL database schema
│
├── routes/
│   ├── auth_routes.py              # Authentication routes
│   ├── portfolio_routes.py         # Portfolio management routes
│   └── stock_routes.py             # Stock analysis routes
│
├── services/
│   ├── data_fetcher.py             # Stock data fetching (yfinance)
│   ├── risk_calculator.py          # Risk metrics calculation
│   ├── portfolio_analysis.py       # Portfolio-level analysis
│   ├── ai_engine.py                # Rule-based AI recommendations
│   └── sentiment_analysis.py       # NLP sentiment analysis
│
└── templates/
    ├── base.html                   # Base template
    ├── login.html                  # Login page
    ├── register.html               # Registration page
    ├── dashboard.html              # Main dashboard
    ├── portfolio.html              # Portfolio details
    ├── stock_analysis.html         # Stock analysis page
    ├── compare_stocks.html         # Stock comparison
    ├── profile.html                # User profile
    ├── disclaimer.html             # Disclaimer page
    └── error.html                  # Error page
```

---

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **MySQL Server**
   - Download from: https://dev.mysql.com/downloads/
   - Or use XAMPP/WAMP/MAMP

3. **pip** (Python package manager)

### Step 1: Clone or Extract Project

```bash
cd "f:/PROJECT'S/AK(2)"
```

### Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**If you encounter errors, install individually:**
```bash
pip install Flask==2.3.3
pip install Flask-Session==0.5.0
pip install mysql-connector-python==8.1.0
pip install pandas==2.1.0
pip install numpy==1.25.2
pip install yfinance==0.2.28
pip install scikit-learn==1.3.0
pip install textblob==0.17.1
pip install bcrypt==4.0.1
pip install scipy==1.11.2
```

**Download NLTK data (for TextBlob):**
```bash
python -m textblob.download_corpora
```

### Step 4: Setup MySQL Database

1. **Start MySQL Server**

2. **Create Database**
   ```bash
   mysql -u root -p
   ```
   
   Then run:
   ```sql
   source database/schema.sql
   ```
   
   **OR** Import using MySQL Workbench:
   - Open MySQL Workbench
   - Connect to your server
   - File → Run SQL Script
   - Select `database/schema.sql`

3. **Update Database Credentials**
   
   Edit `config.py`:
   ```python
   MYSQL_USER = 'root'              # Your MySQL username
   MYSQL_PASSWORD = 'your_password' # Your MySQL password
   MYSQL_DATABASE = 'stock_risk_db'
   MYSQL_HOST = 'localhost'
   MYSQL_PORT = 3306
   ```

### Step 5: Run the Application

```bash
python app.py
```

You should see:
```
======================================================================
ORION (Operational Risk and Investment Optimization Network)
======================================================================
⚠️  EDUCATIONAL PURPOSE ONLY - NOT FINANCIAL ADVICE
======================================================================
Environment: development
Debug Mode: True
Database: stock_risk_db
======================================================================
Starting Flask application...
Access the app at: http://127.0.0.1:5000
======================================================================
```

### Step 6: Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 👤 Demo Login Credentials

```
Username: demo_user
Password: test123
```

---

## 📖 How to Use

### 1. Register/Login
- Create a new account or use demo credentials
- Select your risk profile (Conservative/Moderate/Aggressive)

### 2. Create Portfolio
- Click "New Portfolio" on dashboard
- Name your portfolio and add description

### 3. Add Stocks
- Open a portfolio
- Click "Add Stock"
- Enter stock symbol (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`)
- Provide quantity, purchase price, and date

### 4. View Analysis
- Portfolio health score
- Risk metrics
- Asset allocation
- Sector exposure
- AI recommendations

### 5. Analyze Individual Stocks
- Click "Analyze" next to any stock
- View detailed risk analysis
- Get AI Buy/Hold/Sell recommendation
- See sentiment analysis

### 6. Compare Stocks
- Navigate to "Compare Stocks"
- Enter 2-5 stock symbols
- View side-by-side comparison

---

## 🎓 Educational Value

### Learning Objectives

This project demonstrates:

1. **Full-Stack Web Development**
   - Flask application architecture
   - RESTful API design
   - Session management
   - Form handling and validation

2. **Database Design**
   - Normalized schema design
   - Foreign key relationships
   - Views and stored procedures
   - Data integrity constraints

3. **Data Science**
   - Pandas DataFrames
   - NumPy arrays
   - Statistical calculations
   - Time series analysis

4. **Financial Analysis**
   - Risk metrics calculation
   - Portfolio theory
   - Diversification analysis
   - Correlation analysis

5. **Machine Learning & AI**
   - Rule-based expert systems
   - Explainable AI
   - Feature engineering
   - Confidence scoring

6. **Natural Language Processing**
   - Sentiment analysis
   - Text classification
   - TextBlob library usage

7. **Frontend Development**
   - Responsive design
   - Tailwind CSS
   - JavaScript DOM manipulation
   - Chart.js integration

---

## 🧮 Risk Metrics Explained

### Volatility
- Standard deviation of daily returns
- Annualized: `daily_volatility × √252`
- Higher = More risk

### Sharpe Ratio
- Risk-adjusted return metric
- `(Return - Risk_Free_Rate) / Volatility`
- Higher = Better risk-adjusted performance

### Maximum Drawdown
- Largest peak-to-trough decline
- Measures worst-case loss scenario

### Value at Risk (VaR)
- Maximum expected loss at 95% confidence
- 5% chance of losing more than VaR

### Beta
- Volatility relative to market
- Beta > 1: More volatile than market
- Beta < 1: Less volatile than market

### Risk-Reward Ratio
- Average gain divided by average loss
- Higher = Better reward for risk taken

---

## 🤖 AI Explanation

### Rule-Based System

The AI is **NOT** a black-box neural network. It's a transparent rule-based expert system that:

1. **Evaluates Multiple Factors**:
   - Sharpe ratio
   - Volatility
   - Returns
   - Drawdown
   - Fundamental health
   - Risk-reward ratio

2. **Assigns Scores**:
   - Buy score (0-100)
   - Hold score (0-100)
   - Sell score (0-100)

3. **Makes Decision**:
   - Highest score wins
   - Provides detailed explanation
   - Shows all reasoning

4. **Explainable Output**:
   - Lists all factors considered
   - Explains why decision was made
   - Shows confidence level
   - Provides educational warnings

---

## 📊 Database Schema Highlights

### Tables

1. **users** - User authentication and profiles
2. **portfolios** - Portfolio metadata
3. **holdings** - Individual stock positions
4. **stock_metrics** - Calculated risk metrics
5. **portfolio_metrics** - Portfolio-level metrics
6. **ai_recommendations** - AI suggestions log
7. **market_sentiment** - Sentiment analysis results
8. **audit_log** - System activity tracking

### Key Features

- Foreign key constraints
- Indexed columns for performance
- Views for common queries
- Stored procedures for complex operations

---

## 🔒 Security Features

1. **Password Security**
   - Bcrypt hashing
   - Salt generation
   - No plaintext storage

2. **Session Management**
   - Secure session cookies
   - HttpOnly flag
   - Session timeouts

3. **SQL Injection Prevention**
   - Parameterized queries
   - Input validation

4. **XSS Protection**
   - Template escaping
   - Content Security Policy headers

---

## 🐛 Troubleshooting

### MySQL Connection Error
```
Error: Access denied for user 'root'@'localhost'
```
**Solution**: Update MySQL credentials in `config.py`

### yfinance Data Error
```
Error: No data found for symbol
```
**Solution**: 
- Ensure stock symbol is correct (use `.NS` for NSE)
- Check internet connection
- Try different symbol

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: 
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process using port 5000

### TextBlob Error
```
LookupError: Resource not found
```
**Solution**: 
```bash
python -m textblob.download_corpora
```

---

## 📝 Assignment/Project Submission Guide

### For Students/Interns

This project is ideal for:
- Final year projects
- Internship demonstrations
- Portfolio showcase
- Learning full-stack development

### What to Highlight

1. **Technical Skills**
   - Python programming
   - Web development (Flask)
   - Database design (MySQL)
   - Frontend development
   - API integration

2. **Domain Knowledge**
   - Financial analysis
   - Risk management
   - Portfolio theory
   - Statistical analysis

3. **Problem Solving**
   - Data processing pipelines
   - Real-time data fetching
   - Complex calculations
   - User experience design

### Possible Enhancements

1. **Advanced Features**
   - Machine learning models (LSTM for prediction)
   - Live news feed integration
   - Email notifications
   - PDF report generation

2. **Scalability**
   - Redis caching
   - Background task queues (Celery)
   - API rate limiting
   - Load balancing

3. **DevOps**
   - Docker containerization
   - CI/CD pipeline
   - Cloud deployment (AWS/Azure)
   - Monitoring and logging

---

## 📚 Further Reading

### Financial Concepts
- Modern Portfolio Theory
- Capital Asset Pricing Model (CAPM)
- Efficient Market Hypothesis
- Risk-Return Tradeoff

### Technical Resources
- Flask Documentation: https://flask.palletsprojects.com/
- yfinance: https://pypi.org/project/yfinance/
- Pandas: https://pandas.pydata.org/
- Chart.js: https://www.chartjs.org/

---

## ⚖️ License & Usage

### Academic Use: ✅ Allowed
- University projects
- Learning purposes
- Portfolio demonstrations

### Commercial Use: ❌ Not Recommended
- This is a simplified educational system
- Not suitable for production trading
- Lacks necessary regulatory compliance

---

## 🤝 Contributing

This is an educational project. Feel free to:
- Fork and modify
- Add new features
- Improve algorithms
- Enhance UI/UX

---

## 📧 Support

For questions about this project:
1. Review the code comments
2. Check troubleshooting section
3. Refer to documentation links

---

## 🏆 Project Highlights

### What Makes This Project Special

1. **Complete Full-Stack**: Frontend, backend, database, and ML
2. **Real-World Application**: Actual stock market data
3. **Educational Focus**: Explainable AI, not black-box
4. **Production-Ready Code**: Proper structure, error handling
5. **Scalable Architecture**: Blueprint pattern, service layer
6. **Security Best Practices**: Authentication, session management
7. **Professional UI**: Modern, responsive design

---

## 📊 Demo Stock Symbols (Indian Market)

**Use these symbols for testing:**

- **IT**: TCS.NS, INFY.NS, WIPRO.NS
- **Banking**: HDFCBANK.NS, ICICIBANK.NS, SBIN.NS
- **Energy**: RELIANCE.NS, ONGC.NS
- **FMCG**: HINDUNILVR.NS, ITC.NS
- **Auto**: TATAMOTORS.NS, M&M.NS

**Format**: Use `.NS` suffix for NSE (National Stock Exchange) stocks

---

## 🎯 Success Criteria

This project successfully demonstrates:

✅ Data fetching from external APIs  
✅ Complex calculations and algorithms  
✅ Database design and management  
✅ User authentication and authorization  
✅ RESTful API architecture  
✅ Frontend-backend integration  
✅ Data visualization  
✅ Error handling and validation  
✅ Security best practices  
✅ Code organization and modularity  
✅ Documentation and comments  

---

## 📅 Project Timeline

**Estimated development time**: 40-60 hours

- Database design: 4 hours
- Backend services: 20 hours
- Frontend templates: 12 hours
- Testing & debugging: 8 hours
- Documentation: 6 hours

---

## 🌟 Final Note

This project is a **learning tool** that brings together multiple technologies to solve a real-world problem. While it uses actual stock data and realistic calculations, it should **never** be used for real financial decisions.

The goal is to:
- Learn full-stack development
- Understand financial analysis
- Practice data science
- Build a portfolio project
- Gain practical experience

**Remember**: Always do your own research and consult professionals before making investment decisions!

---

**Built with ❤️ for education**

*Version 1.0.0 - December 2025*
