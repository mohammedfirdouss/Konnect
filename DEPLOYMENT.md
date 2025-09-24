# Konnect Deployment Guide

This guide covers the complete setup and deployment process for Konnect using Supabase and Render.

## 🏗️ Architecture Overview

- **Frontend**: React/Next.js (deployed separately)
- **Backend**: FastAPI Python application
- **Database**: Supabase PostgreSQL with RLS
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage (for images)
- **Deployment**: Render Web Service
- **Caching**: Redis (optional, for recommendations)

## 📋 Prerequisites

1. **Supabase Account**: [Create account](https://supabase.com)
2. **Render Account**: [Create account](https://render.com)
3. **GitHub Repository**: Code must be in a GitHub repository
4. **Domain** (optional): For custom domain setup

## 🚀 Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Choose organization and enter project details:
   - **Name**: `konnect-production` (or your preferred name)
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
4. Wait for project creation (2-3 minutes)

### 1.2 Configure Database Schema

1. Go to **SQL Editor** in your Supabase dashboard
2. Run the migration files in order:
   - `supabase/migrations/20250101120000_create_profiles_table.sql`
   - `supabase/migrations/20250101130000_create_marketplace_tables.sql`
   - `supabase/migrations/20250101140000_create_orders_and_purchases.sql`
   - `supabase/migrations/20250101150000_create_user_activities.sql`
   - `supabase/migrations/20250101160000_create_marketplace_requests.sql`
   - `supabase/migrations/20250101170000_create_messages_table.sql`
   - `supabase/migrations/20250101180000_create_listing_images_table.sql`

3. Run the seed data:
   ```sql
   -- Copy and paste content from supabase/seed.sql
   ```

### 1.3 Configure Authentication

1. Go to **Authentication > Settings**
2. Configure the following:
   - **Site URL**: `https://your-app-name.onrender.com` (update after Render deployment)
   - **Redirect URLs**: Add your frontend URL
   - **Email Confirmation**: Disable for development, enable for production
   - **Email Templates**: Customize as needed

### 1.4 Configure Storage (for image uploads)

1. Go to **Storage**
2. Create a new bucket:
   - **Name**: `listing_images`
   - **Public**: `true`
   - **File size limit**: `10MB`
   - **Allowed MIME types**: `image/jpeg, image/png, image/gif, image/webp`

### 1.5 Get API Keys

1. Go to **Settings > API**
2. Copy the following values:
   - **Project URL**: `https://your-project-ref.supabase.co`
   - **Anon (public) key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Service role (secret) key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

⚠️ **Keep the service role key secure** - it bypasses RLS policies!

## 🚀 Step 2: Render Setup

### 2.1 Create Database Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** > **PostgreSQL**
3. Configure:
   - **Name**: `konnect-db`
   - **Database**: `konnect`
   - **User**: `konnect`
   - **Region**: Choose same as your web service
   - **Plan**: `Starter` ($7/month) or higher
4. Click **Create Database**
5. Wait for provisioning (2-3 minutes)
6. **Save the connection string** from the database info page

### 2.2 Create Redis Service (Optional)

1. Click **New** > **Redis**
2. Configure:
   - **Name**: `konnect-redis`
   - **Region**: Same as database
   - **Plan**: `Starter` ($7/month)
   - **Maxmemory Policy**: `allkeys-lru`
3. Click **Create Redis**

### 2.3 Create Web Service

1. Click **New** > **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `konnect-api` (or your preferred name)
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn konnect.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Starter` ($7/month) or higher

### 2.4 Configure Environment Variables

In the Render dashboard, go to your web service and add these environment variables:

#### Required Variables:
```bash
# Application
SECRET_KEY=<generate-random-32-char-string>
PYTHONPATH=/opt/render/project/src
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (auto-configured by Render)
DATABASE_URL=<from-your-postgresql-service>

# Supabase (from Step 1.5)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>

# Redis (auto-configured by Render, optional)
REDIS_URL=<from-your-redis-service>
CELERY_BROKER_URL=<same-as-redis-url>
CELERY_RESULT_BACKEND=<same-as-redis-url>
REDIS_EXPIRE_TIME=3600
```

#### Optional Variables:
```bash
# Google ADK (for AI features)
GOOGLE_API_KEY=<your-google-api-key>
GOOGLE_APPLICATION_CREDENTIALS=<path-to-service-account-json>
```

### 2.5 Configure Health Check

1. In your web service settings:
   - **Health Check Path**: `/health`
   - **Health Check Grace Period**: `300` seconds

### 2.6 Deploy

1. Click **Create Web Service**
2. Monitor the build logs
3. Wait for deployment to complete (5-10 minutes)

## 🧪 Step 3: Verification & Testing

### 3.1 Test Supabase Configuration

Run the Supabase test script:

```bash
python scripts/test_supabase_connection.py
```

Expected output:
```
🚀 Supabase Connection and Configuration Test
============================================================
🔧 Testing Environment Variables...
  ✅ SUPABASE_URL: ********************...co
  ✅ SUPABASE_ANON_KEY: ********************...xyz
  ✅ SUPABASE_SERVICE_ROLE_KEY: ********************...abc
✅ All environment variables are set

🔧 Testing Supabase Client Initialization...
  ✅ Public Supabase client initialized
  ✅ Admin Supabase client initialized

🔧 Testing Supabase Connection...
  ✅ supabase_configured: True
  ✅ admin_configured: True
  ✅ url_configured: True
  ✅ anon_key_configured: True
  ✅ service_key_configured: True
  ✅ connection_test: success

🎉 All tests passed! Supabase is properly configured.
```

### 3.2 Test Render Deployment

Run the Render test script:

```bash
python scripts/test_render_deployment.py
```

### 3.3 Test API Endpoints

Once deployed, test these endpoints:

#### Health Check:
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "konnect",
  "version": "0.1.0",
  "environment": "production",
  "supabase": {
    "supabase_configured": true,
    "connection_test": "success"
  },
  "database": {
    "type": "supabase_postgresql",
    "connected": true
  }
}
```

#### User Registration:
```bash
curl -X POST "https://your-app-name.onrender.com/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

#### User Login:
```bash
curl -X POST "https://your-app-name.onrender.com/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword123"
```

#### Get Marketplaces:
```bash
curl "https://your-app-name.onrender.com/marketplaces/"
```

## 🔧 Step 4: Configuration Details

### 4.1 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SUPABASE_URL` | ✅ | Your Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_ANON_KEY` | ✅ | Supabase anonymous key | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase service role key | `eyJhbGciOiJIUzI1NiIs...` |
| `DATABASE_URL` | ✅ | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | ✅ | Application secret key | `your-secret-key-here` |
| `ENVIRONMENT` | ✅ | Environment setting | `production` |
| `PYTHONPATH` | ✅ | Python path for imports | `/opt/render/project/src` |
| `REDIS_URL` | ⚪ | Redis connection string | `redis://host:6379/0` |
| `LOG_LEVEL` | ⚪ | Logging level | `INFO` |
| `GOOGLE_API_KEY` | ⚪ | Google AI API key | `AIzaSyC...` |

### 4.2 Database Schema Summary

The application uses the following main tables:

- **`profiles`**: User profiles linked to Supabase auth
- **`marketplaces`**: University marketplaces
- **`listings`**: Product/service listings
- **`orders`**: Purchase orders with escrow
- **`purchases`**: Completed purchases
- **`user_activities`**: User behavior tracking
- **`marketplace_requests`**: Requests for new marketplaces
- **`messages`**: Direct messaging between users
- **`listing_images`**: Image metadata for listings

### 4.3 Security Configuration

- **Row Level Security (RLS)**: Enabled on all tables
- **Authentication**: Handled by Supabase Auth
- **Authorization**: Role-based access control
- **API Security**: JWT token validation
- **CORS**: Configured for cross-origin requests

## 🚨 Troubleshooting

### Common Issues:

#### 1. Build Failures on Render
```bash
# Check Python version
python --version

# Verify requirements.txt
pip install -r requirements.txt

# Check for missing dependencies
pip check
```

#### 2. Database Connection Issues
```bash
# Test connection locally
python scripts/test_render_deployment.py

# Check environment variables
echo $DATABASE_URL
```

#### 3. Supabase Authentication Issues
```bash
# Test Supabase connection
python scripts/test_supabase_connection.py

# Verify API keys in Supabase dashboard
```

#### 4. Import Errors
```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Verify module structure
python -c "import konnect; print('OK')"
```

### Debugging Steps:

1. **Check Render Logs**:
   - Go to your web service in Render dashboard
   - Click on "Logs" tab
   - Look for startup errors

2. **Test Health Endpoint**:
   ```bash
   curl https://your-app-name.onrender.com/health
   ```

3. **Verify Environment Variables**:
   - Check all required variables are set
   - Ensure no typos in variable names
   - Verify Supabase keys are correct

4. **Database Connectivity**:
   - Test database connection from Render service
   - Check if migrations ran successfully
   - Verify RLS policies are working

## 📊 Monitoring & Maintenance

### Health Monitoring:
- **Health Endpoint**: `/health` - Application status
- **Metrics Endpoint**: `/metrics` - Prometheus metrics
- **Logs**: Structured JSON logging

### Performance Monitoring:
- Monitor response times via Render dashboard
- Set up alerts for service downtime
- Monitor database performance in Supabase

### Security Monitoring:
- Review Supabase auth logs
- Monitor failed authentication attempts
- Check for unusual API usage patterns

## 🔄 Updates & Maintenance

### Deploying Updates:
1. Push changes to GitHub
2. Render automatically rebuilds and deploys
3. Monitor deployment logs
4. Test critical endpoints after deployment

### Database Migrations:
1. Create new migration files in `supabase/migrations/`
2. Test migrations in Supabase SQL editor
3. Apply to production database
4. Update application code as needed

### Backup Strategy:
- Supabase automatically backs up your database
- Export critical data regularly
- Test restore procedures

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ User registration and login work
- ✅ CRUD operations on listings work
- ✅ Database queries execute successfully
- ✅ Authentication tokens are validated
- ✅ RLS policies enforce proper access control
- ✅ Application logs show no critical errors
- ✅ Response times are acceptable (< 2 seconds)

## 📞 Support

If you encounter issues:

1. **Check the logs** in both Render and Supabase dashboards
2. **Run the test scripts** to identify specific problems
3. **Review the troubleshooting section** above
4. **Check Supabase status**: [status.supabase.com](https://status.supabase.com)
5. **Check Render status**: [status.render.com](https://status.render.com)

---

**Next Steps**: After successful deployment, consider setting up monitoring, custom domains, and CI/CD pipelines for automated deployments.