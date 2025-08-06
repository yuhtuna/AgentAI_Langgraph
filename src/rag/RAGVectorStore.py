import chromadb
from typing import List, Dict, Optional
import hashlib
from src.rag.CodeVectorStore import CodeVectorStore

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
