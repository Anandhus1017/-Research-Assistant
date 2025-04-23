import chromadb
from chromadb.config import Settings
from typing import List, Dict
import numpy as np

class VectorStore:
    def __init__(self, persist_directory: str):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        self.collection = self.client.get_or_create_collection("research_papers")
    
    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """Add documents and their embeddings to the vector store"""
        ids = [doc['metadata']['chunk_hash'] for doc in documents]
        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return [{
            'text': doc,
            'metadata': metadata
        } for doc, metadata in zip(results['documents'][0], results['metadatas'][0])]