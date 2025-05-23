#!/usr/bin/env python3
"""
Test LangChain Security Agent
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_langchain_agent():
    """Test LangChain agent functionality."""
    try:
        from analysis.langchain_agent import DroneSecurityAgent
        
        print("Testing LangChain Security Agent...")
        
        # Create agent
        agent = DroneSecurityAgent(enable_openai=False)
        
        # Test data
        frame_data = {
            "frame_idx": 25,
            "timestamp": "02:15:00",  # Night time
            "location": "Security_Zone"
        }
        
        detections = [
            {
                "class_name": "person",
                "confidence": 0.95,
                "bbox": [100, 150, 200, 350]
            }
        ]
        
        vlm_description = "A person is walking in a restricted security zone during nighttime"
        
        # Analyze event
        analysis = agent.analyze_security_event(frame_data, detections, vlm_description)
        
        print(f"\n Analysis Results:")
        print(f"   Risk Level: {analysis['risk_level'].upper()}")
        print(f"   Risk Score: {analysis['risk_score']}")
        print(f"   Status: {analysis['security_status']}")
        print(f"   Summary: {analysis['contextual_summary'][:100]}...")
        
        print(f"\n Agent Reasoning:")
        for step in analysis['agent_reasoning'][:3]:
            print(f"   • {step}")
        
        print(f"\n Top Recommendations:")
        for rec in analysis['recommendations'][:2]:
            print(f"   • {rec}")
        
        # Test multiple events for pattern detection
        print(f"\n Testing pattern detection...")
        for i in range(3):
            test_frame = {
                "frame_idx": 30 + i,
                "timestamp": f"02:{20+i}:00",
                "location": "Security_Zone"
            }
            agent.analyze_security_event(test_frame, detections, None)
        
        # Check conversation summary
        summary = agent.get_conversation_summary()
        print(f"\n Conversation Summary:")
        print(f"   Total Events: {summary['total_events_analyzed']}")
        print(f"   Common Objects: {summary['common_objects']}")
        
        print("\nLangChain agent test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_langchain_agent()