#!/usr/bin/env python3
"""
Debug and Fix LangChain Import Issue
"""

import os
import sys

def check_langchain_file():
    """Check if langchain_agent.py exists and has correct content."""
    print("🔍 Checking LangChain Agent File...")
    
    langchain_file = "src/analysis/langchain_agent.py"
    
    if not os.path.exists(langchain_file):
        print("❌ File does not exist!")
        return False
    
    # Check file size
    size = os.path.getsize(langchain_file)
    print(f"   File size: {size} bytes")
    
    if size < 1000:  # Too small
        print("⚠️  File seems too small or empty")
        return False
    
    # Check content
    try:
        with open(langchain_file, 'r') as f:
            content = f.read()
        
        if "class DroneSecurityAgent" in content:
            print("✅ DroneSecurityAgent class found")
            return True
        else:
            print("❌ DroneSecurityAgent class NOT found")
            print("   First 200 characters of file:")
            print(f"   {content[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def create_langchain_agent_file():
    """Create the complete LangChain agent file."""
    print("🔧 Creating LangChain Agent File...")
    
    # Ensure directory exists
    os.makedirs("src/analysis", exist_ok=True)
    
    langchain_content = '''#!/usr/bin/env python3
"""
LangChain Security Agent - Context Management and Reasoning
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class DroneSecurityAgent:
    """
    LangChain-powered security agent for contextual analysis and recommendations.
    """
    
    def __init__(self, enable_openai=False, api_key=None):
        """Initialize the security agent."""
        self.enable_openai = enable_openai
        self.api_key = api_key
        self.llm = None
        self.agent = None
        self.memory = []
        self.context_history = []
        self.security_knowledge = self._load_security_knowledge()
        
        print("🤖 Initializing LangChain Security Agent...")
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize LangChain agent with fallback to local reasoning."""
        if self.enable_openai and self.api_key:
            self._initialize_openai_agent()
        else:
            self._initialize_local_agent()
    
    def _initialize_openai_agent(self):
        """Initialize with OpenAI LLM."""
        try:
            from langchain.llms import OpenAI
            from langchain.agents import initialize_agent, Tool
            from langchain.memory import ConversationBufferMemory
            
            self.llm = OpenAI(temperature=0.3, openai_api_key=self.api_key)
            tools = self._create_agent_tools()
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            
            self.agent = initialize_agent(
                tools, self.llm, agent="conversational-react-description", 
                memory=memory, verbose=True
            )
            
            print("✅ OpenAI LangChain agent initialized!")
            
        except ImportError:
            print("⚠️  LangChain not installed. Using local agent.")
            self._initialize_local_agent()
        except Exception as e:
            print(f"⚠️  OpenAI agent failed: {e}. Using local agent.")
            self._initialize_local_agent()
    
    def _initialize_local_agent(self):
        """Initialize local reasoning agent."""
        print("🔧 Using local security reasoning agent")
        self.agent = "local"
    
    def _create_agent_tools(self):
        """Create tools for the LangChain agent."""
        try:
            from langchain.agents import Tool
            
            tools = [
                Tool(
                    name="Security Database Query",
                    func=self._query_security_database, 
                    description="Query security database for events and patterns"
                ),
                Tool(
                    name="Risk Assessment",
                    func=self._assess_security_risk,
                    description="Assess security risk level and provide recommendations"
                )
            ]
            return tools
        except ImportError:
            return []
    
    def _load_security_knowledge(self):
        """Load security knowledge base."""
        return {
            "threat_levels": {
                "low": {"score": 1, "description": "Routine activity, no immediate concern"},
                "medium": {"score": 2, "description": "Elevated attention required"},
                "high": {"score": 3, "description": "Immediate security response needed"},
                "critical": {"score": 4, "description": "Emergency situation"}
            },
            "object_risk_profiles": {
                "person": {"daytime_risk": "low", "nighttime_risk": "medium", "restricted_area_risk": "high"},
                "car": {"normal_area_risk": "low", "restricted_area_risk": "medium"},
                "truck": {"normal_area_risk": "low", "restricted_area_risk": "high"}
            },
            "location_security_levels": {
                "Highway_Overpass": "low", "Main_Road": "low", "Security_Zone": "high",
                "Gate": "medium", "Driveway": "low", "Garage": "medium"
            }
        }
    
    def analyze_security_event(self, frame_data: Dict, detections: List[Dict], 
                             vlm_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a security event using agent reasoning."""
        
        # Prepare context
        context = {
            "timestamp": frame_data.get("timestamp", "00:00:00"),
            "location": frame_data.get("location", "Unknown"),
            "detections": detections,
            "vlm_description": vlm_description,
            "frame_idx": frame_data.get("frame_idx", 0)
        }
        
        # Add to history
        self.context_history.append(context)
        
        # Analyze using local reasoning (always available)
        return self._local_security_analysis(context)
    
    def _local_security_analysis(self, context: Dict) -> Dict[str, Any]:
        """Local intelligent security analysis."""
        timestamp = context["timestamp"]
        location = context["location"]
        detections = context["detections"]
        vlm_description = context.get("vlm_description", "")
        
        # Calculate risk
        risk_assessment = self._calculate_risk_score(context)
        
        # Detect patterns
        patterns = self._detect_patterns(context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(context, risk_assessment)
        
        # Create summary
        summary = self._create_contextual_summary(context, risk_assessment, patterns)
        
        # Security status
        security_status = self._assess_security_status(risk_assessment)
        
        # Generate reasoning chain
        reasoning = self._generate_reasoning_chain(context, risk_assessment)
        
        return {
            "timestamp": timestamp,
            "location": location,
            "risk_score": risk_assessment["total_score"],
            "risk_level": risk_assessment["risk_level"],
            "security_status": security_status,
            "contextual_summary": summary,
            "pattern_analysis": patterns,
            "recommendations": recommendations,
            "detected_objects": [d.get("class_name") for d in detections],
            "confidence_scores": [d.get("confidence", 0) for d in detections],
            "vlm_enhanced": vlm_description is not None,
            "agent_reasoning": reasoning
        }
    
    def _calculate_risk_score(self, context: Dict) -> Dict[str, Any]:
        """Calculate comprehensive risk score."""
        timestamp = context["timestamp"]
        location = context["location"]
        detections = context["detections"]
        
        base_score = 0
        risk_factors = []
        
        # Time-based risk
        try:
            time_obj = datetime.strptime(timestamp, "%H:%M:%S")
            hour = time_obj.hour
            
            if 22 <= hour or hour < 6:  # Night hours
                base_score += 1.5
                risk_factors.append("nighttime_activity")
        except:
            pass
        
        # Location-based risk
        location_risk = self.security_knowledge["location_security_levels"].get(location, "medium")
        if location_risk == "high":
            base_score += 2
            risk_factors.append("high_security_location")
        elif location_risk == "medium":
            base_score += 1
            risk_factors.append("medium_security_location")
        
        # Object-based risk
        for detection in detections:
            obj_type = detection.get("class_name", "unknown")
            confidence = detection.get("confidence", 0)
            
            if confidence > 0.9:
                base_score += 0.5
                risk_factors.append(f"high_confidence_{obj_type}")
            
            if obj_type == "person":
                if 22 <= hour or hour < 6:
                    base_score += 1.5
                    risk_factors.append("person_nighttime")
                else:
                    base_score += 0.5
                    risk_factors.append("person_detected")
            elif obj_type == "truck":
                base_score += 1
                risk_factors.append("large_vehicle")
            elif obj_type == "car":
                base_score += 0.3
                risk_factors.append("vehicle_detected")
        
        # Multiple objects
        if len(detections) > 2:
            base_score += 1
            risk_factors.append("multiple_objects")
        
        # Determine risk level
        if base_score >= 4:
            risk_level = "critical"
        elif base_score >= 3:
            risk_level = "high"
        elif base_score >= 1.5:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "total_score": round(base_score, 2),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "threat_description": self.security_knowledge["threat_levels"][risk_level]["description"]
        }
    
    def _detect_patterns(self, context: Dict) -> Dict[str, Any]:
        """Detect patterns in security events."""
        if len(self.context_history) < 2:
            return {
                "patterns_detected": False, 
                "pattern_summary": "Insufficient data for pattern analysis"
            }
        
        recent_history = self.context_history[-5:]  # Last 5 events
        
        # Count objects and locations
        object_counts = {}
        location_counts = {}
        
        for event in recent_history:
            for detection in event["detections"]:
                obj_type = detection.get("class_name", "unknown")
                object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
            
            location = event.get("location", "Unknown")
            location_counts[location] = location_counts.get(location, 0) + 1
        
        # Identify patterns
        frequent_objects = {k: v for k, v in object_counts.items() if v >= 2}
        frequent_locations = {k: v for k, v in location_counts.items() if v >= 2}
        
        pattern_summary = ""
        patterns_detected = False
        
        if frequent_objects:
            patterns_detected = True
            pattern_summary += f"Recurring objects: {', '.join(frequent_objects.keys())}. "
        
        if frequent_locations:
            patterns_detected = True
            pattern_summary += f"Active locations: {', '.join(frequent_locations.keys())}. "
        
        if not pattern_summary:
            pattern_summary = "Normal activity patterns observed"
        
        return {
            "patterns_detected": patterns_detected,
            "pattern_summary": pattern_summary,
            "recurring_objects": frequent_objects,
            "location_patterns": frequent_locations
        }
    
    def _generate_recommendations(self, context: Dict, risk_assessment: Dict) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        risk_level = risk_assessment["risk_level"]
        risk_factors = risk_assessment["risk_factors"]
        
        if risk_level == "critical":
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED: Dispatch security personnel",
                "Activate emergency protocols",
                "Notify security supervisor"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Increased monitoring recommended",
                "Consider security personnel deployment",
                "Document incident for review"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Continue monitoring situation",
                "Review security protocols"
            ])
        else:
            recommendations.append("Continue routine monitoring")
        
        # Specific recommendations
        if "nighttime_activity" in risk_factors:
            recommendations.append("Enhanced nighttime security protocols advised")
        
        if "person_nighttime" in risk_factors:
            recommendations.append("Verify authorized personnel for nighttime activity")
        
        if "large_vehicle" in risk_factors:
            recommendations.append("Verify delivery authorization for large vehicles")
        
        return recommendations
    
    def _create_contextual_summary(self, context: Dict, risk_assessment: Dict, patterns: Dict) -> str:
        """Create contextual summary."""
        timestamp = context["timestamp"]
        location = context["location"]
        detections = context["detections"]
        vlm_description = context.get("vlm_description", "")
        
        if vlm_description:
            summary = f"Visual Analysis: {vlm_description}. "
        else:
            summary = f"Security event at {location} ({timestamp}). "
        
        if detections:
            obj_list = [d.get("class_name") for d in detections]
            obj_summary = ", ".join(set(obj_list))
            summary += f"Detected: {obj_summary}. "
        
        summary += f"Risk: {risk_assessment['risk_level'].upper()} "
        summary += f"({risk_assessment['total_score']}). "
        
        if patterns["patterns_detected"]:
            summary += f"Patterns: {patterns['pattern_summary']} "
        
        summary += f"Status: {risk_assessment['threat_description']}"
        
        return summary
    
    def _assess_security_status(self, risk_assessment: Dict) -> str:
        """Assess security status."""
        risk_level = risk_assessment["risk_level"]
        
        status_map = {
            "low": "SECURE - Normal operations",
            "medium": "ELEVATED - Increased attention required",
            "high": "ALERT - Security response recommended", 
            "critical": "EMERGENCY - Immediate action required"
        }
        
        return status_map.get(risk_level, "UNKNOWN")
    
    def _generate_reasoning_chain(self, context: Dict, risk_assessment: Dict) -> List[str]:
        """Generate reasoning chain."""
        reasoning = []
        
        reasoning.append(f"Security event observed at {context['location']} at {context['timestamp']}")
        
        if context["detections"]:
            obj_types = [d.get("class_name") for d in context["detections"]]
            reasoning.append(f"Detected objects: {', '.join(set(obj_types))}")
        
        for factor in risk_assessment["risk_factors"][:3]:  # Top 3 factors
            if factor == "nighttime_activity":
                reasoning.append("Elevated risk due to nighttime activity")
            elif factor == "high_security_location":
                reasoning.append("High concern due to security zone location")
            elif factor.startswith("high_confidence_"):
                obj = factor.replace("high_confidence_", "")
                reasoning.append(f"High confidence {obj} detection")
        
        reasoning.append(f"Risk assessment: {risk_assessment['risk_level']} ({risk_assessment['total_score']} points)")
        
        return reasoning
    
    def get_conversation_summary(self, limit: int = 10) -> Dict[str, Any]:
        """Get conversation summary."""
        recent_events = self.context_history[-limit:] if self.context_history else []
        
        summary = {
            "total_events_analyzed": len(self.context_history),
            "recent_events": len(recent_events),
            "common_objects": {},
            "active_locations": {}
        }
        
        for event in recent_events:
            for detection in event["detections"]:
                obj_type = detection.get("class_name", "unknown")
                summary["common_objects"][obj_type] = summary["common_objects"].get(obj_type, 0) + 1
            
            location = event.get("location", "Unknown")
            summary["active_locations"][location] = summary["active_locations"].get(location, 0) + 1
        
        return summary
    
    def query_security_context(self, query: str) -> Dict[str, Any]:
        """Query security context."""
        query_lower = query.lower()
        
        if "recent" in query_lower:
            return {"type": "recent_events", "data": self.context_history[-5:]}
        elif "pattern" in query_lower:
            return {"type": "pattern_analysis", "data": self._detect_patterns(self.context_history[-1] if self.context_history else {})}
        elif "summary" in query_lower:
            return {"type": "conversation_summary", "data": self.get_conversation_summary()}
        else:
            return {"type": "general_query", "available_commands": ["recent", "patterns", "summary"]}
    
    # Tool functions for LangChain agent
    def _query_security_database(self, query: str) -> str:
        """Tool: Query security database."""
        return f"Database query completed for: {query}"
    
    def _assess_security_risk(self, event_data: str) -> str:
        """Tool: Assess security risk."""
        return f"Risk assessment completed for: {event_data}"
'''
    
    try:
        with open("src/analysis/langchain_agent.py", "w") as f:
            f.write(langchain_content)
        print("✅ LangChain agent file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating file: {e}")
        return False

def test_import():
    """Test importing the LangChain agent."""
    print("\n🧪 Testing Import...")
    
    # Add src to path
    src_path = os.path.abspath("src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        from analysis.langchain_agent import DroneSecurityAgent
        
        print("✅ Import successful!")
        
        # Test creating instance
        agent = DroneSecurityAgent(enable_openai=False)
        print("✅ Agent instance created!")
        
        # Test analysis
        test_frame = {"frame_idx": 1, "timestamp": "12:00:00", "location": "Test"}
        test_detections = [{"class_name": "person", "confidence": 0.8}]
        
        result = agent.analyze_security_event(test_frame, test_detections)
        print(f"✅ Analysis completed! Risk: {result['risk_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import/test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    print("🐛 LANGCHAIN AGENT DEBUG TOOL")
    print("=" * 50)
    
    # Check if file exists and is correct
    if not check_langchain_file():
        print("\n🔧 Creating LangChain agent file...")
        if create_langchain_agent_file():
            print("File created successfully!")
        else:
            print("Failed to create file")
            return
    
    # Test import
    if test_import():
        print("\nLangChain agent is ready!")
        print("You can now run: python test_langchain.py")
    else:
        print("\n Still having issues. Let me recreate the file...")
        create_langchain_agent_file()
        print(" Try running the test again")

if __name__ == "__main__":
    main()