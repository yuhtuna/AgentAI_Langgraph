"""
HITL (Human-in-the-Loop) Controller Node

This node acts as a checkpoint in the LangGraph workflow that can pause execution
when human input is needed. It manages the pause/resume lifecycle and provides
clear communication about why the system is paused.

Key Responsibilities:
- Monitor execution state for conditions requiring human input
- Pause execution when clarification, approval, or user input is needed
- Display current system state to users during pauses
- Resume execution after receiving user input
- Maintain pause state consistency throughout the workflow
"""

from state import AgentState
from config import llm
from langchain.schema import HumanMessage, SystemMessage
import json

def hitl_controller_node(state: AgentState) -> AgentState:
    """
    Main HITL controller that decides whether to pause execution or continue.
    
    This function implements the core pause/resume logic by checking multiple
    conditions that might require human intervention. When a pause is needed,
    it sets the appropriate flags and displays system state information.
    
    Args:
        state: Current AgentState containing all workflow information
        
    Returns:
        Updated AgentState with pause flags set appropriately
        
    Pause Conditions:
        1. System is already paused (waiting for user input)
        2. Clarification is needed from user
        3. Major plan modifications require user approval
        4. User has requested an interrupt
    """
    print("HITL Controller: Checking if pause is needed...")
    
    # CASE 1: System is already paused - maintain pause state
    if state.get("is_paused", False):
        print(f"System is PAUSED: {state.get('pause_reason', 'Unknown reason')}")
        print("Waiting for user input...")
        
        # Ensure waiting flag is set and display current state
        state["waiting_for_user_input"] = True
        _display_system_state(state)
        
        # Return without proceeding - execution remains paused
        return state
    
    # CASE 2: Check if we're resuming from a previous pause
    if state.get("waiting_for_user_input", False) and state.get("user_input_received"):
        print("User input received! Resuming execution...")
        _clear_pause_state(state)
        return state
    
    # CASE 3: Evaluate if a new pause is needed
    pause_decision = _evaluate_pause_conditions(state)
    
    if pause_decision["should_pause"]:
        print(f"Pausing execution: {pause_decision['reason']}")
        _set_pause_state(state, pause_decision["reason"])
        return state
    
    # No pause needed - continue execution
    print("HITL Controller: No pause needed, continuing execution...")
    return state

def _evaluate_pause_conditions(state: AgentState) -> dict:
    """
    Evaluate all conditions that might require pausing execution.
    
    This function implements the business logic for determining when
    human input is needed. It checks multiple criteria and returns
    a decision with the reason for any pause.
    
    Args:
        state: Current AgentState to evaluate
        
    Returns:
        Dictionary with 'should_pause' boolean and 'reason' string
    """
    # Condition 1: Clarification needed from user
    if state.get("is_clarification_needed", False):
        return {
            "should_pause": True,
            "reason": "Clarification needed from user"
        }
    
    # Condition 2: Major plan changes requiring user approval
    if state.get("task_plan") and len(state.get("task_plan", [])) > 0:
        if _needs_user_approval(state):
            return {
                "should_pause": True,
                "reason": "Major plan change detected - user approval required"
            }
    
    # Condition 3: User has requested an interrupt
    if state.get("user_interrupt"):
        return {
            "should_pause": True,
            "reason": f"User interrupt: {state['user_interrupt']}"
        }
    
    # No pause conditions met
    return {
        "should_pause": False,
        "reason": ""
    }

def _needs_user_approval(state: AgentState) -> bool:
    """
    Determine if the current state requires user approval for plan changes.
    
    This function implements the risk assessment logic for plan modifications.
    High-risk changes (like adding new major components) automatically
    trigger a pause for user approval.
    
    Args:
        state: Current AgentState to evaluate
        
    Returns:
        True if user approval is needed, False otherwise
        
    Risk Assessment Criteria:
        - Adding new major components (DatabaseWorker, FrontendWorker)
        - Modifying core system architecture
        - Changes affecting multiple existing tasks
    """
    task_plan = state.get("task_plan", [])
    
    # First-time plans don't need approval
    if not task_plan:
        return False
    
    # Check for high-risk changes that need approval
    for task in task_plan:
        # Example: Pause for approval if adding new major components
        if (task.get("role") in ["DatabaseWorker", "FrontendWorker"] and 
            task.get("status") == "pending"):
            return True
    
    return False

def _display_system_state(state: AgentState) -> None:
    """
    Display current system state to the user during pauses.
    
    This function provides users with a comprehensive overview of the
    current development status, including task progress and pause reasons.
    
    Args:
        state: Current AgentState to display
    """
    print("\n" + "="*50)
    print("CURRENT SYSTEM STATE:")
    print(f"Task: {state.get('user_request', 'No task')}")
    print(f"Plan: {len(state.get('task_plan', []))} tasks")
    print(f"Completed: {len(state.get('completed_tasks', []))} tasks")
    print(f"Pause Reason: {state.get('pause_reason', 'None')}")
    print("="*50)

def _set_pause_state(state: AgentState, reason: str) -> None:
    """
    Set the pause state flags in the AgentState.
    
    Args:
        state: AgentState to modify
        reason: Human-readable reason for the pause
    """
    state["is_paused"] = True
    state["pause_reason"] = reason
    state["waiting_for_user_input"] = True

def _clear_pause_state(state: AgentState) -> None:
    """
    Clear all pause-related flags when resuming execution.
    
    Args:
        state: AgentState to modify
    """
    state["waiting_for_user_input"] = False
    state["is_paused"] = False
    state["pause_reason"] = ""
    # Clear the input to prevent reprocessing
    state["user_input_received"] = None

def resume_execution(state: AgentState, user_input: str, action: str = "continue") -> AgentState:
    """
    Resume execution after receiving user input.
    
    This function is the external interface for resuming execution after
    a pause. It updates the state with user input and clears pause flags.
    
    Args:
        state: AgentState to modify
        user_input: The input provided by the user
        action: The action type that triggered the resume
        
    Returns:
        Updated AgentState ready for continued execution
        
    Usage:
        This function can be called externally (e.g., from a web interface
        or interactive runner) to resume the graph execution.
    """
    print(f"Resuming execution with user input: {user_input}")
    print(f"Action: {action}")
    
    # Update state with user input and resume information
    state["user_input_received"] = user_input
    state["resume_trigger"] = action
    
    # Clear pause state to allow execution to continue
    _clear_pause_state(state)
    
    return state
