from src.state import AgentState
import random

def route_after_tester(state: AgentState) -> str:
    """Route logic after tester node"""
    validation_status = state.get('validation_report', {}).get('status', 'Failed')
    return "passed" if validation_status == "Passed" else "failed"

    