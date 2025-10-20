# Production Migration Checklist

Use this checklist to ensure a smooth migration from local development to production deployment.

## Pre-Deployment Checklist

### Backend Preparation

- [ ] All environment variables documented in `.env.example`
- [ ] Service role keys ready (not anon keys)
- [ ] JWT secret obtained from Supabase
- [ ] OpenAI API key ready
- [ ] YouTube API key ready
- [ ] CORS origins list prepared (will update after frontend deploys)
- [ ] `requirements.txt` is up to date
- [ ] All hardcoded `localhost` references removed
- [ ] Railway configuration files created (`railway.toml`, `nixpacks.toml`, `Procfile`)

### Frontend Preparation

- [ ] All environment variables documented in `.env.local.example`
- [ ] All hardcoded `localhost:8000` replaced with `API_BASE_URL`
- [ ] `NEXT_PUBLIC_BACKEND_URL` configuration tested locally
- [ ] Supabase anon key ready (for auth only)
- [ ] `vercel.json` configuration created
- [ ] All imports use `@/lib/config` for API_BASE_URL
- [ ] No service role keys in frontend code

### Database Preparation

- [ ] RLS enabled on all tables
- [ ] Database migrations applied
- [ ] Verified emails list configured in backend
- [ ] Test data cleaned up (optional)
- [ ] Supabase storage buckets configured
- [ ] Database backups configured

### Security Checklist

- [ ] `.env` files in `.gitignore`
- [ ] No service role keys in frontend
- [ ] No JWT secrets in frontend
- [ ] RLS enabled on all Supabase tables
- [ ] Verified email list configured
- [ ] CORS properly configured
- [ ] API routes protected with authentication

---

## Deployment Steps

### Phase 1: Backend (Railway)

#### 1.1 Create Project

- [ ] Railway project created
- [ ] GitHub repository connected
- [ ] Build settings verified

#### 1.2 Configure Environment

- [ ] `YOUTUBE_API_KEY` set
- [ ] `SUPABASE_URL` set
- [ ] `SUPABASE_KEY` (service role) set
- [ ] `SUPABASE_SERVICE_KEY` set
- [ ] `SUPABASE_JWT_SECRET` set
- [ ] `SUPABASE_URL_2` set
- [ ] `SUPABASE_KEY_2` set
- [ ] `SUPABASE_SERVICE_KEY_2` set
- [ ] `OPENAI_API_KEY` set
- [ ] `API_HOST=0.0.0.0` set
- [ ] `API_PORT=$PORT` set
- [ ] `API_RELOAD=false` set
- [ ] `CORS_ORIGINS` set (temporary, update after frontend)

#### 1.3 Deploy & Test

- [ ] Backend deployed successfully
- [ ] Health endpoint accessible: `https://your-backend.railway.app/`
- [ ] API docs accessible: `https://your-backend.railway.app/docs`
- [ ] Test API with curl/Postman
- [ ] Railway URL noted for frontend configuration

### Phase 2: Frontend (Vercel)

#### 2.1 Create Project

- [ ] Vercel project created
- [ ] GitHub repository connected
- [ ] Build settings verified (Next.js)

#### 2.2 Configure Environment

