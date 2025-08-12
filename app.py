from flask import Flask, request, jsonify
from services.ai_service import AIService
from flask_cors import CORS  # Import CORS to handle cross-origin requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

ai_service = AIService()

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