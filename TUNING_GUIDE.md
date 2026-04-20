# 🔧 Real-Time Configuration Tuning Guide

## No Redeployment Required!

All detection settings can be adjusted **on-the-fly** without restarting servers or redeploying.

**File:** `detection_config.json` (in project root)

---

## 🎯 How It Works

```
You're running detection...
  ↓
Edit detection_config.json (any text editor)
  ↓
Refresh browser (F5)
  ↓
New settings apply IMMEDIATELY on next frame!
  ↓
NO restart needed ✅
NO redeployment ✅
```

---

## 📋 Configuration Parameters

### Detection Settings

```json
"detection": {
    "min_abandonment_time": 3,      // Seconds before alert (increase = less false positives)
    "max_abandonment_time": 300,    // Max tracking time in seconds
    "confidence_threshold": 0.35,   // YOLO confidence 0.0-1.0 (lower = more detections)
    "frame_width": 320,             // Detection frame size (higher = more accuracy, slower)
    "frame_height": 320             // Keep square for YOLO
}
```

### Tracking Settings

```json
"tracking": {
    "dynamic_tolerance_pct": 0.10,  // Movement tolerance (lower = stricter)
    "grace_period": 2.0,            // Seconds before cleanup
    "person_conf_threshold": 0.5    // Person detection confidence
}
```

### Processing Settings

```json
"processing": {
    "person_check_interval": 15,    // Frames between person detection (higher = faster)
    "max_age_frames": 1000,         // Max frames to track bag
    "save_evidence": True           // Save images of detected bags
}
```

---

## 🚀 Quick Tuning Guide

### Problem 1: Too Many False Positives (Bags Detected That Aren't Really Abandoned)

**Symptoms:**
- Every object flagged as abandoned bag
- Too many alerts
- Frustrating noise

**Solution - Most Aggressive (Start Here):**

```json
{
  "detection": {
    "min_abandonment_time": 8,        // INCREASE: Need 8 seconds, not 3
    "confidence_threshold": 0.55      // INCREASE: More picky about what's a bag
  },
  "tracking": {
    "dynamic_tolerance_pct": 0.15     // INCREASE: Allow more movement before reset
  }
}
```

**If still getting false positives:**

```json
{
  "detection": {
    "min_abandonment_time": 12,       // Even higher
    "confidence_threshold": 0.70      // Very picky
  }
}
```

---

### Problem 2: Missing Detections (Real Bags Not Being Detected)

**Symptoms:**
- Baggage visible to you but not detected
- Empty forensic history
- No alerts for obvious abandoned bags

**Solution - Most Aggressive (Start Here):**

```json
{
  "detection": {
    "min_abandonment_time": 2,        // DECREASE: Alert faster
    "confidence_threshold": 0.20,     // DECREASE: Less picky
    "frame_width": 416,               // INCREASE: Better resolution
    "frame_height": 416
  },
  "tracking": {
    "dynamic_tolerance_pct": 0.08     // DECREASE: More sensitive to movement
  }
}
```

**If still missing baggage:**

```json
{
  "detection": {
    "min_abandonment_time": 1,        // Very fast alert
    "confidence_threshold": 0.15,     // Very permissive
    "frame_width": 640,               // Highest resolution (slower)
    "frame_height": 640
  }
}
```

---

### Problem 3: Occlusions (Bags Hidden Behind People/Objects)

**Symptoms:**
- Bag disappears when person walks by
- Detection resets each time something blocks view
- Bag reappears but timer resets

**Solution:**

```json
{
  "tracking": {
    "grace_period": 5.0,              // INCREASE: Don't forget quickly
    "person_conf_threshold": 0.7      // INCREASE: Must be very sure it's a person
  },
  "processing": {
    "max_age_frames": 2000            // INCREASE: Remember longer
  }
}
```

**For aggressive occlusion handling:**

```json
{
  "tracking": {
    "grace_period": 10.0,             // Very forgiving
    "person_conf_threshold": 0.8      // Very high person detection threshold
  },
  "processing": {
    "max_age_frames": 5000,           // Remember for very long time
    "person_check_interval": 30       // Check less often if person might be there
  }
}
```

---

### Problem 4: Slow Processing (FPS Too Low)

**Symptoms:**
- Detection is slow/laggy
- FPS counter shows <10 FPS
- Real-time monitoring is delayed

**Solution - Fastest:**

```json
{
  "detection": {
    "frame_width": 224,               // REDUCE: Faster processing
    "frame_height": 224
  },
  "processing": {
    "person_check_interval": 30       // INCREASE: Check less often
  },
  "models": {
    "device": "cpu"                   // Keep as CPU if that works
  }
}
```

**Balanced Speed/Accuracy:**

```json
{
  "detection": {
    "frame_width": 320,               // Standard
    "frame_height": 320
  },
  "processing": {
    "person_check_interval": 20       // Less aggressive checking
  }
}
```

---

### Problem 5: High CPU Usage

**Symptoms:**
- 100% CPU usage
- Computer gets hot
- Other apps slow down

**Solution:**

```json
{
  "detection": {
    "frame_width": 256,               // Reduce size
    "frame_height": 256
  },
  "processing": {
    "person_check_interval": 30       // Check less frequently
  },
  "tracking": {
    "dynamic_tolerance_pct": 0.12     // Reduce precision
  }
}
```

---

## 🧪 Testing Workflow (Field Testing at Office)

### Scenario: Testing at friend's father's office

**Step 1: Initial Setup (Baseline)**

Use defaults first:
- `min_abandonment_time`: 5 seconds
- `confidence_threshold`: 0.35
- `frame_width`: 320

