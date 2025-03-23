#!/usr/bin/env python3
"""
Big Red Button - Web Server with REST API

This module implements a web server with a REST API that takes a URL and starts
an agentic system with orchestration agent to search for security issues.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Any, Optional, List
import uuid

from app.orhcestration import orchestration_agent
from utils.logging import get_logger, AgentLogger
from utils.config import WEB_HOST, WEB_PORT, validate_config

# Initialize logger
logger = get_logger("web_server")
orch_logger = AgentLogger("orchestration")

# Create FastAPI app
app = FastAPI(
    title="Big Red Button",
    description="A web server with REST API for security scanning using agentic systems",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active scans
active_scans: Dict[str, Dict[str, Any]] = {}

# Models
class ScanRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to scan for security issues")
    scan_depth: Optional[int] = Field(None, description="Maximum depth for crawling the website")
    timeout: Optional[int] = Field(None, description="Timeout in seconds for the scan")

class ScanResponse(BaseModel):
    scan_id: str = Field(..., description="Unique identifier for the scan")
    status: str = Field(..., description="Status of the scan")
    message: str = Field(..., description="Message about the scan")

class ScanStatus(BaseModel):
    scan_id: str = Field(..., description="Unique identifier for the scan")
    status: str = Field(..., description="Status of the scan")
    progress: Optional[float] = Field(None, description="Progress of the scan (0-100)")
    findings: Optional[List[Dict[str, Any]]] = Field(None, description="List of findings")
    start_time: Optional[str] = Field(None, description="Start time of the scan")
    end_time: Optional[str] = Field(None, description="End time of the scan")

# Validate configuration on startup
@app.on_event("startup")
def startup_event():
    error = validate_config()
    if error:
        logger.error(f"Configuration error: {error}")
        raise RuntimeError(f"Configuration error: {error}")
    logger.info("Web server started successfully")

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Big Red Button API", "status": "running"}

@app.post("/scan", response_model=ScanResponse)
async def start_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks):
    # Generate a unique scan ID
    scan_id = str(uuid.uuid4())
    
    # Log the scan request
    logger.info(f"Received scan request for {scan_request.url} with ID {scan_id}")
    orch_logger.log_agent_action(
        "scan_requested", 
        {"url": str(scan_request.url), "scan_id": scan_id}
    )
    
    # Initialize scan status
    active_scans[scan_id] = {
        "status": "initializing",
        "url": str(scan_request.url),
        "progress": 0,
        "findings": []
    }
    
    # Start the scan in the background
    background_tasks.add_task(run_scan, scan_id, scan_request)
    
    return ScanResponse(
        scan_id=scan_id,
        status="initializing",
        message=f"Scan initiated for {scan_request.url}"
    )

@app.get("/scan/{scan_id}", response_model=ScanStatus)
async def get_scan_status(scan_id: str):
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail=f"Scan with ID {scan_id} not found")
    
    scan_data = active_scans[scan_id]
    
    return ScanStatus(
        scan_id=scan_id,
        status=scan_data["status"],
        progress=scan_data.get("progress"),
        findings=scan_data.get("findings"),
        start_time=scan_data.get("start_time"),
        end_time=scan_data.get("end_time")
    )

@app.get("/scans")
async def list_scans():
    return {"scans": active_scans}

# Background scan function
async def run_scan(scan_id: str, scan_request: ScanRequest):
    try:
        # Update scan status
        active_scans[scan_id]["status"] = "running"
        active_scans[scan_id]["start_time"] = asyncio.get_event_loop().time()
        
        # Log scan start
        logger.info(f"Starting scan {scan_id} for {scan_request.url}")
        orch_logger.log_agent_action(
            "scan_started", 
            {"url": str(scan_request.url), "scan_id": scan_id}
        )
        
        # Run the orchestration agent
        # This is where we would integrate with the agent system
        # For now, we'll simulate the scan with a delay
        await simulate_scan(scan_id, scan_request)
        
        # Update scan status to completed
        active_scans[scan_id]["status"] = "completed"
        active_scans[scan_id]["progress"] = 100
        active_scans[scan_id]["end_time"] = asyncio.get_event_loop().time()
        
        # Log scan completion
        logger.info(f"Completed scan {scan_id} for {scan_request.url}")
        orch_logger.log_agent_action(
            "scan_completed", 
            {"url": str(scan_request.url), "scan_id": scan_id, "findings_count": len(active_scans[scan_id]["findings"])}
        )
        
    except Exception as e:
        # Update scan status to failed
        active_scans[scan_id]["status"] = "failed"
        active_scans[scan_id]["error"] = str(e)
        active_scans[scan_id]["end_time"] = asyncio.get_event_loop().time()
        
        # Log scan failure
        logger.error(f"Scan {scan_id} failed: {str(e)}")
        orch_logger.log_agent_action(
            "scan_failed", 
            {"url": str(scan_request.url), "scan_id": scan_id, "error": str(e)}
        )

# Temporary function to simulate a scan while we integrate with the agent system
async def simulate_scan(scan_id: str, scan_request: ScanRequest):
    # In a real implementation, this would use the orchestration_agent to perform the scan
    # For now, we'll simulate progress updates and some findings
    
    # Simulate scanning progress
    for i in range(1, 11):
        await asyncio.sleep(1)  # Simulate work being done
        active_scans[scan_id]["progress"] = i * 10
        
        # Add some simulated findings
        if i == 3:
            active_scans[scan_id]["findings"].append({
                "type": "XSS",
                "severity": "HIGH",
                "url": f"{scan_request.url}/search?q=test",
                "description": "Potential Cross-Site Scripting vulnerability in search parameter"
            })
        elif i == 7:
            active_scans[scan_id]["findings"].append({
                "type": "OUTDATED_LIBRARY",
                "severity": "MEDIUM",
                "url": f"{scan_request.url}",
                "description": "Outdated jQuery library detected (version 1.8.3)"
            })

# Main function to run the server
def main():
    uvicorn.run(
        "main:app",
        host=WEB_HOST,
        port=WEB_PORT,
        reload=True
    )

if __name__ == "__main__":
    main()
