import os
import time
import argparse
from datetime import datetime
import json
import cv2
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from config import SAMPLE_VIDEO, SAMPLE_TELEMETRY
from data_processor.video_processor import VideoProcessor
from data_processor.telemetry_processor import TelemetryProcessor
from analysis.object_detector import ObjectDetector
from analysis.context_analyzer import ContextAnalyzer
from analysis.rule_engine import RuleEngine
from storage.frame_indexer import FrameIndexer
from storage.event_logger import EventLogger

def simulate_drone_security_system(video_path=None, telemetry_path=None, output_dir=None, num_frames=100):
    """
    Run the drone security system simulation.
    
    Args:
        video_path: Path to the video file
        telemetry_path: Path to the telemetry data file
        output_dir: Directory to save output files
        num_frames: Number of frames to process in simulation mode
    """
    print("Starting Drone Security Analyst Agent...")
    
    # Initialize components
    video_processor = VideoProcessor(video_path)
    telemetry_processor = TelemetryProcessor(telemetry_path)
    object_detector = ObjectDetector()
    context_analyzer = ContextAnalyzer(telemetry_processor)
    rule_engine = RuleEngine()
    frame_indexer = FrameIndexer()
    event_logger = EventLogger()
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Check if we're using real video or simulation
    using_real_video = False
    if video_path and os.path.exists(video_path):
        print(f"Using video file: {video_path}")
        if video_processor.open_video():
            using_real_video = True
    
    if not using_real_video:
        print("Using simulated video frames")
        simulated_frames = video_processor.simulate_video_frames(num_frames)
    
    # Check telemetry data
    if not telemetry_processor.telemetry_data:
        print("No telemetry data found, generating sample data")
        telemetry_processor.generate_sample_telemetry(num_frames)
    
    # Process frames
    frame_count = 0
    processed_frames = []
    
    print("\nProcessing frames:")
    
    if using_real_video:
        # Process real video
        while True:
            frame, timestamp = video_processor.read_frame()
            if frame is None:
                break
                
            frame_count += 1
            if frame_count % 10 == 0:
                print(f"Processing frame {frame_count}...")
            
            # Detect objects
            detections = object_detector.detect_objects(frame)
            
            # Create frame data
            frame_data = {
                "frame_idx": frame_count,
                "timestamp": timestamp,
                "description": f"Frame {frame_count} at {timestamp}"
            }
            
            # Analyze context
            context_data = context_analyzer.analyze_frame(frame_data, detections)
            
            # Evaluate security rules
            alerts = rule_engine.evaluate_frame(context_data)
            
            # Log events
            for detection in context_data.get("detections", []):
                event_logger.log_detection(detection)
            
            for alert in alerts:
                event_logger.log_alert(alert)
            
            # Index frame
            frame_indexer.index_frame(frame_data, context_data)
            
            # Index alerts
            for alert in alerts:
                frame_indexer.index_alert(alert)
            
            # Save processed frame if output directory specified
            if output_dir and frame_count % 10 == 0:
                annotated_frame = object_detector.draw_detections(frame, detections)
                frame_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
                cv2.imwrite(frame_path, annotated_frame)
            
            # Store frame data for the report
            frame_info = {
                **frame_data,
                "detections": [d.get("class_name") for d in detections],
                "alerts": [a.get("message") for a in alerts]
            }
            processed_frames.append(frame_info)
            
            # Pause briefly to simulate real-time processing
            time.sleep(0.01)
    else:
        # Process simulated frames
        for frame_data in simulated_frames:
            frame_count += 1
            
            # Create fake detections based on frame description
            desc = frame_data.get("description", "")
            fake_detections = []
            
            # Parse objects from the description
            if "Blue Ford F150" in desc:
                fake_detections.append({
                    "class_id": 7,
                    "class_name": "truck",
                    "confidence": 0.92,
                    "bbox": [100, 150, 300, 250]
                })
            elif "Red Sedan" in desc:
                fake_detections.append({
                    "class_id": 2,
                    "class_name": "car",
                    "confidence": 0.88,
                    "bbox": [200, 180, 350, 240]
                })
            elif "Person" in desc:
                fake_detections.append({
                    "class_id": 0,
                    "class_name": "person",
                    "confidence": 0.85,
                    "bbox": [250, 200, 300, 350]
                })
            elif "delivery truck" in desc:
                fake_detections.append({
                    "class_id": 7,
                    "class_name": "truck",
                    "confidence": 0.75,
                    "bbox": [150, 170, 300, 250]
                })
            
            # Analyze context
            context_data = context_analyzer.analyze_frame(frame_data, fake_detections)
            
            # Evaluate security rules
            alerts = rule_engine.evaluate_frame(context_data)
            
            # Log events
            for detection in context_data.get("detections", []):
                event_logger.log_detection(detection)
            
            for alert in alerts:
                event_logger.log_alert(alert)
            
            # Index frame
            frame_indexer.index_frame(frame_data, context_data)
            
            # Index alerts
            for alert in alerts:
                frame_indexer.index_alert(alert)
            
            # Store frame data for the report
            frame_info = {
                **frame_data,
                "detections": [d.get("class_name") for d in fake_detections],
                "alerts": [a.get("message") for a in alerts]
            }
            processed_frames.append(frame_info)
            
            # Display progress
            if frame_count % 10 == 0 or frame_count == 1 or frame_count == len(simulated_frames):
                print(f"Processed frame {frame_count}/{len(simulated_frames)}")
            
            # Pause briefly to simulate real-time processing
            time.sleep(0.01)
    
    # Clean up resources
    if using_real_video:
        video_processor.release()
    
    # Generate summary report
    summary = {
        "total_frames": frame_count,
        "recent_detections": event_logger.get_recent_detections(),
        "recent_alerts": event_logger.get_recent_alerts(),
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save summary if output directory specified
    if output_dir:
        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    # Print summary
    print("\nDrone Security Analysis Summary:")
    print(f"Processed {frame_count} frames")
    print(f"Recent Detections: {len(event_logger.get_recent_detections())}")
    print(f"Recent Alerts: {len(event_logger.get_recent_alerts())}")
    
    if event_logger.recent_alerts:
        print("\nRecent Alerts:")
        for alert in event_logger.get_recent_alerts(5):
            print(f"- {alert['message']}")
    
    # Example queries
    print("\nExample Queries:")
    
    # Query all truck detections
    truck_frames = frame_indexer.query_frames_by_object("truck")
    print(f"Found {len(truck_frames)} frames with trucks")
    
    # Query all high-priority alerts
    high_alerts = frame_indexer.query_alerts(priority="high")
    print(f"Found {len(high_alerts)} high-priority alerts")
    
    print("\nDrone Security Analysis Complete")
    
    return {
        "summary": summary,
        "processed_frames": processed_frames
    }

def main():
    parser = argparse.ArgumentParser(description="Drone Security Analyst Agent")
    parser.add_argument("--video", type=str, default=None, help="Path to video file")
    parser.add_argument("--telemetry", type=str, default=None, help="Path to telemetry data file")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--frames", type=int, default=100, help="Number of frames to process in simulation mode")
    
    args = parser.parse_args()
    
    # Use default paths if not specified
    video_path = args.video if args.video else SAMPLE_VIDEO
    telemetry_path = args.telemetry if args.telemetry else SAMPLE_TELEMETRY
    
    # Run the simulation
    simulate_drone_security_system(video_path, telemetry_path, args.output, args.frames)

if __name__ == "__main__":
    main()