from typing import Dict, Any
from src.state import Task
from .base_worker import BaseWorker
from langchain.prompts import PromptTemplate
from src.config import llm
import json

CONVEX_SCHEMA_PROMPT = """
You are a database expert specializing in Convex (https://docs.convex.dev/).

Current Task: {task_goal}

Project Requirements:
{requirements}

Instructions:
1. Analyze the requirements and clarify any ambiguities.
2. Design a Convex database schema (TypeScript) using defineSchema, defineTable, and appropriate field types and indexes.
3. Output a migration script (TypeScript) for schema creation.
4. Propose seed data as a TypeScript/JSON object.
5. List any indexes and validation notes.
6. If requirements are unclear, ask clarifying questions and do not generate code.

Respond with a valid JSON object in this format:
{{
  "clarification_questions": ["..."],
  "schema_ts": "// Convex schema as a TypeScript string",
  "migration_ts": "// Migration script as a TypeScript string",
  "seed_data": "// Seed data as a TypeScript/JSON string",
  "indexes": ["..."],
  "validation_notes": "// Any validation or constraint notes"
}}
"""

class DatabaseWorker(BaseWorker):
    """
    Specialized worker for Convex database modeling and implementation.
    """
    def __init__(self):
        super().__init__()
        self.role = "DatabaseWorker"
        self.capabilities = [
            "Convex schema generation",
            "Migration script generation",
            "Seed data creation",
            "Index optimization",
            "Data validation"
        ]
        self.schema_prompt = PromptTemplate(
            template=CONVEX_SCHEMA_PROMPT,
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
            db_context = self.get_relevant_code_context(task, context or {})
            print("\n[DatabaseWorker] Task Goal:", task['goal'])
            print("[DatabaseWorker] Requirements:", db_context['requirements'])
            response = llm.invoke(
                self.schema_prompt.format(
                    task_goal=task['goal'],
                    requirements=db_context['requirements']
                )
            )
            print("\n[DatabaseWorker] Raw LLM response:", response.content)
            json_str = self._extract_json_from_llm_response(response.content)
            try:
                db_result = json.loads(json_str)
            except Exception as e:
                print("[DatabaseWorker] Error parsing JSON:", e)
                return {
                    'result': f"Error parsing JSON: {str(e)}",
                    'error': str(e),
                    'artifacts': {
                        'error_details': str(e),
                        'raw_response': json_str
                    }
                }
            if 'clarification_questions' in db_result and db_result['clarification_questions']:
                print("[DatabaseWorker] Clarification needed:", db_result['clarification_questions'])
                return {
                    'result': None,
                    'clarification_questions': db_result['clarification_questions'],
                    'artifacts': {}
                }
            # Check for Convex schema keys
            for key in ['schema_ts', 'migration_ts', 'seed_data']:
                if key not in db_result:
                    print(f"[DatabaseWorker] '{key}' key missing in LLM response.")
                    return {
                        'result': f"Error: '{key}' key missing in LLM response.",
                        'error': f"'{key}' key missing",
                        'artifacts': {
                            'raw_response': json_str
                        }
                    }
            return {
                'result': db_result['schema_ts'],
                'artifacts': {
                    'schema_ts': db_result['schema_ts'],
                    'migration_ts': db_result['migration_ts'],
                    'seed_data': db_result['seed_data'],
                    'indexes': db_result.get('indexes', []),
                    'validation_notes': db_result.get('validation_notes', '')
                }
            }
        except Exception as e:
            print("[DatabaseWorker] Error in build phase:", e)
            return {
                'result': f"Error in build phase: {str(e)}",
                'error': str(e),
                'artifacts': {
                    'error_details': str(e),
                    'raw_response': response.content if response else 'No response available'
                }
            }

    def validate(self, task: Task, build_result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            schema_ts = build_result['artifacts'].get('schema_ts', '')
            migration_ts = build_result['artifacts'].get('migration_ts', '')
            seed_data = build_result['artifacts'].get('seed_data', '')
            indexes = build_result['artifacts'].get('indexes', [])
            notes = build_result['artifacts'].get('validation_notes', '')
            validation_results = []
            if not schema_ts or not schema_ts.strip():
                validation_results.append({
                    'criterion': 'schema_ts',
                    'status': 'failed',
                    'details': 'No schema TypeScript generated.'
                })
            else:
                validation_results.append({
                    'criterion': 'schema_ts',
                    'status': 'passed',
                    'details': 'Schema TypeScript present.'
                })
            if not migration_ts or not migration_ts.strip():
                validation_results.append({
                    'criterion': 'migration_ts',
                    'status': 'failed',
                    'details': 'No migration script generated.'
                })
            else:
                validation_results.append({
                    'criterion': 'migration_ts',
                    'status': 'passed',
                    'details': 'Migration script present.'
                })
            status = 'Passed' if all(r['status'] == 'passed' for r in validation_results) else 'Failed'
            return {
                'status': status,
                'checks': validation_results,
                'notes': notes,
                'error': None if status == 'Passed' else 'Some validation checks failed'
            }
        except Exception as e:
            print("[DatabaseWorker] Error in validation phase:", e)
            return {
                'status': 'Failed',
                'error': str(e),
                'checks': []
            } 