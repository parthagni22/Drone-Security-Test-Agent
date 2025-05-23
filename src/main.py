import os
import time
import argparse
from datetime import datetime
import json
import cv2
import sys
import numpy as np
import glob

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
from analysis.vlm_descriptor import VLMFrameDescriptor  
from analysis.langchain_agent import DroneSecurityAgent  # ADD THIS LINE
from analysis.video_summarizer import VideoSummarizer  # ADD THIS LINE

def auto_detect_video():
    """Auto-detect video file in data folder."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # Look for common video file extensions
    video_extensions = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.wmv", "*.flv", "*.webm"]
    
    found_videos = []
    for ext in video_extensions:
        pattern = os.path.join(data_dir, ext)
        found_videos.extend(glob.glob(pattern))
    
    if found_videos:
        # Use the first video found
        video_path = found_videos[0]
        print(f"🎥 Auto-detected video: {os.path.basename(video_path)}")
        return video_path
    
    return None

def create_demo_frame(frame_idx, frame_data):
    """Create a demo frame for simulation mode."""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 50
    cv2.rectangle(frame, (50, 50), (590, 430), (100, 100, 100), 2)
    cv2.putText(frame, f"SIMULATION MODE - Frame {frame_idx}", (100, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    timestamp = frame_data.get("timestamp", "00:00:00")
    cv2.putText(frame, f"Time: {timestamp}", (100, 140), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    description = frame_data.get("description", "")
    cv2.putText(frame, description[:50], (100, 180), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
    
    return frame

def create_detections_from_description(description, timestamp):
    """Create detections based on frame description."""
    detections = []
    
    if "truck" in description.lower() or "Blue Ford F150" in description:
        detections.append({
            "class_id": 7,
            "class_name": "truck",
            "confidence": 0.92,
            "bbox": [200, 180, 400, 280],
            "timestamp": timestamp,
            "location": "Gate",
            "method": "SIM"
        })
    
    if "car" in description.lower() or "Red Sedan" in description:
        detections.append({
            "class_id": 2,
            "class_name": "car", 
            "confidence": 0.88,
            "bbox": [250, 200, 420, 290],
            "timestamp": timestamp,
            "location": "Gate",
            "method": "SIM"
        })
    
    if "person" in description.lower() or "Person" in description:
        detections.append({
            "class_id": 0,
            "class_name": "person",
            "confidence": 0.85,
            "bbox": [300, 200, 350, 350],
            "timestamp": timestamp,
            "location": "Gate",
            "method": "SIM"
        })
    
    return detections

def simulate_drone_security_system(video_path=None, telemetry_path=None, output_dir=None, num_frames=100, save_frames=True, use_vlm=True):
    """
    Run the complete drone security system simulation.
    """
    print("🚁 Starting Drone Security Analyst Agent...")
    
    # Auto-detect video if not provided
    if not video_path or not os.path.exists(video_path):
        auto_video = auto_detect_video()
        if auto_video:
            video_path = auto_video
        else:
            print("⚠️  No video file found in data folder")
            print("📁 Supported formats: .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm")
            print("💡 Place your video file in the 'data' folder or use --video parameter")
    
    # Initialize all components
    video_processor = VideoProcessor(video_path)
    telemetry_processor = TelemetryProcessor(telemetry_path)
    object_detector = ObjectDetector()
    context_analyzer = ContextAnalyzer(telemetry_processor)
    rule_engine = RuleEngine()
    frame_indexer = FrameIndexer()
    event_logger = EventLogger()
    # NEW: Initialize Video Summarizer
    video_summarizer = VideoSummarizer()
    print("Video Summarization system ready!")
    # NEW: Initialize VLM Frame Descriptor
    vlm_descriptor = None
    if use_vlm:
        try:
            print("🤖 Initializing VLM Frame Descriptor...")
            vlm_descriptor = VLMFrameDescriptor()
            print("✅ VLM ready for enhanced frame descriptions!")
        except Exception as e:
            print(f"⚠️  VLM initialization failed: {e}")
            print("📝 Continuing without VLM descriptions...")
        vlm_descriptor = None
    
    # NEW: Initialize LangChain Agent
    langchain_agent = None
    try:
        print("🤖 Initializing LangChain Security Agent...")
        langchain_agent = DroneSecurityAgent(enable_openai=False)  # Use local mode
        print("✅ LangChain agent ready for contextual analysis!")
    except Exception as e:
        print(f"⚠️  LangChain agent initialization failed: {e}")
        print("📝 Continuing without agent analysis...")
        langchain_agent = None


    
    # Create output directories
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        if save_frames:
            frames_dir = os.path.join(output_dir, "processed_frames")
            os.makedirs(frames_dir, exist_ok=True)
            print(f"📁 Processed frames will be saved to: {frames_dir}")
    
    # Check video source
    using_real_video = False
    if video_path and os.path.exists(video_path):
        print(f"🎥 Using video file: {video_path}")
        if video_processor.open_video():
            using_real_video = True
    
    if not using_real_video:
        print("🎬 Using simulated video frames")
        simulated_frames = video_processor.simulate_video_frames(num_frames)
    
    # Check telemetry data
    if not telemetry_processor.telemetry_data:
        print("📡 Generating sample telemetry data")
        telemetry_processor.generate_sample_telemetry(num_frames if not using_real_video else 500)
    
    # Processing counters
    frame_count = 0
    detection_count = 0
    alert_count = 0
    processed_frames = []
    
    print("\n🔍 Processing frames:")
    print("-" * 50)
    
    if using_real_video:
        # Process real video
        while True:
            frame, timestamp = video_processor.read_frame()
            if frame is None:
                break
                
            frame_count += 1
            
            # Detect objects
            detections = object_detector.detect_objects(frame, timestamp)
            detection_count += len(detections)
            
            # Create frame data
            # Get telemetry for location context
            telemetry = telemetry_processor.get_telemetry_at_time(timestamp)
            location = telemetry.get("location", "Unknown") if telemetry else "Unknown"

            # NEW: Generate VLM description
            vlm_description = None
            if vlm_descriptor:
                try:
                    vlm_description = vlm_descriptor.generate_description(
                    frame, timestamp, location, detections
                )
                except Exception as e:
                    print(f"VLM Error for frame {frame_count}: {e}")

            # Create enhanced frame data
            frame_data = {
                "frame_idx": frame_count,
                "timestamp": timestamp,
                "description": vlm_description if vlm_description else f"Frame {frame_count} at {timestamp}",
                "vlm_enhanced": vlm_description is not None
            }
            
            # Analyze context
            context_data = context_analyzer.analyze_frame(frame_data, detections)

            # NEW: LangChain Agent Analysis
            agent_analysis = None
            if langchain_agent:
                try:
                    agent_analysis = langchain_agent.analyze_security_event(
                        frame_data, detections, vlm_description
                    )

                        # Add agent analysis  to context
                    context_data["agent_analysis"] = agent_analysis
        
                    # Print agent    insights
                    if agent_analysis and agent_analysis.get("risk_level") in ["high", "critical"]:
                        print(f"🚨 Agent Alert: {agent_analysis['security_status']}")
                        print(f"   Risk: {agent_analysis['risk_level'].upper()} ({agent_analysis['risk_score']})")
            
                except Exception as e:
                    print(f"Agent analysis error: {e}")

            # Evaluate security rules
            alerts = rule_engine.evaluate_frame(context_data)
            alert_count += len(alerts)
            
            # Log events
            for detection in context_data.get("detections", []):
                event_logger.log_detection(detection)
            
            for alert in alerts:
                event_logger.log_alert(alert)
            
            # Index data
            frame_indexer.index_frame(frame_data, context_data)
            for alert in alerts:
                frame_indexer.index_alert(alert)
            
            # NEW: Add to video summarizer
            video_summarizer.add_frame_analysis(
                frame_data, 
                detections,
                vlm_description,
                agent_analysis,
                alerts
            )
            
            # Save processed frame
            if save_frames and output_dir:
                annotated_frame = object_detector.draw_detections(frame, detections)
                
                # Add alerts to frame
                if alerts:
                    y_offset = 60
                    for alert in alerts:
                        alert_text = f"🚨 ALERT: {alert['rule_name']}"
                        cv2.putText(annotated_frame, alert_text, (10, y_offset), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        y_offset += 25
                
                # Add frame info
                info_text = f"Frame: {frame_count} | Time: {timestamp} | Detections: {len(detections)}"
                cv2.putText(annotated_frame, info_text, (10, annotated_frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Save frame
                frame_filename = f"frame_{frame_count:04d}_{timestamp.replace(':', '-')}.jpg"
                frame_path = os.path.join(frames_dir, frame_filename)
                cv2.imwrite(frame_path, annotated_frame)
                
                if detections or alerts:
                    print(f"💾 Saved: {frame_filename} ({len(detections)} detections, {len(alerts)} alerts)")
            
            # Progress update
            if frame_count % 10 == 0:
                print(f"📊 Processed {frame_count} frames | Detections: {detection_count} | Alerts: {alert_count}")
            
            time.sleep(0.01)
    
    else:
        # Process simulated frames
        for frame_data in simulated_frames:
            frame_count += 1
            
            # Create demo frame
            fake_frame = create_demo_frame(frame_count, frame_data)
            
            # Create detections
            fake_detections = create_detections_from_description(
                frame_data.get("description", ""), frame_data["timestamp"])
            detection_count += len(fake_detections)
            
            # Analyze context
            context_data = context_analyzer.analyze_frame(frame_data, fake_detections)
            
            # Evaluate rules
            alerts = rule_engine.evaluate_frame(context_data)
            alert_count += len(alerts)
            
            # Log events
            for detection in context_data.get("detections", []):
                event_logger.log_detection(detection)
            
            for alert in alerts:
                event_logger.log_alert(alert)
            
            # Index data
            frame_indexer.index_frame(frame_data, context_data)
            for alert in alerts:
                frame_indexer.index_alert(alert)
            
            # Save frame
            if save_frames and output_dir:
                annotated_frame = object_detector.draw_detections(fake_frame, fake_detections)
                
                # Add description
                desc = frame_data.get("description", "")
                cv2.putText(annotated_frame, desc[:60], (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Add alerts
                if alerts:
                    y_offset = 250
                    for alert in alerts:
                        alert_text = f"🚨 {alert['rule_name']}"
                        cv2.putText(annotated_frame, alert_text, (10, y_offset), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        y_offset += 25
                
                frame_filename = f"simulated_frame_{frame_count:04d}.jpg"
                frame_path = os.path.join(frames_dir, frame_filename)
                cv2.imwrite(frame_path, annotated_frame)
                
                if fake_detections or alerts:
                    print(f"💾 Saved: {frame_filename} ({len(fake_detections)} detections, {len(alerts)} alerts)")
            
            # Progress update
            if frame_count % 10 == 0 or frame_count in [1, len(simulated_frames)]:
                print(f"📊 Frame {frame_count}/{len(simulated_frames)} processed")
            
            time.sleep(0.01)
    
    # Cleanup
    if using_real_video:
        video_processor.release()
    
    try:
        if 'video_summarizer' in locals() and video_summarizer:
            print("Generating video summary...")
            video_summary = video_summarizer.generate_session_summary()
            one_sentence_summary = video_summarizer.generate_one_sentence_summary()
        
        # Ensure video_summary is a dictionary
            if not isinstance(video_summary, dict):
                print(f"WARNING: video_summary is {type(video_summary)}, creating default")
                video_summary = {
                    "security_assessment": {"security_level": "UNKNOWN", "security_score": 0},
                    "insights_and_patterns": []
                }
        else:
            video_summary = {
                "security_assessment": {"security_level": "NOT_ANALYZED", "security_score": 0},
                "insights_and_patterns": []
            }
            one_sentence_summary = "Video summary not generated"
        
    except Exception as e:
        print(f"Error generating video summary: {e}")
        video_summary = {
            "security_assessment": {"security_level": "ERROR", "security_score": 0},
            "insights_and_patterns": []
        }
        one_sentence_summary = f"Video summary error: {str(e)}"

    # Generate final summary
    summary = {
        "total_frames": frame_count,
        "total_detections": detection_count,
        "total_alerts": alert_count,
        "vlm_enabled": vlm_descriptor is not None,
        "langchain_agent_enabled": langchain_agent is not None,
        "agent_conversation_summary": langchain_agent.get_conversation_summary() if langchain_agent else None,
        "recent_detections": event_logger.get_recent_detections(),
        "recent_alerts": event_logger.get_recent_alerts(),
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "using_real_video": using_real_video,
        "frames_saved": save_frames,
        "video_file": os.path.basename(video_path) if video_path else "Simulation",
    
        # Video Analysis Summary with safe access
        "video_analysis_summary": video_summary,
        "one_sentence_summary": one_sentence_summary,
        "security_assessment": video_summary.get("security_assessment", {"security_level": "UNKNOWN"}),
        "session_insights": video_summary.get("insights_and_patterns", [])
    }
    
    
    # Save video summary
    if output_dir:
        video_summary_path = os.path.join(output_dir, "video_summary.json")
        video_summarizer.export_summary(video_summary_path, "json")
    
        text_summary_path = os.path.join(output_dir, "video_summary.txt") 
        video_summarizer.export_summary(text_summary_path, "txt")
    
        print(f"Video summaries saved to {output_dir}")

    # Save results
    if output_dir:
        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    # Print final results
    print("\n" + "="*60)
    print("🎯 DRONE SECURITY ANALYSIS COMPLETE")
    print("="*60)
    print(f"📊 Total Frames Processed: {frame_count}")
    print(f"🔍 Total Detections: {detection_count}")
    print(f"🚨 Total Alerts Generated: {alert_count}")
    print(f"🎥 Video Source: {'Real Video' if using_real_video else 'Simulation'}")
    if using_real_video and video_path:
        print(f"📁 Video File: {os.path.basename(video_path)}")
    
    if save_frames and output_dir:
        print(f"\n📁 Visual Results: {os.path.join(output_dir, 'processed_frames')}")
        print("   Each frame shows detection boxes, confidence scores, and alerts")
    
    if event_logger.recent_alerts:
        print("\n🚨 Recent Security Alerts:")
        for alert in event_logger.get_recent_alerts(3):
            print(f"   • {alert['message']}")
    
    # Database query examples
    print("\n🔍 Database Query Results:")
    person_frames = frame_indexer.query_frames_by_object("person")
    vehicle_frames = frame_indexer.query_frames_by_object("car") + frame_indexer.query_frames_by_object("truck")
    high_alerts = frame_indexer.query_alerts(priority="high")
    
    print(f"   • Person detections: {len(person_frames)} frames")
    print(f"   • Vehicle detections: {len(vehicle_frames)} frames")
    print(f"   • High-priority alerts: {len(high_alerts)}")
    
    # Display video summary results
    print(f"\nVIDEO ANALYSIS SUMMARY:")
    print(f"One-Sentence: {one_sentence_summary}")
    print(f"Security Assessment: {video_summary['security_assessment']['security_level']}")
    print(f"nSecurity Score: {video_summary['security_assessment']['security_score']}/100")
    
    return {"summary": summary, "processed_frames": frame_count}

def main():
    parser = argparse.ArgumentParser(description="🚁 Drone Security Analyst Agent")
    parser.add_argument("--video", type=str, help="Path to video file (optional - auto-detects from data folder)")
    parser.add_argument("--telemetry", type=str, help="Path to telemetry data file")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--frames", type=int, default=100, help="Number of frames (simulation mode)")
    parser.add_argument("--no-save-frames", action="store_true", help="Don't save frame images")
    parser.add_argument("--disable-vlm", action="store_true", help="Disable VLM descriptions")  # ADD THIS LINE
    

    
    args = parser.parse_args()
    
    # Use provided video or auto-detect
    video_path = args.video
    if not video_path:
        # Try default sample video first, then auto-detect
        if os.path.exists(SAMPLE_VIDEO):
            video_path = SAMPLE_VIDEO
        else:
            video_path = auto_detect_video()
    
    telemetry_path = args.telemetry if args.telemetry else SAMPLE_TELEMETRY
    save_frames = not args.no_save_frames
    use_vlm = not args.disable_vlm  # ADD THIS LINE
    
    # Run the system
    simulate_drone_security_system(video_path, telemetry_path, args.output, args.frames, save_frames, use_vlm)  # MODIFY THIS LINE

if __name__ == "__main__":
    main()
