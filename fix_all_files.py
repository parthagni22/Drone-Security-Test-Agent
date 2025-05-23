#!/usr/bin/env python3
"""
Complete fix script for the Drone Security Analyst Agent repository.
This script implements all missing classes and fixes import errors.
Run this script from the root directory of your project.
"""

import os

def write_file(file_path, content):
    """Write content to a file, creating directories if needed."""
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Fixed file: {file_path}")

# Fix src/analysis/context_analyzer.py
CONTEXT_ANALYZER_PY = """from datetime import datetime, timedelta
import os
import sys

class ContextAnalyzer:
    \"\"\"Analyzes object detections in the context of telemetry data and time.\"\"\"
    
    def __init__(self, telemetry_processor):
        self.telemetry_processor = telemetry_processor
        self.object_history = {}  # Track objects over time
        self.current_context = {}  # Current analysis context
    
    def analyze_frame(self, frame_data, detections):
        \"\"\"
        Analyze detected objects in the context of the current frame.
        
        Args:
            frame_data: Dict containing frame metadata (timestamp, etc.)
            detections: List of object detections from the object detector
            
        Returns:
            Dict containing contextualized detection data
        \"\"\"
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
        \"\"\"Generate a human-readable description of the detection.\"\"\"
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
        \"\"\"Remove old entries from object history.\"\"\"
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

# Fix src/analysis/rule_engine.py
RULE_ENGINE_PY = """from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import ALERT_RULES

class RuleEngine:
    \"\"\"Evaluates security rules against detected objects and generates alerts.\"\"\"
    
    def __init__(self):
        self.rules = ALERT_RULES
        self.object_history = {}  # Track objects over time for duration-based rules
    
    def evaluate_frame(self, context_data):
        \"\"\"
        Evaluate all rules against the current frame context.
        
        Args:
            context_data: Dict containing contextualized detection data
            
        Returns:
            List of triggered alerts
        \"\"\"
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
        \"\"\"Update the object history with new detections.\"\"\"
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
        \"\"\"Remove old entries from object history.\"\"\"
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
        \"\"\"Evaluate a single rule against the current context.\"\"\"
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
        \"\"\"Generate a human-readable alert message.\"\"\"
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

# Fix src/storage/frame_indexer.py
FRAME_INDEXER_PY = """import sqlite3
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_PATH

class FrameIndexer:
    \"\"\"Indexes video frames with metadata for later querying.\"\"\"
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_database()
    
    def _create_database(self):
        \"\"\"Create the database schema if it doesn't exist.\"\"\"
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
        \"\"\"
        Index a frame with its context and detection data.
        
        Args:
            frame_data: Dict containing frame metadata
            context_data: Dict containing contextualized detection data
        
        Returns:
            frame_id: ID of the indexed frame
        \"\"\"
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
        \"\"\"
        Index an alert.
        
        Args:
            alert: Dict containing alert data
        
        Returns:
            alert_id: ID of the indexed alert
        \"\"\"
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
        \"\"\"
        Query frames that contain a specific object class.
        
        Args:
            object_class: Object class name to search for
            
        Returns:
            List of matching frames with object data
        \"\"\"
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
        \"\"\"
        Query frames within a time range.
        
        Args:
            start_time: Start time (HH:MM:SS)
            end_time: End time (HH:MM:SS)
            
        Returns:
            List of matching frames
        \"\"\"
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
        \"\"\"
        Query alerts with optional filters.
        
        Args:
            priority: Filter by priority (high, medium, low)
            start_time: Start time (HH:MM:SS)
            end_time: End time (HH:MM:SS)
            
        Returns:
            List of matching alerts
        \"\"\"
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

# Fix src/storage/event_logger.py
EVENT_LOGGER_PY = """import logging
import os
from pathlib import Path
import json
from datetime import datetime

class EventLogger:
    \"\"\"Logs security events and object detections.\"\"\"
    
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
        \"\"\"Set up logging handlers.\"\"\"
        # Detection logger
        self.detection_logger = logging.getLogger("detection_logger")
        self.detection_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.detection_logger.handlers.clear()
        
        detection_handler = logging.FileHandler(self.detection_log_path)
        detection_formatter = logging.Formatter('%(asctime)s - %(message)s')
        detection_handler.setFormatter(detection_formatter)
        self.detection_logger.addHandler(detection_handler)
        
        # Alert logger
        self.alert_logger = logging.getLogger("alert_logger")
        self.alert_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.alert_logger.handlers.clear()
        
        alert_handler = logging.FileHandler(self.alert_log_path)
        alert_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        alert_handler.setFormatter(alert_formatter)
        self.alert_logger.addHandler(alert_handler)
    
    def log_detection(self, detection):
        \"\"\"
        Log an object detection.
        
        Args:
            detection: Dict containing detection data
        \"\"\"
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
        \"\"\"
        Log a security alert.
        
        Args:
            alert: Dict containing alert data
        \"\"\"
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
        \"\"\"Get recent object detections.\"\"\"
        return self.recent_detections[-limit:] if self.recent_detections else []
    
    def get_recent_alerts(self, limit=10):
        \"\"\"Get recent security alerts.\"\"\"
        return self.recent_alerts[-limit:] if self.recent_alerts else []
    
    def export_logs(self, output_file):
        \"\"\"Export all logs to a JSON file.\"\"\"
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

