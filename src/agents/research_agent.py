from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
import os
import logging
from ..tools.paper_search import PaperSearchTool
from ..tools.pdf_parser import PDFParserTool
from ..tools.summarizer import SummarizerTool
from src.tools.semantic_search import SemanticSearchTool
from src.tools.arxiv_search import ArxivSearchTool
from src.tools.scholar_search import ScholarSearchTool
from src.tools.vector_store import VectorStore
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomPromptTemplate(PromptTemplate):
    def format_prompt(self, **kwargs) -> str:
        # Get the intermediate string from PromptTemplate
        prompt = self.template.format(**kwargs)
        return prompt

    def format(self, **kwargs) -> str:
        return self.format_prompt(**kwargs)

class ResearchAgent:
    def __init__(
        self,
        pdf_parser: PDFParserTool,
        semantic_search: SemanticSearchTool,
        summarizer: SummarizerTool,
        arxiv_search: ArxivSearchTool,
        scholar_search: ScholarSearchTool,
        vector_store: VectorStore
    ):
        self.pdf_parser = pdf_parser
        self.semantic_search = semantic_search
        self.summarizer = summarizer
        self.arxiv_search = arxiv_search
        self.scholar_search = scholar_search
        self.vector_store = vector_store
    
    async def analyze_paper(self, pdf_content: bytes) -> Dict:
        """Analyze a research paper"""
        try:
            start_time = time.time()
            # Parse PDF content
            logger.info("📄 Starting paper analysis...")
            parsed_content = await self.pdf_parser._arun(pdf_content)
            parse_time = time.time() - start_time
            logger.info(f"✅ PDF parsing completed in {parse_time:.2f} seconds")
            
            # Extract text for summarization
            text_content = "\n\n".join([
                parsed_content.get('abstract', ''),
                parsed_content.get('introduction', ''),
                parsed_content.get('methods', ''),
                parsed_content.get('results', ''),
                parsed_content.get('discussion', '')
            ])
            
            # Generate summary and extract key points
            logger.info("📝 Generating summary...")
            summary_start = time.time()
            summary = await self.summarizer.summarize(text_content)
            summary_time = time.time() - summary_start
            logger.info(f"✅ Summary generated in {summary_time:.2f} seconds")
            
            logger.info("🔑 Extracting key points...")
            key_points_start = time.time()
            key_points = await self.summarizer.extract_key_points(text_content)
            key_points_time = time.time() - key_points_start
            logger.info(f"✅ Key points extracted in {key_points_time:.2f} seconds")
            
            # Store the paper in vector store
            logger.info("📥 Storing paper in vector store...")
            store_start = time.time()
            await self.vector_store.store_document({
                'title': parsed_content.get('title', ''),
                'content': text_content,
                'summary': summary,
                'key_points': key_points
            })
            store_time = time.time() - store_start
            logger.info(f"✅ Paper stored in vector store in {store_time:.2f} seconds")
            
            total_time = time.time() - start_time
            logger.info(f"✅ Total processing time: {total_time:.2f} seconds")
            
            return {
                'title': parsed_content.get('title', ''),
                'summary': summary,
                'key_points': key_points,
                'figures': parsed_content.get('figures', ''),
                'references': parsed_content.get('references', '')
            }
        except Exception as e:
            logger.error(f"❌ Paper analysis failed: {str(e)}")
            raise Exception(f"Paper analysis failed: {str(e)}")
    
    async def search_related_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for related papers"""
        try:
            logger.info(f"🔍 Searching for papers related to: {query}")
            
            # Search on arXiv
            arxiv_results = await self.arxiv_search.search_papers(query, max_results)
            
            # Search on Google Scholar
            scholar_results = await self.scholar_search.search_papers(query, max_results)
            
            # Combine and deduplicate results
            all_results = []
            seen_titles = set()
            
            for paper in arxiv_results + scholar_results:
                title = paper.get('title', '').lower()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    all_results.append(paper)
            
            logger.info(f"✅ Found {len(all_results)} unique papers")
            return all_results[:max_results]
        except Exception as e:
            logger.error(f"❌ Related papers search failed: {str(e)}")
            raise Exception(f"Related papers search failed: {str(e)}")
    
    async def compare_papers(self, papers: List[Dict]) -> Dict:
        """Compare multiple papers"""
        try:
            logger.info(f"📊 Comparing {len(papers)} papers...")
            comparison = await self.summarizer.compare_papers(papers)
            logger.info("✅ Paper comparison completed")
            return {
                'comparison': comparison,
                'papers': papers
            }
        except Exception as e:
            logger.error(f"❌ Paper comparison failed: {str(e)}")
            raise Exception(f"Paper comparison failed: {str(e)}")
    
    async def find_citations(self, paper_title: str) -> List[Dict]:
        """Find papers that cite a specific paper"""
        try:
            logger.info(f"📑 Finding citations for: {paper_title}")
            citations = await self.scholar_search.get_citations(paper_title)
            logger.info(f"✅ Found {len(citations)} citations")
            return citations
        except Exception as e:
            logger.error(f"❌ Citation search failed: {str(e)}")
            raise Exception(f"Citation search failed: {str(e)}")
    
    async def find_author_papers(self, author_name: str, max_results: int = 5) -> List[Dict]:
        """Find papers by a specific author"""
        try:
            logger.info(f"👤 Finding papers by author: {author_name}")
            papers = await self.scholar_search.get_author_papers(author_name, max_results)
            logger.info(f"✅ Found {len(papers)} papers by {author_name}")
            return papers
        except Exception as e:
            logger.error(f"❌ Author papers search failed: {str(e)}")
            raise Exception(f"Author papers search failed: {str(e)}")