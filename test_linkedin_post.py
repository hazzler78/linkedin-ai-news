import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_linkedin_post():
    """Test posting a message to LinkedIn."""
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    # The correct LinkedIn ID from the userinfo endpoint
    linkedin_id = "XxnmKJTOHu"
    
    # Construct the post data
    post_data = {
        "author": f"urn:li:person:{linkedin_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "This is a test post from our AI news poster!"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Send the request
    response = requests.post(
        'https://api.linkedin.com/v2/ugcPosts',
        headers=headers,
        json=post_data
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

if __name__ == "__main__":
    test_linkedin_post() 