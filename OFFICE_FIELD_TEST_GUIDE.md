# 🎯 Complete Field Testing Guide - Office CCTV

## Quick Answer to Your Questions

### ❓ "Where is the link?"

**The link is LOCAL (on your computer):**

```
🌐 Dashboard:  http://localhost:8501
🔧 API Docs:  http://localhost:8000/docs
```

**How to get there:**

1. **Windows:** Double-click `START_PLATFORM.bat`
2. **Linux/Mac:** Run `bash start_platform.sh`
3. **Open browser:** Type `http://localhost:8501`

### ❓ "How do I test as a new user?"

**Login with these test accounts (pre-created):**

| Username | Password | Email |
|---|---|---|
| `demo` | `Demo123` | demo@example.com |
| `testuser` | `Test123` | test@example.com |
| `operator` | `Operator123` | operator@airport.com |

Or **create your own account** via Sign Up tab.

### ❓ "How do I edit without redeployment?"

**All detection settings in ONE file:**

```
📄 detection_config.json
```

**Change any value** → **Refresh browser** → **Takes effect immediately!**

---

## 🚀 Getting Started (5 Minutes)

### Step 1: Install Dependencies (2 min)

**Windows:**
```bash
cd d:\projects\Final_year_project
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
pip3 install -r requirements.txt
```

### Step 2: Initialize Platform (1 min)

```bash
python setup.py
```

**This creates:**
- ✅ All databases (users, cameras, detections)
- ✅ Test accounts ready to use
- ✅ Configuration file with defaults

### Step 3: Start Services (1 min)

**Windows:**
- Double-click `START_PLATFORM.bat`

**Linux/Mac:**
- Run `bash start_platform.sh`

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
Streamlit running on http://localhost:8501
```

### Step 4: Access Dashboard (1 min)

Open browser to: **http://localhost:8501**

You're now in the dashboard! ✅

---

## 🎓 Field Testing Workflow (At Office)

### Phase 1: Setup Camera (15 min)

1. **Get camera info from IT:**
   - RTSP URL (e.g., `rtsp://192.168.1.100:554/stream`)
   - Username (if needed)
   - Password (if needed)

2. **In dashboard:**
   - Click: **📹 Camera Management**
   - Click: **➕ Add New Camera**
   - Enter camera details
   - Click: **🧪 Test** → Should show ✅ Connected

### Phase 2: Test Detection (30 min)

1. **Go to:** **🟢 Live Monitoring**
2. **Select camera** from dropdown
3. **Check:** ✅ START SECURITY FEED
4. **Test with real baggage:**
   - Place a bag in view
   - Wait 5 seconds
   - Should alert if abandoned ✅

### Phase 3: Fine-Tune Settings (15 min)

**If detection isn't working well, edit config:**

```bash
# Open this file in ANY text editor:
detection_config.json
```

**Common adjustments:**

| Problem | Solution | Config Change |
|---|---|---|
| Too many false alerts | More picky | `confidence_threshold: 0.35 → 0.55` |
| Missing real bags | Less picky | `confidence_threshold: 0.35 → 0.20` |
| Bag resets when person passes | Better memory | `grace_period: 2.0 → 5.0` |
| Slow processing | Faster | `frame_width: 320 → 256` |

**After editing:**
- Save file (Ctrl+S)
- Refresh browser (F5)
- **Done!** Settings apply immediately ✅

### Phase 4: Collect Test Data (Optional)

Record in a spreadsheet:

```
Date: April 8, 2026
Location: Friend's Father's Office

Test 1: Basic Detection
- Bags placed: 10
- Detected: 8
- False positives: 1
- FPS: 18

Settings Used:
- min_abandonment_time: 5
- confidence_threshold: 0.35
- frame_width: 320
```

---

## 📹 Different Scenarios You'll Face

### Scenario 1: Crowded Area (Lots of People)

**Problem:** False positives, too many alerts

