from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

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

# Chatbot endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    # Here you can integrate with your AI model
    # For now, we'll return a simple response
    response = {
        'response': f"I received your message: {message}. This is a placeholder response. Integrate your AI model here."
    }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 