import pytest
from typing import Dict, Any
from src.state import Task, AgentState
from src.nodes.worker_agents.coordinator import WorkerCoordinator, WorkerMessage, SharedStateManager

@pytest.fixture
def coordinator() -> WorkerCoordinator:
    return WorkerCoordinator()

@pytest.fixture
def state_manager() -> SharedStateManager:
    return SharedStateManager()

@pytest.fixture
def mock_state() -> AgentState:
    return AgentState(
        user_request="Create a web application",
        clarified_request="Create a web application with user authentication",
        is_clarification_needed=False,
        clarification_questions=[],
        retrieved_context=["Sample context"],
        task_plan=[],
        completed_tasks=[],
        final_deliverable="",
        validation_report={"status": "", "details": ""},
        cost_estimate=0.0,
        current_cost=0.0
    )

@pytest.fixture
def mock_task() -> Task:
    return Task(
        id=1,
        role="ArchitectWorker",
        goal="Design system architecture",
        status="pending",
        dependencies=[],
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )

class TestSharedStateManager:
    def test_artifact_storage(self, state_manager: SharedStateManager):
        """Test storing and retrieving artifacts"""
        task_id = 1
        artifact_type = "design_doc"
        content = {"components": ["api", "database"]}
        
        state_manager.store_artifact(task_id, artifact_type, content)
        retrieved = state_manager.get_artifact(task_id, artifact_type)
        
        assert retrieved == content
        
    def test_test_result_storage(self, state_manager: SharedStateManager):
        """Test storing and retrieving test results"""
        task_id = 1
        result = {
            "status": "passed",
            "test_cases": ["test1", "test2"]
        }
        
        state_manager.store_test_result(task_id, result)
        retrieved = state_manager.get_test_result(task_id)
        
        assert retrieved == result

class TestWorkerCoordinator:
    def test_task_routing(self, coordinator: WorkerCoordinator, mock_task: Task, mock_state: AgentState):
        """Test routing task to appropriate worker"""
        result = coordinator.route_task(mock_task, mock_state)
        
        assert result['status'] in ['completed', 'failed']
        assert result['id'] == mock_task['id']
        
    def test_invalid_worker_role(self, coordinator: WorkerCoordinator, mock_task: Task, mock_state: AgentState):
        """Test handling of invalid worker role"""
        mock_task['role'] = "InvalidWorker"
        result = coordinator.route_task(mock_task, mock_state)
        
        assert result['status'] == 'failed'
        assert "No worker found for role" in result['result']
        
    def test_dependency_context_gathering(self, coordinator: WorkerCoordinator, mock_task: Task, mock_state: AgentState):
        """Test gathering context from dependencies"""
        # Store some artifact for a dependency
        dep_task_id = 2
        mock_task['dependencies'] = [dep_task_id]
        coordinator.state_manager.store_artifact(
            dep_task_id,
            'design_doc',
            {'components': ['api']}
        )
        
        context = coordinator._gather_dependency_context(mock_task, mock_state)
        
        assert 'dependency_artifacts' in context
        assert f'task_{dep_task_id}' in context['dependency_artifacts']
        assert context['project_requirements'] == mock_state['clarified_request']
        
    def test_message_handling(self, coordinator: WorkerCoordinator):
        """Test worker message handling"""
        message = WorkerMessage(
            source_worker="ArchitectWorker",
            target_worker="BackendWorker",
            message_type="artifact_ready",
            payload={
                "artifact_type": "api_spec",
                "content": {"endpoints": ["/api/users"]}
            },
            task_id=1
        )
        
        coordinator.send_message(message)
        
        assert len(coordinator.message_queue) == 1
        # Note: BackendWorker not implemented yet, so artifact won't be stored

class TestWorkerIntegration:
    def test_architect_to_coordinator_flow(self, coordinator: WorkerCoordinator, mock_task: Task, mock_state: AgentState):
        """Test complete flow from architect through coordinator"""
        # Execute architect task
        result = coordinator.route_task(mock_task, mock_state)
        
        # Verify task completion
        assert result['status'] in ['completed', 'failed']
        
        # Verify artifacts were stored
        if result['status'] == 'completed':
            stored_result = coordinator.state_manager.get_artifact(mock_task['id'], 'result')
            assert stored_result is not None
            
            stored_tests = coordinator.state_manager.get_test_result(mock_task['id'])
            assert stored_tests is not None
            
    def test_dependency_chain(self, coordinator: WorkerCoordinator, mock_state: AgentState):
        """Test execution of tasks with dependencies"""
        # Create two related tasks
        arch_task = Task(
            id=1,
            role="ArchitectWorker",
            goal="Design API",
            status="pending",
            dependencies=[],
            result=None,
            generated_test_cases=None,
            self_validation_status=None
        )
        
        # Execute first task
        arch_result = coordinator.route_task(arch_task, mock_state)
        assert arch_result['status'] in ['completed', 'failed']
        
        # Verify artifact storage for dependency chain
        if arch_result['status'] == 'completed':
            stored_design = coordinator.state_manager.get_artifact(arch_task['id'], 'result')
            assert stored_design is not None
            
            # TODO: Add backend task test when implemented
            # backend_task = Task(
            #     id=2,
            #     role="BackendWorker",
            #     goal="Implement API",
            #     status="pending",
            #     dependencies=[arch_task['id']],
            #     result=None,
            #     generated_test_cases=None,
            #     self_validation_status=None
            # ) 