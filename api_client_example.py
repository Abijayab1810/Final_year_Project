"""
API Client Example - How to use the REST API
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "1.0.0"

class LuggageDetectionClient:
    """Client for interacting with Abandoned Luggage Detection API"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def get_all_detections(self, limit=100, offset=0):
        """Get all abandoned luggage detections"""
        params = {"limit": limit, "offset": offset}
        response = self.session.get(f"{self.base_url}/api/detections", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_detections_by_camera(self, camera_id, limit=50):
        """Get detections for a specific camera"""
        params = {"limit": limit}
        url = f"{self.base_url}/api/detections/camera/{camera_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_detections_by_date(self, start_date, end_date):
        """Get detections within a date range"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        response = self.session.get(f"{self.base_url}/api/detections/date-range", params=params)
        response.raise_for_status()
        return response.json()
    
    def log_detection(self, track_id, duration_seconds, camera_id, confidence):
        """Log a new abandoned luggage detection"""
        data = {
            "track_id": track_id,
            "duration_seconds": duration_seconds,
            "camera_id": camera_id,
            "confidence": confidence
        }
        response = self.session.post(f"{self.base_url}/api/detections/log", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self):
        """Get overall system statistics"""
        response = self.session.get(f"{self.base_url}/api/statistics")
        response.raise_for_status()
        return response.json()
    
    def get_daily_statistics(self, days=7):
        """Get daily statistics for past N days"""
        params = {"days": days}
        response = self.session.get(f"{self.base_url}/api/statistics/daily", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_camera_statistics(self):
        """Get per-camera statistics"""
        response = self.session.get(f"{self.base_url}/api/statistics/by-camera")
        response.raise_for_status()
        return response.json()
    
    def export_csv(self):
        """Export all detections to CSV"""
        response = self.session.get(f"{self.base_url}/api/export/csv")
        response.raise_for_status()
        return response.json()
    
    def clear_records(self, confirm=False):
        """Clear all records from database"""
        params = {"confirm": confirm}
        response = self.session.delete(f"{self.base_url}/api/records/clear", params=params)
        response.raise_for_status()
        return response.json()


# Example Usage
if __name__ == "__main__":
    print("🔌 Abandoned Luggage Detection API Client Example\n")
    
    # Initialize client
    client = LuggageDetectionClient()
    
    # 1. Health Check
    print("1️⃣ Health Check")
    health = client.health_check()
    print(f"   Status: {health.get('status')}\n")
    
    # 2. Get Statistics
    print("2️⃣ System Statistics")
    try:
        stats = client.get_statistics()
        print(f"   Total Detections: {stats['total_detections']}")
        print(f"   Average Duration: {stats['average_duration_seconds']:.1f}s")
        print(f"   Max Duration: {stats['max_duration_seconds']}s")
        print(f"   Avg Confidence: {stats['average_confidence']:.1%}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 3. Get All Detections
    print("3️⃣ Recent Detections")
    try:
        detections = client.get_all_detections(limit=5)
        print(f"   Found {len(detections)} detections")
        for det in detections[:3]:
            print(f"   - Track ID {det['track_id']}: {det['duration_seconds']}s at {det['camera_id']}")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 4. Get Camera Statistics
    print("4️⃣ Camera Statistics")
    try:
        cam_stats = client.get_camera_statistics()
        print(f"   Found {len(cam_stats)} cameras")
        for cam in cam_stats[:3]:
            print(f"   - {cam['camera_id']}: {cam['detections']} detections")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 5. Get Daily Statistics
    print("5️⃣ Daily Statistics (Last 7 Days)")
    try:
        daily = client.get_daily_statistics(days=7)
        for day in daily[:3]:
            print(f"   - {day['date']}: {day['count']} detections")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 6. Log New Detection (Example)
    print("6️⃣ Logging New Detection")
    try:
        result = client.log_detection(
            track_id=999,
            duration_seconds=45,
            camera_id="Camera-001",
            confidence=0.92
        )
        print(f"   Result: {result['status']}")
        print(f"   Message: {result['message']}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 7. Get Detections by Date Range
    print("7️⃣ Detections Last 7 Days")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        detections = client.get_detections_by_date(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        print(f"   Found {len(detections)} detections\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 8. Get Specific Camera Detections
    print("8️⃣ Camera-001 Detections")
    try:
        cam_detections = client.get_detections_by_camera("Camera-001", limit=10)
        print(f"   Found {len(cam_detections)} detections")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
    
    print("✅ API Client Example Complete!")
    print(f"\n📚 Full API Documentation at: {BASE_URL}/docs")
