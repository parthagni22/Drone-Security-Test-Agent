#!/usr/bin/env python3
"""
LangChain Security Agent - Context Management and Reasoning
Critical Component for Assignment (25% of score)
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class DroneSecurityAgent:
    """
    LangChain-powered security agent for contextual analysis and recommendations.
    Provides conversational memory and intelligent reasoning about security events.
    """
    
    def __init__(self, enable_openai=False, api_key=None):
        """
        Initialize the security agent.
        
        Args:
            enable_openai: Whether to use OpenAI API (requires API key)
            api_key: OpenAI API key (optional)
        """
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
            
            # Initialize OpenAI LLM
            self.llm = OpenAI(
                temperature=0.3,
                openai_api_key=self.api_key,
                model_name="gpt-3.5-turbo-instruct"
            )
            
            # Create tools for the agent
            tools = self._create_agent_tools()
            
            # Initialize memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create agent
            self.agent = initialize_agent(
                tools,
                self.llm,
                agent="conversational-react-description",
                memory=memory,
                verbose=True
            )
            
            print("✅ OpenAI LangChain agent initialized!")
            
        except ImportError:
            print("⚠️  LangChain not installed. Using local agent.")
            self._initialize_local_agent()
        except Exception as e:
            print(f"⚠️  OpenAI agent initialization failed: {e}")
            self._initialize_local_agent()
    
    def _initialize_local_agent(self):
        """Initialize local reasoning agent."""
        print("🔧 Using local security reasoning agent")
        self.agent = "local"
    
    def _create_agent_tools(self):
        """Create tools for the LangChain agent."""
        from langchain.agents import Tool
        
        tools = [
            Tool(
                name="Security Database Query",
                func=self._query_security_database,
                description="Query the security database for past events, patterns, and statistics"
            ),
            Tool(
                name="Risk Assessment",
                func=self._assess_security_risk,
                description="Assess the security risk level of current events and provide recommendations"
            ),
            Tool(
                name="Pattern Analysis",
                func=self._analyze_patterns,
                description="Analyze patterns in security events to identify trends and anomalies"
            ),
            Tool(
                name="Generate Report",
                func=self._generate_security_report,
                description="Generate detailed security reports and summaries"
            )
        ]
        
        return tools
    
    def _load_security_knowledge(self):
        """Load security knowledge base."""
        return {
            "threat_levels": {
                "low": {"score": 1, "description": "Routine activity, no immediate concern"},
                "medium": {"score": 2, "description": "Elevated attention required"},
                "high": {"score": 3, "description": "Immediate security response needed"},
                "critical": {"score": 4, "description": "Emergency situation requiring immediate action"}
            },
            "object_risk_profiles": {
                "person": {
                    "daytime_risk": "low",
                    "nighttime_risk": "medium",
                    "restricted_area_risk": "high"
                },
                "car": {
                    "normal_area_risk": "low",
                    "restricted_area_risk": "medium",
                    "unauthorized_hours_risk": "high"
                },
                "truck": {
                    "normal_area_risk": "low",
                    "restricted_area_risk": "high",
                    "size_concern": "medium"
                }
            },
            "location_security_levels": {
                "Highway_Overpass": "low",
                "Main_Road": "low", 
                "Traffic_Junction": "medium",
                "Security_Zone": "high",
                "Restricted_Area": "critical"
            }
        }
    
    def analyze_security_event(self, frame_data: Dict, detections: List[Dict], 
                             vlm_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a security event using LangChain agent or local reasoning.
        
        Args:
            frame_data: Frame metadata
            detections: Object detections
            vlm_description: VLM-generated description
            
        Returns:
            Dict containing analysis results and recommendations
        """
        # Prepare context data
        context = {
            "timestamp": frame_data.get("timestamp", "00:00:00"),
            "location": frame_data.get("location", "Unknown"),
            "detections": detections,
            "vlm_description": vlm_description,
            "frame_idx": frame_data.get("frame_idx", 0)
        }
        
        # Add to context history
        self.context_history.append(context)
        
        # Analyze using agent
        if self.agent == "local":
            return self._local_security_analysis(context)
        else:
            return self._langchain_security_analysis(context)
    
    def _langchain_security_analysis(self, context: Dict) -> Dict[str, Any]:
        """Analyze using LangChain agent."""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(context)
            
            # Run agent
            response = self.agent.run(prompt)
            
            # Parse response
            analysis = self._parse_agent_response(response, context)
            
            return analysis
            
        except Exception as e:
            print(f"LangChain analysis error: {e}")
            return self._local_security_analysis(context)
    
    def _local_security_analysis(self, context: Dict) -> Dict[str, Any]:
        """Local intelligent security analysis."""
        timestamp = context["timestamp"]
        location = context["location"]
        detections = context["detections"]
        vlm_description = context.get("vlm_description", "")
        
        # Risk assessment
        risk_assessment = self._calculate_risk_score(context)
        
        # Pattern analysis
        patterns = self._detect_patterns(context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(context, risk_assessment)
        
        # Create contextual summary
        summary = self._create_contextual_summary(context, risk_assessment, patterns)
        
        # Security assessment
        security_status = self._assess_security_status(risk_assessment)
        
        analysis = {
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
            "agent_reasoning": self._generate_reasoning_chain(context, risk_assessment)
        }
        
        return analysis
    
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
                base_score += 1
                risk_factors.append("nighttime_activity")
            elif 6 <= hour < 8 or 17 <= hour < 19:  # Rush hours
                base_score += 0.5
                risk_factors.append("high_traffic_hours")
        except:
            pass
        
        # Location-based risk
        location_risk = self.security_knowledge["location_security_levels"].get(location, "medium")
        if location_risk == "high":
            base_score += 2
            risk_factors.append("high_security_location")
        elif location_risk == "critical":
            base_score += 3
            risk_factors.append("critical_security_location")
        elif location_risk == "medium":
            base_score += 1
            risk_factors.append("elevated_security_location")
        
        # Object-based risk
        for detection in detections:
            obj_type = detection.get("class_name", "unknown")
            confidence = detection.get("confidence", 0)
            
            # High confidence detections are more concerning
            if confidence > 0.9:
                base_score += 0.5
                risk_factors.append(f"high_confidence_{obj_type}")
            
            # Object-specific risk
            if obj_type == "person":
                if 22 <= hour or hour < 6:  # Person at night
                    base_score += 1.5
                    risk_factors.append("person_nighttime")
                else:
                    base_score += 0.5
                    risk_factors.append("person_detected")
            
            elif obj_type in ["truck"]:
                base_score += 1
                risk_factors.append("large_vehicle")
            
            elif obj_type in ["car"]:
                base_score += 0.3
                risk_factors.append("vehicle_detected")
        
        # Multiple objects increase risk
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
            return {"patterns_detected": False, "pattern_summary": "Insufficient data for pattern analysis"}
        
        patterns = {
            "patterns_detected": False,
            "pattern_summary": "",
            "recurring_objects": {},
            "location_patterns": {},
            "time_patterns": {},
            "anomalies": []
        }
        
        # Analyze recent history (last 10 events)
        recent_history = self.context_history[-10:]
        
        # Object frequency analysis
        object_counts = {}
        location_counts = {}
        
        for event in recent_history:
            # Count objects
            for detection in event["detections"]:
                obj_type = detection.get("class_name", "unknown")
                object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
            
            # Count locations
            location = event.get("location", "Unknown")
            location_counts[location] = location_counts.get(location, 0) + 1
        
        # Identify patterns
        frequent_objects = {k: v for k, v in object_counts.items() if v >= 3}
        frequent_locations = {k: v for k, v in location_counts.items() if v >= 3}
        
        if frequent_objects:
            patterns["patterns_detected"] = True
            patterns["recurring_objects"] = frequent_objects
            patterns["pattern_summary"] += f"Recurring objects: {', '.join(frequent_objects.keys())}. "
        
        if frequent_locations:
            patterns["patterns_detected"] = True
            patterns["location_patterns"] = frequent_locations
            patterns["pattern_summary"] += f"Active locations: {', '.join(frequent_locations.keys())}. "
        
        # Detect anomalies
        current_objects = [d.get("class_name") for d in context["detections"]]
        if any(obj not in object_counts for obj in current_objects):
            patterns["anomalies"].append("unusual_object_detected")
        
        if not patterns["pattern_summary"]:
            patterns["pattern_summary"] = "Normal activity patterns observed"
        
        return patterns
    
    def _generate_recommendations(self, context: Dict, risk_assessment: Dict) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        risk_level = risk_assessment["risk_level"]
        risk_factors = risk_assessment["risk_factors"]
        
        # Risk-based recommendations
        if risk_level == "critical":
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED: Dispatch security personnel",
                "Activate emergency protocols",
                "Notify security supervisor immediately"
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
                "Review security protocols for this area",
                "Maintain alertness for escalation"
            ])
        else:
            recommendations.append("Continue routine monitoring")
        
        # Specific factor-based recommendations
        if "nighttime_activity" in risk_factors:
            recommendations.append("Enhanced nighttime security protocols advised")
        
        if "person_nighttime" in risk_factors:
            recommendations.append("Verify authorized personnel access for nighttime activity")
        
        if "large_vehicle" in risk_factors:
            recommendations.append("Verify delivery/service authorization for large vehicles")
        
        if "multiple_objects" in risk_factors:
            recommendations.append("Monitor for crowd control or multiple person coordination")
        
        return recommendations
    
    def _create_contextual_summary(self, context: Dict, risk_assessment: Dict, patterns: Dict) -> str:
        """Create contextual summary of the security event."""
        timestamp = context["timestamp"]
        location = context["location"]
        detections = context["detections"]
        vlm_description = context.get("vlm_description", "")
        
        # Start with VLM description if available
        if vlm_description:
            summary = f"Visual Analysis: {vlm_description}. "
        else:
            summary = f"Security event at {location} ({timestamp}). "
        
        # Add detection context
        if detections:
            obj_list = [d.get("class_name") for d in detections]
            obj_summary = ", ".join(set(obj_list))
            summary += f"Detected objects: {obj_summary}. "
        
        # Add risk context
        summary += f"Risk Level: {risk_assessment['risk_level'].upper()} "
        summary += f"(Score: {risk_assessment['total_score']}). "
        
        # Add pattern context
        if patterns["patterns_detected"]:
            summary += f"Pattern Analysis: {patterns['pattern_summary']} "
        
        # Add threat assessment
        summary += f"Assessment: {risk_assessment['threat_description']}"
        
        return summary
    
    def _assess_security_status(self, risk_assessment: Dict) -> str:
        """Assess overall security status."""
        risk_level = risk_assessment["risk_level"]
        
        status_map = {
            "low": "SECURE - Normal operations",
            "medium": "ELEVATED - Increased attention required", 
            "high": "ALERT - Security response recommended",
            "critical": "EMERGENCY - Immediate action required"
        }
        
        return status_map.get(risk_level, "UNKNOWN")
    
    def _generate_reasoning_chain(self, context: Dict, risk_assessment: Dict) -> List[str]:
        """Generate chain of reasoning for the analysis."""
        reasoning = []
        
        # Initial observation
        reasoning.append(f"Observed security event at {context['location']} at {context['timestamp']}")
        
        # Detection reasoning
        if context["detections"]:
            obj_types = [d.get("class_name") for d in context["detections"]]
            reasoning.append(f"Detected objects: {', '.join(set(obj_types))}")
            
            high_conf = [d for d in context["detections"] if d.get("confidence", 0) > 0.8]
            if high_conf:
                reasoning.append(f"High confidence detections: {len(high_conf)} objects")
        
        # Risk factor reasoning
        for factor in risk_assessment["risk_factors"]:
            if factor == "nighttime_activity":
                reasoning.append("Elevated risk due to nighttime activity")
            elif factor == "high_security_location":
                reasoning.append("Increased concern due to high-security location")
            elif factor.startswith("high_confidence_"):
                obj = factor.replace("high_confidence_", "")
                reasoning.append(f"High confidence {obj} detection increases reliability")
        
        # Final assessment
        reasoning.append(f"Overall risk assessment: {risk_assessment['risk_level']} ({risk_assessment['total_score']} points)")
        
        return reasoning
    
    def _create_analysis_prompt(self, context: Dict) -> str:
        """Create prompt for LangChain agent analysis."""
        prompt = f"""
        Analyze this security event and provide recommendations:
        
        Time: {context['timestamp']}
        Location: {context['location']}
        Detected Objects: {[d['class_name'] for d in context['detections']]}
        
        """
        
        if context.get('vlm_description'):
            prompt += f"Visual Description: {context['vlm_description']}\n"
        
        prompt += """
        Please provide:
        1. Risk assessment (low/medium/high/critical)
        2. Security recommendations
        3. Pattern analysis if applicable
        4. Overall security status
        
        Consider factors like time of day, location security level, object types, and confidence scores.
        """
        
        return prompt
    
    def _parse_agent_response(self, response: str, context: Dict) -> Dict[str, Any]:
        """Parse LangChain agent response."""
        # This would parse the agent's natural language response
        # For now, return structured format
        return {
            "agent_response": response,
            "parsed_analysis": "LangChain analysis completed",
            "context": context
        }
    
    def get_conversation_summary(self, limit: int = 10) -> Dict[str, Any]:
        """Get summary of recent security conversations."""
        recent_events = self.context_history[-limit:] if self.context_history else []
        
        summary = {
            "total_events_analyzed": len(self.context_history),
            "recent_events": len(recent_events),
            "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "common_objects": {},
            "active_locations": {},
            "summary_period": f"Last {len(recent_events)} events"
        }
        
        # Analyze recent events
        for event in recent_events:
            # Count objects
            for detection in event["detections"]:
                obj_type = detection.get("class_name", "unknown")
                summary["common_objects"][obj_type] = summary["common_objects"].get(obj_type, 0) + 1
            
            # Count locations
            location = event.get("location", "Unknown")
            summary["active_locations"][location] = summary["active_locations"].get(location, 0) + 1
        
        return summary
    
    def query_security_context(self, query: str) -> Dict[str, Any]:
        """Query the security context and history."""
        # Simple query processing
        query_lower = query.lower()
        
        if "recent" in query_lower or "latest" in query_lower:
            return {"type": "recent_events", "data": self.context_history[-5:]}
        elif "pattern" in query_lower:
            return {"type": "pattern_analysis", "data": self._detect_patterns(self.context_history[-1] if self.context_history else {})}
        elif "summary" in query_lower:
            return {"type": "conversation_summary", "data": self.get_conversation_summary()}
        else:
            return {"type": "general_query", "response": "Query processed", "available_commands": ["recent", "patterns", "summary"]}
    
    # Tool functions for LangChain agent
    def _query_security_database(self, query: str) -> str:
        """Tool function: Query security database."""
        return f"Database query result for: {query}"
    
    def _assess_security_risk(self, event_data: str) -> str:
        """Tool function: Assess security risk."""
        return f"Risk assessment completed for: {event_data}"
    
    def _analyze_patterns(self, data: str) -> str:
        """Tool function: Analyze patterns."""
        return f"Pattern analysis result: {data}"
    
    def _generate_security_report(self, data: str) -> str:
        """Tool function: Generate security report."""
        return f"Security report generated for: {data}"

