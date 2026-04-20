import cv2
import sys

def find_available_cameras():
    """Find all available camera devices."""
    available_cameras = []
    
    print("🔍 Scanning for available cameras... (this may take a moment)")
    
    # Try indices 0-10
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera {i}: FOUND (resolution: {frame.shape[1]}x{frame.shape[0]})")
                available_cameras.append(i)
            else:
                print(f"⚠️ Camera {i}: Device exists but failed to read frame")
            cap.release()
        else:
            print(f"❌ Camera {i}: Not available")
    
    if available_cameras:
        print(f"\n✅ Available cameras: {available_cameras}")
        return available_cameras
    else:
        print("\n❌ No cameras found!")
        print("   - Check if your camera is connected")
        print("   - Try unplugging and plugging back in")
        print("   - Check Device Manager for camera devices")
        return []

def try_directshow_backend():
    """Test DirectShow backend (Windows specific)."""
    print("\n🔌 Testing DirectShow backend (Windows)...")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ DirectShow backend works!")
                cap.release()
                return True
            cap.release()
    except Exception as e:
        print(f"❌ DirectShow error: {e}")
    
    print("❌ DirectShow backend failed")
    return False

if __name__ == "__main__":
    cameras = find_available_cameras()
    try_directshow_backend()
