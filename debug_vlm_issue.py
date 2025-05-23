#!/usr/bin/env python3
"""
Debug VLM Import Issue
"""

import os
import sys

def check_file_structure():
    """Check if files exist in correct locations."""
    print("🔍 Checking File Structure...")
    
    # Check if src directory exists
    if os.path.exists("src"):
        print("✅ src/ directory exists")
    else:
        print("❌ src/ directory NOT found")
        return False
    
    # Check if analysis directory exists
    if os.path.exists("src/analysis"):
        print("✅ src/analysis/ directory exists")
    else:
        print("❌ src/analysis/ directory NOT found")
        return False
    
    # Check if vlm_descriptor.py exists
    vlm_file = "src/analysis/vlm_descriptor.py"
    if os.path.exists(vlm_file):
        print("✅ src/analysis/vlm_descriptor.py exists")
        
        # Check file size
        size = os.path.getsize(vlm_file)
        print(f"   File size: {size} bytes")
        
        if size < 100:
            print("⚠️  File seems too small - might be empty or incomplete")
            return False
        
        return True
    else:
        print("❌ src/analysis/vlm_descriptor.py NOT found")
        return False

def check_file_content():
    """Check the content of vlm_descriptor.py."""
    vlm_file = "src/analysis/vlm_descriptor.py"
    
    try:
        with open(vlm_file, 'r') as f:
            content = f.read()
        
        print(f"\n📄 File Content Analysis:")
        print(f"   Total characters: {len(content)}")
        print(f"   Total lines: {len(content.splitlines())}")
        
        # Check for key components
        if "class VLMFrameDescriptor" in content:
            print("✅ VLMFrameDescriptor class found")
        else:
            print("❌ VLMFrameDescriptor class NOT found")
            return False
        
        if "def __init__" in content:
            print("✅ __init__ method found")
        else:
            print("❌ __init__ method NOT found")
        
        if "def generate_description" in content:
            print("✅ generate_description method found")
        else:
            print("❌ generate_description method NOT found")
        
        # Show first few lines
        lines = content.splitlines()
        print(f"\n📝 First 10 lines of file:")
        for i, line in enumerate(lines[:10]):
            print(f"   {i+1:2d}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def test_direct_import():
    """Test importing directly."""
    print(f"\n🧪 Testing Direct Import...")
    
    # Add src to path
    src_path = os.path.abspath("src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"   Added to path: {src_path}")
    
    try:
        print("   Attempting: import analysis.vlm_descriptor")
        import analysis.vlm_descriptor
        print("✅ Module imported successfully")
        
        # Check if class exists in module
        if hasattr(analysis.vlm_descriptor, 'VLMFrameDescriptor'):
            print("✅ VLMFrameDescriptor class found in module")
            
            # Try to create instance
            vlm = analysis.vlm_descriptor.VLMFrameDescriptor()
            print("✅ VLMFrameDescriptor instance created successfully")
            return True
        else:
            print("❌ VLMFrameDescriptor class NOT found in module")
            print(f"   Available attributes: {dir(analysis.vlm_descriptor)}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_vlm_file():
    """Create the VLM descriptor file if it's missing or broken."""
    print(f"\n🔧 Creating/Fixing VLM Descriptor File...")
    
    # Ensure directories exist
    os.makedirs("src/analysis", exist_ok=True)
    
    vlm_content = '''#!/usr/bin/env python3
"""
VLM Frame Descriptor - Vision Language Model Integration
"""

import os
import cv2
import numpy as np
from datetime import datetime

class VLMFrameDescriptor:
    """
    Vision Language Model for generating detailed frame descriptions.
    """
    
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        """Initialize VLM with specified model."""
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.device = "cpu"
        self.fallback_descriptions = True
        
        print(f"🤖 Initializing VLM Frame Descriptor...")
        self._load_model()
    
    def _load_model(self):
        """Load the VLM model and processor."""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            print("   Loading BLIP model...")
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
            
            print("✅ VLM model loaded successfully!")
            self.fallback_descriptions = False
            
        except ImportError:
            print("⚠️  Transformers not installed. Using intelligent fallback.")
        except Exception as e:
            print(f"⚠️  VLM model error: {e}. Using intelligent fallback.")
    
    def generate_description(self, frame, timestamp="00:00:00", location="Unknown", detections=None):
        """Generate detailed frame description."""
        if self.fallback_descriptions:
            return self._generate_fallback_description(frame, timestamp, location, detections)
        
        try:
            from PIL import Image
            import torch
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Generate caption
            inputs = self.processor(pil_image, return_tensors="pt")
            with torch.no_grad():
                output = self.model.generate(**inputs, max_length=50)
            
            caption = self.processor.decode(output[0], skip_special_tokens=True)
            
            # Enhance with context
            enhanced = self._enhance_with_context(caption, timestamp, location, detections)
            return enhanced
            
        except Exception as e:
            print(f"VLM Error: {e}")
            return self._generate_fallback_description(frame, timestamp, location, detections)
    
    def _enhance_with_context(self, base_description, timestamp, location, detections):
        """Enhance description with context."""
        enhanced = base_description
        
        # Add time context
        time_context = self._get_time_context(timestamp)
        if time_context:
            enhanced += f" {time_context}"
        
        # Add location
        if location != "Unknown":
            location_desc = self._interpret_location(location)
            enhanced += f" at {location_desc}"
        
        # Add detections
        if detections:
            detection_context = self._get_detection_context(detections)
            enhanced += f". {detection_context}"
        
        enhanced += f" (captured at {timestamp})"
        return enhanced
    
    def _get_time_context(self, timestamp):
        """Get time-based context."""
        try:
            time_obj = datetime.strptime(timestamp, "%H:%M:%S")
            hour = time_obj.hour
            
            if 5 <= hour < 12:
                return "during morning hours"
            elif 12 <= hour < 17:
                return "during afternoon"
            elif 17 <= hour < 21:
                return "during evening"
            else:
                return "during nighttime"
        except:
            return ""
    
    def _interpret_location(self, location):
        """Interpret location codes."""
        location_map = {
            "Highway_Overpass": "a highway overpass",
            "Main_Road": "the main road",
            "Gate": "the security gate",
            "Driveway": "the driveway",
        }
        return location_map.get(location, location.lower().replace("_", " "))
    
    def _get_detection_context(self, detections):
        """Generate detection context."""
        if not detections:
            return ""
        
        obj_types = [d.get("class_name", "object") for d in detections]
        unique_objects = list(set(obj_types))
        
        if len(unique_objects) == 1:
            return f"Security system detected {unique_objects[0]}"
        else:
            return f"Security system detected {', '.join(unique_objects)}"
    
    def _generate_fallback_description(self, frame, timestamp, location, detections):
        """Generate fallback description when VLM unavailable."""
        height, width = frame.shape[:2]
        brightness = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        
        description = "Drone surveillance footage shows "
        
        # Add brightness context
        if brightness < 80:
            description += "a dimly lit scene"
        elif brightness > 180:
            description += "a brightly lit scene"  
        else:
            description += "a moderately lit scene"
        
        # Add detection info
        if detections:
            obj_types = [d.get("class_name", "object") for d in detections]
            unique_objects = list(set(obj_types))
            description += f" with {', '.join(unique_objects)} detected"
        else:
            description += " with no immediate detections"
        
        # Add context
        time_context = self._get_time_context(timestamp)
        if time_context:
            description += f" {time_context}"
        
        if location != "Unknown":
            location_desc = self._interpret_location(location)
            description += f" at {location_desc}"
        
        description += f" (timestamp: {timestamp})"
        return description
    
    def get_model_info(self):
        """Get model information."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.model is not None,
            "fallback_mode": self.fallback_descriptions,
            "status": "VLM Active" if not self.fallback_descriptions else "Intelligent Fallback Active"
        }
'''
    
    try:
        with open("src/analysis/vlm_descriptor.py", "w") as f:
            f.write(vlm_content)
        print("✅ VLM descriptor file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating file: {e}")
        return False

def main():
    """Main debug function."""
    print("🐛 VLM IMPORT DEBUG TOOL")
    print("=" * 50)
    
    # Step 1: Check file structure
    if not check_file_structure():
        print("\n🔧 File structure issue detected. Creating VLM file...")
        if create_vlm_file():
            print("✅ File created. Please run test again.")
        else:
            print("❌ Failed to create file.")
        return
    
    # Step 2: Check file content
    if not check_file_content():
        print("\n🔧 File content issue detected. Recreating VLM file...")
        if create_vlm_file():
            print("✅ File recreated. Please run test again.")
        else:
            print("❌ Failed to recreate file.")
        return
    
    # Step 3: Test import
    if test_direct_import():
        print("\n✅ VLM import working correctly!")
        print("🚀 You can now run: python test_vlm.py")
    else:
        print("\n❌ Import still failing. Recreating file...")
        if create_vlm_file():
            print("✅ File recreated. Try running test again.")

if __name__ == "__main__":
    main()