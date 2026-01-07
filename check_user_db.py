#!/usr/bin/env python3
"""
Quick diagnostic to check if user was created in database
"""
import os
import sys
from app import app, db
from models import User

with app.app_context():
    # Check database path
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"\n📊 Database: {db_uri}")
    
    # Check if user exists
    email = 'gaurav0133@gmail.com'
    user = User.query.filter_by(email=email.lower()).first()
    
    if user:
        print(f"\n✅ User found:")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Full Name: {user.full_name}")
        print(f"   Created: {user.created_at}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Password Hash: {user.password_hash[:20]}...")
        
        # Test password
        test_password = 'DemoPassword@1234'
        password_valid = user.check_password(test_password)
        print(f"   Password Valid: {password_valid}")
        
    else:
        print(f"\n❌ User NOT found with email: {email}")
        print(f"\nAll users in database:")
        all_users = User.query.all()
        if all_users:
            for u in all_users:
                print(f"   - {u.email}")
        else:
            print("   (no users)")
