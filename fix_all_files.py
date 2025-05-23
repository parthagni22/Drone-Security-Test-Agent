import os

def ensure_dir(dir_path):
    """Ensure the directory exists."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

def write_file(file_path, content):
    """Write content to a file, creating directories if needed."""
    # Ensure the directory exists
    dir_path = os.path.dirname(file_path)
    ensure_dir(dir_path)
    
    # Write the file
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Updated file: {file_path}")

# Define all the file contents

CONFIG_PY = """# Configuration settings for the Drone Security Analyst Agent

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

OBJECT_DETECTOR_PY = """import cv2
import numpy as np
import os
import time
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import CONFIDENCE_THRESHOLD, NMS_THRESHOLD, CLASSES_OF_INTEREST

class ObjectDetector:
    """Simulated object detector class."""
    
    def __init__(self):
        self.classes = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", 
            "truck", "boat", "traffic light", "fire hydrant", "stop sign", 
            "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", 
            "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", 
            "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", 
            "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", 
            "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", 
            "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", 
            "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant", 
            "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", 
            "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", 
            "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", 
            "hair drier", "toothbrush"
        ]
    
    def detect_objects(self, frame):
        """
        Simulated object detection for the prototype.
        In a real implementation, this would use a model like YOLO, SSD, or similar.
        """
        if frame is None:
            return []
        
        # For the prototype, we'll simulate detections
        # In a real implementation, this would call the model
        height, width = frame.shape[:2]
        
        # Simulate some random detections
        detections = []
        
        # Create more deterministic "detections" based on frame color patterns
        # This helps create more consistent behavior for demo purposes
        
        # Calculate the average color in different regions of the frame
        regions = [
            (0, 0, width//3, height//3),           # top-left
            (width//3*2, 0, width, height//3),     # top-right
            (width//3, height//3, width//3*2, height//3*2),  # center
            (0, height//3*2, width//3, height)     # bottom-left
        ]
        
        for i, (x1, y1, x2, y2) in enumerate(regions):
            region = frame[y1:y2, x1:x2]
            if region.size == 0:
                continue
                
            avg_color = np.mean(region, axis=(0, 1))
            
            # Use color values to determine if an object is "detected"
            if avg_color[0] > 100:  # Higher blue component
                class_id = 2  # car
                confidence = 0.8 + (avg_color[0] - 100) / 400  # Normalize to 0.8-0.9 range
            elif avg_color[1] > 100:  # Higher green component
                class_id = 0  # person
                confidence = 0.75 + (avg_color[1] - 100) / 400
            elif avg_color[2] > 150:  # Higher red component
                class_id = 7  # truck
                confidence = 0.85 + (avg_color[2] - 150) / 400
            elif np.mean(avg_color) > 200:  # Very bright region
                class_id = 67  # cell phone
                confidence = 0.6 + (np.mean(avg_color) - 200) / 200
            else:
                continue
            
            # Limit confidence to valid range
            confidence = min(max(confidence, 0.5), 0.99)
            
            # Create a bounding box that's proportional to the region
            region_width = x2 - x1
            region_height = y2 - y1
            box_width = int(region_width * 0.6)
            box_height = int(region_height * 0.6)
            
            # Position the box near the center of the region
            box_x = x1 + (region_width - box_width) // 2
            box_y = y1 + (region_height - box_height) // 2
            
            bbox = [box_x, box_y, box_x + box_width, box_y + box_height]
            
            # Only add if class is in our classes of interest
            class_name = self.classes[class_id]
            if class_name in CLASSES_OF_INTEREST:
                detections.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": bbox
                })
        
        return detections
    
    def draw_detections(self, frame, detections):
        """Draw detection bounding boxes on the frame."""
        if frame is None or not detections:
            return frame
        
        result = frame.copy()
        
        for detection in detections:
            bbox = detection["bbox"]
            class_name = detection["class_name"]
            confidence = detection["confidence"]
            
            # Define a different color for each class
            if class_name == "person":
                color = (0, 255, 0)  # Green for people
            elif class_name in ["car", "truck", "motorcycle"]:
                color = (255, 0, 0)  # Blue for vehicles
            else:
                color = (0, 0, 255)  # Red for others
            
            # Draw bounding box
            cv2.rectangle(result, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw label background
            label = f"{class_name}: {confidence:.2f}"
            label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            y = bbox[1] - 15 if bbox[1] - 15 > 15 else bbox[1] + 15
            cv2.rectangle(result, (bbox[0], y - label_size[1]), (bbox[0] + label_size[0], y + baseline), color, -1)
            
            # Draw label text
            cv2.putText(result, label, (bbox[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return result
"""

CONTEXT_ANALYZER_PY = """from datetime import datetime, timedelta
import os
import sys

class ContextAnalyzer:
    """Analyzes object detections in the context of telemetry data and time."""
    
    def __init__(self, telemetry_processor):
        self.telemetry_processor = telemetry_processor
        self.object_history = {}  # Track objects over time
        self.current_context = {}  # Current analysis context
    
    def analyze_frame(self, frame_data, detections):
        """
        Analyze detected objects in the context of the current frame.
        
        Args:
            frame_data: Dict containing frame metadata (timestamp, etc.)
            detections: List of object detections from the object detector
            
        Returns:
            Dict containing contextualized detection data
        """
        timestamp = frame_data.get("timestamp", "00:00:00")
        
        # Get telemetry data for this timestamp
        telemetry = self.telemetry_processor.get_telemetry_at_time(timestamp)
        location = telemetry.get("location", "Unknown") if telemetry else "Unknown"
        
        # Update context
        self.current_context = {
            "timestamp": timestamp,
            "location": location,
            "telemetry": telemetry
        }
        
        # Process each detection with context
        contextualized_detections = []
        current_time = datetime.strptime(timestamp, "%H:%M:%S") if isinstance(timestamp, str) else timestamp
        
        for detection in detections:
            detection_id = f"{detection['class_name']}_{detection['bbox'][0]}_{detection['bbox'][1]}"
            
            # Check if we've seen this object before (simple tracking)
            if detection_id in self.object_history:
                prev_detection = self.object_history[detection_id]
                prev_time = datetime.strptime(prev_detection["timestamp"], "%H:%M:%S")
                duration = (current_time - prev_time).total_seconds()
                
                # Update with duration information
                detection_with_context = {
                    **detection,
                    "timestamp": timestamp,
                    "location": location,
                    "first_seen": prev_detection["timestamp"],
                    "duration": duration,
                    "count": prev_detection.get("count", 1) + 1
                }
            else:
                # First time seeing this object
                detection_with_context = {
                    **detection,
                    "timestamp": timestamp,
                    "location": location,
                    "first_seen": timestamp,
                    "duration": 0,
                    "count": 1
                }
            
            # Add telemetry data if available
            if telemetry:
                detection_with_context["altitude"] = telemetry.get("altitude")
                detection_with_context["drone_status"] = telemetry.get("status")
            
            # Add descriptive context
            description = self._generate_detection_description(detection_with_context)
            detection_with_context["description"] = description
            
            contextualized_detections.append(detection_with_context)
            
            # Update history
            self.object_history[detection_id] = detection_with_context
        
        # Clean up old entries from history (older than 5 minutes)
        self._clean_history(current_time)
        
        return {
            "timestamp": timestamp,
            "location": location,
            "detections": contextualized_detections,
            "telemetry": telemetry
        }
    
    def _generate_detection_description(self, detection):
        """Generate a human-readable description of the detection."""
        class_name = detection["class_name"]
        location = detection["location"]
        timestamp = detection["timestamp"]
        confidence = detection["confidence"]
        
        # Generate more specific descriptions based on object type
        if class_name == "car":
            return f"Car detected at {location}, {timestamp}"
        elif class_name == "truck":
            return f"Truck spotted at {location}, {timestamp}"
        elif class_name == "person":
            # Add special context for people based on time
            time_obj = datetime.strptime(timestamp, "%H:%M:%S") if isinstance(timestamp, str) else timestamp
            hour = time_obj.hour
            
            if 22 <= hour or hour < 6:
                return f"Person detected at {location} during nighttime ({timestamp})"
            else:
                return f"Person present at {location}, {timestamp}"
        else:
            return f"{class_name.capitalize()} detected at {location}, {timestamp}"
    
    def _clean_history(self, current_time, max_age_seconds=300):
        """Remove old entries from object history."""
        keys_to_remove = []
        
        for obj_id, data in self.object_history.items():
            timestamp = data["timestamp"]
            if isinstance(timestamp, str):
                obj_time = datetime.strptime(timestamp, "%H:%M:%S")
            else:
                obj_time = timestamp
                
            age = (current_time - obj_time).total_seconds()
            if age > max_age_seconds:
                keys_to_remove.append(obj_id)
        
        for key in keys_to_remove:
            del self.object_history[key]
"""

