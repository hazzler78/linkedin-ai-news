from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime
from database import Database
from functools import wraps

# Force reload environment variables
print("\n=== Loading Environment Variables ===")
if os.path.exists('.env'):
    print("Found .env file, loading variables...")
    load_dotenv(override=True)
    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
    print(f"Loaded BLOB_READ_WRITE_TOKEN: {blob_token[:20]}...")
else:
    print("No .env file found, using system environment variables")

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Initialize database with environment variables
db = Database()

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return ('Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

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
        print("\n=== Chat Endpoint ===")
        data = request.json
        user_message = data.get('message', '')
        email = data.get('email')
        
        print(f"Request data:")
        print(f"- Email: {email}")
        print(f"- Message length: {len(user_message)}")
        print(f"- Headers: {dict(request.headers)}")
        
        if not email:
            print("Error: No email provided")
            return jsonify({'error': 'Please register first'}), 401
        
        print("\nChecking user existence...")
        user_exists = db.user_exists(email)
        print(f"User exists result: {user_exists}")
        
        if not user_exists:
            print("Error: User not found")
            return jsonify({'error': 'Please register first'}), 401
        
        if not DEEPSEEK_API_KEY:
            print("Error: DeepSeek API key not configured")
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

@app.route('/admin/dashboard')
@requires_auth
def admin_dashboard():
    users = db.get_all_users()
    user_count = db.get_user_count()
    
    # Simple HTML template for the dashboard
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Registration Statistics</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .stats { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f0f0f0; }
            .count { font-size: 24px; font-weight: bold; color: #2196F3; }
        </style>
    </head>
    <body>
        <h1>Admin Dashboard</h1>
        <div class="stats">
            <h2>Total Registrations: <span class="count">{{ user_count }}</span></h2>
        </div>
        <h2>Recent Registrations</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Registration Date</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user.id }}</td>
                <td>{{ user.name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.created_at }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(dashboard_html, users=users, user_count=user_count)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 