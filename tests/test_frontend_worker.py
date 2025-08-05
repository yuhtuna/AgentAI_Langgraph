from src.nodes.worker_agents.frontend_worker import FrontendWorker
from src.state import Task
import json

def test_frontend_worker_build():
    print("\n=== Testing FrontendWorker Build ===")
    worker = FrontendWorker()
    task = Task(
        id=1,
        role="FrontendWorker",
        goal="Build a web dashboard for a blogging platform with user login, post creation, and comment display",
        status="pending",
        dependencies=[],
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )
    context = {
        'project_requirements': '''
        Requirements:
        1. Web dashboard for a blogging platform
        2. Users can log in and create posts
        3. Posts are displayed in a feed
        4. Each post can have comments displayed
        5. Use Next.js and CSS modules
        '''
    }
    print("\n--- Task ---")
    print(json.dumps(task, indent=2))
    print("\n--- Context ---")
    print(json.dumps(context, indent=2))
    print("\n--- Running build() ---")
    build_result = worker.build(task, context)
    print("\n--- Build Result ---")
    print(json.dumps(build_result, indent=2))
    if 'error' in build_result:
        print("\n[ERROR] Build failed:", build_result['error'])
        print("[ERROR] Raw LLM response:", build_result['artifacts'].get('raw_response'))
        return
    if 'clarification_questions' in build_result and build_result['clarification_questions']:
        print("\n[CLARIFICATION NEEDED]", build_result['clarification_questions'])
        return
    print("\n--- Build Artifacts ---")
    for k, v in build_result['artifacts'].items():
        print(f"\n[{k}]\n{v}")
    assert 'files' in build_result['artifacts']
    assert 'folder_structure' in build_result['artifacts']
    assert 'dependencies' in build_result['artifacts']

def test_frontend_worker_validate():
    print("\n=== Testing FrontendWorker Validate ===")
    worker = FrontendWorker()
    task = Task(
        id=1,
        role="FrontendWorker",
        goal="Build a web dashboard for a blogging platform with user login, post creation, and comment display",
        status="pending",
        dependencies=[],
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )
    build_result = {
        'artifacts': {
            'files': [
                {'filename': 'pages/index.tsx', 'content': '// Next.js page code'},
                {'filename': 'components/Header.tsx', 'content': '// Header component code'},
                {'filename': 'styles/global.css', 'content': '/* CSS styles */'},
                {'filename': 'tests/App.test.tsx', 'content': '// Jest test code'}
            ],
            'folder_structure': ['pages/', 'components/', 'styles/', 'tests/'],
            'dependencies': ['next', 'react', 'react-dom', 'jest'],
            'readme': 'This is a minimal Next.js blogging dashboard.'
        }
    }
    print("\n--- Validating the following build result ---")
    print(json.dumps(build_result, indent=2))
    print("\n--- Running validate() ---")
    validation_result = worker.validate(task, build_result)
    print("\n--- Validation Result ---")
    print(json.dumps(validation_result, indent=2))
    assert 'status' in validation_result
    assert 'checks' in validation_result
    print(f"\nValidation status: {validation_result['status']}")

if __name__ == "__main__":
    test_frontend_worker_build()
    test_frontend_worker_validate() 