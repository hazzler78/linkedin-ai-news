import os
import requests
from dotenv import load_dotenv
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

# Load environment variables
load_dotenv()

# LinkedIn OAuth settings
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8000/callback'
SCOPES = 'openid profile w_member_social email'

# Store the authorization code
auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        
        # Parse the query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if 'code' in query_components:
            # Get the authorization code
            auth_code = query_components['code'][0]
            
            # Send a success response to the browser
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the application.</p>
                </body>
            </html>
            """
            self.wfile.write(response.encode())
            
            # Stop the server
            self.server.running = False
        else:
            # Send an error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization failed!")

def get_access_token(auth_code):
    """Exchange the authorization code for an access token."""
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get('access_token')
    else:
        print(f"Error getting access token: {response.text}")
        return None

def get_profile_id(access_token):
    """Get the user's LinkedIn profile ID."""
    # With the new scopes, we need to use a different endpoint
    profile_url = 'https://api.linkedin.com/v2/userinfo'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    response = requests.get(profile_url, headers=headers)
    
    if response.status_code == 200:
        profile_data = response.json()
        # The sub field contains the user's unique identifier
        return profile_data.get('sub')
    else:
        print(f"Error getting profile ID: {response.text}")
        return None

def main():
    # Construct the authorization URL
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}"
    
    # Open the authorization URL in the browser
    print("Opening browser for LinkedIn authorization...")
    webbrowser.open(auth_url)
    
    # Start a local server to receive the callback
    server = HTTPServer(('localhost', 8000), OAuthHandler)
    server.running = True
    
    print("Waiting for authorization...")
    while server.running:
        server.handle_request()
    
    server.server_close()
    
    if auth_code:
        print("Authorization code received!")
        
        # Exchange the authorization code for an access token
        access_token = get_access_token(auth_code)
        
        if access_token:
            print("Access token received!")
            
            # Get the user's profile ID
            profile_id = get_profile_id(access_token)
            
            if profile_id:
                print(f"Profile ID: {profile_id}")
                
                # Update the .env file with the new access token and profile ID
                update_env_file(access_token, profile_id)
                
                print("LinkedIn authentication successful!")
                print("Your .env file has been updated with the new access token and profile ID.")
            else:
                print("Failed to get profile ID.")
        else:
            print("Failed to get access token.")
    else:
        print("Failed to get authorization code.")

def update_env_file(access_token, profile_id):
    """Update the .env file with the new access token and profile ID."""
    env_path = '.env'
    
    # Read the current .env file
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    # Update the access token and profile ID
    updated_lines = []
    for line in lines:
        if line.startswith('LINKEDIN_ACCESS_TOKEN='):
            updated_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}\n')
        elif line.startswith('LINKEDIN_PERSON_ID='):
            # Store just the ID part without the 'person:' prefix
            updated_lines.append(f'LINKEDIN_PERSON_ID={profile_id}\n')
        else:
            updated_lines.append(line)
    
    # Write the updated .env file
    with open(env_path, 'w') as file:
        file.writelines(updated_lines)

if __name__ == "__main__":
    main() 