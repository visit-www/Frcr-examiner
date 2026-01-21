#!/usr/bin/env python3
"""
Migration Script: Add profile_pic_url and profile_pic_public_id columns to User table
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app, db
from sqlalchemy import text

def add_profile_pic_columns():
    """Add profile picture columns to User table"""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'profile_pic_url' in columns and 'profile_pic_public_id' in columns:
                print("✅ Columns already exist. No migration needed.")
                return
            
            print("🔄 Adding profile_pic_url and profile_pic_public_id columns to User table...")
            
            # Get database URL to determine database type
            db_url = str(db.engine.url)
            
            if 'sqlite' in db_url.lower():
                # SQLite migration
                with db.engine.connect() as conn:
                    # Check if columns exist
                    result = conn.execute(text("PRAGMA table_info(user)"))
                    existing_columns = [row[1] for row in result]
                    
                    if 'profile_pic_url' not in existing_columns:
                        conn.execute(text("ALTER TABLE user ADD COLUMN profile_pic_url VARCHAR(500)"))
                        conn.commit()
                        print("  ✅ Added profile_pic_url column")
                    
                    if 'profile_pic_public_id' not in existing_columns:
                        conn.execute(text("ALTER TABLE user ADD COLUMN profile_pic_public_id VARCHAR(255)"))
                        conn.commit()
                        print("  ✅ Added profile_pic_public_id column")
                    
                    print("✅ Migration complete!")
            else:
                # PostgreSQL migration
                with db.engine.connect() as conn:
                    # Check if columns exist
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'user' 
                        AND column_name IN ('profile_pic_url', 'profile_pic_public_id')
                    """))
                    existing_columns = [row[0] for row in result]
                    
                    if 'profile_pic_url' not in existing_columns:
                        conn.execute(text("ALTER TABLE \"user\" ADD COLUMN profile_pic_url VARCHAR(500)"))
                        conn.commit()
                        print("  ✅ Added profile_pic_url column")
                    
                    if 'profile_pic_public_id' not in existing_columns:
                        conn.execute(text("ALTER TABLE \"user\" ADD COLUMN profile_pic_public_id VARCHAR(255)"))
                        conn.commit()
                        print("  ✅ Added profile_pic_public_id column")
                    
                    print("✅ Migration complete!")
                    
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    print("🔄 Starting database migration...")
    print("=" * 60)
    add_profile_pic_columns()
    print("=" * 60)
