from src.state import AgentState

def retriever_node(state: AgentState) -> AgentState:
    """
    A node that retrieves information from a data source.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The updated state after retrieval.
    """
    return state