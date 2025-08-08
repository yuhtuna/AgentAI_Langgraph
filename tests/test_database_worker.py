from src.nodes.worker_agents.database_worker import DatabaseWorker
from src.state import Task
import json

def test_database_worker_build():
    print("\n=== Testing DatabaseWorker Build ===")
    worker = DatabaseWorker()
    task = Task(
        id=1,
        role="DatabaseWorker",
        goal="Design a Convex database for a blogging platform with users, posts, and comments",
        status="pending",
        dependencies=[],
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )
    context = {
        'project_requirements': '''
        Requirements:
        1. Users can create posts and comments
        2. Each post belongs to a user
        3. Each comment belongs to a post and a user
        4. Support for querying posts by user and comments by post
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
    assert 'schema_ts' in build_result['artifacts']
    assert 'migration_ts' in build_result['artifacts']
    assert 'seed_data' in build_result['artifacts']

def test_database_worker_validate():
    print("\n=== Testing DatabaseWorker Validate ===")
    worker = DatabaseWorker()
    task = Task(
        id=1,
        role="DatabaseWorker",
        goal="Design a Convex database for a blogging platform with users, posts, and comments",
        status="pending",
        dependencies=[],
        result=None,
        generated_test_cases=None,
        self_validation_status=None
    )
    build_result = {
        'artifacts': {
            'schema_ts': '// Convex schema TypeScript here',
            'migration_ts': '// Migration script here',
            'seed_data': '{ "users": [], "posts": [], "comments": [] }',
            'indexes': ['userId', 'postId'],
            'validation_notes': 'All tables have primary keys and required indexes.'
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
    test_database_worker_build()
    test_database_worker_validate() 