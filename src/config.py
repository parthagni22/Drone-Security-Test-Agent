# Configuration settings for the Drone Security Analyst Agent

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SAMPLE_VIDEO = os.path.join(DATA_DIR, "sample_video.mp4")
SAMPLE_TELEMETRY = os.path.join(DATA_DIR, "sample_telemetry.json")
DB_PATH = os.path.join(PROJECT_ROOT, "drone_security.db")

# Object detection settings
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4
CLASSES_OF_INTEREST = ["person", "car", "truck", "motorcycle", "bicycle"]

# Enhanced alert rules for better detection
ALERT_RULES = [
    {
        "name": "Night Person Detection",
        "condition": {
            "object_type": "person",
            "time_range": {"start": "22:00", "end": "06:00"}
        },
        "priority": "high"
    },
    {
        "name": "Vehicle in Restricted Hours", 
        "condition": {
            "object_type": ["car", "truck"],
            "time_range": {"start": "23:00", "end": "05:00"}
        },
        "priority": "medium"
    },
    {
        "name": "Multiple People Gathering",
        "condition": {
            "object_type": "person",
            "count": 2,
            "time_window": 300
        },
        "priority": "medium"
    },
    {
        "name": "Loitering Detection",
        "condition": {
            "object_type": "person",
            "duration": 30,
            "same_location": True
        },
        "priority": "high"
    },
    {
        "name": "Large Vehicle Alert",
        "condition": {
            "object_type": "truck",
            "confidence_threshold": 0.7
        },
        "priority": "medium"
    }
]
