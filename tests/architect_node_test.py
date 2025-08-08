from src.nodes.worker_agents.architect_worker import ArchitectWorker
from src.state import Task
import json

def test_architect_node():
    print("\n=== Testing Architect Worker ===")
    
    # Initialize worker
    print("\n1. Creating Architect Worker...")
    architect_worker = ArchitectWorker()
    
    # Create task
    print("\n2. Creating test task...")
    task = Task(
        id=1,
        role="ArchitectWorker",
        goal="Design a REST API for a user management system with authentication",
        status="pending",
        dependencies=[], 
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )
    print(f"Task details: {json.dumps(task, indent=2)}")
    
    # Add context
    print("\n3. Setting up context...")
    context = {
        'project_requirements': '''
        Requirements:
        1. User registration and login
        2. JWT-based authentication
        3. Role-based access control
        4. Password reset functionality
        '''
    }
    print(f"Context: {json.dumps(context, indent=2)}")
    
    # Execute build
    print("\n4. Executing build phase...")
    build_result = architect_worker.build(task, context)
    
    # Print results
    print("\n5. Build Results:")
    print(f"Raw result: {json.dumps(build_result, indent=2)}")
    
    if 'error' in build_result:
        print(f"\nError occurred: {build_result['error']}")
    else:
        try:
            # Parse and display the architecture design
            design = json.loads(build_result['result'])
            print("\n6. Parsed Architecture Design:")
            print(f"Components: {json.dumps(design['architecture_design']['components'], indent=2)}")
            print(f"API Interfaces: {json.dumps(design['architecture_design']['api_interfaces'], indent=2)}")
            print(f"Data Models: {json.dumps(design['architecture_design']['data_models'], indent=2)}")
            print(f"\nRationale: {design['rationale']}")
            
            # Display diagrams if present
            if 'diagrams' in design:
                print("\n7. System Diagrams:")
                print("System Diagram:")
                print(design['diagrams']['system'])
                print("\nData Flow Diagram:")
                print(design['diagrams']['data_flow'])
                
        except json.JSONDecodeError as e:
            print(f"\nFailed to parse architecture design: {e}")
            print(f"Raw content: {build_result['result']}")

def test_architect_validate():
    print("\n=== Testing Architect Worker Validation ===")
    architect_worker = ArchitectWorker()
    task = Task(
        id=1,
        role="ArchitectWorker",
        goal="Design a REST API for a user management system with authentication",
        status="pending",
        dependencies=[],
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )
    # Use a realistic architecture design result
    build_result = {
        'result': json.dumps({
            "architecture_design": {
                "components": ["API Gateway", "Authentication Service", "User Service", "Database"],
                "data_models": [
                    {"name": "User", "attributes": {"id": {"type": "UUID", "primary_key": True}}},
                    {"name": "Role", "attributes": {"id": {"type": "integer", "primary_key": True}}}
                ],
                "api_interfaces": [
                    {"endpoint": "/register", "method": "POST", "description": "Registers a new user"},
                    {"endpoint": "/login", "method": "POST", "description": "Logs in an existing user and returns a JWT"}
                ],
                "tech_stack": {"language": "Python", "framework": "FastAPI", "database": "PostgreSQL"}
            },
            "diagrams": {
                "system": "graph LR\n  API Gateway --> Authentication Service\n  Authentication Service --> User Service\n  User Service --> Database",
                "data_flow": "graph LR\n  Client -- Request --> API Gateway\n  API Gateway -- Request --> Authentication Service"
            },
            "rationale": "This design uses a microservices architecture with separate services for authentication and user management."
        })
    }
    print("\nValidating the following build result:")
    print(json.dumps(build_result, indent=2))
    validation_result = architect_worker.validate(task, build_result)
    print("\nValidation Result:")
    print(json.dumps(validation_result, indent=2))
    assert 'status' in validation_result
    assert 'test_cases' in validation_result
    assert 'checks' in validation_result
    print(f"\nValidation status: {validation_result['status']}")

if __name__ == "__main__":
    test_architect_node()
    test_architect_validate()