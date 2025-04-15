from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Chatbot endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
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
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        else:
            return jsonify({'error': 'Failed to get response from AI'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 