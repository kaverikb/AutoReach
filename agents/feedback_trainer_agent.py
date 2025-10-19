import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class FeedbackTrainerAgent:
    """
    Agent to analyze responses and log feedback to Google Sheets.
    Input: responses from ResponseTrackerAgent
    Output: recommendations (array of suggested improvements)
    """

    def __init__(self, sheet_id=None):
        """
        Initialize FeedbackTrainerAgent.
        Accepts sheet_id if provided.
        """
        self.sheet_id = sheet_id or os.getenv("SHEET_ID")
        self.creds_path = "credentials/service_account.json"
        self.sheet = None
        self._init_sheets()

    def _init_sheets(self):
        """Initialize Google Sheets connection."""
        try:
            print(f"[DEBUG] SHEET_ID: {self.sheet_id}")
            print(f"[DEBUG] Creds path: {self.creds_path}")
            print(f"[DEBUG] Creds file exists: {os.path.exists(self.creds_path)}")
            
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_path, scope)
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(self.sheet_id).sheet1
            print(f"[FeedbackTrainer] Connected to Google Sheet: {self.sheet_id}")
        except Exception as e:
            print(f"[FeedbackTrainer] Warning: Could not connect to Google Sheets: {e}")
            self.sheet = None

    def _log_to_sheets(self, data):
        """Log workflow results to Google Sheets."""
        if not self.sheet:
            print("[FeedbackTrainer] No sheet connection available — skipping write.")
            return

        try:
            # Prepare header row if sheet is empty
            if len(self.sheet.get_all_values()) == 0:
                headers = ["Timestamp", "Campaign ID", "Total Sent", "Open Rate", "Click Rate", "Reply Rate", "Recommendations"]
                self.sheet.insert_row(headers, 1)

            # Format recommendations as comma-separated string
            recommendations = ", ".join(data.get("recommendations", []))

            # Add row with workflow results
            row = [
                data.get("timestamp"),
                data.get("campaign_id"),
                data.get("total_sent"),
                f"{data.get('open_rate', 0):.1f}%",
                f"{data.get('click_rate', 0):.1f}%",
                f"{data.get('reply_rate', 0):.1f}%",
                recommendations
            ]
            self.sheet.append_row(row)
            print(f"[FeedbackTrainer] Logged results to Google Sheet")
        except Exception as e:
            print(f"[FeedbackTrainer] Error writing to sheet: {e}")

    def run(self, responses: list = None) -> dict:
        """
        Analyze email responses and generate recommendations.
        
        Args:
            responses: List of response dicts from ResponseTrackerAgent

        Returns:
            dict with "recommendations" and "analytics" keys
        """
        
        if responses is None or len(responses) == 0:
            responses = [
                {
                    "lead": "Jane Doe",
                    "opened": True,
                    "clicked": False,
                    "replied": True,
                    "timestamp": "2025-10-19T09:00:00"
                },
                {
                    "lead": "Alice Smith",
                    "opened": True,
                    "clicked": True,
                    "replied": False,
                    "timestamp": "2025-10-19T09:30:00"
                }
            ]

        # Analyze response metrics
        total_responses = len(responses)
        opened_count = sum(1 for r in responses if r.get("opened", False))
        clicked_count = sum(1 for r in responses if r.get("clicked", False))
        replied_count = sum(1 for r in responses if r.get("replied", False))

        open_rate = (opened_count / total_responses * 100) if total_responses > 0 else 0
        click_rate = (clicked_count / total_responses * 100) if total_responses > 0 else 0
        reply_rate = (replied_count / total_responses * 100) if total_responses > 0 else 0

        recommendations = []

        # Generate recommendations based on engagement metrics
        if open_rate < 30:
            recommendations.append(
                f"Low open rate ({open_rate:.1f}%). Consider tweaking subject lines and send times."
            )
        
        if click_rate < 10:
            recommendations.append(
                "Low click-through rate. Add more compelling CTAs and improve email formatting."
            )
        
        if reply_rate < 5:
            recommendations.append(
                "Low reply rate. Improve email personalization and focus on addressing specific pain points."
            )
        
        if open_rate > 50 and reply_rate < 10:
            recommendations.append(
                "High opens but low replies. Your subject line is working, but body content needs refinement."
            )
        
        if reply_rate > 20:
            recommendations.append(
                "Great reply rate! Consider increasing ICP targeting scope to find more similar prospects."
            )

        if not recommendations:
            recommendations.append(
                "Campaign metrics look good. Continue with current strategy and A/B test subject variations."
            )

        # Prepare data for logging
        log_data = {
            "timestamp": responses[0].get("timestamp") if responses else "",
            "campaign_id": "autoreach_campaign",
            "total_sent": total_responses,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "reply_rate": reply_rate,
            "recommendations": recommendations
        }

        # Log to Google Sheets
        self._log_to_sheets(log_data)

        return {
            "recommendations": recommendations,
            "analytics": {
                "total_sent": total_responses,
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "reply_rate": round(reply_rate, 2),
                "opened_count": opened_count,
                "clicked_count": clicked_count,
                "replied_count": replied_count
            }
        }