RULE_ENGINE_PY = """from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import ALERT_RULES

class RuleEngine:
    """Evaluates security rules against detected objects and generates alerts."""
    
    def __init__(self):
        self.rules = ALERT_RULES
        self.object_history = {}  # Track objects over time for duration-based rules
    
    def evaluate_frame(self, context_data):
        """
        Evaluate all rules against the current frame context.
        
        Args:
            context_data: Dict containing contextualized detection data
            
        Returns:
            List of triggered alerts
        """
        if not context_data or "detections" not in context_data:
            return []
            
        timestamp = context_data.get("timestamp", "00:00:00")
        location = context_data.get("location", "Unknown")
        detections = context_data.get("detections", [])
        
        # Update object history for tracking over time
        self._update_history(detections, timestamp)
        
        # Evaluate each rule
        triggered_alerts = []
        
        for rule in self.rules:
            alerts = self._evaluate_rule(rule, detections, timestamp, location)
            triggered_alerts.extend(alerts)
        
        return triggered_alerts
    
    def _update_history(self, detections, timestamp):
        """Update the object history with new detections."""
        current_time = datetime.strptime(timestamp, "%H:%M:%S") if isinstance(timestamp, str) else timestamp
        
        # Group detections by class for counting
        class_counts = {}
        for detection in detections:
            class_name = detection["class_name"]
            if class_name not in class_counts:
                class_counts[class_name] = 0
            class_counts[class_name] += 1
            
            # Track individual objects too
            obj_id = f"{class_name}_{detection['bbox'][0]}_{detection['bbox'][1]}"
            
            if obj_id in self.object_history:
                # Update existing entry
                self.object_history[obj_id]["last_seen"] = current_time
                duration = (current_time - self.object_history[obj_id]["first_seen"]).total_seconds()
                self.object_history[obj_id]["duration"] = duration
            else:
                # New entry
                self.object_history[obj_id] = {
                    "class_name": class_name,
                    "location": detection.get("location", "Unknown"),
                    "first_seen": current_time,
                    "last_seen": current_time,
                    "duration": 0
                }
        
        # Update class counts
        for class_name, count in class_counts.items():
            self.object_history[f"count_{class_name}"] = count
        
        # Clean up old entries (older than 10 minutes)
        self._clean_history(current_time)
    
    def _clean_history(self, current_time, max_age_seconds=600):
        """Remove old entries from object history."""
        keys_to_remove = []
        
        for obj_id, data in self.object_history.items():
            if obj_id.startswith("count_"):
                continue
                
            age = (current_time - data["last_seen"]).total_seconds()
            if age > max_age_seconds:
                keys_to_remove.append(obj_id)
        
        for key in keys_to_remove:
            del self.object_history[key]
    
    def _evaluate_rule(self, rule, detections, timestamp, location):
        """Evaluate a single rule against the current context."""
        alerts = []
        rule_name = rule.get("name", "Unnamed Rule")
        priority = rule.get("priority", "low")
        condition = rule.get("condition", {})
        
        # Parse current time
        current_time = datetime.strptime(timestamp, "%H:%M:%S") if isinstance(timestamp, str) else timestamp
        current_hour = current_time.hour
        
        # Check time range condition if specified
        time_range = condition.get("time_range")
        if time_range:
            start_hour = int(time_range["start"].split(":")[0])
            end_hour = int(time_range["end"].split(":")[0])
            
            # Handle overnight ranges (e.g., 22:00 to 06:00)
            if start_hour > end_hour:
                if not (current_hour >= start_hour or current_hour < end_hour):
                    return []  # Outside time range
            else:
                if not (start_hour <= current_hour < end_hour):
                    return []  # Outside time range
        
        # Check location condition if specified
        if "location" in condition and location != condition["location"]:
            return []  # Location doesn't match
        
        # Check object type and count conditions
        object_type = condition.get("object_type")
        min_count = condition.get("count", 1)
        min_duration = condition.get("duration", 0)
        
        # Allow object_type to be either a string or a list
        if isinstance(object_type, str):
            object_types = [object_type]
        else:
            object_types = object_type
        
        # Check for matching objects
        matching_objects = []
        for detection in detections:
            if detection["class_name"] in object_types:
                matching_objects.append(detection)
        
        # Check count condition
        if len(matching_objects) < min_count:
            return []  # Not enough matching objects
        
        # Check duration condition if specified
        if min_duration > 0:
            # For duration rules, check if any object has been present for the required time
            duration_condition_met = False
            
            for obj_id, data in self.object_history.items():
                if obj_id.startswith("count_"):
                    continue
                    
                if data["class_name"] in object_types and data["duration"] >= min_duration:
                    duration_condition_met = True
                    break
            
            if not duration_condition_met:
                return []  # Duration condition not met
        
        # All conditions met, generate alert
        alert = {
            "timestamp": timestamp,
            "rule_name": rule_name,
            "priority": priority,
            "message": self._generate_alert_message(rule, matching_objects, location, timestamp),
            "objects": [obj["class_name"] for obj in matching_objects],
            "location": location
        }
        
        alerts.append(alert)
        return alerts
    
    def _generate_alert_message(self, rule, objects, location, timestamp):
        """Generate a human-readable alert message."""
        rule_name = rule.get("name", "Security Alert")
        
        if rule_name == "Person Loitering":
            return f"ALERT: Person loitering at {location}, {timestamp}"
        elif rule_name == "Vehicle at Restricted Area":
            vehicle_types = [obj["class_name"] for obj in objects]
            return f"ALERT: {', '.join(vehicle_types)} detected in restricted area ({location}), {timestamp}"
        elif rule_name == "Multiple People Gathering":
            count = len(objects)
            return f"ALERT: Group of {count} people detected at {location}, {timestamp}"
        else:
            return f"ALERT: {rule_name} at {location}, {timestamp}"
"""

