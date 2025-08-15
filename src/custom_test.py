"""
Custom HITL Testing Framework

This module provides a flexible testing framework that allows developers to test
the HITL functionality with their own custom prompts and scenarios. It's designed
to be easily customizable for different testing needs.

Key Features:
- Test with your own custom prompts
- Test plan modification detection
- Test clarification flow with vague requests
- Easy customization for different scenarios

Usage:
    1. Edit the prompt variables in the test functions
    2. Run: python custom_test.py
    3. Observe how the system handles different types of requests

This framework is ideal for:
- Testing specific use cases
- Demonstrating HITL functionality to stakeholders
- Debugging pause/resume behavior
- Learning how different prompts affect system behavior
"""

from state import AgentState, Task
from nodes.manager import manager_node
from nodes.hitl_controller import hitl_controller_node

def test_custom_prompt():
    """
    Test the HITL system with your own custom prompt.
    
    This function demonstrates how the system processes a clear, well-defined
    request. It shows the complete flow from request analysis through
    clarification and HITL decision making.
    
    Customization:
        - Edit the 'your_prompt' variable to test different scenarios
        - Try various types of requests (web apps, mobile apps, APIs, etc.)
        - Test different levels of detail in your prompts
    """
    print("Custom HITL Test")
    print("=" * 50)
    
    # CUSTOMIZE THIS: Change this prompt to test different scenarios
    your_prompt = "[Enter your custom development request here]"
    
    print(f"Testing with prompt: {your_prompt}")
    
    # Create initial state for the test
    state = AgentState(
        user_request=your_prompt,
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
    
    # STEP 1: Run manager node to analyze the request
    print("\nStep 1: Running Manager Node...")
    state = manager_node(state)
    
    # Display analysis results
    print(f"Clarification needed: {state['is_clarification_needed']}")
    if state.get('clarified_request'):
        print(f"Clarified request: {state['clarified_request']}")
    
    # STEP 2: Run HITL controller to check for pause conditions
    print("\nStep 2: Running HITL Controller...")
    state = hitl_controller_node(state)
    
    # Display HITL decision
    print(f"Is paused: {state['is_paused']}")
    print(f"Pause reason: {state.get('pause_reason', 'None')}")
    
    # Provide guidance if system is paused
    if state.get('is_paused'):
        print("\nSystem is paused! You can now:")
        print("1. Modify the prompt and test again")
        print("2. Check the clarification questions")
        print("3. Test different scenarios")
    
    return state

def test_with_existing_plan():
    """
    Test plan modification detection with an existing development plan.
    
    This function demonstrates how the system detects when a new request
    modifies existing work. It's useful for testing the modification
    analysis and impact assessment features.
    
    Customization:
        - Edit the 'modification_request' variable to test different modifications
        - Modify the existing_tasks list to simulate different project states
        - Test various types of modifications (additions, changes, removals)
    """
    print("\n" + "="*50)
    print("Testing with Existing Task Plan")
    print("=" * 50)
    
    # Create a realistic existing development plan
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
        )
    ]
    
    # CUSTOMIZE THIS: Change this to test different modification scenarios
    modification_request = "[Enter your modification request here]"
    
    print(f"Modification request: {modification_request}")
    
    # Create state with existing plan
    state = AgentState(
        user_request=modification_request,
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
    
    # Run manager node to analyze modifications
    print("\nRunning Manager Node...")
    state = manager_node(state)
    
    # Display modification analysis results
    if state.get('manager_analysis'):
        print(f"Manager analysis: {state['manager_analysis']}")
    
    # Run HITL controller to check for pause conditions
    print("\nRunning HITL Controller...")
    state = hitl_controller_node(state)
    
    # Display HITL decision
    print(f"Is paused: {state['is_paused']}")
    print(f"Pause reason: {state.get('pause_reason', 'None')}")
    
    return state

def test_vague_request():
    """
    Test clarification detection with deliberately vague requests.
    
    This function demonstrates how the system handles incomplete or unclear
    requests by automatically detecting when clarification is needed and
    generating specific questions to help users provide more details.
    
    Customization:
        - Edit the 'vague_request' variable to test different vague scenarios
        - Try various levels of vagueness to see where the system draws the line
        - Test different types of unclear requests
    """
    print("\n" + "="*50)
    print("Testing with Vague Request")
    print("=" * 50)
    
    # CUSTOMIZE THIS: Change this to test different vague request scenarios
    vague_request = "[Enter your vague request here]"
    
    print(f"Vague request: {vague_request}")
    
    # Create state with vague request
    state = AgentState(
        user_request=vague_request,
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
    
    # Run manager node to detect clarification needs
    print("\nRunning Manager Node...")
    state = manager_node(state)
    
    # Display clarification detection results
    print(f"Clarification needed: {state['is_clarification_needed']}")
    if state['is_clarification_needed']:
        print("Clarification questions:")
        for i, question in enumerate(state['clarification_questions'], 1):
            print(f"  {i}. {question}")
    
    # Run HITL controller to see if pause is triggered
    print("\nRunning HITL Controller...")
    state = hitl_controller_node(state)
    
    # Display HITL decision
    print(f"Is paused: {state['is_paused']}")
    print(f"Pause reason: {state.get('pause_reason', 'None')}")
    
    return state

if __name__ == "__main__":
    print("Starting Custom HITL Tests")
    print("=" * 60)
    
    try:
        # Run all test scenarios
        print("Running comprehensive HITL tests...")
        
        # Test 1: Custom prompt analysis
        test_custom_prompt()
        
        # Test 2: Plan modification detection
        test_with_existing_plan()
        
        # Test 3: Vague request handling
        test_vague_request()
        
        print("\nAll custom tests completed successfully!")
        
        # Provide customization guidance
        print("\nTo test with different prompts:")
        print("1. Edit the 'your_prompt' variable in test_custom_prompt()")
        print("2. Edit the 'modification_request' variable in test_with_existing_plan()")
        print("3. Edit the 'vague_request' variable in test_vague_request()")
        print("4. Run: python custom_test.py")
        
        print("\nTesting Tips:")
        print("- Try different types of requests (web, mobile, API, etc.)")
        print("- Test various levels of detail and clarity")
        print("- Experiment with different modification scenarios")
        print("- Observe how the system adapts to different inputs")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
