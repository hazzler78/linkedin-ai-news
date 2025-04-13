import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
import requests

# Load environment variables
load_dotenv()

def test_news_api():
    print("Testing News API...")
    news_api = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
    try:
        news = news_api.get_everything(
            q='artificial intelligence',
            language='en',
            sort_by='publishedAt',
            page_size=2
        )
        print("News API Response:")
        print(news)
    except Exception as e:
        print(f"News API Error: {e}")

def test_deepseek():
    print("\nTesting DeepSeek API...")
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Write a short test message about AI"}],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        print("DeepSeek API Response:")
        print(response.status_code)
        print(response.text)
    except Exception as e:
        print(f"DeepSeek API Error: {e}")

if __name__ == "__main__":
    test_news_api()
    test_deepseek() 