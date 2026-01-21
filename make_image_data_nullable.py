#!/usr/bin/env python3
"""
Migration Script: Make image_data column nullable in case_image table
This allows images to be stored only in Cloudinary without requiring binary data
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

def make_image_data_nullable():
    """Make image_data column nullable in case_image table"""
    with app.app_context():
        try:
            print("🔄 Making image_data column nullable in case_image table...")
            
            # Get database URL to determine database type
            db_url = str(db.engine.url)
            
            if 'sqlite' in db_url.lower():
                # SQLite doesn't support ALTER COLUMN directly
                # We need to recreate the table
                print("  ⚠️  SQLite detected - recreating table to make column nullable...")
                
                with db.engine.connect() as conn:
                    # Check current schema
                    result = conn.execute(text("PRAGMA table_info(case_image)"))
                    columns = {row[1]: row for row in result}
                    
                    if 'image_data' in columns:
                        col_info = columns['image_data']
                        # Check if it's already nullable (notnull = 0 means nullable)
                        if col_info[3] == 0:
                            print("  ✅ image_data is already nullable")
                            return
                    
                    # SQLite workaround: Create new table with nullable image_data
                    print("  📝 Creating new table structure...")
                    
                    # Create new table (note: 'case' is a reserved word in SQLite, so we quote it)
                    conn.execute(text("""
                        CREATE TABLE case_image_new (
                            id INTEGER PRIMARY KEY,
                            case_id INTEGER NOT NULL,
                            image_data BLOB,
                            cloudinary_url VARCHAR(500),
                            cloudinary_public_id VARCHAR(255),
                            image_filename VARCHAR(255) NOT NULL,
                            image_type VARCHAR(50) NOT NULL,
                            image_description TEXT,
                            created_at DATETIME,
                            FOREIGN KEY (case_id) REFERENCES "case"(id)
                        )
                    """))
                    
                    # Copy data
                    conn.execute(text("""
                        INSERT INTO case_image_new 
                        (id, case_id, image_data, cloudinary_url, cloudinary_public_id, 
                         image_filename, image_type, image_description, created_at)
                        SELECT 
                            id, case_id, image_data, cloudinary_url, cloudinary_public_id,
                            image_filename, image_type, image_description, created_at
                        FROM case_image
                    """))
                    
                    # Drop old table
                    conn.execute(text("DROP TABLE case_image"))
                    
                    # Rename new table
                    conn.execute(text("ALTER TABLE case_image_new RENAME TO case_image"))
                    
                    conn.commit()
                    print("  ✅ Table recreated with nullable image_data")
            else:
                # PostgreSQL - can use ALTER COLUMN
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE case_image ALTER COLUMN image_data DROP NOT NULL"))
                    conn.commit()
                    print("  ✅ Made image_data nullable")
                    
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    print("🔄 Starting migration to make image_data nullable...")
    print("=" * 60)
    make_image_data_nullable()
    print("=" * 60)
    print("✅ Migration complete!")
