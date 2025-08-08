from src.state import AgentState
from src.config import llm
from langchain.prompts import PromptTemplate

async def manager_node(state:AgentState) -> AgentState: 
    
    prompt = PromptTemplate(
        input_variables=["user_request", "current_state"],
        template = "Analyze the user's request: {user_request} and the current state of the agent: {current_state}. " \
        "Based on this analysis, determine the next steps for the agent. " \
        "Provide a detailed plan of action that includes any necessary tasks, resources, or considerations. " \
        "The plan should be actionable and clear, allowing the agent to proceed effectively."
    )
    response = await llm(prompt.format(user_request=state["user_request"], current_state=state["current_state"]))
    return state