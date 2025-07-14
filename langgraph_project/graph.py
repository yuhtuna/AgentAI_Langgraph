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
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # If the last message was a tool call, execute the tool.
        print("---DECISION: EXECUTING TOOL---")
        return "tool"
    else:
        # Otherwise, the LLM has responded with a final answer.
        print("---DECISION: PROCEEDING TO WRITER---")
        return "writer"


def route_after_tool(state: AgentState) -> str:
    """
    Decision node after tool execution.
    Check if we need more information or can proceed to writing.
    """
    # Count how many tool executions we've done by counting ToolMessage instances
    messages = state.get('messages', [])
    
    # Debug: Print messages at this routing point
    print(f"🔄 ROUTE_AFTER_TOOL - MESSAGES: {len(messages)}")
    for i, msg in enumerate(messages):
        msg_type = type(msg).__name__
        msg_name = getattr(msg, 'name', 'no_name')
        print(f"  Route Message {i}: {msg_type} (name: {msg_name})")
    
    # Count tool executions by type
    knowledge_base_used = any(hasattr(msg, 'name') and msg.name == 'knowledge_base_search' for msg in messages)
    web_search_used = any(hasattr(msg, 'name') and msg.name == 'tavily_search' for msg in messages)
    
    tool_execution_count = sum(1 for msg in messages if hasattr(msg, 'name') and 
                              msg.name in ['tavily_search', 'knowledge_base_search'])
    
    print(f"🔄 ROUTE TOOL COUNT: {tool_execution_count}")
    print(f"📚 ROUTE KB used: {knowledge_base_used}")  
    print(f"🌐 ROUTE Web used: {web_search_used}")
    
    if knowledge_base_used and web_search_used:
        print("---DECISION: ENOUGH RESEARCH DONE, PROCEEDING TO WRITER---")
        return "writer"
    else:
        print("---DECISION: CONTINUING RESEARCH---")
        return "researcher"


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
    
    # Add conditional routing after tool execution to prevent infinite loops
    workflow.add_conditional_edges(
        "tool_executor",
        route_after_tool,
        {
            "researcher": "researcher",
            "writer": "writer",
        },
    )
    workflow.add_edge("writer", END)

    # Compile the graph into a runnable application
    return workflow.compile()
