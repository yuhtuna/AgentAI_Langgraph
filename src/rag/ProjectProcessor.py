from src.rag.CodeVectorStore import CodeVectorStore
from pathlib import Path
from typing import List, Optional
import re
import json

class ProjectProcessor: 
    def __init__(self): 
        print("✅ ProjectProcessor initialized (Tree Sitter disabled)")

    def process_project(self, project_path: str, project_name: str) -> List[CodeVectorStore]: 
        chunks = []
        project_root = Path(project_path)
        
        # Updated patterns for modern JS/TS projects
        file_patterns = {
            'components': ['**/components/**/*.tsx', '**/components/**/*.jsx'],
            'pages': ['**/pages/**/*.ts', '**/pages/**/*.js', '**/pages/**/*.tsx', '**/pages/**/*.jsx'],
            'app_routes': ['**/app/**/page.tsx', '**/app/**/layout.tsx', '**/app/**/loading.tsx', '**/app/**/error.tsx'],
            'app_components': ['**/app/**/*.tsx', '**/app/**/*.jsx'],
            'api': ['**/api/**/*.ts', '**/api/**/*.js'],
            'utils': ['**/utils/**/*.ts', '**/utils/**/*.js'],
            'lib': ['**/lib/**/*.ts', '**/lib/**/*.js'],
            'hooks': ['**/hooks/**/*.ts', '**/hooks/**/*.js'],
            'schemas': ['**/schemas/**/*.ts', '**/types/**/*.ts'],
            'styles': ['**/*.css', '**/*.scss', '**/*.module.css'],
            'config': ['**/*.config.ts', '**/*.config.js', '**/*.config.json', 'package.json', 'tsconfig.json'],
            'screens': ['**/screens/**/*.tsx', '**/screens/**/*.ts'],
            'navigation': ['**/navigation/**/*.tsx', '**/navigation/**/*.ts'],
        }
    
        for category, patterns in file_patterns.items(): 
            for pattern in patterns: 
                for file in project_root.glob(pattern): 
                    if file.is_file() and not self._should_ignore_file(file):
                        chunks.extend(self._process_file(file, category, project_name))
        
        print(f"✅ Processed {len(chunks)} chunks from {project_name}")
        return chunks
        
    def _should_ignore_file(self, file: Path) -> bool: 
        ignore_patterns = [ 
            'node_modules', '.next', '.expo', 'dist', 'build', '.git', '.env', '.DS_Store',
            '__pycache__', '.pytest_cache', 'coverage', '.nyc_output'
        ] 
        return any(pattern in str(file) for pattern in ignore_patterns)

    def _process_file(self, file: Path, category: str, project_name: str) -> List[CodeVectorStore]: 
        try: 
            content = file.read_text(encoding='utf-8')
            
            if file.suffix == '.json':
                return self._process_json_file(file, project_name, content)

            language = self._get_language_from_extension(file.suffix)
            if not language: 
                return []

            return self._create_file_chunk(content, file, project_name, category, language)
            
        except Exception as e: 
            print(f"Error processing file {file}: {str(e)}")
            return []

    def _get_language_from_extension(self, extension: str) -> Optional[str]: 
        language_map = {
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.py': 'python',
            '.json': 'json',
            '.css': 'css',
            '.scss': 'scss'
        }
        return language_map.get(extension)

    def _create_file_chunk(self, content: str, file: Path, project_name: str, category: str, language: str) -> List[CodeVectorStore]:
        """Create a chunk for the entire file with metadata extraction"""
        try:
            framework_type = self._determine_framework_type(file, content)
            dependencies = self._extract_dependencies(content)
            
            # Determine if this looks like a React component
            is_component = self._detect_react_component(content, file.name)
            
            # Extract component/function names
            component_name = None
            function_name = None
            
            if is_component:
                component_name = self._extract_component_name(content, file.name)
            else:
                function_name = self._extract_function_name(content)
            
            chunk = CodeVectorStore(
                content=content,
                file_path=str(file),
                project_name=project_name,
                file_type='component' if is_component else category,
                language=language,
                component_name=component_name,
                function_name=function_name,
                dependencies=dependencies,
                description=self._generate_description(content, file.name, framework_type, is_component),
                framework=framework_type
            )
            
            return [chunk]
            
        except Exception as e:
            print(f"Error creating chunk for {file}: {e}")
            # Ultra-simple fallback
            chunk = CodeVectorStore(
                content=content,
                file_path=str(file),
                project_name=project_name,
                file_type=category,
                language=language,
                description=f"Code from {file.name}"
            )
            return [chunk]

    def _determine_framework_type(self, file: Path, content: str) -> str:
        """Determine the framework/technology used"""
        path_str = str(file).lower()
        content_lower = content.lower()
        
        # Framework detection based on path and content
        if 'convex' in path_str or 'convex' in content_lower:
            return 'convex'
        elif any(x in path_str for x in ['native', 'expo', 'react-native']):
            return 'react-native'
        elif any(x in path_str for x in ['app', 'pages']) and 'native' not in path_str:
            return 'nextjs'
        elif 'clerk' in content_lower:
            return 'clerk-auth'
        elif 'api' in path_str:
            return 'api'
        elif any(x in content_lower for x in ['react', 'jsx', 'tsx']):
            return 'react'
        
        return 'general'

    def _detect_react_component(self, content: str, filename: str) -> bool:
        """Simple detection for React components"""
        if not filename.endswith(('.tsx', '.jsx')):
            return False
            
        # Check for React patterns in content
        react_patterns = [
            'export default function',
            'export const',
            'return (',
            'React.',
            'useState',
            'useEffect',
            '<div',
            '<View',
            'JSX.Element',
            'FC<',
            'FunctionComponent'
        ]
        return any(pattern in content for pattern in react_patterns)

    def _extract_component_name(self, content: str, filename: str) -> Optional[str]:
        """Extract component name from file"""
        # Try to get from filename first
        base_name = filename.split('.')[0]
        if base_name and base_name[0].isupper():
            return base_name
        
        # Try to extract from export statements
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('export default function '):
                parts = line.split('export default function ')
                if len(parts) > 1:
                    name = parts[1].split('(')[0].strip()
                    if name:
                        return name
            elif line.startswith('export const '):
                parts = line.split('export const ')
                if len(parts) > 1:
                    name = parts[1].split('=')[0].strip()
                    if name and name[0].isupper():
                        return name
        
        return None

    def _extract_function_name(self, content: str) -> Optional[str]:
        """Extract main function name from non-component files"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('export function '):
                parts = line.split('export function ')
                if len(parts) > 1:
                    name = parts[1].split('(')[0].strip()
                    if name:
                        return name
            elif line.startswith('function '):
                parts = line.split('function ')
                if len(parts) > 1:
                    name = parts[1].split('(')[0].strip()
                    if name:
                        return name
        return None

    def _extract_dependencies(self, content: str) -> List[str]: 
        """Extract import dependencies from the file - FIXED VERSION"""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Handle: import something from 'module'
            if line.startswith('import ') and ' from ' in line:
                try:
                    # Use regex to extract the module name after 'from'
                    from_match = re.search(r'from\s+["\']([^"\']+)["\']', line)
                    if from_match:
                        module = from_match.group(1)
                        # Skip relative imports
                        if not (module.startswith('./') or module.startswith('../')):
                            dependencies.append(module)
                except Exception as e:
                    print(f"Error parsing import line: {line} - {e}")
            
            # Handle: import 'module' (direct imports)
            elif line.startswith('import ') and not ' from ' in line and ('import "' in line or "import '" in line):
                try:
                    import_match = re.search(r'import\s+["\']([^"\']+)["\']', line)
                    if import_match:
                        module = import_match.group(1)
                        if not (module.startswith('./') or module.startswith('../')):
                            dependencies.append(module)
                except Exception as e:
                    print(f"Error parsing direct import: {line} - {e}")
        
        # Remove duplicates and return
        return list(set(dependencies))

    def _generate_description(self, content: str, filename: str, framework_type: str, is_component: bool) -> str:
        """Generate a description for the code"""
        # Look for comments at the top
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                comment = line.lstrip('/*/ *').strip()
                if len(comment) > 10 and not comment.startswith('@'):
                    return comment
        
        # Generate based on file type and patterns
        if is_component:
            component_name = self._extract_component_name(content, filename)
            return f"React component: {component_name or filename} ({framework_type})"
        elif 'api' in filename.lower() or 'api' in framework_type:
            return f"API endpoint: {filename} ({framework_type})"
        elif filename.endswith('.config.js') or filename.endswith('.config.ts'):
            return f"Configuration file: {filename}"
        elif 'hook' in filename.lower():
            return f"React hook: {filename} ({framework_type})"
        elif 'util' in filename.lower() or 'lib' in filename.lower():
            return f"Utility function: {filename} ({framework_type})"
        else:
            return f"Code file: {filename} ({framework_type})"
    
    def _process_json_file(self, file_path: Path, project_name: str, content: str) -> List[CodeVectorStore]:
        """Process JSON configuration files"""
        try:
            data = json.loads(content)
            
            # Special handling for different JSON files
            if file_path.name == 'package.json':
                description = f"Package configuration - {data.get('name', 'Unknown')}"
                dependencies = list(data.get('dependencies', {}).keys())
            elif file_path.name == 'tsconfig.json':
                description = "TypeScript configuration"
                dependencies = []
            else:
                description = f"JSON configuration: {file_path.name}"
                dependencies = []
                
            return [CodeVectorStore(
                content=content,
                file_path=str(file_path),
                project_name=project_name,
                file_type='config',
                language='json',
                dependencies=dependencies,
                description=description,
                framework='config'
            )]
            
        except json.JSONDecodeError:
            return []
