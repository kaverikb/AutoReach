# AutoReach

AutoReach is an autonomous B2B lead generation system that automates the entire prospect-to-lead workflow. It discovers high-potential prospects matching specific ICPs (Ideal Customer Profiles), enriches and scores them, generates personalized outreach emails, sends them through integrated APIs, and tracks engagement— all managed through a single JSON-based workflow configuration.

---

## Project Overview

AutoReach streamlines the B2B outreach process by combining multiple APIs and intelligent agents into one unified workflow. Each stage is modular and agent-driven, enabling full automation, scalability, and traceability.

---

## Core Technologies

* LangGraph + LangChain: Agent orchestration framework
* Streamlit: Interactive dashboard for workflow execution and monitoring
* Chroma: Vector database for lead and workflow state persistence
* gspread + oauth2client: Google Sheets API integration
* requests: For API interactions and external calls

---

## Integrated APIs and Services

| Purpose            | API / Service             | Endpoint Example           |
| ------------------ | ------------------------- | -------------------------- |
| Prospect Discovery | Apollo API                | `/v1/contacts/search`      |
| Lead Enrichment    | Hunter.io                 | `/v2/domain-search`        |
| Email Generation   | DeepSeek (via OpenRouter) | `/api/v1/chat/completions` |
| Email Delivery     | Brevo API                 | `/v3/smtp/email`           |
| Feedback & Metrics | Google Sheets API         | Logged via `gspread`       |

---

## Agent Architecture

1. **ProspectSearchAgent**
   Searches and retrieves B2B leads from Apollo API based on ICP filters (industry, location, title, company size).

2. **DataEnrichmentAgent**
   Enhances lead profiles using Hunter.io API, adding missing attributes such as role, domain, or technology stack.

3. **ScoringAgent**
   Evaluates each prospect’s ICP fit and assigns a lead score based on defined heuristics and rules.

4. **OutreachContentAgent**
   Generates contextually personalized outreach emails using DeepSeek via OpenRouter API.

5. **OutreachExecutorAgent**
   Sends generated emails via Brevo API and manages sending schedules.

6. **ResponseTrackerAgent**
   Tracks opens, clicks, and replies from Apollo or Brevo logs to measure engagement performance.

7. **FeedbackTrainerAgent**
   Logs campaign results and performance metrics into Google Sheets and recommends message optimizations.

---

## Folder Structure

```
AutoReach/
│
├── src/
│   ├── agents/
│   │   ├── prospect_search_agent.py
│   │   ├── data_enrichment_agent.py
│   │   ├── scoring_agent.py
│   │   ├── outreach_content_agent.py
│   │   ├── outreach_executor_agent.py
│   │   ├── response_tracker_agent.py
│   │   └── feedback_trainer_agent.py
│   ├── langgraph_builder.py
│   ├── workflow.json
│   └── utils/
│       ├── apollo_utils.py
│       ├── hunter_utils.py
│       ├── brevo_utils.py
│       └── sheet_utils.py
│
├── ui/
│   └── dashboard.py
│
├── logs/
│   └── workflow_logs.txt
│
├── .env
├── .env.example
├── requirements.txt
├── config.yaml
└── README.md
```

---

## Setup Instructions

1. Clone the repository

   ```
   git clone https://github.com/yourusername/AutoReach.git
   cd AutoReach
   ```

2. Create and activate virtual environment

   ```
   python -m venv venv
   venv\Scripts\activate   # For Windows
   source venv/bin/activate   # For macOS/Linux
   ```

3. Install dependencies

   ```
   pip install -r requirements.txt
   ```

4. Add API keys to `.env`

   ```
   OPENROUTER_API_KEY=
   APOLLO_API_KEY=
   HUNTER_API_KEY=
   BREVO_API_KEY=
   GOOGLE_SHEETS_CREDENTIALS=
   ```

5. Run the Streamlit dashboard

   ```
   streamlit run ui/dashboard.py
   ```

---

## Workflow Configuration

All agent execution order and parameters are defined in `workflow.json`.
Each step defines the input, output, dependencies, and agent name, enabling LangGraph to orchestrate the complete autonomous flow.

Example snippet:

```json
{
  "workflow": [
    {"name": "prospect_search", "agent": "ProspectSearchAgent"},
    {"name": "data_enrichment", "agent": "DataEnrichmentAgent"},
    {"name": "scoring", "agent": "ScoringAgent"},
    {"name": "outreach_content", "agent": "OutreachContentAgent"},
    {"name": "outreach_executor", "agent": "OutreachExecutorAgent"},
    {"name": "response_tracker", "agent": "ResponseTrackerAgent"},
    {"name": "feedback_trainer", "agent": "FeedbackTrainerAgent"}
  ]
}
```

---

## Logging and Monitoring

All runtime activities, agent logs, and workflow traces are stored under the `logs/` directory.
Google Sheets integration allows you to visualize campaign results, performance metrics, and suggestions for optimization.

---

## License

This project is for educational and portfolio purposes.
All external API usage must comply with respective provider terms.
