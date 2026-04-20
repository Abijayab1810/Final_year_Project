# 🏗️ Architecture & System Design

## Project Structure
```
final_year_project/
├── 🚀 PRODUCTION BACKEND
│   ├── main.py                      # FastAPI application
│   ├── Dockerfile                   # Docker image definition
│   ├── docker-compose.yml           # Container orchestration
│   ├── nginx.conf                   # Reverse proxy config
│   └── test_api_client.py           # API test client
│
├── 💻 WEB INTERFACE
│   └── app.py                       # Streamlit dashboard
│
├── 📚 DOCUMENTATION
│   ├── README.md                    # Project overview
│   ├── ARCHITECTURE.md              # This file
│   ├── DEPLOYMENT.md                # Production deployment
│   ├── PERFORMANCE_METRICS.md       # Detailed metrics
│   └── OPTIMIZATION_ROADMAP.md      # Future optimization
│
├── 🤖 AI MODELS
│   ├── best_int8_openvino_model/    # Deployed INT8 model
│   ├── bag_openvino_model/          # FP32 baseline
│   ├── bag_openvino_model_half/     # FP16 variant
│   ├── bag.pt                       # Original PyTorch
│   ├── yolov8n.pt                   # Person detection
│   └── yolov8l.pt                   # Optional: larger model
│
├── 📊 DATASETS
│   └── bags_only_dataset/           # Training/validation data
│       ├── images/
│       │   ├── train/               # Training images
│       │   ├── valid/               # Validation images
│       │   └── test/                # Test images
│       └── labels/                  # YOLO annotations
│
├── ⚙️ UTILITIES
│   ├── benchmark*.py                # Performance benchmarking
│   ├── fetch_model.py               # Model utilities
│   ├── data.yaml                    # Dataset config
│   └── requirements.txt             # Python dependencies
│
└── 🔧 CONFIGURATION
    └── .streamlit/
        └── config.toml              # Streamlit settings
```

---

## System Architecture

### High-Level Overview
```
┌───────────────────────────────────────────────────────────────────┐
│                     CLIENT TIER                                   │
├─────────────────┬──────────────────┬────────────────┬─────────────┤
│  Web Browser    │  Mobile App      │  Desktop App   │  IoT Device │
│  (React/Vue)    │  (React Native)  │  (Python SDK)  │  (Python)   │
└────────┬────────┴────────┬─────────┴────────┬───────┴──────┬──────┘
         │                 │                  │              │
         └─────────────────┼──────────────────┴──────────────┘
                           │ HTTP/HTTPS
         ┌─────────────────▼────────────────────┐
         │    GATEWAY TIER (Nginx)              │
         │  - Load balancing                    │
         │  - SSL/TLS termination               │
         │  - Rate limiting                     │
         │  - Request routing                   │
         └─────────────────┬────────────────────┘
                           │
         ┌─────────────────▼────────────────────┐
         │   APPLICATION TIER (FastAPI)         │
         │  - REST API endpoints                │
         │  - WebSocket streaming               │
         │  - Request validation                │
         │  - Session management                │
         └────────┬────────────────┬────────────┘
                  │                │
         ┌────────▼──────┐  ┌──────▼────────┐
         │ MODEL TIER    │  │ DATABASE TIER │
         ├───────────────┤  ├───────────────┤
         │ YOLOv8 INT8   │  │ Session cache │
         │ (Detection)   │  │ Analytics log │
         │ YOLOv8n       │  │ Alert history │
         │ (People)      │  └───────────────┘
         └───────────────┘
```

### Data Flow

#### 1. Single Image Detection Flow
```
Client Request
    │
    ├─ Upload image file
    ├─ Specify confidence (0.1-0.9)
    ├─ Specify time_limit (3-15s)
    │
    ▼
FastAPI Endpoint: /detect/image
    │
    ├─ Validate input
    ├─ Decode image
    ├─ Resize to 320x320
    │
    ▼
Detection Engine
    │
    ├─ Run YOLOv8 INT8 (bag detection)
    ├─ Extract confidence + bounding boxes
    ├─ Run YOLOv8n (person detection)
    ├─ Spatial matching (owner association)
    ├─ Stationary time calculation
    │
    ▼
Response Generator
    │
    ├─ Format detections JSON
    ├─ Encode frame (base64)
    ├─ Include alert information
    │
    ▼
Client Response (JSON + image)
```

