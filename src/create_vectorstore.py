import os 
import re
import json 
import hashlib 
from pathlib import Path 
from typing import List, Dict, Optional, Tuple 
from dataclasses import dataclass, field, asdict
import chromadb 
from chromadb.config import Settings

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


class RAGVectorStore: 

    def __init__(self, collection_name: str = "narbtech_code", persist_directory: str = "./chroma_db"):
         self.client = chromadb.PersistentClient(path=persist_directory)
         self.collection_name = collection_name
         self.collection = None 
         self._setup_collection()

    def _setup_collection(self): 
        try: 
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except Exception as e: 
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Narbtech code chunks for RAG"}
            )
            print(f"Created new collection: {self.collection_name}")

    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Narbtech code chunks for RAG"}
            )
            print(f"Cleared and recreated collection: {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    
    def _create_searchable_text(self, chunk: CodeVectorStore) -> str:
        """Create searchable text representation of code chunk"""
        searchable_parts = [
            f"Framework: {chunk.framework}",
            f"Type: {chunk.file_type}",
            f"Language: {chunk.language}",
            f"Description: {chunk.description}",
        ]
        
        if chunk.component_name:
            searchable_parts.append(f"Component: {chunk.component_name}")
        if chunk.function_name:
            searchable_parts.append(f"Function: {chunk.function_name}")
        if chunk.dependencies:
            searchable_parts.append(f"Dependencies: {', '.join(chunk.dependencies)}")
            
        searchable_parts.append(f"Code:\n{chunk.content}")
        
        return "\n".join(searchable_parts)
    
    def add_chunks(self, chunks: List[CodeVectorStore]): 
        if not chunks: 
            print("No chunks to add")
            return 
        
        print(f"Starting to process {len(chunks)} chunks...")
        
        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks): 
            try:
                doc_text = self._create_searchable_text(chunk)
                documents.append(doc_text)
                
                # Create metadata - ensure all values are JSON serializable
                metadata = self._prepare_metadata(chunk)
                metadatas.append(metadata)
                
                # Create unique ID
                chunk_id = self._generate_chunk_id(chunk)
                ids.append(chunk_id)
                
                if i < 3:  # Debug first few
                    print(f"Chunk {i+1}: ID={chunk_id}, doc_length={len(doc_text)}")
                    
            except Exception as e:
                print(f"Error processing chunk {i}: {e}")
                continue
        
        print(f"Prepared {len(documents)} documents for insertion")
        
        # Remove duplicates
        unique_docs, unique_metas, unique_ids = self._remove_duplicates(documents, metadatas, ids)
        print(f"After deduplication: {len(unique_docs)} unique documents")
        
        if not unique_docs:
            print("No unique documents to add!")
            return
        
        # Add in smaller batches with error handling
        batch_size = 10  # Smaller batches for debugging
        total_added = 0
        
        for i in range(0, len(unique_docs), batch_size):
            batch_docs = unique_docs[i:i+batch_size]
            batch_metadata = unique_metas[i:i+batch_size]
            batch_ids = unique_ids[i:i+batch_size]
            
            print(f"Adding batch {i//batch_size + 1}: {len(batch_docs)} documents")
            
            try:
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadata,
                    ids=batch_ids
                )
                total_added += len(batch_docs)
                print(f"✅ Successfully added batch {i//batch_size + 1}")
                
            except Exception as e:
                print(f"❌ Error adding batch {i//batch_size + 1}: {e}")
                print(f"Batch details: {len(batch_docs)} docs, {len(batch_metadata)} metadata, {len(batch_ids)} ids")
                
                # Try individual documents in this batch
                for j, (doc, meta, doc_id) in enumerate(zip(batch_docs, batch_metadata, batch_ids)):
                    try:
                        print(f"  Trying individual document {j+1}: {doc_id}")
                        self.collection.add(
                            documents=[doc],
                            metadatas=[meta],
                            ids=[doc_id]
                        )
                        total_added += 1
                        print(f"  ✅ Added individual document {doc_id}")
                    except Exception as individual_error:
                        print(f"  ❌ Failed individual document {doc_id}: {individual_error}")
                        print(f"    Doc length: {len(doc)}")
                        print(f"    Metadata keys: {list(meta.keys())}")
        
        # Verify what was actually added
        try:
            final_count = self.collection.count()
            print(f"Final collection count: {final_count}")
            print(f"Successfully added {total_added} out of {len(chunks)} chunks")
        except Exception as e:
            print(f"Error getting final count: {e}")
    
    def _prepare_metadata(self, chunk: CodeVectorStore) -> Dict:
        """Prepare metadata ensuring all values are JSON serializable"""
        metadata = {
            'file_path': str(chunk.file_path),
            'project_name': str(chunk.project_name),
            'file_type': str(chunk.file_type),
            'language': str(chunk.language),
            'framework': str(chunk.framework),
            'description': str(chunk.description),
        }
        
        # Add optional fields if they exist
        if chunk.function_name:
            metadata['function_name'] = str(chunk.function_name)
        if chunk.component_name:
            metadata['component_name'] = str(chunk.component_name)
        if chunk.dependencies:
            # Join dependencies into a string to avoid list serialization issues
            metadata['dependencies'] = ', '.join(str(dep) for dep in chunk.dependencies)
        
        return metadata
    
    def _remove_duplicates(self, documents, metadatas, ids):
        """Remove duplicate IDs"""
        seen_ids = set()
        unique_docs = []
        unique_metas = []
        unique_ids = []
        
        for doc, meta, doc_id in zip(documents, metadatas, ids):
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_docs.append(doc)
                unique_metas.append(meta)
                unique_ids.append(doc_id)
            else:
                print(f"Skipping duplicate ID: {doc_id}")
        
        return unique_docs, unique_metas, unique_ids
    
    def _create_searchable_text(self, chunk: CodeVectorStore) -> str:
        """Create searchable text representation of code chunk"""
        searchable_parts = [
            f"Framework: {chunk.framework}",
            f"Type: {chunk.file_type}",
            f"Language: {chunk.language}",
            f"Description: {chunk.description}",
        ]
        
        if chunk.component_name:
            searchable_parts.append(f"Component: {chunk.component_name}")
        if chunk.function_name:
            searchable_parts.append(f"Function: {chunk.function_name}")
        if chunk.dependencies:
            searchable_parts.append(f"Dependencies: {', '.join(chunk.dependencies)}")
            
        searchable_parts.append(f"Code:\n{chunk.content}")
        
        return "\n".join(searchable_parts)

    def _generate_chunk_id(self, chunk: CodeVectorStore) -> str:
        path_hash = hashlib.md5(chunk.file_path.encode()).hexdigest()[:8]
        content_hash = hashlib.md5(chunk.content.encode()).hexdigest()[:8]
        return f"{chunk.project_name}_{chunk.framework}_{path_hash}_{content_hash}"

    def search(self, query: str, n_results: int = 5, 
              framework_filter: Optional[str] = None,
              file_type_filter: Optional[str] = None) -> List[Dict]:
        """Search for code chunks"""
        where_clause = {}
        if framework_filter:
            where_clause["framework"] = framework_filter
        if file_type_filter:
            where_clause["file_type"] = file_type_filter

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Format results
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                result = {
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)
        
        return formatted_results


