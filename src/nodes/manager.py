"""
Enhanced Manager Node with HITL Integration

This node serves as the entry point for user requests and implements intelligent
analysis to determine when human input is needed. It provides three key capabilities:

1. Clarification Detection: Automatically identifies vague requests that need more detail
2. Request Clarification: Expands user requests into detailed specifications
3. Plan Modification Analysis: Detects when new requests modify existing development plans

The node integrates with the HITL system by setting appropriate flags that trigger
pauses when human intervention is required.
"""

from state import AgentState
from config import llm
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import json

def manager_node(state: AgentState) -> AgentState: 
    """
    Enhanced manager node that analyzes user requests and manages task plan modifications.
    
    This function implements a three-stage analysis process:
    1. Check if clarification is needed for the user request
    2. Clarify and expand the request if no clarification is needed
    3. Analyze if the request modifies existing development plans
    
    The function sets HITL flags that can trigger pauses for human input when needed.
    
    Args:
        state: Current AgentState containing the user request and existing plan
        
    Returns:
        Updated AgentState with clarification results and modification analysis
    """
    print("Manager Node: Analyzing user request and current state...")
    
    user_request = state["user_request"]
    current_task_plan = state.get("task_plan", [])
    
    # STAGE 1: Check if clarification is needed
    clarification_needed = _check_clarification_needed(user_request)
    
    if clarification_needed:
        state["is_clarification_needed"] = True
        state["clarification_questions"] = clarification_needed
        print("Clarification needed. Questions generated:")
        for question in clarification_needed:
            print(f"  - {question}")
        return state
    
    # STAGE 2: No clarification needed - analyze and clarify the request
    state["is_clarification_needed"] = False
    clarified_request = _clarify_request(user_request)
    state["clarified_request"] = clarified_request
    print(f"Clarified request: {clarified_request}")
    
    # STAGE 3: Analyze if this request modifies existing development work
    if current_task_plan:
        print("Analyzing existing task plan for modifications...")
        modification_analysis = _analyze_plan_modifications(user_request, current_task_plan)
        
        if modification_analysis["has_modifications"]:
            print("Plan modifications detected!")
            print(f"   - Type: {modification_analysis['modification_type']}")
            print(f"   - Impact: {modification_analysis['impact_level']}")
            
            # Store analysis for HITL controller to evaluate
            state["manager_analysis"] = json.dumps(modification_analysis)
            
            # High-impact modifications trigger user approval pauses
            if modification_analysis["impact_level"] == "high":
                state["user_interrupt"] = f"High-impact modification: {modification_analysis['modification_type']}"
                print("High-impact modification - will pause for user approval")
        else:
            print("No significant plan modifications detected")
            state["manager_analysis"] = None
            state["user_interrupt"] = None
    else:
        print("First-time request - no existing plan to modify")
        state["manager_analysis"] = None
        state["user_interrupt"] = None
    
    return state

def _check_clarification_needed(user_request: str) -> list:
    """
    Determine if a user request needs clarification before proceeding.
    
    This function uses LLM analysis to identify vague or incomplete requests
    that would benefit from additional user input. It generates specific
    questions to help users provide the necessary details.
    
    Args:
        user_request: The original user request to analyze
        
    Returns:
        List of clarification questions, or empty list if no clarification needed
        
    Clarification Triggers:
        - Missing technical requirements (frameworks, databases)
        - Unclear functional requirements (features, user flows)
        - Vague non-functional requirements (performance, scalability)
        - Missing context (target audience, use case)
        - Unclear integration requirements
    """
    prompt = PromptTemplate(
        input_variables=["user_request"],
        template="""
        Based on the user request: {user_request}, determine if clarification is needed in 
        order to proceed with the task, particularly if it involves: 
        - Technical requirements (frameworks, databases, etc.)
        - Functional requirements (specific features, user flows)
        - Non-functional requirements (performance, scalability)
        - Target audience or use case
        - Integration requirements
        
        If clarification needed, generate specific questions.
        If clear enough, respond with "NO_CLARIFICATION_NEEDED".
        
        Format your response as a list of questions, one per line, or just "NO_CLARIFICATION_NEEDED".
        """
    )
    
    formatted_prompt = prompt.format(user_request=user_request)
    response = llm.invoke([HumanMessage(content=formatted_prompt)]).content
    
    if "NO_CLARIFICATION_NEEDED" in response:
        return []
    
    # Parse questions from response, filtering out formatting artifacts
    questions = [q.strip() for q in response.split('\n') 
                if q.strip() and not q.startswith('-') and not q.startswith('```')]
    return questions

