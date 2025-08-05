import pytest
from typing import Dict, Any
from src.state import Task
from src.nodes.worker_agents.base_worker import BaseWorker
from src.nodes.worker_agents.architect_worker import ArchitectWorker

# Mock worker for testing base functionality
class MockWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.role = "MockWorker"
        
    def build(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'result': f"Built task {task['id']}",
            'artifacts': {'mock_artifact': 'test'}
        }
        
    def validate(self, task: Task, build_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'Passed',
            'test_cases': ['mock_test_1', 'mock_test_2'],
            'error': None
        }

# Fixtures
@pytest.fixture
def mock_task() -> Task:
    return Task(
        id=1,
        role="MockWorker",
        goal="Test task",
        status="pending",
        dependencies=[],
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )

@pytest.fixture
def mock_context() -> Dict[str, Any]:
    return {
        'project_requirements': 'Test requirements',
        'existing_code': 'Test code'
    }

@pytest.fixture
def mock_worker() -> MockWorker:
    return MockWorker()

@pytest.fixture
def architect_worker() -> ArchitectWorker:
    return ArchitectWorker()

# Base Worker Tests
class TestBaseWorker:
    def test_execute_task_success(self, mock_worker: MockWorker, mock_task: Task, mock_context: Dict[str, Any]):
        """Test successful task execution flow"""
        result = mock_worker.execute_task(mock_task, mock_context)
        
        assert result['status'] == 'completed'
        assert result['self_validation_status'] == 'Passed'
        assert result['result'] == f"Built task {mock_task['id']}"
        assert len(result['generated_test_cases']) == 2
        
    def test_execute_task_error_handling(self, mock_worker: MockWorker, mock_task: Task):
        """Test error handling during task execution"""
        # Simulate error by passing invalid context
        result = mock_worker.execute_task(mock_task, None)
        
        assert result['status'] == 'failed'
        assert result['self_validation_status'] == 'Failed'
        assert 'Error' in result['result']
        
    def test_get_relevant_code_context(self, mock_worker: MockWorker, mock_task: Task):
        """Test context gathering functionality"""
        context = mock_worker.get_relevant_code_context(mock_task)
        
        assert context['task_id'] == mock_task['id']
        assert context['task_goal'] == mock_task['goal']
        assert context['dependencies'] == mock_task['dependencies']

# Architect Worker Tests
class TestArchitectWorker:
    def test_build_phase(self, architect_worker: ArchitectWorker, mock_task: Task, mock_context: Dict[str, Any]):
        """Test architecture design generation"""
        build_result = architect_worker.build(mock_task, mock_context)
        
        assert 'result' in build_result
        assert 'artifacts' in build_result
        assert 'architecture_doc' in build_result['artifacts']
        
    def test_validation_phase(self, architect_worker: ArchitectWorker, mock_task: Task):
        """Test architecture validation"""
        build_result = {
            'result': '''{
                "architecture_design": {
                    "components": ["api", "database"],
                    "data_models": ["user", "product"],
                    "api_interfaces": ["/api/v1/users"],
                    "tech_stack": {"backend": "FastAPI"}
                }
            }''',
            'artifacts': {'architecture_doc': 'test'}
        }
        
        validation_result = architect_worker.validate(mock_task, build_result)
        
        assert 'status' in validation_result
        assert 'test_cases' in validation_result
        assert isinstance(validation_result['test_cases'], list)
        
    def test_error_handling(self, architect_worker: ArchitectWorker, mock_task: Task):
        """Test error handling in architect worker"""
        # Test with invalid context
        build_result = architect_worker.build(mock_task, None)
        assert 'error' in build_result
        
        # Test with invalid build result
        validation_result = architect_worker.validate(mock_task, {'result': None})
        assert validation_result['status'] == 'Failed'
        assert 'error' in validation_result

# Integration Tests
class TestWorkerIntegration:
    def test_architect_to_backend_handoff(self, architect_worker: ArchitectWorker, mock_task: Task, mock_context: Dict[str, Any]):
        """Test handoff of architecture artifacts to backend worker"""
        # Execute architect task
        arch_task = mock_task.copy()
        arch_task['role'] = 'ArchitectWorker'
        arch_task['goal'] = 'Design API architecture'
        
        completed_arch_task = architect_worker.execute_task(arch_task, mock_context)
        
        # Verify artifacts for backend
        assert completed_arch_task['status'] == 'completed'
        assert completed_arch_task['result'] is not None
        
        # TODO: Add backend worker test when implemented
        # backend_task = Task(
        #     id=2,
        #     role='BackendWorker',
        #     goal='Implement API',
        #     status='pending',
        #     dependencies=[arch_task['id']],
        #     result=None,
        #     generated_test_cases=None,
        #     self_validation_status=None
        # ) 