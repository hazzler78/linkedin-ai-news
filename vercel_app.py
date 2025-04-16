from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from database import Database
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
print("\n=== Vercel App Initialization ===")
print("Environment variables:")
for var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'DEEPSEEK_API_KEY', 'NEWS_API_KEY']:
    print(f"- {var}: {'Present' if os.getenv(var) else 'Missing'}")
print("Vercel environment:")
for var in ['VERCEL_ENV', 'VERCEL']:
    print(f"- {var}: {os.getenv(var, 'Not set')}")
print(f"- BLOB_TOKEN: {'Present' if os.getenv('BLOB_READ_WRITE_TOKEN') else 'Missing'}")

try:
    db = Database()
    db_initialized = db.initialized
    if not db_initialized:
        logger.warning("Database not initialized. Some functionality will be limited.")
except Exception as e:
    logger.error(f"Error initializing database: {e}")
    db_initialized = False

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# API routes
@app.route('/api/register', methods=['POST'])
def register():
    if not db_initialized:
        return jsonify({"error": "Database service is currently unavailable. Please try again later."}), 503
        
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({"error": "Name and email are required"}), 400
            
        success = db.add_user(name, email)
        if success:
            return jsonify({"message": "User registered successfully"}), 200
        else:
            return jsonify({"error": "Failed to register user"}), 500
    except Exception as e:
        logger.error(f"Error in register endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    if not db_initialized:
        return jsonify({"error": "Database service is currently unavailable. Please try again later."}), 503
        
    try:
        data = request.json
        email = data.get('email')
        message = data.get('message')
        
        if not email or not message:
            return jsonify({"error": "Email and message are required"}), 400
            
        # Check if user exists
        if not db.user_exists(email):
            return jsonify({"error": "Please register first"}), 401
            
        # Call DeepSeek API
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            return jsonify({"error": "DeepSeek API key not configured"}), 500
            
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are a helpful AI assistant for LinkedIn AI News Poster.
User email: {email}
User message: {message}

Please provide a helpful response."""
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant for LinkedIn AI News Poster."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        
        print(f"DeepSeek API Response Status: {response.status_code}")
        print(f"DeepSeek API Response Headers: {response.headers}")
        print(f"DeepSeek API Response Body: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                ai_response = response_data['choices'][0]['message']['content']
                return jsonify({"response": ai_response}), 200
            else:
                return jsonify({"error": "Invalid response from DeepSeek API"}), 500
        else:
            error_message = response.text
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_message = error_data['error']
            except:
                pass
            return jsonify({"error": f"DeepSeek API error: {error_message}"}), response.status_code
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    if not db_initialized:
        return jsonify({"error": "Database service is currently unavailable. Please try again later."}), 503
        
    try:
        users = db.get_all_users()
        return jsonify({"users": users}), 200
    except Exception as e:
        logger.error(f"Error in get_users endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user-count', methods=['GET'])
def get_user_count():
    if not db_initialized:
        return jsonify({"error": "Database service is currently unavailable. Please try again later."}), 503
        
    try:
        count = db.get_user_count()
        return jsonify({"count": count}), 200
    except Exception as e:
        logger.error(f"Error in get_user_count endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True) 