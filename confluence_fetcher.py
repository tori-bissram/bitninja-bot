import requests
import os
from dotenv import load_dotenv

load_dotenv()

CONFLUENCE_BASE_URL = "https://contentstack-sandbox.atlassian.net"
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")  # Your Atlassian email

def get_confluence_content():
    """Fetch all pages from Confluence space"""
    headers = {
        "Accept": "application/json"
    }
    
    auth = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    
    # Get all pages from the space
    space_key = "~712020bdad7f4779c741cead4c6f18c0daeeb5"
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content"
    
    params = {
        "spaceKey": space_key,
        "expand": "body.storage,title",
        "limit": 100
    }
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    if response.status_code == 200:
        pages = response.json()["results"]
        return [(page["title"], page["body"]["storage"]["value"]) for page in pages]
    else:
        print(f"Error fetching Confluence content: {response.status_code}")
        return []

