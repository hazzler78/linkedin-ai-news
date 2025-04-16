from flask import Flask
from app import app
import os

# Print environment info for debugging
print("\n=== Vercel App Initialization ===")
print("Environment variables:")
for key in os.environ:
    if 'TOKEN' in key or 'KEY' in key:
        print(f"- {key}: {'Present' if os.environ[key] else 'Missing'}")

print("\nVercel environment:")
print(f"- VERCEL_ENV: {os.getenv('VERCEL_ENV', 'development')}")
print(f"- VERCEL: {os.getenv('VERCEL', 'Not present')}")
print(f"- BLOB_TOKEN: {'Present' if os.getenv('BLOB_READ_WRITE_TOKEN') else 'Missing'}")

# This file is specifically for Vercel deployment
app = app

# Handle CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run() 