import datetime
import json
import os
from typing import Dict, List, Optional, Any
import openai

from dotenv import load_dotenv

load_dotenv()

class EmergencyTools:
    """Tools for emergency management and response"""
    
    @staticmethod
    def extract_emergency_data(transcript: str) -> Dict[str, Any]:
        """
        Extract structured data from emergency transcripts using AI
        
        Args:
            transcript (str): The transcript text from emergency call/message
            
        Returns:
            dict: Structured data extracted from the transcript
        """
        try:
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
                                "severity": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high", "critical"],
                                    "description": "Severity level of the emergency"
                                },
                                "time_submitted": {
                                    "type": "string",
                                    "format": "date-time",
                                    "description": "Timestamp when the emergency was reported"
                                },
                                "service_type": {
                                    "type": "string",
                                    "enum": ["fire", "police", "ambulance", "mentalhealth", "foodbank", "other"],
                                    "description": "Type of emergency service needed"
                                },
                                "transcript": {
                                    "type": "string",
                                    "description": "Raw transcription of the caller's statement"
                                }
                            },
                            "required": ["severity", "time_submitted", "service_type"]
                        }
                    }
                ],
                function_call={"name": "triage_emergency"}
            )
            
            print (f"OpenAI response: {response}")
            # Extract the JSON arguments returned by the model
            triage_data = json.loads(response.choices[0].message.function_call.arguments)
            print(f"Extracted emergency data: {triage_data}")
            return triage_data.to_dict()
            
        except Exception as e:
            print(f"Error extracting emergency data: {e}")
            return {
                "error": str(e),
                "severity": "unknown",
                "service_type": "unknown",
                "time_submitted": datetime.datetime.now().isoformat()
            }
    
    @staticmethod
    def alert_emergency_services(emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alert relevant emergency services based on the emergency data
        
        Args:
            emergency_data (dict): Structured emergency data
            
        Returns:
            dict: Response from emergency services
        """
        # In a production environment, this would integrate with emergency service APIs
        # For now, we'll simulate the response
        try:
            service_type = emergency_data.get("service_type", "unknown")
            severity = emergency_data.get("severity", "unknown")
            
            # Simulate different response times based on severity
            response_times = {
                "critical": "2-5 minutes",
                "high": "5-10 minutes",
                "medium": "10-20 minutes",
                "low": "30-60 minutes",
                "unknown": "unknown"
            }
            
            return {
                "alert_sent": True,
                "service_alerted": service_type,
                "severity_reported": severity,
                "estimated_response_time": response_times.get(severity, "unknown"),
                "alert_time": datetime.datetime.now().isoformat(),
                "alert_id": f"EM-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
        except Exception as e:
            print(f"Error alerting emergency services: {e}")
            return {
                "alert_sent": False,
                "error": str(e)
            }
    
    @staticmethod
    def generate_report(emergency_data: Dict[str, Any], response_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report of the emergency and response
        
        Args:
            emergency_data (dict): Structured emergency data
            response_data (dict, optional): Response data from emergency services
            
        Returns:
            dict: Comprehensive report data
        """
        try:
            report = {
                "report_id": f"RPT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.datetime.now().isoformat(),
                "emergency_details": emergency_data,
                "response_details": response_data if response_data else {},
                "status": "open"
            }
            
            # In a production environment, you might want to save this report to a database
            
            return report
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return {
                "error": str(e),
                "report_generated": False
            }
    
    @staticmethod
    def find_next_steps(emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine recommended next steps based on emergency data
        
        Args:
            emergency_data (dict): Structured emergency data
            
        Returns:
            dict: Recommended next steps
        """
        try:
            service_type = emergency_data.get("service_type", "unknown")
            severity = emergency_data.get("severity", "unknown")
            
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
                next_steps[service_type].insert(0, "This is a CRITICAL situation - act immediately")
            
            return {
                "recommended_steps": next_steps.get(service_type, next_steps["other"]),
                "priority": severity,
                "follow_up_required": severity in ["critical", "high"]
            }
            
        except Exception as e:
            print(f"Error finding next steps: {e}")
            return {
                "error": str(e),
                "recommended_steps": ["Contact emergency services directly"]
            }
    
    @staticmethod
    def translate_to_language(text: str, target_language: str) -> Dict[str, Any]:
        """
        Translate text to the specified language
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (e.g., "es" for Spanish)
            
        Returns:
            dict: Translation results
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
                "translation_time": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error translating text: {e}")
            return {
                "error": str(e),
                "original_text": text,
                "translation_successful": False
            }
