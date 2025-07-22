from src.state import AgentState

def tester(state: AgentState) -> AgentState:
    """
    A simple tester node that returns the state without modification.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The unmodified state.
    """
    return state