from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from ..llm_config import llm
from ..state import AgentState
from ..tools import search_tool, rag_tool
import json
import pprint


def planner_node(state: AgentState):
    """
    This node acts as the "Manager". It takes the initial user task
    and creates a plan for the other agents to follow.
    """
    print("---PLANNING---")
    messages = [
        SystemMessage(content="You are an expert project planner. Create a simple, step-by-step plan to accomplish the user's task. Your plan should be clear and concise."),
        HumanMessage(content=state['task'])
    ]
    response = llm.invoke(messages)
    return {"plan": response.content}


def researcher_node(state: AgentState):
    """
    This node acts as a "Router". It decides which tool to use (web search or RAG)
    and generates the appropriate query.
    """
    print("---ROUTING: DECIDING WHICH TOOL TO USE---")
    
    # This prompt helps the LLM decide which tool is more appropriate
    system_prompt = """You are a research assistant. Your goal is to answer the user's request.
    You have two tools at your disposal:
    1. `tavily_search`: A general web search tool for current events and broad topics.
    2. `knowledge_base_search`: A tool to search local documents about AI advancements and ethics.

    Based on the user's plan, decide which tool is more appropriate.
    Your response should be a tool call to either `tavily_search` or `knowledge_base_search`.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state['plan'])
    ]
    
    # Bind the tools to the LLM
    llm_with_tools = llm.bind_tools([search_tool, rag_tool])
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}


def tool_node(state: AgentState):
    """
    This node executes the tool called by the researcher.
    It appends the results to the messages list.
    """
    print("---EXECUTING TOOL---")
    tool_calls = state['messages'][-1].tool_calls
    tool_responses = []
    for call in tool_calls:
        tool_name = call['name']
        tool_args = call['args']
        print(f"Calling tool: {tool_name} with args: {tool_args}")
        if tool_name == search_tool.name:
            response = search_tool.invoke(tool_args)
        elif tool_name == rag_tool.name:
            response = rag_tool.invoke(tool_args)
        else:
            response = f"Error: Unknown tool {tool_name}"
        
        # Append the response as a ToolMessage
        tool_responses.append(ToolMessage(content=str(response), tool_call_id=call['id']))
    
    # Return the responses to be added to the state's messages list
    return {"messages": tool_responses}


def writer_node(state: AgentState):
    """
    This node takes the full conversation history and generates the final report.
    """
    print("---WRITING FINAL REPORT---")
    
    # Extract text content from the conversation history
    context_parts = []
    
    # Add the original task and plan
    if 'task' in state:
        context_parts.append(f"Task: {state['task']}")
    if 'plan' in state:
        context_parts.append(f"Plan: {state['plan']}")
    
    # Extract content from messages (tool responses)
    for message in state['messages']:
        if hasattr(message, 'content') and message.content:
            # For tool messages, the content is the search results
            if message.__class__.__name__ == 'ToolMessage':
                context_parts.append(f"Search Results: {message.content}")
            elif message.__class__.__name__ == 'HumanMessage':
                context_parts.append(f"User Input: {message.content}")
    
    # Combine all context
    full_context = "\n\n".join(context_parts)
    
    # Create the writer messages with proper text content
    system_prompt = "You are an expert technical writer. Based on the provided context, write a comprehensive and polished final report. Synthesize all the information provided."
    
    writer_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=full_context)
    ]
    
    response = llm.invoke(writer_messages)
    return {"review": response.content}
