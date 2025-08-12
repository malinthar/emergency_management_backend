from flask import Flask, request, jsonify
from services.ai_service import AIService
from flask_cors import CORS  # Import CORS to handle cross-origin requests
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

ai_service = AIService()

secret_key = os.getenv("OPEN_AI_KEY")

print(secret_key)



#Example JSON Body for using api/query
#For MVP only required field is query 
# {
#   "query": {
#     "transcript": "I am hurt badly and need help",
#     "location": {
#       "latitude": -41.2865,
#       "longitude": 174.7762
#     },
#     "time_submitted": "2025-08-12T07:00:00+00:00",
#     "chat_history": [
#       {
#         "timestamp": "2025-08-12T06:50:00+00:00",
#         "role": "assistant",
#         "message": "Are you okay?"
#       },
#       {
#         "timestamp": "2025-08-12T06:55:00+00:00",
#         "role": "user",
#         "message": "Where exactly are you?"
#       }
#     ],
#     "profile_data": {
#       "fName": "John",
#       "sName": "Doe",
#       "bloodType": "AB",
#       "knownMedicalIssues": []
#     }
#   }
# }


@app.route('/api/query', methods=['POST'])
def process_user_query():
    try:
        print("Received request to process user query")
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        user_query = data['query']
        
        # Process the query using the AI service
        response = ai_service.get_response(user_query)
        
        return jsonify({
            'query': user_query,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


#This is Datu
#This is my next change
