# Azure Deployment Guide - YouTube Notes Backend

## 🚀 Quick Deploy (VS Code Extension)

### Prerequisites

1. **Azure Account** - Free tier works
2. **VS Code** with Azure App Service extension installed
3. **Signed into Azure** in VS Code (View → Command Palette → "Azure: Sign In")

### Deploy Steps

1. **Open Azure Extension** (Azure icon in left sidebar)

2. **Create Web App**:

   - Right-click on your subscription
   - Select **"Create New Web App... (Advanced)"**
   - Configure:
     - **Name**: `yt-notes-backend` (or your choice - must be globally unique)
     - **Resource Group**: Create new: `yt-notes-rg`
     - **Runtime Stack**: `Python 3.11`
     - **OS**: `Linux`
     - **Region**: Choose closest to you (e.g., `East US`, `West Europe`)
     - **App Service Plan**: Create new
     - **Pricing Tier**: `F1 (Free)`
     - **Application Insights**: Skip for now

3. **Deploy Code**:

   - In Azure extension, find your new Web App
   - Right-click → **"Deploy to Web App..."**
   - Select the `backend` folder when prompted
   - Confirm deployment

4. **Configure Environment Variables** (CRITICAL):

   - In Azure extension, expand your Web App
   - Right-click **"Application Settings"** → **"Add New Setting"**
   - Add each variable (see section below)

5. **Restart Web App**:
   - Right-click Web App → **"Restart"**

---

## 🔧 Environment Variables Configuration

### Required Settings

Add these in **Application Settings** (Azure Portal or VS Code):

```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
DB_PASSWORD=your_supabase_db_password

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
```

### How to Add Settings in VS Code:

1. Azure extension → Your Web App
2. Right-click **"Application Settings"**
3. Select **"Add New Setting..."**
4. Enter key name (e.g., `YOUTUBE_API_KEY`)
5. Enter value
6. Repeat for each variable

---

## 🌐 CORS Configuration

### Current Setting (Local Dev)

The backend currently allows:

```python
allow_origins=["http://localhost:3000", "http://localhost:3001"]
```

### To Add Production Frontend (e.g., Vercel):

**Option 1: Edit `api.py` before deployment**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-app.vercel.app"  # Add your deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Option 2: Use environment variable (better)**
Edit `api.py`:

```python
import os
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # ... rest of config
)
```

Then add to Azure Application Settings:

```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://your-app.vercel.app
```

---

## 📝 Getting API Keys

### 1. YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a project (if new)
3. Enable **YouTube Data API v3**
4. Create credentials → API Key
5. Restrict the key (optional but recommended):
   - API restrictions → YouTube Data API v3
   - Application restrictions → HTTP referrers (for web apps)

### 2. Supabase Credentials

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings → API**:
   - `SUPABASE_URL`: Project URL
   - `SUPABASE_KEY`: `anon` `public` key
4. Go to **Settings → API → JWT Settings**:
   - `SUPABASE_JWT_SECRET`: JWT Secret
5. Go to **Settings → Database**:
   - `DB_PASSWORD`: Your database password

### 3. OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy immediately (won't be shown again)

---

## 🧪 Testing Your Deployment

### 1. Check if API is Running

```bash
curl https://your-app-name.azurewebsites.net/
```

Expected response:

```json
{ "message": "YouTube Notes API", "version": "2.0.0" }
```

### 2. View Logs (VS Code)

- Azure extension → Your Web App
- Right-click → **"Start Streaming Logs"**

### 3. Test API Endpoints

```bash
# Check video metadata
curl https://your-app-name.azurewebsites.net/api/videos/VIDEO_ID

# Health check
curl https://your-app-name.azurewebsites.net/docs
```

---

## 🔍 Troubleshooting

### Deployment Fails

- Check **Deployment Center** in Azure Portal for error logs
- Ensure `requirements.txt` is correct
- Verify Python version matches (3.11)

### App Won't Start

- Check **Log Stream** in Azure Portal or VS Code
- Verify all environment variables are set
- Check `startup.txt` command is correct

### Database Connection Issues

- Verify Supabase credentials are correct
- Check if Supabase project is active
- Ensure `DB_PASSWORD` is set

### API Endpoints Return Errors

- Check if API keys are valid
- View application logs for specific errors
- Verify CORS settings if frontend can't connect

### 502 Bad Gateway

- App might be starting up (wait 30 seconds)
- Check if gunicorn/uvicorn is running (view logs)
- Restart the Web App

---

## 💰 Free Tier Limitations

**Azure App Service F1 (Free)**:

- ✅ 1 GB RAM
- ✅ 1 GB storage
- ⚠️ **60 minutes compute time per day**
- ⚠️ Custom domain requires paid tier
- ✅ SSL/HTTPS included with `.azurewebsites.net` domain

**When you hit the limit**: App will stop until next day (UTC reset)

**To monitor usage**: Azure Portal → Your Web App → Metrics

---

## 🔄 Updating Your Deployment

### Method 1: VS Code (Easiest)

1. Make code changes
2. Right-click Web App → **"Deploy to Web App..."**
3. Confirm overwrite

### Method 2: Git Deployment (Advanced)

- Enable Deployment Center in Azure Portal
- Connect to GitHub repository
- Auto-deploy on push to main branch

---

## 🛡️ Security Best Practices

1. **Never commit `.env` files** (already in `.gitignore`)
2. **Rotate API keys** periodically
3. **Use HTTPS only** for production frontend
4. **Restrict CORS** to your actual frontend domain
5. **Monitor logs** for unauthorized access attempts
6. **Keep dependencies updated** (`pip list --outdated`)

---

## 📊 Your Deployed App URL

After deployment, your API will be available at:

```
https://YOUR-APP-NAME.azurewebsites.net
```

**API Documentation (Swagger UI)**:

```
https://YOUR-APP-NAME.azurewebsites.net/docs
```

**Update Frontend** to use this URL instead of `http://localhost:8000`

---

## 🎯 Next Steps

1. ✅ Deploy backend to Azure
2. ✅ Configure environment variables
3. ✅ Test API endpoints
4. 🔄 Update frontend `API_URL` to Azure backend
5. 🚀 Deploy frontend to Vercel/Netlify
6. 🔧 Update CORS with production frontend URL

---

## 📞 Need Help?

- **Azure Portal**: [portal.azure.com](https://portal.azure.com)
- **View Logs**: Azure Portal → Your Web App → Log Stream
- **Restart App**: Azure Portal → Your Web App → Restart button
- **Check Metrics**: Azure Portal → Your Web App → Metrics
