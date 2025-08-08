from src.state import AgentState

def resource_monitor_node(state: AgentState) -> AgentState:
    state["cost_estimate"] = len(state["task_plan"]) * 0.1
    state["current_cost"] = 0
    return state