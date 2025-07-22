import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- Configuration ---
KNOWLEDGE_BASE_DIR = "knowledge_base"
VECTORSTORE_DIR = "vectorstore"
# Using a local, open-source embedding model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def create_vectorstore():
    """
    Creates a Chroma vector store from documents in the knowledge base directory.
    """
    print("--- Creating vector store ---")
    
    # 1. Load documents manually
    documents = []
    knowledge_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith('.md')]
    
    for filename in knowledge_files:
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        print(f"Loading: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                doc = Document(page_content=content, metadata={"source": filename})
                documents.append(doc)
                print(f"✅ Loaded {filename} ({len(content)} characters)")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
    
    if not documents:
        print("No documents found in the knowledge base.")
        return

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    # 3. Create embeddings
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # 4. Create and persist the vector store
    print(f"Creating vector store in directory: {VECTORSTORE_DIR}")
    if not os.path.exists(VECTORSTORE_DIR):
        os.makedirs(VECTORSTORE_DIR)
        
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR
    )
    
    print("--- Vector store created successfully! ---")
    print(f"Total documents processed: {len(documents)}")
    print(f"Total chunks created: {len(splits)}")
    print(f"Vector store saved to: {VECTORSTORE_DIR}")
    
    # Test the vector store
    test_results = vectorstore.similarity_search("AI advancements", k=2)
    print(f"🧪 Test search found {len(test_results)} results")
    for i, doc in enumerate(test_results):
        print(f"  Result {i+1}: {doc.page_content[:100]}...")


if __name__ == "__main__":
    create_vectorstore()
