import unittest
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