**Solution:**
```json
{
  "detection": {
    "min_abandonment_time": 8,
    "confidence_threshold": 0.55
  },
  "tracking": {
    "dynamic_tolerance_pct": 0.15
  }
}
```

### Scenario 2: Occlusions (People Walking by)

**Problem:** Bag disappears when someone blocks it

**Solution:**
```json
{
  "tracking": {
    "grace_period": 5.0,
    "person_conf_threshold": 0.7
  },
  "processing": {
    "max_age_frames": 2000
  }
}
```

### Scenario 3: Poor Lighting

**Problem:** Objects not detected clearly

**Solution:**
```json
{
  "detection": {
    "confidence_threshold": 0.20,
    "frame_width": 416,
    "frame_height": 416
  }
}
```

### Scenario 4: Slow Computer/Hardware

**Problem:** FPS too low, system laggy

**Solution:**
```json
{
  "detection": {
    "frame_width": 256,
    "frame_height": 256
  },
  "processing": {
    "person_check_interval": 30
  }
}
```

---

## 🔧 All Tuning Parameters Explained

### Detection Section
```json
"detection": {
    "min_abandonment_time": 5,        // Increase for fewer false positives
    "max_abandonment_time": 300,      // Max tracking time
    "confidence_threshold": 0.35,     // LOWER = sensitive, HIGHER = strict
    "frame_width": 320,               // HIGHER = better quality, slower
    "frame_height": 320
}
```

### Tracking Section
```json
"tracking": {
    "dynamic_tolerance_pct": 0.10,    // Movement allowance (lower = stricter)
    "grace_period": 2.0,              // Forgiveness when bag disappears
    "person_conf_threshold": 0.5      // Person detection confidence
}
```

### Processing Section
```json
"processing": {
    "person_check_interval": 15,      // Lower = more accurate, higher = faster
    "max_age_frames": 1000,           // How long to remember a bag
    "save_evidence": True             // Save images of detections
}
```

---

## 🧪 Testing at Office - Day By Day

### Day 1: Setup & Baseline

- [ ] Install software
- [ ] Run `python setup.py`
- [ ] Start platform with `START_PLATFORM.bat`
- [ ] Create account / login
- [ ] Add office camera
- [ ] Test connection ✅
- [ ] Record baseline settings

### Day 2: Detection Testing

- [ ] Test with 10 bags at different locations
- [ ] Record what works / what doesn't
- [ ] Note any false positives
- [ ] Calculate detection rate

### Day 3: Fine-Tuning

- [ ] Adjust ONE parameter only
- [ ] Test again
- [ ] Record new results
- [ ] Repeat for each parameter

### Day 4: Occlusion Testing

- [ ] Place bag in view
- [ ] Walk in front repeatedly
- [ ] Does it track through or reset?
- [ ] Adjust grace_period if needed

### Day 5: Final Validation

- [ ] Run full day of monitoring
- [ ] Check for false positives
- [ ] Document final working configuration
- [ ] Ready for deployment!

---

## 📊 Configuration Comparison

### Quick Comparison of Common Settings

| Use Case | Confidence | Time | Frame Size | Grace Period |
|---|---|---|---|---|
| **Sensitive** | 0.15 | 2s | 416 | 2.0 |
| **Balanced** | 0.35 | 5s | 320 | 2.0 |
| **Strict** | 0.60 | 10s | 320 | 3.0 |
| **Fast** | 0.35 | 5s | 256 | 2.0 |

---

## 🚨 Troubleshooting at Office

### Issue: Dashboard won't load

```bash
# Check if backend is running
http://localhost:8000/health  # Should show {"status": "healthy"}

# If not, restart from START_PLATFORM.bat
```

### Issue: Camera won't connect

```bash
# 1. Verify RTSP URL works in VLC:
vlc rtsp://192.168.1.100:554/stream

# 2. Check network connectivity:
ping 192.168.1.100

# 3. Verify credentials are correct
```

