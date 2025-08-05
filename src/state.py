from typing import TypedDict, Optional , List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class Task(TypedDict):
    id: int
    role: str # e.g., 'CodeWorker', 'TestWriter'
    goal: str
    # NEW: Fields to support dynamic planning and HITL
    status: str # 'pending', 'in_progress', 'completed', 'cancelled', 'failed'
    dependencies: List[int] # List of other task IDs to be completed first
    result: Optional[str]
    generated_test_cases: Optional[List[str]]
    self_validation_status: Optional[str] # e.g., 'Passed', 'Failed'

class ValidationReport(TypedDict):
    status: str # "Passed" or "Failed"
    details: str

class AgentState(TypedDict):
    user_request: str
    clarified_request: str
    is_clarification_needed: bool
    clarification_questions: List[str]
    retrieved_context: List[str]
    task_plan: List[Task]
    completed_tasks: List[Task]
    final_deliverable: str
    validation_report: ValidationReport
    cost_estimate: float
    current_cost: float