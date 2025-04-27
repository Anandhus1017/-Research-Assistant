from langchain.tools import BaseTool
from typing import Dict, List
import logging
from scholarly import scholarly

logger = logging.getLogger(__name__)

class ScholarSearchTool(BaseTool):
    name = "scholar_search"
    description = "Search for papers on Google Scholar"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def _run(self, query: str) -> Dict:
        """Synchronous version of search (required by BaseTool)"""
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, query: str) -> Dict:
        """Search Google Scholar for papers"""
        try:
            logger.info(f"🔍 Searching Google Scholar for: {query}")
            # Placeholder for actual Scholar search implementation
            return {
                "results": [],
                "query": query
            }
        except Exception as e:
            logger.error(f"❌ Google Scholar search failed: {str(e)}")
            raise Exception(f"Google Scholar search failed: {str(e)}")
    
    async def search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for papers on Google Scholar"""
        try:
            logger.info(f"📚 Searching Google Scholar papers for: {query}")
            search_query = scholarly.search_pubs(query)
            results = []
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                    
                paper = {
                    "title": result.bib.get('title', ''),
                    "authors": result.bib.get('author', []),
                    "abstract": result.bib.get('abstract', ''),
                    "year": result.bib.get('year', ''),
                    "url": result.bib.get('url', ''),
                    "citations": result.citedby if hasattr(result, 'citedby') else 0
                }
                results.append(paper)
            
            logger.info(f"✅ Found {len(results)} papers")
            return results
        except Exception as e:
            logger.error(f"❌ Google Scholar paper search failed: {str(e)}")
            raise Exception(f"Google Scholar paper search failed: {str(e)}")
    
    async def get_author_papers(self, author_name: str, max_results: int = 5) -> List[Dict]:
        """Get papers by a specific author"""
        try:
            logger.info(f"👤 Searching papers by author: {author_name}")
            search_query = scholarly.search_author(author_name)
            author = next(search_query)
            results = []
            
            for i, pub in enumerate(author.publications):
                if i >= max_results:
                    break
                    
                paper = {
                    "title": pub.bib.get('title', ''),
                    "authors": pub.bib.get('author', []),
                    "abstract": pub.bib.get('abstract', ''),
                    "year": pub.bib.get('year', ''),
                    "url": pub.bib.get('url', ''),
                    "citations": pub.citedby if hasattr(pub, 'citedby') else 0
                }
                results.append(paper)
            
            logger.info(f"✅ Found {len(results)} papers by {author_name}")
            return results
        except Exception as e:
            logger.error(f"❌ Failed to fetch author papers: {str(e)}")
            raise Exception(f"Failed to fetch author papers: {str(e)}")
    
    async def get_citations(self, paper_title: str) -> List[Dict]:
        """Get papers that cite a specific paper"""
        try:
            logger.info(f"📑 Searching citations for: {paper_title}")
            search_query = scholarly.search_pubs(paper_title)
            paper = next(search_query)
            results = []
            
            for citation in paper.get_citedby():
                cited_paper = {
                    "title": citation.bib.get('title', ''),
                    "authors": citation.bib.get('author', []),
                    "year": citation.bib.get('year', ''),
                    "url": citation.bib.get('url', '')
                }
                results.append(cited_paper)
            
            logger.info(f"✅ Found {len(results)} citations")
            return results
        except Exception as e:
            logger.error(f"❌ Failed to fetch citations: {str(e)}")
            raise Exception(f"Failed to fetch citations: {str(e)}") 