### Issue: No detections

```bash
# 1. Lower confidence threshold
"confidence_threshold": 0.35 → 0.20

# 2. Reduce frame size
"frame_width": 320 → 416

# 3. Reduce abandonment time
"min_abandonment_time": 5 → 2
```

### Issue: Too many false alerts

```bash
# 1. Increase confidence threshold
"confidence_threshold": 0.35 → 0.60

# 2. Increase abandonment time
"min_abandonment_time": 5 → 8

# 3. Increase movement tolerance
"dynamic_tolerance_pct": 0.10 → 0.15
```

---

## 💾 Important Files Reference

| File | Purpose | Edit? |
|---|---|---|
| `detection_config.json` | **ALL settings** | ✅ YES (for tuning) |
| `app_auth.py` | Dashboard UI | ❌ No |
| `api_auth.py` | Backend API | ❌ No |
| `cameras_db.py` | Camera management | ❌ No |
| `users.db` | User database | ❌ No |
| `forensic_detections.db` | Detection logs | ❌ No |
| `cameras.db` | Camera profiles | ❌ No |

---

## 📚 Documentation Map

| Document | Purpose | When to Read |
|---|---|---|
| **QUICK_START.md** | How to run the platform | Before first launch |
| **TUNING_GUIDE.md** | How to adjust detection | When thing not working |
| **CAMERA_MANAGEMENT_GUIDE.md** | Camera setup help | When adding cameras |
| **CAMERA_MANAGEMENT_SUMMARY.md** | Technical details | If curious about architecture |
| **DEPLOYMENT.md** | Cloud deployment | When ready for production |

---

## ✅ Pre-Office Checklist

Before going to friend's father's office:

- [ ] Installed Python 3.9+
- [ ] Ran `pip install -r requirements.txt`
- [ ] Ran `python setup.py`
- [ ] Can start services with `START_PLATFORM.bat`
- [ ] Can access `http://localhost:8501`
- [ ] Can login with test account
- [ ] Understand how to edit `detection_config.json`
- [ ] Know how to refresh browser to apply changes
- [ ] Have RTSP URL for office camera
- [ ] Have camera credentials (username/password)

---

## 🎯 Your Field Testing Superpower

### No Redeployment = Fast Iteration

```
Traditional Process:
  Find problem → Fix code → Rebuild → Redeploy → Test (30 min)

Your Process:
  Find problem → Edit JSON → Refresh browser → Test (30 sec)
```

**That's 60× faster!**

---

## 🚀 Ready to Go!

### Commands to Remember:

```bash
# First time
python setup.py

# Jump start
START_PLATFORM.bat  (Windows)
bash start_platform.sh  (Linux/Mac)

# Access
http://localhost:8501

# Edit config
detection_config.json
```

### Test Accounts:
```
demo / Demo123
testuser / Test123
operator / Operator123
```

### When Problems Occur:
1. Edit `detection_config.json`
2. Save (Ctrl+S)
3. Refresh browser (F5)
4. Test again
5. No restart needed! ✅

---

## 📞 Quick Reference Card

Print or screenshot this:

```
LUGGAGE DETECTION SYSTEM - QUICK REFERENCE

START:        START_PLATFORM.bat
DASHBOARD:    http://localhost:8501
API DOCS:     http://localhost:8000/docs

TEST LOGIN:   demo / Demo123

EDIT CONFIG:  detection_config.json
APPLY:        Save (Ctrl+S) → Refresh (F5)

PROBLEMS:     See TUNING_GUIDE.md
HELP:         See QUICK_START.md
CAMERAS:      See CAMERA_MANAGEMENT_GUIDE.md

NO DEPLOYMENT NEEDED!
Just edit JSON and refresh! 🎉
```

---

**Version:** 2.0.0 - Multi-Camera Edition  
**Date:** April 8, 2026  
**Status:** Ready for Field Testing ✅

You're all set to test at your friend's father's office! 🎉

