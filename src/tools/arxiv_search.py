from langchain.tools import BaseTool
from typing import Dict, List
import logging
import arxiv

logger = logging.getLogger(__name__)

class ArxivSearchTool(BaseTool):
    name = "arxiv_search"
    description = "Search for papers on arXiv"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def _run(self, query: str) -> Dict:
        """Synchronous version of search (required by BaseTool)"""
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, query: str) -> Dict:
        """Search arXiv for papers"""
        try:
            logger.info(f"🔍 Searching arXiv for: {query}")
            # Placeholder for actual arXiv search implementation
            return {
                "results": [],
                "query": query
            }
        except Exception as e:
            logger.error(f"❌ arXiv search failed: {str(e)}")
            raise Exception(f"arXiv search failed: {str(e)}")
    
    async def search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for papers on arXiv"""
        try:
            logger.info(f"📚 Searching arXiv papers for: {query}")
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for result in search.results():
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "pdf_url": result.pdf_url,
                    "doi": result.doi if hasattr(result, 'doi') else None
                }
                results.append(paper)
            
            logger.info(f"✅ Found {len(results)} papers")
            return results
        except Exception as e:
            logger.error(f"❌ arXiv paper search failed: {str(e)}")
            raise Exception(f"arXiv paper search failed: {str(e)}")
    
    async def get_paper_by_id(self, paper_id: str) -> Dict:
        """Get a specific paper by its arXiv ID"""
        try:
            logger.info(f"📄 Fetching paper with ID: {paper_id}")
            search = arxiv.Search(id_list=[paper_id])
            result = next(search.results())
            
            paper = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "pdf_url": result.pdf_url,
                "doi": result.doi if hasattr(result, 'doi') else None
            }
            
            logger.info("✅ Paper fetched successfully")
            return paper
        except Exception as e:
            logger.error(f"❌ Failed to fetch paper: {str(e)}")
            raise Exception(f"Failed to fetch paper: {str(e)}") 