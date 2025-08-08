from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from src.state import Task
from src.config import llm
from langchain.prompts import PromptTemplate
import subprocess
import tempfile
import os
import json

class TestResult:
    def __init__(self, passed: bool, message: str, details: Dict[str, Any] = None):
        self.passed = passed
        self.message = message
        self.details = details or {}

class BaseWorker(ABC):
    """
    Base class for all worker agents. Provides common functionality and required interface.
    """
    
    def __init__(self):
        self.role: str = "BaseWorker"
        self.capabilities: List[str] = []
        self.tools_available: List[str] = []
        self.test_framework: str = "pytest"  # Default test framework
        
    @abstractmethod
    def build(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the build phase of the task.
        
        Args:
            task: The task to execute
            context: Additional context including codebase state, requirements, etc.
            
        Returns:
            Dict containing build results including any generated code/artifacts
        """
        pass
        
    @abstractmethod
    def validate(self, task: Task, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the self-validation phase for the task.
        
        Args:
            task: The completed task
            build_result: Results from the build phase
            
        Returns:
            Dict containing validation results including test cases and execution results
        """
        pass

    def generate_tests(self, task: Task, build_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test cases for the task result.
        
        Args:
            task: The task being tested
            build_result: The result to test
            
        Returns:
            List of test cases with code and metadata
        """
        try:
            # Create prompt for test generation
            test_prompt = PromptTemplate(
                template="""Generate comprehensive test cases for the following component:

Task Goal: {goal}
Component Role: {role}
Component Result: {result}

Requirements:
1. Generate both unit and integration tests
2. Include edge cases and error scenarios
3. Follow {test_framework} conventions
4. Tests should be executable

For each test, provide:
1. Test name and description
2. Test code
3. Expected results
4. Required setup/teardown

Response Format:
{
    "tests": [
        {
            "name": "test_name",
            "description": "what is being tested",
            "code": "actual test code",
            "expected_result": "what should happen",
            "setup": "setup code if needed",
            "teardown": "cleanup code if needed"
        }
    ]
}""",
                input_variables=["goal", "role", "result", "test_framework"]
            )
            
            # Generate tests using LLM
            response = llm.invoke(
                test_prompt.format(
                    goal=task['goal'],
                    role=task['role'],
                    result=str(build_result.get('result', '')),
                    test_framework=self.test_framework
                )
            )
            
            # Parse and validate test cases
            test_cases = json.loads(response.content)['tests']
            return test_cases
            
        except Exception as e:
            print(f"Error generating tests: {str(e)}")
            return []

    def execute_tests(self, test_cases: List[Dict[str, Any]], build_result: Dict[str, Any]) -> List[TestResult]:
        """
        Execute the generated test cases.
        
        Args:
            test_cases: List of test cases to execute
            build_result: The build result being tested
            
        Returns:
            List of test results
        """
        results = []
        
        try:
            # Create temporary test directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write test files
                test_file_path = os.path.join(temp_dir, "test_component.py")
                with open(test_file_path, "w") as f:
                    # Write imports and setup
                    f.write("import pytest\n\n")
                    
                    # Write any necessary setup code
                    for test in test_cases:
                        if test.get('setup'):
                            f.write(f"{test['setup']}\n\n")
                    
                    # Write test cases
                    for test in test_cases:
                        f.write(f"def {test['name']}():\n")
                        f.write(f"    \"\"\"{test['description']}\"\"\"\n")
                        f.write(f"    {test['code']}\n\n")
                
                # Run tests
                try:
                    result = subprocess.run(
                        ["pytest", test_file_path, "-v"],
                        capture_output=True,
                        text=True
                    )
                    
                    # Parse test results
                    for test in test_cases:
                        if test['name'] in result.stdout:
                            passed = "PASSED" in result.stdout
                            results.append(TestResult(
                                passed=passed,
                                message=f"Test {test['name']} {'passed' if passed else 'failed'}",
                                details={
                                    'name': test['name'],
                                    'description': test['description'],
                                    'output': result.stdout
                                }
                            ))
                        
                except subprocess.SubprocessError as e:
                    results.append(TestResult(
                        passed=False,
                        message=f"Error running tests: {str(e)}",
                        details={'error': str(e)}
                    ))
                    
                # Run teardown if needed
                for test in test_cases:
                    if test.get('teardown'):
                        exec(test['teardown'])
                        
        except Exception as e:
            results.append(TestResult(
                passed=False,
                message=f"Error in test execution framework: {str(e)}",
                details={'error': str(e)}
            ))
            
        return results
        
    def execute_task(self, task: Task, context: Dict[str, Any]) -> Task:
        """
        Main execution flow for a task.
        
        Args:
            task: The task to execute
            context: Additional context for task execution
            
        Returns:
            Updated task with results and validation status
        """
        try:
            print(f"🔨 {self.role} executing task {task['id']}: {task['goal']}")
            
            # Build phase
            print(f"  🏗️  BUILD PHASE: Starting...")
            build_result = self.build(task, context)
            task['result'] = build_result.get('result')
            
            # Generate test cases
            print(f"  🧪 VALIDATION PHASE: Generating tests...")
            test_cases = self.generate_tests(task, build_result)
            
            # Execute tests
            print(f"  🧪 VALIDATION PHASE: Running {len(test_cases)} tests...")
            test_results = self.execute_tests(test_cases, build_result)
            
            # Store test results
            task['generated_test_cases'] = [
                {
                    'name': test['name'],
                    'description': test['description'],
                    'code': test['code']
                }
                for test in test_cases
            ]
            
            # Update validation status
            all_passed = all(result.passed for result in test_results)
            task['self_validation_status'] = 'Passed' if all_passed else 'Failed'
            
            if all_passed:
                task['status'] = 'completed'
                print(f"  ✅ Task {task['id']} completed and validated successfully")
            else:
                task['status'] = 'failed'
                failed_tests = [r.message for r in test_results if not r.passed]
                print(f"  ❌ Task {task['id']} failed validation:")
                for msg in failed_tests:
                    print(f"    - {msg}")
                
        except Exception as e:
            print(f"  ❌ Error executing task {task['id']}: {str(e)}")
            task['status'] = 'failed'
            task['self_validation_status'] = 'Failed'
            task['result'] = f"Error: {str(e)}"
            
        return task
        
    def get_relevant_code_context(self, task: Task) -> Dict[str, Any]:
        """
        Helper method to gather relevant code context for a task.
        Should be overridden by specialized workers that need custom context.
        
        Args:
            task: The task being executed
            
        Returns:
            Dict containing relevant code snippets, files, etc.
        """
        return {
            'task_id': task['id'],
            'task_goal': task['goal'],
            'dependencies': task['dependencies']
        }
        
    def format_code_for_review(self, code: str) -> str:
        """
        Helper method to format code for LLM review.
        
        Args:
            code: The code to format
            
        Returns:
            Formatted code string
        """
        return f"```\n{code}\n```" 