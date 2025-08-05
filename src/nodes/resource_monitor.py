from src.state import AgentState

def resource_monitor_node(state: AgentState) -> AgentState:
    active_tasks = [task for task in state.get('task_plan', []) if task['status'] != 'cancelled']
    base_cost_per_task = 2.50  # Simulated cost per task
    estimated_cost = len(active_tasks) * base_cost_per_task
    
    state['cost_estimate'] = estimated_cost
    state['current_cost'] = state.get('current_cost', 0)
    
    print(f"💰 Cost Analysis:")
    print(f"  Active tasks: {len(active_tasks)}")
    print(f"  Estimated cost: ${estimated_cost:.2f}")
    print(f"  Current spend: ${state['current_cost']:.2f}")
    
    if estimated_cost > 20:
        print(f"  ⚠️  Warning: Estimated cost exceeds $20 threshold")
    return state