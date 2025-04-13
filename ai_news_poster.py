import os
import requests
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

class AINewsPoster:
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.linkedin_id = os.getenv('LINKEDIN_PERSON_ID')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        # Configure retry strategy
        self.retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))
        
    def fetch_ai_news(self):
        """Fetch the latest AI-related news articles."""
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q': '("artificial intelligence" OR "machine learning" OR "ChatGPT" OR "OpenAI" OR "Google Gemini") AND (technology OR innovation OR research)',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 10,  # Fetch more articles to filter better ones
            'apiKey': self.news_api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json()['articles']
            
            # Filter out stock market news and prioritize tech news
            filtered_articles = [
                article for article in articles
                if not any(keyword in article['title'].lower() 
                          for keyword in ['stock', 'nasdaq', 'nyse', 'shares', 'market'])
            ]
            
            return filtered_articles[:5]  # Return top 5 filtered articles
        except requests.exceptions.Timeout:
            print("Error: Request timed out while fetching news")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error while fetching news: {e}")
            return []

    def format_news_post(self, articles):
        """Format the news articles into a LinkedIn post."""
        if not articles:
            return None
            
        try:
            # Get the current date
            today = datetime.now().strftime("%B %d, %Y")
            
            # Start with a header
            post_text = f"🤖 AI News Update - {today}\n\n"
            
            # Add each article
            for i, article in enumerate(articles[:3], 1):  # Limit to top 3 articles
                title = article['title'].split(' - ')[0]  # Remove source from title
                post_text += f"{i}. {title}\n"
                if article.get('description'):
                    # Truncate description if too long
                    desc = article['description'][:150] + '...' if len(article['description']) > 150 else article['description']
                    post_text += f"   {desc}\n"
                post_text += f"   Read more: {article['url']}\n\n"
            
            # Add hashtags
            post_text += "\n#ArtificialIntelligence #MachineLearning #AI #TechNews #Innovation"
            
            return post_text
        except Exception as e:
            print(f"Error formatting post: {e}")
            return None

    def post_to_linkedin(self, content):
        """Post the formatted content to LinkedIn."""
        post_data = {
            "author": f"urn:li:person:XxnmKJTOHu",  # Using the working LinkedIn ID
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = self.session.post(
                'https://api.linkedin.com/v2/ugcPosts',
                headers=headers,
                json=post_data,
                timeout=10
            )
            
            if response.status_code in [201, 200]:
                print("Successfully posted to LinkedIn!")
                print(f"Response: {response.text}")
                return True
            elif response.status_code == 401:
                print("Error: LinkedIn authentication failed. Please check your access token.")
                return False
            elif response.status_code == 403:
                print("Error: LinkedIn API access denied. Please check your permissions.")
                return False
            elif response.status_code == 429:
                print("Error: Rate limit exceeded. Will retry automatically.")
                return False
            else:
                print(f"Error posting to LinkedIn. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("Error: Request timed out while posting to LinkedIn")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error posting to LinkedIn: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while posting to LinkedIn: {e}")
            return False

    def run(self):
        """Main method to fetch news and post to LinkedIn."""
        try:
            print(f"\nStarting AI news post at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Fetching AI news...")
            articles = self.fetch_ai_news()
            
            if not articles:
                print("No articles found.")
                return
                
            print(f"Found {len(articles)} articles.")
            post_content = self.format_news_post(articles)
            
            if post_content:
                print("\nPost content preview:")
                print("-" * 50)
                print(post_content)
                print("-" * 50)
                print("\nPosting to LinkedIn...")
                self.post_to_linkedin(post_content)
            else:
                print("Failed to format post content.")
        except Exception as e:
            print(f"Unexpected error in main run loop: {e}")

def main():
    poster = AINewsPoster()
    
    # Schedule the job to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(poster.run)
    
    # Run immediately on startup
    poster.run()
    
    print("\nScheduler started. Will post daily at 9:00 AM.")
    print("Press Ctrl+C to exit.")
    
    # Keep the script running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            break
        except Exception as e:
            print(f"Error in scheduler loop: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main() 