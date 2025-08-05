from typing import TypedDict, List, Optional, Dict, Literal
from langgraph.graph import StateGraph, END
import time
import json

# State Definitions
class Task(TypedDict):
    id: int
    role: str  # e.g., 'CodeWorker', 'TestWriter'
    goal: str
    status: str  # 'pending', 'in_progress', 'completed', 'cancelled', 'failed'
    dependencies: List[int]  # List of other task IDs to be completed first
    result: Optional[str]
    generated_test_cases: Optional[List[str]]
    self_validation_status: Optional[str]  # e.g., 'Passed', 'Failed'

class ValidationReport(TypedDict):
    status: str  # "Passed" or "Failed"
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
    # Additional fields for HITL
    user_interrupt: Optional[str]
    manager_analysis: Optional[str]

def print_node_entry(node_name: str, state: AgentState):
    """Helper function to print node entry with current state summary"""
    print(f"\n{'='*50}")
    print(f"🤖 ENTERING NODE: {node_name.upper()}")
    print(f"{'='*50}")
    print(f"User Request: {state.get('user_request', 'None')[:100]}...")
    print(f"Current Status: {len(state.get('completed_tasks', []))} completed, {len(state.get('task_plan', []))} planned")
    if state.get('user_interrupt'):
        print(f"🚨 User Interrupt: {state['user_interrupt']}")
    print(f"{'='*50}")

def print_node_exit(node_name: str, action_taken: str, state: AgentState):
    """Helper function to print node exit with action summary"""
    print(f"✅ EXITING NODE: {node_name.upper()}")
    print(f"Action Taken: {action_taken}")
    print(f"Updated State: {len(state.get('completed_tasks', []))} completed, {len(state.get('task_plan', []))} planned")
    print(f"{'='*50}\n")

# Node Implementations
def manager_node(state: AgentState) -> AgentState:
    """
    Entry point and HITL coordinator. Manages clarification and user interrupts.
    """
    print_node_entry("manager_node", state)
    
    # Simulate processing time
    time.sleep(0.5)
    
    # Check for user interrupt (HITL scenario)
    if state.get('user_interrupt'):
        print("🔄 Processing user interrupt...")
        # Simulate impact analysis
        analysis = f"Analyzing impact of: '{state['user_interrupt']}' on current plan"
        print(f"Manager Analysis: {analysis}")
        
        # Update state with analysis
        state['manager_analysis'] = analysis
        state['is_clarification_needed'] = False  # Skip clarification, go to replanning
        
        print_node_exit("manager_node", "User interrupt processed, routing to replanning", state)
        return state
    
    # Initial request processing
    if not state.get('clarified_request'):
        # Simulate clarification logic
        request = state['user_request'].lower()
        needs_clarification = len(request.split()) < 5 or any(word in request for word in ['maybe', 'something', 'anything'])
        
        if needs_clarification:
            state['is_clarification_needed'] = True
            state['clarification_questions'] = [
                "What specific functionality do you need?",
                "Who is the target user for this application?",
                "Do you have any preferred technologies or constraints?"
            ]
            print(f"🤔 Clarification needed. Questions generated: {len(state['clarification_questions'])}")
        else:
            state['is_clarification_needed'] = False
            state['clarified_request'] = state['user_request']
            print(f"✨ Request is clear, proceeding with: {state['clarified_request']}")
    
    action = "Clarification assessment completed"
    print_node_exit("manager_node", action, state)
    return state

def retriever_node(state: AgentState) -> AgentState:
    """
    Queries vector database for relevant context (placeholder implementation).
    """
    print_node_entry("retriever_node", state)
    
    # Simulate retrieval processing
    time.sleep(0.3)
    
    # Placeholder: Simulate retrieving relevant context
    simulated_context = [
        f"Similar project: {state['clarified_request'][:30]}... implementation pattern",
        "Code snippet: FastAPI route structure for REST APIs",
        "Best practice: Database schema design for user management",
        "Template: React component structure for dashboards"
    ]
    
    state['retrieved_context'] = simulated_context
    print(f"📚 Retrieved {len(simulated_context)} relevant context items:")
    for i, context in enumerate(simulated_context, 1):
        print(f"  {i}. {context}")
    
    print_node_exit("retriever_node", f"Retrieved {len(simulated_context)} context items", state)
    return state

