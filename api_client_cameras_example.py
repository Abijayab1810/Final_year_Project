"""
Python Client Example with Camera Management
Demonstrates how to use camera management API endpoints
"""

import requests
import json
from api_client_auth_example import LuggageDetectionClient

class LuggageDetectionClientWithCameras(LuggageDetectionClient):
    """Extended client with camera management"""
    
    # ==========================================
    # 📹 CAMERA METHODS
    # ==========================================
    
    def add_camera(self, camera_name: str, rtsp_url: str, username: str = None, 
                   password: str = None, camera_type: str = "RTSP", port: int = 554) -> dict:
        """Add a new CCTV camera"""
        url = f"{self.base_url}/cameras/add"
        payload = {
            "camera_name": camera_name,
            "rtsp_url": rtsp_url,
            "username": username,
            "password": password,
            "camera_type": camera_type,
            "port": port
        }
        
        response = requests.post(url, json=payload, headers=self._headers())
        return response.json()
    
    def list_cameras(self, active_only: bool = False) -> dict:
        """Get all cameras for current user"""
        url = f"{self.base_url}/cameras/list"
        params = {"active_only": active_only}
        response = requests.get(url, params=params, headers=self._headers())
        return response.json()
    
    def get_camera(self, camera_id: int) -> dict:
        """Get specific camera details"""
        url = f"{self.base_url}/cameras/{camera_id}"
        response = requests.get(url, headers=self._headers())
        return response.json()
    
    def update_camera(self, camera_id: int, **kwargs) -> dict:
        """Update camera details
        
        Supported fields: camera_name, rtsp_url, username, password, is_active
        """
        url = f"{self.base_url}/cameras/{camera_id}"
        payload = {k: v for k, v in kwargs.items() if v is not None}
        response = requests.put(url, json=payload, headers=self._headers())
        return response.json()
    
    def delete_camera(self, camera_id: int) -> dict:
        """Delete a camera"""
        url = f"{self.base_url}/cameras/{camera_id}"
        response = requests.delete(url, headers=self._headers())
        return response.json()
    
    def test_camera_connection(self, camera_id: int) -> dict:
        """Test connection to a camera"""
        url = f"{self.base_url}/cameras/{camera_id}/test"
        response = requests.post(url, headers=self._headers())
        return response.json()


# ==========================================
# 📝 USAGE EXAMPLES
# ==========================================

def example_camera_management():
    """Demonstrate camera management API"""
    
    print("=" * 70)
    print("📹 CAMERA MANAGEMENT - CLIENT EXAMPLE")
    print("=" * 70)
    
    # Initialize client
    client = LuggageDetectionClientWithCameras("http://localhost:8000")
    
    # Login
    print("\n1️⃣  Login:")
    login_response = client.login("testuser123", "SecurePass123")
    print(f"   Status: {login_response.get('status')}")
    
    if login_response.get("status") == "error":
        print("❌ Login failed. Exiting example.")
        return
    
    # Add Camera 1: Hikvision
    print("\n2️⃣  Add Camera 1 (Hikvision):")
    camera1 = client.add_camera(
        camera_name="Terminal 1 Front Gate",
        rtsp_url="rtsp://192.168.1.100:554/Streaming/Channels/101",
        username="admin",
        password="12345",
        camera_type="RTSP"
    )
    print(json.dumps(camera1, indent=2))
    camera1_id = camera1.get("camera_id")
    
    # Add Camera 2: Dahua (no credentials)
    print("\n3️⃣  Add Camera 2 (Dahua - No Credentials):")
    camera2 = client.add_camera(
        camera_name="Terminal 2 Baggage Claim",
        rtsp_url="rtsp://192.168.1.101:554/stream/ch0",
        camera_type="RTSP"
    )
    print(json.dumps(camera2, indent=2))
    camera2_id = camera2.get("camera_id")
    
    # Add Camera 3: Generic IP Camera
    print("\n4️⃣  Add Camera 3 (Generic IP Camera):")
    camera3 = client.add_camera(
        camera_name="Entrance Hallway",
        rtsp_url="rtsp://192.168.1.102:554/stream",
        username="user",
        password="pass123",
        camera_type="RTSP",
        port=554
    )
    print(json.dumps(camera3, indent=2))
    camera3_id = camera3.get("camera_id")
    
    # List all cameras
    print("\n5️⃣  List All Cameras:")
    cameras_list = client.list_cameras()
    print(f"   Total cameras: {cameras_list.get('total')}")
    for cam in cameras_list.get('cameras', []):
        print(f"   - {cam['camera_name']}: {cam['connection_status']}")
    
    # Get specific camera
    if camera1_id:
        print(f"\n6️⃣  Get Camera Details (Camera 1):")
        camera_details = client.get_camera(camera1_id)
        print(json.dumps(camera_details, indent=2)[:300] + "...")
    
    # Test camera connections
    print("\n7️⃣  Test Camera Connections:")
    
    if camera1_id:
        print(f"   Testing Camera 1...")
        result1 = client.test_camera_connection(camera1_id)
        print(f"   → {result1.get('message')}")
    
    if camera2_id:
        print(f"   Testing Camera 2...")
        result2 = client.test_camera_connection(camera2_id)
        print(f"   → {result2.get('message')}")
    
    # Update camera
    if camera3_id:
        print(f"\n8️⃣  Update Camera 3 (Update Password):")
        update_result = client.update_camera(
            camera3_id,
            password="newpassword456"
        )
        print(json.dumps(update_result, indent=2))
    
    # Delete camera
    if camera3_id:
        print(f"\n9️⃣  Delete Camera 3:")
        delete_result = client.delete_camera(camera3_id)
        print(json.dumps(delete_result, indent=2))
    
    # List cameras again to verify deletion
    print("\n🔟 List Cameras After Deletion:")
    cameras_list_after = client.list_cameras()
    print(f"   Total cameras: {cameras_list_after.get('total')}")
    for cam in cameras_list_after.get('cameras', []):
        print(f"   - {cam['camera_name']}")
    
    print("\n" + "=" * 70)
    print("✅ CAMERA MANAGEMENT EXAMPLE COMPLETED")
    print("=" * 70)


def example_detection_with_cameras():
    """Demonstrate detection workflow with multiple cameras"""
    
    print("\n" + "=" * 70)
    print("📊 DETECTION WITH MULTIPLE CAMERAS - EXAMPLE")
    print("=" * 70)
    
    client = LuggageDetectionClientWithCameras("http://localhost:8000")
    
    # Login
    client.login("testuser123", "SecurePass123")
    
    # Get all cameras
    print("\n📹 Retrieving connected cameras...")
    cameras = client.list_cameras()
    
    if cameras['total'] == 0:
        print("❌ No cameras connected. Add cameras first.")
        return
    
    print(f"✅ Found {cameras['total']} camera(s):")
    
    # For each camera, show monitoring stats
    for i, camera in enumerate(cameras['cameras'], 1):
        print(f"\n  Camera {i}: {camera['camera_name']}")
        print(f"  └─ Status: {camera['connection_status']}")
        print(f"  └─ URL: {camera['rtsp_url']}")
        
        # Get detections (would need to log them first)
        stats = client.get_statistics_summary()
        print(f"  └─ Total Detections: {stats.get('total_detections')}")
        print(f"  └─ Avg Duration: {stats.get('avg_duration'):.1f}s")
    
    print("\n" + "=" * 70)
    print("✅ MULTI-CAMERA WORKFLOW COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    # Run camera management example
    example_camera_management()
    
    # Uncomment to run multi-camera detection example
    # example_detection_with_cameras()
