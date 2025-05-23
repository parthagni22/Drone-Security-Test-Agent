from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Context-aware alert rules
IMPROVED_ALERT_RULES = [
    {
        "name": "Unauthorized Person in Secure Area",
        "condition": {
            "object_type": "person",
            "location_keywords": ["Security_Zone", "Restricted", "Private"],
            "time_range": {"start": "22:00", "end": "06:00"}
        },
        "priority": "high"
    },
    {
        "name": "Vehicle Traffic Monitoring",
        "condition": {
            "object_type": ["car", "truck"],
            "location_keywords": ["Highway", "Road", "Traffic"],
            "confidence_threshold": 0.7
        },
        "priority": "low",
        "description": "Normal vehicle traffic detected"
    },
    {
        "name": "Heavy Vehicle Alert",
        "condition": {
            "object_type": "truck",
            "confidence_threshold": 0.8,
            "location_keywords": ["Security", "Restricted", "Private"]
        },
        "priority": "medium"
    },
    {
        "name": "Person in Vehicle Area",
        "condition": {
            "object_type": "person",
            "location_keywords": ["Highway", "Road", "Traffic"],
            "confidence_threshold": 0.8
        },
        "priority": "medium",
        "description": "Person detected in vehicle traffic area"
    },
    {
        "name": "High Activity Zone",
        "condition": {
            "object_type": ["person", "car", "truck"],
            "count": 3,
            "time_window": 300
        },
        "priority": "low",
        "description": "High activity detected in monitoring area"
    }
]

class RuleEngine:
    """Enhanced rule engine with context-aware alert generation."""
    
    def __init__(self):
        self.rules = IMPROVED_ALERT_RULES
        self.frame_history = []  # Simple frame-based tracking
        self.detection_counts = {}
    
    def evaluate_frame(self, context_data):
        """
        Evaluate rules with improved context awareness.
        """
        if not context_data or "detections" not in context_data:
            return []
            
        timestamp = context_data.get("timestamp", "00:00:00")
        location = context_data.get("location", "Unknown")
        detections = context_data.get("detections", [])
        
        # Update tracking
        self._update_tracking(detections, timestamp, location)
        
        # Evaluate rules
        triggered_alerts = []
        
        for rule in self.rules:
            alerts = self._evaluate_rule(rule, detections, timestamp, location)
            triggered_alerts.extend(alerts)
        
        return triggered_alerts
    
    def _update_tracking(self, detections, timestamp, location):
        """Simple tracking update."""
        frame_data = {
            "timestamp": timestamp,
            "location": location,
            "detection_count": len(detections),
            "objects": [d["class_name"] for d in detections]
        }
        
        self.frame_history.append(frame_data)
        
        # Keep only recent history
        if len(self.frame_history) > 100:
            self.frame_history = self.frame_history[-100:]
        
        # Update detection counts
        for detection in detections:
            obj_type = detection["class_name"]
            if obj_type not in self.detection_counts:
                self.detection_counts[obj_type] = 0
            self.detection_counts[obj_type] += 1
    
    def _evaluate_rule(self, rule, detections, timestamp, location):
        """Evaluate a single rule with context awareness."""
        alerts = []
        rule_name = rule.get("name", "Unnamed Rule")
        priority = rule.get("priority", "low")
        condition = rule.get("condition", {})
        description = rule.get("description", f"{rule_name} triggered")
        
        # Parse time
        try:
            current_time = datetime.strptime(timestamp, "%H:%M:%S")
            current_hour = current_time.hour
        except:
            current_hour = 12  # Default to noon
        
        # Check time range if specified
        time_range = condition.get("time_range")
        if time_range:
            start_hour = int(time_range["start"].split(":")[0])
            end_hour = int(time_range["end"].split(":")[0])
            
            if start_hour > end_hour:  # Overnight range
                time_match = current_hour >= start_hour or current_hour < end_hour
            else:
                time_match = start_hour <= current_hour < end_hour
            
            if not time_match:
                return []
        
        # Check location keywords
        location_keywords = condition.get("location_keywords", [])
        if location_keywords:
            location_match = any(keyword.lower() in location.lower() for keyword in location_keywords)
            if not location_match:
                return []
        
        # Check object types
        object_type = condition.get("object_type")
        if isinstance(object_type, str):
            object_types = [object_type]
        else:
            object_types = object_type or []
        
        # Find matching detections
        matching_objects = []
        for detection in detections:
            if detection["class_name"] in object_types:
                confidence_threshold = condition.get("confidence_threshold", 0.0)
                if detection.get("confidence", 0) >= confidence_threshold:
                    matching_objects.append(detection)
        
        # Check count condition
        min_count = condition.get("count", 1)
        if len(matching_objects) < min_count:
            return []
        
        # Generate contextual alert message
        if matching_objects:
            object_names = [obj["class_name"] for obj in matching_objects]
            object_summary = ", ".join(set(object_names))
            
            # Create context-aware message
            if "Highway" in location or "Road" in location or "Traffic" in location:
                if priority == "low":
                    message = f"Traffic Monitor: {len(matching_objects)} {object_summary} detected on {location}"
                else:
                    message = f"ALERT: {description} - {object_summary} at {location}"
            else:
                message = f"ALERT: {description} - {object_summary} detected at {location}"
            
            alert = {
                "timestamp": timestamp,
                "rule_name": rule_name,
                "priority": priority,
                "message": message,
                "objects": object_names,
                "location": location,
                "detection_count": len(matching_objects)
            }
            alerts.append(alert)
        
        return alerts
    
    def get_detection_summary(self):
        """Get summary of detected objects."""
        return {
            "total_frames": len(self.frame_history),
            "detection_counts": self.detection_counts,
            "recent_activity": self.frame_history[-10:] if self.frame_history else []
        }
