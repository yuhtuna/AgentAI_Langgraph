from src.state import AgentState
from langchain.prompts import PromptTemplate
from src.config import llm

def aggregator_node(state: AgentState) -> AgentState:
    """
    Aggregates the state of the agent.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The aggregated state of the agent.
    """
    
    ##let's start off with something simple to test if connections are working
    """
    prompt = PromptTemplate(
        input_variables=["task_plan", "completed_tasks"],
        template="Aggregate the following task plan: {task_plan} and completed tasks: {completed_tasks}."
    )
    state["final_deliverable"] = await llm(prompt.format(
        task_plan=state["task_plan"],
        completed_tasks=state["completed_tasks"]
    ))
    """

    completed_tasks = state.get('completed_tasks', [])
    
    if not completed_tasks:
        print("⚠️  No completed tasks to aggregate")
        state['final_deliverable'] = "No work completed yet"
        return state 
    
    print(f"🔗 Aggregating {len(completed_tasks)} completed tasks:")
    
    deliverable_parts = []
    for task in completed_tasks:
        print(f"  📦 Integrating: {task['role']} - {task['result'][:50]}...")
        deliverable_parts.append(f"{task['role']}: {task['result']}")
    
    # Create integrated deliverable
    final_deliverable = f"""
    PROJECT DELIVERABLE:
    User Request: {state.get('clarified_request', 'N/A')}
    
    Integrated Components:
    {chr(10).join(f'- {part}' for part in deliverable_parts)}
    
    Total Components: {len(deliverable_parts)}
    Cost: ${state.get('current_cost', 0):.2f}
    """
    
    state['final_deliverable'] = final_deliverable
    print(f"📋 Final deliverable created with {len(completed_tasks)} integrated components")
    return state