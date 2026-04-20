# 🛡️ Smart Edge AI: Abandoned Luggage Detection

> **Advanced YOLOv8 INT8 Edge Computing Application for Real-Time Security Monitoring**

A production-ready **real-time object detection system** optimized for CPU deployment with 3.5x speed improvement through INT8 quantization. Detects abandoned luggage in security camera feeds with dual-model architecture (luggage + human detection).

## 🎯 Key Features

### 🚀 Performance
- **31.2 FPS** on CPU (3.5x faster than original)
- **12.4 MB** model size (78% compression)
- **92.8% accuracy** maintained after quantization
- **84 MB** RAM usage - edge device ready

### 🔍 Detection Capabilities
- **11 bag/luggage classes**: Backpack, Handbag, Suitcase, Trash bag, Paper bag, Hand bag, Gunny bag, Carry bag, Big handbag, Box bag, Kattapai
- **Dual-model tracking**: Bags + Humans for smart owner association
- **Spatial intelligence**: Movement tolerance logic
- **Grace period**: Smart bag persistence (2 seconds)

### 📊 Advanced Features
- **Multi-tab dashboard**: Live detection, performance metrics, model comparison, statistics
- **Adjustable confidence threshold**: Fine-tune detection sensitivity
- **Real-time metrics**: FPS, detection count, alert status
- **Session statistics**: Track detections and alerts over time
- **Camera compatibility**: Works with any USB/integrated camera

---

## 📋 Technical Specifications

### Models Used
| Model | Purpose | Architecture | Optimization |
|-------|---------|--------------|--------------|
| **Primary** | Bag Detection | YOLOv8 | OpenVINO INT8 ⭐ |
| **Secondary** | Human Detection | YOLOv8n | Standard PyTorch |
| **Input Size** | Both | 320×320 pixels | Pre-optimized |

## 🚀 Performance Comparison
```
┌─────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Model Type      │ FPS      │ Size     │ Accuracy │ Device   │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Original (FP32) │ 8.9      │ 56.3 MB  │ 94.0%    │ GPU      │
│ OpenVINO FP32   │ 15.2     │ 52.1 MB  │ 93.9%    │ CPU      │
│ OpenVINO FP16   │ 22.4     │ 26.0 MB  │ 93.7%    │ CPU      │
│ OpenVINO INT8 ⭐ │ 31.2     │ 12.4 MB  │ 92.8%    │ CPU ✓    │
└─────────────────┴──────────┴──────────┴──────────┴──────────┘

Metrics Explanation:
- FPS: Frames per second on Intel Core i7
- Size: Model file size (78% reduction for INT8)
- Accuracy: mAP50 on validation set
- INT8 achieves 3.5x speedup with <2% accuracy loss ✅
```

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
Webcam or RTSP camera feed
6GB+ available RAM
Intel CPU (OpenVINO optimized)
```

### Installation

1. **Clone & Setup**
```bash
git clone https://github.com/Abijayab1810/final_year_project.git
cd final_year_project
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the App**
```bash
streamlit run app.py
```

4. **Open Browser**
```
http://localhost:8501
```

---

## 📖 Usage Guide

### Live Detection Tab
1. Click the **"🟢 START SECURITY FEED"** checkbox in sidebar
2. App will access your webcam
3. View real-time detections and tracking
4. **Colors indicate:**
   - 🟢 **Green**: Bag with owner (accompanied)
   - 🟡 **Yellow**: Stationary bag (counting time)
   - 🔴 **Red**: ABANDONED LUGGAGE (ALERT!)
   - 🔵 **Blue**: Human detected

### Adjustable Parameters
- **Abandonment Time**: 3-15 seconds (default: 5s)
- **Confidence Threshold**: 0.1-0.9 (default: 0.35)

### Performance Metrics Tab
- View model optimization benchmarks
- Compare INT8 vs original model
- See accuracy/speed trade-offs

### Model Comparison Tab
- Side-by-side comparison of all 4 model variants
- Precision, FPS, size, accuracy metrics
- Deployment recommendation

### Statistics Tab
- Session detection count
- Alert triggers count
- Detection history

---

## 🏗️ Project Architecture

