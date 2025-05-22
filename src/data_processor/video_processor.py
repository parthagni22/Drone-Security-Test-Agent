# Video processor

import cv2
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