**Step 2: First Test Run**

1. Set up camera in common area
2. Place a bag and walk away
3. Does it detect? 
   - Yes ✅ → Go to Step 3
   - No ❌ → Increase sensitivity (Problem 2 solution)

**Step 3: False Positive Test**

4. Place various objects (backpacks, boxes, luggage carts)
5. Are they all detected as abandoned? 
   - Too many ❌ → Reduce sensitivity (Problem 1 solution)
   - Reasonable ✅ → Go to Step 4

**Step 4: Occlusion Test**

6. Place a bag, walk in front repeatedly
7. Does it keep tracking or reset each time? 
   - Resets ❌ → Increase grace period (Problem 3 solution)
   - Tracks through ✅ → Go to Step 5

**Step 5: Performance Test**

8. Watch FPS counter
   - Below 10 FPS ❌ → Reduce frame size (Problem 4 solution)
   - 15+ FPS ✅ → Perfect!

### Real-Time Adjustment Workflow

```
Test running...
  ↓
See problem (e.g., too many false positives)
  ↓
Open detection_config.json in editor
  ↓
Make small change (e.g., confidence_threshold: 0.35 → 0.45)
  ↓
Save file (Ctrl+S)
  ↓
Refresh browser (F5)
  ↓
Test again immediately
  ↓
Good? Done! Bad? Adjust again
```

---

## 📊 Configuration Presets

### Preset 1: "Sensitive" (Catch Everything)

Good for: Low-traffic areas, need to catch all bags

```json
{
  "detection": {
    "min_abandonment_time": 2,
    "confidence_threshold": 0.15,
    "frame_width": 416,
    "frame_height": 416
  }
}
```

### Preset 2: "Balanced" (Recommended Start)

Good for: Most scenarios

```json
{
  "detection": {
    "min_abandonment_time": 5,
    "confidence_threshold": 0.35,
    "frame_width": 320,
    "frame_height": 320
  }
}
```

### Preset 3: "Strict" (Reduce False Positives)

Good for: High-traffic areas, lots of clutter

```json
{
  "detection": {
    "min_abandonment_time": 10,
    "confidence_threshold": 0.60,
    "frame_width": 320,
    "frame_height": 320
  },
  "tracking": {
    "dynamic_tolerance_pct": 0.15
  }
}
```

### Preset 4: "Performance" (Fast)

Good for: Low-end hardware

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

## 🔄 How to Apply Presets

**File:** `detection_config.json`

**Option 1: Manual Edit**

Open file, find the section, change values

**Option 2: Command Line**

```bash
python
```

```python
from config import update_parameter

# Apply "Strict" preset
update_parameter("detection", "min_abandonment_time", 10)
update_parameter("detection", "confidence_threshold", 0.60)

# Verify
from config import load_config, print_config
print_config()
```

---

## 📈 Testing Data to Collect

At the office, document:

| Test | Result | Notes |
|---|---|---|
| **Detection Rate** | __/10 bags found | How many of 10 test bags detected? |
| **False Positives** | __/hour | How many wrong alerts? |
| **Processing Speed** | __ FPS | Frames per second |
| **Occlusion Test** | Passed/Failed | Survived person walking by? |
| **Best Settings** | See below | Record final config |

**Best Final Configuration:**
```
min_abandonment_time: ___
confidence_threshold: ___
frame_width: ___
person_check_interval: ___
```

---

## 🚨 Emergency Adjustments

### If detection is completely broken:

**Reset to defaults:**

```bash
python
```

```python
from config import reset_to_defaults, print_config
reset_to_defaults()
print_config()
```

This loads `DEFAULT_CONFIG` (safe baseline).

### View current config:

```python
from config import load_config, print_config
print_config()
```

Displays all current settings.

---

## 💡 Pro Tips

### Tip 1: Small Changes Work Best

Change **ONE** parameter at a time:
```json
✅ "min_abandonment_time": 5 → 6  (small change)
❌ "min_abandonment_time": 5 → 15 (too big)
```

### Tip 2: Test Before Deploying

Perfect your settings at office first, THEN deploy.

### Tip 3: Document Your Adjustments

Keep notes of what worked:
```
Office Building Setup - April 8, 2026

Issue: Missing bags near corner (occlusions)
Solution:
  - grace_period: 2.0 → 5.0
  - min_abandonment_time: 3 → 4

Result: 95% detection rate, 2% false positives
```

### Tip 4: Use Browser Dev Tools

Press F12 to see console messages from detection logic.

---

## 🔗 Related Files

- **Main Config:** `detection_config.json` (auto-created)
- **Config Module:** `config.py` (Python interface)
- **Detection Code:** `app_auth.py` (uses config values)

---

## ❓ FAQ

**Q: Do I need to restart anything after changing config?**
A: No! Just refresh browser. Changes apply immediately.

**Q: What if config file gets corrupted?**
A: Delete it and restart app. Fresh copy with defaults created automatically.

**Q: Can I change config while detection is running?**
A: Yes! Changes apply on next frame (within 1 second).

**Q: Best values for typical office?**
A: Start with "Balanced" preset above. Tune from there.

**Q: Will changed config affect past detections?**
A: No. Only affects future detections. History stays intact.

---

## 📞 Support

If you find issues at office:

1. **Document the problem**
   - Screenshot of config
   - Screenshot of detection result
   - FPS value at the moment

2. **Try a preset** (see above)

3. **Adjust one parameter** at a time

4. **Keep test results** for reference

---

**Last Updated:** April 8, 2026  
**Version:** 2.0.0  
**Ready for Field Testing:** ✅
