#!/usr/bin/env python3
"""
Migration Script: Add cloudinary_url and cloudinary_public_id columns to CaseImage table
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

def add_cloudinary_columns_to_case_image():
    """Add Cloudinary columns to CaseImage table"""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('case_image')]
            
            if 'cloudinary_url' in columns and 'cloudinary_public_id' in columns:
                print("✅ Columns already exist. No migration needed.")
                return
            
            print("🔄 Adding cloudinary_url and cloudinary_public_id columns to case_image table...")
            
            # Get database URL to determine database type
            db_url = str(db.engine.url)
            
            if 'sqlite' in db_url.lower():
                # SQLite migration
                with db.engine.connect() as conn:
                    # Check if columns exist
                    result = conn.execute(text("PRAGMA table_info(case_image)"))
                    existing_columns = [row[1] for row in result]
                    
                    if 'cloudinary_url' not in existing_columns:
                        conn.execute(text("ALTER TABLE case_image ADD COLUMN cloudinary_url VARCHAR(500)"))
                        conn.commit()
                        print("  ✅ Added cloudinary_url column")
                    
                    if 'cloudinary_public_id' not in existing_columns:
                        conn.execute(text("ALTER TABLE case_image ADD COLUMN cloudinary_public_id VARCHAR(255)"))
                        conn.commit()
                        print("  ✅ Added cloudinary_public_id column")
                    
                    print("✅ Migration complete!")
            else:
                # PostgreSQL migration
                with db.engine.connect() as conn:
                    # Check if columns exist
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'case_image' 
                        AND column_name IN ('cloudinary_url', 'cloudinary_public_id')
                    """))
                    existing_columns = [row[0] for row in result]
                    
                    if 'cloudinary_url' not in existing_columns:
                        conn.execute(text("ALTER TABLE case_image ADD COLUMN cloudinary_url VARCHAR(500)"))
                        conn.commit()
                        print("  ✅ Added cloudinary_url column")
                    
                    if 'cloudinary_public_id' not in existing_columns:
                        conn.execute(text("ALTER TABLE case_image ADD COLUMN cloudinary_public_id VARCHAR(255)"))
                        conn.commit()
                        print("  ✅ Added cloudinary_public_id column")
                    
                    print("✅ Migration complete!")
                    
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    print("🔄 Starting database migration for CaseImage table...")
    print("=" * 60)
    add_cloudinary_columns_to_case_image()
    print("=" * 60)
