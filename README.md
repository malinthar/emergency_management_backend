# Backend

## Setup with Virtual Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. To deactivate the virtual environment when done:
   ```bash
   deactivate
   ```

## API Documentation

### User Query Endpoint

**Endpoint:** `/api/query`  
**Method:** POST  
**Description:** Process user queries and return AI-generated responses

**Request Body:**
```json
{
  "query": "User's question text"
}
```

**Response:**
```json
{
  "query": "User's question text",
  "response": "AI-generated response"
}
```

**Error Responses:**
- 400: Missing query parameter
- 500: Server error
