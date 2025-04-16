from datetime import datetime
import os
import json
import requests
from typing import Optional, List, Dict
import urllib.parse

class Database:
    def __init__(self):
        print("\n=== Database Initialization ===")
        self.blob_api_url = "https://blob.vercel-storage.com"
        self.blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
        self.store_id = self.blob_token.split('_')[3] if self.blob_token else None
        self.users_prefix = "users/"
        self.user_paths = {}  # Store the full paths of user files
        
        print(f"Environment: {os.getenv('VERCEL_ENV', 'development')}")
        print(f"Blob Token: {self.blob_token[:20]}...")
        print(f"Store ID: {self.store_id}")
        print(f"Blob API URL: {self.blob_api_url}")
        
        if not self.blob_token:
            raise ValueError("BLOB_READ_WRITE_TOKEN environment variable is required")
            
        if not self.blob_token.startswith('vercel_blob_rw_'):
            raise ValueError("Invalid Blob token format. Token should start with 'vercel_blob_rw_'")
        
        # Initialize users index if it doesn't exist
        self._ensure_users_index_exists()
        
        # Load existing user paths
        self._load_user_paths()

    def _get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.blob_token}",
            "Content-Type": "application/json"
        }
        print(f"Using headers: {json.dumps(headers, indent=2)}")
        return headers

    def _encode_email(self, email: str) -> str:
        """Safely encode email for use in URLs"""
        return urllib.parse.quote(email, safe='')

    def _get_public_url(self, path: str) -> str:
        """Get the public URL for a blob"""
        return f"https://{self.store_id}.public.blob.vercel-storage.com/{path}"

    def _ensure_users_index_exists(self):
        """Ensure the users index file exists in Blob storage."""
        try:
            print("\nChecking users index...")
            index_url = f"{self.blob_api_url}/{self.users_prefix}_index.json"
            print(f"Index URL: {index_url}")
            
            headers = self._get_headers()
            response = requests.get(
                index_url,
                headers=headers,
                timeout=5
            )
            
            print(f"Index check response: {response.status_code}")
            
            if response.status_code == 404:
                print("Creating users index...")
                response = requests.put(
                    index_url,
                    headers=headers,
                    json={"emails": []},
                    timeout=5
                )
                print(f"Index creation response: {response.status_code}")
                if response.status_code == 200:
                    print("Users index created successfully")
                else:
                    print(f"Failed to create users index: {response.status_code}")
                    print(f"Response: {response.text}")
            elif response.status_code == 200:
                print("Users index exists")
                print(f"Current index: {response.text}")
            else:
                print(f"Error checking users index: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Error ensuring users index exists: {e}")

    def _load_user_paths(self):
        """Load existing user paths from the index"""
        try:
            print("\nLoading user paths...")
            index_url = f"{self.blob_api_url}/{self.users_prefix}_index.json"
            response = requests.get(
                index_url,
                headers=self._get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                index_data = response.json()
                if isinstance(index_data, dict) and 'paths' in index_data:
                    self.user_paths = index_data['paths']
                    print(f"Loaded {len(self.user_paths)} user paths")
                else:
                    print("Creating new paths index")
                    self.user_paths = {}
            else:
                print("No existing paths index found")
                self.user_paths = {}
        except Exception as e:
            print(f"Error loading user paths: {e}")
            self.user_paths = {}

    def _update_users_index(self, email: str, file_path: str = None) -> bool:
        """Update the users index in Vercel Blob Storage."""
        try:
            print("\nUpdating users index...")
            index_url = f"{self.blob_api_url}/{self.users_prefix}_index.json"
            print(f"Index URL: {index_url}")
            
            # Update paths dictionary
            if file_path:
                self.user_paths[email] = file_path
            
            # Create index data with both emails list and paths dictionary
            index_data = {
                'emails': list(self.user_paths.keys()),
                'paths': self.user_paths
            }
            
            # Update index
            print("Saving updated index...")
            response = requests.put(
                index_url,
                headers=self._get_headers(),
                json=index_data,
                timeout=5
            )
            
            print(f"Save index response: {response.status_code}")
            if response.status_code == 200:
                print(f"Updated index content: {response.text}")
            
            success = response.status_code == 200
            print(f"Index update success: {success}")
            return success
            
        except Exception as e:
            print(f"Error updating users index: {e}")
            return False

    def add_user(self, name: str, email: str) -> bool:
        """Add a new user to Vercel Blob Storage."""
        try:
            print(f"\nAttempting to add user: {email}")
            
            # Check if user exists
            if self.user_exists(email):
                print(f"User already exists: {email}")
                return True
            
            # Create user data
            user_data = {
                'name': name,
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to Vercel Blob
            print("Saving user data...")
            encoded_email = self._encode_email(email)
            user_url = f"{self.blob_api_url}/{self.users_prefix}{encoded_email}.json"
            print(f"User URL: {user_url}")
            
            response = requests.put(
                user_url,
                headers=self._get_headers(),
                json=user_data,
                timeout=10
            )
            
            print(f"Save user response: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                print("User data saved successfully")
                # Extract the full path from the response
                response_data = response.json()
                file_url = response_data.get('url', '')
                if file_url:
                    # Update the index with the full path
                    success = self._update_users_index(email, file_url)
                    if success:
                        print("Users index updated successfully")
                        return True
                    else:
                        print("Failed to update users index")
                        return False
            
            print(f"Failed to save user data: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    def user_exists(self, email: str) -> bool:
        """Check if a user exists in Vercel Blob Storage."""
        try:
            print(f"\nChecking if user exists: {email}")
            
            # Check if we have the user's file path
            if email in self.user_paths:
                file_url = self.user_paths[email]
                print(f"Found stored path: {file_url}")
                
                # Try to access the file
                response = requests.get(file_url, timeout=5)
                print(f"User check response: {response.status_code}")
                
                if response.status_code == 200:
                    print("User found using stored path")
                    return True
            
            # If no stored path or file not found, check the index
            index_url = f"{self.blob_api_url}/{self.users_prefix}_index.json"
            response = requests.get(
                index_url,
                headers=self._get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                try:
                    index_data = response.json()
                    emails = index_data.get('emails', [])
                    exists = email in emails
                    print(f"User found in index: {exists}")
                    return exists
                except Exception as e:
                    print(f"Error parsing index data: {e}")
            
            return False
            
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user information from Vercel Blob Storage."""
        try:
            response = requests.get(
                f"{self.blob_api_url}/{self.users_prefix}{email}.json",
                headers=self._get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            
            print(f"Failed to get user. Status: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def get_all_users(self) -> List[Dict]:
        """Get all users from Vercel Blob Storage."""
        try:
            # Get users index
            response = requests.get(
                f"{self.blob_api_url}/{self.users_prefix}_index.json",
                headers=self._get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                index_data = response.json()
                emails = index_data.get('emails', [])
                
                # Get all user data
                users = []
                for email in emails:
                    user_data = self.get_user_by_email(email)
                    if user_data:
                        users.append(user_data)
                
                return sorted(users, key=lambda x: x['created_at'], reverse=True)
            
            print(f"Failed to get users index. Status: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []

    def get_user_count(self) -> int:
        """Get the total number of users."""
        try:
            users = self.get_all_users()
            return len(users)
        except Exception as e:
            print(f"Error getting user count: {e}")
            return 0 