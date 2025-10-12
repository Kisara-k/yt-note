# Vercel Deployment Guide - Frontend Only

## ⚠️ Important: Backend Limitations on Vercel

### FastAPI Backend Cannot Be Fully Deployed on Vercel Free Tier

**Critical Limitations:**

1. **Execution Timeout**:

   - Free tier: **10 seconds max execution time** for serverless functions
   - Your backend needs: Long-running AI processing (OpenAI API calls, subtitle extraction)
   - Your video processing jobs can take **minutes**, not seconds

2. **Bundle Size**:

   - Maximum uncompressed bundle size: **250 MB**
   - Your requirements include heavy dependencies:
     - `yt-dlp` (video downloader)
     - `google-api-python-client` (YouTube API)
     - `openai` (AI processing)
     - `psycopg2-binary` (PostgreSQL)
     - These dependencies likely exceed or come very close to the limit

3. **Stateful Operations**:

   - Your backend uses:
     - Background job queue (`orchestrator.py`)
     - Long-running video processing
     - Direct database connections with `psycopg2`
   - Vercel Functions are **stateless** and designed for quick API responses

4. **WebSocket Support**:
   - Your FastAPI app may use WebSockets or SSE for job status updates
   - Vercel has limited WebSocket support (30 seconds max on free tier)

### Recommended Architecture

**✅ Deploy on Vercel (Free):**

- Next.js Frontend only
- Static site generation
- Client-side routing

**🚀 Deploy Backend Elsewhere:**

- **Railway.app** (Free tier: 500 hours/month, $5 credit)
- **Render.com** (Free tier with auto-sleep after 15 min inactivity)
- **Fly.io** (Free tier with shared CPU)
- **Azure App Service** (Free F1 tier)
- **Google Cloud Run** (Free tier with generous limits)

---

## 📋 Step-by-Step: Deploy Frontend to Vercel

### Prerequisites

✅ GitHub account  
✅ Vercel account (sign up at [vercel.com](https://vercel.com))  
✅ Your backend deployed elsewhere and accessible via HTTPS  
✅ Environment variables ready

---

### Step 1: Prepare Your Repository

1. **Ensure your code is committed to GitHub:**

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin azure-deploy
```

2. **Verify your frontend build works locally:**

```bash
cd frontend
pnpm install
pnpm build
```

---

### Step 2: Configure Environment Variables

Create a file: `frontend/.env.production` (DO NOT commit this file!)

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend API URL (your deployed backend)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
# Or: https://your-backend.onrender.com
# Or: https://your-backend.fly.dev

# Optional: Analytics, monitoring, etc.
```

**Important**: Add `.env.production` to your `.gitignore`!

---

### Step 3: Create Vercel Configuration

Create file: `vercel.json` in the **root** of your repository:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "cd frontend && pnpm install && pnpm build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.com/:path*"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ]
}
```

**Replace `your-backend-url.com` with your actual backend URL.**

---

### Step 4: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended for first-time)

1. **Go to [vercel.com/new](https://vercel.com/new)**

2. **Import your GitHub repository:**

   - Click "Import Project"
   - Select your repository: `Kisara-k/yt-note`
   - Choose the branch: `azure-deploy`

3. **Configure Project:**

   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `pnpm build`
   - **Output Directory**: `.next`
   - **Install Command**: `pnpm install`

4. **Add Environment Variables:**

   - Click "Environment Variables"
   - Add each variable from your `.env.production`:
     - `NEXT_PUBLIC_SUPABASE_URL`
     - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
     - `NEXT_PUBLIC_API_URL`

5. **Deploy:**
   - Click "Deploy"
   - Wait 2-3 minutes for the build to complete
   - You'll get a URL like: `https://yt-note-xyz.vercel.app`

#### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI:**

```bash
npm i -g vercel
```

2. **Login to Vercel:**

```bash
vercel login
```

3. **Deploy from root directory:**

```bash
# From the root of your repo
vercel --cwd frontend
```

4. **Follow the prompts:**

   - Link to existing project? **No**
   - What's your project's name? **yt-note**
   - In which directory is your code located? **frontend**
   - Want to modify settings? **Yes**
   - Set environment variables

