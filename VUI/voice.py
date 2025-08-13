import sys
import queue
import sounddevice as sd
import vosk
import json
from dotenv import load_dotenv
import os
from openai import OpenAI
import pyttsx3


load_dotenv()  # Load variables from .env file into environment

import requests

def call_emergency(transcript):
    url = "http://localhost:5000/api/query"  # Change to your Flask server URL

    payload = {
        "query": {
            f"transcript": "{transcript}",
            "location": {
                "latitude": -41.2865,
                "longitude": 174.7762
            },
            "time_submitted": "2025-08-12T07:00:00+00:00",
            "chat_history": [
                {
                    "timestamp": "2025-08-12T06:50:00+00:00",
                    "role": "assistant",
                    "message": "Are you okay?"
                },
                {
                    "timestamp": "2025-08-12T06:55:00+00:00",
                    "role": "user",
                    "message": "Where exactly are you?"
                }
            ],
            "profile_data": {
                "fName": "John",
                "sName": "Doe",
                "bloodType": "AB",
                "knownMedicalIssues": []
            }
        }
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("")
    else:
        print("Error:", response.status_code, response.text)

    return response



tts_engine = pyttsx3.init()

voices = tts_engine.getProperty('voices')
female_voice_id = None
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower() or "kate" in voice.name.lower() or "susan" in voice.name.lower():
        female_voice_id = voice.id
        break

if female_voice_id:
    tts_engine.setProperty('voice', female_voice_id)
else:
    print("Female voice not found, using default voice.")

tts_engine.setProperty('rate', 120)  # slower rate
tts_engine.setProperty('volume', 0.8)

def do_ai(transcript):
    response = call_emergency(transcript)
    
    if response.status_code == 200:
        data = response.json()
        resp = data.get("response", {})
        
        response_message = resp.get("response_message", "No message")
        print("Response message:", response_message)
        print("Emergency type:", resp.get("emergency_type", "Unknown"))
        print("Resources alerted:", ", ".join(resp.get("resources_alerted", []) or ["None"]))
        print("Additional notes:", resp.get("additional_notes", "None"))
        
        tts_engine.say(response_message)
        tts_engine.runAndWait()

    else:
        print("Error:", response.status_code, response.text)



#api_key = os.getenv("OPEN_AI_API_KEY")
#client = OpenAI()  # pass the API key here


#Open Ai Starts



# def do_ai(transcript):
#     response = call_emergency(transcript)
    
#     if response.status_code == 200:
#         data = response.json()
#         # The useful info is inside the 'response' key:
#         resp = data.get("response", {})
        
#         print("Response message:", resp.get("response_message", "No message"))
#         print("Emergency type:", resp.get("emergency_type", "Unknown"))
#         print("Resources alerted:", ", ".join(resp.get("resources_alerted", []) or ["None"]))
#         print("Additional notes:", resp.get("additional_notes", "None"))
#     else:
#         print("Error:", response.status_code, response.text)




#Open Ai Ends

q = queue.Queue()

def transcribe_speech():
    full_text = ""

    model_path = r"C:\Users\datub\OneDrive\Desktop\Vosk_Models\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" #this is hard coded
    model = vosk.Model(model_path)
    samplerate = 16000

    device_info = sd.query_devices(None, 'input')
    if device_info['default_samplerate'] != samplerate:
        print(f"Warning: Your device sample rate is {device_info['default_samplerate']}, but model expects {samplerate}.")

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, samplerate)
            print("Start speaking... Press Ctrl+C to stop.")
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    text = json.loads(result).get("text", "")
                    if text:
                        print("You said:", text)
                        full_text += text + " "
    except KeyboardInterrupt:
        print("\nRecording stopped.")
        return full_text.strip()

# Example use
if __name__ == "__main__":
    transcript = transcribe_speech()
    #transcript = "I think my cat is stuck in a tree"
    print("\nFinal transcript:")
    print(transcript)
    print("\nYou can now continue with the rest of your program.")
    

    print("AI summary: ", do_ai(transcript))