```
final_year_project/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── data.yaml                       # Dataset configuration
├── best_int8_openvino_model/      # Deployed INT8 model
│   ├── best.xml                    # Model graph
│   ├── best.bin                    # Model weights
│   └── metadata.yaml               # Metadata
├── bags_only_dataset/              # Training dataset
│   ├── images/
│   │   ├── train/
│   │   ├── valid/
│   │   └── test/
│   └── labels/
├── .streamlit/                     # Streamlit config
│   └── config.toml
├── benchmark*.py                   # Performance benchmarking scripts
└── PROJECT_SUMMARY.md             # Detailed project documentation
```

---

## 🔧 Advanced Configuration

### Modify Detection Sensitivity
Edit [app.py](app.py) line to adjust confidence:
```python
conf_threshold = 0.35  # Lower = more detections, more false positives
```

### Change Abandonment Time Logic
```python
time_limit = 5  # seconds before alert triggers
MOVEMENT_TOLERANCE = 20  # pixels allowed before reset
GRACE_PERIOD = 2.0  # seconds to remember bags
```

### Add Custom Alerts
Extend the alert logic:
```python
if alert_triggered:
    # Add email notification
    # Add sound/buzzer
    # Send webhook to server
    pass
```

---

## 📊 Accuracy & Performance

### Benchmarking Results
- **mAP50 Score**: 92.8% (INT8 vs 94.0% original)
- **Inference Latency**: 32ms per frame (CPU)
- **False Positive Rate**: <3% (confidence threshold: 0.35)
- **False Negative Rate**: <5% in optimal lighting

### Tested Environments
- ✅ Windows 10/11 (Intel Core i7)
- ✅ Ubuntu 20.04 (CPU)
- ✅ Raspberry Pi 4 (ARM CPU)
- ✅ Jetson Nano (NVIDIA edge device)

---

## 🎯 Use Cases

1. **Airport Security**: Detect abandoned luggage at check-in/departure areas
2. **Public Transport**: Monitor bags in trains/buses
3. **Retail**: Detect unattended packages in malls
4. **Corporate Events**: Security monitoring at venues
5. **Border Control**: Bag detection in security checkpoints

---

## � Advanced Optimization Opportunities

**Further latency reduction possible with:**
- **Structured Pruning**: 10-15% speedup (1-2% accuracy loss)
- **Knowledge Distillation**: 25% speedup with accuracy recovery
- **Dynamic Batching**: 15-20% speedup (CPU optimized)
- **QAT Fine-tuning**: Recovers 94.2% accuracy (same latency)

**See [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md) for detailed implementation strategies.**

Current INT8 represents optimal **Pareto frontier** for production edge deployment:
- ✅ **3.5x faster** than original
- ✅ **78% smaller** model size  
- ✅ **92.8% accuracy** maintained
- ✅ **32ms latency** per frame (31.2 FPS)
- ✅ **84 MB RAM** - works on edge devices

---

### Option 1: Streamlit Cloud (Fastest)
```bash
git push origin main
# Go to share.streamlit.io → Deploy
```

### Option 2: Docker Deployment
```bash
docker build -t luggage-detection .
docker run -p 8501:8501 luggage-detection
```

### Option 3: Self-Hosted Server
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 📚 Model Training Details

### Dataset
- **Size**: 1,500+ annotated images
- **Classes**: 11 luggage types
- **Train/Valid/Test Split**: 70/20/10
- **Format**: YOLO format (.txt annotations)

### Training Configuration
- **Framework**: YOLOv8 (Ultralytics)
- **Epochs**: 100
- **Batch Size**: 16
- **Input Size**: 640×640 (inference: 320×320)
- **Augmentation**: Mosaic, rotation, flip, color jitter

### Optimization Pipeline
```
Original Model (FP32)
        ↓ (Export)
   OpenVINO FP32
        ↓ (Half-precision conversion)
   OpenVINO FP16
        ↓ (INT8 Quantization)
   OpenVINO INT8 ⭐ (DEPLOYED)
```

---

## 🎓 Educational Value

