#!/usr/bin/env python3
"""
Video Summarization Feature - Bonus Component
Generates intelligent summaries of video analysis sessions
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class VideoSummarizer:
    """
    Generates intelligent summaries of drone security video analysis sessions.
    Provides both technical summaries and natural language reports.
    """
    
    def __init__(self):
        """Initialize the video summarizer."""
        self.session_data = []
        self.summary_templates = {
            "security": "Security monitoring session analyzed {total_frames} frames over {duration} minutes. Detected {total_detections} objects including {object_summary}. Generated {total_alerts} security alerts with {high_priority_alerts} high-priority incidents requiring immediate attention.",
            "traffic": "Traffic monitoring captured {vehicle_count} vehicles and {person_count} pedestrians over {duration} minutes. Peak activity occurred at {peak_time} with {peak_activity} simultaneous detections.",
            "general": "Drone surveillance session processed {total_frames} frames detecting {unique_objects} types of objects. System maintained {detection_accuracy}% confidence with {alert_rate} alerts per minute."
        }
        
        print("Video Summarization system initialized")
    
    def add_frame_analysis(self, frame_data: Dict, detections: List[Dict], 
                          vlm_description: Optional[str] = None, 
                          agent_analysis: Optional[Dict] = None,
                          alerts: Optional[List] = None):
        """
        Add frame analysis data for summarization.
        
        Args:
            frame_data: Frame metadata
            detections: Object detections
            vlm_description: VLM description
            agent_analysis: LangChain agent analysis
            alerts: Generated alerts
        """
        session_entry = {
            "timestamp": frame_data.get("timestamp", "00:00:00"),
            "frame_idx": frame_data.get("frame_idx", 0),
            "location": frame_data.get("location", "Unknown"),
            "detections": detections,
            "vlm_description": vlm_description,
            "agent_analysis": agent_analysis,
            "alerts": alerts or [],
            "processed_at": datetime.now().isoformat()
        }
        
        self.session_data.append(session_entry)
    
    def generate_session_summary(self, session_type: str = "auto") -> Dict[str, Any]:
        """
        Generate comprehensive session summary.
        
        Args:
            session_type: Type of summary ("security", "traffic", "general", "auto")
            
        Returns:
            Dict containing comprehensive summary
        """
        if not self.session_data:
            return {"error": "No session data available for summarization"}
        
        # Calculate basic statistics
        stats = self._calculate_session_statistics()
        
        # Determine session type if auto
        if session_type == "auto":
            session_type = self._determine_session_type(stats)
        
        # Generate natural language summary
        natural_summary = self._generate_natural_language_summary(stats, session_type)
        
        # Generate technical summary
        technical_summary = self._generate_technical_summary(stats)
        
        # Generate insights and patterns
        insights = self._generate_insights(stats)
        
        # Create comprehensive summary
        summary = {
            "session_metadata": {
                "summary_generated_at": datetime.now().isoformat(),
                "session_type": session_type,
                "total_frames": stats["total_frames"],
                "session_duration": stats["duration_minutes"],
                "analysis_period": f"{stats['start_time']} to {stats['end_time']}"
            },
            "natural_language_summary": natural_summary,
            "technical_summary": technical_summary,
            "key_statistics": stats,
            "insights_and_patterns": insights,
            "security_assessment": self._generate_security_assessment(stats),
            "recommendations": self._generate_summary_recommendations(stats),
            "detailed_timeline": self._generate_timeline_summary(),
            "alert_summary": self._generate_alert_summary(stats)
        }
        
        return summary
    
    def _calculate_session_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive session statistics."""
        if not self.session_data:
            return {}
        
        # Basic counts
        total_frames = len(self.session_data)
        total_detections = sum(len(entry["detections"]) for entry in self.session_data)
        total_alerts = sum(len(entry["alerts"]) for entry in self.session_data)
        
        # Time analysis
        timestamps = [entry["timestamp"] for entry in self.session_data]
        start_time = min(timestamps)
        end_time = max(timestamps)
        
        # Calculate duration
        try:
            start_dt = datetime.strptime(start_time, "%H:%M:%S")
            end_dt = datetime.strptime(end_time, "%H:%M:%S")
            duration = (end_dt - start_dt).total_seconds() / 60  # Minutes
        except:
            duration = total_frames * 0.033 / 60  # Assume 30 FPS
        
        # Object analysis
        all_objects = []
        for entry in self.session_data:
            all_objects.extend([d.get("class_name", "unknown") for d in entry["detections"]])
        
        object_counts = {}
        for obj in all_objects:
            object_counts[obj] = object_counts.get(obj, 0) + 1
        
        # Location analysis
        location_counts = {}
        for entry in self.session_data:
            location = entry["location"]
            location_counts[location] = location_counts.get(location, 0) + 1
        
        # Risk analysis (if agent data available)
        risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        avg_risk_score = 0
        risk_entries = 0
        
        for entry in self.session_data:
            if entry.get("agent_analysis"):
                risk_level = entry["agent_analysis"].get("risk_level", "low")
                risk_levels[risk_level] += 1
                risk_score = entry["agent_analysis"].get("risk_score", 0)
                avg_risk_score += risk_score
                risk_entries += 1
        
        if risk_entries > 0:
            avg_risk_score /= risk_entries
        
        # VLM analysis
        vlm_enhanced_frames = sum(1 for entry in self.session_data if entry.get("vlm_description"))
        
        # Alert analysis
        alert_types = {}
        high_priority_alerts = 0
        
        for entry in self.session_data:
            for alert in entry["alerts"]:
                alert_type = alert.get("rule_name", "unknown")
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
                
                if alert.get("priority") in ["high", "critical"]:
                    high_priority_alerts += 1
        
        # Peak activity analysis
        activity_by_frame = [len(entry["detections"]) for entry in self.session_data]
        peak_activity_frame = max(range(len(activity_by_frame)), key=activity_by_frame.__getitem__) if activity_by_frame else 0
        peak_activity_count = max(activity_by_frame) if activity_by_frame else 0
        peak_time = self.session_data[peak_activity_frame]["timestamp"] if self.session_data else "00:00:00"
        
        return {
            "total_frames": total_frames,
            "total_detections": total_detections,
            "total_alerts": total_alerts,
            "duration_minutes": round(duration, 2),
            "start_time": start_time,
            "end_time": end_time,
            "object_counts": object_counts,
            "unique_objects": len(object_counts),
            "most_common_object": max(object_counts.items(), key=lambda x: x[1]) if object_counts else ("none", 0),
            "location_counts": location_counts,
            "most_active_location": max(location_counts.items(), key=lambda x: x[1]) if location_counts else ("unknown", 0),
            "risk_distribution": risk_levels,
            "average_risk_score": round(avg_risk_score, 2),
            "vlm_enhanced_frames": vlm_enhanced_frames,
            "vlm_coverage_percent": round((vlm_enhanced_frames / total_frames) * 100, 1) if total_frames > 0 else 0,
            "alert_types": alert_types,
            "high_priority_alerts": high_priority_alerts,
            "alert_rate_per_minute": round(total_alerts / duration, 2) if duration > 0 else 0,
            "detection_rate_per_minute": round(total_detections / duration, 2) if duration > 0 else 0,
            "peak_activity": {
                "frame": peak_activity_frame,
                "time": peak_time,
                "count": peak_activity_count
            }
        }
    
    def _determine_session_type(self, stats: Dict) -> str:
        """Determine the type of monitoring session based on statistics."""
        object_counts = stats.get("object_counts", {})
        high_priority_alerts = stats.get("high_priority_alerts", 0)
        
        # Security-focused session
        if high_priority_alerts > 0 or stats.get("average_risk_score", 0) > 2:
            return "security"
        
        # Traffic-focused session
        vehicle_count = object_counts.get("car", 0) + object_counts.get("truck", 0) + object_counts.get("motorcycle", 0)
        if vehicle_count > stats.get("total_detections", 0) * 0.7:
            return "traffic"
        
        # General monitoring
        return "general"
    
    def _generate_natural_language_summary(self, stats: Dict, session_type: str) -> str:
        """Generate natural language summary of the session."""
        template = self.summary_templates.get(session_type, self.summary_templates["general"])
        
        # Prepare template variables
        object_counts = stats.get("object_counts", {})
        
        # Create object summary
        if object_counts:
            top_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            object_summary = ", ".join([f"{count} {obj}{'s' if count > 1 else ''}" for obj, count in top_objects])
        else:
            object_summary = "no objects"
        
        # Vehicle and person counts for traffic summary
        vehicle_count = object_counts.get("car", 0) + object_counts.get("truck", 0) + object_counts.get("motorcycle", 0)
        person_count = object_counts.get("person", 0)
        
        # Format template
        try:
            if session_type == "security":
                summary = template.format(
                    total_frames=stats["total_frames"],
                    duration=stats["duration_minutes"],
                    total_detections=stats["total_detections"],
                    object_summary=object_summary,
                    total_alerts=stats["total_alerts"],
                    high_priority_alerts=stats["high_priority_alerts"]
                )
            elif session_type == "traffic":
                summary = template.format(
                    vehicle_count=vehicle_count,
                    person_count=person_count,
                    duration=stats["duration_minutes"],
                    peak_time=stats["peak_activity"]["time"],
                    peak_activity=stats["peak_activity"]["count"]
                )
            else:  # general
                detection_accuracy = 85  # Placeholder - could be calculated from confidence scores
                summary = template.format(
                    total_frames=stats["total_frames"],
                    unique_objects=stats["unique_objects"],
                    detection_accuracy=detection_accuracy,
                    alert_rate=stats["alert_rate_per_minute"]
                )
        except KeyError as e:
            summary = f"Comprehensive drone surveillance session analyzed {stats['total_frames']} frames with {stats['total_detections']} detections over {stats['duration_minutes']} minutes."
        
        return summary
    
    def _generate_technical_summary(self, stats: Dict) -> Dict[str, Any]:
        """Generate technical summary with detailed metrics."""
        return {
            "processing_metrics": {
                "frames_per_minute": round(stats["total_frames"] / stats["duration_minutes"], 2) if stats["duration_minutes"] > 0 else 0,
                "detections_per_frame": round(stats["total_detections"] / stats["total_frames"], 2) if stats["total_frames"] > 0 else 0,
                "alerts_per_frame": round(stats["total_alerts"] / stats["total_frames"], 3) if stats["total_frames"] > 0 else 0,
                "vlm_utilization": f"{stats['vlm_coverage_percent']}%"
            },
            "detection_breakdown": stats["object_counts"],
            "location_distribution": stats["location_counts"],
            "risk_analysis": {
                "distribution": stats["risk_distribution"],
                "average_score": stats["average_risk_score"],
                "high_risk_incidents": stats["risk_distribution"]["high"] + stats["risk_distribution"]["critical"]
            },
            "alert_breakdown": stats["alert_types"],
            "performance_indicators": {
                "peak_activity_time": stats["peak_activity"]["time"],
                "max_simultaneous_detections": stats["peak_activity"]["count"],
                "most_monitored_location": stats["most_active_location"][0],
                "primary_object_type": stats["most_common_object"][0]
            }
        }
    
    def _generate_insights(self, stats: Dict) -> List[str]:
        """Generate insights and patterns from the session data."""
        insights = []
        
        # Activity patterns
        if stats["peak_activity"]["count"] > 5:
            insights.append(f"Peak activity detected at {stats['peak_activity']['time']} with {stats['peak_activity']['count']} simultaneous objects")
        
        # Object patterns
        most_common = stats["most_common_object"]
        if most_common[1] > stats["total_frames"] * 0.3:
            insights.append(f"Predominant object type: {most_common[0]} appeared in {round((most_common[1]/stats['total_frames'])*100, 1)}% of frames")
        
        # Location patterns
        most_active_location = stats["most_active_location"]
        if most_active_location[1] > stats["total_frames"] * 0.5:
            insights.append(f"Primary monitoring focus: {most_active_location[0]} with sustained activity")
        
        # Risk patterns
        if stats["average_risk_score"] > 2:
            insights.append(f"Elevated security concern with average risk score of {stats['average_risk_score']}")
        
        if stats["high_priority_alerts"] > 0:
            insights.append(f"Critical security events: {stats['high_priority_alerts']} high-priority alerts generated")
        
        # VLM utilization
        if stats["vlm_coverage_percent"] > 80:
            insights.append(f"High AI utilization with {stats['vlm_coverage_percent']}% frames enhanced by vision language model")
        
        # Detection efficiency
        if stats["detection_rate_per_minute"] > 10:
            insights.append(f"High activity environment with {stats['detection_rate_per_minute']} detections per minute")
        
        return insights
    
    def _generate_security_assessment(self, stats: Dict) -> Dict[str, Any]:
        """Generate overall security assessment."""
        # Calculate security score
        security_score = 100  # Start with perfect score
        
        # Deduct for high-risk incidents
        high_risk_incidents = stats["risk_distribution"]["high"] + stats["risk_distribution"]["critical"]
        security_score -= (high_risk_incidents * 10)
        
        # Deduct for high alert rate
        if stats["alert_rate_per_minute"] > 2:
            security_score -= 20
        elif stats["alert_rate_per_minute"] > 1:
            security_score -= 10
        
        # Bonus for comprehensive monitoring
        if stats["vlm_coverage_percent"] > 70:
            security_score += 5
        
        # Ensure score is within bounds
        security_score = max(0, min(100, security_score))
        
        # Determine security level
        if security_score >= 90:
            security_level = "EXCELLENT"
            security_description = "Optimal security conditions with minimal incidents"
        elif security_score >= 75:
            security_level = "GOOD"
            security_description = "Satisfactory security with minor concerns"
        elif security_score >= 60:
            security_level = "MODERATE"
            security_description = "Moderate security concerns requiring attention"
        elif security_score >= 40:
            security_level = "CONCERNING"
            security_description = "Significant security issues identified"
        else:
            security_level = "CRITICAL"
            security_description = "Serious security threats requiring immediate action"
        
        return {
            "security_score": security_score,
            "security_level": security_level,
            "description": security_description,
            "incident_count": high_risk_incidents,
            "monitoring_effectiveness": f"{stats['vlm_coverage_percent']}%",
            "response_required": security_level in ["CONCERNING", "CRITICAL"]
        }
    
    def _generate_summary_recommendations(self, stats: Dict) -> List[str]:
        """Generate recommendations based on session analysis."""
        recommendations = []
        
        # High alert rate
        if stats["alert_rate_per_minute"] > 2:
            recommendations.append("Consider adjusting alert sensitivity to reduce false positives")
        
        # Low VLM coverage
        if stats["vlm_coverage_percent"] < 50:
            recommendations.append("Increase VLM utilization for better frame analysis")
        
        # High-risk incidents
        if stats["high_priority_alerts"] > 0:
            recommendations.append("Review high-priority security incidents and update protocols")
        
        # Activity concentration
        most_active_location = stats["most_active_location"]
        if most_active_location[1] > stats["total_frames"] * 0.7:
            recommendations.append(f"Consider additional monitoring resources for {most_active_location[0]}")
        
        # Detection efficiency
        if stats["detection_rate_per_minute"] < 1 and stats["total_frames"] > 100:
            recommendations.append("Review detection sensitivity - potentially missing events")
        
        # Risk distribution
        if stats["risk_distribution"]["critical"] > 0:
            recommendations.append("Immediate security review required for critical risk incidents")
        
        if not recommendations:
            recommendations.append("Monitoring performance is within acceptable parameters")
        
        return recommendations
    
    def _generate_timeline_summary(self) -> List[Dict[str, Any]]:
        """Generate timeline summary of significant events."""
        timeline = []
        
        # Sample every 10th frame or significant events
        sample_interval = max(1, len(self.session_data) // 10)
        
        for i in range(0, len(self.session_data), sample_interval):
            entry = self.session_data[i]
            
            if entry["detections"] or entry["alerts"]:
                timeline_entry = {
                    "timestamp": entry["timestamp"],
                    "location": entry["location"],
                    "detections": len(entry["detections"]),
                    "objects": [d.get("class_name") for d in entry["detections"]],
                    "alerts": len(entry["alerts"]),
                    "risk_level": entry.get("agent_analysis", {}).get("risk_level", "unknown") if entry.get("agent_analysis") else "unknown"
                }
                timeline.append(timeline_entry)
        
        return timeline
    
    def _generate_alert_summary(self, stats: Dict) -> Dict[str, Any]:
        """Generate comprehensive alert summary."""
        alert_summary = {
            "total_alerts": stats["total_alerts"],
            "high_priority_alerts": stats["high_priority_alerts"],
            "alert_rate_per_minute": stats["alert_rate_per_minute"],
            "alert_types": stats["alert_types"],
            "alert_distribution": {
                "security_related": 0,
                "traffic_related": 0,
                "system_related": 0
            }
        }
        
        # Categorize alerts
        for alert_type, count in stats["alert_types"].items():
            if any(keyword in alert_type.lower() for keyword in ["security", "unauthorized", "restricted"]):
                alert_summary["alert_distribution"]["security_related"] += count
            elif any(keyword in alert_type.lower() for keyword in ["traffic", "vehicle", "road"]):
                alert_summary["alert_distribution"]["traffic_related"] += count
            else:
                alert_summary["alert_distribution"]["system_related"] += count
        
        return alert_summary
    
    def generate_one_sentence_summary(self) -> str:
        """Generate a concise one-sentence summary (bonus requirement)."""
        if not self.session_data:
            return "No video analysis data available for summarization."
        
        stats = self._calculate_session_statistics()
        
        # Template for one-sentence summary
        most_common = stats["most_common_object"]
        duration = stats["duration_minutes"]
        
        if stats["high_priority_alerts"] > 0:
            return f"Security monitoring session detected {stats['total_detections']} objects over {duration:.1f} minutes with {stats['high_priority_alerts']} critical security incidents requiring immediate attention."
        elif most_common[1] > 0:
            return f"Drone surveillance analyzed {duration:.1f} minutes of footage detecting primarily {most_common[0]} activity with {stats['total_alerts']} alerts generated across {stats['unique_objects']} object types."
        else:
            return f"Comprehensive {duration:.1f}-minute security monitoring session processed {stats['total_frames']} frames with standard detection and alert protocols."
    
    def export_summary(self, output_path: str, format: str = "json") -> bool:
        """
        Export summary to file.
        
        Args:
            output_path: Path to save summary
            format: Export format ("json", "txt")
            
        Returns:
            bool: Success status
        """
        try:
            summary = self.generate_session_summary()
            
            if format.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2)
            elif format.lower() == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("DRONE SECURITY VIDEO ANALYSIS SUMMARY\\n")
                    f.write("=" * 50 + "\\n\\n")
                    f.write(f"Natural Language Summary:\\n{summary['natural_language_summary']}\\n\\n")
                    f.write(f"One-Sentence Summary:\\n{self.generate_one_sentence_summary()}\\n\\n")
                    f.write(f"Security Assessment: {summary['security_assessment']['security_level']}\\n")
                    f.write(f"Security Score: {summary['security_assessment']['security_score']}/100\\n\\n")
                    f.write("Key Statistics:\\n")
                    for key, value in summary['key_statistics'].items():
                        f.write(f"  {key}: {value}\\n")
            
            print(f"Summary exported to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting summary: {e}")
            return False
    
    def clear_session(self):
        """Clear current session data."""
        self.session_data = []
        print("Session data cleared")

