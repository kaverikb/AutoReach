class ScoringAgent:
    """
    Agent to score and rank leads based on ICP and engagement criteria.
    Input: enriched_leads from DataEnrichmentAgent
    Output: ranked leads with scores
    """

    def __init__(self, **kwargs):
        """
        Initialize ScoringAgent.
        Optionally accepts scoring_criteria dict for weighting factors.
        Example:
            {
                "employee_count": 0.25,
                "revenue": 0.35,
                "role_match": 0.25,
                "engagement_score": 0.15
            }
        """
        self.scoring_criteria = kwargs.get("scoring_criteria", {
            "employee_count": 0.25,
            "revenue": 0.35,
            "role_match": 0.25,
            "engagement_score": 0.15
        })

    def normalize(self, value, min_val, max_val):
        """
        Normalize a numeric value to a 0–1 scale between min_val and max_val.
        """
        if value is None:
            return 0
        return max(0, min(1, (value - min_val) / (max_val - min_val)))

    def run(self, enriched_leads: list = None, scoring_criteria: dict = None) -> dict:
        """
        Score and rank leads based on criteria like employee_count, revenue,
        role alignment, and engagement.

        Args:
            enriched_leads: list of enriched lead dicts from DataEnrichmentAgent
            scoring_criteria: optional dict to override weighting

        Returns:
            dict: { "ranked_leads": [ { ... lead info + score ... } ] }
        """
        criteria = scoring_criteria or self.scoring_criteria

        # Dummy fallback for testing
        if not enriched_leads:
            enriched_leads = [
                {
                    "company": "ExampleCorp",
                    "contact_name": "Jane Doe",
                    "role": "Sales Manager",
                    "technologies": ["Salesforce", "HubSpot"],
                    "employee_count": 250,
                    "revenue": 50000000,
                    "engagement_score": 0.75
                },
                {
                    "company": "TestCo",
                    "contact_name": "Alice Smith",
                    "role": "Sales Executive",
                    "technologies": ["Pipedrive"],
                    "employee_count": 150,
                    "revenue": 35000000,
                    "engagement_score": 0.6
                }
            ]

        ranked_leads = []

        for lead in enriched_leads:
            lead_score = 0.0

            # 1️⃣ Employee Count
            emp_score = self.normalize(lead.get("employee_count", 0), 50, 1000)
            lead_score += emp_score * criteria.get("employee_count", 0)

            # 2️⃣ Revenue
            rev_score = self.normalize(lead.get("revenue", 0), 20000000, 200000000)
            lead_score += rev_score * criteria.get("revenue", 0)

            # 3️⃣ Role Match
            role = lead.get("role", "").lower()
            target_roles = ["sales manager", "sales executive", "director of sales", "vp of sales"]
            role_score = 1.0 if any(r in role for r in target_roles) else 0.5
            lead_score += role_score * criteria.get("role_match", 0)

            # 4️⃣ Engagement
            engagement = lead.get("engagement_score", 0.5)
            lead_score += engagement * criteria.get("engagement_score", 0)

            # Final score + debugging trace
            lead["score_breakdown"] = {
                "employee_count": round(emp_score * criteria.get("employee_count", 0), 3),
                "revenue": round(rev_score * criteria.get("revenue", 0), 3),
                "role_match": round(role_score * criteria.get("role_match", 0), 3),
                "engagement": round(engagement * criteria.get("engagement_score", 0), 3)
            }
            lead["total_score"] = round(lead_score, 3)

            ranked_leads.append(lead)

        # Sort by descending total score
        ranked_leads.sort(key=lambda x: x["total_score"], reverse=True)

        return {"ranked_leads": ranked_leads}
