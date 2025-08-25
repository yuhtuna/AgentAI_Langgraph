from typing import TypedDict, Optional , List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class Task(TypedDict):
    """
    Represents a development task in the system.
    Each task has a specific role, goal, and tracks its progress through the development lifecycle.
    """
    id: int
    role: str # e.g., 'CodeWorker', 'TestWriter'
    goal: str
    # Fields to support dynamic planning and HITL (Human-in-the-Loop)
    status: str # 'pending', 'in_progress', 'completed', 'cancelled', 'failed'
    dependencies: List[int] # List of other task IDs to be completed first
    result: Optional[str]
    generated_test_cases: Optional[List[str]]
    self_validation_status: Optional[str] # e.g., 'Passed', 'Failed'

class ValidationReport(TypedDict):
    """
    Contains the validation results for a completed development task or final deliverable.
    """
    status: str # "Passed" or "Failed"
    details: str

class AgentState(TypedDict):
    """
    The central state object that flows through the LangGraph workflow.
    It holds all information that agents work with and tracks the development process.
    
    HITL (Human-in-the-Loop) Integration:
    - The system can automatically pause execution when human input is needed
    - Users can provide clarification, modify plans, or approve changes
    - Execution resumes automatically after receiving user input
    """
    # Core development request and planning
    user_request: str
    clarified_request: str
    is_clarification_needed: bool
    clarification_questions: List[str]
    retrieved_context: List[str]
    task_plan: List[Task]
    completed_tasks: List[Task]
    final_deliverable: str
    validation_report: ValidationReport
    
    # Cost tracking and resource management
    cost_estimate: float
    current_cost: float
    
    # HITL pause mechanism - enables human interaction during execution
    user_interrupt: Optional[str]  # Set when user wants to modify direction
    manager_analysis: Optional[str]  # JSON string containing modification analysis
    
    # Pause state management
    is_paused: bool  # True when execution is paused for human input
    pause_reason: str  # Human-readable reason why execution paused
    waiting_for_user_input: bool  # True when actively waiting for user response
    user_input_received: Optional[str]  # The actual input provided by user
    resume_trigger: Optional[str]  # What action caused execution to resume