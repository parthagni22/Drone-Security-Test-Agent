#!/usr/bin/env python3
"""
VLM Frame Descriptor - Vision Language Model Integration
"""

import os
import cv2
import numpy as np
from PIL import Image
import sys
from datetime import datetime

class VLMFrameDescriptor:
    """
    Vision Language Model for generating detailed frame descriptions.
    Uses BLIP for high-quality captions with intelligent fallback.
    """
    
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        """Initialize VLM with specified model."""
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.device = "cpu"
        self.fallback_descriptions = True
        
        print(f"Initializing VLM Frame Descriptor...")
        self._load_model()
    
    def _load_model(self):
        """Load the VLM model and processor."""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            import torch
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"   Device: {self.device}")
            
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
            
            print("VLM model loaded successfully!")
            self.fallback_descriptions = False
            
        except ImportError:
            print("Transformers not installed. Using intelligent fallback.")
        except Exception as e:
            print(f"VLM model error: {e}. Using intelligent fallback.")
    
    def generate_description(self, frame, timestamp="00:00:00", location="Unknown", detections=None):
        """Generate detailed frame description using VLM or intelligent fallback."""
        if self.model is None or self.fallback_descriptions:
            return self._generate_intelligent_fallback_description(frame, timestamp, location, detections)
        
        try:
            # Convert BGR to RGB and create PIL Image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Generate base description with VLM
            base_description = self._generate_vlm_caption(pil_image)
            
            # Enhance with context information
            enhanced_description = self._enhance_with_context(
                base_description, timestamp, location, detections
            )
            
            return enhanced_description
            
        except Exception as e:
            return self._generate_intelligent_fallback_description(frame, timestamp, location, detections)
    
    def _generate_vlm_caption(self, pil_image):
        """Generate caption using BLIP model."""
        try:
            import torch
            
            inputs = self.processor(pil_image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_length=50,
                    num_beams=5,
                    temperature=0.7
                )
            
            caption = self.processor.decode(output[0], skip_special_tokens=True)
            return caption
            
        except Exception as e:
            return "A scene captured by drone surveillance camera"
    
    def _enhance_with_context(self, base_description, timestamp, location, detections):
        """Enhance VLM description with contextual information."""
        try:
            time_context = self._get_time_context(timestamp)
            detection_context = self._get_detection_context(detections) if detections else ""
            
            enhanced = f"{base_description}"
            
            if time_context:
                enhanced += f" {time_context}"
            
            if location and location != "Unknown":
                location_desc = self._interpret_location(location)
                enhanced += f" at {location_desc}"
            
            if detection_context:
                enhanced += f". {detection_context}"
            
            enhanced += f" (captured at {timestamp})"
            
            return enhanced
            
        except Exception as e:
            return base_description
    
    def _get_time_context(self, timestamp):
        """Extract time-based context."""
        try:
            time_obj = datetime.strptime(timestamp, "%H:%M:%S")
            hour = time_obj.hour
            
            if 5 <= hour < 12:
                return "during morning hours"
            elif 12 <= hour < 17:
                return "during afternoon"
            elif 17 <= hour < 21:
                return "during evening"
            elif 21 <= hour or hour < 5:
                return "during nighttime"
            else:
                return ""
        except:
            return ""
    
    def _interpret_location(self, location):
        """Interpret location codes into readable descriptions."""
        location_map = {
            "Highway_Overpass": "a highway overpass",
            "Main_Road": "the main road",
            "Traffic_Junction": "a traffic junction",
            "Gate": "the security gate",
            "Driveway": "the driveway",
            "Garage": "the garage area",
        }
        return location_map.get(location, location.lower().replace("_", " "))
    
    def _get_detection_context(self, detections):
        """Generate detection-specific context."""
        if not detections:
            return ""
        
        detection_counts = {}
        for detection in detections:
            obj_type = detection.get("class_name", "object")
            detection_counts[obj_type] = detection_counts.get(obj_type, 0) + 1
        
        context_parts = []
        for obj_type, count in detection_counts.items():
            if count == 1:
                context_parts.append(f"1 {obj_type}")
            else:
                context_parts.append(f"{count} {obj_type}s")
        
        if context_parts:
            if len(context_parts) == 1:
                return f"Security system detected {context_parts[0]}"
            else:
                return f"Security system detected {', '.join(context_parts)}"
        
        return ""
    
    def _generate_intelligent_fallback_description(self, frame, timestamp, location, detections):
        """Generate intelligent fallback description when VLM is not available."""
        height, width = frame.shape[:2]
        brightness = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        
        description = "Drone security footage shows "
        
        # Add brightness context
        if brightness < 80:
            description += "a dimly lit scene"
        elif brightness > 180:
            description += "a brightly lit scene"
        else:
            description += "a moderately lit scene"
        
        # Add detection information
        if detections:
            obj_types = [d.get("class_name", "object") for d in detections]
            unique_objects = list(set(obj_types))
            
            if len(unique_objects) == 1:
                description += f" with {unique_objects[0]} detection"
            elif len(unique_objects) > 1:
                description += f" with {', '.join(unique_objects)} detections"
        else:
            description += " with no immediate object detections"
        
        # Add contextual location and time information
        time_context = self._get_time_context(timestamp)
        if time_context:
            description += f" {time_context}"
        
        if location != "Unknown":
            location_desc = self._interpret_location(location)
            description += f" at {location_desc}"
        
        description += f" (timestamp: {timestamp})"
        
        return description
    
    def get_model_info(self):
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.model is not None,
            "fallback_mode": self.fallback_descriptions,
            "status": "VLM Active" if not self.fallback_descriptions else "Intelligent Fallback Active"
        }