# Fix src/alert/alert_generator.py
ALERT_GENERATOR_PY = """import json
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AlertGenerator:
    \"\"\"Generates and manages security alerts.\"\"\"
    
    def __init__(self):
        self.active_alerts = []
        self.alert_history = []
        self.notification_callbacks = []
    
    def generate_alert(self, alert_data):
        \"\"\"
        Generate a new security alert.
        
        Args:
            alert_data: Dict containing alert information
            
        Returns:
            Dict: Generated alert with additional metadata
        \"\"\"
        if not alert_data:
            return None
        
        # Add metadata to the alert
        enhanced_alert = {
            **alert_data,
            "alert_id": self._generate_alert_id(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active",
            "acknowledged": False
        }
        
        # Add to active alerts
        self.active_alerts.append(enhanced_alert)
        
        # Add to history
        self.alert_history.append(enhanced_alert)
        
        # Trigger notifications
        self._trigger_notifications(enhanced_alert)
        
        return enhanced_alert
    
    def acknowledge_alert(self, alert_id):
        \"\"\"Mark an alert as acknowledged.\"\"\"
        for alert in self.active_alerts:
            if alert.get("alert_id") == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
        return False
    
    def dismiss_alert(self, alert_id):
        \"\"\"Dismiss an active alert.\"\"\"
        for i, alert in enumerate(self.active_alerts):
            if alert.get("alert_id") == alert_id:
                alert["status"] = "dismissed"
                alert["dismissed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.active_alerts.pop(i)
                return True
        return False
    
    def get_active_alerts(self, priority=None):
        \"\"\"Get currently active alerts, optionally filtered by priority.\"\"\"
        if priority:
            return [alert for alert in self.active_alerts if alert.get("priority") == priority]
        return self.active_alerts.copy()
    
    def get_alert_history(self, limit=100):
        \"\"\"Get alert history.\"\"\"
        return self.alert_history[-limit:] if self.alert_history else []
    
    def add_notification_callback(self, callback):
        \"\"\"Add a callback function to be called when alerts are generated.\"\"\"
        if callable(callback):
            self.notification_callbacks.append(callback)
    
    def _generate_alert_id(self):
        \"\"\"Generate a unique alert ID.\"\"\"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import random
        suffix = random.randint(1000, 9999)
        return f"ALERT_{timestamp}_{suffix}"
    
    def _trigger_notifications(self, alert):
        \"\"\"Trigger all registered notification callbacks.\"\"\"
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Error in notification callback: {e}")
    
    def export_alerts(self, output_file):
        \"\"\"Export all alerts to a JSON file.\"\"\"
        data = {
            "active_alerts": self.active_alerts,
            "alert_history": self.alert_history,
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting alerts: {e}")
            return False
"""

def main():
    print("Fixing Drone Security Analyst Agent repository...")
    
    # Write all the fixed files
    files_to_fix = {
        "src/analysis/context_analyzer.py": CONTEXT_ANALYZER_PY,
        "src/analysis/rule_engine.py": RULE_ENGINE_PY,
        "src/storage/frame_indexer.py": FRAME_INDEXER_PY,
        "src/storage/event_logger.py": EVENT_LOGGER_PY,
        "src/alert/alert_generator.py": ALERT_GENERATOR_PY,
    }
    
    for file_path, content in files_to_fix.items():
        write_file(file_path, content)
    
    # Create necessary directories
    directories_to_create = ["logs", "output"]
    for directory in directories_to_create:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    print("\n" + "="*60)
    print("✅ Repository fixes completed successfully!")
    print("="*60)
    print("\nFixed issues:")
    print("- Implemented missing ContextAnalyzer class")
    print("- Implemented missing RuleEngine class")  
    print("- Implemented missing FrameIndexer class")
    print("- Implemented missing EventLogger class")
    print("- Implemented missing AlertGenerator class")
    print("- Fixed import path issues")
    print("- Created necessary directories")
    print("\nYou can now run:")
    print("1. python src/main.py - Run the main application")
    print("2. python src/demo.py - Run the interactive demo")
    print("3. python -m unittest tests/test_drone_agent.py - Run tests")

if __name__ == "__main__":
    main()