from typing import Dict, Any
from src.state import Task
from .base_worker import BaseWorker
from langchain.prompts import PromptTemplate
from src.config import llm
import json

ARCHITECTURE_DESIGN_TEMPLATE = """You are an expert software architect tasked with designing system architecture and data models.

Current Task: {task_goal}

Project Requirements:
{requirements}

Instructions:
1. Analyze the requirements
2. Design the system architecture including:
   - Component breakdown
   - Data flow
   - API interfaces
   - Data models
   - Technology choices
3. Consider:
   - Scalability
   - Maintainability
   - Security
   - Performance

You must respond with a valid JSON object in exactly this format:
{{
    "architecture_design": {{
        "components": [],
        "data_models": [],
        "api_interfaces": [],
        "tech_stack": {{}}
    }},
    "diagrams": {{
        "system": "mermaid diagram string",
        "data_flow": "mermaid diagram string"
    }},
    "rationale": "Explanation of design decisions"
}}

Ensure your response is a properly formatted JSON object and nothing else."""

class ArchitectWorker(BaseWorker):
    """
    Specialized worker for system architecture and design tasks.
    """
    
    def __init__(self):
        super().__init__()
        self.role = "ArchitectWorker"
        self.capabilities = [
            "System design",
            "Data modeling",
            "API design",
            "Technology selection",
            "Architecture documentation"
        ]
        self.design_prompt = PromptTemplate(
            template=ARCHITECTURE_DESIGN_TEMPLATE,
            input_variables=["task_goal", "requirements"]
        )
        
    def get_relevant_code_context(self, task: Task, state_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather architecture-relevant context from state.
        
        Args:
            task: The current task
            state_context: The current state context
            
        Returns:
            Dict containing formatted context for the architect
        """
        # Get base context
        context = super().get_relevant_code_context(task)
        
        # Extract requirements
        requirements = state_context.get('clarified_request', '')
        if not requirements and 'project_requirements' in state_context:
            requirements = state_context['project_requirements']
            
        return {
            'requirements': requirements or task['goal']  # Fallback to task goal if no requirements
        }
        
    def _extract_json_from_llm_response(self, content: str) -> str:
        """
        Strips markdown code block (```json ... ```) from LLM response if present.
        """
        content = content.strip()
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        elif content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()
        return content

    def build(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create system architecture design based on task requirements.
        """
        response = None
        try:
            # Get and format context
            design_context = self.get_relevant_code_context(task, context or {})
            
            print("\nSending prompt to LLM with:")
            print(f"Task Goal: {task['goal']}")
            print(f"Requirements: {design_context['requirements']}")
            
            # Generate architecture design
            response = llm.invoke(
                self.design_prompt.format(
                    task_goal=task['goal'],
                    requirements=design_context['requirements']
                )
            )
            
            print("\nReceived LLM response:")
            print(response.content)
            
            # Strip markdown code block if present
            json_str = self._extract_json_from_llm_response(response.content)
            
            # Parse and validate response
            try:
                design_result = json.loads(json_str)
                
                # Validate expected structure
                if not isinstance(design_result, dict):
                    raise ValueError("Response is not a JSON object")
                if "architecture_design" not in design_result:
                    raise ValueError("Response missing architecture_design")
                
                return {
                    'result': json.dumps(design_result, indent=2),
                    'artifacts': {
                        'architecture_doc': design_result,
                        'diagrams': design_result.get('diagrams', {}),
                        'components': design_result['architecture_design']['components'],
                        'api_interfaces': design_result['architecture_design']['api_interfaces']
                    }
                }
                
            except json.JSONDecodeError as e:
                print(f"\nFailed to parse LLM response as JSON: {str(e)}")
                print(f"Raw response content: {json_str}")
                return {
                    'result': f"Error parsing JSON: {str(e)}",
                    'error': str(e),
                    'artifacts': {
                        'error_details': str(e),
                        'raw_response': json_str
                    }
                }
                
        except Exception as e:
            print(f"\nError in build phase: {str(e)}")
            return {
                'result': f"Error in build phase: {str(e)}",
                'error': str(e),
                'artifacts': {
                    'error_details': str(e),
                    'raw_response': response.content if response else 'No response available'
                }
            }
            
    def validate(self, task: Task, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the architecture design against best practices and requirements.
        """
        try:
            # Parse the design if it's a string
            design = (
                json.loads(build_result['result'])
                if isinstance(build_result['result'], str)
                else build_result['result']
            )
            
            # Basic validation checks
            validation_results = []
            
            # Check components
            components = design['architecture_design']['components']
            if not components:
                validation_results.append({
                    'criterion': 'components',
                    'status': 'failed',
                    'details': 'No components defined'
                })
            else:
                validation_results.append({
                    'criterion': 'components',
                    'status': 'passed',
                    'details': f'Found {len(components)} components'
                })
            
            # Check API interfaces
            api_interfaces = design['architecture_design']['api_interfaces']
            if not api_interfaces:
                validation_results.append({
                    'criterion': 'api_interfaces',
                    'status': 'failed',
                    'details': 'No API interfaces defined'
                })
            else:
                validation_results.append({
                    'criterion': 'api_interfaces',
                    'status': 'passed',
                    'details': f'Found {len(api_interfaces)} API endpoints'
                })
            
            # Overall status
            status = 'Passed' if all(r['status'] == 'passed' for r in validation_results) else 'Failed'
            
            return {
                'status': status,
                'test_cases': [r['criterion'] for r in validation_results],
                'checks': validation_results,
                'error': None if status == 'Passed' else 'Some validation checks failed'
            }
            
        except Exception as e:
            print(f"Error in validation phase: {str(e)}")
            return {
                'status': 'Failed',
                'error': str(e),
                'test_cases': [],
                'checks': []
            } 