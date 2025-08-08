from src.state import AgentState
from src.state import Task
from src.config import llm
from langchain.prompts import PromptTemplate
import json
from typing import List, Dict, Any

# Prompt template for task generation
TASK_PLANNING_TEMPLATE = """You are an AI Project Manager responsible for breaking down user requests into specific, actionable tasks. Your goal is to create a detailed task plan that can be executed by specialized AI workers.

Context:
{context}

User Request: {request}

{replanning_context}

Instructions:
1. Break down the request into logical, sequential tasks
2. Each task must have:
   - A unique ID (sequential integers starting from 1)
   - A specific role from: ['ArchitectWorker', 'BackendWorker', 'FrontendWorker', 'TestWorker', 'UIWorker', 'DevOpsWorker']
   - A clear, actionable goal
   - Dependencies (list of task IDs that must be completed before this task)
   - Status (should be 'pending' for new tasks)

3. Ensure tasks follow a logical order and dependencies make sense
4. For replanning scenarios, consider existing tasks and their states

Output the task plan as a JSON array where each task follows this structure:
{
    "id": int,
    "role": str,
    "goal": str,
    "status": "pending",
    "dependencies": [int],
    "result": null,
    "generated_test_cases": null,
    "self_validation_status": null
}

Response Format:
{
    "tasks": [
        // array of task objects
    ],
    "reasoning": "Explanation of the task breakdown and dependencies"
}"""

task_planning_prompt = PromptTemplate(
    template=TASK_PLANNING_TEMPLATE,
    input_variables=["context", "request", "replanning_context"]
)

def validate_task_plan(tasks: List[Dict[str, Any]]) -> bool:
    """
    Validates the generated task plan for correctness.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        bool: True if valid, raises ValueError if invalid
    """
    valid_roles = {'ArchitectWorker', 'BackendWorker', 'FrontendWorker', 'TestWorker', 'UIWorker', 'DevOpsWorker'}
    task_ids = set()
    
    for task in tasks:
        # Check required fields
        required_fields = {'id', 'role', 'goal', 'status', 'dependencies'}
        if not all(field in task for field in required_fields):
            raise ValueError(f"Task missing required fields: {required_fields - set(task.keys())}")
        
        # Validate ID is unique and positive integer
        if not isinstance(task['id'], int) or task['id'] < 1:
            raise ValueError(f"Invalid task ID: {task['id']}")
        if task['id'] in task_ids:
            raise ValueError(f"Duplicate task ID: {task['id']}")
        task_ids.add(task['id'])
        
        # Validate role
        if task['role'] not in valid_roles:
            raise ValueError(f"Invalid role '{task['role']}' for task {task['id']}")
        
        # Validate dependencies
        for dep in task['dependencies']:
            if not isinstance(dep, int) or dep < 1:
                raise ValueError(f"Invalid dependency ID {dep} in task {task['id']}")
            if dep >= task['id']:
                raise ValueError(f"Task {task['id']} cannot depend on future task {dep}")
    
    return True

def prepare_replanning_context(state: AgentState) -> str:
    """
    Prepares context string for replanning scenarios.
    
    Args:
        state: Current agent state
        
    Returns:
        str: Context string for replanning
    """
    if not state.get('user_interrupt'):
        return "Initial Planning: Create a new task plan from scratch."
        
    existing_tasks = state.get('task_plan', [])
    context = ["Replanning Required: User interrupt received.", 
               f"Original plan had {len(existing_tasks)} tasks.",
               "Current task statuses:"]
    
    for task in existing_tasks:
        deps = f" (depends on: {task['dependencies']})" if task['dependencies'] else ""
        context.append(f"- Task {task['id']}: {task['status']} - {task['role']}: {task['goal']}{deps}")
    
    context.append(f"\nUser Interrupt: {state['user_interrupt']}")
    return "\n".join(context)

def create_task_objects(task_data: List[Dict[str, Any]]) -> List[Task]:
    """
    Converts raw task dictionaries into Task objects.
    
    Args:
        task_data: List of task dictionaries from LLM
        
    Returns:
        List[Task]: List of validated Task objects
    """
    return [
        Task(
            id=task['id'],
            role=task['role'],
            goal=task['goal'],
            status=task['status'],
            dependencies=task['dependencies'],
            result=None,
            generated_test_cases=None,
            self_validation_status=None
        )
        for task in task_data
    ]


def manager_planning_node(state: AgentState) -> AgentState:
    """
    This function processes the agent's state and returns it with an updated task plan.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The processed state of the agent with updated task plan.
    """
    try:
        # Prepare context and request information
        context = "\n".join(state.get('retrieved_context', ["No additional context available."]))
        request = state.get('clarified_request', state.get('user_request', ''))
        replanning_context = prepare_replanning_context(state)
        
        # Generate task plan using LLM
        response = llm.invoke(
            task_planning_prompt.format(
                context=context,
                request=request,
                replanning_context=replanning_context
            )
        )
        
        # Parse LLM response
        try:
            result = json.loads(response.content)
            tasks = result['tasks']
            reasoning = result.get('reasoning', 'No reasoning provided')
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
        
        # Validate task plan
        validate_task_plan(tasks)
        
        # Convert to Task objects
        task_objects = create_task_objects(tasks)
        
        # Update state
        print(f"\n📋 {'REPLANNING' if state.get('user_interrupt') else 'INITIAL PLANNING'}")
        print(f"LLM Reasoning: {reasoning}")
        print(f"Generated {len(task_objects)} tasks:")
        
        for task in task_objects:
            deps = f" (depends on: {task['dependencies']})" if task['dependencies'] else ""
            print(f"  {task['id']}. {task['role']}: {task['goal']}{deps}")
        
        state['task_plan'] = task_objects
        if state.get('user_interrupt'):
            state['user_interrupt'] = None  # Clear the interrupt
            
        return state
        
    except Exception as e:
        print(f"❌ Error in task planning: {str(e)}")
        # Return state with empty task plan in case of error
        state['task_plan'] = []
        return state