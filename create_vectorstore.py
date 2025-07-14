import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
    
    # 1. Load documents
    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.md", show_progress=True)
    documents = loader.load()
    
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


if __name__ == "__main__":
    create_vectorstore()
