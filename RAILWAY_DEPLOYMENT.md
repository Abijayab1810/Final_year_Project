# Railway Deployment Guide

Your YOLOv8 Abandoned Luggage Detection system is ready to deploy on Railway! 🚀

## Quick Deploy (2 minutes)

### Step 1: Go to Railway
1. Open https://railway.app
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub"**

### Step 2: Connect GitHub
1. Click **"Configure GitHub App"**
2. Authorize Railway to access your GitHub account
3. Select your repository: **`Final_year_Project`**
4. Click **"Deploy"**

Railway will automatically:
- ✅ Detect your Dockerfile
- ✅ Build the production container
- ✅ Deploy your FastAPI + Streamlit application
- ✅ Assign a public HTTPS URL

### Step 3: Get Your Public URL
1. Go to your Railway project dashboard
2. Find the **"Deployments"** tab
3. Click the latest deployment
4. Look for **"Domain"** or **"Public URL"**
5. Your app will be at: `https://yourapp-xxxxx.railway.app`

## Environment Variables (Optional)

If you need to configure environment variables in Railway:

1. In Railway dashboard → **"Variables"** tab
2. Add any optional settings:
   - `LOG_LEVEL=INFO` (default)
   - `MAX_UPLOAD_SIZE=50` (MB, default 50)
   - `DETECTION_CONFIDENCE=0.5` (default)

## What Gets Deployed

Your app includes two entry points:

**FastAPI Backend** (Main):
- REST API for detection: `POST /api/detect`
- WebSocket for real-time: `ws://app/ws`
- Health check: `GET /health`
- Runs on port `8000` (Railway proxies to HTTPS)

**Streamlit Frontend** (Optional):
- Interactive dashboard at `/streamlit`
- Direct launch: `https://yourapp-xxxxx.railway.app/streamlit`

## Access Your App

### After deployment, visit:
```
https://yourapp-xxxxx.railway.app
```

This will show:
- ✅ Live detection interface
- ✅ Performance metrics
- ✅ Model comparison
- ✅ Statistics dashboard
- ✅ Saved detections
- ✅ Upload test files

### For Direct Streamlit Access:
```
https://yourapp-xxxxx.railway.app/streamlit
```

## Troubleshooting

### Build Failing?
- Check Railway logs: `Deployments` → Click deployment → **"Build Logs"**
- Common issue: Missing dependencies (check `requirements.txt`)

### App Crashes After Deploy?
- Check Runtime Logs: `Deployments` → Click deployment → **"Runtime Logs"**
- Likely cause: Environment variables or model loading

### Slow Startup?
- First startup takes 30-60 seconds (OpenVINO model loads)
- Subsequent requests are fast (~30 FPS)

## Scale Up (Production)

Once deployed, you can:
- **Add multiple replicas** for load balancing
- **Enable auto-scaling** based on traffic
- **Monitor performance** in Railway dashboard
- **Set custom domains** (yourcompany.com)

## Share With Your CV Engineer

Share this URL:
```
https://yourapp-xxxxx.railway.app
```

They can:
1. **Try live detection** - Upload images/videos
2. **See performance metrics** - FPS, latency, accuracy
3. **Check database** - All detections logged with timestamps
4. **Review documentation** - Architecture, optimization details

## Next Steps

After successful deployment:
1. ✅ Test the live detection interface
2. ✅ Upload a sample image/video
3. ✅ Verify database logging
4. ✅ Share public URL with CV engineer
5. ✅ Monitor logs for any issues

Good luck! 🎉
