"""Check if users exist in the database"""
import os
from app import app, db
from models import User

# Get the database type
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
print(f"📊 Database: {db_uri[:60]}...\n")

with app.app_context():
    try:
        # Check all users
        users = User.query.all()
        
        if not users:
            print("❌ NO USERS FOUND IN DATABASE!\n")
        else:
            print(f"✅ Found {len(users)} user(s):\n")
            
            for user in users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Full Name: {user.full_name}")
                print(f"Password Hash: {user.password_hash[:50]}...")
                print(f"Is Active: {user.is_active}")
                print(f"Created: {user.created_at}")
                print(f"Last Login: {user.last_login}")
                
                # Test password verification
                test_passwords = [
                    'DemoPassword@1234',
                    'testpass123',
                    'wrong@123456',
                ]
                
                print(f"\nPassword tests:")
                for test_pwd in test_passwords:
                    result = user.check_password(test_pwd)
                    print(f"  - '{test_pwd}': {result}")
                
                print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        traceback.print_exc()
