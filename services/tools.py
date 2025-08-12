import datetime
import json
import os
from typing import Dict, List, Optional, Any, Union
import openai
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

class PersonProfile(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None
    medical_conditions: Optional[str] = None

class Location(BaseModel):
    address: Optional[str] = None
    landmarks: Optional[str] = None
    coordinates: Optional[str] = None

class ExtractedEmergencyData(BaseModel):
    emergency_type: str  # Type of emergency (fire, flood, medical emergency, etc.)
    person_profile: Optional[PersonProfile] = None
    location: Optional[Location] = None
    time_of_incident: Optional[str] = None
    people_affected: Optional[int] = None
    immediate_risks: Optional[List[str]] = None
    resources_needed: Optional[List[str]] = None
    additional_notes: Optional[str] = None
    severity: Optional[str] = None
    
class ServiceInvokedResponse(BaseModel):
    alert_sent: bool
    service_alerted: Optional[str] = None
    severity_reported: Optional[str] = None
    estimated_response_time: Optional[str] = None
    alert_time: Optional[str] = None
    alert_id: Optional[str] = None
    error: Optional[str] = None
    
class NextStepsResponse(BaseModel):
    recommended_steps: List[str]
    priority: Optional[str] = None  # e.g., "critical", "high", "medium", "low"
    follow_up_required: Optional[bool] = None  # Indicates if further action is needed
    additional_notes: Optional[str] = None  # Any extra information or context
    error: Optional[str] = None

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: Optional[str] = None
    target_language: str
    translation_time: Optional[str] = None
    translation_successful: Optional[bool] = None
    error: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: Optional[str] = None
    generated_at: Optional[str] = None
    emergency_details: Optional[Dict] = None
    response_details: Optional[Dict] = None
    status: Optional[str] = None
    report_generated: Optional[bool] = None
    error: Optional[str] = None
    
class EmergencyTools:
    """Tools for emergency management and response"""
    
    @staticmethod
    def extract_emergency_data(transcript: str) -> ExtractedEmergencyData:
        """
        Extract structured data from emergency transcripts using AI
        
        Args:
            transcript (str): The transcript text from emergency call/message
            
        Returns:
            Dict: Structured data extracted from the transcript
        """
        try:
            print(f"Extracting emergency data from transcript: {transcript}")
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": transcript}
                ],
                functions=[
                    {
                        "name": "triage_emergency",
                        "description": "Extract emergency triage details from caller input",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "emergency_type": {
                                    "type": "string",
                                    "description": "Type of emergency (fire, flood, medical emergency, etc.)"
                                },
                                "person_profile": {
                                    "type": "object",
                                    "properties": {
                                        "age": {
                                            "type": "string",
                                            "description": "Age of affected person(s)"
                                        },
                                        "gender": {
                                            "type": "string",
                                            "description": "Gender of affected person(s)"
                                        },
                                        "medical_conditions": {
                                            "type": "string",
                                            "description": "Any relevant medical conditions"
                                        }
                                    }
                                },
                                "location": {
                                    "type": "object",
                                    "properties": {
                                        "address": {
                                            "type": "string",
                                            "description": "Address where emergency is occurring"
                                        },
                                        "landmarks": {
                                            "type": "string",
                                            "description": "Nearby landmarks to help locate the emergency"
                                        },
                                        "coordinates": {
                                            "type": "string",
                                            "description": "GPS coordinates if available"
                                        }
                                    }
                                },
                                "time_of_incident": {
                                    "type": "string",
                                    "description": "When the emergency occurred"
                                },
                                "people_affected": {
                                    "type": "integer",
                                    "description": "Number of people affected by the emergency"
                                },
                                "immediate_risks": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    },
                                    "description": "Immediate risks present in the situation"
                                },
                                "resources_needed": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    },
                                    "description": "Resources needed to address the emergency"
                                },
                                "additional_notes": {
                                    "type": "string",
                                    "description": "Any additional relevant information"
                                },
                                "severity": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high", "critical"],
                                    "description": "Severity level of the emergency"
                                }
                            },
                            "required": ["emergency_type", "location", "severity"]
                        }
                    }
                ],
                function_call={"name": "triage_emergency"}
            )
            
            print(f"OpenAI response: {response}")
            # Extract the JSON arguments returned by the model
            triage_data = json.loads(response.choices[0].message.function_call.arguments)
            print(f"Extracted emergency data: {triage_data}")
            # Convert to a dictionary for easy serialization
            return triage_data
            
        except Exception as e:
            print(f"Error extracting emergency data: {e}")
            return {
                "error": str(e),
                "severity": "unknown",
                "emergency_type": "unknown",
                "time_of_incident": datetime.datetime.now().isoformat()
            }
    
    @staticmethod
    def alert_emergency_services(emergency_data: ExtractedEmergencyData) -> ServiceInvokedResponse:
        """
        Alert relevant emergency services based on the emergency data
        
        Args:
            emergency_data (ExtractedEmergencyData): Structured emergency data
            
        Returns:
            ServiceInvokedResponse: Response from emergency services
        """
        # In a production environment, this would integrate with emergency service APIs
        try:
            print(f"Received request: {emergency_data}")
            service_type = emergency_data.emergency_type
            severity = emergency_data.severity
            
            # Simulate different response times based on severity
            response_times = {
                "critical": "2-5 minutes",
                "high": "5-10 minutes",
                "medium": "10-20 minutes",
                "low": "30-60 minutes",
                "unknown": "unknown"
            }
            
            response = {
                "alert_sent": True,
                "service_alerted": service_type,
                "severity_reported": severity,
                "estimated_response_time": response_times.get(severity, "unknown"),
                "alert_time": datetime.datetime.now().isoformat(),
                "alert_id": f"EM-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            return response
            
        except Exception as e:
            print(f"Error alerting emergency services: {e}")
            return {
                "alert_sent": False,
                "error": str(e)
            }
    
    @staticmethod
    def generate_report(emergency_data: ExtractedEmergencyData, response_data: Optional[ServiceInvokedResponse] = None) -> ReportResponse:
        """
        Generate a comprehensive report of the emergency and response
        
        Args:
            emergency_data (ExtractedEmergencyData): Structured emergency data
            response_data (ServiceInvokedResponse, optional): Response data from emergency services
            
        Returns:
            ReportResponse: Comprehensive report data
        """
        try:
            report = {
                "report_id": f"RPT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.datetime.now().isoformat(),
                "emergency_details": emergency_data,
                "response_details": response_data if response_data else {},
                "status": "open"
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return {
                "error": str(e),
                "report_generated": False
            }
    
    @staticmethod
    def find_next_steps(emergency_data: ExtractedEmergencyData, services_response: ServiceInvokedResponse) -> NextStepsResponse:
        """
        Determine recommended next steps based on emergency data
        
        Args:
            emergency_data (ExtractedEmergencyData): Structured emergency data
            services_response (ServiceInvokedResponse): Response from emergency services
            
        Returns:
            NextStepsResponse: Recommended next steps
        """
        try:
            print(f"Finding next steps for: {emergency_data}")
            service_type = emergency_data.emergency_type
            severity = emergency_data.severity
            services_alerted = services_response.service_alerted
            
            # Define common next steps based on emergency type
            next_steps = {
                "fire": [
                    "Evacuate the building immediately",
                    "Call 911 if not already done",
                    "Move to a safe distance",
                    "Do not re-enter until cleared by authorities"
                ],
                "police": [
                    "Stay in a safe location",
                    "Cooperate with authorities",
                    "Document any relevant details"
                ],
                "ambulance": [
                    "Stay on the line with emergency services",
                    "Follow first aid instructions if provided",
                    "Clear a path for emergency responders",
                    "Have medical information ready if available"
                ],
                "mentalhealth": [
                    "Stay on the line with the crisis counselor",
                    "Remove any dangerous objects from vicinity",
                    "Focus on breathing and grounding techniques",
                    "Have a trusted person join if possible"
                ],
                "foodbank": [
                    "Document current food supplies",
                    "Identify dietary restrictions",
                    "Prepare for delivery or pickup instructions"
                ],
                "other": [
                    "Stay calm",
                    "Follow instructions from authorities",
                    "Document the situation"
                ]
            }
            
            # Add severity-specific recommendations
            if severity == "critical":
                next_steps.get(service_type, next_steps["other"]).insert(0, "This is a CRITICAL situation - act immediately")
            
            return {
                "recommended_steps": next_steps.get(service_type, next_steps["other"]),
                "priority": severity,
                "follow_up_required": severity in ["critical", "high"],
                "additional_notes": "Ensure to keep communication lines open with emergency services"
            }
            
        except Exception as e:
            print(f"Error finding next steps: {e}")
            return {
                "error": str(e),
                "recommended_steps": ["Contact emergency services directly"]
            }
    
    @staticmethod
    def translate_to_language(text: str, target_language: str) -> TranslationResponse:
        """
        Translate text to the specified language
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (e.g., "es" for Spanish)
            
        Returns:
            TranslationResponse: Translation results
        """
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            # Using OpenAI for translation
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are a translator. Translate the following text to {target_language}:"},
                    {"role": "user", "content": text}
                ]
            )
            
            translated_text = response.choices[0].message.content
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "target_language": target_language,
                "translation_time": datetime.datetime.now().isoformat(),
                "translation_successful": True
            }
            
        except Exception as e:
            print(f"Error translating text: {e}")
            return {
                "error": str(e),
                "original_text": text,
                "target_language": target_language,
                "translation_successful": False
            }
