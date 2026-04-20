# 🐳 Docker & REST API Deployment Guide

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- 4GB+ available storage
- GPU optional (CPU will work fine)

### Build & Run with Docker Compose

```bash
# Clone/navigate to project
cd d:\projects\Final_year_project

# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f streamlit
docker-compose logs -f nginx
```

### Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **FastAPI** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **API ReDoc** | http://localhost:8000/redoc | Alternative Docs |
| **Streamlit** | http://localhost:8501 | Web Dashboard |
| **Nginx** | http://localhost:80 | Production Proxy |

---

## 🔌 REST API Endpoints

### Base URL
```
http://localhost:8000
```

### Health Check
```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2026-04-08T10:30:00",
  "version": "1.0.0"
}
```

### Get All Detections
```http
GET /api/detections?limit=100&offset=0

Response:
[
  {
    "id": 1,
    "track_id": 123,
    "timestamp": "2026-04-08 10:30:00",
    "duration_seconds": 45,
    "camera_id": "Camera-001",
    "confidence_score": 0.95,
    "frame_width": 1920,
    "frame_height": 1080,
    "bag_x1": 100,
    "bag_y1": 200,
    "bag_x2": 300,
    "bag_y2": 400,
    "image_filepath": "/app/evidence/...",
    "actions_taken": "Logged"
  }
]
```

### Get Detections by Camera
```http
GET /api/detections/camera/Camera-001?limit=50

Response: List of detections for Camera-001
```

### Get Detections by Date Range
```http
GET /api/detections/date-range?start_date=2026-04-01&end_date=2026-04-08

Response: List of detections within date range
```

### Log Manual Detection
```http
POST /api/detections/log

Request Body:
{
  "track_id": 456,
  "duration_seconds": 35,
  "camera_id": "Camera-002",
  "confidence": 0.88
}

Response:
{
  "status": "success",
  "message": "Detection logged"
}
```

### Get Statistics
```http
GET /api/statistics

Response:
{
  "total_detections": 156,
  "average_duration_seconds": 32.5,
  "max_duration_seconds": 120,
  "average_confidence": 0.92
}
```

### Get Daily Statistics
```http
GET /api/statistics/daily?days=7

Response:
[
  {
    "date": "2026-04-08",
    "count": 12,
    "avg_duration": 35.2,
    "max_duration": 95
  }
]
```

### Get Camera Statistics
```http
GET /api/statistics/by-camera

Response:
[
  {
    "camera_id": "Camera-001",
    "detections": 85,
    "avg_duration": 33.4,
    "max_duration": 120,
    "avg_confidence": 0.94
  }
]
```

### Export Data to CSV
```http
GET /api/export/csv

Response:
{
  "status": "success",
  "filename": "forensic_export_20260408_103000.csv",
  "message": "Export completed"
}
```

### Clear All Records
```http
DELETE /api/records/clear?confirm=true

Response:
{
  "status": "success",
  "message": "All records cleared"
}
```

---

## 🐍 Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get all detections
def get_detections():
    response = requests.get(f"{BASE_URL}/api/detections")
    return response.json()

# Get statistics
def get_stats():
    response = requests.get(f"{BASE_URL}/api/statistics")
    return response.json()

# Log a detection
def log_detection(track_id, duration_seconds, camera_id, confidence):
    data = {
        "track_id": track_id,
        "duration_seconds": duration_seconds,
        "camera_id": camera_id,
        "confidence": confidence
    }
    response = requests.post(f"{BASE_URL}/api/detections/log", json=data)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Get stats
    stats = get_stats()
    print(f"Total detections: {stats['total_detections']}")
    
    # Log a new detection
    result = log_detection(789, 50, "Camera-001", 0.91)
    print(f"Log result: {result}")
    
    # Get all detections
    detections = get_detections()
    print(f"Found {len(detections)} detections")
```

---

## 🚀 Docker Commands

### Build Individual Services
```bash
# Build API only
docker build -f Dockerfile -t luggage-api:latest .

# Run API container
docker run -p 8000:8000 \
  -v $(pwd)/best_int8_openvino_model:/app/best_int8_openvino_model \
  -v $(pwd)/yolov8n.pt:/app/yolov8n.pt \
  -v $(pwd)/evidence:/app/evidence \
  luggage-api:latest
```

### Docker Compose Commands
```bash
# Start services in background
docker-compose up -d

# Stop services
docker-compose down

# View real-time logs
docker-compose logs -f

# Restart services
docker-compose restart

# Build containers (rebuild if changes made)
docker-compose build

# Run commands in container
docker-compose exec api bash
docker-compose exec streamlit bash
```

### Push to Registry
```bash
# Build with version tag
docker build -t myregistry.azurecr.io/luggage-api:v1.0.0 .

# Push to registry
docker push myregistry.azurecr.io/luggage-api:v1.0.0

# Pull and run
docker pull myregistry.azurecr.io/luggage-api:v1.0.0
docker run -p 8000:8000 myregistry.azurecr.io/luggage-api:v1.0.0
```

---

## 📊 Environment Variables

Create `.env` file for configuration:

```env
# API Settings
ENVIRONMENT=production
LOG_LEVEL=info
API_WORKERS=4

# Camera Settings
CAMERA_COUNT=1
CAMERA_TIMEOUT=30

# Model Settings
MODEL_PATH=/app/best_int8_openvino_model
PERSON_MODEL_PATH=/app/yolov8n.pt

# Database
DATABASE_URL=sqlite:///./forensic_detections.db

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

Load in app:
```python
from dotenv import load_dotenv
import os

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "info")
```

---

## 🔒 Production Deployment

### Using Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: luggage-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: luggage-api
  template:
    metadata:
      labels:
        app: luggage-api
    spec:
      containers:
      - name: api
        image: myregistry.azurecr.io/luggage-api:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

### Using AWS EC2
```bash
# SSH into EC2 instance
ssh -i key.pem ec2-user@your-instance

# Install Docker & Docker Compose
sudo yum update -y
sudo yum install docker -y
sudo usermod -a -G docker ec2-user

# Clone repo and start services
git clone your-repo
cd your-repo
docker-compose up -d
```

### Using Azure Container Instances
```bash
# Create container group
az container create \
  --resource-group myResourceGroup \
  --name luggage-api \
  --image myregistry.azurecr.io/luggage-api:v1.0.0 \
  --ports 8000 \
  --cpu 1 \
  --memory 1
```

---

## 🛠️ Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs api

# Rebuild container
docker-compose build --no-cache api
docker-compose up api
```

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database locked
```bash
# Remove database and restart
rm forensic_detections.db
docker-compose restart
```

### GPU support needed
```yaml
# In docker-compose.yml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

---

## 💡 Notes

- Models are mounted as read-only (`ro`) for safety
- Evidence folder persists detections across container restarts
- Database is shared between API and Streamlit containers
- In production, use PostgreSQL instead of SQLite
- Enable HTTPS with proper certificates
- Monitor container health with `docker-compose ps`

---

## 📞 Support

For API documentation: http://localhost:8000/docs
For issues: Check container logs with `docker-compose logs`
