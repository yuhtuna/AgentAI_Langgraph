from typing import Dict, Any
from src.state import Task
from .base_worker import BaseWorker
from langchain.prompts import PromptTemplate
from src.config import llm
import json

FRONTEND_PROMPT = """
You are a frontend engineer specializing in Next.js (for web) and React Native (for mobile).

Current Task: {task_goal}

Project Requirements:
{requirements}

Instructions:
1. If the requirements are unclear, ask clarifying questions and do not generate code.
2. If the requirements mention a web dashboard, assume Next.js. If they mention a mobile app, assume React Native. If in doubt, default to Next.js.
3. If the requirements specify a web app, generate a minimal working Next.js frontend (React, TypeScript) with navigation, sample pages, and CSS style files.
4. If the requirements specify a mobile app, generate a minimal working React Native frontend (TypeScript) with navigation, sample screens, and style files.
5. For both, include at least one Jest/React test file.
6. Output all code as strings, with clear file names (e.g., 'pages/index.tsx', 'components/Header.tsx', 'App.tsx', 'styles/global.css', 'tests/App.test.tsx', etc.).
7. Suggest a folder structure and list any required dependencies.
8. Provide a README or usage instructions.

Respond with a valid JSON object in this format:
{
  "clarification_questions": ["..."],
  "files": [
    {"filename": "pages/index.tsx", "content": "// Next.js page code here"},
    {"filename": "components/Header.tsx", "content": "// Header component code here"},
    {"filename": "styles/global.css", "content": "/* CSS styles here */"},
    {"filename": "tests/App.test.tsx", "content": "// Jest test code here"},
    ...
  ],
  "folder_structure": [
    "pages/",
    "components/",
    "styles/",
    "tests/",
    ...
  ],
  "dependencies": ["next", "react", "react-dom", "jest", ...],
  "readme": "// README or usage instructions"
}
"""

class FrontendWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.role = "FrontendWorker"
        self.capabilities = [
            "Next.js frontend generation",
            "React Native frontend generation",
            "Component design",
            "CSS styling",
            "Jest/React test generation",
            "Folder structure suggestion",
            "Dependency listing"
        ]
        self.frontend_prompt = PromptTemplate(
            template=FRONTEND_PROMPT,
            input_variables=["task_goal", "requirements"]
        )

    def get_relevant_code_context(self, task: Task, state_context: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_relevant_code_context(task)
        requirements = state_context.get('clarified_request', '')
        if not requirements and 'project_requirements' in state_context:
            requirements = state_context['project_requirements']
        return {
            'requirements': requirements or task['goal']
        }

    def _extract_json_from_llm_response(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        elif content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()
        return content

    def build(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        response = None
        try:
            fe_context = self.get_relevant_code_context(task, context or {})
            print("\n[FrontendWorker] Task Goal:", task['goal'])
            print("[FrontendWorker] Requirements:", fe_context['requirements'])
            response = llm.invoke(
                self.frontend_prompt.format(
                    task_goal=task['goal'],
                    requirements=fe_context['requirements']
                )
            )
            # Always print the raw LLM response, even if parsing fails
            print("\n[FrontendWorker] Raw LLM response:", getattr(response, 'content', response))
            json_str = self._extract_json_from_llm_response(getattr(response, 'content', ''))
            try:
                fe_result = json.loads(json_str)
            except Exception as e:
                print("[FrontendWorker] Error parsing JSON:", e)
                return {
                    'result': f"Error parsing JSON: {str(e)}",
                    'error': str(e),
                    'artifacts': {
                        'error_details': str(e),
                        'raw_response': getattr(response, 'content', response)
                    }
                }
            if 'clarification_questions' in fe_result and fe_result['clarification_questions']:
                print("[FrontendWorker] Clarification needed:", fe_result['clarification_questions'])
                return {
                    'result': None,
                    'clarification_questions': fe_result['clarification_questions'],
                    'artifacts': {}
                }
            # Check for required keys
            for key in ['files', 'folder_structure', 'dependencies']:
                if key not in fe_result:
                    print(f"[FrontendWorker] '{key}' key missing in LLM response.")
                    return {
                        'result': f"Error: '{key}' key missing in LLM response.",
                        'error': f"'{key}' key missing",
                        'artifacts': {
                            'raw_response': getattr(response, 'content', response)
                        }
                    }
            return {
                'result': fe_result['files'],
                'artifacts': {
                    'files': fe_result['files'],
                    'folder_structure': fe_result['folder_structure'],
                    'dependencies': fe_result['dependencies'],
                    'readme': fe_result.get('readme', '')
                }
            }
        except Exception as e:
            print("[FrontendWorker] Error in build phase:", e)
            return {
                'result': f"Error in build phase: {str(e)}",
                'error': str(e),
                'artifacts': {
                    'error_details': str(e),
                    'raw_response': getattr(response, 'content', response)
                }
            }

    def validate(self, task: Task, build_result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            files = build_result['artifacts'].get('files', [])
            folder_structure = build_result['artifacts'].get('folder_structure', [])
            dependencies = build_result['artifacts'].get('dependencies', [])
            notes = build_result['artifacts'].get('readme', '')
            validation_results = []
            if not files or not isinstance(files, list):
                validation_results.append({
                    'criterion': 'files',
                    'status': 'failed',
                    'details': 'No frontend files generated.'
                })
            else:
                validation_results.append({
                    'criterion': 'files',
                    'status': 'passed',
                    'details': f'{len(files)} files generated.'
                })
            if not folder_structure or not isinstance(folder_structure, list):
                validation_results.append({
                    'criterion': 'folder_structure',
                    'status': 'failed',
                    'details': 'No folder structure provided.'
                })
            else:
                validation_results.append({
                    'criterion': 'folder_structure',
                    'status': 'passed',
                    'details': 'Folder structure present.'
                })
            if not dependencies or not isinstance(dependencies, list):
                validation_results.append({
                    'criterion': 'dependencies',
                    'status': 'failed',
                    'details': 'No dependencies listed.'
                })
            else:
                validation_results.append({
                    'criterion': 'dependencies',
                    'status': 'passed',
                    'details': f'{len(dependencies)} dependencies listed.'
                })
            # Check for at least one test file
            has_test = any('test' in f['filename'].lower() for f in files if 'filename' in f)
            if not has_test:
                validation_results.append({
                    'criterion': 'jest_tests',
                    'status': 'failed',
                    'details': 'No Jest/React test file generated.'
                })
            else:
                validation_results.append({
                    'criterion': 'jest_tests',
                    'status': 'passed',
                    'details': 'At least one Jest/React test file present.'
                })
            status = 'Passed' if all(r['status'] == 'passed' for r in validation_results) else 'Failed'
            return {
                'status': status,
                'checks': validation_results,
                'notes': notes,
                'error': None if status == 'Passed' else 'Some validation checks failed'
            }
        except Exception as e:
            print("[FrontendWorker] Error in validation phase:", e)
            return {
                'status': 'Failed',
                'error': str(e),
                'checks': []
            } 