#### 2. WebSocket Real-Time Streaming
```
Client                          Server
   │                              │
   ├─ Connect to /ws/detection    │
   │─────────────────────────────▶│
   │                   (establish session)
   │
   ├─ Send frame 1 (base64)       │
   │─────────────────────────────▶│ Detect
   │◀─────────────────────────────┤ Send result
   │     Result with detections    │
   │
   ├─ Send frame 2 (base64)       │
   │─────────────────────────────▶│ Detect
   │◀─────────────────────────────┤ Send result
   │     Result with detections    │
   │
   └─ Close connection            │
   │─────────────────────────────▶│
   │                   (cleanup session)
```

---

## Component Details

### 1. FastAPI Backend (`main.py`)

**Key Components:**

```python
ModelManager (Singleton)
├─ Load YOLOv8 INT8 once
├─ Load YOLOv8n once
└─ Share across requests

DetectionSession (Per-websocket)
├─ Track bag states
├─ Store alerts
├─ Count detections
└─ Manage statistics

LuggageDetector (Stateless)
├─ Detect bags (YOLOv8 INT8)
├─ Detect humans (YOLOv8n)
├─ Process detections
├─ Calculate stationary time
└─ Generate alerts
```

**Async Architecture:**
- Non-blocking requests
- Concurrent WebSocket connections
- Efficient resource utilization

### 2. Docker Containerization

**Multi-stage Build Process:**
```
Stage 1: Builder
├─ Base: python:3.9-slim
├─ Install build tools (gcc, g++)
├─ Install Python packages
└─ Output: /root/.local (optimized)

Stage 2: Runtime
├─ Base: python:3.9-slim (clean)
├─ Install only runtime deps
├─ Copy from builder
├─ Non-root user (security)
└─ Output: Optimized image
```

**Benefits:**
- Smaller image size (multi-stage)
- Security (non-root user)
- Health checks built-in
- Auto-restart on failure

### 3. Nginx Reverse Proxy

**Key Features:**
- Load balancing (future: multiple backends)
- SSL/TLS termination
- Gzip compression
- WebSocket upgrade handling
- Request routing
- Rate limiting support

**Configuration:**
```nginx
Upstream: api:8000
Client:80/443 ──▶ Nginx ──▶ FastAPI:8000
```

---

## API Design

### REST Endpoints

```
GET /health
├─ Purpose: Health check
├─ Response: Status, models, timestamp
└─ Use: Runtime monitoring

GET /models/info
├─ Purpose: Model metadata
├─ Response: All model specs
└─ Use: Client configuration

POST /detect/image
├─ Input: Image file + params
├─ Output: Detections JSON
└─ Use: Single frame detection

POST /detect/batch
├─ Input: Multiple images
├─ Output: Batch results
└─ Use: Dataset processing

GET /stats/session/{id}
├─ Purpose: Session statistics
├─ Response: Aggregated metrics
└─ Use: Analytics/monitoring
```

### WebSocket Endpoints

```
WS /ws/detection/{session_id}
├─ Connection: Persistent
├─ Message format: JSON
├─ Bidirectional streaming
└─ Use: Real-time processing
```

---

## Performance Characteristics

### Inference Times
```
Image Preprocessing:    2ms  (resize, normalize)
YOLOv8 INT8 (bags):    24ms  (backbone + neck + head)
YOLOv8n 1/15 frames:    1.6ms (humans - skipped 14/15)
Post-processing:        2ms  (NMS, box conversion)
─────────────────────────────
Per-frame latency:     32ms  (31.2 FPS with background overhead)
```

### Concurrency
```
Sequential Processing:  1 image = 32ms
Async/Await:           10 images = ~320ms (parallel)
WebSocket (batching):  1000 images = ~320ms
```

