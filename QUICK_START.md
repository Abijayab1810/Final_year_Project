# 🚀 Quick Start Guide - Local Testing & Deployment

## Step 1: Prerequisites

Make sure you have:
- Python 3.9+ installed
- pip package manager
- Git (optional)

## Step 2: Install Dependencies

```bash
cd d:\projects\Final_year_project

# Install all required packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed ultralytics==8.0.205
Successfully installed opencv-python==4.8.1.78
...
Successfully installed streamlit==1.28.1
```

## Step 3: Start the Platform (Two Terminals)

### Terminal 1: Start FastAPI Backend (Port 8000)

```bash
cd d:\projects\Final_year_project
python api_auth.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

🟢 **Backend is ready at:** `http://localhost:8000`

### Terminal 2: Start Streamlit Frontend (Port 8501)

```bash
cd d:\projects\Final_year_project
streamlit run app_auth.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

🟢 **Frontend is ready at:** `http://localhost:8501`

---

## Step 4: Access the Platform

### 🌐 Open in Browser

**Main Dashboard:** `http://localhost:8501`

### 📝 Create Test Account

1. **First Time Access:**
   - Click the "📝 Sign Up" tab
   - Fill in:
     - **Username:** `testuser`
     - **Email:** `test@example.com`
     - **Password:** `TestPass123`
     - **Full Name:** `Test User`
   - Click "📝 Sign Up"

2. **Login:**
   - Use same credentials
   - Click "🔓 Login"
   - You're now in the dashboard!

### ✅ Test Accounts (Pre-created)

If you want to add pre-made test accounts, run:

```bash
python -c "
from users_db import register_user
users = [
    ('operator1', 'operator1@airport.com', 'Secure123'),
    ('operator2', 'operator2@airport.com', 'Secure456'),
    ('admin_user', 'admin@airport.com', 'AdminPass123'),
]
for username, email, password in users:
    result = register_user(username, email, password, username.upper())
    print(f'{username}: {result[\"message\"]}')
"
```

---

## Step 5: Test with Real CCTV Camera

### 📹 Add Your Friend's Father's Office Camera

1. **Dashboard → 📹 Camera Management**
2. **Click: ➕ Add New Camera**
3. **Fill in these fields:**

   ```
   Camera Name: "Office Building"
   RTSP URL: rtsp://192.168.1.100:554/stream  ← Ask for this
   Username: admin  (optional)
   Password: 12345  (optional)
   Port: 554
   Type: RTSP
   ```

4. **Click: 🧪 Test**
   - If ✅ Connected → Ready!
   - If ❌ Error → Check URL and credentials

### **Common RTSP URLs (Ask for these):**

| Camera Brand | Default RTSP URL |
|---|---|
| **Hikvision** | `rtsp://192.168.1.100:554/Streaming/Channels/101` |
| **Dahua** | `rtsp://192.168.1.100:554/stream/ch0` |
| **Generic IP** | `rtsp://192.168.1.100:554/stream` |

---

## Step 6: Start Detection

1. **Dashboard → 🟢 Live Monitoring**
2. **Select Camera:** Choose the office camera from dropdown
3. **Adjust Settings:**
   - Abandonment Time Limit: 5 seconds (start here)
   - Detection Confidence: Use default
4. **Check:** 🟢 START SECURITY FEED
5. **Detection Starts!** ✅

---

## Step 7: Real-Time Configuration (No Redeployment!)

### 📋 Edit Settings On-The-Fly

**File Location:** `d:\projects\Final_year_project\detection_config.json`

**Edit with any text editor:**

```json
{
    "detection": {
        "min_abandonment_time": 3,
        "confidence_threshold": 0.35,
        "frame_width": 320
    },
    "tracking": {
        "dynamic_tolerance_pct": 0.10
    }
}
```

### 🔧 Common Adjustments for Real CCTV:

**Problem: Too many false positives**
```json
"confidence_threshold": 0.35 → 0.50
"min_abandonment_time": 3 → 5
```

**Problem: Missing detections (occlusion)**
```json
"confidence_threshold": 0.35 → 0.25
"frame_width": 320 → 640
```

**Problem: Slow processing**
```json
"frame_width": 320 → 416 (or 320)
"person_check_interval": 15 → 30
```

### 💻 Python Script to Update Config:

```bash
python
```

```python
from config import update_parameter, load_config, print_config

# View current config
print_config()

# Adjust detection time
update_parameter("detection", "min_abandonment_time", 5)

# Adjust confidence
update_parameter("detection", "confidence_threshold", 0.40)

# Changes apply IMMEDIATELY on next frame!
```

---

## Step 8: Monitor Detections

### 📊 View Detection Logs

1. **Dashboard → 📊 Forensic History**
2. See all detected abandoned items with:
   - ⏱️ Duration detected
   - 🕐 Timestamp
   - 📸 Evidence image
   - 📍 Location coordinates

### 📈 View Statistics

1. **Dashboard → 📈 Statistics**
2. See:
   - Total detections
   - Average duration
   - Detection accuracy
   - Detection timeline

---

## 🔗 API Documentation

### Access Interactive API Docs

