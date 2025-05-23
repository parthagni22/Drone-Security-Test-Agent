#!/usr/bin/env python3
"""
Quick Fix for Video Summarizer Error
"""

import os


def fix_main_py_summary_section():
    """
    Provides the corrected summary section with error handling
    """
    
    corrected_code = '''
    # Cleanup
    if using_real_video:
        video_processor.release()
    
    # Generate video summary with error handling
    try:
        if 'video_summarizer' in locals() and video_summarizer:
            print("Generating video summary...")
            video_summary = video_summarizer.generate_session_summary()
            one_sentence_summary = video_summarizer.generate_one_sentence_summary()
            
            # Debug: Check what we got
            print(f"Video summary type: {type(video_summary)}")
            
            # Ensure video_summary is a dictionary
            if not isinstance(video_summary, dict):
                print(f"WARNING: video_summary is {type(video_summary)}, creating empty dict")
                video_summary = {
                    "error": "Video summary generation failed",
                    "security_assessment": {"security_level": "UNKNOWN", "security_score": 0},
                    "insights_and_patterns": []
                }
                one_sentence_summary = "Video summary generation encountered an error"
        else:
            print("Video summarizer not available, using defaults")
            video_summary = {
                "security_assessment": {"security_level": "NOT_ANALYZED", "security_score": 0},
                "insights_and_patterns": []
            }
            one_sentence_summary = "Video summary not generated - summarizer unavailable"
            
    except Exception as e:
        print(f"Error generating video summary: {e}")
        video_summary = {
            "error": str(e),
            "security_assessment": {"security_level": "ERROR", "security_score": 0},
            "insights_and_patterns": []
        }
        one_sentence_summary = f"Video summary error: {str(e)}"
    
    # Generate final summary with safe access
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
        "security_assessment": video_summary.get("security_assessment", {"security_level": "UNKNOWN", "security_score": 0}),
        "session_insights": video_summary.get("insights_and_patterns", [])
    }
    
    # Save results with error handling
    if output_dir:
        try:
            summary_path = os.path.join(output_dir, "summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"Summary saved to {summary_path}")
        except Exception as e:
            print(f"Error saving summary: {e}")
        
        # Save video summary separately if available
        try:
            if isinstance(video_summary, dict) and "error" not in video_summary:
                video_summary_path = os.path.join(output_dir, "video_summary.json")
                with open(video_summary_path, 'w') as f:
                    json.dump(video_summary, f, indent=2)
                print(f"Video summary saved to {video_summary_path}")
        except Exception as e:
            print(f"Error saving video summary: {e}")
    '''
    
    return corrected_code

def check_video_summarizer_file():
    """Check if the video summarizer file exists and has the right content"""
    
    summarizer_file = "src/analysis/video_summarizer.py"
    
    if not os.path.exists(summarizer_file):
        print("ERROR: video_summarizer.py does not exist!")
        print("You need to create this file first.")
        return False
    
    # Check file content
    try:
        with open(summarizer_file, 'r') as f:
            content = f.read()
        
        if "class VideoSummarizer" not in content:
            print("ERROR: VideoSummarizer class not found in file!")
            return False
        
        if "def generate_session_summary" not in content:
            print("ERROR: generate_session_summary method not found!")
            return False
        
        print("✅ VideoSummarizer file looks correct")
        return True
        
    except Exception as e:
        print(f"ERROR reading video_summarizer.py: {e}")
        return False

