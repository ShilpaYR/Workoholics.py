import os
from dotenv import load_dotenv
from chromadb import Client
from chromadb.config import Settings
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests

# Load environment variables from .env file
load_dotenv()

# Get Jina API key from environment variable
JINA_API_KEY = os.environ.get("JINA_API_KEY")
if not JINA_API_KEY:
    raise ValueError("Please set JINA_API_KEY environment variable")

def read_text_files(directory):
    """Read all txt files from the reports directory"""
    documents = []
    metadatas = []
    
    reports_path = os.path.join(directory, "reports")
    
    if not os.path.exists(reports_path):
        raise FileNotFoundError(f"Reports directory not found at {reports_path}")
    
    for filename in os.listdir(reports_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(reports_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append(content)
                metadatas.append({"source": filename})
    
    return documents, metadatas

def chunk_documents(documents, metadatas):
    """Chunk documents using RecursiveCharacterTextSplitter"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,  # Adjust based on your needs
        chunk_overlap=20,  # Overlap to maintain context
        
    )
    
    chunked_documents = []
    chunked_metadatas = []
    chunked_ids = []
    
    for idx, (doc, metadata) in enumerate(zip(documents, metadatas)):
        chunks = text_splitter.split_text(doc)
        
        for chunk_idx, chunk in enumerate(chunks):
            chunked_documents.append(chunk)
            # Add chunk information to metadata
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_idx
            chunk_metadata["total_chunks"] = len(chunks)
            chunked_metadatas.append(chunk_metadata)
            # Create unique ID for each chunk
            chunked_ids.append(f"{metadata['source']}_chunk_{chunk_idx}")
    
    return chunked_documents, chunked_metadatas, chunked_ids

def create_embeddings(texts):
    """Create embeddings using Jina AI API"""
    url = 'https://api.jina.ai/v1/embeddings'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JINA_API_KEY}'
    }
    
    # Process in batches to avoid API limits
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        data = {
            'input': batch,
            'model': 'jina-embeddings-v3'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            batch_embeddings = [item['embedding'] for item in result['data']]
            all_embeddings.extend(batch_embeddings)
            
            print(f"Processed {min(i + batch_size, len(texts))}/{len(texts)} chunks")
        except requests.exceptions.HTTPError as e:
            print(f"Error response: {response.text}")
            raise e
    
    return all_embeddings

def main():
    # Get the current directory (chatbot directory)
    current_dir = os.getcwd()
    
    print("Reading documents from reports directory...")
    documents, metadatas = read_text_files(current_dir)
    print(f"Found {len(documents)} documents")
    
    print("Chunking documents...")
    chunked_docs, chunked_metas, chunked_ids = chunk_documents(documents, metadatas)
    print(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
    
    print("Creating embeddings...")
    embeddings = create_embeddings(chunked_docs)
    print(f"Created {len(embeddings)} embeddings")
    
    # Initialize ChromaDB with persistence
    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Create or get collection
    collection_name = "reports_collection"
    
    # Delete collection if it exists (for fresh start)
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Reports documents collection with chunking"}
    )
    
    print("Adding chunks to ChromaDB...")
    collection.add(
        embeddings=embeddings,
        documents=chunked_docs,
        metadatas=chunked_metas,
        ids=chunked_ids
    )
    
    print(f"Successfully stored {len(chunked_docs)} chunks from {len(documents)} documents in ChromaDB")
    print("Database persisted at ./chroma_db")

if __name__ == "__main__":
    main()