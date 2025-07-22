from src.state import AgentState
from src.config import llm
from langchain.prompts import PromptTemplate

async def worker_node(state: AgentState) -> AgentState:
    """
    Worker node that processes tasks and updates the state.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The updated state after processing tasks.
    """
    for task in state["task_plan"]: 
        if(task["status"] == "pending"):
            task["status"] = "in progress" 
            prompt = PromptTemplate(
                input_variables=["role", "goal", "context"],
                template="You are a {role} tasked with: {goal}. " \
                         "Context: {context}. " \
                         "Please provide a detailed response to accomplish this task."
            )
            response = await llm(prompt.format(role=task["role"], goal=task["goal"], context=task.get("context", "")))
            task["result"] = response.split("Tests:")[0]
            task["generated_test_cases"] = response.split("Tests:")[1].split("\n") if "Tests:" in response else []
            task["status"] = "completed"
            state["completed_tasks"][task["id"]] = task
    return state