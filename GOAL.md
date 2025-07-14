# Project Genesis: AI-Powered Application Platform

## Important: Consider to integrate with narbtech!

## 1. Vision & Mission 🎯

**Vision:** To create a premier low-code/no-code platform that allows anyone—from entrepreneurs to enterprise users—to design, build, and deploy custom business logic as a functional application without writing a single line of code.

**Mission for the Dev Team:** Our mission is to engineer a sophisticated multi-agent system using langgraph. This system will form the core of the platform, capable of autonomously planning, developing, testing, and deploying applications based on user requirements in a dynamic, collaborative process.

---

## 2. Core Architecture & Technology Stack 🛠️

The system is architected as a stateful graph where each node represents a specific function performed by an AI agent. langgraph manages the state and orchestrates the complex control flow, including the crucial clarification and self-correction loops.

### Technology Stack

| Component             | Recommendation                 | Rationale                                                                                             |
|-----------------------|--------------------------------|-------------------------------------------------------------------------------------------------------|
| **Backend Language**  | Python                         | Native environment for langgraph and the wider AI ecosystem.                                          |
| **Agent Framework**   | LangGraph                      | Manages the state, control flow, and cyclical logic of our agent team.                                |
| **Web Framework**     | FastAPI                        | High performance and async support, ideal for serving a user-facing application and handling WebSocket communication for HITL.     |
| **LLM**               | Google Gemini                  | Powers the reasoning for all agents, from planning to coding and testing.                                  |
| **Web Search Tool**   | Tavily API                     | Provides agents with access to real-time information for research and fact-checking.                             |
| **Database (Vector)** | ChromaDB, Qdrant, etc.         | Forms the foundation of the agent's knowledge base and long-term memory.                              |
| **Database (Relational)** | PostgreSQL                   | For robust logging of agent states, user sessions, and application metadata.                                         |
| **Deployment**        | Docker, Kubernetes, Google Cloud SDK | For creating a scalable production environment and for enabling the agent to perform autonomous deployments. |

---

## 3. The `langgraph` Implementation 📈

The entire application builder is defined as a single, cohesive `StatefulGraph`.

### The `AgentState`

This is the central data structure for our application-building workflow. It is designed to be dynamic, supporting in-flight modifications to the project plan.

```python
from typing import TypedDict, List, Optional, Dict

class Task(TypedDict):
    id: int
    role: str # e.g., 'CodeWorker', 'TestWriter'
    goal: str
    # NEW: Fields to support dynamic planning and HITL
    status: str # 'pending', 'in_progress', 'completed', 'cancelled', 'failed'
    dependencies: List[int] # List of other task IDs to be completed first
    result: Optional[str]
    generated_test_cases: Optional[List[str]]
    self_validation_status: Optional[str] # e.g., 'Passed', 'Failed'

class ValidationReport(TypedDict):
    status: str # "Passed" or "Failed"
    details: str

class AgentState(TypedDict):
    user_request: str
    clarified_request: str
    is_clarification_needed: bool
    clarification_questions: List[str]
    retrieved_context: List[str]
    task_plan: List[Task]
    completed_tasks: Dict[int, Task]
    final_deliverable: str
    validation_report: ValidationReport
    cost_estimate: float
    current_cost: float
```

### Graph Nodes: The AI Development Team

- **`manager_node` (Entry Point & Human-in-the-Loop):** This agent acts as the central project manager and the primary, continuous interface with the user. See Section 4 for the detailed HITL workflow.
- **`retriever_node`:** Queries the vector database using the `clarified_request` to fetch relevant context, code snippets, and past solutions.
- **`manager_planning_node`:** Decomposes the request into a detailed `task_plan`. This node is re-triggered by the `manager_node` whenever the user modifies the project, taking the new context to create a revised plan.
- **`resource_monitor_node`:** Provides a `cost_estimate` based on the plan and tracks real-time API usage.
- **`worker_node`:** A pool of specialized agents that perform the core development tasks. Each worker now follows a rigorous two-step "build-and-validate" process:
    - **Build:** Executes its assigned task based on the goal.
    - **Self-Validate (Intensive Testing):** After building, the worker generates its own specific unit or integration test cases for the component it just created. It then runs these tests. Only if all self-generated tests pass does it update its `self_validation_status` to "Passed" and submit the result.
