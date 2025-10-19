import os
import requests

class OutreachContentAgent:
    """
    Agent to generate personalized outreach messages using OpenRouter DeepSeek API.
    Input: ranked_leads from ScoringAgent
    Output: messages (lead + email_body)
    """

    def __init__(self, api_key):
        """
        Initialize OutreachContentAgent.
        Accepts api_key if provided.
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.endpoint ="https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat-v3.1:free"

    def _generate_email(self, prompt: str) -> str:
        """
        Call OpenRouter DeepSeek API to generate email body.
        
        Args:
            prompt: Email generation prompt
            
        Returns:
            Generated email body or error message
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://autoreach.local",
            "X-Title": "AutoReach"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an SDR writing concise, personalized outreach emails. Keep emails under 150 words. Be friendly, professional, and specific."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=20)
            print(f"[DEBUG] Status code: {response.status_code}")
            print(f"[DEBUG] Response text: {response.text}")
            print(f"[DEBUG] Response headers: {response.headers}")
            
            response.raise_for_status()
            data = response.json()
            email_body = data["choices"][0]["message"]["content"].strip()
            return email_body
        except requests.exceptions.Timeout:
            return "[Error generating email: Request timeout]"
        except requests.exceptions.RequestException as e:
            return f"[Error generating email: {str(e)}]"
        except (KeyError, ValueError) as e:
            return f"[Error parsing response: {str(e)}]"

    def run(self, ranked_leads: list = None, persona: str = "SDR", tone: str = "friendly") -> dict:
        """
        Generate personalized outreach messages for leads using DeepSeek.
        
        Args:
            ranked_leads: List of leads with scores from ScoringAgent
            persona: Role persona for signature (e.g., "SDR", "Sales Manager")
            tone: Email tone (e.g., "friendly", "formal", "casual")

        Returns:
            dict with "messages" key containing list of personalized email dicts
        """
        
        if ranked_leads is None or len(ranked_leads) == 0:
            ranked_leads = [
                {
                    "company": "ExampleCorp",
                    "contact": "Jane Doe",
                    "role": "Sales Manager",
                    "technologies": ["Salesforce"],
                    "score": 0.85
                },
                {
                    "company": "TestCo",
                    "contact": "Alice Smith",
                    "role": "Sales Executive",
                    "technologies": ["Pipedrive"],
                    "score": 0.72
                }
            ]

        messages = []

        for lead in ranked_leads:
            contact_name = lead.get("contact", lead.get("contact_name", "there"))
            company_name = lead.get("company", "your company")
            role = lead.get("role", "decision maker")
            technologies = ", ".join(lead.get("technologies", []))

            # Build personalized prompt
            prompt = (
                f"Write a short {tone} outreach email to {contact_name} at {company_name}. "
                f"They are a {role} and their company uses: {technologies}. "
                f"Mention one specific way we can help their team. "
                f"Sign off professionally as {persona}. "
                f"Keep it under 120 words. No subject line needed."
            )

            email_body = self._generate_email(prompt)

            message = {
                "lead": contact_name,
                "company": company_name,
                "email": f"{contact_name.lower().replace(' ', '.')}@{company_name.lower().replace(' ', '')}.com",
                "subject": f"Quick idea for {company_name}",
                "email_body": email_body,
                "score": lead.get("score", 0)
            }

            messages.append(message)

        return {"messages": messages}