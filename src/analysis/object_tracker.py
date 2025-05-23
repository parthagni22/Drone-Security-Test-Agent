import numpy as np
from scipy.optimize import linear_sum_assignment
import cv2
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import MAX_TRACKING_AGE, MIN_DETECTION_PERSISTENCE, TRACKING_OVERLAP_THRESHOLD

class TrackedObject:
    """Represents a tracked object with its history and metadata."""
    
    def __init__(self, detection, track_id):
        self.track_id = track_id
        self.class_name = detection["class_name"]
        self.detections = [detection]
        self.bbox_history = [detection["bbox"]]
        self.confidence_history = [detection["confidence"]]
        self.last_seen = 0
        self.age = 0
        self.consecutive_misses = 0
        self.is_confirmed = False
        self.first_seen = datetime.now()
        self.velocity = [0, 0]  # x, y velocity in pixels per frame
    
    def update(self, detection):
        """Update the tracked object with a new detection."""
        self.detections.append(detection)
        self.bbox_history.append(detection["bbox"])
        self.confidence_history.append(detection["confidence"])
        self.last_seen = 0
        self.consecutive_misses = 0
        
        # Update velocity if we have enough history
        if len(self.bbox_history) >= 2:
            prev_box = self.bbox_history[-2]
            curr_box = self.bbox_history[-1]
            prev_center = [(prev_box[0] + prev_box[2])/2, (prev_box[1] + prev_box[3])/2]
            curr_center = [(curr_box[0] + curr_box[2])/2, (curr_box[1] + curr_box[3])/2]
            self.velocity = [
                curr_center[0] - prev_center[0],
                curr_center[1] - prev_center[1]
            ]
        
        # Check if object should be confirmed
        if len(self.detections) >= MIN_DETECTION_PERSISTENCE:
            self.is_confirmed = True
    
    def predict(self):
        """Predict next position based on velocity."""
        if not self.bbox_history:
            return None
        
        last_bbox = self.bbox_history[-1]
        width = last_bbox[2] - last_bbox[0]
        height = last_bbox[3] - last_bbox[1]
        
        # Predict new center
        center_x = (last_bbox[0] + last_bbox[2])/2 + self.velocity[0]
        center_y = (last_bbox[1] + last_bbox[3])/2 + self.velocity[1]
        
        # Return predicted bbox
        return [
            int(center_x - width/2),
            int(center_y - height/2),
            int(center_x + width/2),
            int(center_y + height/2)
        ]

class ObjectTracker:
    """Tracks objects across frames using IoU matching and motion prediction."""
    
    def __init__(self):
        self.tracked_objects = []
        self.next_track_id = 0
    
    def update(self, detections):
        """Update tracks with new detections."""
        # Predict new locations for existing tracks
        predicted_boxes = []
        valid_tracks = []
        
        for track in self.tracked_objects:
            predicted_box = track.predict()
            if predicted_box is not None:
                predicted_boxes.append(predicted_box)
                valid_tracks.append(track)
        
        # Match detections to existing tracks
        if predicted_boxes and detections:
            # Calculate IoU matrix
            iou_matrix = np.zeros((len(predicted_boxes), len(detections)))
            for i, pred_box in enumerate(predicted_boxes):
                for j, det in enumerate(detections):
                    iou_matrix[i, j] = self._calculate_iou(pred_box, det["bbox"])
            
            # Hungarian algorithm for optimal assignment
            track_indices, det_indices = linear_sum_assignment(-iou_matrix)
            
            # Update matched tracks
            for track_idx, det_idx in zip(track_indices, det_indices):
                if iou_matrix[track_idx, det_idx] >= TRACKING_OVERLAP_THRESHOLD:
                    valid_tracks[track_idx].update(detections[det_idx])
                    detections[det_idx]["track_id"] = valid_tracks[track_idx].track_id
            
            # Find unmatched detections
            matched_det_indices = set(det_indices[iou_matrix[track_indices, det_indices] >= TRACKING_OVERLAP_THRESHOLD])
            unmatched_detections = [det for i, det in enumerate(detections) if i not in matched_det_indices]
        else:
            unmatched_detections = detections
        
        # Create new tracks for unmatched detections
        for detection in unmatched_detections:
            new_track = TrackedObject(detection, self.next_track_id)
            self.tracked_objects.append(new_track)
            detection["track_id"] = self.next_track_id
            self.next_track_id += 1
        
        # Update track ages and remove old tracks
        self._update_track_ages()
        
        # Return updated detections with tracking info
        return detections
    
    def _calculate_iou(self, box1, box2):
        """Calculate Intersection over Union between two boxes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def _update_track_ages(self):
        """Update track ages and remove old tracks."""
        current_tracks = []
        for track in self.tracked_objects:
            track.age += 1
            track.last_seen += 1
            track.consecutive_misses = track.last_seen
            
            # Keep track if it's confirmed or young enough
            if track.is_confirmed or track.age < MAX_TRACKING_AGE:
                current_tracks.append(track)
        
        self.tracked_objects = current_tracks
    
    def get_track_info(self, track_id):
        """Get information about a specific track."""
        for track in self.tracked_objects:
            if track.track_id == track_id:
                return {
                    "track_id": track.track_id,
                    "class_name": track.class_name,
                    "age": track.age,
                    "consecutive_misses": track.consecutive_misses,
                    "is_confirmed": track.is_confirmed,
                    "first_seen": track.first_seen,
                    "detection_count": len(track.detections),
                    "average_confidence": np.mean(track.confidence_history),
                    "velocity": track.velocity
                }
        return None 