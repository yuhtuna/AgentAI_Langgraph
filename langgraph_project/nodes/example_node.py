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
    
    # Check if we've already used tools (to prevent infinite loops)
    messages = state.get('messages', [])
    
    # Debug: Print all messages for debugging
    print(f"📋 TOTAL MESSAGES: {len(messages)}")
    for i, msg in enumerate(messages):
        msg_type = type(msg).__name__
        msg_name = getattr(msg, 'name', 'no_name')
        print(f"  Message {i}: {msg_type} (name: {msg_name})")
    
    # Count tool executions by type
    knowledge_base_used = any(hasattr(msg, 'name') and msg.name == 'knowledge_base_search' for msg in messages)
    web_search_used = any(hasattr(msg, 'name') and msg.name == 'tavily_search' for msg in messages)
    
    tool_execution_count = sum(1 for msg in messages if hasattr(msg, 'name') and 
                              msg.name in ['tavily_search', 'knowledge_base_search'])
    
    print(f"🔄 TOOL EXECUTION COUNT: {tool_execution_count}")
    print(f"📚 Knowledge base used: {knowledge_base_used}")
    print(f"🌐 Web search used: {web_search_used}")
    
    # Stop if we've used both tools
    if knowledge_base_used and web_search_used:
        print("🛑 STOPPING: Both tools used, proceeding to write")
        response_content = "I have gathered comprehensive information from both local knowledge base and web search. Now I will compile a detailed report."
        from langchain_core.messages import AIMessage
        response = AIMessage(content=response_content)
        return {"messages": [response]}
    
    # Enhanced prompt that guides sequential tool usage
    if not knowledge_base_used:
        # First, use knowledge base
        system_prompt = """You are a research assistant. You MUST use the knowledge_base_search tool first to gather local AI information.

        Available tools:
        1. knowledge_base_search - for local AI documents (USE THIS FIRST)
        2. tavily_search - for current web information

        Since this is an AI-related task, start by searching the knowledge base for foundational information.
        Make a tool call to knowledge_base_search with a relevant query."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Plan: {state['plan']}\n\nPlease search the knowledge base for information about AI advancements.")
        ]
    elif not web_search_used:
        # Second, use web search for current information
        system_prompt = """You are a research assistant. You have already searched the knowledge base. Now use tavily_search to get current web information to complement your research.

        Available tools:
        1. knowledge_base_search - already used ✓
        2. tavily_search - for current web information (USE THIS NOW)

        Make a tool call to tavily_search to find the latest information and current developments."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Plan: {state['plan']}\n\nPlease search the web for the latest AI advancements and current developments in 2025.")
        ]
    else:
        # Both tools used, should not reach here due to earlier check
        system_prompt = "Both research tools have been used."
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Research complete.")
        ]
    
    # Debug: Print messages being sent to LLM
    print("📤 SENDING TO LLM:")
    for i, msg in enumerate(messages):
        print(f"  Message {i}: {type(msg).__name__} - {msg.content[:100]}...")
    
    # Bind the tools to the LLM
    llm_with_tools = llm.bind_tools([search_tool, rag_tool])
    
    try:
        response = llm_with_tools.invoke(messages)
        
        # Debug: Print the full response to see what's happening
        print(f"🔍 FULL RESPONSE: {response}")
        print(f"🔍 RESPONSE TYPE: {type(response)}")
        print(f"🔍 HAS TOOL_CALLS: {hasattr(response, 'tool_calls')}")
        if hasattr(response, 'tool_calls'):
            print(f"🔍 TOOL_CALLS: {response.tool_calls}")
        
        # Print which tool was selected
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_name = response.tool_calls[0]['name']
            tool_args = response.tool_calls[0]['args']
            print(f"🔧 TOOL SELECTED: {tool_name}")
            print(f"📝 QUERY: {tool_args}")
        else:
            print("⚠️ NO TOOL SELECTED - Agent provided direct response")
        
        return {"messages": [response]}
    except Exception as e:
        print(f"❌ ERROR IN LLM INVOCATION: {e}")
        # Return a simple response without tool calls to prevent crashes
        from langchain_core.messages import AIMessage
        simple_response = AIMessage(content="Error occurred during tool selection")
        return {"messages": [simple_response]}


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
        print(f"🚀 EXECUTING: {tool_name}")
        print(f"📋 WITH ARGS: {tool_args}")
        
        if tool_name == search_tool.name:
            print("🌐 Using Tavily web search...")
            response = search_tool.invoke(tool_args)
        elif tool_name == rag_tool.name:
            print("📚 Using local knowledge base search...")
            response = rag_tool.invoke(tool_args)
        else:
            print(f"❌ ERROR: Unknown tool {tool_name}")
            response = f"Error: Unknown tool {tool_name}"
        
        print(f"✅ TOOL RESPONSE RECEIVED (length: {len(str(response))} characters)")
        print(f"📄 FIRST 200 CHARS: {str(response)[:200]}...")
        
        # Append the response as a ToolMessage with the correct name
        tool_responses.append(ToolMessage(
            content=str(response), 
            tool_call_id=call['id'],
            name=tool_name
        ))
    
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
