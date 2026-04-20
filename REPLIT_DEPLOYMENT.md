# Replit Deployment Guide

Deploy your YOLOv8 Abandoned Luggage Detection system on Replit for **FREE**! 🚀

## Quick Deploy (5 minutes)

### Step 1: Go to Replit
1. Open https://replit.com
2. Sign up or log in with GitHub
3. Click **"+ Create"** or **"New Replit"**

### Step 2: Import from GitHub
1. Select **"Import from GitHub"**
2. Paste your repository URL: `https://github.com/Abijayab1810/Final_year_Project`
3. Click **"Import"**

Replit will automatically:
- ✅ Clone your repository
- ✅ Detect the Python project
- ✅ Install dependencies from requirements.txt
- ✅ Create a web server environment

### Step 3: Configure the Run Command
1. Click **".replit"** file (or create it)
2. Set the run command to start your FastAPI app:

```
run = "uvicorn main:app --host 0.0.0.0 --port 8000"
```

3. Click **"Run"** button (top toolbar)

### Step 4: Get Your Public URL
- Replit will show a **"Webview"** tab with your live app
- The public URL is shown at the top (like `https://your-project.replit.dev`)
- This URL is **publicly accessible**!

## What Runs on Replit

**FastAPI Backend** (Primary):
- HTTP API: `/api/detect`
- WebSocket: `/ws`
- Health check: `/health`
- Runs on port 8000

**Streamlit Frontend** (Optional):
- Dashboard available but requires separate deployment
- You can access FastAPI endpoints directly via the web interface

## Important Notes

### Replit Free Tier Limits:
- ✅ Always-on hosting during active development
- ⏱️ Projects **go to sleep after 1 hour of inactivity**
- ✅ Wakes up automatically when accessed
- 📦 5GB storage limit (plenty for source code)
- 🔄 Free tier has some CPU throttling (still good for demos)

### Wake-up Behavior:
- First access after sleep takes **~10-20 seconds** to start
- Subsequent requests are instant
- Good for **demos and testing**, less ideal for production

### Model Loading:
- **First run takes ~1-2 minutes** (downloading YOLOv8 model)
- Subsequent runs are **instant** (model cached)
- The app will be unresponsive during first load—wait for it!

## How to Optimize on Replit

### Add the `.replit` Config File:
Create `.replit` in your repository root:

```yaml
run = "uvicorn main:app --host 0.0.0.0 --port 8000"
entrypoint = "main.py"
language = "python3"
channels = ["python"]

[env]
PYTHONUNBUFFERED = "1"
```

### Keep Your Replit Awake:
- Access your app regularly to prevent sleep
- Share the link with your CV engineer for review
- Mention the 1-hour sleep limit (they'll understand for proof-of-concept)

## Share Your Live App

Once running, share this URL with your CV engineer:
```
https://your-project.replit.dev
```

They can:
- ✅ See live FastAPI endpoints
- ✅ Test API with sample images
- ✅ View performance metrics
- ✅ Check the database if accessible
- ✅ Review your source code (visible on Replit)

## Upgrade to Always-On (Optional)

If you need always-on hosting:
- **Replit Hacker ($7/month)**: Always-on, 10GB storage, faster CPU
- **Render Free Tier**: Sleep after 15 min inactivity, 500 hours/month
- **Railway Paid**: $5-10/month, full production features

## Testing Before Deploy

### Local Test First:
```bash
# Run locally to verify everything works
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Then visit http://localhost:8000
```

### Check Dependencies:
Make sure all required packages are in `requirements.txt`:
```
uvicorn
fastapi
opencv-python
ultralytics
openvino
websockets
streamlit
sqlalchemy
```

## Troubleshooting on Replit

| Problem | Solution |
|---------|----------|
| **App won't start** | Check "Webview" for error logs |
| **Model not found** | First run needs 1-2 min to download, be patient |
| **Port already in use** | Replit auto-assigns port 8000, should work |
| **Dependencies missing** | Replit auto-installs from requirements.txt—wait for it |
| **Slow after 1 hour** | Replit put it to sleep, just refresh the page |

## Next Steps

1. ✅ Go to https://replit.com
2. ✅ Click **"Import from GitHub"**
3. ✅ Paste your repo URL
4. ✅ Click **"Run"**
5. ✅ Share the public URL with your CV engineer
6. ✅ Mention it's a working proof-of-concept (free tier with auto-sleep)

**Deployment time: ~5 minutes to live!** 🎉

Good luck! Let me know if you hit any issues.