- **`aggregator_node`:** Synthesizes the work from all successfully self-validated workers in `completed_tasks` into a `final_deliverable`.
- **`tester_node`:** Validates the fully integrated `final_deliverable` against the user's overall requirements and provides the final `validation_report`, enabling the high-level self-correction loop.

### Graph Edges: The Workflow Logic

The graph's control flow is defined by a series of standard and conditional edges.

**Entry Point:**
```python
workflow.set_entry_point("manager_node")
```

**Clarification & HITL Loop (Conditional Edge):** After the manager node runs, it decides the next step.
```python
workflow.add_conditional_edges(
    "manager_node",
    # This function checks state for clarification needs or user interrupts
    route_after_manager,
    {
        "clarify": END, # Pause to get more info from user
        "plan": "retriever_node", # Proceed with planning
        "replan": "manager_planning_node" # User interrupted, go straight to replanning
    }
)
```

**Main Execution Path (Standard Edges):**
```python
workflow.add_edge('retriever_node', 'manager_planning_node')
workflow.add_edge('manager_planning_node', 'resource_monitor_node')
workflow.add_edge('resource_monitor_node', 'worker_node')
workflow.add_edge('worker_node', 'aggregator_node')
workflow.add_edge('aggregator_node', 'tester_node')
```

**Self-Correction Loop (Conditional Edge):**
```python
workflow.add_conditional_edges(
    "tester_node",
    lambda state: state["validation_report"]["status"],
    {
        "Passed": END,
        "Failed": "manager_planning_node" # Re-route for revision
    }
)
```

---

## 4. Human-in-the-Loop (HITL) & Dynamic Planning

To create a truly collaborative platform, the system must handle user interruptions and mid-stream changes gracefully. This is achieved via a "smart pause" and dynamic re-planning workflow orchestrated by the `manager_node`.

### The HITL Workflow

- **User Interrupt:** The user sends a new message during the project (e.g., "add a dark mode toggle"). The FastAPI backend signals the langgraph execution to pause.
- **Manager-Led Impact Analysis:** The `manager_node` is invoked with the current `AgentState` and the new user request. It uses an LLM to perform an impact analysis on the `task_plan`.
- **Intelligent Plan Modification:** Based on the analysis, the manager updates the `task_plan` in the state by performing a series of actions:
    - **CANCEL:** Sets the status of obsolete pending tasks to 'cancelled'. The `worker_node` logic will ignore these.
    - **MODIFY:** Updates the goal of a pending task. If a task is already `in_progress`, it may be cancelled and a new, modified task created to ensure consistency.
    - **ADD:** Appends new tasks to the plan with appropriate dependencies.
- **Workflow Resume:** The langgraph execution is resumed with the updated `AgentState`. Unaffected workers continue their tasks without interruption, while others pick up the revised plan.

### Performance & Latency Considerations

- **Latency:** This process introduces a brief, controlled pause for re-planning but dramatically reduces total project delivery time by avoiding wasted work on incorrect features.
- **Performance:** The small, one-time cost of the manager's impact analysis is far more efficient than running an entire incorrect workflow and starting over.
- **Accuracy:** This iterative, feedback-driven approach ensures the final product aligns perfectly with the user's evolving vision.

---

## 5. Knowledge Base & Autonomous Learning

The system's intelligence is amplified by a Vector Database that serves as its long-term memory (Retrieval-Augmented Generation - RAG).

**Purpose:** To create a persistent knowledge base of successful solutions, code patterns, and documentation, allowing the system to improve its efficiency and consistency with every application it builds.

**Implementation:**
- **Retrieval:** The `retriever_node` queries the database at the start of a job to inform the planning process.
- **Learning:** After a job is successfully completed and validated, the final deliverable and its components are processed and saved back into the vector database, creating a virtuous learning cycle.

---

## 6. Automated Deployment Task

A key capability of the platform is the agent's ability to deploy the applications it builds.

**Objective:** Integrate the Google Cloud SDK into the agent's available tools.

**Functionality:** This will empower the `worker_node` with a new set of capabilities, allowing it to perform actions such as:
- Provisioning cloud resources (e.g., virtual machines, storage buckets).
- Deploying applications using services like Google App Engine or Cloud Run.
- Managing configurations and monitoring deployed applications.

This task is the final step in realizing the full vision of a platform where a user request can be taken all the way from an idea to a live, deployed application.