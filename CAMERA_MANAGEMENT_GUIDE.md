# 📹 CCTV Camera Management Guide

## Overview

The Luggage Detection platform now supports connecting multiple CCTV cameras for abandoned luggage detection. This guide covers setting up cameras, managing connections, and monitoring multiple camera feeds.

---

## Features

✅ **Multi-Camera Support** - Connect unlimited CCTV cameras to your account
✅ **RTSP Protocol** - Support for any RTSP-compatible camera
✅ **Credential Management** - Safely store camera username and password
✅ **Connection Testing** - Test camera connectivity before use
✅ **Live Monitoring** - Switch between cameras during monitoring
✅ **Connection Status Tracking** - See which cameras are online/offline

---

## Getting Started

### Step 1: Access Camera Management

1. Log in to the platform
2. In the sidebar, select **📹 Camera Management** tab
3. You'll see two tabs:
   - **📋 My Cameras** - View connected cameras
   - **➕ Add New Camera** - Add a new camera

### Step 2: Connect Your First Camera

#### Option A: With Camera Credentials

1. Go to the **➕ Add New Camera** tab
2. Fill in the following fields:

   | Field | Example | Required |
   |-------|---------|----------|
   | **Camera Name** | Terminal 1 Front Gate | ✅ Yes |
   | **RTSP URL** | rtsp://192.168.1.100:554/stream | ✅ Yes |
   | **Username** | admin | ❌ Optional |
   | **Password** | password123 | ❌ Optional |
   | **Port** | 554 | Defaults to 554 |
   | **Camera Type** | RTSP / HTTP / USB | Defaults to RTSP |

3. Click **➕ Add Camera**
4. Camera appears in your list

#### Option B: Without Credentials (Anonymous Access)

Leave the username and password fields empty if your camera allows anonymous RTSP streaming.

### Step 3: Test Camera Connection

1. Go to **📋 My Cameras** tab
2. Find your camera in the list
3. Click the **🧪 Test** button
4. Wait for connection result:
   - ✅ **Connected** - Camera is working
   - ❌ **Error** - Check URL and credentials

---

## Common Camera RTSP URLs

### Hikvision (Popular Airport/Security Cameras)
```
rtsp://username:password@192.168.1.100:554/Streaming/Channels/101
```
- Default username: `admin`
- Default password: usually printed on camera

### Dahua (Common in Asia-Pacific)
```
rtsp://username:password@192.168.1.100:554/stream/ch0
```

### Axis Communications (Professional Networks)
```
rtsp://username:password@192.168.1.100:554/axis-media/media.amp
```

### Uniview (Enterprise Surveillance)
```
rtsp://username:password@192.168.1.100:554/media/video1
```

### Generic / IP Cameras
```
rtsp://192.168.1.100:554/stream
rtsp://192.168.1.100:554/video1
rtsp://192.168.1.100:554/streaming/channels/1
```

### Local USB Camera (Fallback)
```
0  (for built-in webcam)
1  (for USB external camera)
```

---

## Finding Your Camera's RTSP URL

### Method 1: Check Camera Manual
- Look in the camera manual for "RTSP" or "streaming" section
- RTSP URL is usually in the format: `rtsp://[IP]:[PORT]/[PATH]`

### Method 2: Network Scanning
```bash
# Linux/Mac: Find camera IP on network
nmap -sn 192.168.1.0/24

# Windows: Use Angry IP Scanner
# Download from: https://angryip.org/
```

### Method 3: Router's Connected Devices
1. Open your router (usually `192.168.1.1` or `192.168.0.1`)
2. Check Connected Devices list
3. Find device name containing "camera" or "hikvision"
4. Note the IP address

### Method 4: Web Interface Discovery
1. Type camera IP in browser: `http://192.168.1.100`
2. Login with default credentials
3. Look for "RTSP URL" or "Stream URL" in settings
4. Copy the URL provided

---

## Using Cameras in Live Monitoring

### Switching Between Cameras

1. Go to **🟢 Live Monitoring** tab
2. At the top, you'll see a dropdown: **Select Camera**
3. Choose from your connected cameras
4. The status indicator shows:
   - 🟢 **Connected** - Camera is ready
   - 🔴 **Disconnected** - Connection failed
   - ⚠️ **Error** - Authentication issue

### Starting Detection

1. Select your camera
2. Set **Abandonment Time Limit** (default: 5 seconds)
3. Check **🟢 START SECURITY FEED**
4. Stream starts and detection begins
5. Any abandoned luggage will be:
   - Highlighted with red box
   - Logged to forensic history
   - Timestamped with evidence image

---

## Camera Management Operations

### View Connected Cameras

**📋 My Cameras** tab shows:
- Camera name with status indicator
- RTSP URL
- Connection status (Connected/Disconnected/Error)
- Date added
- Last used timestamp

### Edit Camera Password

Currently, you can:
1. Delete the old camera
2. Add a new camera with updated password

**Future Enhancement:** In-place password updates

### Delete a Camera

