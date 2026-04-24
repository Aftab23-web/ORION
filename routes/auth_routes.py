"""
Authentication Routes Blueprint
Handles user registration, login, logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import mysql.connector
import bcrypt
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    """Get database connection"""
    from app import get_db_connection as get_conn
    return get_conn()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler"""
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        risk_profile = request.form.get('risk_profile', 'Moderate')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not email or '@' not in email:
            errors.append('Valid email address is required')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if risk_profile not in ['Conservative', 'Moderate', 'Aggressive']:
            errors.append('Invalid risk profile selected')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user into database
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again.', 'error')
            return render_template('register.html')
        
        try:
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute(
                "SELECT user_id FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Username or email already exists', 'error')
                return render_template('register.html')
            
            # Insert new user
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, full_name, risk_profile) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (username, email, password_hash.decode('utf-8'), full_name, risk_profile)
            )
            conn.commit()
            
            # Get the new user's ID
            user_id = cursor.lastrowid
            
            # Create a default portfolio for the new user
            cursor.execute(
                """INSERT INTO portfolios (user_id, portfolio_name, description) 
                   VALUES (%s, %s, %s)""",
                (user_id, 'My Portfolio', 'Default investment portfolio')
            )
            conn.commit()
            
            # Log the registration
            cursor.execute(
                """INSERT INTO audit_log (user_id, action_type, action_description, ip_address) 
                   VALUES (%s, %s, %s, %s)""",
                (user_id, 'REGISTER', f'New user registered: {username}', request.remote_addr)
            )
            conn.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except mysql.connector.Error as err:
            flash(f'Registration failed: {str(err)}', 'error')
            return render_template('register.html')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler"""
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        # Check if admin login
        if username == 'ankitmor@2004gmail.com' and password == 'ankit@2004':
            session['is_admin'] = True
            session['username'] = 'Admin'
            session['full_name'] = 'Administrator'
            session.permanent = True
            flash('Welcome Admin!', 'success')
            return redirect(url_for('auth.admin_dashboard'))
        
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again.', 'error')
            return render_template('login.html')
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get user from database (check both username and email)
            cursor.execute(
                """SELECT user_id, username, email, password_hash, full_name, risk_profile, is_active, terms_accepted 
                   FROM users WHERE username = %s OR email = %s""",
                (username, username)
            )
            user = cursor.fetchone()
            
            if not user:
                flash('Invalid username or password', 'error')
                return render_template('login.html')
            
            if not user['is_active']:
                flash('Account is inactive. Please contact support.', 'error')
                return render_template('login.html')
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                flash('Invalid username or password', 'error')
                return render_template('login.html')
            
            # Check if this is the admin user
            is_admin = (user['email'] == 'ankitmor@2004gmail.com')
            
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE user_id = %s",
                (datetime.now(), user['user_id'])
            )
            conn.commit()
            
            # Log the login
            cursor.execute(
                """INSERT INTO audit_log (user_id, action_type, action_description, ip_address) 
                   VALUES (%s, %s, %s, %s)""",
                (user['user_id'], 'LOGIN', f'User logged in: {username}', request.remote_addr)
            )
            conn.commit()
            
            # Set session variables
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['risk_profile'] = user['risk_profile']
            session['terms_accepted'] = user['terms_accepted']
            session['is_admin'] = is_admin
            session.permanent = True
            
            # Check if user has accepted terms
            if not user['terms_accepted']:
                return redirect(url_for('auth.terms_and_conditions'))
            
            # Redirect admin to admin dashboard
            if is_admin:
                flash(f'Welcome back, Administrator!', 'success')
                return redirect(url_for('auth.admin_dashboard'))
            
            flash(f'Welcome back, {user["full_name"] or username}!', 'success')
            return redirect(url_for('portfolio.dashboard'))
            
        except mysql.connector.Error as err:
            flash(f'Login failed: {str(err)}', 'error')
            return render_template('login.html')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """User logout handler"""
    
    # Log the logout
    if 'user_id' in session:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO audit_log (user_id, action_type, action_description, ip_address) 
                       VALUES (%s, %s, %s, %s)""",
                    (session['user_id'], 'LOGOUT', f'User logged out: {session["username"]}', request.remote_addr)
                )
                conn.commit()
            except:
                pass
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
    
    # Check if admin is logging out
    is_admin = session.get('is_admin', False)
    
    # Clear session
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard showing user statistics"""
    
    # Check if user is admin
    if not session.get('is_admin', False):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get total users count
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()['total_users']
        
        # Get active users count (logged in within last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as active_users 
            FROM users 
            WHERE last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        active_users = cursor.fetchone()['active_users']
        
        # Get new users this month
        cursor.execute("""
            SELECT COUNT(*) as new_users 
            FROM users 
            WHERE created_at >= DATE_FORMAT(NOW(), '%Y-%m-01')
        """)
        new_users_this_month = cursor.fetchone()['new_users']
        
        # Get all users with their login information
        cursor.execute("""
            SELECT user_id, username, email, full_name, risk_profile, 
                   created_at, last_login, is_active, terms_accepted
            FROM users 
            ORDER BY last_login DESC, created_at DESC
        """)
        all_users = cursor.fetchall()
        
        # Get recent login activity from audit_log
        cursor.execute("""
            SELECT al.timestamp, al.action_type, al.action_description, 
                   al.ip_address, u.username, u.email
            FROM audit_log al
            LEFT JOIN users u ON al.user_id = u.user_id
            WHERE al.action_type IN ('LOGIN', 'LOGOUT')
            ORDER BY al.timestamp DESC
            LIMIT 50
        """)
        recent_activity = cursor.fetchall()
        
        # Get login statistics by day for the last 30 days
        cursor.execute("""
            SELECT DATE(timestamp) as login_date, 
                   COUNT(DISTINCT user_id) as unique_logins,
                   COUNT(*) as total_logins
            FROM audit_log
            WHERE action_type = 'LOGIN' 
              AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(timestamp)
            ORDER BY login_date DESC
        """)
        login_stats = cursor.fetchall()
        
        return render_template('admin_dashboard.html',
                             total_users=total_users,
                             active_users=active_users,
                             new_users_this_month=new_users_this_month,
                             all_users=all_users,
                             recent_activity=recent_activity,
                             login_stats=login_stats)
        
    except mysql.connector.Error as err:
        flash(f'Error loading admin dashboard: {str(err)}', 'error')
        return redirect(url_for('auth.login'))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile page - view and update profile"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # Update profile
        full_name = request.form.get('full_name', '').strip()
        risk_profile = request.form.get('risk_profile')
        
        if risk_profile not in ['Conservative', 'Moderate', 'Aggressive']:
            flash('Invalid risk profile selected', 'error')
            return redirect(url_for('auth.profile'))
        
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error', 'error')
            return redirect(url_for('auth.profile'))
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE users SET full_name = %s, risk_profile = %s 
                   WHERE user_id = %s""",
                (full_name, risk_profile, session['user_id'])
            )
            conn.commit()
            
            # Update session
            session['full_name'] = full_name
            session['risk_profile'] = risk_profile
            
            flash('Profile updated successfully', 'success')
            return redirect(url_for('auth.profile'))
            
        except mysql.connector.Error as err:
            flash(f'Update failed: {str(err)}', 'error')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    # Get user data
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('portfolio.dashboard'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT username, email, full_name, risk_profile, created_at, last_login 
               FROM users WHERE user_id = %s""",
            (session['user_id'],)
        )
        user_data = cursor.fetchone()
        
        return render_template('profile.html', user=user_data)
        
    except mysql.connector.Error as err:
        flash(f'Error loading profile: {str(err)}', 'error')
        return redirect(url_for('portfolio.dashboard'))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@auth_bp.route('/terms-and-conditions')
def terms_and_conditions():
    """Display terms and conditions page"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('terms_and_conditions.html')


@auth_bp.route('/accept-terms', methods=['POST'])
def accept_terms():
    """Handle terms and conditions acceptance"""
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('auth.terms_and_conditions'))
    
    try:
        cursor = conn.cursor()
        
        # Update user's terms acceptance
        cursor.execute(
            """UPDATE users SET terms_accepted = TRUE, terms_accepted_at = %s 
               WHERE user_id = %s""",
            (datetime.now(), session['user_id'])
        )
        conn.commit()
        
        # Update session
        session['terms_accepted'] = True
        
        # Log the acceptance
        cursor.execute(
            """INSERT INTO audit_log (user_id, action_type, action_description, ip_address) 
               VALUES (%s, %s, %s, %s)""",
            (session['user_id'], 'TERMS_ACCEPTED', 'User accepted terms and conditions', request.remote_addr)
        )
        conn.commit()
        
        flash('Terms and conditions accepted. Welcome!', 'success')
        return redirect(url_for('portfolio.dashboard'))
        
    except mysql.connector.Error as err:
        flash(f'Error accepting terms: {str(err)}', 'error')
        return redirect(url_for('auth.terms_and_conditions'))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
