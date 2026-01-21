#!/usr/bin/env python3
"""
Migration Script: Migrate existing binary images to Cloudinary
This script uploads all images stored as binary data in the database to Cloudinary
and updates the database records with Cloudinary URLs.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app, db
from models import CaseImage
import cloudinary
import cloudinary.uploader
from io import BytesIO

def migrate_images_to_cloudinary():
    """Migrate all binary images to Cloudinary"""
    with app.app_context():
        # Find all images with binary data but no Cloudinary URL
        images_to_migrate = CaseImage.query.filter(
            CaseImage.image_data.isnot(None),
            (CaseImage.cloudinary_url.is_(None) | (CaseImage.cloudinary_url == ''))
        ).all()
        
        total_images = len(images_to_migrate)
        print(f"Found {total_images} images to migrate to Cloudinary")
        print("=" * 60)
        
        if total_images == 0:
            print("✅ No images to migrate. All images are already in Cloudinary!")
            return
        
        successful = 0
        failed = 0
        
        for idx, image in enumerate(images_to_migrate, 1):
            try:
                print(f"\n[{idx}/{total_images}] Migrating image ID {image.id}: {image.image_filename}")
                
                # Check if image_data exists and is not empty
                if not image.image_data or len(image.image_data) == 0:
                    print(f"  ⚠️  Skipping: Image has no binary data")
                    failed += 1
                    continue
                
                # Create a BytesIO object from binary data for Cloudinary upload
                image_file = BytesIO(image.image_data)
                image_file.seek(0)
                
                # Upload to Cloudinary in frcr-examiner-media/case-images folder
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="frcr-examiner-media/case-images",
                    resource_type="image",
                    overwrite=False,
                    use_filename=True,
                    unique_filename=True,
                    filename_override=image.image_filename  # Use original filename
                )
                
                cloudinary_url = upload_result.get('secure_url')
                cloudinary_public_id = upload_result.get('public_id')
                
                print(f"  ✅ Uploaded to Cloudinary: {cloudinary_public_id}")
                print(f"  📎 URL: {cloudinary_url}")
                
                # Update database record
                image.cloudinary_url = cloudinary_url
                image.cloudinary_public_id = cloudinary_public_id
                # Optionally clear binary data after successful upload (saves space)
                # image.image_data = None
                
                db.session.commit()
                print(f"  ✅ Database updated")
                successful += 1
                
            except Exception as e:
                print(f"  ❌ Error migrating image {image.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
                failed += 1
                continue
        
        print("\n" + "=" * 60)
        print(f"Migration Complete!")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📊 Total: {total_images}")
        print("=" * 60)
        
        if successful > 0:
            print("\n💡 Tip: After verifying images work correctly, you can:")
            print("   1. Run this script again with --clear-binary flag to remove binary data")
            print("   2. This will free up database space")

if __name__ == '__main__':
    # Check for --clear-binary flag
    clear_binary = '--clear-binary' in sys.argv
    
    if clear_binary:
        print("⚠️  WARNING: This will delete binary data after Cloudinary upload!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
    
    print("🔄 Starting image migration to Cloudinary...")
    print("=" * 60)
    
    migrate_images_to_cloudinary()
    
    if clear_binary:
        print("\n🧹 Clearing binary data from migrated images...")
        with app.app_context():
            migrated_images = CaseImage.query.filter(
                CaseImage.cloudinary_url.isnot(None),
                CaseImage.image_data.isnot(None)
            ).all()
            
            for image in migrated_images:
                image.image_data = None
                db.session.commit()
            
            print(f"✅ Cleared binary data from {len(migrated_images)} images")