# Example usage and testing
def test_langchain_agent():
    """Test the LangChain security agent."""
    print("🧪 Testing LangChain Security Agent...")
    
    # Initialize agent
    agent = DroneSecurityAgent(enable_openai=False)  # Use local mode for testing
    
    # Create test frame data
    test_frame_data = {
        "frame_idx": 15,
        "timestamp": "23:30:00", 
        "location": "Security_Zone"
    }
    
    # Create test detections
    test_detections = [
        {
            "class_name": "person",
            "confidence": 0.92,
            "bbox": [100, 150, 200, 350]
        },
        {
            "class_name": "car",
            "confidence": 0.85,
            "bbox": [250, 200, 450, 300]
        }
    ]
    
    # Test VLM description
    test_vlm_description = "A person is walking near a parked car in a security zone during nighttime hours"
    
    # Analyze security event
    analysis = agent.analyze_security_event(
        test_frame_data, 
        test_detections, 
        test_vlm_description
    )
    
    print(f"\n📊 Security Analysis Results:")
    print(f"   Risk Level: {analysis['risk_level'].upper()}")
    print(f"   Risk Score: {analysis['risk_score']}")
    print(f"   Security Status: {analysis['security_status']}")
    print(f"   Summary: {analysis['contextual_summary']}")
    
    print(f"\n🔍 Agent Reasoning:")
    for step in analysis['agent_reasoning']:
        print(f"   • {step}")
    
    print(f"\n💡 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"   • {rec}")
    
    # Test conversation summary
    summary = agent.get_conversation_summary()
    print(f"\n📈 Conversation Summary:")
    print(f"   Total Events: {summary['total_events_analyzed']}")
    print(f"   Recent Events: {summary['recent_events']}")
    
    return agent

if __name__ == "__main__":
    test_langchain_agent()