import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

def log_message(message, level="INFO"):
    """Log messages with timestamp and level."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

class AINewsPoster:
    def __init__(self):
        # Check for required environment variables
        required_vars = {
            'LINKEDIN_ACCESS_TOKEN': os.getenv('LINKEDIN_ACCESS_TOKEN'),
            'LINKEDIN_PERSON_ID': os.getenv('LINKEDIN_PERSON_ID'),
            'NEWS_API_KEY': os.getenv('NEWS_API_KEY'),
            'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY')
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            log_message(error_msg, "ERROR")
            raise ValueError(error_msg)

        self.access_token = required_vars['LINKEDIN_ACCESS_TOKEN']
        self.linkedin_id = required_vars['LINKEDIN_PERSON_ID']
        self.news_api_key = required_vars['NEWS_API_KEY']
        self.deepseek_api_key = required_vars['DEEPSEEK_API_KEY']
        
        log_message(f"Initialized with LinkedIn ID: {self.linkedin_id}")
        
        # Configure retry strategy
        self.retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))

    def analyze_article(self, article):
        """Use Deepseek AI to analyze the article and generate insights."""
        try:
            # Combine title and description for analysis
            content = f"{article['title']}\n{article.get('description', '')}"
            
            prompt = """Analyze this AI news article and provide exactly three parts, separated by '|' characters:

1. Key takeaway (one clear sentence)
2. Impact on industry/society (one clear sentence)
3. Why it matters for professionals (one clear sentence)

Important: Your response MUST follow this EXACT format:
[Key takeaway sentence] | [Impact sentence] | [Why it matters sentence]

Example format:
New AI model achieves breakthrough in medical diagnosis | This advancement could revolutionize healthcare delivery worldwide | Medical professionals can now diagnose conditions with greater accuracy and speed.

