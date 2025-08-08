from src.state import AgentState
from langchain.prompts import PromptTemplate
from src.config import llm

async def aggregator_node(state: AgentState) -> AgentState:
    """
    Aggregates the state of the agent.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The aggregated state of the agent.
    """
    prompt = PromptTemplate(
        input_variables=["task_plan", "completed_tasks"],
        template="Aggregate the following task plan: {task_plan} and completed tasks: {completed_tasks}."
    )
    state["final_deliverable"] = await llm(prompt.format(
        task_plan=state["task_plan"],
        completed_tasks=state["completed_tasks"]
    ))
    return state