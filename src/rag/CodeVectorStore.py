from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CodeVectorStore: 
    content: str 
    file_path: str
    project_name: str 
    file_type: str 
    language: str 
    function_name: Optional[str] = None
    component_name: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    framework: str = ""