def _clarify_request(user_request: str) -> str:
    """
    Expand a user request into a comprehensive, detailed specification.
    
    This function takes a clear user request and uses LLM analysis to create
    a detailed specification that includes technical requirements, functional
    specifications, success criteria, and assumptions.
    
    Args:
        user_request: The user request to clarify and expand
        
    Returns:
        Detailed specification document as a string
    """
    prompt = PromptTemplate(
        input_variables=["user_request"],
        template="""
        Take this user request and expand it into a clear, detailed specification:
        {user_request}
        
        Provide a comprehensive, clarified version that includes:
        - Technical requirements
        - Functional specifications
        - Success criteria
        - Any assumptions made
        
        Be specific and actionable.
        """
    )
    
    formatted_prompt = prompt.format(user_request=user_request)
    response = llm.invoke([HumanMessage(content=formatted_prompt)]).content
    return response.strip()

def _analyze_plan_modifications(new_request: str, current_plan: list) -> dict:
    """
    Analyze if a new request modifies an existing development plan.
    
    This function compares a new user request against an existing task plan
    to determine if modifications are needed. It assesses the type and impact
    of changes to help the HITL system decide when user approval is required.
    
    Args:
        new_request: The new user request to analyze
        current_plan: List of existing Task objects
        
    Returns:
        Dictionary containing modification analysis with fields:
        - has_modifications: Boolean indicating if changes are needed
        - modification_type: Type of change (addition, change, removal, scope_change)
        - impact_level: Impact assessment (low, medium, high)
        - affected_tasks: List of task IDs that would be affected
        - description: Human-readable description of the changes
    """
    # Convert current plan to a summary for LLM analysis
    plan_summary = _summarize_plan(current_plan)
    
    prompt = PromptTemplate(
        input_variables=["new_request", "current_plan_summary"],
        template="""
        Analyze if this new request modifies the existing development plan.
        
        NEW REQUEST: {new_request}
        
        CURRENT PLAN SUMMARY: {current_plan_summary}
        
        Determine:
        1. Does this request modify the existing plan? (yes/no)
        2. What type of modification? (addition, change, removal, scope_change)
        3. What is the impact level? (low, medium, high)
        4. Which existing tasks are affected?
        
        Respond in JSON format:
        {{
            "has_modifications": true/false,
            "modification_type": "type",
            "impact_level": "level",
            "affected_tasks": ["task1", "task2"],
            "description": "brief description of changes"
        }}
        """
    )
    
    formatted_prompt = prompt.format(
        new_request=new_request,
        current_plan_summary=plan_summary
    )
    
    try:
        response = llm.invoke([HumanMessage(content=formatted_prompt)]).content
        # Parse JSON response from LLM
        analysis = json.loads(response)
        return analysis
    except json.JSONDecodeError:
        # Fallback response if JSON parsing fails
        print("Warning: Could not parse LLM response as JSON, using fallback analysis")
        return {
            "has_modifications": False,
            "modification_type": "unknown",
            "impact_level": "low",
            "affected_tasks": [],
            "description": "Unable to parse modification analysis"
        }

def _summarize_plan(plan: list) -> str:
    """
    Create a human-readable summary of the current task plan.
    
    This function converts the task plan into a format suitable for LLM analysis,
    highlighting key information like task roles, goals, and current status.
    
    Args:
        plan: List of Task objects to summarize
        
    Returns:
        Formatted string summary of the plan
    """
    if not plan:
        return "No existing plan"
    
    summary_parts = []
    for task in plan:
        status = task.get("status", "unknown")
        role = task.get("role", "unknown")
        goal = task.get("goal", "no goal")
        summary_parts.append(f"- {role}: {goal} (Status: {status})")
    
    return "\n".join(summary_parts)