"""
ORION (Operational Risk and Investment Optimization Network)
Main Flask Application Entry Point
"""

from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
import mysql.connector
from config import config
import os

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize Flask-Session
Session(app)

# Database connection helper
def get_db_connection():
    """Create and return a MySQL database connection"""
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE'],
            port=app.config['MYSQL_PORT']
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.portfolio_routes import portfolio_bp
from routes.stock_routes import stock_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
app.register_blueprint(stock_bp, url_prefix='/stock')

# Root route
@app.route('/')
def index():
    """Landing page - redirect to dashboard if logged in, else login page"""
    if 'user_id' in session:
        return redirect(url_for('portfolio.dashboard'))
    return redirect(url_for('auth.login'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', 
                         error_code=500, 
                         error_message='Internal server error'), 500

# Template context processors
@app.context_processor
def inject_app_info():
    """Inject app info into all templates"""
    return {
        'app_name': app.config['APP_NAME'],
        'app_version': app.config['APP_VERSION'],
        'disclaimer_short': '⚠️ Educational Purpose Only - Not Financial Advice'
    }

# Before request hook to check authentication
@app.before_request
def check_auth():
    """Check if user needs to be authenticated"""
    from flask import request
    
    # List of routes that don't require authentication
    public_routes = ['auth.login', 'auth.register', 'static', 'auth.terms_and_conditions', 'auth.accept_terms']
    
    # Check if route requires authentication
    if request.endpoint and request.endpoint not in public_routes:
        if not request.endpoint.startswith('auth.'):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            # Check if user has accepted terms (only for logged-in users)
            if 'user_id' in session and not session.get('terms_accepted', False):
                # Allow access to terms pages
                if request.endpoint not in ['auth.terms_and_conditions', 'auth.accept_terms', 'auth.logout']:
                    return redirect(url_for('auth.terms_and_conditions'))

if __name__ == '__main__':
    print("=" * 60)
    print("ORION (Operational Risk and Investment Optimization Network)")
    print("=" * 60)
    print("⚠️  EDUCATIONAL PURPOSE ONLY - NOT FINANCIAL ADVICE")
    print("=" * 60)
    print(f"Environment: {env}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(f"Database: {app.config['MYSQL_DATABASE']}")
    print("=" * 60)
    print("Starting Flask application...")
    print("Access the app at: http://127.0.0.1:5000")
    print("=" * 60)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
