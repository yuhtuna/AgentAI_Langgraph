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
    
    # Initialize the iteration counter
    return {"plan": response.content, "iteration_count": 0}


def researcher_node(state: AgentState):
    """
    The "brain" of the research process. This node evaluates the current state
    and decides the next best action. It can choose to:
    - Call a tool (for the first time or to refine results).
    - Conclude the research process if enough information has been gathered.
    """
    print("---ROUTING: DECIDING NEXT STEP---")

    # Construct the prompt for the researcher LLM
    system_prompt = """You are a master researcher. Your goal is to gather comprehensive information to fulfill the user's plan.

You have two tools available:
1. `knowledge_base_search`: For internal documentation and established knowledge.
2. `tavily_search`: For real-time web searches and current events.

Your research strategy is as follows:
1. Start with `knowledge_base_search` to see what internal information exists.
2. Then, use `tavily_search` to get up-to-date information from the web.
3. **Crucially, you must evaluate the results of each tool call.** If the results are not satisfactory (e.g., not relevant, not enough detail), you can call the **same tool again** with a refined query to get better results.
4. After you are satisfied with the results from both tools, you can conclude the research.

Based on the conversation history and the original plan, decide on the next best action. This could be:
- Calling a tool (either for the first time or again).
- Responding with a final summary if you have sufficient information. This will pass the result to the writer.
"""

    # Prepend the plan to the message history to give the LLM context.
    plan = state.get('plan', "No plan provided.")
    plan_message = HumanMessage(content=f"Here is the research plan I need you to execute:\n\n{plan}")
    
    messages = [SystemMessage(content=system_prompt), plan_message]
    messages.extend(state.get('messages', []))

    # Debug: Print messages being sent to LLM
    print("📤 SENDING TO LLM:")
    for i, msg in enumerate(messages):
        # Truncate content for cleaner logging
        content_preview = msg.content.replace('\n', ' ').strip()
        if len(content_preview) > 150:
            content_preview = content_preview[:150] + "..."
        print(f"  Message {i}: {type(msg).__name__} - {content_preview}")

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
    This node executes the tool called by the researcher and increments
    the iteration counter.
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
    
    # Increment the iteration counter
    new_count = state.get('iteration_count', 0) + 1
    
    # Return the responses and the updated count
    return {"messages": tool_responses, "iteration_count": new_count}


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
