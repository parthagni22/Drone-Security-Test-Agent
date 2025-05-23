# Save this as fix_config.py and run it with: python fix_config.py

def fix_config_file():
    """Fix the config.py file by replacing its content."""
    config_content = """# Configuration settings for the Drone Security Analyst Agent

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

# Alert rules
ALERT_RULES = [
    {
        "name": "Person Loitering",
        "condition": {
            "object_type": "person",
            "duration": 60,  # seconds
            "time_range": {"start": "22:00", "end": "06:00"}
        },
        "priority": "high"
    },
    {
        "name": "Vehicle at Restricted Area",
        "condition": {
            "object_type": ["car", "truck", "motorcycle"],
            "location": "restricted_zone",
        },
        "priority": "medium"
    },
    {
        "name": "Multiple People Gathering",
        "condition": {
            "object_type": "person",
            "count": 3,
            "time_range": {"start": "20:00", "end": "08:00"}
        },
        "priority": "low"
    }
]
"""
    
    try:
        with open('src/config.py', 'w') as f:
            f.write(config_content)
        print("Successfully fixed src/config.py!")
    except Exception as e:
        print(f"Error fixing config.py: {e}")

if __name__ == "__main__":
    fix_config_file()