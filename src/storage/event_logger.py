import logging
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