def manager_planning_node(state: AgentState) -> AgentState:
    """
    Creates or updates the task plan based on requirements and context.
    """
    print_node_entry("manager_planning_node", state)
    
    # Simulate planning processing
    time.sleep(0.7)
    
    # Handle replanning scenario (user interrupt)
    if state.get('user_interrupt'):
        print("🔄 REPLANNING: Modifying existing plan based on user interrupt")
        print(f"Original plan had {len(state.get('task_plan', []))} tasks")
        
        # Simulate plan modification
        existing_plan = state.get('task_plan', [])
        
        # Cancel some tasks, modify others, add new ones
        for task in existing_plan:
            if task['status'] == 'pending' and 'ui' in task['goal'].lower():
                task['status'] = 'cancelled'
                print(f"  ❌ Cancelled task {task['id']}: {task['goal']}")
        
        # Add new task based on interrupt
        new_task = Task(
            id=len(existing_plan) + 1,
            role='UIWorker',
            goal=f"Implement feature requested in interrupt: {state['user_interrupt']}",
            status='pending',
            dependencies=[],
            result=None,
            generated_test_cases=None,
            self_validation_status=None
        )
        existing_plan.append(new_task)
        print(f"  ➕ Added new task {new_task['id']}: {new_task['goal']}")
        
        state['task_plan'] = existing_plan
        state['user_interrupt'] = None  # Clear the interrupt
        
    else:
        # Initial planning
        print("📋 INITIAL PLANNING: Creating task plan from scratch")
        
        # Simulate task plan generation based on clarified request
        sample_tasks = [
            Task(
                id=1,
                role='ArchitectWorker',
                goal='Design system architecture and data models',
                status='pending',
                dependencies=[],
                result=None,
                generated_test_cases=None,
                self_validation_status=None
            ),
            Task(
                id=2,
                role='BackendWorker',
                goal='Implement API endpoints and business logic',
                status='pending',
                dependencies=[1],
                result=None,
                generated_test_cases=None,
                self_validation_status=None
            ),
            Task(
                id=3,
                role='FrontendWorker',
                goal='Create user interface components',
                status='pending',
                dependencies=[1],
                result=None,
                generated_test_cases=None,
                self_validation_status=None
            ),
            Task(
                id=4,
                role='TestWorker',
                goal='Implement comprehensive test suite',
                status='pending',
                dependencies=[2, 3],
                result=None,
                generated_test_cases=None,
                self_validation_status=None
            )
        ]
        
        state['task_plan'] = sample_tasks
        print(f"📋 Created plan with {len(sample_tasks)} tasks:")
        for task in sample_tasks:
            deps = f" (depends on: {task['dependencies']})" if task['dependencies'] else ""
            print(f"  {task['id']}. {task['role']}: {task['goal']}{deps}")
    
    print_node_exit("manager_planning_node", f"Plan updated with {len(state['task_plan'])} tasks", state)
    return state

def resource_monitor_node(state: AgentState) -> AgentState:
    """
    Estimates costs and monitors resource usage.
    """
    print_node_entry("resource_monitor_node", state)
    
    # Simulate cost calculation
    time.sleep(0.2)
    
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
    
    print_node_exit("resource_monitor_node", f"Cost estimated at ${estimated_cost:.2f}", state)
    return state