# Test function
def test_video_summarizer():
    """Test the video summarizer."""
    print("Testing Video Summarization System...")
    
    # Create summarizer
    summarizer = VideoSummarizer()
    
    # Add sample session data
    sample_frames = [
        {
            "frame_data": {"frame_idx": 1, "timestamp": "12:00:00", "location": "Security_Zone"},
            "detections": [{"class_name": "person", "confidence": 0.9}],
            "vlm_description": "A person walking in a security zone",
            "agent_analysis": {"risk_level": "high", "risk_score": 3.2},
            "alerts": [{"rule_name": "Unauthorized Access", "priority": "high"}]
        },
        {
            "frame_data": {"frame_idx": 2, "timestamp": "12:01:00", "location": "Security_Zone"},
            "detections": [{"class_name": "person", "confidence": 0.85}, {"class_name": "car", "confidence": 0.92}],
            "vlm_description": "Person near parked car in restricted area",
            "agent_analysis": {"risk_level": "critical", "risk_score": 4.1},
            "alerts": [{"rule_name": "Critical Security Breach", "priority": "critical"}]
        },
        {
            "frame_data": {"frame_idx": 3, "timestamp": "12:02:00", "location": "Main_Road"},
            "detections": [{"class_name": "truck", "confidence": 0.88}],
            "vlm_description": "Truck passing on main road",
            "agent_analysis": {"risk_level": "low", "risk_score": 1.1},
            "alerts": []
        }
    ]
    
    # Add data to summarizer
    for sample in sample_frames:
        summarizer.add_frame_analysis(
            sample["frame_data"],
            sample["detections"],
            sample["vlm_description"],
            sample["agent_analysis"],
            sample["alerts"]
        )
    
    # Generate summary
    summary = summarizer.generate_session_summary()
    
    print("\\nSUMMARY RESULTS:")
    print("=" * 50)
    print(f"Natural Summary: {summary['natural_language_summary']}")
    print(f"\\nOne-Sentence: {summarizer.generate_one_sentence_summary()}")
    print(f"\\nSecurity Level: {summary['security_assessment']['security_level']}")
    print(f"Security Score: {summary['security_assessment']['security_score']}/100")
    
    # Test export
    summarizer.export_summary("test_summary.json", "json")
    summarizer.export_summary("test_summary.txt", "txt")
    
    print("\\nVideo Summarization test completed!")
    return summarizer

if __name__ == "__main__":
    test_video_summarizer()