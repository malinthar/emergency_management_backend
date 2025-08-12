import openai
import os

openai.api_key = os.getenv("OPEN_AI_KEY")

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "I am hurt badly and need an ambulance right now."}
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

# Extract the JSON arguments returned by the model
triage_data = response.choices[0].message.function_call.arguments

print(triage_data)