class RAGRetriever: 
    def __init__(self, vector_store: RAGVectorStore): 
        self.vector_store = vector_store

    def retrieve_context(self, user_request: str, max_chunks: int = 5) -> List[str]: 
        """Retrieve context from vector store"""
        all_results = []
        
        # Search for UI/component related requests
        if self._mentions_ui(user_request):
            ui_results = self.vector_store.search(
                query=f"{user_request} React component UI",
                n_results=3,
                file_type_filter="component"
            )
            all_results.extend(ui_results)
        
        # Search for backend functionality
        if self._mentions_backend(user_request):
            backend_results = self.vector_store.search(
                query=f"{user_request} function API",
                n_results=3,
                framework_filter="convex"
            )
            all_results.extend(backend_results)
        
        # Search for authentication related code
        if self._mentions_auth(user_request):
            auth_results = self.vector_store.search(
                query=f"{user_request} authentication login",
                n_results=2,
                framework_filter="clerk-auth"
            )
            all_results.extend(auth_results)
        
        # General search if we don't have enough results
        if len(all_results) < max_chunks:
            general_results = self.vector_store.search(
                query=user_request,
                n_results=max_chunks - len(all_results)
            )
            all_results.extend(general_results)
        
        # Extract and format contexts
        contexts = []
        for result in all_results[:max_chunks]:
            contexts.append(self._format_context(result))
        
        return contexts

    def _mentions_ui(self, request: str) -> bool:
        """Check if request mentions UI elements"""
        ui_terms = ['page', 'component', 'form', 'button', 'ui', 'interface', 'layout', 'design', 'dashboard', 'screen']
        return any(term in request.lower() for term in ui_terms)
    
    def _mentions_backend(self, request: str) -> bool:
        """Check if request mentions backend functionality"""
        backend_terms = ['api', 'database', 'function', 'store', 'save', 'fetch', 'query', 'mutation', 'convex']
        return any(term in request.lower() for term in backend_terms)
    
    def _mentions_auth(self, request: str) -> bool:
        """Check if request mentions authentication"""
        auth_terms = ['auth', 'login', 'signin', 'signup', 'user', 'authentication', 'clerk']
        return any(term in request.lower() for term in auth_terms)
    
    def _format_context(self, result: Dict) -> str:
        """Format search result into context string"""
        metadata = result['metadata']
        
        context_parts = [
            f"// File: {metadata['file_path']}",
            f"// Project: {metadata['project_name']}",
            f"// Type: {metadata['file_type']} ({metadata['framework']})",
            f"// Description: {metadata['description']}",
        ]
        
        if metadata.get('dependencies'):
            context_parts.append(f"// Dependencies: {', '.join(metadata['dependencies'])}")
        
        context_parts.append("")  # Empty line
        
        # Extract actual code content (it's embedded in the searchable text)
        content = result['content']
        if "Code:\n" in content:
            code_content = content.split("Code:\n", 1)[1]
            context_parts.append(code_content)
        else:
            context_parts.append(content)
        
        return "\n".join(context_parts)

