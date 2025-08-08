from src.state import AgentState
import random

def route_after_manager(state: AgentState) -> str:
    """Route logic after manager node"""
    if state.get('user_interrupt'):
        return "replan"
    elif state["is_clarification_needed"]:
        return "clarify"
    else:
        return "plan"