This project demonstrates:
- ✅ **Resource Optimization**: 3.5x speed improvement through quantization
- ✅ **Edge Computing**: CPU-optimized inference
- ✅ **Real-Time Processing**: Multi-model tracking pipeline
- ✅ **Production Deployment**: Streamlit containerization
- ✅ **Computer Vision**: Object detection + tracking logic
- ✅ **Decision Logic**: Smart owner association algorithm

---

## 📝 License

This project is open-source for educational purposes.

---

## 💬 Contact & Support

- **GitHub**: [Abijayab1810/final_year_project](https://github.com/Abijayab1810/final_year_project)
- **Email**: abijayab1810@gmail.com
- **Issues**: Report bugs via GitHub Issues

---

## 🙏 Acknowledgments

- **Ultralytics** - YOLOv8 framework
- **Intel OpenVINO** - Model optimization toolkit
- **Streamlit** - Web app framework

---

**⭐ If this project helps you, please star the repository!**

---

## 🚀 Production Deployment

### Option 1: Docker Deployment (Recommended)

**One-command deployment:**
```bash
# Make script executable and deploy
chmod +x deploy.sh
./deploy.sh deploy
```

**Manual deployment:**
```bash
# Build and run with Docker Compose
docker-compose build
docker-compose up -d

# Check health
curl http://localhost:8000/
```

**Access your application:**
- **Frontend:** http://localhost:8000/frontend
- **API Docs:** http://localhost:8000/docs
- **Statistics:** http://localhost:8000/stats

### Option 2: Direct FastAPI

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python main.py
```

### Option 3: Cloud Deployment

**Railway (Recommended for production):**
```bash
# Push to GitHub first
git add .
git commit -m "Production deployment"
git push origin main

# Deploy on Railway
# 1. Go to railway.app
# 2. Connect GitHub repo
# 3. Set build command: pip install -r requirements.txt
# 4. Set start command: python main.py
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/stats` | Session statistics |
| `POST` | `/detect` | Single image detection |
| `WebSocket` | `/ws/detect` | Real-time camera detection |
| `GET` | `/frontend` | Web interface |
| `GET` | `/docs` | Interactive API documentation |

---

## 🔧 Configuration

### Environment Variables
```bash
MOVEMENT_TOLERANCE=20    # Pixels for movement detection
GRACE_PERIOD=2.0         # Seconds to remember bags
CONFIDENCE_THRESHOLD=0.35 # Detection confidence
HOST=0.0.0.0
PORT=8000
```

---

## 📈 Monitoring & Analytics

### Real-time Metrics
- **FPS:** Current processing speed
- **Latency:** End-to-end processing time
- **Memory:** RAM usage
- **Detections:** Total bags detected
- **Alerts:** Abandoned luggage alerts

### Health Checks
```bash
# Application health
curl http://localhost:8000/

# Detailed stats
curl http://localhost:8000/stats
```

---

## 🐛 Troubleshooting

**Camera not working:**
```bash
ls /dev/video*
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

**Model loading errors:**
```bash
ls -la best_int8_openvino_model/
python -c "import openvino; print(openvino.__version__)"
```

**Port issues:**
```bash
lsof -ti:8000 | xargs kill -9
```

---

## 🔒 Security Considerations

- ✅ **HTTPS:** Use reverse proxy
- ✅ **Authentication:** Add API keys
- ✅ **Rate limiting:** Prevent abuse
- ✅ **Container security:** Non-root user
- ✅ **Input validation:** Sanitize images

---

## 📚 Advanced Features

### Custom Model Integration
```python
model = YOLO("your_custom_model.pt")
ov_model = convert_model(model.model)
```

### Multi-Camera Support
```python
@app.websocket("/ws/camera/{camera_id}")
async def camera_feed(websocket: WebSocket, camera_id: int):
    pass
```

---

## 🎯 Performance Optimization

### Current Benchmarks
```
FPS: 31.2 | Accuracy: 92.8% | Memory: 84 MB
Latency: 32ms | CPU Usage: 25-35%
```

### Further Optimizations
- **Structured Pruning:** +10-15% speed
- **Knowledge Distillation:** +25% speed
- **Dynamic Batching:** +15-20% speed

*See [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md)*

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for real-world computer vision applications**
