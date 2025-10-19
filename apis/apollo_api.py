# apis/apollo_integration.py
import os
import requests

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
BASE_URL = "https://api.apollo.io/v1"

HEADERS = {"Authorization": f"Bearer {APOLLO_API_KEY}"}

def search_leads(query: str, limit: int = 10) -> dict:
    """Search for leads matching a query"""
    url = f"{BASE_URL}/mixed_search"
    params = {"q": query, "page_size": limit}
    resp = requests.get(url, headers=HEADERS, params=params)
    return resp.json()

def send_email(campaign_id: str, recipient_email: str, subject: str, body: str) -> dict:
    """Send email via Apollo"""
    url = f"{BASE_URL}/campaigns/{campaign_id}/emails"
    payload = {"to": recipient_email, "subject": subject, "body": body}
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json()

def get_responses(campaign_id: str) -> dict:
    """Fetch responses for a campaign"""
    url = f"{BASE_URL}/campaigns/{campaign_id}/responses"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()
