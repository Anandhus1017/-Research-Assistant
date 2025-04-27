from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from ..agents.research_agent import ResearchAgent
from ..agents.task_planner import TaskPlanner
import logging
import asyncio
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
research_agent = ResearchAgent()
task_planner = TaskPlanner()

class ResearchRequest(BaseModel):
    topic: str
    max_papers: int = 10

@router.post("/research")
async def conduct_research(request: ResearchRequest):
    """Conduct research on a given topic"""
    try:
        # Create research plan
        plan = await task_planner.create_plan(request.topic)
        
        # Execute research
        results = await research_agent.research(request.topic)
        
        return {
            "plan": plan,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-paper")
async def upload_paper(file: UploadFile = File(...)):
    """Upload and analyze a research paper"""
    try:
        logger.info(f"Starting paper upload for file: {file.filename}")
        
        # Read file content with timeout
        try:
            content = await asyncio.wait_for(file.read(), timeout=30.0)
            logger.info(f"File read successfully, size: {len(content)} bytes")
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="File read timeout")
        
        # Parse and analyze the paper with timeout
        try:
            logger.info("Starting paper analysis...")
            results = await asyncio.wait_for(
                research_agent.analyze_paper(content),
                timeout=300.0  # 5 minutes timeout
            )
            logger.info("Paper analysis completed successfully")
            return JSONResponse(content=results)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Paper analysis timeout")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error during paper upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Paper analysis failed: {str(e)}"
        ) 