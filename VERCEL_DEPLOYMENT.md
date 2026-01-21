# 🚀 Vercel Deployment Guide

## Database Setup with Neon

This app is configured to use **Neon** (serverless Postgres) on Vercel.

### Environment Variables

Set these in your Vercel project settings:

1. **DATABASE_URL** (Required)
   ```
   postgresql://neondb_owner:npg_mJFlLaRt47eM@ep-crimson-butterfly-ah7kdtkj-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

2. **SECRET_KEY** (Required)
   ```
   Generate a strong random key:
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **VERCEL** (Auto-set by Vercel)
   - Automatically set to `1` when running on Vercel

### Deployment Steps

1. **Connect Repository to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will auto-detect Python/Flask

2. **Set Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add `DATABASE_URL` with your Neon connection string
   - Add `SECRET_KEY` with a secure random key
   - Apply to Production, Preview, and Development

3. **Deploy**
   - Push to your main branch
   - Vercel will automatically deploy
   - Or trigger manual deployment from dashboard

### Database Connection

The app automatically:
- ✅ Detects Vercel environment
- ✅ Uses NullPool for serverless (no connection pooling)
- ✅ Handles connection timeouts properly
- ✅ Cleans up connections after each request
- ✅ Supports SSL connections (required for Neon)

### Neon Database Setup

1. **Create Neon Project**
   - Go to [neon.tech](https://neon.tech)
   - Create a new project
   - Copy the connection string

2. **Connection String Format**
   ```
   postgresql://user:password@host/database?sslmode=require
   ```

3. **Important Notes**
   - Use the **pooler** endpoint for serverless (Vercel)
   - Always include `sslmode=require` for security
   - The app handles connection pooling automatically

### Troubleshooting

**Connection Errors:**
- Verify `DATABASE_URL` is set correctly in Vercel
- Check that SSL mode is enabled (`sslmode=require`)
- Ensure the database is accessible from Vercel's IP ranges

**Session Issues:**
- Make sure `SECRET_KEY` is set
- Check that cookies are enabled in browser
- Verify `SESSION_COOKIE_SECURE` is true in production

**Database Schema:**
- Tables are created automatically on first deployment
- Run migrations if needed: `flask db upgrade`

### Local Development

For local development, the app uses SQLite by default. To use Neon locally:

```bash
export DATABASE_URL="postgresql://..."
python app.py
```

Or create a `.env` file:
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
```