def worker_node(state: AgentState) -> AgentState:
    """
    Executes tasks with build-and-validate approach.
    """
    print_node_entry("worker_node", state)
    
    pending_tasks = [task for task in state.get('task_plan', []) if task['status'] == 'pending']
    completed_tasks = state.get('completed_tasks', [])
    
    if not pending_tasks:
        print("ℹ️  No pending tasks to execute")
        print_node_exit("worker_node", "No tasks to process", state)
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
        print_node_exit("worker_node", "Waiting on dependencies", state)
        return state
    
    # Execute the task
    print(f"🔨 Executing Task {executable_task['id']}: {executable_task['goal']}")
    executable_task['status'] = 'in_progress'
    
    # Simulate work
    time.sleep(1)
    
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
    
    # Simulate test execution
    time.sleep(0.5)
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
    
    print_node_exit("worker_node", f"Task {executable_task['id']} completed and validated", state)
    return state

def aggregator_node(state: AgentState) -> AgentState:
    """
    Synthesizes completed work into final deliverable.
    """
    print_node_entry("aggregator_node", state)
    
    completed_tasks = state.get('completed_tasks', [])
    
    if not completed_tasks:
        print("⚠️  No completed tasks to aggregate")
        state['final_deliverable'] = "No work completed yet"
        print_node_exit("aggregator_node", "No tasks to aggregate", state)
        return state
    
    # Simulate aggregation
    time.sleep(0.8)
    
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
    
    print_node_exit("aggregator_node", f"Aggregated {len(completed_tasks)} components", state)
    return state

def tester_node(state: AgentState) -> AgentState:
    """
    Validates final deliverable against user requirements.
    """
    print_node_entry("tester_node", state)
    
    # Simulate comprehensive testing
    time.sleep(1)
    
    final_deliverable = state.get('final_deliverable', '')
    user_request = state.get('clarified_request', '')
    
    print("🔍 FINAL VALIDATION: Testing complete application against requirements")
    print(f"  📋 Original request: {user_request}")
    print(f"  📦 Deliverable length: {len(final_deliverable)} characters")
    
    # Simulate validation logic
    validation_checks = [
        "Functional requirements coverage",
        "Code quality and structure",
        "Security implementation",
        "Performance benchmarks",
        "User experience validation"
    ]
    
    print("  🧪 Running validation checks:")
    for check in validation_checks:
        print(f"    ✅ {check}: PASSED")
        time.sleep(0.1)
    
    # Simulate final validation result
    validation_passed = True  # In real implementation, this would be LLM-determined
    
    if validation_passed:
        validation_report = ValidationReport(
            status="Passed",
            details=f"All validation checks passed. Deliverable meets requirements for: {user_request}"
        )
        print("🎉 FINAL VALIDATION: PASSED")
    else:
        validation_report = ValidationReport(
            status="Failed",
            details="Validation failed - see detailed report for issues"
        )
        print("❌ FINAL VALIDATION: FAILED")
    
    state['validation_report'] = validation_report
    
    print_node_exit("tester_node", f"Validation {validation_report['status']}", state)
    return state

# Route Functions
def route_after_manager(state: AgentState) -> Literal["clarify", "plan", "replan"]:
    """Route logic after manager node"""
    if state.get('user_interrupt'):
        return "replan"
    elif state.get('is_clarification_needed'):
        return "clarify"
    else:
        return "plan"

def route_after_tester(state: AgentState) -> Literal["passed", "failed"]:
    """Route logic after tester node"""
    validation_status = state.get('validation_report', {}).get('status', 'Failed')
    return "passed" if validation_status == "Passed" else "failed"

def check_worker_completion(state: AgentState) -> Literal["continue", "aggregate"]:
    """Check if all tasks are completed"""
    pending_tasks = [task for task in state.get('task_plan', []) 
                    if task['status'] in ['pending', 'in_progress']]
    return "aggregate" if not pending_tasks else "continue"

