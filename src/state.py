from typing import TypedDict, Optional , List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class Task(TypedDict):
    """
    Represents a task that an agent can perform.
    It includes the task description and any additional metadata.
    """
    id: int
    role: str 
    goal: str
    context: str
    status: str
    result: Optional[str]
    generated_test_cases: Optional[List[str]]
    self_validation_status: Optional[str]

class ValidationReport(TypedDict):
    """
    Represents a validation report for a task.
    It includes the task ID, validation status, and any additional comments.
    """
    task_id: int
    validation_status: str
    details: str

class AgentState(TypedDict):
    """
    The central state object that will be passed between nodes.
    It holds all the information our agents will work with.
    """
    user_request: str
    clarified_request: str
    is_clarification_needed: bool
    clarification_questions: List[str]
    retrieved_information: List[str]
    processed_information: List[str]
    task_plan: List[Task]
    completed_tasks: List[Task]
    final_deliverable: Optional[str]
    validation_reports: List[ValidationReport]
    cost_estimate: float 
    current_cost: float