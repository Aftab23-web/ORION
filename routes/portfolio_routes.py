"""
Portfolio Routes Blueprint
Handles portfolio management, dashboard, and portfolio analysis
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
import mysql.connector
from datetime import datetime, date
from services.portfolio_analysis import PortfolioAnalyzer
from services.data_fetcher import StockDataFetcher

portfolio_bp = Blueprint('portfolio', __name__)

def get_db_connection():
    """Get database connection"""
    from app import get_db_connection as get_conn
    return get_conn()


@portfolio_bp.route('/dashboard')
def dashboard():
    """Main dashboard - shows portfolio summary and quick stats"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return render_template('dashboard.html', portfolios=[], stats={})
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get user's portfolios
        cursor.execute(
            """SELECT p.portfolio_id, p.portfolio_name, p.description, p.created_at,
                      COUNT(h.holding_id) AS total_holdings
               FROM portfolios p
               LEFT JOIN holdings h ON p.portfolio_id = h.portfolio_id
               WHERE p.user_id = %s AND p.is_active = TRUE
               GROUP BY p.portfolio_id, p.portfolio_name, p.description, p.created_at""",
            (session['user_id'],)
        )
        portfolios = cursor.fetchall()
        
        # Calculate portfolio values (convert Decimal to float)
        for portfolio in portfolios:
            cursor.execute(
                """SELECT 
                    SUM(h.quantity * h.purchase_price) AS total_invested,
                    SUM(h.quantity * COALESCE(h.current_price, h.purchase_price)) AS current_value
                   FROM holdings h
                   WHERE h.portfolio_id = %s""",
                (portfolio['portfolio_id'],)
            )
            values = cursor.fetchone()
            portfolio['total_invested'] = float(values['total_invested'] or 0)
            portfolio['current_value'] = float(values['current_value'] or 0)
            portfolio['total_return'] = portfolio['current_value'] - portfolio['total_invested']
            portfolio['return_percentage'] = (
                (portfolio['total_return'] / portfolio['total_invested'] * 100) 
                if portfolio['total_invested'] > 0 else 0
            )
        
        # Get overall stats
        cursor.execute(
            """SELECT 
                COUNT(DISTINCT p.portfolio_id) AS total_portfolios,
                COUNT(h.holding_id) AS total_holdings,
                SUM(h.quantity * h.purchase_price) AS total_invested,
                SUM(h.quantity * COALESCE(h.current_price, h.purchase_price)) AS total_value
               FROM portfolios p
               LEFT JOIN holdings h ON p.portfolio_id = h.portfolio_id
               WHERE p.user_id = %s AND p.is_active = TRUE""",
            (session['user_id'],)
        )
        stats = cursor.fetchone()
        
        # Convert Decimal to float for stats calculations
        stats['total_portfolios'] = int(stats['total_portfolios'] or 0)
        stats['total_holdings'] = int(stats['total_holdings'] or 0)
        stats['total_invested'] = float(stats['total_invested'] or 0)
        stats['total_value'] = float(stats['total_value'] or 0)
        
        if stats['total_invested']:
            stats['overall_return'] = stats['total_value'] - stats['total_invested']
            stats['return_percentage'] = (stats['overall_return'] / stats['total_invested'] * 100)
        else:
            stats['overall_return'] = 0
            stats['return_percentage'] = 0
        
        return render_template('dashboard.html', 
                             portfolios=portfolios, 
                             stats=stats,
                             risk_profile=session.get('risk_profile', 'Moderate'))
        
    except mysql.connector.Error as err:
        flash(f'Error loading dashboard: {str(err)}', 'error')
        return render_template('dashboard.html', portfolios=[], stats={})
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@portfolio_bp.route('/view/<int:portfolio_id>')
def view_portfolio(portfolio_id):
    """View detailed portfolio analysis"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('portfolio.dashboard'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verify portfolio belongs to user
        cursor.execute(
            """SELECT * FROM portfolios 
               WHERE portfolio_id = %s AND user_id = %s AND is_active = TRUE""",
            (portfolio_id, session['user_id'])
        )
        portfolio = cursor.fetchone()
        
        if not portfolio:
            flash('Portfolio not found', 'error')
            return redirect(url_for('portfolio.dashboard'))
        
        # Get holdings
        cursor.execute(
            """SELECT * FROM holdings WHERE portfolio_id = %s ORDER BY stock_symbol""",
            (portfolio_id,)
        )
        holdings = cursor.fetchall()
        
        # Update current prices using yfinance
        data_fetcher = StockDataFetcher()
        for holding in holdings:
            try:
                current_data = data_fetcher.get_current_price(holding['stock_symbol'])
                if current_data and 'price' in current_data:
                    holding['current_price'] = current_data['price']
                    # Update in database
                    cursor.execute(
                        """UPDATE holdings SET current_price = %s, updated_at = %s 
                           WHERE holding_id = %s""",
                        (current_data['price'], datetime.now(), holding['holding_id'])
                    )
                    conn.commit()
            except Exception as e:
                print(f"Error fetching price for {holding['stock_symbol']}: {e}")
            
            # Calculate holding values (convert Decimal to float for calculations)
            quantity = float(holding['quantity'])
            purchase_price = float(holding['purchase_price'])
            current_price = float(holding['current_price'] or holding['purchase_price'])
            
            holding['invested_amount'] = quantity * purchase_price
            holding['current_value'] = quantity * current_price
            holding['return_amount'] = holding['current_value'] - holding['invested_amount']
            holding['return_percentage'] = (
                (holding['return_amount'] / holding['invested_amount'] * 100)
                if holding['invested_amount'] > 0 else 0
            )
        
        # Perform portfolio analysis
        analyzer = PortfolioAnalyzer()
        analysis = analyzer.analyze_portfolio(holdings, session.get('risk_profile', 'Moderate'))
        
        return render_template('portfolio.html', 
                             portfolio=portfolio,
                             holdings=holdings,
                             analysis=analysis)
        
    except Exception as err:
        flash(f'Error loading portfolio: {str(err)}', 'error')
        return redirect(url_for('portfolio.dashboard'))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@portfolio_bp.route('/add-holding', methods=['POST'])
def add_holding():
    """Add a new stock holding to portfolio"""
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    portfolio_id = request.form.get('portfolio_id', type=int)
    stock_symbol = request.form.get('stock_symbol', '').strip().upper()
    quantity = request.form.get('quantity', type=float)
    purchase_price = request.form.get('purchase_price', type=float)
    purchase_date = request.form.get('purchase_date')
    
    # Validation
    if not all([portfolio_id, stock_symbol, quantity, purchase_price, purchase_date]):
        flash('All fields are required', 'error')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio_id))
    
    if quantity <= 0 or purchase_price <= 0:
        flash('Quantity and price must be positive', 'error')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio_id))
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio_id))
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verify portfolio belongs to user
        cursor.execute(
            """SELECT * FROM portfolios 
               WHERE portfolio_id = %s AND user_id = %s""",
            (portfolio_id, session['user_id'])
        )
        if not cursor.fetchone():
            flash('Invalid portfolio', 'error')
            return redirect(url_for('portfolio.dashboard'))
        
        # Fetch stock name and info
        data_fetcher = StockDataFetcher()
        stock_info = data_fetcher.get_stock_info(stock_symbol)
        stock_name = stock_info.get('name', stock_symbol) if stock_info else stock_symbol
        sector = stock_info.get('sector', '') if stock_info else ''
        
        # Insert holding
        cursor.execute(
            """INSERT INTO holdings 
               (portfolio_id, stock_symbol, stock_name, quantity, purchase_price, 
                purchase_date, asset_type, sector)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (portfolio_id, stock_symbol, stock_name, quantity, purchase_price, 
             purchase_date, 'Equity', sector)
        )
        conn.commit()
        
        flash(f'Successfully added {stock_symbol} to portfolio', 'success')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio_id))
        
    except mysql.connector.Error as err:
        flash(f'Error adding holding: {str(err)}', 'error')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio_id))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@portfolio_bp.route('/delete-holding/<int:holding_id>', methods=['POST'])
