"""
Python Client Example for Authenticated Luggage Detection API
Demonstrates how to use the JWT-authenticated REST API
"""

import requests
import json
from datetime import datetime, timedelta

class LuggageDetectionClient:
    """HTTP client for interacting with the Luggage Detection API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client"""
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.user_id = None
        self.username = None
    
    def _headers(self):
        """Get headers with authorization token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    # ==========================================
    # 🔐 AUTHENTICATION METHODS
    # ==========================================
    
    def register(self, username: str, email: str, password: str, full_name: str = None) -> dict:
        """Register a new user account"""
        url = f"{self.base_url}/auth/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name
        }
        
        response = requests.post(url, json=payload, headers=self._headers())
        return response.json()
    
    def login(self, username: str, password: str) -> dict:
        """Login with username and password"""
        url = f"{self.base_url}/auth/login"
        payload = {
            "username": username,
            "password": password
        }
        
        response = requests.post(url, json=payload, headers=self._headers())
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.user_id = data["user_id"]
            self.username = data["username"]
            return {"status": "success", "message": f"Logged in as {username}"}
        else:
            return {"status": "error", "message": response.json()}
    
    def get_profile(self) -> dict:
        """Get current user profile"""
        url = f"{self.base_url}/auth/profile"
        response = requests.get(url, headers=self._headers())
        return response.json()
    
    # ==========================================
    # 📊 DETECTION METHODS
    # ==========================================
    
    def log_detection(self, track_id: int, duration_seconds: int, camera_id: str = "Camera-001",
                      confidence: float = 0.85, frame_width: int = 640, frame_height: int = 480,
                      bag_x1: int = 100, bag_y1: int = 100, bag_x2: int = 200, bag_y2: int = 300) -> dict:
        """Log a detected abandoned luggage incident"""
        url = f"{self.base_url}/detections/log"
        payload = {
            "track_id": track_id,
            "duration_seconds": duration_seconds,
            "camera_id": camera_id,
            "confidence": confidence,
            "frame_width": frame_width,
            "frame_height": frame_height,
            "bag_x1": bag_x1,
            "bag_y1": bag_y1,
            "bag_x2": bag_x2,
            "bag_y2": bag_y2
        }
        
        response = requests.post(url, json=payload, headers=self._headers())
        return response.json()
    
    def get_all_detections(self, limit: int = 100, offset: int = 0) -> dict:
        """Get all detections for current user"""
        url = f"{self.base_url}/detections/all"
        params = {"limit": limit, "offset": offset}
        response = requests.get(url, params=params, headers=self._headers())
        return response.json()
    
    def get_detection_by_id(self, track_id: int) -> dict:
        """Get specific detection by track ID"""
        url = f"{self.base_url}/detections/{track_id}"
        response = requests.get(url, headers=self._headers())
        return response.json()
    
    def get_detections_by_date_range(self, start_date: str, end_date: str) -> dict:
        """Get detections within a date range (format: YYYY-MM-DD)"""
        url = f"{self.base_url}/detections/by-date-range"
        params = {"start_date": start_date, "end_date": end_date}
        response = requests.get(url, params=params, headers=self._headers())
        return response.json()
    
    # ==========================================
    # 📈 STATISTICS METHODS
    # ==========================================
    
    def get_statistics_summary(self) -> dict:
        """Get statistics summary"""
        url = f"{self.base_url}/statistics/summary"
        response = requests.get(url, headers=self._headers())
        return response.json()
    
    def get_statistics_by_camera(self) -> dict:
        """Get statistics grouped by camera"""
        url = f"{self.base_url}/statistics/by-camera"
        response = requests.get(url, headers=self._headers())
        return response.json()
    
    # ==========================================
    # 📥 EXPORT METHODS
    # ==========================================
    
    def export_csv(self, output_file: str = None) -> bytes:
        """Export all detections as CSV"""
        url = f"{self.base_url}/export/csv"
        response = requests.get(url, headers=self._headers())
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"✅ CSV exported to {output_file}")
        
        return response.content
    
    def export_json(self) -> dict:
        """Export all detections as JSON"""
        url = f"{self.base_url}/export/json"
        response = requests.get(url, headers=self._headers())
        return response.json()
    
    # ==========================================
    # 🖼️ EVIDENCE METHODS
    # ==========================================
    
    def get_evidence_image(self, track_id: int, output_file: str = None) -> bytes:
        """Get evidence image for a detection"""
        url = f"{self.base_url}/evidence/{track_id}"
        response = requests.get(url, headers=self._headers())
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"✅ Evidence image saved to {output_file}")
        
        return response.content
    
    # ==========================================
    # 🏥 HEALTH METHODS
    # ==========================================
    
    def health_check(self) -> dict:
        """Check API health status"""
        url = f"{self.base_url}/health"
        response = requests.get(url, headers=self._headers())
        return response.json()
    
    def health_check_auth(self) -> dict:
        """Check API health with authentication"""
        url = f"{self.base_url}/health/auth"
        response = requests.get(url, headers=self._headers())
        return response.json()


# ==========================================
# 📝 USAGE EXAMPLES
# ==========================================

def example_usage():
    """Demonstrate API usage"""
    
    print("=" * 60)
    print("🛡️  LUGGAGE DETECTION API - CLIENT EXAMPLE")
    print("=" * 60)
    
    # Initialize client
    client = LuggageDetectionClient("http://localhost:8000")
    
    # Check API health
    print("\n1️⃣  Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # Register new user
    print("\n2️⃣  Register New User:")
    reg_response = client.register(
        username="testuser123",
        email="test@example.com",
        password="SecurePass123",
        full_name="Test User"
    )
    print(json.dumps(reg_response, indent=2))
    
    # Login
    print("\n3️⃣  Login:")
    login_response = client.login("testuser123", "SecurePass123")
    print(json.dumps(login_response, indent=2))
    
    if login_response.get("status") == "error":
        print("❌ Login failed. Exiting example.")
        return
    
    # Get user profile
    print("\n4️⃣  Get User Profile:")
    profile = client.get_profile()
    print(json.dumps(profile, indent=2))
    
    # Check authenticated health
    print("\n5️⃣  Authenticated Health Check:")
    auth_health = client.health_check_auth()
    print(json.dumps(auth_health, indent=2))
    
    # Log a detection
    print("\n6️⃣  Log a Detection:")
    detection_response = client.log_detection(
        track_id=1,
        duration_seconds=25,
        camera_id="Camera-001",
        confidence=0.87
    )
    print(json.dumps(detection_response, indent=2))
    
    # Log more detections
    print("\n7️⃣  Log More Detections:")
    for i in range(2, 5):
        detection = client.log_detection(
            track_id=i,
            duration_seconds=10 + (i * 5),
            camera_id=f"Camera-{i % 3}",
            confidence=0.80 + (i * 0.02)
        )
        print(f"   Track ID {i}: {detection.get('message', 'Logged')}")
    
    # Get all detections
    print("\n8️⃣  Get All Detections:")
    detections = client.get_all_detections(limit=5)
    print(json.dumps(detections, indent=2)[:500] + "...")
    
    # Get statistics
    print("\n9️⃣  Get Statistics Summary:")
    stats = client.get_statistics_summary()
    print(json.dumps(stats, indent=2))
    
    # Get camera statistics
    print("\n🔟 Get Statistics by Camera:")
    camera_stats = client.get_statistics_by_camera()
    print(json.dumps(camera_stats, indent=2))
    
    # Export JSON
    print("\n1️⃣1️⃣  Export as JSON:")
    json_export = client.export_json()
    print(f"   Total detections: {json_export.get('total_detections')}")
    print(f"   Export time: {json_export.get('export_timestamp')}")
    
    # Get detections by date range
    print("\n1️⃣2️⃣  Get Detections by Date Range:")
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    date_detections = client.get_detections_by_date_range(
        str(today),
        str(tomorrow)
    )
    print(json.dumps(date_detections, indent=2)[:300] + "...")
    
    print("\n" + "=" * 60)
    print("✅ EXAMPLE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    example_usage()
