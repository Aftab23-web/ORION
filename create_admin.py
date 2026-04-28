"""
Script to create admin user account
"""
import mysql.connector
import bcrypt
from config import Config

# Create admin user
def create_admin_user():
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    
    cursor = conn.cursor()
    
    # Admin credentials
    admin_email = 'ankitmor@2004gmail.com'
    admin_username = 'AdminAnkit'
    admin_password = 'ankit@2004'
    admin_full_name = 'Ankit Mor (Admin)'
    
    # Hash password
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
    
    # Check if admin already exists
    cursor.execute("SELECT user_id FROM users WHERE email = %s", (admin_email,))
    existing_admin = cursor.fetchone()
    
    if existing_admin:
        print(f" Admin user already exists with email: {admin_email}")
        print(f"   Username: AdminAnkit")
        print(f"   Password: ankit@2004")
        cursor.close()
        conn.close()
        return
    
    # Create admin user
    try:
        cursor.execute(
            """INSERT INTO users 
               (username, email, password_hash, full_name, risk_profile, is_active, terms_accepted) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (admin_username, admin_email, hashed_password.decode('utf-8'), 
             admin_full_name, 'Conservative', 1, 1)
        )
        conn.commit()
        print(" Admin user created successfully!")
        print(f"\n Email: {admin_email}")
        print(f" Username: {admin_username}")
        print(f" Password: {admin_password}")
        print(f"\n You can now login with either username or email!")
        
    except mysql.connector.Error as err:
        print(f" Error creating admin user: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_admin_user()