FRAME_INDEXER_PY = """import sqlite3
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_PATH

class FrameIndexer:
    """Indexes video frames with metadata for later querying."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_database()
    
    def _create_database(self):
        """Create the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create frames table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS frames (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            location TEXT,
            frame_index INTEGER,
            description TEXT,
            telemetry_data TEXT
        )
        ''')
        
        # Create objects table for detected objects
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY,
            frame_id INTEGER,
            class_name TEXT NOT NULL,
            confidence REAL,
            bbox TEXT,
            description TEXT,
            FOREIGN KEY (frame_id) REFERENCES frames (id)
        )
        ''')
        
        # Create alerts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            rule_name TEXT NOT NULL,
            priority TEXT,
            message TEXT,
            location TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def index_frame(self, frame_data, context_data):
        """
        Index a frame with its context and detection data.
        
        Args:
            frame_data: Dict containing frame metadata
            context_data: Dict containing contextualized detection data
        
        Returns:
            frame_id: ID of the indexed frame
        """
        timestamp = context_data.get("timestamp", "00:00:00")
        location = context_data.get("location", "Unknown")
        frame_index = frame_data.get("frame_idx", 0)
        description = frame_data.get("description", "")
        telemetry = context_data.get("telemetry", {})
        
        # Serialize telemetry data
        telemetry_json = json.dumps(telemetry) if telemetry else None
        
        # Insert frame data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO frames (timestamp, location, frame_index, description, telemetry_data)
        VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, location, frame_index, description, telemetry_json))
        
        frame_id = cursor.lastrowid
        
        # Insert object detections
        detections = context_data.get("detections", [])
        for detection in detections:
            class_name = detection.get("class_name", "unknown")
            confidence = detection.get("confidence", 0.0)
            bbox = json.dumps(detection.get("bbox", [0, 0, 0, 0]))
            description = detection.get("description", "")
            
            cursor.execute('''
            INSERT INTO objects (frame_id, class_name, confidence, bbox, description)
            VALUES (?, ?, ?, ?, ?)
            ''', (frame_id, class_name, confidence, bbox, description))
        
        conn.commit()
        conn.close()
        
        return frame_id
    
    def index_alert(self, alert):
        """
        Index an alert.
        
        Args:
            alert: Dict containing alert data
        
        Returns:
            alert_id: ID of the indexed alert
        """
        timestamp = alert.get("timestamp", "00:00:00")
        rule_name = alert.get("rule_name", "Unknown Rule")
        priority = alert.get("priority", "low")
        message = alert.get("message", "")
        location = alert.get("location", "Unknown")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO alerts (timestamp, rule_name, priority, message, location)
        VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, rule_name, priority, message, location))
        
        alert_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return alert_id
    
    def query_frames_by_object(self, object_class):
        """
        Query frames that contain a specific object class.
        
        Args:
            object_class: Object class name to search for
            
        Returns:
            List of matching frames with object data
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT f.*, o.class_name, o.confidence, o.bbox, o.description as object_description
        FROM frames f
        JOIN objects o ON f.id = o.frame_id
        WHERE o.class_name = ?
        ORDER BY f.timestamp
        ''', (object_class,))
        
        results = []
        for row in cursor.fetchall():
            frame = dict(row)
            # Parse the bbox JSON
            if frame["bbox"]:
                frame["bbox"] = json.loads(frame["bbox"])
            # Parse telemetry data
            if frame["telemetry_data"]:
                frame["telemetry_data"] = json.loads(frame["telemetry_data"])
            results.append(frame)
        
        conn.close()
        return results
    
    def query_frames_by_time(self, start_time, end_time):
        """
        Query frames within a time range.
        
        Args:
            start_time: Start time (HH:MM:SS)
            end_time: End time (HH:MM:SS)
            
        Returns:
            List of matching frames
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT f.*, GROUP_CONCAT(o.class_name) as objects
        FROM frames f
        LEFT JOIN objects o ON f.id = o.frame_id
        WHERE f.timestamp BETWEEN ? AND ?
        GROUP BY f.id
        ORDER BY f.timestamp
        ''', (start_time, end_time))
        
        results = []
        for row in cursor.fetchall():
            frame = dict(row)
            # Parse telemetry data
            if frame["telemetry_data"]:
                frame["telemetry_data"] = json.loads(frame["telemetry_data"])
            results.append(frame)
        
        conn.close()
        return results
    
    def query_alerts(self, priority=None, start_time=None, end_time=None):
        """
        Query alerts with optional filters.
        
        Args:
            priority: Filter by priority (high, medium, low)
            start_time: Start time (HH:MM:SS)
            end_time: End time (HH:MM:SS)
            
        Returns:
            List of matching alerts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM alerts WHERE 1=1"
        params = []
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if start_time and end_time:
            query += " AND timestamp BETWEEN ? AND ?"
            params.extend([start_time, end_time])
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
"""

