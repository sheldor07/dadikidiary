#!/usr/bin/env python3
"""
DadiKi Diary - WordPress Utilities
This module provides functions for publishing content to WordPress.
"""

import os
import requests
import webbrowser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WordPressConfig:
    def __init__(self):
        self.wordpress = {
            "client_id": os.getenv("WORDPRESS_CLIENT_ID"),
            "client_secret": os.getenv("WORDPRESS_CLIENT_SECRET"),
            "redirect_uri": os.getenv("WORDPRESS_REDIRECT_URI"),
            "site_identifier": os.getenv("WORDPRESS_SITE_IDENTIFIER"),
            "access_token": os.getenv("WORDPRESS_ACCESS_TOKEN")
        }

def get_auth_token(client_id, client_secret, redirect_uri):
    """
    Get the authentication token using OAuth 2.0
    """
    # Step 1: Direct user to authorization page
    auth_url = f"https://public-api.wordpress.com/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    print(f"Please visit this URL in your browser to authorize the application:\n{auth_url}")
    
    # Optionally open the browser automatically
    try:
        webbrowser.open(auth_url)
    except:
        pass
    print(f"You'll see a url in the format: {redirect_uri}?code=<code>&state=<state>")
    # Step 2: Get the authorization code from the user
    auth_code = input("After authorizing, enter the code from the redirect URL: ")
    
    # Step 3: Exchange code for access token
    token_url = "https://public-api.wordpress.com/oauth2/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code != 200:
        print(f"Authentication error: {response.status_code}")
        print(response.text)
        return None
    
    # Return the access token
    return response.json().get("access_token")

def create_wordpress_post(access_token, site_identifier, post_data):
    """
    Create a post on WordPress.com using an existing access token
    
    Parameters:
    - access_token: Your OAuth access token
    - site_identifier: Your site ID or domain (e.g., 'yourblog.wordpress.com' or '12345')
    - post_data: Dictionary containing post parameters
    """
    # API endpoint
    api_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_identifier}/posts/new"
    
    # Headers with authorization
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Make the request
    response = requests.post(api_url, headers=headers, json=post_data)
    
    if response.status_code == 200:
        print("Post created successfully!")
        print(f"Post URL: {response.json().get('URL')}")
        return response.json()
    else:
        print(f"Error creating post: {response.status_code}")
        print(response.text)
        return None

def publish_to_wordpress(title, content):
    """
    Publish content to WordPress
    
    Args:
        title: The title of the post
        content: The content of the post
    """
    config = WordPressConfig().wordpress
    
    # Format content for WordPress (convert plain text to HTML paragraphs)
    html_content = ""
    for paragraph in content.split('\n\n'):
        if paragraph.strip():
            html_content += f"<p>{paragraph}</p>\n"
    
    # Post data
    post_data = {
        "title": title,
        "content": html_content,
        "status": "publish"  # or "draft" if you want to save without publishing
    }
    
    # Create the post
    result = create_wordpress_post(
        config["access_token"], 
        config["site_identifier"], 
        post_data
    )
    
    if result:
        print(f"Published to WordPress: {result.get('URL')}")
        return result.get('URL')
    else:
        print("Failed to publish to WordPress")
        return None

if __name__ == "__main__":
    # When run directly, help the user get their auth token
    config = WordPressConfig().wordpress
    
    print("\n=== WordPress Authentication Token Generator ===")
    print("This utility will help you get an authentication token for WordPress.")
    print("Make sure you have set the following environment variables in your .env file:")
    print("  - WORDPRESS_CLIENT_ID")
    print("  - WORDPRESS_CLIENT_SECRET")
    print("  - WORDPRESS_REDIRECT_URI")
    print("  - WORDPRESS_SITE_IDENTIFIER")
    
    # Check if we have the required config
    if not config["client_id"] or not config["client_secret"] or not config["redirect_uri"]:
        print("\nError: Missing required environment variables. Please check your .env file.")
        exit(1)
    
    print(f"\nUsing client ID: {config['client_id']}")
    print(f"Using redirect URI: {config['redirect_uri']}")
    print(f"Target site: {config['site_identifier']}")
    
    # Get the auth token
    token = get_auth_token(config["client_id"], config["client_secret"], config["redirect_uri"])
    
    if token:
        print("\n=== Success! ===")
        print(f"Your access token is: {token}")
        print("\nAdd this to your .env file as:")
        print(f"WORDPRESS_ACCESS_TOKEN={token}")
    else:
        print("\nFailed to get access token. Please try again.")