# ui/app.py
import sys
import os
import streamlit as st
import logging
from dotenv import load_dotenv

load_dotenv()

# ----------------------
# Fix import path for langgraph_builder
# ----------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langgraph_builder import LangGraphBuilder
from utils.chroma_store import ChromaStore

# ----------------------
# Logger setup
# ----------------------
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/run.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ----------------------
# Initialize Chroma Store
# ----------------------
chroma_store = ChromaStore()

# ----------------------
# Streamlit UI
# ----------------------
st.set_page_config(page_title="AutoReach Dashboard", layout="wide")
st.title("AutoReach — B2B Lead Generation Workflow")

st.markdown(
    """
This dashboard allows you to:
- Run the AutoReach workflow
- Track step-by-step outputs
- View recommendations for outreach optimization
- Store and retrieve lead data persistently
"""
)

# ----------------------
# Workflow Runner
# ----------------------
@st.cache_data(show_spinner=True)
def run_workflow():
    builder = LangGraphBuilder()
    agents = builder.get_agents()
    workflow = builder.get_workflow()
    step_outputs = {}

    for step in workflow.get("steps", []):
        step_id = step["id"]
        agent = agents.get(step_id)

        if agent is None:
            st.warning(f"Agent for step '{step_id}' not initialized. Skipping...")
            continue

        st.info(f"Running step: {step_id} ({step['agent']})")

        # Prepare inputs
        inputs = {}
        for key, val in step.get("inputs", {}).items():
            if isinstance(val, str) and val.startswith("{{") and val.endswith("}}"):
                # Reference another step's output
                ref = val[2:-2].strip().split(".")
                ref_step = ref[0]
                ref_key = ref[-1]
                ref_output = step_outputs.get(ref_step, {}).get("output")
                # If ref_output is list, pass it directly
                if isinstance(ref_output, list):
                    inputs[key] = ref_output
                elif isinstance(ref_output, dict):
                    inputs[key] = ref_output.get(ref_key)
                else:
                    inputs[key] = ref_output
            else:
                inputs[key] = val

        # Run agent
        try:
            output = agent.run(**inputs)
            step_outputs[step_id] = {"output": output}
            st.success(f"Step '{step_id}' completed.")
            logger.info(f"Step '{step_id}' output: {output}")
            
            # Store data in Chroma based on step
            if step_id == "prospect_search" and isinstance(output, dict):
                leads = output.get("leads", [])
                if leads:
                    chroma_store.store_leads(leads)
            
            elif step_id == "enrichment" and isinstance(output, dict):
                enriched_leads = output.get("enriched_leads", [])
                if enriched_leads:
                    chroma_store.store_enriched_leads(enriched_leads)
        
        except Exception as e:
            st.error(f"Error in step '{step_id}': {e}")
            logger.error(f"Error in step '{step_id}': {e}")

    return step_outputs


# ----------------------
# Sidebar for Chroma operations
# ----------------------
st.sidebar.header("📊 Data Management")

if st.sidebar.button("View Stored Leads"):
    stored_leads = chroma_store.get_all_leads("enriched")
    if stored_leads:
        st.sidebar.success(f"Found {len(stored_leads)} stored leads")
        st.sidebar.json(stored_leads[:5])  # Show first 5
    else:
        st.sidebar.info("No stored leads yet")

if st.sidebar.button("Clear Stored Data"):
    chroma_store.clear_collection("leads")
    chroma_store.clear_collection("enriched")
    st.sidebar.success("Cleared all stored data")

search_query = st.sidebar.text_input("Search stored leads:")
if search_query:
    similar_leads = chroma_store.get_similar_leads(search_query, "enriched", n_results=5)
    st.sidebar.json(similar_leads)

# ----------------------
# Run workflow button
# ----------------------
st.header("🚀 Workflow Execution")

if st.button("Run AutoReach Workflow"):
    st.info("Workflow execution started...")
    results = run_workflow()

    st.header("Workflow Outputs")
    for step, data in results.items():
        st.subheader(step)
        st.write(data["output"])

    st.success("Workflow execution completed.")
    st.info("✅ Data automatically stored in Chroma for future reference")