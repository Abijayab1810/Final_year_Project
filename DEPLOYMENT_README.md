# 🛡️ Abandoned Luggage Detection System - Complete Deployment Guide

## 📋 Overview

This is a production-ready system for detecting abandoned luggage in security environments using:
- **FastAPI** REST API for external integrations
- **Streamlit** Web Dashboard for operators
- **YOLOv8** ML models (Bag detection + Person detection)
- **OpenVINO** optimization for edge deployment
- **Docker** containerization
- **Nginx** reverse proxy (production)

---

## 🚀 Quick Start (Docker)

### Option 1: Windows (Using Batch Script)
```bash
# Double-click or run in command prompt
quickstart.bat
```

### Option 2: Linux/macOS (Using Bash Script)
```bash
chmod +x quickstart.sh
./quickstart.sh
```

### Option 3: Manual Docker Compose
```bash
# Build and start all services
docker-compose up -d

# Access services
# - API: http://localhost:8000
# - Dashboard: http://localhost:8501
# - Docs: http://localhost:8000/docs
```

---

## 📁 Project Structure

```
Final_year_project/
├── app.py                      # Streamlit Web Dashboard
├── api.py                      # FastAPI REST API
├── forensic_db.py              # Database module
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Multi-container orchestration
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .dockerignore                # Files to exclude from Docker
│
├── best_int8_openvino_model/   # Bag detection model
├── yolov8n.pt                  # Person detection model
├── evidence/                   # Detected bag evidence images
│
├── DOCKER_API_GUIDE.md         # Complete API documentation
├── api_client_example.py       # Python API client example
├── quickstart.bat              # Windows quick start script
├── quickstart.sh               # Linux/Mac quick start script
└── README.md                   # This file
```

---

## 🔧 Installation & Setup

### Prerequisites
- Docker & Docker Compose installed
- 4GB+ available storage for models
- GPU (optional, CPU works fine)

### Step 1: Clone/Navigate to Project
```bash
cd Final_year_project
```

### Step 2: Create Environment File
```bash
# Copy example to create .env
cp .env.example .env

# Edit as needed (optional)
nano .env
```

### Step 3: Build Docker Images
```bash
docker-compose build
```

### Step 4: Start Services
```bash
docker-compose up -d

# Verify all services are running
docker-compose ps
```

---

## 🌐 Accessing Services

| Service | URL | Purpose | Type |
|---------|-----|---------|------|
| **FastAPI** | http://localhost:8000 | REST API Root | HTTP |
| **Swagger Docs** | http://localhost:8000/docs | Interactive API Docs | HTML |
| **ReDoc** | http://localhost:8000/redoc | Alternative API Docs | HTML |
| **Streamlit Dashboard** | http://localhost:8501 | Web UI for Operators | Web App |
| **Nginx Proxy** | http://localhost:80 | Production Proxy | HTTP/HTTPS |

---

## 🔌 REST API Quick Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### Get All Detections
```bash
curl http://localhost:8000/api/detections?limit=10
```

### Get Statistics
```bash
curl http://localhost:8000/api/statistics
```

### Log Detection
```bash
curl -X POST http://localhost:8000/api/detections/log \
  -H "Content-Type: application/json" \
  -d '{
    "track_id": 123,
    "duration_seconds": 45,
    "camera_id": "Camera-001",
    "confidence": 0.95
  }'
```

### Get All API Endpoints
```bash
curl http://localhost:8000/docs
```

---

## 🐍 Python Client Example

```python
from api_client_example import LuggageDetectionClient

# Initialize client
client = LuggageDetectionClient()

# Get statistics
stats = client.get_statistics()
print(f"Total detections: {stats['total_detections']}")

# Get detections for specific camera
detections = client.get_detections_by_camera("Camera-001")
print(f"Found {len(detections)} detections")

# Log new detection
result = client.log_detection(456, 50, "Camera-002", 0.92)
print(f"Result: {result['status']}")
```

### Run Example
```bash
# Inside Docker container
docker-compose exec api python api_client_example.py

# Or locally (requires running API)
python api_client_example.py
```

---

