# 📸 Migrate Images to Cloudinary

This guide explains how to migrate existing binary images stored in the database to Cloudinary.

## Why Migrate?

- **Smaller backups**: Cloudinary URLs instead of base64-encoded images
- **Better performance**: Images served from CDN
- **Reduced database size**: No binary data storage
- **Organized storage**: All images in `frcr-examiner-media` folder

## Migration Methods

### Method 1: Admin Dashboard (Recommended)

1. **Log in as admin** (first registered user)
2. **Go to Admin Dashboard**
3. **Click "Migrate Images to Cloudinary"** (if button exists)
   - Or use the API endpoint directly
4. **Wait for migration to complete**
5. **Verify images still work**

### Method 2: API Endpoint

1. **Log in as admin**
2. **Call the migration endpoint:**
   ```bash
   curl -X POST https://your-app.vercel.app/api/admin/migrate-images \
     -H "Cookie: your-session-cookie"
   ```
3. **Or use browser console:**
   ```javascript
   fetch('/api/admin/migrate-images', { method: 'POST' })
     .then(r => r.json())
     .then(data => console.log(data));
   ```

### Method 3: Command Line Script

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run migration script:**
   ```bash
   python3 migrate_images_to_cloudinary.py
   ```

3. **Optional: Clear binary data after migration:**
   ```bash
   python3 migrate_images_to_cloudinary.py --clear-binary
   ```
   ⚠️ **Warning**: This permanently deletes binary data. Only run after verifying images work!

## What Gets Migrated?

- ✅ All `CaseImage` records with `image_data` (binary) but no `cloudinary_url`
- ✅ Images are uploaded to `frcr-examiner-media/case-images/`
- ✅ Database records updated with Cloudinary URLs
- ✅ Original filenames preserved

## After Migration

1. **Verify images work:**
   - Check a few cases with images
   - Ensure images load correctly
   - Test image viewer functionality

2. **Optional: Clear binary data:**
   - After verifying everything works
   - Run script with `--clear-binary` flag
   - This frees up database space

3. **Create new backup:**
   - New backups will be much smaller
   - Only contain Cloudinary URLs, not binary data

## Troubleshooting

**Migration fails for some images:**
- Check Cloudinary dashboard for upload errors
- Verify Cloudinary credentials are correct
- Check image file sizes (max 10MB per image)

**Images not showing after migration:**
- Check browser console for errors
- Verify Cloudinary URLs are accessible
- Check that frontend uses `image.url` field

**Migration is slow:**
- Normal for large images
- Migration processes one image at a time
- Large batches may take several minutes

## Folder Structure

After migration, images are organized in Cloudinary:

```
frcr-examiner-media/
├── case-images/          (all case images)
└── profile-pics/         (profile pictures)
```

## Safety

- ✅ Binary data is kept by default (can restore if needed)
- ✅ Migration is idempotent (safe to run multiple times)
- ✅ Only migrates images without Cloudinary URLs
- ✅ Original images remain in database until explicitly cleared