**Swagger UI:** `http://localhost:8000/docs`
**ReDoc UI:** `http://localhost:8000/redoc`

### Example: Add Detection via API

```bash
curl -X POST "http://localhost:8000/detections/log" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "track_id": 1,
    "duration_seconds": 25,
    "camera_id": "Office-001",
    "confidence": 0.87,
    "frame_width": 640,
    "frame_height": 480,
    "bag_x1": 100,
    "bag_y1": 100,
    "bag_x2": 200,
    "bag_y2": 300
  }'
```

---

## 🚨 Troubleshooting

### Issue: "Port 8501 already in use"

```bash
# Kill existing Streamlit
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run app_auth.py --server.port 8502
```

### Issue: "Camera won't connect"

```bash
# Test RTSP URL with VLC
vlc rtsp://192.168.1.100:554/stream

# Or test with FFmpeg
ffplay rtsp://192.168.1.100:554/stream
```

### Issue: "OpenVINO model not found"

```bash
# Make sure model files exist
ls -la best_int8_openvino_model/
```

Should show:
```
best.xml
metadata.yaml
```

### Issue: Models downloading (first run)

First run will download YOLOv8 models (~100MB). Wait for:
```
✅ Successfully loaded models
```

---

## 📊 Performance Tips for Real CCTV

### 🖥️ Hardware Requirements

| Component | Min | Recommended |
|---|---|---|
| CPU | Dual Core | Quad Core i5+ |
| RAM | 4GB | 8GB+ |
| Storage | 50GB | 100GB+ |
| Network | 10Mbps | 100Mbps+ |

### ⚡ Optimization

1. **Position CCTV on same network**
   - Lower latency
   - Better stability

2. **Adjust frame size in config**
   ```json
   "frame_width": 320,  ← Lower = faster, less accurate
   "frame_height": 320  ← Lower = faster, less accurate
   ```

3. **Increase person check interval**
   ```json
   "person_check_interval": 30  ← Check less often = faster
   ```

4. **Use lighter confidence thresholds**
   ```json
   "confidence_threshold": 0.25  ← Lower = faster BUT more false positives
   ```

---

## 🔄 Hot-Reload Workflow (Testing & Tweaking)

### Scenario: Detection not working well at office

**Without Redeployment:**

1. **Terminal running Streamlit** - KEEP RUNNING
2. **Edit `detection_config.json`** - Make changes
3. **Refresh browser** (`F5`) - New settings apply
4. **Test again** - See results
5. **Adjust again** - Repeat until perfect

**No need to:**
- Restart servers
- Rebuild Docker
- Redeploy to cloud
- Recompile anything

---

## 🧪 Testing Checklist

Before deploying to production:

- [ ] Can login with test account
- [ ] Can add camera and test connection
- [ ] Can see live feed (if office camera available)
- [ ] Detection works on test footage
- [ ] Changed detection timeout in config.json
- [ ] Settings reloaded without restart
- [ ] Viewed forensic history
- [ ] Viewed statistics
- [ ] Can export CSV
- [ ] API endpoints responding (Swagger UI)

---

## 📱 Mobile/Remote Access

### Access from remote machine:

Replace `localhost` with your machine IP:

```
http://YOUR_MACHINE_IP:8501   ← Streamlit
http://YOUR_MACHINE_IP:8000   ← API
```

**Find your IP:**
```bash
ipconfig  # Windows
ifconfig  # Linux/Mac
```

Look for IPv4 address like: `192.168.1.100`

---

## 🚀 Next Steps

### Option 1: Keep Testing Locally
- Keep Streamlit + API running
- Test with office cameras
- Adjust config as needed
- No redeployment needed

### Option 2: Deploy to Cloud (Later)

```bash
# When ready, deploy to Heroku
heroku create my-luggage-app
git push heroku main

# Or use Docker
docker build -t luggage-app .
docker-compose up
```

---

## 📞 Quick Reference

| What | Where | How |
|---|---|---|
| **Dashboard (UI)** | `http://localhost:8501` | Open browser |
| **API Docs** | `http://localhost:8000/docs` | Swagger UI |
| **Edit Settings** | `detection_config.json` | Any text editor |
| **View Logs** | Dashboard → Forensic History | In app |
| **Add Camera** | Dashboard → Camera Management | In app |
| **Test Camera** | Camera Management → Test button | In app |
| **Stop Servers** | Ctrl+C in both terminals | Keyboard interrupt |

---

## ✅ Summary

```
1. pip install -r requirements.txt           ← Install dependencies
2. Terminal 1: python api_auth.py            ← Start backend
3. Terminal 2: streamlit run app_auth.py     ← Start frontend
4. Open: http://localhost:8501               ← Access dashboard
5. Sign up or login                          ← Create account
6. Add camera via Camera Management          ← Add office CCTV
7. Go to Live Monitoring                     ← Start detection
8. Edit detection_config.json                ← Tune settings
9. Refresh browser                           ← Apply changes
10. No restart needed! ✅                    ← Magic!
```

**You're ready to test at the office! 🎉**

---

**Last Updated:** April 8, 2026  
**Version:** 2.0.0 Multi-Camera Edition
