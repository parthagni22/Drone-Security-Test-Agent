import sqlite3
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
