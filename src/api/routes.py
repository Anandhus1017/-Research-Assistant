from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from ..agents.research_agent import ResearchAgent
from ..agents.task_planner import TaskPlanner

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
        content = await file.read()
        results = await research_agent.analyze_paper(content)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 