def delete_holding(holding_id):
    """Delete a stock holding"""
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'Database error'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get holding and verify ownership
        cursor.execute(
            """SELECT h.holding_id, h.portfolio_id, p.user_id
               FROM holdings h
               JOIN portfolios p ON h.portfolio_id = p.portfolio_id
               WHERE h.holding_id = %s""",
            (holding_id,)
        )
        holding = cursor.fetchone()
        
        if not holding or holding['user_id'] != session['user_id']:
            return jsonify({'success': False, 'message': 'Holding not found'}), 404
        
        # Delete holding
        cursor.execute("DELETE FROM holdings WHERE holding_id = %s", (holding_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Holding deleted successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@portfolio_bp.route('/create', methods=['POST'])
def create_portfolio():
    """Create a new portfolio"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    portfolio_name = request.form.get('portfolio_name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not portfolio_name:
        flash('Portfolio name is required', 'error')
        return redirect(url_for('portfolio.dashboard'))
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('portfolio.dashboard'))
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO portfolios (user_id, portfolio_name, description) 
               VALUES (%s, %s, %s)""",
            (session['user_id'], portfolio_name, description)
        )
        conn.commit()
        
        flash(f'Portfolio "{portfolio_name}" created successfully', 'success')
        return redirect(url_for('portfolio.dashboard'))
        
    except mysql.connector.Error as err:
        flash(f'Error creating portfolio: {str(err)}', 'error')
        return redirect(url_for('portfolio.dashboard'))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@portfolio_bp.route('/delete/<int:portfolio_id>')
def delete_portfolio(portfolio_id):
    """Delete a portfolio and all its holdings"""
    
    if 'user_id' not in session:
        flash('Please login to continue', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('portfolio.dashboard'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verify portfolio belongs to user
        cursor.execute(
            """SELECT portfolio_name FROM portfolios 
               WHERE portfolio_id = %s AND user_id = %s AND is_active = TRUE""",
            (portfolio_id, session['user_id'])
        )
        portfolio = cursor.fetchone()
        
        if not portfolio:
            flash('Portfolio not found or access denied', 'error')
            return redirect(url_for('portfolio.dashboard'))
        
        portfolio_name = portfolio['portfolio_name']
        
        # Soft delete: Set is_active to FALSE instead of actually deleting
        # This preserves data for potential recovery and audit purposes
        cursor.execute(
            """UPDATE portfolios SET is_active = FALSE, updated_at = %s 
               WHERE portfolio_id = %s""",
            (datetime.now(), portfolio_id)
        )
        conn.commit()
        
        # Log the deletion in audit_log
        try:
            cursor.execute(
                """INSERT INTO audit_log (user_id, action_type, action_description, ip_address) 
                   VALUES (%s, %s, %s, %s)""",
                (session['user_id'], 'DELETE_PORTFOLIO', 
                 f'Deleted portfolio: {portfolio_name} (ID: {portfolio_id})', 
                 request.remote_addr)
            )
            conn.commit()
        except:
            pass  # Don't fail if audit log fails
        
        flash(f'Portfolio "{portfolio_name}" has been deleted successfully', 'success')
        return redirect(url_for('portfolio.dashboard'))
        
    except mysql.connector.Error as err:
        flash(f'Error deleting portfolio: {str(err)}', 'error')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio_id))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
