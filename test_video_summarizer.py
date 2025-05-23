#!/usr/bin/env python3
"""
Test Video Summarization System
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_video_summarizer():
    """Test video summarization functionality."""
    try:
        from analysis.video_summarizer import VideoSummarizer
        
        print("Testing Video Summarization System...")
        
        # Create summarizer
        summarizer = VideoSummarizer()
        
        # Test data
        sample_data = [
            {
                "frame_data": {"frame_idx": 1, "timestamp": "14:30:00", "location": "Highway_Overpass"},
                "detections": [{"class_name": "car", "confidence": 0.9}, {"class_name": "truck", "confidence": 0.85}],
                "vlm_description": "Multiple vehicles traveling on highway overpass during afternoon",
                "agent_analysis": {"risk_level": "low", "risk_score": 1.2},
                "alerts": []
            },
            {
                "frame_data": {"frame_idx": 2, "timestamp": "14:31:00", "location": "Highway_Overpass"},
                "detections": [{"class_name": "person", "confidence": 0.92}],
                "vlm_description": "Person walking near highway during daytime",
                "agent_analysis": {"risk_level": "medium", "risk_score": 2.3},
                "alerts": [{"rule_name": "Pedestrian Safety Concern", "priority": "medium"}]
            }
        ]
        
        # Add sample data
        for sample in sample_data:
            summarizer.add_frame_analysis(
                sample["frame_data"],
                sample["detections"], 
                sample["vlm_description"],
                sample["agent_analysis"],
                sample["alerts"]
            )
        
        # Generate summaries
        full_summary = summarizer.generate_session_summary()
        one_sentence = summarizer.generate_one_sentence_summary()
        
        print(f"\\nRESULTS:")
        print(f"One-Sentence Summary: {one_sentence}")
        print(f"\\nNatural Language: {full_summary['natural_language_summary']}")
        print(f"\\nSecurity Assessment: {full_summary['security_assessment']['security_level']}")
        print(f"Security Score: {full_summary['security_assessment']['security_score']}/100")
        
        # Test export
        summarizer.export_summary("test_summary.json", "json")
        print("\\nSummary exported to test_summary.json")
        
        print("\\nVideo Summarization test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_video_summarizer()