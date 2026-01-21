# ✅ Vercel Deployment Checklist - Neon Database

## Pre-Deployment

- [x] Code updated to use Neon database
- [x] Database connection string ready
- [ ] Environment variables configured in Vercel
- [ ] Database tables created (auto-created on first deploy)

## Environment Variables to Set in Vercel

### Required Variables

1. **DATABASE_URL**
   ```
   postgresql://neondb_owner:npg_mJFlLaRt47eM@ep-crimson-butterfly-ah7kdtkj-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
   - Go to: Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add `DATABASE_URL` with the value above
   - Apply to: Production, Preview, and Development

2. **SECRET_KEY**
   ```
   Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   - Generate a secure random key
   - Add as `SECRET_KEY` in Vercel
   - Apply to: Production, Preview, and Development

### Optional Variables

- `PYTHON_VERSION`: `3.9` (if not auto-detected)
- `VERCEL`: Automatically set by Vercel (don't set manually)

## Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update database configuration for Neon"
   git push origin main
   ```

2. **Verify Environment Variables**
   - Check Vercel dashboard
   - Ensure `DATABASE_URL` and `SECRET_KEY` are set
   - Verify they're applied to all environments

3. **Deploy**
   - Vercel will auto-deploy on push
   - Or trigger manual deployment from dashboard

4. **Verify Deployment**
   - Check deployment logs for database connection
   - Look for: `[DB] Using PostgreSQL: postgresql://...`
   - Test login/registration functionality

## Post-Deployment Verification

- [ ] App loads without errors
- [ ] Database connection successful (check logs)
- [ ] User registration works
- [ ] User login works
- [ ] Database tables created automatically
- [ ] Images can be uploaded
- [ ] Backup/restore functionality works

## Troubleshooting

### Database Connection Issues

**Error: "Connection refused"**
- Verify `DATABASE_URL` is correct
- Check Neon dashboard - is database active?
- Verify SSL mode is set (`sslmode=require`)

**Error: "Authentication failed"**
- Check username/password in connection string
- Verify credentials in Neon dashboard

**Error: "Database does not exist"**
- Verify database name in connection string
- Check Neon project settings

### Session Issues

**Users getting logged out**
- Verify `SECRET_KEY` is set
- Check cookie settings in browser
- Verify `SESSION_COOKIE_SECURE` is true in production

### Migration from Supabase

If migrating from Supabase:
1. Export data from Supabase (use backup feature)
2. Deploy app with new Neon database
3. Import data using restore feature in admin dashboard

## Neon Database Notes

- ✅ Uses standard PostgreSQL protocol
- ✅ Supports SSL connections (required)
- ✅ Serverless-friendly (auto-scaling)
- ✅ Connection pooling handled by Neon
- ✅ Compatible with SQLAlchemy

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check Neon dashboard for database status
3. Verify environment variables are set correctly
4. Test database connection locally with connection string
