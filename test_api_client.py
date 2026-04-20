"""
Test client for FastAPI backend
Demonstrates API usage for detection
"""

import requests
import base64
import json
import asyncio
import websockets
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

class LuggageDetectionClient:
    """Client for luggage detection API"""
    
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
    
    def health_check(self):
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_models_info(self):
        """Get model information"""
        try:
            response = requests.get(f"{self.base_url}/models/info")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def detect_single_image(self, image_path, confidence=0.35, time_limit=5):
        """Detect luggage in single image"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {'confidence': confidence, 'time_limit': time_limit}
                response = requests.post(
                    f"{self.base_url}/detect/image",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def detect_batch(self, image_paths, confidence=0.35, time_limit=5):
        """Batch detection for multiple images"""
        try:
            files = []
            for path in image_paths:
                with open(path, 'rb') as f:
                    files.append(('files', f))
            
            data = {'confidence': confidence, 'time_limit': time_limit}
            response = requests.post(
                f"{self.base_url}/detect/batch",
                files=files,
                data=data,
                timeout=60
            )
            
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def get_session_stats(self, session_id):
        """Get statistics for a session"""
        try:
            response = requests.get(f"{self.base_url}/stats/session/{session_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# ==========================================
# EXAMPLE USAGE
# ==========================================

def main():
    client = LuggageDetectionClient()
    
    print("=" * 60)
    print("🛡️  Luggage Detection API Client")
    print("=" * 60)
    
    # 1. Health check
    print("\n1️⃣  Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # 2. Model info
    print("\n2️⃣  Model Information:")
    models = client.get_models_info()
    print(json.dumps(models, indent=2))
    
    # 3. Single image detection
    print("\n3️⃣  Single Image Detection:")
    test_images = list(Path("bags_only_dataset/bags_only_dataset/images/test").glob("*.jpg"))[:1]
    
    if test_images:
        result = client.detect_single_image(
            str(test_images[0]),
            confidence=0.35,
            time_limit=5
        )
        
        if result.get('success'):
            print(f"✅ Detection successful!")
            print(f"   - Total detections: {result['result']['total_detections']}")
            print(f"   - Frame count: {result['result']['frame_count']}")
            print(f"   - Detections this frame: {len(result['result']['detections'])}")
            print(f"   - Alerts: {len(result['result']['alerts'])}")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print("⚠️  No test images found in dataset")
    
    # 4. Batch detection
    print("\n4️⃣  Batch Detection:")
    batch_images = list(Path("bags_only_dataset/bags_only_dataset/images/test").glob("*.jpg"))[:3]
    
    if batch_images:
        result = client.detect_batch(
            [str(img) for img in batch_images],
            confidence=0.35,
            time_limit=5
        )
        
        if result.get('success'):
            print(f"✅ Batch detection successful!")
            print(f"   - Files processed: {result['total_files']}")
            print(f"   - Total detections: {result['session_stats']['total_detections']}")
            print(f"   - Total alerts: {result['session_stats']['total_alerts']}")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print("⚠️  Not enough test images")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    main()