EVENT_LOGGER_PY = """import logging
import os
from pathlib import Path
import json
from datetime import datetime

class EventLogger:
    """Logs security events and object detections."""
    
    def __init__(self, log_dir=None):
        if log_dir is None:
            # Default to a logs directory in the project root
            project_root = Path(__file__).parent.parent.parent
            log_dir = os.path.join(project_root, "logs")
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        self.log_dir = log_dir
        self.detection_log_path = os.path.join(log_dir, "detections.log")
        self.alert_log_path = os.path.join(log_dir, "alerts.log")
        
        # Configure logging
        self._setup_logging()
        
        # In-memory storage for recent events (for quick access)
        self.recent_detections = []
        self.recent_alerts = []
        self.max_recent_items = 100
    
    def _setup_logging(self):
        """Set up logging handlers."""
        # Detection logger
        self.detection_logger = logging.getLogger("detection_logger")
        self.detection_logger.setLevel(logging.INFO)
        
        detection_handler = logging.FileHandler(self.detection_log_path)
        detection_formatter = logging.Formatter('%(asctime)s - %(message)s')
        detection_handler.setFormatter(detection_formatter)
        self.detection_logger.addHandler(detection_handler)
        
        # Alert logger
        self.alert_logger = logging.getLogger("alert_logger")
        self.alert_logger.setLevel(logging.INFO)
        
        alert_handler = logging.FileHandler(self.alert_log_path)
        alert_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        alert_handler.setFormatter(alert_formatter)
        self.alert_logger.addHandler(alert_handler)
    
    def log_detection(self, detection):
        """
        Log an object detection.
        
        Args:
            detection: Dict containing detection data
        """
        if not detection:
            return
        
        class_name = detection.get("class_name", "unknown")
        confidence = detection.get("confidence", 0.0)
        location = detection.get("location", "Unknown")
        timestamp = detection.get("timestamp", "00:00:00")
        
        # Create a log message
        log_message = f"{timestamp} - {class_name} spotted at {location} (confidence: {confidence:.2f})"
        
        # Log to file
        self.detection_logger.info(log_message)
        
        # Add to recent detections
        self.recent_detections.append({
            "timestamp": timestamp,
            "message": log_message,
            "detection": detection
        })
        
        # Trim recent detections if needed
        if len(self.recent_detections) > self.max_recent_items:
            self.recent_detections = self.recent_detections[-self.max_recent_items:]
    
    def log_alert(self, alert):
        """
        Log a security alert.
        
        Args:
            alert: Dict containing alert data
        """
        if not alert:
            return
        
        timestamp = alert.get("timestamp", "00:00:00")
        rule_name = alert.get("rule_name", "Unknown Rule")
        priority = alert.get("priority", "low")
        message = alert.get("message", "")
        
        # Set log level based on priority
        log_level = logging.INFO
        if priority == "high":
            log_level = logging.CRITICAL
        elif priority == "medium":
            log_level = logging.WARNING
        
        # Log to file
        self.alert_logger.log(log_level, message)
        
        # Add to recent alerts
        self.recent_alerts.append({
            "timestamp": timestamp,
            "message": message,
            "alert": alert
        })
        
        # Trim recent alerts if needed
        if len(self.recent_alerts) > self.max_recent_items:
            self.recent_alerts = self.recent_alerts[-self.max_recent_items:]
    
    def get_recent_detections(self, limit=10):
        """Get recent object detections."""
        return self.recent_detections[-limit:] if self.recent_detections else []
    
    def get_recent_alerts(self, limit=10):
        """Get recent security alerts."""
        return self.recent_alerts[-limit:] if self.recent_alerts else []
    
    def export_logs(self, output_file):
        """Export all logs to a JSON file."""
        data = {
            "detections": self.recent_detections,
            "alerts": self.recent_alerts,
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
"""

TELEMETRY_PROCESSOR_PY = """import json
from datetime import datetime

class TelemetryProcessor:
    def __init__(self, telemetry_file=None):
        self.telemetry_data = []
        if telemetry_file:
            self.load_telemetry(telemetry_file)
    
    def load_telemetry(self, telemetry_file):
        """Load telemetry data from a JSON file."""
        try:
            with open(telemetry_file, 'r') as f:
                self.telemetry_data = json.load(f)
            print(f"Loaded {len(self.telemetry_data)} telemetry records")
        except Exception as e:
            print(f"Error loading telemetry data: {e}")
            # Create sample data if file doesn't exist
            self.generate_sample_telemetry()
    
    def generate_sample_telemetry(self, num_records=100):
        """Generate sample telemetry data."""
        import random
        from datetime import datetime, timedelta
        
        self.telemetry_data = []
        locations = ["Gate", "Garage", "Backyard", "Perimeter", "Main Entrance"]
        start_time = datetime.now()
        
        for i in range(num_records):
            timestamp = (start_time + timedelta(seconds=i*5)).strftime("%H:%M:%S")
            self.telemetry_data.append({
                "timestamp": timestamp,
                "location": random.choice(locations),
                "altitude": round(random.uniform(2.0, 10.0), 2),
                "battery": random.randint(50, 100),
                "status": "monitoring"
            })
        
        print(f"Generated {len(self.telemetry_data)} sample telemetry records")
    
    def get_telemetry_at_time(self, timestamp):
        """Get telemetry data closest to the given timestamp."""
        if not self.telemetry_data:
            return None
        
        # Convert timestamp string to datetime for comparison
        if isinstance(timestamp, str):
            try:
                target_time = datetime.strptime(timestamp, "%H:%M:%S")
            except ValueError:
                print(f"Invalid timestamp format: {timestamp}")
                return None
        else:
            target_time = timestamp
        
        # Find closest telemetry entry
        closest_entry = None
        min_diff = float('inf')
        
        for entry in self.telemetry_data:
            entry_time = datetime.strptime(entry["timestamp"], "%H:%M:%S")
            time_diff = abs((target_time - entry_time).total_seconds())
            
            if time_diff < min_diff:
                min_diff = time_diff
                closest_entry = entry
        
        return closest_entry
    
    def save_telemetry(self, output_file):
        """Save telemetry data to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.telemetry_data, f, indent=2)
            print(f"Saved telemetry data to {output_file}")
        except Exception as e:
            print(f"Error saving telemetry data: {e}")
"""

VIDEO_PROCESSOR_PY = """import cv2
import time
from datetime import datetime

