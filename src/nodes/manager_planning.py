from src.state import AgentState
from src.config import llm 
from langchain.prompts import PromptTemplate

async def manager_planning_node(state: AgentState) -> AgentState:
    """
    This function processes the agent's state and returns it.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The processed state of the agent.
    """
    prompt = PromptTemplate(
        input_variables = ["clarified_request", "retrieved_context"],
        template = "Based on the clarified user request: {clarified_request} and the retrieved context: {retrieved_context}, " \
        "generate a detailed plan of action for the agent. " \  
        "The plan should be actionable and clear, allowing the agent to proceed effectively."
    )
    tasks = [] 
    response = await llm(prompt.format(clarified_request=state["clarified_request"], retrieved_context=state["retrieved_context"]))
    tasks = []
    for i, task_desc in enumerate(response.split("\n")):
        tasks.append({
            "id": i,
            "role": task_desc.split(":")[0],
            "goal": task_desc.split(":")[1],
            "status": "pending",
            "dependencies": [],
            "result": None,
            "generated_test_cases": None,
            "self_validation_status": None
        })
    state["task_plan"] = tasks
    return state