def create_simple_video_summarizer():
    """Create a simple, working video summarizer"""
    
    print("Creating simplified video summarizer...")
    
    summarizer_code = '''#!/usr/bin/env python3
"""
Simple Video Summarizer - Working Version
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class VideoSummarizer:
    """Simple video summarizer that always returns proper dictionaries."""
    
    def __init__(self):
        """Initialize the video summarizer."""
        self.session_data = []
        print("Video Summarization system initialized")
    
    def add_frame_analysis(self, frame_data: Dict, detections: List[Dict], 
                          vlm_description: Optional[str] = None, 
                          agent_analysis: Optional[Dict] = None,
                          alerts: Optional[List] = None):
        """Add frame analysis data for summarization."""
        session_entry = {
            "timestamp": frame_data.get("timestamp", "00:00:00"),
            "frame_idx": frame_data.get("frame_idx", 0),
            "location": frame_data.get("location", "Unknown"),
            "detections": detections or [],
            "vlm_description": vlm_description,
            "agent_analysis": agent_analysis,
            "alerts": alerts or [],
            "processed_at": datetime.now().isoformat()
        }
        
        self.session_data.append(session_entry)
    
    def generate_session_summary(self) -> Dict[str, Any]:
        """Generate comprehensive session summary - ALWAYS returns a dict."""
        try:
            if not self.session_data:
                return {
                    "error": "No session data available",
                    "security_assessment": {"security_level": "NO_DATA", "security_score": 0},
                    "insights_and_patterns": [],
                    "session_metadata": {"total_frames": 0}
                }
            
            # Calculate basic statistics
            total_frames = len(self.session_data)
            total_detections = sum(len(entry["detections"]) for entry in self.session_data)
            total_alerts = sum(len(entry["alerts"]) for entry in self.session_data)
            
            # Time analysis
            timestamps = [entry["timestamp"] for entry in self.session_data]
            start_time = min(timestamps) if timestamps else "00:00:00"
            end_time = max(timestamps) if timestamps else "00:00:00"
            
            # Calculate duration in minutes
            try:
                start_dt = datetime.strptime(start_time, "%H:%M:%S")
                end_dt = datetime.strptime(end_time, "%H:%M:%S")
                duration = (end_dt - start_dt).total_seconds() / 60
            except:
                duration = total_frames * 0.033 / 60  # Assume 30 FPS
            
            # Object analysis
            all_objects = []
            for entry in self.session_data:
                all_objects.extend([d.get("class_name", "unknown") for d in entry["detections"]])
            
            object_counts = {}
            for obj in all_objects:
                object_counts[obj] = object_counts.get(obj, 0) + 1
            
            # Risk analysis
            risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            avg_risk_score = 0
            risk_entries = 0
            
            for entry in self.session_data:
                if entry.get("agent_analysis"):
                    risk_level = entry["agent_analysis"].get("risk_level", "low")
                    if risk_level in risk_levels:
                        risk_levels[risk_level] += 1
                    risk_score = entry["agent_analysis"].get("risk_score", 0)
                    avg_risk_score += risk_score
                    risk_entries += 1
            
            if risk_entries > 0:
                avg_risk_score /= risk_entries
            
            # Security assessment
            security_score = 100
            high_risk_incidents = risk_levels["high"] + risk_levels["critical"]
            security_score -= (high_risk_incidents * 10)
            security_score = max(0, min(100, security_score))
            
            if security_score >= 90:
                security_level = "EXCELLENT"
            elif security_score >= 75:
                security_level = "GOOD"
            elif security_score >= 60:
                security_level = "MODERATE"
            else:
                security_level = "CONCERNING"
            
            # Generate insights
            insights = []
            if object_counts:
                most_common = max(object_counts.items(), key=lambda x: x[1])
                insights.append(f"Most frequent object: {most_common[0]} ({most_common[1]} detections)")
            
            if avg_risk_score > 2:
                insights.append(f"Elevated security concern with average risk score of {avg_risk_score:.1f}")
            
            if high_risk_incidents > 0:
                insights.append(f"High-priority security events: {high_risk_incidents} incidents")
            
            # Create comprehensive summary
            summary = {
                "session_metadata": {
                    "summary_generated_at": datetime.now().isoformat(),
                    "total_frames": total_frames,
                    "session_duration": round(duration, 2),
                    "analysis_period": f"{start_time} to {end_time}"
                },
                "natural_language_summary": f"Drone surveillance session analyzed {total_frames} frames over {duration:.1f} minutes, detecting {total_detections} objects with {total_alerts} alerts generated.",
                "key_statistics": {
                    "total_frames": total_frames,
                    "total_detections": total_detections,
                    "total_alerts": total_alerts,
                    "duration_minutes": round(duration, 2),
                    "object_counts": object_counts,
                    "risk_distribution": risk_levels,
                    "average_risk_score": round(avg_risk_score, 2)
                },
                "security_assessment": {
                    "security_score": security_score,
                    "security_level": security_level,
                    "incident_count": high_risk_incidents,
                    "description": f"{security_level} security conditions observed"
                },
                "insights_and_patterns": insights,
                "recommendations": [
                    "Continue monitoring as configured" if security_level in ["EXCELLENT", "GOOD"] 
                    else "Review security protocols and consider additional measures"
                ]
            }
            
            return summary
            
        except Exception as e:
            print(f"Error in generate_session_summary: {e}")
            return {
                "error": f"Summary generation failed: {str(e)}",
                "security_assessment": {"security_level": "ERROR", "security_score": 0},
                "insights_and_patterns": [],
                "session_metadata": {"total_frames": len(self.session_data)}
            }
    
    def generate_one_sentence_summary(self) -> str:
        """Generate a concise one-sentence summary."""
        try:
            if not self.session_data:
                return "No video analysis data available for summarization."
            
            total_frames = len(self.session_data)
            total_detections = sum(len(entry["detections"]) for entry in self.session_data)
            total_alerts = sum(len(entry["alerts"]) for entry in self.session_data)
            
            # Calculate duration
            timestamps = [entry["timestamp"] for entry in self.session_data]
            try:
                start_time = min(timestamps)
                end_time = max(timestamps)
                start_dt = datetime.strptime(start_time, "%H:%M:%S")
                end_dt = datetime.strptime(end_time, "%H:%M:%S")
                duration = (end_dt - start_dt).total_seconds() / 60
            except:
                duration = total_frames * 0.033 / 60
            
            # Count high-priority alerts
            high_priority_alerts = 0
            for entry in self.session_data:
                for alert in entry["alerts"]:
                    if alert.get("priority") in ["high", "critical"]:
                        high_priority_alerts += 1
            
            if high_priority_alerts > 0:
                return f"Security monitoring session detected {total_detections} objects over {duration:.1f} minutes with {high_priority_alerts} critical security incidents requiring immediate attention."
            else:
                return f"Drone surveillance analyzed {duration:.1f} minutes of footage detecting {total_detections} objects with {total_alerts} standard alerts across {total_frames} processed frames."
                
        except Exception as e:
            return f"Video summary generation encountered an error: {str(e)}"
    
    def export_summary(self, output_path: str, format: str = "json") -> bool:
        """Export summary to file."""
        try:
            summary = self.generate_session_summary()
            
            if format.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2)
            elif format.lower() == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("DRONE SECURITY VIDEO ANALYSIS SUMMARY\\n")
                    f.write("=" * 50 + "\\n\\n")
                    f.write(f"Natural Language Summary:\\n{summary.get('natural_language_summary', 'N/A')}\\n\\n")
                    f.write(f"One-Sentence Summary:\\n{self.generate_one_sentence_summary()}\\n\\n")
                    
                    security = summary.get('security_assessment', {})
                    f.write(f"Security Assessment: {security.get('security_level', 'N/A')}\\n")
                    f.write(f"Security Score: {security.get('security_score', 0)}/100\\n")
            
            print(f"Summary exported to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting summary: {e}")
            return False
    
    def clear_session(self):
        """Clear current session data."""
        self.session_data = []
        print("Session data cleared")
'''
    
    try:
        os.makedirs("src/analysis", exist_ok=True)
        with open("src/analysis/video_summarizer.py", "w", encoding='utf-8') as f:
            f.write(summarizer_code)
        print("✅ Simple video summarizer created successfully!")
        return True
    except Exception as e:
        print(f"ERROR creating video summarizer: {e}")
        return False

def main():
    """Main fix function"""
    print("FIXING VIDEO SUMMARIZER ERROR")
    print("=" * 40)
    
    # Check if summarizer exists
    if not check_video_summarizer_file():
        print("\\nCreating video summarizer...")
        if create_simple_video_summarizer():
            print("✅ Video summarizer created!")
        else:
            print("❌ Failed to create video summarizer")
            return
    
    print("\\n📋 CORRECTED SUMMARY SECTION:")
    print("Replace your summary section in main.py with:")
    print("-" * 50)
    print(fix_main_py_summary_section())
    
    print("\\n🚀 After fixing, run:")
    print("python src/main.py --video data/your_video.mp4")

if __name__ == "__main__":
    main()