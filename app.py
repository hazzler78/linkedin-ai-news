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

# Chatbot endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    
    # Simple response logic based on keywords
    if 'hello' in message or 'hi' in message or 'hey' in message:
        response = "Hello! I'm your AI assistant for LinkedIn AI News Poster. How can I help you today?"
    elif 'help' in message:
        response = "I can help you with: \n- Setting up the LinkedIn AI News Poster\n- Configuring API keys\n- Understanding how the system works\n- Troubleshooting issues\nWhat would you like to know more about?"
    elif 'setup' in message or 'install' in message or 'configure' in message:
        response = "To set up LinkedIn AI News Poster:\n1. Clone the repository\n2. Install dependencies with 'pip install -r requirements.txt'\n3. Create a .env file with your API keys\n4. Run the script with 'python ai_news_poster.py'"
    elif 'api' in message and 'key' in message:
        response = "You need two API keys:\n1. LinkedIn API: Get from LinkedIn Developer Portal\n2. NewsAPI: Sign up at newsapi.org\nAdd them to your .env file as LINKEDIN_ACCESS_TOKEN and NEWS_API_KEY"
    elif 'schedule' in message or 'time' in message:
        response = "The default posting schedule is 9:00 AM daily. You can modify this in the ai_news_poster.py file."
    elif 'news' in message or 'article' in message:
        response = "The system fetches AI-related news from NewsAPI, filters out stock market news, and focuses on technology and innovation."
    elif 'linkedin' in message and 'post' in message:
        response = "The system automatically formats news into professional LinkedIn posts and publishes them to your profile."
    elif 'error' in message or 'problem' in message or 'issue' in message:
        response = "If you're experiencing issues, check:\n1. Your API keys are correct\n2. Your internet connection\n3. The logs for specific error messages\n4. Your LinkedIn permissions include 'w_member_social'"
    elif 'thank' in message:
        response = "You're welcome! Let me know if you need anything else."
    elif 'bye' in message or 'goodbye' in message:
        response = "Goodbye! Have a great day!"
    else:
        # Try to fetch a relevant news article as a response
        try:
            news_api_key = os.getenv('NEWS_API_KEY')
            if news_api_key:
                news_response = requests.get(
                    f"https://newsapi.org/v2/everything?q=artificial+intelligence&sortBy=publishedAt&apiKey={news_api_key}&pageSize=1"
                )
                if news_response.status_code == 200:
                    news_data = news_response.json()
                    if news_data.get('articles') and len(news_data['articles']) > 0:
                        article = news_data['articles'][0]
                        response = f"Here's a recent AI news article: {article['title']}\n\n{article['description']}\n\nRead more at: {article['url']}"
                    else:
                        response = "I couldn't find any recent AI news articles. Is there something specific about LinkedIn AI News Poster you'd like to know?"
                else:
                    response = "I'm having trouble fetching news articles right now. How else can I help you with LinkedIn AI News Poster?"
            else:
                response = "I'm not sure I understand. Could you ask about setting up the LinkedIn AI News Poster, API keys, scheduling, or how it works?"
        except Exception as e:
            print(f"Error fetching news: {e}")
            response = "I'm having trouble processing your request. Could you try asking about the LinkedIn AI News Poster setup, API keys, or scheduling?"
    
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 