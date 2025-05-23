import os
import sys
import time
import json
from datetime import datetime
import argparse

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

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the demo header."""
    print("=" * 80)
    print("                   DRONE SECURITY ANALYST AGENT DEMO                    ")
    print("=" * 80)
    print("This demo shows the capabilities of the Drone Security Analyst Agent.")
    print("It simulates processing video frames and generates security alerts.")
    print("=" * 80)
    print()

def print_menu():
    """Print the main menu."""
    print("\nMAIN MENU:")
    print("1. Run simulation")
    print("2. View recent detections")
    print("3. View recent alerts")
    print("4. Query frames by object type")
    print("5. Query frames by time range")
    print("6. Query alerts by priority")
    print("7. Exit")
    print()

def run_simulation(num_frames=50):
    """Run the drone security system simulation."""
    clear_screen()
    print_header()
    print(f"Running simulation with {num_frames} frames...\n")
    
    # Initialize components
    video_processor = VideoProcessor()
    telemetry_processor = TelemetryProcessor()
    telemetry_processor.generate_sample_telemetry(num_frames)
    object_detector = ObjectDetector()
    context_analyzer = ContextAnalyzer(telemetry_processor)
    rule_engine = RuleEngine()
    frame_indexer = FrameIndexer()
    event_logger = EventLogger()
    
    # Simulate video frames
    simulated_frames = video_processor.simulate_video_frames(num_frames)
    
    # Process frames
    frame_count = 0
    alert_count = 0
    detection_count = 0
    
    print("Processing frames:")
    print("-" * 40)
    
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
            detection_count += 1
        
        for alert in alerts:
            event_logger.log_alert(alert)
            alert_count += 1
        
        # Index frame
        frame_indexer.index_frame(frame_data, context_data)
        
        # Index alerts
        for alert in alerts:
            frame_indexer.index_alert(alert)
        
        # Display progress
        if frame_count % 5 == 0 or frame_count == 1 or frame_count == len(simulated_frames):
            print(f"Frame {frame_count}/{len(simulated_frames)}: ", end="")
            if fake_detections:
                objects = [d["class_name"] for d in fake_detections]
                print(f"Detected {', '.join(objects)}")
            else:
                print("No objects detected")
        
        # If there are alerts, display them
        for alert in alerts:
            print(f"  ALERT: {alert['message']}")
        
        # Pause briefly to simulate real-time processing
        time.sleep(0.1)
    
    print("\nSimulation complete!")
    print(f"Processed {frame_count} frames")
    print(f"Detected {detection_count} objects")
    print(f"Generated {alert_count} security alerts")
    
    return {
        "frame_indexer": frame_indexer,
        "event_logger": event_logger
    }

def view_recent_detections(event_logger, limit=10):
    """View the most recent object detections."""
    clear_screen()
    print_header()
    print("RECENT OBJECT DETECTIONS:")
    print("-" * 80)
    
    detections = event_logger.get_recent_detections(limit)
    
    if not detections:
        print("No detections found.")
    else:
        for i, detection in enumerate(detections):
            print(f"{i+1}. {detection['message']}")
    
    input("\nPress Enter to continue...")

def view_recent_alerts(event_logger, limit=10):
    """View the most recent security alerts."""
    clear_screen()
    print_header()
    print("RECENT SECURITY ALERTS:")
    print("-" * 80)
    
    alerts = event_logger.get_recent_alerts(limit)
    
    if not alerts:
        print("No alerts found.")
    else:
        for i, alert in enumerate(alerts):
            print(f"{i+1}. {alert['message']}")
    
    input("\nPress Enter to continue...")

def query_frames_by_object(frame_indexer):
    """Query frames containing a specific object type."""
    clear_screen()
    print_header()
    print("QUERY FRAMES BY OBJECT TYPE:")
    print("-" * 80)
    
    print("Object types: person, car, truck, motorcycle, bicycle")
    object_type = input("Enter object type to search for: ").strip().lower()
    
    if not object_type:
        return
    
    frames = frame_indexer.query_frames_by_object(object_type)
    
    print(f"\nFound {len(frames)} frames containing '{object_type}':")
    print("-" * 80)
    
    if not frames:
        print("No matching frames found.")
    else:
        for i, frame in enumerate(frames[:10]):  # Show max 10 results
            print(f"{i+1}. {frame['timestamp']} at {frame['location']}: {frame['description']}")
        
        if len(frames) > 10:
            print(f"... and {len(frames) - 10} more results.")
    
    input("\nPress Enter to continue...")

def query_frames_by_time(frame_indexer):
    """Query frames within a time range."""
    clear_screen()
    print_header()
    print("QUERY FRAMES BY TIME RANGE:")
    print("-" * 80)
    
    print("Enter time range in format HH:MM:SS")
    start_time = input("Start time: ").strip()
    end_time = input("End time: ").strip()
    
    if not start_time or not end_time:
        return
    
    try:
        frames = frame_indexer.query_frames_by_time(start_time, end_time)
        
        print(f"\nFound {len(frames)} frames between {start_time} and {end_time}:")
        print("-" * 80)
        
        if not frames:
            print("No matching frames found.")
        else:
            for i, frame in enumerate(frames[:10]):  # Show max 10 results
                objects = frame['objects'] if frame['objects'] else "No objects"
                print(f"{i+1}. {frame['timestamp']} at {frame['location']}: {objects}")
            
            if len(frames) > 10:
                print(f"... and {len(frames) - 10} more results.")
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to continue...")

def query_alerts_by_priority(frame_indexer):
    """Query alerts by priority level."""
    clear_screen()
    print_header()
    print("QUERY ALERTS BY PRIORITY:")
    print("-" * 80)
    
    print("Priority levels: high, medium, low")
    priority = input("Enter priority level to search for: ").strip().lower()
    
    if priority not in ["high", "medium", "low"]:
        print("Invalid priority level.")
        input("\nPress Enter to continue...")
        return
    
    alerts = frame_indexer.query_alerts(priority=priority)
    
    print(f"\nFound {len(alerts)} {priority}-priority alerts:")
    print("-" * 80)
    
    if not alerts:
        print("No matching alerts found.")
    else:
        for i, alert in enumerate(alerts):
            print(f"{i+1}. {alert['timestamp']} - {alert['message']}")
    
    input("\nPress Enter to continue...")

def main():
    """Main function to run the interactive demo."""
    parser = argparse.ArgumentParser(description="Drone Security Analyst Agent Demo")
    parser.add_argument("--frames", type=int, default=50, help="Number of frames to process in simulation")
    
    args = parser.parse_args()
    
    # Run the initial simulation
    components = run_simulation(args.frames)
    frame_indexer = components["frame_indexer"]
    event_logger = components["event_logger"]
    
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            components = run_simulation(args.frames)
            frame_indexer = components["frame_indexer"]
            event_logger = components["event_logger"]
        elif choice == "2":
            view_recent_detections(event_logger)
        elif choice == "3":
            view_recent_alerts(event_logger)
        elif choice == "4":
            query_frames_by_object(frame_indexer)
        elif choice == "5":
            query_frames_by_time(frame_indexer)
        elif choice == "6":
            query_alerts_by_priority(frame_indexer)
        elif choice == "7":
            clear_screen()
            print("Thank you for using the Drone Security Analyst Agent Demo!")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()