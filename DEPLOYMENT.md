# 🚀 FastAPI + Docker Deployment Guide

## Production Setup

### Architecture
```
┌─────────────────────────────────────────┐
│          Client (Web/Mobile)            │
└──────────────────┬──────────────────────┘
                   │ HTTPS
                   ▼
        ┌──────────────────────┐
        │   Nginx Reverse Proxy│
        │   (Port 80/443)      │
        └──────────┬───────────┘
                   │ : Load balance
                   ▼
        ┌──────────────────────┐
        │   FastAPI Backend    │
        │   (Port 8000)        │
        │   - YOLOv8 INT8      │
        │   - Async detection  │
        │   - WebSocket stream │
        └──────────────────────┘
```

---

## Quick Start

### 1. Local Development (No Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Visit API docs
http://localhost:8000/docs
```

### 2. Docker Single Container
```bash
# Build image
docker build -t luggage-detection:latest .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/best_int8_openvino_model:/app/best_int8_openvino_model:ro \
  -v $(pwd)/yolov8n.pt:/app/yolov8n.pt:ro \
  luggage-detection:latest

# Access
http://localhost:8000/docs
```

### 3. Docker Compose (Production) ⭐ RECOMMENDED
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## API Endpoints

### 🏥 Health Check
```bash
curl http://localhost:8000/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-07T10:30:00",
  "models": {
    "bag_detection": "YOLOv8 INT8",
    "person_detection": "YOLOv8n"
  }
}
```

### 📋 Model Information
```bash
curl http://localhost:8000/models/info
```

### 🎯 Single Image Detection
```bash
curl -X POST "http://localhost:8000/detect/image" \
  -F "file=@image.jpg" \
  -F "confidence=0.35" \
  -F "time_limit=5"
```
**Response:**
```json
{
  "success": true,
  "frame": "base64_encoded_image",
  "result": {
    "detections": [
      {
        "id": 1,
        "box": [100, 150, 250, 350],
        "center": [175, 250],
        "stationary_time": 3.2,
        "status": "monitoring"
      }
    ],
    "alerts": [],
    "total_detections": 5,
    "frame_count": 23
  }
}
```

### 📦 Batch Detection
```bash
curl -X POST "http://localhost:8000/detect/batch" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg" \
  -F "confidence=0.35" \
  -F "time_limit=5"
```

### 🔌 WebSocket Real-Time Streaming
```javascript
// JavaScript client
const ws = new WebSocket("ws://localhost:8000/ws/detection/session_123");

ws.onopen = () => {
  // Send frames
  ws.send(JSON.stringify({
    frame: base64_frame,
    confidence: 0.35,
    time_limit: 5
  }));
};

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log("Detection result:", result);
};
```

### 📊 Session Statistics
```bash
curl http://localhost:8000/stats/session/session_123
```

---

## Deployment Options

### Option 1: Local Machine
```bash
docker-compose up -d
# Accessible at: http://localhost
```

### Option 2: AWS EC2
```bash
# 1. SSH into instance
ssh -i key.pem ec2-user@instance_ip

# 2. Install Docker
sudo yum install docker -y
sudo service docker start

# 3. Clone repo & run
git clone https://github.com/Abijayab1810/final_year_project.git
cd final_year_project
docker-compose up -d

# 4. Configure security group
# Open port 80/443/8000
```

### Option 3: Docker Hub / Registry
```bash
# Build and push image
docker build -t abijayab1810/luggage-detection:latest .
docker push abijayab1810/luggage-detection:latest

# Pull and run anywhere
docker pull abijayab1810/luggage-detection:latest
docker run -p 8000:8000 abijayab1810/luggage-detection:latest
```

### Option 4: Kubernetes (Enterprise)
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: luggage-detection
spec:
  replicas: 3
  selector:
    matchLabels:
      app: luggage-detection
  template:
    metadata:
      labels:
        app: luggage-detection
    spec:
      containers:
      - name: api
        image: abijayab1810/luggage-detection:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 40
          periodSeconds: 10
```

---

## Client Implementation Examples

### Python Client
```python
import requests
import json

# Single image detection
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/detect/image',
        files=files,
        data={'confidence': 0.35, 'time_limit': 5}
    )
    
result = response.json()
print(f"Detections: {len(result['result']['detections'])}")
print(f"Alerts: {result['result']['alerts']}")
```

### JavaScript/React Client
```javascript
async function detectImage(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('confidence', 0.35);
  formData.append('time_limit', 5);
  
  const response = await fetch('http://localhost:8000/detect/image', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  return result;
}

// WebSocket streaming
function startRealTimeDetection(sessionId) {
  const ws = new WebSocket(`ws://localhost:8000/ws/detection/${sessionId}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data.result);
  };
  
  return ws;
}
```

### cURL Examples
```bash
# Get health status
curl http://localhost:8000/health | jq

# Detect single image
curl -X POST http://localhost:8000/detect/image \
  -F file=@image.jpg | jq .result.detections

# Get API documentation
curl http://localhost:8000/docs
```

---

## Performance Tuning

### Uvicorn Workers
```bash
# Production - multiple workers
python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

### Nginx Worker Connections
```nginx
events {
    worker_connections 2048;  # Increase for high traffic
}
```

### Docker Resource Limits
```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## Monitoring & Logging

### View Logs
```bash
# Docker logs
docker-compose logs -f api

# Follow specific service
docker-compose logs -f --tail=100 api

# Save to file
docker-compose logs api > logs.txt
```

### Health Monitoring
```bash
# Continuous monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq'

# With JSON parsing
while true; do
  curl -s http://localhost:8000/health | jq '.status'
  sleep 5
done
```

---

## Security Best Practices

### 1. Enable HTTPS
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Mount in docker-compose
volumes:
  - ./ssl:/etc/nginx/ssl:ro
```

### 2. API Authentication
```python
# Add to main.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/detect/image")
async def detect_image(
    file: UploadFile,
    credentials: HTTPAuthCredentials = Depends(security)
):
    # Validate token
    if credentials.credentials != "your_secret_token":
        raise HTTPException(status_code=401)
    # ... detection logic
```

### 3. Rate Limiting
```bash
pip install slowapi

# In main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/detect/image")
@limiter.limit("10/minute")
async def detect_image(...):
    ...
```

### 4. CORS Configuration
```python
# Already in main.py
CORSMiddleware(
    allow_origins=["https://yourdomain.com"],  # Restrict
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### "Models not found" Error
```bash
# Ensure model volumes are mounted
docker-compose ps
docker-compose logs api | grep "model"

# Verify model files exist
ls -la best_int8_openvino_model/
ls -la yolov8n.pt
```

### High Memory Usage
```bash
# Limit container memory
docker-compose down
docker-compose up -d --memory="1g"
```

### Slow Detection
```bash
# Check CPU usage
docker stats luggage_detection_api

# Increase workers/threads in docker-compose
```

---

## Production Checklist

- [ ] SSL/HTTPS enabled
- [ ] Rate limiting configured
- [ ] Authentication token set
- [ ] CORS restricted to specific domains
- [ ] Monitoring/logging set up
- [ ] Health checks configured
- [ ] Resource limits defined
- [ ] Backup strategy in place
- [ ] Auto-restart enabled
- [ ] Documentation updated

---

**Last Updated:** April 7, 2026  
**Version:** 1.0.0
