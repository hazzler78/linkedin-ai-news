import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_deepseek_api():
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("Error: DEEPSEEK_API_KEY not found in environment variables")
        return

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful AI assistant.'
            },
            {
                'role': 'user',
                'content': 'Say hello!'
            }
        ],
        'model': 'deepseek-chat',
        'temperature': 0.7,
        'max_tokens': 100
    }

    try:
        print("Testing DeepSeek API connection...")
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("Success! DeepSeek API is working correctly.")
        else:
            print(f"Error: API returned status code {response.status_code}")
            
    except Exception as e:
        print(f"Error connecting to DeepSeek API: {str(e)}")

if __name__ == "__main__":
    test_deepseek_api() 