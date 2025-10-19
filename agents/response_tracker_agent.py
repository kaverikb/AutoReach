import requests
import datetime

class ResponseTrackerAgent:
    """
    Agent to monitor Apollo campaign email engagement and responses.
    Input: campaign_id from OutreachExecutorAgent
    Output: responses (list of open/click/reply events)
    """

    def __init__(self, **kwargs):
        """
        Initialize ResponseTrackerAgent.
        Accepts apollo_api_key if provided.
        """
        self.apollo_api_key = kwargs.get("api_key")
        self.base_url = "https://api.apollo.io/v1"

    def _fetch_campaign_emails(self, campaign_id: str):
        """
        Fetch all emails under a specific campaign from Apollo.
        """
        url = f"{self.base_url}/campaigns/{campaign_id}/emails"
        headers = {
            "Authorization": f"Bearer {self.apollo_api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return response.json().get("emails", [])
        except Exception as e:
            print(f"[ResponseTrackerAgent] Error fetching campaign emails: {e}")
            return []

    def _parse_response_event(self, email_event: dict) -> dict:
        """
        Parse Apollo email event object into standard workflow schema.
        """
        lead = email_event.get("contact_name") or email_event.get("recipient", "Unknown")
        company = email_event.get("account_name", "Unknown Company")
        email = email_event.get("recipient_email", "")
        opened = email_event.get("opened", False)
        clicked = email_event.get("clicked", False)
        replied = email_event.get("replied", False)
        reply_text = email_event.get("reply_text", None)
        timestamp = email_event.get("last_activity_at") or datetime.datetime.utcnow().isoformat()

        return {
            "lead": lead,
            "company": company,
            "email": email,
            "opened": opened,
            "clicked": clicked,
            "replied": replied,
            "reply_text": reply_text,
            "timestamp": timestamp
        }

    def run(self, campaign_id: str = None) -> dict:
        """
        Track email responses and engagement metrics.

        Args:
            campaign_id: ID of the email campaign (optional)

        Returns:
            dict with "responses" key containing list of response events
        """
        if not campaign_id:
            campaign_id = "autoreach_campaign_001"

        emails = self._fetch_campaign_emails(campaign_id)
        responses = [self._parse_response_event(e) for e in emails]

        return {"responses": responses}
