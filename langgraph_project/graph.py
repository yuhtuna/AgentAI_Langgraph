from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.example_node import planner_node, researcher_node, writer_node


def create_workflow():
    """
    Build and compile the LangGraph workflow.
    This defines the connections between our nodes, creating the workflow.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)

    # Set the entry point of the graph
    workflow.set_entry_point("planner")

    # Add edges to define the flow
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")

    # The final edge connects to the special "END" node, which stops the graph.
    workflow.add_edge("writer", END)

    # Compile the graph into a runnable application
    return workflow.compile()
