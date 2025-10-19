import requests

class DataEnrichmentAgent:
    """
    Agent to enrich lead data using Hunter.io API.
    Input: leads from ProspectSearchAgent
    Output: enriched leads with company info, role, and technologies.
    """

    def __init__(self, **kwargs):
        """
        Initialize DataEnrichmentAgent.
        Accepts hunter_api_key if provided.
        """
        self.hunter_api_key = kwargs.get("api_key")

    def fetch_role_from_hunter(self, email: str) -> str:
        """
        Use Hunter.io API to fetch role/title for a given email.
        Returns a role string or None if not found.
        """
        try:
            url = f"https://api.hunter.io/v2/email-finder?email={email}&api_key={self.hunter_api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("position")
        except Exception as e:
            print(f"Hunter.io lookup failed for {email}: {e}")
        return None

    def run(self, leads: list = None) -> dict:
        """
        Enrich lead data with role, technologies, and engagement scores.

        Args:
            leads: List of leads from ProspectSearchAgent
                Example:
                [
                    {
                        "company": "ExampleCorp",
                        "contact_name": "Jane Doe",
                        "email": "jane@examplecorp.com",
                        "linkedin": "https://linkedin.com/in/janedoe"
                    }
                ]

        Returns:
            dict: { "enriched_leads": [ ... ] }
        """

        if not leads:
            leads = [
                {
                    "company": "ExampleCorp",
                    "contact_name": "Jane Doe",
                    "email": "jane@examplecorp.com",
                    "linkedin": "https://linkedin.com/in/janedoe"
                },
                {
                    "company": "TestCo",
                    "contact_name": "Alice Smith",
                    "email": "alice@testco.com",
                    "linkedin": "https://linkedin.com/in/alicesmith"
                }
            ]

        # Technology stack mapping (example placeholders)
        tech_stacks = {
            "ExampleCorp": ["Salesforce", "HubSpot", "Outreach", "LinkedIn Sales Navigator"],
            "TestCo": ["Pipedrive", "Microsoft Dynamics", "Slack", "Zapier"],
            "default": ["Salesforce", "HubSpot"]
        }

        enriched_leads = []

        for lead in leads:
            company = lead.get("company", "Unknown")
            name = lead.get("contact_name", "John Doe")
            email = lead.get("email", "")
            linkedin = lead.get("linkedin", "")

            # Try to fetch real role from Hunter.io
            role = None
            if self.hunter_api_key and email:
                role = self.fetch_role_from_hunter(email)

            # Fallback heuristic if Hunter.io doesn’t return
            if not role:
                lower_email = email.lower()
                if "vp" in lower_email or "vp" in name.lower():
                    role = "VP of Sales"
                elif "director" in lower_email or "director" in name.lower():
                    role = "Director of Sales"
                elif "manager" in lower_email or "manager" in name.lower():
                    role = "Sales Manager"
                else:
                    role = "Sales Executive"

            # Determine seniority
            if any(x in role.lower() for x in ["vp", "chief", "head"]):
                seniority = "executive"
            elif "director" in role.lower():
                seniority = "senior"
            else:
                seniority = "mid"

            technologies = tech_stacks.get(company, tech_stacks["default"])

            enriched_leads.append({
                "company": company,
                "contact_name": name,
                "email": email,
                "linkedin": linkedin,
                "role": role,
                "technologies": technologies,
                "seniority_level": seniority,
                "engagement_score": 0.75  # initial base score; updated later
            })

        return {"enriched_leads": enriched_leads}