- [ ] `NEXT_PUBLIC_BACKEND_URL` set to Railway URL
- [ ] `NEXT_PUBLIC_SUPABASE_URL` set
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` set
- [ ] All environment variables use `NEXT_PUBLIC_` prefix

#### 2.3 Deploy & Test

- [ ] Frontend deployed successfully
- [ ] App accessible at Vercel URL
- [ ] Login page loads
- [ ] No console errors in browser
- [ ] Network tab shows requests going to Railway backend
- [ ] No direct Supabase database requests (only auth)

#### 2.4 Update Backend CORS

- [ ] Go back to Railway
- [ ] Update `CORS_ORIGINS` with Vercel URL
- [ ] Redeploy backend
- [ ] Test frontend → backend communication

### Phase 3: Database (Supabase)

#### 3.1 Enable RLS

- [ ] RLS enabled on `youtube_videos`
- [ ] RLS enabled on `subtitle_chunks`
- [ ] RLS enabled on `video_notes`
- [ ] RLS enabled on `books`
- [ ] RLS enabled on `book_chapters`
- [ ] RLS enabled on `book_notes`
- [ ] RLS enabled on `job_queue`

#### 3.2 Verify Security

- [ ] Test direct Supabase access (should fail)
- [ ] Backend can still access database (service role)
- [ ] Frontend CANNOT directly access database
- [ ] Auth still works

### Phase 4: End-to-End Testing

#### 4.1 Authentication

- [ ] User can sign up
- [ ] User can log in
- [ ] Token is sent to backend
- [ ] Protected routes work
- [ ] Unauthorized access is blocked

#### 4.2 Core Features

- [ ] Can add YouTube video
- [ ] Video metadata loads
- [ ] Subtitles extraction works
- [ ] Can view chunks
- [ ] Can add notes
- [ ] Can add book
- [ ] Book chapters load
- [ ] AI enrichment works

#### 4.3 Security Testing

- [ ] Open DevTools → Network
- [ ] Verify no direct Supabase DB calls
- [ ] Verify all API calls go to Railway backend
- [ ] Check for exposed secrets in source
- [ ] Test with user JWT token
- [ ] Test with expired token (should fail)

---

## Post-Deployment

### Monitoring Setup

- [ ] Railway metrics enabled
- [ ] Vercel analytics enabled
- [ ] Error tracking configured
- [ ] Log monitoring set up

### Domain Configuration (Optional)

- [ ] Custom domain for frontend
- [ ] Custom domain for backend
- [ ] DNS records configured
- [ ] SSL certificates verified

### Performance

- [ ] Frontend loads in < 3 seconds
- [ ] API response times < 500ms
- [ ] No memory leaks in Railway
- [ ] Database queries optimized

### Documentation

- [ ] Update README with production URLs
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Share credentials with team (securely)

---

## Rollback Plan

If something goes wrong:

### Immediate Rollback

- [ ] Revert to previous Railway deployment
- [ ] Revert to previous Vercel deployment
- [ ] Check database state
- [ ] Notify users if needed

### Root Cause Analysis

- [ ] Check Railway logs
- [ ] Check Vercel logs
- [ ] Check Supabase logs
- [ ] Identify issue
- [ ] Fix and prepare for re-deployment

---

## Verification Commands

### Test Backend Health

```bash
curl https://your-backend.railway.app/
```

### Test Backend API (with auth)

```bash
curl https://your-backend.railway.app/api/videos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Direct Supabase Access (should fail)

```bash
curl "https://your-project.supabase.co/rest/v1/youtube_videos" \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

### Check CORS

```bash
curl -I https://your-backend.railway.app/api/videos \
  -H "Origin: https://your-app.vercel.app"
```

---

## Common Issues & Solutions

### CORS Error

**Issue**: `Access-Control-Allow-Origin` header missing

**Solution**:

1. Check `CORS_ORIGINS` in Railway
2. Ensure Vercel URL is included
3. Redeploy backend

### Auth Error

**Issue**: "Invalid token" or "JWT verification failed"

**Solution**:

1. Verify `SUPABASE_JWT_SECRET` matches Supabase project
2. Check token format in requests
3. Ensure user email is verified

### Database Error

**Issue**: "No rows returned" or RLS blocking queries

**Solution**:

1. Verify backend uses service role key
2. Check RLS policies
3. Service role should bypass RLS

### Build Error

**Backend**: Check `requirements.txt` and Python version

**Frontend**: Check `package.json` and TypeScript errors

---

## Success Criteria

✅ **Deployment is successful when:**

- [ ] Frontend loads at Vercel URL
- [ ] Backend responds at Railway URL
- [ ] Users can log in
- [ ] All core features work
- [ ] No direct database access from frontend
- [ ] No console errors
- [ ] No CORS errors
- [ ] RLS is enabled
- [ ] Monitoring is active

---

## Next Steps After Deployment

1. Monitor for 24 hours
2. Collect user feedback
3. Set up automated backups
4. Configure CI/CD pipeline
5. Plan for scaling
6. Document lessons learned

---

## Emergency Contacts

- **Railway Support**: https://railway.app/help
- **Vercel Support**: https://vercel.com/support
- **Supabase Support**: https://supabase.com/support
- **Team Lead**: [Add contact]
- **Database Admin**: [Add contact]