# Build the Graph
def create_genesis_workflow():
    """Create and configure the Project Genesis workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("manager_node", manager_node)
    workflow.add_node("retriever_node", retriever_node)
    workflow.add_node("manager_planning_node", manager_planning_node)
    workflow.add_node("resource_monitor_node", resource_monitor_node)
    workflow.add_node("worker_node", worker_node)
    workflow.add_node("aggregator_node", aggregator_node)
    workflow.add_node("tester_node", tester_node)
    
    # Set entry point
    workflow.set_entry_point("manager_node")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "manager_node",
        route_after_manager,
        {
            "clarify": END,  # Pause for user input
            "plan": "retriever_node",
            "replan": "manager_planning_node"
        }
    )
    
    # Add standard edges
    workflow.add_edge("retriever_node", "manager_planning_node")
    workflow.add_edge("manager_planning_node", "resource_monitor_node")
    workflow.add_edge("resource_monitor_node", "worker_node")
    
    # Worker loop (continues until all tasks complete)
    workflow.add_conditional_edges(
        "worker_node",
        check_worker_completion,
        {
            "continue": "worker_node",
            "aggregate": "aggregator_node"
        }
    )
    
    workflow.add_edge("aggregator_node", "tester_node")
    
    # Self-correction loop
    workflow.add_conditional_edges(
        "tester_node",
        route_after_tester,
        {
            "passed": END,
            "failed": "manager_planning_node"  # Go back for revision
        }
    )
    
    return workflow.compile()

# Demo Functions
def run_basic_demo():
    """Run a basic workflow demonstration"""
    print("🚀 PROJECT GENESIS PROTOTYPE DEMO")
    print("=" * 60)
    
    app = create_genesis_workflow()
    
    initial_state = AgentState(
        user_request="Create a task management web application with user authentication",
        clarified_request="",
        is_clarification_needed=False,
        clarification_questions=[],
        retrieved_context=[],
        task_plan=[],
        completed_tasks=[],
        final_deliverable="",
        validation_report=ValidationReport(status="", details=""),
        cost_estimate=0.0,
        current_cost=0.0,
        user_interrupt=None,
        manager_analysis=None
    )
    
    # Run the workflow
    result = app.invoke(initial_state)
    
    print("\n" + "=" * 60)
    print("🎉 WORKFLOW COMPLETED!")
    print("=" * 60)
    print(f"Final Status: {result['validation_report']['status']}")
    print(f"Total Cost: ${result['current_cost']:.2f}")
    print(f"Tasks Completed: {len(result['completed_tasks'])}")
    
    return result

def run_hitl_demo():
    """Run a Human-in-the-Loop demonstration"""
    print("🚀 PROJECT GENESIS HITL DEMO")
    print("=" * 60)
    
    app = create_genesis_workflow()
    
    # Start with initial state
    initial_state = AgentState(
        user_request="Create a simple blog website",
        clarified_request="Create a simple blog website with posting and reading capabilities",
        is_clarification_needed=False,
        clarification_questions=[],
        retrieved_context=[],
        task_plan=[],
        completed_tasks=[],
        final_deliverable="",
        validation_report=ValidationReport(status="", details=""),
        cost_estimate=0.0,
        current_cost=0.0,
        user_interrupt="Add a dark mode toggle feature",  # Simulate user interrupt
        manager_analysis=None
    )
    
    # Run the workflow with interrupt
    result = app.invoke(initial_state)
    
    print("\n" + "=" * 60)
    print("🎉 HITL WORKFLOW COMPLETED!")
    print("=" * 60)
    print(f"Final Status: {result['validation_report']['status']}")
    print(f"User Interrupt Handled: ✅")
    print(f"Total Cost: ${result['current_cost']:.2f}")
    
    return result

if __name__ == "__main__":
    print("Choose demo:")
    print("1. Basic Workflow Demo")
    print("2. Human-in-the-Loop Demo")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        run_basic_demo()
    elif choice == "2":
        run_hitl_demo()
    else:
        print("Running basic demo by default...")
        run_basic_demo()