### Memory Usage
```
Idle:                   40 MB
Model Loaded:           55 MB
Single Inference:       84 MB (peak)
Multiple Concurrent:    84 MB (shared models)
```

---

## Scalability Design

### Horizontal Scaling (Add more containers)
```
Load Balancer (Nginx)
    │
    ├─ FastAPI #1 (cpu-core-0)
    ├─ FastAPI #2 (cpu-core-1)
    └─ FastAPI #3 (cpu-core-2)

Session Distribution:
├─ Session A ──▶ FastAPI #1
├─ Session B ──▶ FastAPI #2
└─ Session C ──▶ FastAPI #3
```

### Vertical Scaling (More resources)
```
Current: 1 core, 1GB RAM per container
Scaled:  4 cores, 4GB RAM per container

Uvicorn Workers: 1 ──▶ 4
```

### Database for Persistence (Future)
```
FastAPI ──▶ PostgreSQL
    │
    ├─ Store detection history
    ├─ Archive alerts
    ├─ Analytics queries
    └─ Audit logs
```

---

## Security Architecture

### Authentication
```
Option 1: Token-based (JWT)
├─ Client sends: Authorization: Bearer token
├─ Server validates token
└─ Allow/reject request

Option 2: API Key
├─ Client sends: X-API-Key: key
├─ Server lookup in database
└─ Allow/reject request
```

### CORS Policy
```
Production: 
├─ allow_origins=["https://yourdomain.com"]
├─ allow_methods=["POST", "GET"]
└─ allow_credentials=True

Development:
├─ allow_origins=["*"]
└─ allow_methods=["*"]
```

### SSL/TLS
```
Nginx ──(TLS)──▶ FastAPI
Client ──(TLS)──▶ Nginx
```

---

## Monitoring & Observability

### Logging
```
FastAPI (Uvicorn):
├─ Request logs
├─ Error traces
└─ Performance timing

Docker:
├─ Container stdout/stderr
├─ Log drivers (json-file, syslog)
└─ Log aggregation (ELK, Datadog)
```

### Metrics to Monitor
```
Performance:
├─ FPS (frames processed)
├─ Latency (per-request time)
├─ Memory usage
└─ CPU utilization

Business:
├─ Detection count
├─ Alert frequency
├─ Session duration
└─ Peak hours
```

### Health Checks
```
Container Level:
├─ HTTP /health endpoint
├─ Interval: 30 seconds
├─ Timeout: 10 seconds
└─ Retries: 3

Application Level:
├─ Model loading check
├─ Memory availability
├─ Disk space check
└─ Database connection
```

---

## Deployment Environments

### Development
```
docker run -p 8000:8000 \
  -v $(pwd):/app \
  luggage-detection:latest
```

### Staging
```
docker-compose -f docker-compose.yml up
# With Nginx on port 80
```

### Production
```
Kubernetes:
├─ Multiple replicas (3+)
├─ Load balancing
├─ Auto-scaling
├─ Health checks
├─ Rolling updates
└─ Persistent storage
```

---

## Future Enhancements

### Phase 2: Data Persistence
```
┌─ PostgreSQL (alerts history)
├─ Redis (session cache)
└─ S3/Blob (frame storage)
```

### Phase 3: Machine Learning Pipeline
```
├─ Model versioning
├─ A/B testing (different models)
├─ Feedback loop (improve accuracy)
└─ Automated retraining
```

### Phase 4: Advanced Features
```
├─ Multi-model ensemble
├─ Edge device deployment (ONNX)
├─ Custom model training endpoint
└─ Federated learning
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Client** | React/Vue/Python | User interface |
| **Gateway** | Nginx | Reverse proxy, load balancing |
| **Backend** | FastAPI | REST/WebSocket API |
| **Runtime** | Python 3.9 | Application runtime |
| **Detection** | YOLOv8 | Object detection |
| **Optimization** | OpenVINO | Model acceleration |
| **Container** | Docker | Containerization |
| **Orchestration** | Docker Compose | Service coordination |
| **Monitoring** | Built-in logging | Observability |

---

**Last Updated:** April 7, 2026  
**Version:** 1.0.0