class VideoProcessor:
    def __init__(self, video_source=None):
        self.video_source = video_source
        self.cap = None
        self.frame_count = 0
        self.fps = 0
        
    def open_video(self, video_source=None):
        """Open a video file or camera stream."""
        if video_source:
            self.video_source = video_source
            
        if self.video_source is None:
            raise ValueError("No video source specified")
            
        try:
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                raise ValueError(f"Could not open video source: {self.video_source}")
                
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"Opened video source: {self.video_source}")
            print(f"  - Frames: {self.frame_count}")
            print(f"  - FPS: {self.fps}")
            return True
        except Exception as e:
            print(f"Error opening video source: {e}")
            return False
    
    def generate_frame_timestamp(self, frame_idx):
        """Generate a timestamp for a frame based on its index and FPS."""
        if self.fps == 0:
            return "00:00:00"
            
        seconds = frame_idx / self.fps
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def simulate_video_frames(self, num_frames=100):
        """Simulate video frames with text descriptions for testing."""
        simulated_frames = []
        objects = ["Blue Ford F150", "Red Sedan", "Person in black jacket", 
                  "White delivery truck", "Black SUV", "Person with backpack"]
        locations = ["gate", "driveway", "garage", "backyard", "front door", "perimeter fence"]
        
        for i in range(num_frames):
            timestamp = self.generate_frame_timestamp(i)
            
            # Create patterns in the simulated data
            if i % 20 < 5:  # Every 20 frames, show a vehicle for 5 frames
                obj = objects[0]  # Blue Ford F150
                location = locations[0]  # gate
            elif i % 30 > 25:  # Person appears occasionally
                obj = objects[2]  # Person in black jacket
                location = locations[4]  # front door
            elif i == 50:  # Special one-time event
                obj = objects[5]  # Person with backpack
                location = locations[5]  # perimeter fence
            else:
                # Random selection for variety
                import random
                obj_idx = random.randint(1, len(objects) - 2)
                loc_idx = random.randint(1, len(locations) - 2)
                obj = objects[obj_idx]
                location = locations[loc_idx]
            
            frame_desc = {
                "frame_idx": i,
                "timestamp": timestamp,
                "description": f"Frame {i}: {obj} at {location}"
            }
            simulated_frames.append(frame_desc)
        
        return simulated_frames
    
    def read_frame(self):
        """Read the next frame from the video source."""
        if self.cap is None or not self.cap.isOpened():
            return None, None
            
        ret, frame = self.cap.read()
        if not ret:
            return None, None
            
        timestamp = self.generate_frame_timestamp(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
        return frame, timestamp
    
    def release(self):
        """Release the video capture resource."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
"""

MAIN_PY = """import os
import time
import argparse
from datetime import datetime
import json
import cv2
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from config import SAMPLE_VIDEO, SAMPLE_TELEMETRY
from data_processor.video_processor import VideoProcessor
from data_processor.telemetry_processor import TelemetryProcessor
from analysis.object_detector import ObjectDetector
from analysis.context_analyzer import ContextAnalyzer
from analysis.rule_engine import RuleEngine
from storage.frame_indexer import FrameIndexer
from storage.event_logger import EventLogger

def simulate_drone_security_system(video_path=None, telemetry_path=None, output_dir=None, num_frames=100):
    """
    Run the drone security system simulation.
    
    Args:
        video_path: Path to the video file
        telemetry_path: Path to the telemetry data file
        output_dir: Directory to save output files
        num_frames: Number of frames to process in simulation mode
    """
    print("Starting Drone Security Analyst Agent...")
    
    # Initialize components
    video_processor = VideoProcessor(video_path)
    telemetry_processor = TelemetryProcessor(telemetry_path)
    object_detector = ObjectDetector()
    context_analyzer = ContextAnalyzer(telemetry_processor)
    rule_engine = RuleEngine()
    frame_indexer = FrameIndexer()
    event_logger = EventLogger()
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Check if we're using real video or simulation
    using_real_video = False
    if video_path and os.path.exists(video_path):
        print(f"Using video file: {video_path}")
        if video_processor.open_video():
            using_real_video = True
    
    if not using_real_video:
        print("Using simulated video frames")
        simulated_frames = video_processor.simulate_video_frames(num_frames)
    
    # Check telemetry data
    if not telemetry_processor.telemetry_data:
        print("No telemetry data found, generating sample data")
        telemetry_processor.generate_sample_telemetry(num_frames)
    
    # Process frames
    frame_count = 0
    processed_frames = []
    
    print("\\nProcessing frames:")
    
    if using_real_video:
        # Process real video
        while True:
            frame, timestamp = video_processor.read_frame()
            if frame is None:
                break
                
            frame_count += 1
            if frame_count % 10 == 0:
                print(f"Processing frame {frame_count}...")
            
            # Detect objects
            detections = object_detector.detect_objects(frame)
            
            # Create frame data
            frame_data = {
                "frame_idx": frame_count,
                "timestamp": timestamp,
                "description": f"Frame {frame_count} at {timestamp}"
            }
            
            # Analyze context
            context_data = context_analyzer.analyze_frame(frame_data, detections)
            
            # Evaluate security rules
            alerts = rule_engine.evaluate_frame(context_data)
            
            # Log events
            for detection in context_data.get("detections", []):
                event_logger.log_detection(detection)
            
            for alert in alerts:
                event_logger.log_alert(alert)
            
            # Index frame
            frame_indexer.index_frame(frame_data, context_data)
            
            # Index alerts
            for alert in alerts:
                frame_indexer.index_alert(alert)
            
            # Save processed frame if output directory specified
            if output_dir and frame_count % 10 == 0:
                annotated_frame = object_detector.draw_detections(frame, detections)
                frame_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
                cv2.imwrite(frame_path, annotated_frame)
            
            # Store frame data for the report
            frame_info = {
                **frame_data,
                "detections": [d.get("class_name") for d in detections],
                "alerts": [a.get("message") for a in alerts]
            }
            processed_frames.append(frame_info)
            
            # Pause briefly to simulate real-time processing
            time.sleep(0.01)
    else:
        # Process simulated frames
        for frame_data in simulated_frames:
            frame_count += 1
            
            # Create fake detections based on frame description
            desc = frame_data.get("description", "")
            fake_detections = []
            
            # Parse objects from the description
            if "Blue Ford F150" in desc:
                fake_detections.append({
                    "class_id": 7,
                    "class_name": "truck",
                    "confidence": 0.92,
                    "bbox": [100, 150, 300, 250]
                })
            elif "Red Sedan" in desc:
                fake_detections.append({
                    "class_id": 2,
                    "class_name": "car",
                    "confidence": 0.88,
                    "bbox": [200, 180, 350, 240]
                })
            elif "Person" in desc:
                fake_detections.append({
                    "class_id": 0,
                    "class_name": "person",
                    "confidence": 0.85,
                    "bbox": [250, 200, 300, 350]
                })
            elif "delivery truck" in desc:
                fake_detections.append({
                    "class_id": 7,
                    "class_name": "truck",
                    "confidence": 0.75,
                    "bbox": [150, 170, 300, 250]
                })
            
            # Analyze context
            context_data = context_analyzer.analyze_frame(frame_data, fake_detections)
            
            # Evaluate security rules
            alerts = rule_engine.evaluate_frame(context_data)
            
            # Log events
            for detection in context_data.get("detections", []):
                event_logger.log_detection(detection)
            
            for alert in alerts:
                event_logger.log_alert(alert)
            
            # Index frame
            frame_indexer.index_frame(frame_data, context_data)
            
            # Index alerts
            for alert in alerts:
                frame_indexer.index_alert(alert)
            
            # Store frame data for the report
            frame_info = {
                **frame_data,
                "detections": [d.get("class_name") for d in fake_detections],
                "alerts": [a.get("message") for a in alerts]
            }
            processed_frames.append(frame_info)
            
            # Display progress
            if frame_count % 10 == 0 or frame_count == 1 or frame_count == len(simulated_frames):
                print(f"Processed frame {frame_count}/{len(simulated_frames)}")
            
            # Pause briefly to simulate real-time processing
            time.sleep(0.01)
    
    # Clean up resources
    if using_real_video:
        video_processor.release()
    
    # Generate summary report
    summary = {
        "total_frames": frame_count,
        "recent_detections": event_logger.get_recent_detections(),
        "recent_alerts": event_logger.get_recent_alerts(),
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save summary if output directory specified
    if output_dir:
        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    # Print summary
    print("\\nDrone Security Analysis Summary:")
    print(f"Processed {frame_count} frames")
    print(f"Recent Detections: {len(event_logger.get_recent_detections())}")
    print(f"Recent Alerts: {len(event_logger.get_recent_alerts())}")
    
    if event_logger.recent_alerts:
        print("\\nRecent Alerts:")
        for alert in event_logger.get_recent_alerts(5):
            print(f"- {alert['message']}")
    
    # Example queries
    print("\\nExample Queries:")
    
    # Query all truck detections
    truck_frames = frame_indexer.query_frames_by_object("truck")
    print(f"Found {len(truck_frames)} frames with trucks")
    
    # Query all high-priority alerts
    high_alerts = frame_indexer.query_alerts(priority="high")
    print(f"Found {len(high_alerts)} high-priority alerts")
    
    print("\\nDrone Security Analysis Complete")
    
    return {
        "summary": summary,
        "processed_frames": processed_frames
    }

def main():
    parser = argparse.ArgumentParser(description="Drone Security Analyst Agent")
    parser.add_argument("--video", type=str, default=None, help="Path to video file")
    parser.add_argument("--telemetry", type=str, default=None, help="Path to telemetry data file")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--frames", type=int, default=100, help="Number of frames to process in simulation mode")
    
    args = parser.parse_args()
    
    # Use default paths if not specified
    video_path = args.video if args.video else SAMPLE_VIDEO
    telemetry_path = args.telemetry if args.telemetry else SAMPLE_TELEMETRY
    
    # Run the simulation
    simulate_drone_security_system(video_path, telemetry_path, args.output, args.frames)

if __name__ == "__main__":
    main()
"""

TEST_DRONE_AGENT_PY = """import unittest
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data_processor.video_processor import VideoProcessor
from data_processor.telemetry_processor import TelemetryProcessor
from analysis.object_detector import ObjectDetector
from analysis.context_analyzer import ContextAnalyzer
from analysis.rule_engine import RuleEngine
from storage.frame_indexer import FrameIndexer
from storage.event_logger import EventLogger

class TestDroneSecurityAgent(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create test data
        self.create_test_data()
        
        # Initialize components
        self.video_processor = VideoProcessor()
        self.telemetry_processor = TelemetryProcessor(self.telemetry_path)
        self.object_detector = ObjectDetector()
        self.context_analyzer = ContextAnalyzer(self.telemetry_processor)
        self.rule_engine = RuleEngine()
        self.frame_indexer = FrameIndexer(os.path.join(self.test_dir, "test.db"))
        self.event_logger = EventLogger(self.test_dir)
    
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
    
    def create_test_data(self):
        """Create test data files."""
        # Create sample telemetry data
        self.telemetry_path = os.path.join(self.test_dir, "test_telemetry.json")
        telemetry_data = [
            {
                "timestamp": "00:00:05",
                "location": "Gate",
                "altitude": 5.2,
                "battery": 98,
                "status": "monitoring"
            },
            {
                "timestamp": "00:00:10",
                "location": "Gate",
                "altitude": 5.1,
                "battery": 97,
                "status": "monitoring"
            }
        ]
        
        with open(self.telemetry_path, 'w') as f:
            json.dump(telemetry_data, f)
    
    def test_video_processor(self):
        """Test the video processor component."""
        # Test simulated frames generation
        frames = self.video_processor.simulate_video_frames(10)
        self.assertEqual(len(frames), 10)
        self.assertIn("timestamp", frames[0])
        self.assertIn("description", frames[0])
    
    def test_telemetry_processor(self):
        """Test the telemetry processor component."""
        # Test loading telemetry data
        self.assertEqual(len(self.telemetry_processor.telemetry_data), 2)
        
        # Test getting telemetry at time
        telemetry = self.telemetry_processor.get_telemetry_at_time("00:00:05")
        self.assertEqual(telemetry["location"], "Gate")
        self.assertEqual(telemetry["altitude"], 5.2)
    
    def test_object_detector(self):
        """Test the object detector component."""
        # Create a simple test image
        import numpy as np
        import cv2
        
        # Create a blank image with different colored regions to trigger detections
        test_image = np.zeros((300, 400, 3), dtype=np.uint8)
        # Blue region (top-left)
        test_image[0:100, 0:200, 0] = 200
        # Green region (top-right)
        test_image[0:100, 200:400, 1] = 200
        # Red region (bottom-left)
        test_image[200:300, 0:200, 2] = 200
        
        # Detect objects
        detections = self.object_detector.detect_objects(test_image)
        
        # Check if detections were made
        self.assertTrue(len(detections) > 0)
        
        # Verify detection format
        for detection in detections:
            self.assertIn("class_name", detection)
            self.assertIn("confidence", detection)
            self.assertIn("bbox", detection)
    
    def test_context_analyzer(self):
        """Test the context analyzer component."""
        # Create test frame data
        frame_data = {
            "frame_idx": 1,
            "timestamp": "00:00:05",
            "description": "Test frame"
        }
        
        # Create test detections
        detections = [
            {
                "class_id": 0,
                "class_name": "person",
                "confidence": 0.85,
                "bbox": [100, 150, 150, 250]
            }
        ]
        
        # Analyze context
        context_data = self.context_analyzer.analyze_frame(frame_data, detections)
        
        # Check context data
        self.assertEqual(context_data["location"], "Gate")
        self.assertEqual(len(context_data["detections"]), 1)
        self.assertEqual(context_data["detections"][0]["class_name"], "person")
        self.assertIn("description", context_data["detections"][0])
    
    def test_rule_engine(self):
        """Test the rule engine component."""
        # Create test context data with a person at night
        context_data = {
            "timestamp": "23:30:00",
            "location": "Gate",
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.85,
                    "bbox": [100, 150, 150, 250],
                    "timestamp": "23:30:00",
                    "location": "Gate",
                    "duration": 65  # seconds
                }
            ]
        }
        
        # Add to the object history to simulate duration
        self.rule_engine.object_history["person_100_150"] = {
            "class_name": "person",
            "location": "Gate",
            "first_seen": "23:29:00",
            "last_seen": "23:30:00",
            "duration": 65
        }
        
        # Evaluate rules
        alerts = self.rule_engine.evaluate_frame(context_data)
        
        # There should be at least one alert for "Person Loitering"
        self.assertTrue(len(alerts) > 0)
        alert_messages = [alert["rule_name"] for alert in alerts]
        self.assertIn("Person Loitering", alert_messages)
    
    def test_frame_indexer(self):
        """Test the frame indexer component."""
        # Create test frame data
        frame_data = {
            "frame_idx": 1,
            "timestamp": "00:00:05",
            "description": "Test frame"
        }
        
        # Create test context data
        context_data = {
            "timestamp": "00:00:05",
            "location": "Gate",
            "detections": [
                {
                    "class_name": "car",
                    "confidence": 0.92,
                    "bbox": [100, 150, 300, 250],
                    "timestamp": "00:00:05",
                    "location": "Gate",
                    "description": "Car detected at Gate, 00:00:05"
                }
            ],
            "telemetry": {
                "altitude": 5.2,
                "battery": 98,
                "status": "monitoring"
            }
        }
        
        # Index frame
        frame_id = self.frame_indexer.index_frame(frame_data, context_data)
        self.assertTrue(frame_id > 0)
        
        # Query frames by object
        car_frames = self.frame_indexer.query_frames_by_object("car")
        self.assertEqual(len(car_frames), 1)
        
        # Create and index an alert
        alert = {
            "timestamp": "00:00:05",
            "rule_name": "Vehicle at Restricted Area",
            "priority": "medium",
            "message": "ALERT: car detected in restricted area (Gate), 00:00:05",
            "location": "Gate"
        }
        
        alert_id = self.frame_indexer.index_alert(alert)
        self.assertTrue(alert_id > 0)
        
        # Query alerts
        medium_alerts = self.frame_indexer.query_alerts(priority="medium")
        self.assertEqual(len(medium_alerts), 1)
    
    def test_event_logger(self):
        """Test the event logger component."""
        # Create test detection
        detection = {
            "class_name": "car",
            "confidence": 0.92,
            "location": "Gate",
            "timestamp": "00:00:05"
        }
        
        # Log detection
        self.event_logger.log_detection(detection)
        
        # Check recent detections
        recent_detections = self.event_logger.get_recent_detections()
        self.assertEqual(len(recent_detections), 1)
        
        # Create test alert
        alert = {
            "timestamp": "00:00:05",
            "rule_name": "Vehicle at Restricted Area",
            "priority": "high",
            "message": "ALERT: car detected in restricted area (Gate), 00:00:05",
            "location": "Gate"
        }
        
        # Log alert
        self.event_logger.log_alert(alert)
        
        # Check recent alerts
        recent_alerts = self.event_logger.get_recent_alerts()
        self.assertEqual(len(recent_alerts), 1)

if __name__ == "__main__":
    unittest.main()
"""

DEMO_PY = """import os
import sys
import time
import json
from datetime import datetime
import argparse

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from data_processor.video_processor import VideoProcessor
from data_processor.telemetry_processor import TelemetryProcessor
from analysis.object_detector import ObjectDetector
from analysis.context_analyzer import ContextAnalyzer
from analysis.rule_engine import RuleEngine
from storage.frame_indexer import FrameIndexer
from storage.event_logger import EventLogger

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the demo header."""
    print("=" * 80)
    print("                   DRONE SECURITY ANALYST AGENT DEMO                    ")
    print("=" * 80)
    print("This demo shows the capabilities of the Drone Security Analyst Agent.")
    print("It simulates processing video frames and generates security alerts.")
    print("=" * 80)
    print()

def print_menu():
    """Print the main menu."""
    print("\\nMAIN MENU:")
    print("1. Run simulation")
    print("2. View recent detections")
    print("3. View recent alerts")
    print("4. Query frames by object type")
    print("5. Query frames by time range")
    print("6. Query alerts by priority")
    print("7. Exit")
    print()

def run_simulation(num_frames=50):
    """Run the drone security system simulation."""
    clear_screen()
    print_header()
    print(f"Running simulation with {num_frames} frames...\\n")
    
    # Initialize components
    video_processor = VideoProcessor()
    telemetry_processor = TelemetryProcessor()
    telemetry_processor.generate_sample_telemetry(num_frames)
    object_detector = ObjectDetector()
    context_analyzer = ContextAnalyzer(telemetry_processor)
    rule_engine = RuleEngine()
    frame_indexer = FrameIndexer()
    event_logger = EventLogger()
    
    # Simulate video frames
    simulated_frames = video_processor.simulate_video_frames(num_frames)
    
    # Process frames
    frame_count = 0
    alert_count = 0
    detection_count = 0
    
    print("Processing frames:")
    print("-" * 40)
    
    for frame_data in simulated_frames:
        frame_count += 1
        
        # Create fake detections based on frame description
        desc = frame_data.get("description", "")
        fake_detections = []
        
        # Parse objects from the description
        if "Blue Ford F150" in desc:
            fake_detections.append({
                "class_id": 7,
                "class_name": "truck",
                "confidence": 0.92,
                "bbox": [100, 150, 300, 250]
            })
        elif "Red Sedan" in desc:
            fake_detections.append({
                "class_id": 2,
                "class_name": "car",
                "confidence": 0.88,
                "bbox": [200, 180, 350, 240]
            })
        elif "Person" in desc:
            fake_detections.append({
                "class_id": 0,
                "class_name": "person",
                "confidence": 0.85,
                "bbox": [250, 200, 300, 350]
            })
        elif "delivery truck" in desc:
            fake_detections.append({
                "class_id": 7,
                "class_name": "truck",
                "confidence": 0.75,
                "bbox": [150, 170, 300, 250]
            })
        
        # Analyze context
        context_data = context_analyzer.analyze_frame(frame_data, fake_detections)
        
        # Evaluate security rules
        alerts = rule_engine.evaluate_frame(context_data)
        
        # Log events
        for detection in context_data.get("detections", []):
            event_logger.log_detection(detection)
            detection_count += 1
        
        for alert in alerts:
            event_logger.log_alert(alert)
            alert_count += 1
        
        # Index frame
        frame_indexer.index_frame(frame_data, context_data)
        
        # Index alerts
        for alert in alerts:
            frame_indexer.index_alert(alert)
        
        # Display progress
        if frame_count % 5 == 0 or frame_count == 1 or frame_count == len(simulated_frames):
            print(f"Frame {frame_count}/{len(simulated_frames)}: ", end="")
            if fake_detections:
                objects = [d["class_name"] for d in fake_detections]
                print(f"Detected {', '.join(objects)}")
            else:
                print("No objects detected")
        
        # If there are alerts, display them
        for alert in alerts:
            print(f"  ALERT: {alert['message']}")
        
        # Pause briefly to simulate real-time processing
        time.sleep(0.1)
    
    print("\\nSimulation complete!")
    print(f"Processed {frame_count} frames")
    print(f"Detected {detection_count} objects")
    print(f"Generated {alert_count} security alerts")
    
    return {
        "frame_indexer": frame_indexer,
        "event_logger": event_logger
    }

def view_recent_detections(event_logger, limit=10):
    """View the most recent object detections."""
    clear_screen()
    print_header()
    print("RECENT OBJECT DETECTIONS:")
    print("-" * 80)
    
    detections = event_logger.get_recent_detections(limit)
    
    if not detections:
        print("No detections found.")
    else:
        for i, detection in enumerate(detections):
            print(f"{i+1}. {detection['message']}")
    
    input("\\nPress Enter to continue...")

def view_recent_alerts(event_logger, limit=10):
    """View the most recent security alerts."""
    clear_screen()
    print_header()
    print("RECENT SECURITY ALERTS:")
    print("-" * 80)
    
    alerts = event_logger.get_recent_alerts(limit)
    
    if not alerts:
        print("No alerts found.")
    else:
        for i, alert in enumerate(alerts):
            print(f"{i+1}. {alert['message']}")
    
    input("\\nPress Enter to continue...")

def query_frames_by_object(frame_indexer):
    """Query frames containing a specific object type."""
    clear_screen()
    print_header()
    print("QUERY FRAMES BY OBJECT TYPE:")
    print("-" * 80)
    
    print("Object types: person, car, truck, motorcycle, bicycle")
    object_type = input("Enter object type to search for: ").strip().lower()
    
    if not object_type:
        return
    
    frames = frame_indexer.query_frames_by_object(object_type)
    
    print(f"\\nFound {len(frames)} frames containing '{object_type}':")
    print("-" * 80)
    
    if not frames:
        print("No matching frames found.")
    else:
        for i, frame in enumerate(frames[:10]):  # Show max 10 results
            print(f"{i+1}. {frame['timestamp']} at {frame['location']}: {frame['description']}")
        
        if len(frames) > 10:
            print(f"... and {len(frames) - 10} more results.")
    
    input("\\nPress Enter to continue...")

def query_frames_by_time(frame_indexer):
    """Query frames within a time range."""
    clear_screen()
    print_header()
    print("QUERY FRAMES BY TIME RANGE:")
    print("-" * 80)
    
    print("Enter time range in format HH:MM:SS")
    start_time = input("Start time: ").strip()
    end_time = input("End time: ").strip()
    
    if not start_time or not end_time:
        return
    
    try:
        frames = frame_indexer.query_frames_by_time(start_time, end_time)
        
        print(f"\\nFound {len(frames)} frames between {start_time} and {end_time}:")
        print("-" * 80)
        
        if not frames:
            print("No matching frames found.")
        else:
            for i, frame in enumerate(frames[:10]):  # Show max 10 results
                objects = frame['objects'] if frame['objects'] else "No objects"
                print(f"{i+1}. {frame['timestamp']} at {frame['location']}: {objects}")
            
            if len(frames) > 10:
                print(f"... and {len(frames) - 10} more results.")
    except Exception as e:
        print(f"Error: {e}")
    
    input("\\nPress Enter to continue...")

def query_alerts_by_priority(frame_indexer):
    """Query alerts by priority level."""
    clear_screen()
    print_header()
    print("QUERY ALERTS BY PRIORITY:")
    print("-" * 80)
    
    print("Priority levels: high, medium, low")
    priority = input("Enter priority level to search for: ").strip().lower()
    
    if priority not in ["high", "medium", "low"]:
        print("Invalid priority level.")
        input("\\nPress Enter to continue...")
        return
    
    alerts = frame_indexer.query_alerts(priority=priority)
    
    print(f"\\nFound {len(alerts)} {priority}-priority alerts:")
    print("-" * 80)
    
    if not alerts:
        print("No matching alerts found.")
    else:
        for i, alert in enumerate(alerts):
            print(f"{i+1}. {alert['timestamp']} - {alert['message']}")
    
    input("\\nPress Enter to continue...")

def main():
    """Main function to run the interactive demo."""
    parser = argparse.ArgumentParser(description="Drone Security Analyst Agent Demo")
    parser.add_argument("--frames", type=int, default=50, help="Number of frames to process in simulation")
    
    args = parser.parse_args()
    
    # Run the initial simulation
    components = run_simulation(args.frames)
    frame_indexer = components["frame_indexer"]
    event_logger = components["event_logger"]
    
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            components = run_simulation(args.frames)
            frame_indexer = components["frame_indexer"]
            event_logger = components["event_logger"]
        elif choice == "2":
            view_recent_detections(event_logger)
        elif choice == "3":
            view_recent_alerts(event_logger)
        elif choice == "4":
            query_frames_by_object(frame_indexer)
        elif choice == "5":
            query_frames_by_time(frame_indexer)
        elif choice == "6":
            query_alerts_by_priority(frame_indexer)
        elif choice == "7":
            clear_screen()
            print("Thank you for using the Drone Security Analyst Agent Demo!")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()
import os
import json

# Define the file paths
files = {
    "src/config.py": CONFIG_PY,
    "src/analysis/object_detector.py": OBJECT_DETECTOR_PY,
    "src/analysis/context_analyzer.py": CONTEXT_ANALYZER_PY,
    "src/analysis/rule_engine.py": RULE_ENGINE_PY,
    "src/storage/frame_indexer.py": FRAME_INDEXER_PY,
    "src/storage/event_logger.py": EVENT_LOGGER_PY,
    "src/data_processor/telemetry_processor.py": TELEMETRY_PROCESSOR_PY,
    "src/data_processor/video_processor.py": VIDEO_PROCESSOR_PY,
    "src/main.py": MAIN_PY,
    "src/demo.py": DEMO_PY,
    "tests/test_drone_agent.py": TEST_DRONE_AGENT_PY
}

# Create __init__.py files for each directory
init_dirs = [
    "src",
    "src/analysis",
    "src/storage",
    "src/data_processor",
    "tests"
]

# Create the files
for file_path, content in files.items():
    write_file(file_path, content)

# Create __init__.py files
for dir_path in init_dirs:
    init_path = os.path.join(dir_path, "__init__.py")
    write_file(init_path, "# This file marks the directory as a Python package.\n")

# Create required directories
ensure_dir("data")
ensure_dir("logs")
ensure_dir("output")

print("\nAll files have been fixed!")
print("You can now run your project with one of the following commands:")
print("\n1. python src/main.py - Run the main application")
print("2. python src/demo.py - Run the interactive demo")
print("3. python -m unittest tests/test_drone_agent.py - Run the tests")

            "