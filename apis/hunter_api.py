# apis/hunter_integration.py
import os
import requests

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
BASE_URL = "https://api.hunter.io/v2"

def email_verifier(email: str) -> dict:
    """Verify email using Hunter.io"""
    url = f"{BASE_URL}/email-verifier?email={email}&api_key={HUNTER_API_KEY}"
    resp = requests.get(url)
    return resp.json()

def domain_search(domain: str, limit: int = 10) -> dict:
    """Get leads from a domain"""
    url = f"{BASE_URL}/domain-search?domain={domain}&limit={limit}&api_key={HUNTER_API_KEY}"
    resp = requests.get(url)
    return resp.json()