Article to analyze:
{content}"""
            
            headers = {
                'Authorization': f'Bearer {self.deepseek_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messages': [
                    {
                        'role': 'system', 
                        'content': 'You are an AI expert analyzing tech news. Be concise and insightful. Always respond in the exact format requested, using | as separators.'
                    },
                    {
                        'role': 'user', 
                        'content': prompt.format(content=content)
                    }
                ],
                'model': 'deepseek-chat',
                'temperature': 0.5,  # Reduced temperature for more consistent formatting
                'max_tokens': 200
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                response_content = response.json()['choices'][0]['message']['content'].strip()
                
                # More robust splitting and validation
                parts = [part.strip() for part in response_content.split('|')]
                
                if len(parts) != 3:
                    print(f"Warning: Unexpected response format from Deepseek: {response_content}")
                    # Fallback analysis if format is wrong
                    return {
                        'takeaway': response_content[:100] + "..." if len(response_content) > 100 else response_content,
                        'impact': "This development could have significant implications for the AI industry.",
                        'why_matters': "Professionals should monitor these developments to stay competitive."
                    }
                
                return {
                    'takeaway': parts[0].strip(),
                    'impact': parts[1].strip(),
                    'why_matters': parts[2].strip()
                }
            else:
                print(f"Error from Deepseek API: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error analyzing article: {e}")
            # Return a default analysis rather than None
            return {
                'takeaway': "This article discusses important developments in AI technology.",
                'impact': "These developments could significantly influence the AI landscape.",
                'why_matters': "Staying informed about AI advancements is crucial for professional growth."
            }

    def fetch_ai_news(self):
        """Fetch the latest AI-related news articles."""
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q': '("artificial intelligence" OR "machine learning" OR "ChatGPT" OR "OpenAI" OR "Google Gemini") AND (technology OR innovation OR research)',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 10,
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
            
            # Add AI analysis to each article
            for article in filtered_articles[:3]:
                article['analysis'] = self.analyze_article(article)
            
            return filtered_articles[:3]
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def format_news_post(self, articles):
        """Format the news articles into a LinkedIn post with AI insights."""
        if not articles:
            return None
            
        try:
            today = datetime.now().strftime("%B %d, %Y")
            
            # Start with an engaging header
            post_text = f"🤖 AI Innovation Digest - {today}\n\n"
            post_text += "Today's curated insights on the latest AI developments, analyzed by our AI for busy professionals.\n\n"
            
            # Add each article with AI analysis
            for i, article in enumerate(articles, 1):
                # Clean up title by removing any line breaks and extra spaces
                title = ' '.join(article['title'].split(' - ')[0].split())
                post_text += f"📰 {i}. {title}\n\n"
                
                if article.get('analysis'):
                    # Clean up analysis text and ensure proper line breaks
                    takeaway = ' '.join(article['analysis']['takeaway'].split())
                    impact = ' '.join(article['analysis']['impact'].split())
                    why_matters = ' '.join(article['analysis']['why_matters'].split())
                    
                    post_text += f"🔍 Key Takeaway: {takeaway}\n"
                    post_text += f"💡 Impact: {impact}\n"
                    post_text += f"💼 Why It Matters: {why_matters}\n"
                
                # Clean up URL and ensure it's on its own line
                url = article['url'].strip()
                post_text += f"🔗 Read more: {url}\n\n"
            
            # Add our service promotion
            post_text += "-------------------\n"
            post_text += "🚀 Want AI-powered insights for your LinkedIn presence?\n"
            post_text += "Check out our AI News Poster service: https://linkedin-ai-news.vercel.app\n"
            post_text += "Stay ahead of the curve with automated, intelligent content curation.\n\n"
            
            # Add relevant hashtags
            post_text += "#ArtificialIntelligence #AIInnovation #TechNews #FutureOfWork #LinkedInAutomation"
            
            return post_text
        except Exception as e:
            print(f"Error formatting post: {e}")
            return None

    def post_to_linkedin(self, content):
        """Post the formatted content to LinkedIn."""
        if not content:
            log_message("No content to post", "ERROR")
            return False

        log_message("Attempting to post to LinkedIn...")
        log_message(f"Using LinkedIn ID: {self.linkedin_id}")
        
        post_data = {
            "author": f"urn:li:person:{self.linkedin_id}",
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
            log_message("Sending POST request to LinkedIn API...")
            response = self.session.post(
                'https://api.linkedin.com/v2/ugcPosts',
                json=post_data,
                headers=headers,
                timeout=10
            )
            
            log_message(f"LinkedIn API Response Status: {response.status_code}")
            log_message(f"LinkedIn API Response: {response.text}")
            
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            log_message(f"Error posting to LinkedIn: {str(e)}", "ERROR")
            log_message(f"Response content: {getattr(e.response, 'text', 'No response content')}", "ERROR")
            return False

    def run(self):
        """Run the news posting process."""
        try:
            log_message("Starting news posting process...")
            
            # Fetch news articles
            log_message("Fetching AI news articles...")
            articles = self.fetch_ai_news()
            if not articles:
                log_message("No articles found", "ERROR")
                return False
            log_message(f"Found {len(articles)} articles")
            
            # Format the post
            log_message("Formatting news post...")
            post_content = self.format_news_post(articles)
            if not post_content:
                log_message("Failed to format post content", "ERROR")
                return False
            log_message("Post content formatted successfully")
            
            # Post to LinkedIn
            log_message("Posting to LinkedIn...")
            success = self.post_to_linkedin(post_content)
            
            if success:
                log_message("Successfully posted to LinkedIn!")
                return True
            else:
                log_message("Failed to post to LinkedIn", "ERROR")
                return False
                
        except Exception as e:
            log_message(f"Unexpected error: {str(e)}", "ERROR")
            return False

if __name__ == "__main__":
    try:
        poster = AINewsPoster()
        success = poster.run()
        if not success:
            log_message("Script completed with errors", "ERROR")
            sys.exit(1)
        log_message("Script completed successfully")
    except Exception as e:
        log_message(f"Fatal error: {str(e)}", "ERROR")
        sys.exit(1) 