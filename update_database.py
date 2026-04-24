"""
Quick script to add terms_accepted columns to users table
"""
import mysql.connector
from config import config

# Get database config
db_config = config['development']

try:
    # Connect to database
    conn = mysql.connector.connect(
        host=db_config.MYSQL_HOST,
        user=db_config.MYSQL_USER,
        password=db_config.MYSQL_PASSWORD,
        database=db_config.MYSQL_DATABASE,
        port=db_config.MYSQL_PORT
    )
    
    cursor = conn.cursor()
    
    print("Connected to database successfully!")
    print("Adding terms_accepted columns to users table...")
    
    # Add columns
    try:
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN terms_accepted BOOLEAN DEFAULT FALSE AFTER is_active
        """)
        print("✓ Added terms_accepted column")
    except mysql.connector.Error as e:
        if "Duplicate column name" in str(e):
            print("✓ terms_accepted column already exists")
        else:
            raise
    
    try:
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN terms_accepted_at TIMESTAMP NULL AFTER terms_accepted
        """)
        print("✓ Added terms_accepted_at column")
    except mysql.connector.Error as e:
        if "Duplicate column name" in str(e):
            print("✓ terms_accepted_at column already exists")
        else:
            raise
    
    conn.commit()
    
    # Verify
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    
    print("\nCurrent users table structure:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]})")
    
    print("\n✅ Database update completed successfully!")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"❌ Database error: {err}")
except Exception as e:
    print(f"❌ Error: {e}")
