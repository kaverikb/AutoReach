# src/main.py
import os
from langgraph_builder import LangGraphBuilder

def run_workflow():
    # Initialize LangGraph workflow and agents
    builder = LangGraphBuilder()
    agents = builder.get_agents()
    workflow = builder.get_workflow()

    # Dictionary to store outputs of each step
    step_outputs = {}

    # Execute each step sequentially
    for step in workflow.get("steps", []):
        step_id = step["id"]
        agent = agents.get(step_id)
        print(f"\nRunning step: {step_id} ({step['agent']})")

        # Prepare inputs by resolving references to previous step outputs
        inputs = {}
        for key, val in step.get("inputs", {}).items():
            if isinstance(val, str) and val.startswith("{{") and val.endswith("}}"):
                # Example: "{{prospect_search.output.leads}}"
                ref = val[2:-2].strip().split(".")
                ref_step = ref[0]
                ref_key = ref[-1]
                inputs[key] = step_outputs.get(ref_step, {}).get(ref_key)
            else:
                inputs[key] = val

        # Run the agent
        try:
            output = agent.run(**inputs)
            # Store output using step_id as key
            step_outputs[step_id] = {"output": output}
            print(f"Step '{step_id}' completed. Output keys: {list(output[0].keys()) if isinstance(output, list) and output else output.keys() if isinstance(output, dict) else 'unknown'}")
        except Exception as e:
            print(f"Error running step {step_id}: {e}")

    print("\nWorkflow execution completed.")
    return step_outputs


if __name__ == "__main__":
    results = run_workflow()
    print("\nFinal outputs by step:")
    for step, data in results.items():
        print(f"{step}: {data['output']}")
