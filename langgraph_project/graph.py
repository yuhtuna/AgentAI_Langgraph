from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.example_node import planner_node, researcher_node, writer_node, search_node
from langchain_core.messages import SystemMessage


def should_continue(state: AgentState) -> str:
    """
    Decision node to determine whether to continue searching or end the process.
    """
    # If the search returned an error message (string) or is empty, end.
    if not state.get("search_results") or isinstance(state["search_results"], str):
        print("---NO RESULTS OR ERROR, ENDING---")
        return "end"
    # If there are search results, proceed to the writer.
    else:
        print("---SEARCH SUCCESSFUL, PROCEEDING TO WRITER---")
        return "continue"


def create_workflow():
    """
    Build and compile the LangGraph workflow.
    This defines the connections between our nodes, creating the workflow.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("search", search_node)
    workflow.add_node("writer", writer_node)

    # Set the entry point of the graph
    workflow.set_entry_point("planner")

    # Add edges to define the flow
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "search")

    # Add a conditional edge to decide whether to continue searching or proceed to the writer
    workflow.add_conditional_edges(
        "search",
        should_continue,
        {
            "continue": "writer",
            "end": END,
        },
    )

    workflow.add_edge("writer", END)

    # Compile the graph into a runnable application
    return workflow.compile()
