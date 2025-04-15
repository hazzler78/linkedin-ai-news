from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime
from database import Database

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

db = Database()

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'landing.html')

@app.route('/<path:path>')
def serve_static(path):
    # First try to serve from static folder
    static_path = os.path.join('static', path)
    if os.path.exists(static_path):
        return send_from_directory('static', path)
    
    # Then try to serve from root
    if os.path.exists(path):
        directory = os.path.dirname(path) or '.'
        filename = os.path.basename(path)
        return send_from_directory(directory, filename)
    
    # Finally, try to serve from root as fallback
    return send_from_directory('.', path)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    
    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400
    
    if db.user_exists(email):
        return jsonify({'error': 'Email already registered'}), 409
    
    success = db.add_user(name, email)
    if success:
        return jsonify({'message': 'Registration successful'}), 201
    else:
        return jsonify({'error': 'Registration failed'}), 500

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Chatbot endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        email = data.get('email')
        
        if not email or not db.user_exists(email):
            return jsonify({'error': 'Please register first'}), 401
        
        if not DEEPSEEK_API_KEY:
            return jsonify({'error': 'DeepSeek API key is not configured'}), 500
        
        # Prepare the prompt for Deepseek
        prompt = f"""You are an AI assistant for LinkedIn AI News Poster, a service that helps professionals stay updated with AI news.
        Be helpful, professional, and concise in your responses.
        
        User message: {user_message}
        
        Respond in a helpful and engaging way, focusing on AI news, technology trends, and professional development.
        Keep responses under 200 words."""
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful AI assistant for LinkedIn AI News Poster. Be professional and concise.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'model': 'deepseek-chat',
            'temperature': 0.7,
            'max_tokens': 200
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            json=data,
            headers=headers
        )
        
        print(f"DeepSeek API Response Status: {response.status_code}")
        print(f"DeepSeek API Response Headers: {response.headers}")
        print(f"DeepSeek API Response Body: {response.text}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                ai_response = response_data['choices'][0]['message']['content']
                return jsonify({'response': ai_response})
            except (KeyError, IndexError) as e:
                print(f"Error parsing DeepSeek response: {str(e)}")
                print(f"Response content: {response.text}")
                return jsonify({'error': 'Failed to parse AI response'}), 500
        else:
            print(f"DeepSeek API error: {response.status_code}")
            print(f"Response content: {response.text}")
            return jsonify({'error': f'Failed to get response from AI (Status: {response.status_code})'}), 500
            
    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 