"""
HITL (Human-in-the-Loop) Demo Script

This script demonstrates the complete HITL functionality by running through
realistic development scenarios. It shows how the system automatically pauses
when human input is needed and how users can interact with the paused system.

Demo Scenarios:
1. Basic HITL: Shows plan modification detection and pause/resume functionality
2. Clarification Flow: Demonstrates automatic pause when requests are vague

Usage:
    python demo_hitl.py

This demo is ideal for:
- Understanding how HITL works in practice
- Testing the pause/resume functionality
- Demonstrating the system to stakeholders
- Learning the different pause conditions
"""

from state import AgentState, Task
from nodes.manager import manager_node
from nodes.hitl_controller import hitl_controller_node

def demo_basic_hitl():
    """
    Demonstrate basic HITL functionality with plan modification detection.
    
    This demo creates a realistic scenario where a user wants to add features
    to an existing development project. It shows how the system:
    1. Analyzes the new request against existing work
    2. Detects plan modifications
    3. Decides whether to pause for user approval
    4. Handles the pause/resume cycle
    """
    print("HITL Demo: Basic Functionality")
    print("=" * 50)
    
    # Create a realistic existing task plan
    # This simulates a project that already has some completed work
    existing_tasks = [
        Task(
            id=1,
            role="FrontendWorker",
            goal="[Example: Create basic application structure]",
            status="completed",
            dependencies=[],
            result="[Example: Basic structure created]",
            generated_test_cases=None,
            self_validation_status="Passed"
        ),
        Task(
            id=2,
            role="DatabaseWorker",
            goal="[Example: Set up database schema]",
            status="in_progress",
            dependencies=[],
            result=None,
            generated_test_cases=None,
            self_validation_status=None
        )
    ]
    
    # Create initial state with existing work
    state = AgentState(
        user_request="[Enter your modification request here]",
        clarified_request="",
        is_clarification_needed=False,
        clarification_questions=[],
        retrieved_context=[],
        task_plan=existing_tasks,
        completed_tasks=[],
        final_deliverable="",
        validation_report={"status": "", "details": ""},
        cost_estimate=0.0,
        current_cost=0.0,
        user_interrupt=None,
        manager_analysis=None,
        is_paused=False,
        pause_reason="",
        waiting_for_user_input=False,
        user_input_received=None,
        resume_trigger=None
    )
    
    # Display initial state for context
    print("Initial State:")
    print(f"  User Request: {state['user_request']}")
    print(f"  Existing Tasks: {len(state['task_plan'])}")
    
    # STEP 1: Run manager node to analyze the request
    print("\nStep 1: Running Manager Node...")
    state = manager_node(state)
    
    # Display analysis results
    print(f"  Clarification needed: {state['is_clarification_needed']}")
    if state.get('manager_analysis'):
        print(f"  Manager analysis: {state['manager_analysis'][:100]}...")
    if state.get('user_interrupt'):
        print(f"  User interrupt: {state['user_interrupt']}")
    
    # STEP 2: Run HITL controller to check if pause is needed
    print("\nStep 2: Running HITL Controller...")
    state = hitl_controller_node(state)
    
    # Display HITL decision
    print(f"  Is paused: {state['is_paused']}")
    print(f"  Pause reason: {state.get('pause_reason', 'None')}")
    print(f"  Waiting for user input: {state['waiting_for_user_input']}")
    
    # STEP 3: Simulate user input if system is paused
    if state.get('is_paused'):
        print("\nStep 3: Simulating User Input...")
        print("  (In real usage, this would be interactive)")
        
        # Simulate realistic user input
        user_input = "[Enter your detailed requirements here]"
        print(f"  User input: {user_input}")
        
        # Update state with user input
        state["user_input_received"] = user_input
        state["resume_trigger"] = "modify"
        
        # STEP 4: Resume execution after user input
        print("\nStep 4: Resuming Execution...")
        state = hitl_controller_node(state)
        
        # Display final state
        print(f"  Is paused: {state['is_paused']}")
        print(f"  Waiting for user input: {state['waiting_for_user_input']}")
    
    print("\nDemo completed!")

def demo_clarification_flow():
    """
    Demonstrate the clarification flow with automatic pause detection.
    
    This demo shows how the system handles vague or incomplete requests
    by automatically detecting when clarification is needed and pausing
    execution until the user provides more details.
    """
    print("\nHITL Demo: Clarification Flow")
    print("=" * 50)
    
    # Create a state with a deliberately vague request
    # This will trigger the clarification detection logic
    state = AgentState(
        user_request="[Enter your vague request here]",
        clarified_request="",
        is_clarification_needed=False,
        clarification_questions=[],
        retrieved_context=[],
        task_plan=[],
        completed_tasks=[],
        final_deliverable="",
        validation_report={"status": "", "details": ""},
        cost_estimate=0.0,
        current_cost=0.0,
        user_interrupt=None,
        manager_analysis=None,
        is_paused=False,
        pause_reason="",
        waiting_for_user_input=False,
        user_input_received=None,
        resume_trigger=None
    )
    
    # Display the vague request
    print("Initial State:")
    print(f"  User Request: {state['user_request']}")
    
    # Run manager node to detect clarification needs
    print("\nRunning Manager Node...")
    state = manager_node(state)
    
    # Display clarification results
    print(f"  Clarification needed: {state['is_clarification_needed']}")
    if state['is_clarification_needed']:
        print("  Clarification questions:")
        for i, question in enumerate(state['clarification_questions'], 1):
            print(f"    {i}. {question}")
    
    # Run HITL controller to see if pause is triggered
    print("\nRunning HITL Controller...")
    state = hitl_controller_node(state)
    
    # Display HITL decision
    print(f"  Is paused: {state['is_paused']}")
    print(f"  Pause reason: {state.get('pause_reason', 'None')}")
    
    print("\nClarification demo completed!")

if __name__ == "__main__":
    print("Starting HITL Demo")
    print("=" * 60)
    
    try:
        # Run both demo scenarios
        demo_basic_hitl()
        demo_clarification_flow()
        
        print("\nAll demos completed successfully!")
        print("\nTo run the interactive HITL runner, use:")
        print("   python -m src.hitl_runner")
        
        print("\nDemo Summary:")
        print("- Basic HITL: Shows plan modification detection and pause/resume")
        print("- Clarification Flow: Shows automatic pause for vague requests")
        print("- Both demos demonstrate real-world HITL scenarios")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