1. Go to **📋 My Cameras**
2. Find the camera
3. Click **❌ Delete**
4. Camera is immediately removed
5. Note: This does NOT delete from REST API - you can re-add anytime

### Monitor Connection Status

Cameras show status:
- 🟢 **Connected** - Last connection successful
- 🔴 **Disconnected** - Cannot reach camera
- ⚠️ **Error** - Authentication or URL problem
- ⏳ **Untested** - Haven't tested yet

---

## Troubleshooting

### Camera Won't Connect

**Problem:** Status shows "Disconnected" or "Error"

**Solutions:**
1. ✅ Verify camera IP is correct
   ```
   ping 192.168.1.100
   ```

2. ✅ Check credentials are correct
   - Try logging into camera's web interface first
   - Use same username/password in app

3. ✅ Verify RTSP port is open
   - Default: 554
   - Some cameras use: 8554, 9554, 554/tcp

4. ✅ Test RTSP URL manually using:
   ```bash
   ffplay rtsp://admin:password@192.168.1.100:554/stream
   vlc rtsp://admin:password@192.168.1.100:554/stream
   ```

### Username/Password Not Accepted

1. Reset camera to factory settings
2. Try default credentials:
   - Hikvision: `admin / 12345`
   - Dahua: `admin / admin`
   - Axis: `root / pass`
   
3. Check camera web interface works first

### Firewall/Network Issues

- Ensure camera and computer are on same network (or camera is port-forwarded)
- Check firewall isn't blocking port 554 (or custom port)
- If on different network, need to port-forward in router

### RTSP URL Rejection

- Platform only accepts `rtsp://` URLs (not `http://`)
- URL must be in format: `rtsp://host:port/path`
- Check there are no spaces in URL
- If using credentials: `rtsp://user:pass@host:port/path`

---

## REST API for Cameras

### Add Camera via API
```bash
curl -X POST "http://localhost:8000/cameras/add" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_name": "Terminal 1",
    "rtsp_url": "rtsp://192.168.1.100:554/stream",
    "username": "admin",
    "password": "password123"
  }'
```

### List Cameras
```bash
curl -X GET "http://localhost:8000/cameras/list" \
  -H "Authorization: Bearer {token}"
```

### Test Camera Connection
```bash
curl -X POST "http://localhost:8000/cameras/1/test" \
  -H "Authorization: Bearer {token}"
```

### Delete Camera
```bash
curl -X DELETE "http://localhost:8000/cameras/1" \
  -H "Authorization: Bearer {token}"
```

---

## Best Practices

### 🔒 Security
- ✅ Change default camera passwords before connecting
- ✅ Use strong passwords (8+ characters)
- ✅ Don't share camera credentials
- ✅ System stores passwords in encrypted database

### 🚀 Performance
- ✅ Use cameras on same network for best performance
- ✅ Limit detection range if monitoring long airport terminals
- ✅ If slow: reduce frame resolution in camera settings
- ✅ Use OpenVINO optimized model for faster processing

### 🎯 Accuracy
- ✅ Position cameras to cover full luggage drop areas
- ✅ Adjust time limit based on your needs (3-15 seconds)
- ✅ Test with known abandoned items first
- ✅ Monitor false positives in forensic history

### 📊 Monitoring
- ✅ Regularly check camera status
- ✅ Review forensic history daily
- ✅ Update camera URLs if IP changes
- ✅ Keep records of abandoned items found

---

## FAQ

**Q: Can I use multiple cameras at the same time?**
A: Yes! Connect unlimited cameras. Switch between them in live monitoring tab.

**Q: What if my camera doesn't support RTSP?**
A: Platform requires RTSP. Check camera manual or contact manufacturer for RTSP support.

**Q: Can I use the same camera as webcam and security feed?**
A: Yes, most cameras support multiple simultaneous RTSP connections.

**Q: How do I know the RTSP path for my camera?**
A: Check the camera's web interface → Settings → Network/Streaming → look for "RTSP" or "Stream URL".

**Q: Is there a limit to camera resolution?**
A: No limit, but higher resolution = slower processing. Most cameras default to 1080p which works well.

**Q: Can I monitor cameras from outside my network?**
A: Yes, with port-forwarding on your router, but REQUIRES strong security (VPN recommended).

**Q: What happens if camera goes offline?**
A: Detection pauses. Status shows "Disconnected". System automatically tries to reconnect.

**Q: Can I use the same camera account on multiple devices?**
A: Yes, but only one connection active at a time. Switch between app instances as needed.

---

## Support

For camera-specific issues:
1. Check camera manual for RTSP documentation
2. Try connecting with VLC or FFmpeg first
3. Test RTSP URL on another device
4. Contact camera manufacturer support

For platform issues:
- Review error messages carefully
- Check connection test results
- Verify credentials match camera settings
- Restart application if persistent issues

---

**Last Updated:** April 2026  
**Version:** 2.0.0  
**Platform:** Multi-User Abandoned Luggage Detection SaaS
