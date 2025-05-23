from datetime import datetime
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
    
    def _parse_timestamp(self, timestamp):
        """Parse timestamp string to datetime object."""
        if isinstance(timestamp, str):
            try:
                return datetime.strptime(timestamp, "%H:%M:%S")
            except ValueError:
                return datetime.strptime("00:00:00", "%H:%M:%S")
        return timestamp
    
    def _update_history(self, detections, timestamp):
        """Update the object history with new detections."""
        current_time = self._parse_timestamp(timestamp)
        
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
                first_seen = self.object_history[obj_id]["first_seen"]
                if isinstance(first_seen, str):
                    first_seen = self._parse_timestamp(first_seen)
                duration = (current_time - first_seen).total_seconds()
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
                
            last_seen = data["last_seen"]
            if isinstance(last_seen, str):
                last_seen = self._parse_timestamp(last_seen)
                
            age = (current_time - last_seen).total_seconds()
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
        current_time = self._parse_timestamp(timestamp)
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
