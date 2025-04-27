from PyPDF2 import PdfReader
from typing import Dict
import re
import io
import logging
from langchain.tools import BaseTool
from pydantic import PrivateAttr
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParserTool(BaseTool):
    name: str = "pdf_parser"
    description: str = "Parse PDF content and extract structured information including title, abstract, sections, figures, and references"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Compile regex patterns once
        object.__setattr__(self, '_figures_pattern', re.compile(r'Figure \d+:.*?(?=Figure \d+:|$)', re.DOTALL))
        object.__setattr__(self, '_references_pattern', re.compile(r'References.*', re.DOTALL))
        object.__setattr__(self, '_section_patterns', {
            'Abstract': re.compile(r'Abstract.*?(?=Introduction|$)', re.DOTALL | re.IGNORECASE),
            'Introduction': re.compile(r'Introduction.*?(?=Methods|Methodology|$)', re.DOTALL | re.IGNORECASE),
            'Methods': re.compile(r'Methods.*?(?=Results|$)', re.DOTALL | re.IGNORECASE),
            'Results': re.compile(r'Results.*?(?=Discussion|$)', re.DOTALL | re.IGNORECASE),
            'Discussion': re.compile(r'Discussion.*?(?=Conclusion|References|$)', re.DOTALL | re.IGNORECASE)
        })
    
    def parse_pdf(self, pdf_content: bytes) -> Dict:
        """Public method to parse PDF content"""
        return self._run(pdf_content)
    
    def _run(self, pdf_content: bytes) -> Dict:
        """Parse PDF content and extract structured information"""
        start_time = time.time()
        logger.info("🔄 Starting PDF parsing...")
        
        pdf_file = io.BytesIO(pdf_content)
        reader = PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        # Extract text content page by page
        logger.info(f"📄 Processing {total_pages} pages...")
        full_text = ""
        for i, page in enumerate(reader.pages, 1):
            page_start = time.time()
            logger.info(f"📑 Processing page {i}/{total_pages}...")
            full_text += page.extract_text() + "\n"
            logger.info(f"✅ Page {i} processed in {time.time() - page_start:.2f} seconds")
        
        logger.info("🔍 Extracting sections...")
        # Extract sections
        sections = self._extract_sections(full_text)
        logger.info("✅ Sections extracted")
        
        logger.info("🖼️ Extracting figures...")
        # Extract figures
        figures = self._figures_pattern.findall(full_text)
        logger.info(f"✅ Found {len(figures)} figures")
        
        logger.info("📚 Extracting references...")
        # Extract references
        references_match = self._references_pattern.search(full_text)
        references = references_match.group() if references_match else ""
        logger.info("✅ References extracted")
        
        total_time = time.time() - start_time
        logger.info(f"✨ PDF parsing completed in {total_time:.2f} seconds")
        
        # Ensure all values are strings
        return {
            'title': str(self._extract_title(full_text)),
            'abstract': str(sections.get('Abstract', '')),
            'introduction': str(sections.get('Introduction', '')),
            'methods': str(sections.get('Methods', '')),
            'results': str(sections.get('Results', '')),
            'discussion': str(sections.get('Discussion', '')),
            'figures': '\n'.join(str(fig) for fig in figures),
            'references': str(references)
        }
    
    async def _arun(self, pdf_content: bytes) -> Dict:
        """Async version of parse_pdf"""
        return self._run(pdf_content)
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from the paper"""
        sections = {}
        for section, pattern in self._section_patterns.items():
            match = pattern.search(text)
            if match:
                sections[section] = match.group().strip()
        return sections
    
    def _extract_title(self, text: str) -> str:
        """Extract paper title"""
        first_line = text.split('\n')[0]
        return first_line.strip()