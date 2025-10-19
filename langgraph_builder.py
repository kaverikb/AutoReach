# langgraph_builder.py
import json
import os
import re
from importlib import import_module


class LangGraphBuilder:
    """
    Reads workflow.json and initializes the LangGraph workflow.
    Dynamically imports agent classes from the 'agents' folder
    and passes tool configs (with environment variable support) to agent constructors.
    Raises clear errors if required keys are missing.
    """

    def __init__(self, workflow_file: str = "workflow.json"):
        self.workflow_file = workflow_file
        self.workflow_data = {}
        self.agents = {}

        self._load_workflow()
        self._init_agents()

    # ----------------------
    # Workflow loading
    # ----------------------
    def _load_workflow(self):
        """Load workflow.json into a dictionary"""
        if not os.path.exists(self.workflow_file):
            raise FileNotFoundError(f"{self.workflow_file} not found")
        with open(self.workflow_file, "r") as f:
            self.workflow_data = json.load(f)
        print(f"Loaded workflow: {self.workflow_data.get('workflow_name', 'Unnamed')}")

    # ----------------------
    # Agent initialization
    # ----------------------
    def _init_agents(self):
        """Dynamically import and initialize agent classes"""
        for step in self.workflow_data.get("steps", []):
            agent_name = step.get("agent")
            step_id = step.get("id")
            if not agent_name or not step_id:
                raise ValueError(f"Step missing 'agent' or 'id': {step}")

            try:
                # Convert CamelCase class name to snake_case filename
                module_name = self._camel_to_snake(agent_name)
                module = import_module(f"agents.{module_name}")
                AgentClass = getattr(module, agent_name)

                # Extract tool configs as kwargs for the agent constructor
                init_kwargs = self._extract_agent_config(step)

                # Check for missing API keys / required configs
                missing_keys = [k for k, v in init_kwargs.items() if v is None]
                if missing_keys:
                    raise ValueError(
                        f"Missing environment values for agent '{agent_name}' in step '{step_id}': {missing_keys}"
                    )

                self.agents[step_id] = AgentClass(**init_kwargs)
                print(f"Initialized agent: {agent_name} with config: {init_kwargs}")

            except Exception as e:
                print(f"Error initializing agent '{agent_name}' (step '{step_id}'): {e}")

    # ----------------------
    # Helpers
    # ----------------------
    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """
        Convert CamelCase to snake_case for Python filenames.
        Example: "ProspectSearchAgent" -> "prospect_search_agent"
        """
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _extract_agent_config(self, step: dict) -> dict:
        """
        Convert workflow tool configs to agent constructor kwargs.
        Replaces {{ENV_VAR}} with environment variable values.
        """
        init_kwargs = {}
        for tool in step.get("tools", []):
            config = tool.get("config", {})
            for key, value in config.items():
                if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                    env_key = value[2:-2].strip()
                    env_val = os.getenv(env_key)
                    init_kwargs[key.lower()] = env_val
                else:
                    init_kwargs[key.lower()] = value
        return init_kwargs

    # ----------------------
    # Getters
    # ----------------------
    def get_workflow(self) -> dict:
        """Return the loaded workflow JSON data"""
        return self.workflow_data

    def get_agents(self) -> dict:
        """Return the initialized agent instances"""
        return self.agents


# ----------------------
# CLI / debug test
# ----------------------
if __name__ == "__main__":
    builder = LangGraphBuilder()
    workflow = builder.get_workflow()
    agents = builder.get_agents()
    print(f"\nAgents ready for execution: {list(agents.keys())}")
