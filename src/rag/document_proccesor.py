from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
import hashlib

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def process_pdf(self, file_path: str) -> List[Dict]:
        """Process a PDF document and return chunks with metadata"""
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        chunks = self.text_splitter.split_documents(pages)
        
        processed_chunks = []
        for chunk in chunks:
            chunk_text = chunk.page_content
            chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()
            
            processed_chunks.append({
                'text': chunk_text,
                'metadata': {
                    'page': chunk.metadata.get('page', 0),
                    'chunk_hash': chunk_hash,
                    'source_file': file_path
                }
            })
        
        return processed_chunks