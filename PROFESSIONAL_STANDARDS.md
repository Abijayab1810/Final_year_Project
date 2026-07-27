# Professional Code Standards & Guidelines

## Overview
This document outlines the professional coding standards adopted in this project to meet enterprise-grade requirements.

---

## 1. Code Style & Organization

### Python Code Standards (PEP 8 + Black)
- **Line Length**: Maximum 100 characters
- **Indentation**: 4 spaces (never tabs)
- **Naming Conventions**:
  - Classes: `PascalCase` (e.g., `ModelManager`)
  - Functions/Methods: `snake_case` (e.g., `detect_bags()`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `MOVEMENT_TOLERANCE`)
  - Private methods: `_leading_underscore` (e.g., `_load_model()`)

### Module Organization
```
project/
├── core/              # Core detection engine
│   ├── __init__.py
│   ├── detector.py
│   └── tracker.py
├── api/               # FastAPI endpoints
│   ├── __init__.py
│   ├── routes.py
│   └── models.py
├── ui/                # Streamlit interface
│   ├── __init__.py
│   └── app.py
├── config/            # Configuration management
│   ├── __init__.py
│   └── settings.py
└── utils/             # Utility functions
    ├── __init__.py
    └── helpers.py
```

---

## 2. Documentation Standards

### Module-Level Docstrings
```python
"""
Module description: One-line summary.

Longer description if needed. Explain what this module does, why it exists,
and any important design decisions.

Example:
    Basic usage example::
    
        from module import MyClass
        obj = MyClass()
        result = obj.method()
"""
```

### Function/Method Docstrings (Google Style)
```python
def detect_bags(frame: np.ndarray, confidence: float = 0.35) -> List[Dict]:
    """
    Detect bags in a video frame using YOLOv8 INT8.
    
    Args:
        frame (np.ndarray): Input frame in BGR format (H, W, 3).
        confidence (float): Detection confidence threshold (0-1). Default: 0.35.
    
    Returns:
        List[Dict]: List of detections with format:
            {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class_id': int,
                'track_id': int
            }
    
    Raises:
        ValueError: If confidence is not in range [0, 1].
        RuntimeError: If model fails to load.
    
    Example:
        >>> frame = cv2.imread('image.jpg')
        >>> detections = detect_bags(frame, confidence=0.5)
        >>> print(f"Found {len(detections)} bags")
    """
```

### Class Docstrings
```python
class LuggageDetector:
    """
    Core detection engine for abandoned luggage.
    
    This class manages the complete detection pipeline including bag detection,
    human detection, and temporal reasoning to identify abandoned luggage.
    
    Attributes:
        bag_model (YOLO): YOLOv8 INT8 model for bag detection.
        person_model (YOLO): YOLOv8n model for person detection.
        movement_tolerance (int): Pixel distance for movement detection.
        grace_period (float): Seconds to keep tracking after last seen.
    
    Example:
        >>> detector = LuggageDetector()
        >>> frame = cv2.imread('security_feed.jpg')
        >>> result = detector.process_frame(frame, time_limit=5)
        >>> for alert in result['alerts']:
        ...     print(f"Abandoned bag detected: {alert}")
    """
```

---

## 3. Type Hints

**All public functions must have type hints:**

```python
from typing import List, Dict, Tuple, Optional, Union
import numpy as np

def track_bags(
    frame: np.ndarray,
    bag_states: Dict[int, Dict],
    time_limit: int = 5
) -> Tuple[List[Dict], List[Dict]]:
    """Track bags and return detections and alerts."""
    pass

def get_config(section: str) -> Optional[Dict[str, any]]:
    """Load configuration or None if not found."""
    pass
```

---

## 4. Error Handling

### Exception Strategy
```python
class DetectionError(Exception):
    """Base exception for detection errors."""
    pass

class ModelLoadError(DetectionError):
    """Raised when model fails to load."""
    pass

class CameraError(DetectionError):
    """Raised when camera is unavailable."""
    pass

# Usage
try:
    model = YOLO("path/to/model")
except FileNotFoundError:
    raise ModelLoadError("Model file not found at specified path")
except Exception as e:
    logger.error(f"Unexpected error loading model: {e}")
    raise ModelLoadError(f"Failed to load model: {str(e)}") from e
```

### Logging Strategy
```python
import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Usage
logger.debug("Detailed diagnostic information")
logger.info("General informational message")
logger.warning("Warning about potential issues")
logger.error("Error that needs attention")
logger.critical("Critical failure")
```

---

## 5. Testing Standards

### Unit Tests Structure
```
tests/
├── __init__.py
├── test_detector.py
├── test_tracker.py
├── test_api.py
└── fixtures/
    └── sample_frames/
```

### Test Example
```python
import pytest
from core.detector import LuggageDetector

class TestLuggageDetector:
    """Test suite for LuggageDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        return LuggageDetector()
    
    def test_detect_bags_returns_list(self, detector, sample_frame):
        """Test that detect_bags returns a list."""
        result = detector.detect_bags(sample_frame)
        assert isinstance(result, list)
    
    def test_detect_bags_empty_frame(self, detector, empty_frame):
        """Test detection on frame with no bags."""
        result = detector.detect_bags(empty_frame)
        assert len(result) == 0
    
    @pytest.mark.parametrize("confidence", [0.0, 0.5, 1.0])
    def test_confidence_threshold(self, detector, sample_frame, confidence):
        """Test different confidence thresholds."""
        result = detector.detect_bags(sample_frame, confidence=confidence)
        assert isinstance(result, list)
```

