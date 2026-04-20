"""
Create the default detection_config.json file
Run this once to generate the initial configuration
"""

import json
import os
from datetime import datetime

CONFIG_FILE = "detection_config.json"

DEFAULT_CONFIG = {
    "detection": {
        "min_abandonment_time": 5,
        "max_abandonment_time": 300,
        "confidence_threshold": 0.35,
        "bag_classes": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "frame_width": 320,
        "frame_height": 320
    },
    "tracking": {
        "dynamic_tolerance_pct": 0.10,
        "grace_period": 2.0,
        "person_conf_threshold": 0.5
    },
    "processing": {
        "person_check_interval": 15,
        "max_age_frames": 1000,
        "save_evidence": True
    },
    "camera": {
        "auto_reconnect": True,
        "reconnect_interval": 5
    },
    "alerts": {
        "enable_alerts": True,
        "alert_cooldown": 30,
        "log_to_database": True
    },
    "models": {
        "bag_model": "best_int8_openvino_model",
        "person_model": "yolov8n.pt",
        "device": "cpu"
    },
    "_comments": {
        "min_abandonment_time": "Increase for fewer false positives (default 5)",
        "confidence_threshold": "Lower (0.2) for sensitive, Higher (0.6) for strict (default 0.35)",
        "frame_width": "Higher (416) for accuracy, Lower (256) for speed (default 320)",
        "dynamic_tolerance_pct": "Movement allowance - lower = stricter (default 0.10)",
        "grace_period": "Forgiveness when bag disappears - higher helps with occlusions (default 2.0)",
        "person_check_interval": "Frames between person detection - higher = faster (default 15)"
    },
    "last_modified": datetime.now().isoformat()
}

if __name__ == "__main__":
    # Create the config file
    with open(CONFIG_FILE, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    
    print(f"✅ Created {CONFIG_FILE}")
    print("\nDefault Configuration:")
    print(json.dumps({k: v for k, v in DEFAULT_CONFIG.items() if k != "_comments"}, indent=2))
