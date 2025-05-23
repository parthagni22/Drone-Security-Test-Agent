from datetime import datetime, timedelta
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