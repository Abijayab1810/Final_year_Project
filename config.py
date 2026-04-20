"""
Real-time configuration for detection parameters
Load and adjust detection settings without redeploying
"""

import json
import os
from datetime import datetime

CONFIG_FILE = "detection_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "detection": {
        "min_abandonment_time": 3,  # seconds before alert
        "max_abandonment_time": 300,  # seconds max tracking
        "confidence_threshold": 0.35,  # YOLO confidence (0-1)
        "bag_classes": list(range(11)),  # Classes 0-10 for bags
        "frame_width": 320,  # Detection frame size
        "frame_height": 320
    },
    "tracking": {
        "dynamic_tolerance_pct": 0.10,  # Movement tolerance
        "grace_period": 2.0,  # Seconds before cleanup
        "person_conf_threshold": 0.5
    },
    "processing": {
        "person_check_interval": 15,  # Frames between person detection
        "max_age_frames": 1000,  # Max frames to track
        "save_evidence": True
    },
    "camera": {
        "auto_reconnect": True,
        "reconnect_interval": 5  # seconds
    },
    "alerts": {
        "enable_alerts": True,
        "alert_cooldown": 30,  # seconds between repeated alerts
        "log_to_database": True
    },
    "models": {
        "bag_model": "best_int8_openvino_model",
        "person_model": "yolov8n.pt",
        "device": "cpu"  # cpu, cuda, etc
    },
    "last_modified": datetime.now().isoformat()
}


def load_config() -> dict:
    """Load configuration from file, create default if not exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            print(f"✅ Loaded config from {CONFIG_FILE}")
            return config
        except Exception as e:
            print(f"⚠️ Error loading config: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """Save configuration to file"""
    try:
        config['last_modified'] = datetime.now().isoformat()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✅ Saved config to {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False


def get_detection_params(config: dict = None) -> dict:
    """Get detection parameters"""
    if config is None:
        config = load_config()
    return config.get('detection', DEFAULT_CONFIG['detection'])


def get_tracking_params(config: dict = None) -> dict:
    """Get tracking parameters"""
    if config is None:
        config = load_config()
    return config.get('tracking', DEFAULT_CONFIG['tracking'])


def get_processing_params(config: dict = None) -> dict:
    """Get processing parameters"""
    if config is None:
        config = load_config()
    return config.get('processing', DEFAULT_CONFIG['processing'])


def update_parameter(section: str, key: str, value) -> bool:
    """Update a single parameter"""
    config = load_config()
    
    if section not in config:
        print(f"❌ Section '{section}' not found")
        return False
    
    if key not in config[section]:
        print(f"❌ Key '{key}' not found in section '{section}'")
        return False
    
    old_value = config[section][key]
    config[section][key] = value
    
    success = save_config(config)
    if success:
        print(f"✅ Updated {section}.{key}: {old_value} → {value}")
    
    return success


def reset_to_defaults() -> bool:
    """Reset all settings to default"""
    return save_config(DEFAULT_CONFIG.copy())


def print_config(config: dict = None):
    """Pretty print current configuration"""
    if config is None:
        config = load_config()
    
    print("\n" + "=" * 60)
    print("📋 DETECTION CONFIGURATION")
    print("=" * 60)
    print(json.dumps(config, indent=2))
    print("=" * 60 + "\n")


# Initialize config on import
if not os.path.exists(CONFIG_FILE):
    load_config()
