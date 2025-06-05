from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import asyncio
import uuid
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Code Archeologist",
    description="Analyze GitHub repositories and uncover their architectural evolution",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo (replace with database in production)
analysis_jobs: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class AnalysisRequest(BaseModel):
    github_url: HttpUrl
    commit_count: int = 50
    include_docs: bool = True
    include_tests: bool = True

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    current_stage: str
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "AI Code Archeologist API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "analyze": "/analyze/start",
            "status": "/analyze/status/{job_id}",
            "results": "/analyze/results/{job_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/analyze/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start analyzing a GitHub repository"""
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    analysis_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "current_stage": "Initializing analysis",
        "started_at": datetime.now(),
        "github_url": str(request.github_url),
        "commit_count": request.commit_count,
        "include_docs": request.include_docs,
        "include_tests": request.include_tests,
        "results": None,
        "error_message": None
    }
    
    # Start background analysis
    background_tasks.add_task(run_analysis, job_id)
    
    logger.info(f"Started analysis job {job_id} for {request.github_url}")
    
    return AnalysisResponse(
        job_id=job_id,
        status="queued",
        message="Analysis started successfully"
    )

@app.get("/analyze/status/{job_id}", response_model=JobStatus)
async def get_analysis_status(job_id: str):
    """Get the current status of an analysis job"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    
    job_data = analysis_jobs[job_id]
    
    return JobStatus(
        job_id=job_data["job_id"],
        status=job_data["status"],
        progress=job_data["progress"],
        current_stage=job_data["current_stage"],
        started_at=job_data["started_at"],
        estimated_completion=job_data.get("estimated_completion"),
        error_message=job_data.get("error_message")
    )

@app.get("/analyze/results/{job_id}")
async def get_analysis_results(job_id: str):
    """Get the complete analysis results"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    
    job_data = analysis_jobs[job_id]
    
    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis not completed yet. Current status: {job_data['status']}"
        )
    
    return {
        "job_id": job_id,
        "status": job_data["status"],
        "results": job_data["results"],
        "completed_at": job_data.get("completed_at")
    }

@app.delete("/analyze/{job_id}")
async def cancel_analysis(job_id: str):
    """Cancel a running analysis job"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    
    job_data = analysis_jobs[job_id]
    
    if job_data["status"] in ["completed", "failed"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel completed or failed analysis"
        )
    
    analysis_jobs[job_id]["status"] = "cancelled"
    analysis_jobs[job_id]["current_stage"] = "Cancelled by user"
    
    return {"message": "Analysis cancelled successfully"}

@app.get("/analyze/jobs")
async def list_analysis_jobs(limit: int = 10):
    """List recent analysis jobs"""
    
    jobs = list(analysis_jobs.values())
    jobs.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {
        "jobs": jobs[:limit],
        "total": len(jobs)
    }

async def run_analysis(job_id: str):
    """Background task to run the actual analysis"""
    
    try:
        job_data = analysis_jobs[job_id]
        job_data["status"] = "running"
        
        # Import analysis modules
        from app.services.github_service import GitHubService
        from app.services.ai_service import AIService
        
        github_service = GitHubService()
        ai_service = AIService()
        
        # Stage 1: Clone repository
        job_data["current_stage"] = "Cloning repository"
        job_data["progress"] = 10
        
        repo_data = await github_service.clone_repository(
            job_data["github_url"],
            job_data["commit_count"]
        )
        
        # Stage 2: Analyze commits
        job_data["current_stage"] = "Analyzing commit history"
        job_data["progress"] = 30
        
        commit_analysis = await github_service.analyze_commits(repo_data)
        
        # Stage 3: AI Analysis
        job_data["current_stage"] = "Running AI analysis"
        job_data["progress"] = 50
        
        code_analysis = await ai_service.analyze_codebase(repo_data, commit_analysis)
        
        # Stage 4: Generate insights
        job_data["current_stage"] = "Generating insights"
        job_data["progress"] = 70
        
        insights = await ai_service.generate_insights(code_analysis)
        
        # Stage 5: Create visualizations
        job_data["current_stage"] = "Creating visualizations"
        job_data["progress"] = 90
        
        visualizations = await ai_service.create_visualizations(insights)
        
        # Complete analysis
        job_data["status"] = "completed"
        job_data["current_stage"] = "Analysis complete"
        job_data["progress"] = 100
        job_data["completed_at"] = datetime.now()
        job_data["results"] = {
            "repository_info": repo_data["info"],
            "commit_analysis": commit_analysis,
            "code_analysis": code_analysis,
            "insights": insights,
            "visualizations": visualizations,
            "summary": {
                "total_commits_analyzed": len(commit_analysis["commits"]),
                "files_analyzed": code_analysis["total_files"],
                "languages_detected": code_analysis["languages"],
                "analysis_duration": str(datetime.now() - job_data["started_at"])
            }
        }
        
        logger.info(f"Analysis job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed: {str(e)}")
        job_data["status"] = "failed"
        job_data["current_stage"] = "Analysis failed"
        job_data["error_message"] = str(e)
        job_data["completed_at"] = datetime.now()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)