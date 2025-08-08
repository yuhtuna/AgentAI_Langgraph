from src.state import AgentState
from src.config import llm
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

def manager_node(state:AgentState) -> AgentState: 
    #First, let's just check if clarification is needed 
    user_request = state["user_request"]
    prompt = PromptTemplate(
        input_variables = ["user_request"],
        template = """
        Based on the user request: {user_request}, determine if clarification is needed in 
        order to proceed with the task, particularly if it involves: 
        - Technical requirements (frameworks, databases, etc.)
        - Functional requirements (specific features, user flows)
        - Non-functional requirements (performance, scalability)
        - Target audience or use case
        - Integration requirements
        
        If clarification needed, generate specific questions.
        If clear enough, provide a clarified, detailed version.
        """
    )
    formatted_prompt = prompt.format(user_request=user_request)
    response = llm([HumanMessage(content=formatted_prompt)]).content
    print(response)
    if("Clarification needed" in response):
        state["is_clarification_needed"] = True
        state["clarification_questions"] = response.split("\n")
        print("❓ Clarification needed. Questions generated:")
        for question in state["clarification_questions"]:
            print(f"  - {question}")
    else:
        state["is_clarification_needed"] = False
        state["clarified_request"] = response.strip()
        print(f"✅ Clarified request: {state['clarified_request']}")
    return state