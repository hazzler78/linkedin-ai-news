import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_linkedin_profile():
    """Get the LinkedIn profile information."""
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Try different endpoints to get profile information
    endpoints = [
        'https://api.linkedin.com/v2/me',
        'https://api.linkedin.com/v2/userinfo',
        'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
        'https://api.linkedin.com/v2/connections'
    ]
    
    for endpoint in endpoints:
        print(f"Trying endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print("-" * 50)

if __name__ == "__main__":
    get_linkedin_profile() 