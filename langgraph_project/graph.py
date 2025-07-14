from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.example_node import planner_node, researcher_node, writer_node, tool_node
from langchain_core.messages import BaseMessage


def route_after_researcher(state: AgentState) -> str:
    """
    Decision node to determine the next step after the researcher has run.
    If the researcher decided to call a tool, we execute it.
    Otherwise, we have a final answer and can proceed to the writer.
    """
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        # If the last message was a tool call, execute the tool.
        print("---DECISION: EXECUTING TOOL---")
        return "tool"
    else:
        # Otherwise, the LLM has responded with a final answer.
        print("---DECISION: PROCEEDING TO WRITER---")
        return "writer"


def create_workflow():
    """
    Build and compile the LangGraph workflow.
    This defines the connections between our nodes, creating the workflow.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("tool_executor", tool_node)
    workflow.add_node("writer", writer_node)

    # Set the entry point of the graph
    workflow.set_entry_point("planner")

    # Add edges to define the flow
    workflow.add_edge("planner", "researcher")

    # This is the new conditional edge after the researcher
    workflow.add_conditional_edges(
        "researcher",
        route_after_researcher,
        {
            "tool": "tool_executor",
            "writer": "writer",
        },
    )
    
    # The tool executor always loops back to the researcher to process the results
    workflow.add_edge("tool_executor", "researcher")
    workflow.add_edge("writer", END)

    # Compile the graph into a runnable application
    return workflow.compile()
