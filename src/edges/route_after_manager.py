"""
Routing Logic After Manager Node

This module defines the conditional routing logic that determines the next step
in the development workflow after the manager node has analyzed a user request.

The routing decisions are based on:
1. Whether clarification is needed from the user
2. Whether the request requires planning or replanning
3. The current state of the development process

This routing is critical for the HITL system as it determines when to pause
for user input versus when to continue with automated development.
"""

from state import AgentState

def route_after_manager(state: AgentState) -> str:
    """
    Determine the next step in the workflow after manager analysis.
    
    This function implements the routing logic that decides whether to:
    - Pause for user clarification
    - Proceed with planning and development
    - Replan existing work
    
    The routing is based on the state set by the manager node, which includes
    flags for clarification needs and plan modifications.
    
    Args:
        state: Current AgentState containing manager analysis results
        
    Returns:
        String indicating the next workflow step:
        - "clarify": Pause for user clarification
        - "plan": Proceed with planning phase
        - "replan": Replan existing development work
    """
    # CASE 1: Clarification needed from user
    # This triggers a pause in the HITL system
    if state.get("is_clarification_needed", False):
        return "clarify"
    
    # CASE 2: No existing plan - proceed with initial planning
    # This is the normal flow for first-time requests
    if not state.get("task_plan") or len(state.get("task_plan", [])) == 0:
        return "plan"
    
    # CASE 3: Existing plan with modifications
    # Check if the manager detected significant plan changes
    if state.get("manager_analysis"):
        # For now, we'll replan if any modifications are detected
        # In a more sophisticated system, you might analyze the impact level
        return "replan"
    
    # CASE 4: Existing plan with no modifications
    # Continue with the current plan
    return "plan"