## 🐳 Docker Management

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f streamlit
```

### Stop Services
```bash
# Stop but keep containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Rebuild Services
```bash
# Rebuild if code changed
docker-compose build --no-cache

# Start with rebuilt images
docker-compose up -d
```

### Access Container Shell
```bash
# Enter API container
docker-compose exec api bash

# Enter Streamlit container
docker-compose exec streamlit bash

# Run Python command
docker-compose exec api python api_client_example.py
```

---

## 📊 Dashboard Features

### 🟢 Live Monitoring
- Real-time camera feed
- Dynamic bag detection
- Person association logic
- Live FPS and status metrics

### 📊 Forensic History
- All detected abandoned luggage incidents
- Evidence images with metadata
- CSV export functionality
- Expandable incident details

### 📈 Statistics
- Total detections overview
- Average abandonment duration
- Maximum duration tracking
- Average detection confidence
- Daily statistics
- Camera-wise breakdown

---

## 🔐 Security Considerations

### For Development
- SQLite database (current)
- No authentication required
- CORS enabled for all origins

### For Production
- Use PostgreSQL instead of SQLite
- Enable JWT authentication
- Restrict CORS to specific domains
- Use HTTPS with SSL certificates
- Run behind Nginx proxy
- Use environment variables for secrets
- Regular database backups

---

## 🚨 Common Issues & Solutions

### Issue: Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Issue: Container Won't Start
```bash
# Check logs
docker-compose logs api

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Database Locked
```bash
# Remove database and restart
rm forensic_detections.db
docker-compose restart
```

### Issue: GPU Not Recognized
```bash
# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.0-runtime nvidia-smi

# Enable in docker-compose.yml
# See DOCKER_API_GUIDE.md for details
```

---

## 📚 Additional Documentation

- **[DOCKER_API_GUIDE.md](DOCKER_API_GUIDE.md)** - Complete Docker & API documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Cloud deployment guides
- **[PERFORMANCE_METRICS.md](PERFORMANCE_METRICS.md)** - Performance benchmarks

---

## 🔗 API Endpoints Reference

### Detections
- `GET /api/detections` - Get all detections
- `GET /api/detections/camera/{camera_id}` - Get by camera
- `GET /api/detections/date-range` - Get by date range
- `POST /api/detections/log` - Log manual detection

### Statistics
- `GET /api/statistics` - Overall statistics
- `GET /api/statistics/daily` - Daily breakdown
- `GET /api/statistics/by-camera` - Per-camera stats

### Export
- `GET /api/export/csv` - Export to CSV

### Management
- `DELETE /api/records/clear` - Clear all records
- `GET /health` - Health check

See [DOCKER_API_GUIDE.md](DOCKER_API_GUIDE.md) for full documentation.

---

## 🚀 Deployment Options

### Local Development
```bash
docker-compose up -d
```

### AWS EC2
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed steps

### Kubernetes
See [DOCKER_API_GUIDE.md](DOCKER_API_GUIDE.md) for k8s YAML examples

### Azure Container Instances
See [DOCKER_API_GUIDE.md](DOCKER_API_GUIDE.md) for Azure CLI commands

---

## 📞 Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Status**: `docker-compose ps`
- **Logs**: `docker-compose logs -f`
- **Health**: http://localhost:8000/health

---

## 📝 Requirements

### Hardware (Minimum)
- CPU: 2+ cores
- RAM: 4GB+
- Storage: 10GB+
- Optional: GPU (for faster inference)

### Software
- Docker 20.10+
- Docker Compose 1.29+
- Python 3.11+ (for local development)

### Network
- Ports: 8000, 8501, 80, 443 (configurable)
- Internet access for model downloads

---

## 📜 License & Credits

This system was developed as a final year project for abandoned luggage detection using state-of-the-art computer vision and edge AI technologies.

---

## 🤝 Next Steps

1. ✅ Deploy system with Docker
2. ✅ Access REST API at `/docs`
3. ✅ Test with `api_client_example.py`
4. ⏭️ Integrate with security infrastructure
5. ⏭️ Add SMS/Email notifications
6. ⏭️ Deploy to cloud (AWS/Azure)
7. ⏭️ Set up monitoring & logging

---

**Last Updated**: April 8, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
