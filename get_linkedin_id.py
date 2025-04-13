import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_linkedin_member_id():
    """Get the LinkedIn member ID using the access token."""
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    # First, try to get the profile using the /v2/me endpoint
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Try the /v2/me endpoint
    response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    
    if response.status_code == 200:
        profile_data = response.json()
        member_id = profile_data.get('id')
        if member_id:
            print(f"LinkedIn Member ID: {member_id}")
            return member_id
    
    # If that fails, try the /v2/userinfo endpoint
    response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
    
    if response.status_code == 200:
        profile_data = response.json()
        sub = profile_data.get('sub')
        if sub:
            print(f"LinkedIn User ID: {sub}")
            return sub
    
    # If both fail, try to get the profile using the /v2/emailAddress endpoint
    response = requests.get('https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))', headers=headers)
    
    if response.status_code == 200:
        email_data = response.json()
        elements = email_data.get('elements', [])
        if elements:
            handle = elements[0].get('handle~', {}).get('emailAddress')
            if handle:
                print(f"LinkedIn Email: {handle}")
                return handle
    
    print("Failed to get LinkedIn ID. Response:")
    print(response.text)
    return None

if __name__ == "__main__":
    member_id = get_linkedin_member_id()
    
    if member_id:
        # Update the .env file with the member ID
        env_path = '.env'
        
        # Read the current .env file
        with open(env_path, 'r') as file:
            lines = file.readlines()
        
        # Update the person ID
        updated_lines = []
        for line in lines:
            if line.startswith('LINKEDIN_PERSON_ID='):
                updated_lines.append(f'LINKEDIN_PERSON_ID={member_id}\n')
            else:
                updated_lines.append(line)
        
        # Write the updated .env file
        with open(env_path, 'w') as file:
            file.writelines(updated_lines)
        
        print("Updated .env file with LinkedIn Member ID.") 