import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get DATABASE_URL from environment
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL not set!")
    exit(1)

print(f"📊 Connecting to: {database_url.split('@')[1][:50]}...")

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if user table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'user'
        );
    """)
    table_exists = cursor.fetchone()['exists']
    
    if not table_exists:
        print("❌ 'user' table does not exist!")
        cursor.close()
        conn.close()
        exit(1)
    
    # Get all users
    cursor.execute("""
        SELECT id, email, full_name, password_hash, is_active, created_at, last_login
        FROM "user"
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    users = cursor.fetchall()
    
    if not users:
        print("❌ No users found in database!")
    else:
        print(f"✅ Found {len(users)} users:\n")
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Full Name: {user['full_name']}")
            print(f"Password Hash: {user['password_hash'][:40]}...")
            print(f"Is Active: {user['is_active']}")
            print(f"Created: {user['created_at']}")
            print(f"Last Login: {user['last_login']}")
            print("-" * 50)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
