import os
import requests
from datetime import datetime

class OutreachExecutorAgent:
    def __init__(self, api_key, from_email=None):
        self.api_key = api_key
        self.from_email = from_email or os.getenv("FROM_EMAIL", "noreply@autoreach.io")
        self.from_name = "AutoReach"
        self.endpoint = "https://api.brevo.com/v3/smtp/email"

    def run(self, messages):
        sent_status = []
        campaign_id = f"autoreach_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }

        for idx, msg in enumerate(messages, start=1):
            error = None
            status = "sent"
            message_id = None
            
            payload = {
                "sender": {
                    "name": self.from_name,
                    "email": self.from_email
                },
                "to": [
                    {
                        "email": msg.get("email"),
                        "name": msg.get("lead")
                    }
                ],
                "subject": msg.get("subject"),
                "htmlContent": f"<p>{msg.get('email_body').replace(chr(10), '<br>')}</p>",
                "tags": ["autoreach", campaign_id]
            }

            try:
                response = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                message_id = data.get("messageId")
            except Exception as e:
                status = "failed"
                error = str(e)

            sent_status.append({
                "lead": msg.get("lead"),
                "email": msg.get("email"),
                "subject": msg.get("subject"),
                "campaign_id": campaign_id,
                "status": status,
                "message_id": message_id or f"msg_{idx}",
                "error": error
            })

        return {"sent_status": sent_status, "campaign_id": campaign_id}