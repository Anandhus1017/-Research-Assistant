from fastapi import FastAPI, UploadFile, File, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.agents.research_agent import ResearchAgent
from src.tools.pdf_parser import PDFParserTool
from src.tools.semantic_search import SemanticSearchTool
from src.tools.summarizer import SummarizerTool
from src.tools.arxiv_search import ArxivSearchTool
from src.tools.scholar_search import ScholarSearchTool
from src.tools.vector_store import VectorStore
import os
import logging
import time
import asyncio
from typing import Dict
import uuid
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS with specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]  # Expose all headers
)

# Add middleware to handle CORS headers
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Store processing tasks
processing_tasks: Dict[str, Dict] = {}

# Initialize tools
pdf_parser = PDFParserTool()
semantic_search = SemanticSearchTool()
summarizer = SummarizerTool()
arxiv_search = ArxivSearchTool()
scholar_search = ScholarSearchTool()
vector_store = VectorStore()

# Initialize research agent
research_agent = ResearchAgent(
    pdf_parser=pdf_parser,
    semantic_search=semantic_search,
    summarizer=summarizer,
    arxiv_search=arxiv_search,
    scholar_search=scholar_search,
    vector_store=vector_store
)

async def process_paper(task_id: str, content: bytes):
    try:
        processing_tasks[task_id]["status"] = "processing"
        logger.info(f"🔄 Starting processing for task {task_id}")
        
        # Analyze the paper
        result = await research_agent.analyze_paper(content)
        
        processing_tasks[task_id]["status"] = "completed"
        processing_tasks[task_id]["result"] = result
        logger.info(f"✅ Processing completed for task {task_id}")
        
    except Exception as e:
        error_msg = f"❌ Error processing task {task_id}: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        processing_tasks[task_id]["status"] = "error"
        processing_tasks[task_id]["error"] = str(e)

@app.post("/api/v1/upload-paper")
async def upload_paper(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Initialize task status
        processing_tasks[task_id] = {
            "status": "pending",
            "start_time": time.time()
        }
        
        # Start processing in background
        asyncio.create_task(process_paper(task_id, content))
        
        return JSONResponse(
            content={
                "task_id": task_id,
                "status": "processing",
                "message": "Paper processing started"
            }
        )
    except Exception as e:
        logger.error(f"❌ Error starting paper processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/task-status/{task_id}")
async def get_task_status(task_id: str):
    try:
        if task_id not in processing_tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = processing_tasks[task_id]
        
        if task["status"] == "completed":
            return JSONResponse(content={
                "status": "completed",
                "result": task["result"]
            })
        elif task["status"] == "error":
            return JSONResponse(content={
                "status": "error",
                "error": task["error"]
            })
        else:
            elapsed_time = time.time() - task["start_time"]
            return JSONResponse(content={
                "status": "processing",
                "elapsed_time": round(elapsed_time, 2),
                "stage": task.get("current_stage", "unknown")
            })
    except Exception as e:
        logger.error(f"Error checking task status: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",  # Changed to allow external connections
        port=9000,
        timeout_keep_alive=300,
        log_level="info"
    )