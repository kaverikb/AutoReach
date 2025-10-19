# agents/prospect_search_agent.py

import os
import requests

class ProspectSearchAgent:
    """
    Agent to fetch company + prospect data matching ICP using Apollo API.
    Tools: Apollo API (contacts/search endpoint)
    Output: {"leads": [ ... ]}
    """

    def __init__(self, **kwargs):
        """
        Initialize ProspectSearchAgent.
        Extracts apollo_api_key from kwargs.
        """
        self.apollo_api_key = kwargs.get("api_key") or os.getenv("APOLLO_API_KEY")
        self.search_endpoint = "https://api.apollo.io/v1/contacts/search"

    def _search_apollo(self, icp: dict, signals: list) -> list:
        """
        Search Apollo for contacts matching ICP criteria.
        
        Args:
            icp: Ideal customer profile filters
            signals: Buying signals to filter by
            
        Returns:
            List of formatted leads from Apollo
        """
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.apollo_api_key
        }

        # Build search payload for Apollo
        payload = {
            "q_organization_industry": icp.get("industry", "SaaS"),
            "organization_locations": [icp.get("location", "United States")],
            "person_titles": ["Sales Manager", "Sales Executive", "VP of Sales", "Director of Sales", "Head of Growth"],
            "per_page": 10,
            "page": 1
        }

        # Add employee count range if provided
        emp_min = icp.get("employee_count", {}).get("min", 100)
        emp_max = icp.get("employee_count", {}).get("max", 1000)
        if emp_min and emp_max:
            payload["q_organization_employee_count_range"] = f"{emp_min}-{emp_max}"

        try:
            response = requests.post(self.search_endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            leads = []
            contacts = data.get("contacts", [])
            
            for contact in contacts:
                lead = {
                    "company": contact.get("organization", {}).get("name", "Unknown"),
                    "contact_name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                    "email": contact.get("email", ""),
                    "linkedin": contact.get("linkedin_url", ""),
                    "signal": "apollo_search",
                    "industry": contact.get("organization", {}).get("industry", ""),
                    "location": contact.get("organization", {}).get("locations", [{}])[0].get("city", "") if contact.get("organization", {}).get("locations") else "",
                    "employee_count": contact.get("organization", {}).get("employee_count"),
                    "revenue": contact.get("organization", {}).get("annual_revenue"),
                    "apollo_id": contact.get("id")
                }
                leads.append(lead)
            
            return leads
            
        except requests.exceptions.RequestException as e:
            print(f"[Apollo Search Error]: {e}")
            return []

    def run(self, icp: dict = None, signals: list = None) -> dict:
        """
        Search for prospects matching ICP using Apollo API.
        
        Args:
            icp: Ideal customer profile filters
            signals: Buying signals to match
            
        Returns:
            dict: {"leads": [ {...}, {...} ]}
        """
        
        # Default ICP
        if icp is None:
            icp = {
                "industry": "SaaS",
                "location": "United States",
                "employee_count": {"min": 100, "max": 1000},
                "revenue": {"min": 20000000, "max": 200000000}
            }

        if signals is None:
            signals = ["recent_funding", "hiring_for_sales"]

        # Try Apollo API if key exists
        if self.apollo_api_key:
            print(f"[ProspectSearch] Searching Apollo API with ICP: {icp}")
            leads = self._search_apollo(icp, signals)
            
            if leads:
                print(f"[ProspectSearch] Found {len(leads)} leads from Apollo")
                return {"leads": leads}
            else:
                print("[ProspectSearch] No leads found from Apollo, using fallback data")
        else:
            print("[ProspectSearch] No Apollo API key provided, using fallback data")

        # Fallback dummy data
        fallback_leads = [
            {
                "company": "ExampleCorp",
                "contact_name": "Jane Doe",
                "email": "jane.doe@examplecorp.com",
                "linkedin": "https://linkedin.com/in/janedoe",
                "signal": "recent_funding",
                "industry": "SaaS",
                "location": "San Francisco, CA",
                "employee_count": 250,
                "revenue": 50000000,
                "apollo_id": "contact_001"
            },
            {
                "company": "TestCo",
                "contact_name": "Alice Smith",
                "email": "alice@testco.com",
                "linkedin": "https://linkedin.com/in/alicesmith",
                "signal": "hiring_for_sales",
                "industry": "SaaS",
                "location": "Austin, TX",
                "employee_count": 150,
                "revenue": 35000000,
                "apollo_id": "contact_002"
            }
        ]

        return {"leads": fallback_leads}