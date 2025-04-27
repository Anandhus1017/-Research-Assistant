from langchain_community.llms import Ollama
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from typing import Dict, List, Any
from pydantic import Field, PrivateAttr
import os
import asyncio
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummarizerTool(BaseTool):
    name = "summarizer"
    description = "Generate summaries and extract key points from research papers and text content"
    _llm: Any = PrivateAttr()
    _summary_prompt: Any = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Get Ollama configuration from environment variables
        ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'mistral')
        
        # Using Ollama with configuration from environment variables
        object.__setattr__(self, '_llm', Ollama(
            base_url=ollama_host,
            model=ollama_model,
            num_ctx=1024,  # Reduced context size
            num_thread=2,  # Reduced threads
            timeout=30     # 30 second timeout
        ))
        object.__setattr__(self, '_summary_prompt', ChatPromptTemplate.from_template(
            """Summarize the following research paper content in 3-4 sentences:
            
            {content}
            
            Focus on:
            1. Main findings
            2. Key contributions
            3. Methodology
            """
        ))
    
    def _run(self, text: str) -> str:
        """Synchronous version of summarize (required by BaseTool)"""
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, text: str) -> str:
        """Generate a summary of the given text"""
        return await self.summarize(text)
    
    async def summarize(self, text: str) -> str:
        """Generate a summary of the given text"""
        try:
            start_time = time.time()
            logger.info("📝 Starting summarization...")
            
            # Limit text length to first 1000 characters
            text = text[:1000] + "..." if len(text) > 1000 else text
            
            prompt = self._summary_prompt.format(content=text)
            logger.info("🤖 Sending request to Mistral model...")
            
            # Use a simpler approach with Ollama and add timeout
            try:
                response = await asyncio.wait_for(
                    self._llm.agenerate([prompt]),
                    timeout=30
                )
                logger.info("✅ Summary generated")
                
                total_time = time.time() - start_time
                logger.info(f"✨ Summarization completed in {total_time:.2f} seconds")
                
                return str(response.generations[0][0].text)
            except asyncio.TimeoutError:
                logger.error("❌ Summarization timed out")
                return "Summary generation timed out. Please try again with a shorter text."
            
        except Exception as e:
            logger.error(f"❌ Summarization failed: {str(e)}")
            raise Exception(f"Summarization failed: {str(e)}")
    
    async def extract_key_points(self, text: str) -> Dict:
        """Extract key points from the text"""
        try:
            start_time = time.time()
            logger.info("🔑 Starting key points extraction...")
            
            # Limit text length to first 1000 characters
            text = text[:1000] + "..." if len(text) > 1000 else text
            
            prompt = f"""
            Extract the 3 most important points from the following text:
            
            {text}
            
            Format the response as a JSON object with the following structure:
            {{
                "main_points": ["point1", "point2", "point3"]
            }}
            """
            logger.info("🤖 Sending request to Mistral model...")
            
            # Use a simpler approach with Ollama and add timeout
            try:
                response = await asyncio.wait_for(
                    self._llm.agenerate([prompt]),
                    timeout=30
                )
                logger.info("✅ Key points extracted")
                
                total_time = time.time() - start_time
                logger.info(f"✨ Key points extraction completed in {total_time:.2f} seconds")
                
                return self._parse_key_points(str(response.generations[0][0].text))
            except asyncio.TimeoutError:
                logger.error("❌ Key points extraction timed out")
                return {"main_points": ["Extraction timed out. Please try again with a shorter text."]}
            
        except Exception as e:
            logger.error(f"❌ Key points extraction failed: {str(e)}")
            raise Exception(f"Key points extraction failed: {str(e)}")
    
    def _parse_key_points(self, text: str) -> Dict:
        """Parse the key points from the LLM response"""
        try:
            import json
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback to a simple structure if JSON parsing fails
            return {
                "main_points": ["Failed to parse key points. Please try again."]
            }
    
    async def summarize_paper(self, paper_content: Dict) -> Dict:
        """Generate a comprehensive summary of a research paper"""
        try:
            # Limit the content we process
            text = paper_content.get('text', '')[:1000] + "..." if len(paper_content.get('text', '')) > 1000 else paper_content.get('text', '')
            
            summary = await self.summarize(text)
            key_points = await self.extract_key_points(text)
            
            return {
                'summary': summary,
                'key_points': key_points,
                'title': paper_content.get('title', ''),
                'authors': paper_content.get('authors', []),
                'year': paper_content.get('year', '')
            }
        except Exception as e:
            raise Exception(f"Paper summarization failed: {str(e)}")
    
    async def compare_papers(self, summaries: List[Dict]) -> str:
        """Compare multiple paper summaries"""
        try:
            # Limit the number of papers to compare
            summaries = summaries[:2]  # Only compare first two papers
            
            formatted_summaries = self._format_summaries(summaries)
            prompt = f"""
            Compare these two research papers in 2-3 sentences:
            
            {formatted_summaries}
            
            Focus on:
            1. Similarities in findings
            2. Key differences
            """
            # Use a simpler approach with Ollama and add timeout
            try:
                response = await asyncio.wait_for(
                    self._llm.agenerate([prompt]),
                    timeout=30
                )
                return str(response.generations[0][0].text)
            except asyncio.TimeoutError:
                return "Comparison timed out. Please try again with fewer papers."
        except Exception as e:
            raise Exception(f"Paper comparison failed: {str(e)}")
    
    def _format_summaries(self, summaries: List[Dict]) -> str:
        """Format multiple summaries for comparison"""
        formatted = []
        for i, summary in enumerate(summaries, 1):
            formatted.append(f"Paper {i}:")
            formatted.append(f"Title: {summary.get('title', 'Unknown')}")
            formatted.append(f"Summary: {summary.get('summary', 'No summary available')}")
            formatted.append("")
        return "\n".join(formatted)