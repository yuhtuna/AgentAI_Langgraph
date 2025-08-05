from src.state import AgentState
from src.config import llm
from langchain.prompts import PromptTemplate

def worker_node(state: AgentState) -> AgentState:
    """
    Worker node that processes tasks and updates the state.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The updated state after processing tasks.
    """
    #Placeholder for worker_node logic
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
    """
    pending_tasks = [task for task in state.get('task_plan', []) if task['status'] == 'pending']
    completed_tasks = state.get('completed_tasks', [])
    
    if not pending_tasks:
        print("ℹ️  No pending tasks to execute")
        return state
    
    # Find next executable task (dependencies met)
    executable_task = None
    completed_task_ids = {task['id'] for task in completed_tasks}
    
    for task in pending_tasks:
        if all(dep_id in completed_task_ids for dep_id in task['dependencies']):
            executable_task = task
            break
    
    if not executable_task:
        print("⏳ No tasks ready for execution (waiting on dependencies)")
        return state
    
    # Execute the task
    print(f"🔨 Executing Task {executable_task['id']}: {executable_task['goal']}")
    executable_task['status'] = 'in_progress'
    
    # Build phase
    print(f"  🏗️  BUILD PHASE: {executable_task['role']} working on task...")
    simulated_result = f"Completed {executable_task['goal']} - Generated code/components for {executable_task['role']}"
    executable_task['result'] = simulated_result
    
    # Self-validation phase
    print(f"  🧪 SELF-VALIDATION PHASE: Generating and running tests...")
    test_cases = [
        f"Unit test for {executable_task['role']} component",
        f"Integration test for {executable_task['goal'][:30]}...",
        f"Performance test for core functionality"
    ]
    executable_task['generated_test_cases'] = test_cases
    
    validation_passed = True  # Simulate successful validation
    
    if validation_passed:
        executable_task['self_validation_status'] = 'Passed'
        executable_task['status'] = 'completed'
        completed_tasks.append(executable_task)
        print(f"  ✅ Self-validation PASSED for task {executable_task['id']}")
    else:
        executable_task['self_validation_status'] = 'Failed'
        executable_task['status'] = 'failed'
        print(f"  ❌ Self-validation FAILED for task {executable_task['id']}")
    
    # Update cost
    state['current_cost'] = state.get('current_cost', 0) + 2.50
    
    state['completed_tasks'] = completed_tasks
    return state