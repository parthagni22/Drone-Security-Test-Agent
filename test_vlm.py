#!/usr/bin/env python3
"""
Simple VLM Test
"""

import sys
import os
import numpy as np
import cv2

# Add src to path
sys.path.insert(0, 'src')

def test_vlm():
    """Test VLM functionality."""
    try:
        from analysis.vlm_descriptor import VLMFrameDescriptor
        
        print("🧪 Testing VLM Frame Descriptor...")
        
        # Create VLM instance
        vlm = VLMFrameDescriptor()
        
        # Create test image
        test_frame = np.ones((200, 300, 3), dtype=np.uint8) * 100
        cv2.rectangle(test_frame, (50, 50), (250, 150), (0, 255, 0), -1)
        
        # Generate description
        description = vlm.generate_description(
            frame=test_frame,
            timestamp="12:00:00",
            location="Test_Area",
            detections=[{"class_name": "car", "confidence": 0.85}]
        )
        
        print(f"📝 Generated Description:")
        print(f"   {description}")
        
        info = vlm.get_model_info()
        print(f"\n🔧 VLM Status: {info['status']}")
        
        print("\n✅ VLM test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_vlm()