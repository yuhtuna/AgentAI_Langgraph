from src.config import llm
# Run this to debug your tree-sitter installation
# Debug script to find out why no chunks are being processed

import os
from pathlib import Path
from src.create_vectorstore import ProjectProcessor

def debug_project_processing():
    project_path = "/knowledge_base/narbhacks-main"
    project_name = "notes app"
    
    print("=== DEBUGGING PROJECT PROCESSING ===\n")
    
    # Step 1: Check if path exists
    print(f"1. Checking project path: {project_path}")
    if not os.path.exists(project_path):
        print(f"❌ ERROR: Path does not exist!")
        return
    else:
        print(f"✅ Path exists")
    
    # Step 2: List contents of the directory
    print(f"\n2. Contents of {project_path}:")
    try:
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path):
                print(f"📁 {item}/")
            else:
                print(f"📄 {item}")
    except Exception as e:
        print(f"❌ Error listing directory: {e}")
        return
    
    # Step 3: Look for specific file types
    print(f"\n3. Searching for JavaScript/TypeScript files:")
    project_root = Path(project_path)
    
    file_extensions = ['.js', '.jsx', '.ts', '.tsx', '.json']
    found_files = []
    
    for ext in file_extensions:
        files = list(project_root.rglob(f"*{ext}"))
        if files:
            print(f"  {ext} files: {len(files)}")
            for file in files[:5]:  # Show first 5
                print(f"    - {file}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
            found_files.extend(files)
        else:
            print(f"  {ext} files: 0")
    
    print(f"\nTotal files found: {len(found_files)}")
    
    # Step 4: Test file pattern matching
    print(f"\n4. Testing file pattern matching:")
    file_patterns = {
        'components': ['**/*.tsx', '**/*.jsx'],
        'pages': ['**/*.tsx', '**/*.jsx', '**/pages/**/*.ts', '**/pages/**/*.js'],
        'app': ['**/app/**/*.tsx', '**/app/**/*.jsx', '**/app/**/*.ts', '**/app/**/*.js'],
        'api': ['**/api/**/*.ts', '**/api/**/*.js'],
        'utils': ['**/utils/**/*.ts', '**/utils/**/*.js', '**/lib/**/*.ts', '**/lib/**/*.js'],
        'config': ['**/*.config.ts', '**/*.config.js', '**/*.config.json', 'package.json'],
    }
    
    total_matches = 0
    for category, patterns in file_patterns.items():
        category_matches = []
        for pattern in patterns:
            matches = list(project_root.glob(pattern))
            category_matches.extend(matches)
        
        if category_matches:
            print(f"  {category}: {len(category_matches)} files")
            for file in category_matches[:3]:  # Show first 3
                print(f"    - {file}")
            total_matches += len(category_matches)
        else:
            print(f"  {category}: 0 files")
    
    print(f"\nTotal pattern matches: {total_matches}")
    
    # Step 5: Test ignore patterns
    print(f"\n5. Testing ignore patterns:")
    ignore_patterns = [ 
        'node_modules', '.next', '.expo', 'dist', 'build', '.git', '.env', '.DS_Store'
    ]
    
    for file in found_files[:10]:  # Test first 10 files
        should_ignore = any(pattern in str(file) for pattern in ignore_patterns)
        status = "IGNORED" if should_ignore else "INCLUDED"
        print(f"  {file.name}: {status}")
    
    # Step 6: Test processor directly
    print(f"\n6. Testing ProjectProcessor:")
    try:
        processor = ProjectProcessor()
        print("✅ ProjectProcessor created successfully")
        
        # Test on a single file if available
        if found_files:
            test_file = found_files[0]
            print(f"Testing with file: {test_file}")
            
            try:
                chunks = processor._process_file(test_file, "test", project_name)
                print(f"✅ File processed successfully, generated {len(chunks)} chunks")
                
                if chunks:
                    chunk = chunks[0]
                    print(f"Sample chunk:")
                    print(f"  - Content length: {len(chunk.content)}")
                    print(f"  - File type: {chunk.file_type}")
                    print(f"  - Language: {chunk.language}")
                    print(f"  - Framework: {chunk.framework}")
                
            except Exception as e:
                print(f"❌ Error processing file: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error creating ProjectProcessor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_project_processing()
response = llm.invoke("Hello, how are you?")
print(response)