---

## 6. API Design Standards

### RESTful Endpoint Design
```python
# Good: Resource-oriented, clear semantics
GET    /api/v1/detections           # List all detections
POST   /api/v1/detections           # Create detection
GET    /api/v1/detections/{id}      # Get specific detection
PUT    /api/v1/detections/{id}      # Update detection
DELETE /api/v1/detections/{id}      # Delete detection

# Bad: Verb-heavy, action-oriented
GET    /api/listDetections
POST   /api/createDetection
GET    /api/getDetection
```

### Request/Response Models (Pydantic)
```python
from pydantic import BaseModel, Field, validator

class DetectionRequest(BaseModel):
    """Incoming detection request."""
    image: str = Field(..., description="Base64 encoded image")
    confidence: float = Field(0.35, ge=0.0, le=1.0)
    time_limit: int = Field(5, ge=1, le=300)
    
    @validator('confidence')
    def confidence_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('confidence must be between 0 and 1')
        return v

class DetectionResponse(BaseModel):
    """Outgoing detection response."""
    success: bool
    detections: List[Dict]
    processing_time_ms: float
    timestamp: str
```

---

## 7. Version Control Practices

### Commit Message Standards
```
Format: <type>(<scope>): <subject>

type: feat, fix, docs, style, refactor, test, chore
scope: detector, api, ui, config, etc.
subject: Imperative mood, max 50 chars

Example:
  feat(detector): Add dynamic tolerance for bag tracking
  fix(api): Handle empty frame gracefully
  docs(readme): Update deployment instructions
  refactor(core): Extract tracking logic to separate class
```

### Branch Naming
```
feature/add-camera-management
bugfix/fix-model-loading-error
docs/update-readme
refactor/extract-detection-logic
```

---

## 8. Performance Standards

### Benchmarking Requirements
- All major functions should have benchmarks
- Record baseline metrics for regression testing
- Target: 31.2 FPS @ 320x320 input

```python
import time

def benchmark_detector(iterations: int = 100):
    """Benchmark detection performance."""
    detector = LuggageDetector()
    times = []
    
    for _ in range(iterations):
        start = time.time()
        detector.detect_bags(sample_frame)
        times.append(time.time() - start)
    
    print(f"Mean: {np.mean(times):.4f}s")
    print(f"Std: {np.std(times):.4f}s")
    print(f"95th percentile: {np.percentile(times, 95):.4f}s")
```

---

## 9. Security Standards

### Sensitive Data Handling
- ✅ Never commit API keys, passwords, or secrets
- ✅ Use `.env` files with `.env.example` templates
- ✅ Validate all user inputs
- ✅ Use HTTPS in production
- ✅ Implement rate limiting on public APIs

```python
from pydantic import validator

class ConfigSettings(BaseModel):
    api_key: str = Field(..., description="API key from environment")
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if len(v) < 32:
            raise ValueError('API key must be at least 32 characters')
        return v
```

---

## 10. Deployment Standards

### Environment Configuration
```bash
# .env.example
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
MODEL_PATH=./models/best_int8_openvino_model
CAMERA_ID=0
CONFIDENCE_THRESHOLD=0.35
```

### Docker Standards
```dockerfile
# Use specific version pins
FROM python:3.10-slim

# Run as non-root user
RUN useradd -m appuser
USER appuser

# Health checks
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8000/ || exit 1
```

---

## 11. Monitoring & Logging

### Structured Logging
```python
import json
from datetime import datetime

def log_detection_event(detection_id: int, status: str, duration: float):
    """Log detection event in structured format."""
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': 'detection',
        'detection_id': detection_id,
        'status': status,
        'duration_seconds': duration,
        'service': 'luggage_detector'
    }
    logger.info(json.dumps(event))
```

### Metrics Collection
```python
from prometheus_client import Counter, Histogram

detections_total = Counter('detections_total', 'Total detections')
detection_duration = Histogram('detection_duration_seconds', 'Detection time')

@detection_duration.time()
def detect_bags(frame):
    detections_total.inc()
    return detector.detect_bags(frame)
```

---

## 12. Checklist for Pull Requests

- [ ] Code follows PEP 8 style guide
- [ ] All public functions have type hints
- [ ] Docstrings written (module, class, function level)
- [ ] Unit tests added (>80% coverage)
- [ ] No hardcoded values (use config)
- [ ] Error handling for edge cases
- [ ] Performance impact assessed
- [ ] Security review completed
- [ ] Commit messages follow convention
- [ ] README updated if needed

---

## 13. Code Review Guidelines

### Reviewer Checklist
- Correctness: Does the code do what it intends?
- Performance: Any inefficiencies or bottlenecks?
- Maintainability: Will others understand this code?
- Security: Any vulnerabilities or data leaks?
- Testing: Adequate test coverage?
- Documentation: Clear and up-to-date?

### Common Issues to Flag
- Missing error handling
- Insufficient type hints
- Performance regression
- Security vulnerabilities
- Untested edge cases
- Missing documentation

---

## References
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code by Robert Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/best-practices/)
