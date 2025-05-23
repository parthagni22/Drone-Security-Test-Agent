import cv2
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