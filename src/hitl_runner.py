"""
Interactive HITL (Human-in-the-Loop) Runner

This module provides an interactive command-line interface for running the LangGraph
workflow with full HITL support. It handles the complete lifecycle of pause/resume
operations and provides a user-friendly way to interact with the system.

Key Features:
- Interactive pause/resume functionality
- Real-time state display during pauses
- User input collection and processing
- Automatic execution flow management
- Error handling and recovery

Usage:
    python hitl_runner.py

This runner is ideal for:
- Interactive development and testing
- Demonstrating HITL functionality
- Debugging workflow issues
- Learning how the system responds to different inputs
"""

from state import AgentState
from nodes.manager import manager_node
from nodes.hitl_controller import hitl_controller_node
from nodes.hitl_controller import resume_execution

class HITLRunner:
    """
    Interactive runner for the HITL-enabled LangGraph workflow.
    
    This class manages the complete execution lifecycle, including:
    - Running individual nodes in sequence
    - Detecting when pauses are needed
    - Collecting user input during pauses
    - Resuming execution after user input
    - Displaying system state information
    """
    
    def __init__(self):
        """
        Initialize the HITL runner with default configuration.
        """
        self.state = None
        self.is_running = False
    
    def run(self, initial_request: str):
        """
        Run the complete HITL workflow with the given initial request.
        
        This method orchestrates the entire development process, automatically
        pausing when human input is needed and resuming when input is received.
        
        Args:
            initial_request: The user's initial development request
            
        The workflow follows this pattern:
        1. Initialize state with user request
        2. Run manager node for request analysis
        3. Run HITL controller to check for pause conditions
        4. If paused, collect user input and resume
        5. Continue with normal development workflow
        """
        print("Starting HITL Workflow")
        print("=" * 50)
        
        # Initialize the workflow state
        self.state = self._initialize_state(initial_request)
        self.is_running = True
        
        try:
            # PHASE 1: Request Analysis and HITL Check
            print("\nPhase 1: Analyzing Request and Checking HITL Conditions")
            print("-" * 60)
            
            # Step 1: Run manager node to analyze the request
            print("Running Manager Node...")
            self.state = manager_node(self.state)
            
            # Display analysis results
            self._display_analysis_results()
            
            # Step 2: Run HITL controller to check for pause conditions
            print("\nRunning HITL Controller...")
            self.state = hitl_controller_node(self.state)
            
            # Check if we need to pause for user input
            if self._should_pause():
                self._handle_pause()
            
            # PHASE 2: Continue with normal development workflow
            print("\nPhase 2: Continuing Development Workflow")
            print("-" * 60)
            
            # For demo purposes, we'll show what would happen next
            print("Development workflow would continue with:")
            print("- Context retrieval and planning")
            print("- Task execution and monitoring")
            print("- Result aggregation and testing")
            print("- Final validation and delivery")
            
            print("\nHITL Workflow completed successfully!")
            
        except Exception as e:
            print(f"\nWorkflow failed with error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
    
    def _initialize_state(self, user_request: str) -> AgentState:
        """
        Initialize the AgentState with the user's request.
        
        Args:
            user_request: The development request from the user
            
        Returns:
            Initialized AgentState ready for workflow execution
        """
        return AgentState(
            user_request=user_request,
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
            # HITL fields initialized for normal execution
            is_paused=False,
            pause_reason="",
            waiting_for_user_input=False,
            user_input_received=None,
            resume_trigger=None
        )
    
    def _display_analysis_results(self):
        """
        Display the results of the manager node analysis.
        
        This method shows users what the system discovered about their request,
        including whether clarification is needed and any plan modifications detected.
        """
        print("\nAnalysis Results:")
        print(f"  Clarification needed: {self.state['is_clarification_needed']}")
        
        if self.state.get('clarified_request'):
            print(f"  Clarified request: {self.state['clarified_request']}")
        
        if self.state.get('manager_analysis'):
            print(f"  Manager analysis: {self.state['manager_analysis']}")
        
        if self.state.get('user_interrupt'):
            print(f"  User interrupt: {self.state['user_interrupt']}")
    
    def _should_pause(self) -> bool:
        """
        Determine if the workflow should pause for user input.
        
        Returns:
            True if a pause is needed, False otherwise
        """
        return (self.state.get("is_paused", False) or 
                self.state.get("waiting_for_user_input", False))
    
    def _handle_pause(self):
        """
        Handle the pause state by collecting user input and resuming execution.
        
        This method manages the complete pause/resume cycle:
        1. Display current system state
        2. Collect user input
        3. Resume execution with the new input
        4. Continue workflow
        """
        print("\n" + "="*60)
        print("SYSTEM PAUSED - Human Input Required")
        print("="*60)
        
        # Display current system state
        self._display_current_state()
        
        # Collect user input
        user_input = self._get_user_input()
        
        # Resume execution with user input
        print("\nResuming execution...")
        self.state = resume_execution(self.state, user_input, "user_input")
        
        # Run HITL controller again to continue
        self.state = hitl_controller_node(self.state)
        
        print("Execution resumed successfully!")
    
    def _display_current_state(self):
        """
        Display the current system state during pauses.
        
        This method provides users with a comprehensive overview of what
        the system is working on and why it paused.
        """
        print("\nCurrent System State:")
        print(f"  Task: {self.state.get('user_request', 'No task')}")
        print(f"  Pause Reason: {self.state.get('pause_reason', 'None')}")
        
        if self.state.get('task_plan'):
            print(f"  Task Plan: {len(self.state['task_plan'])} tasks")
        
        if self.state.get('completed_tasks'):
            print(f"  Completed: {len(self.state['completed_tasks'])} tasks")
    
    def _get_user_input(self) -> str:
        """
        Collect user input during pauses.
        
        Returns:
            The user's input as a string
        """
        print("\nPlease provide your input:")
        print("(Type your response and press Enter)")
        
        try:
            user_input = input("> ").strip()
            if not user_input:
                user_input = "Continue with current plan"
                print(f"Using default input: {user_input}")
            return user_input
        except KeyboardInterrupt:
            print("\nInput cancelled, using default response")
            return "Continue with current plan"
    
    def _update_state(self, new_state: AgentState):
        """
        Update the runner's internal state.
        
        Args:
            new_state: New AgentState to use
        """
        self.state = new_state

def main():
    """
    Main entry point for the interactive HITL runner.
    
    This function provides a simple interface for users to start the HITL
    workflow with their own development requests.
    """
    print("HITL Interactive Runner")
    print("=" * 50)
    print("This runner demonstrates the complete HITL workflow.")
    print("You can test different types of requests and see how")
    print("the system automatically pauses when human input is needed.")
    print()
    
    # Get user request
    print("Enter your development request:")
    print("(Examples: 'Create a web app', 'Add user authentication', 'Improve existing features')")
    
    try:
        user_request = input("Request: ").strip()
        if not user_request:
            user_request = "[Enter your development request]"
            print(f"Using default request: {user_request}")
    except KeyboardInterrupt:
        print("\nRequest cancelled, using default")
        user_request = "[Enter your development request]"
    
    print()
    
    # Create and run the HITL runner
    runner = HITLRunner()
    runner.run(user_request)

if __name__ == "__main__":
    main()