5. **Deploy to production:**

```bash
vercel --prod --cwd frontend
```

---

### Step 5: Configure Custom Domain (Optional)

1. **Go to your Vercel project dashboard**
2. **Settings → Domains**
3. **Add your domain:**
   - Enter your domain: `yournotes.com`
   - Follow DNS configuration instructions
   - Vercel provides free SSL certificates

---

### Step 6: Set Up Automatic Deployments

Vercel automatically deploys when you push to GitHub:

- **Production**: Pushes to `main` or `azure-deploy` branch
- **Preview**: Pull requests and other branches

**Configure in Vercel Dashboard:**

1. Settings → Git
2. Production Branch: `azure-deploy`
3. Enable automatic deployments

---

### Step 7: Verify Deployment

1. **Visit your Vercel URL**: `https://yt-note-xyz.vercel.app`

2. **Test authentication:**

   - Can you log in with Supabase?
   - Check browser console for errors

3. **Test API connectivity:**

   - Try fetching a YouTube video
   - Check Network tab to verify API calls reach your backend

4. **Check logs in Vercel Dashboard:**
   - Functions tab shows serverless function logs (if any)
   - Real-time logs for debugging

---

## 🐛 Troubleshooting

### Build Fails

**Error**: `pnpm: command not found`

**Solution**: Configure package manager in `package.json`:

```json
{
  "packageManager": "pnpm@9.0.0"
}
```

---

**Error**: `Module not found: Can't resolve '@/...'`

**Solution**: Check `tsconfig.json` paths are correct:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

---

### Environment Variables Not Working

**Check:**

1. All variables start with `NEXT_PUBLIC_` for client-side access
2. Variables are set in Vercel Dashboard
3. Redeploy after adding new variables

---

### API Calls Fail (CORS)

**Backend must allow your Vercel domain:**

Update your FastAPI backend's CORS middleware:

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yt-note-xyz.vercel.app",  # Add your Vercel URL
        "https://yournotes.com",  # Add custom domain if you have one
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Supabase Connection Issues

**Check:**

1. Supabase URL and key are correct
2. Supabase project is not paused (free tier pauses after inactivity)
3. RLS policies allow authenticated access

---

## 📊 Free Tier Limits (Vercel Hobby)

| Resource                           | Limit              |
| ---------------------------------- | ------------------ |
| **Bandwidth**                      | 100 GB/month       |
| **Serverless Function Executions** | 100 GB-Hours/month |
| **Serverless Function Duration**   | 10 seconds max     |
| **Builds**                         | Unlimited          |
| **Team Members**                   | 1 (just you)       |
| **Custom Domains**                 | Unlimited          |
| **SSL Certificates**               | Free, automatic    |

**Your frontend should easily fit within these limits!**

---

## 🚀 Next Steps

1. ✅ Deploy frontend to Vercel (this guide)
2. 🔄 Deploy backend to Railway/Render/Fly.io
3. 🔗 Update `NEXT_PUBLIC_API_URL` in Vercel env vars
4. 🎯 Set up custom domain (optional)
5. 📊 Monitor usage in Vercel dashboard
6. 🔄 Set up CI/CD with GitHub Actions (optional)

---

## 📚 Additional Resources

- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment Docs](https://nextjs.org/docs/deployment)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Environment Variables Guide](https://vercel.com/docs/concepts/projects/environment-variables)

---

## 💡 Pro Tips

1. **Use Preview Deployments**: Every PR gets its own preview URL for testing
2. **Monitor Analytics**: Vercel provides free Web Analytics
3. **Enable Speed Insights**: See real-world performance metrics
4. **Use Edge Functions**: For fast, globally distributed API routes (if needed)
5. **Set up Monitoring**: Use Vercel's built-in monitoring or integrate with external tools

---

## ⚠️ Important Notes

- **Never commit `.env.production` to Git**
- **Always use HTTPS for your backend API**
- **Keep your Supabase keys secure**
- **Monitor your usage to avoid overages**
- **Test thoroughly before switching DNS for custom domains**

---

**Need help?** Check the [Vercel Discord](https://vercel.com/discord) or [GitHub Discussions](https://github.com/vercel/vercel/discussions)
