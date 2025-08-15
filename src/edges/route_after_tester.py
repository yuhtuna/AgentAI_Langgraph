"""
Routing Logic After Tester Node

This module defines the conditional routing logic that determines the next step
in the development workflow after the tester node has validated completed work.

The routing decisions are based on:
1. Whether the validation passed or failed
2. The quality and completeness of the delivered work
3. Whether additional development work is needed

This routing ensures that the system can handle both successful completions
and cases where work needs to be redone or improved.
"""

from state import AgentState

def route_after_tester(state: AgentState) -> str:
    """
    Determine the next step in the workflow after testing/validation.
    
    This function implements the routing logic that decides whether to:
    - End the workflow (validation passed)
    - Replan and rework (validation failed)
    - Continue with additional development
    
    The routing is based on the validation results from the tester node,
    which assesses the quality and completeness of the delivered work.
    
    Args:
        state: Current AgentState containing validation results
        
    Returns:
        String indicating the next workflow step:
        - "passed": Work completed successfully, end workflow
        - "failed": Validation failed, replan and rework
    """
    # Get the validation status from the state
    validation_status = state.get("validation_report", {}).get("status", "")
    
    # CASE 1: Validation passed - work completed successfully
    # This ends the workflow as the development goal has been achieved
    if validation_status.lower() == "passed":
        return "passed"
    
    # CASE 2: Validation failed - work needs to be redone
    # This triggers a replanning phase to address the issues
    elif validation_status.lower() == "failed":
        return "failed"
    
    # CASE 3: Validation status unclear or missing
    # Default to replanning to ensure quality
    else:
        print("Warning: Validation status unclear, defaulting to replan")
        return "failed"

    