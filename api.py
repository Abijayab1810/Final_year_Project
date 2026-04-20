"""
FastAPI REST API for Abandoned Luggage Detection System
Provides endpoints for integrating with external systems and mobile apps
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import cv2
import numpy as np
from forensic_db import (
    get_all_abandoned_bags, get_statistics, get_bags_by_date_range, 
    get_bags_by_camera, log_abandoned_bag, clear_all_records,
    export_to_csv, get_daily_stats, get_camera_stats
)
import io

# ==========================================
# FASTAPI INITIALIZATION
# ==========================================
app = FastAPI(
    title="Abandoned Luggage Detection API",
    description="Professional REST API for abandoned luggage detection system",
    version="1.0.0"
)

# ==========================================
# CORS CONFIGURATION (Allow external access)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class DetectionRecord(BaseModel):
    """Schema for a detection record"""
    id: int
    track_id: int
    timestamp: str
    duration_seconds: int
    camera_id: str
    confidence_score: float
    frame_width: int
    frame_height: int
    bag_x1: int
    bag_y1: int
    bag_x2: int
    bag_y2: int
    image_filepath: Optional[str] = None
    actions_taken: Optional[str] = None


class StatisticsResponse(BaseModel):
    """Schema for statistics response"""
    total_detections: int
    average_duration_seconds: float
    max_duration_seconds: int
    average_confidence: float


class AlertRequest(BaseModel):
    """Schema for manual alert logging"""
    track_id: int
    duration_seconds: int
    camera_id: str
    confidence: float


class CameraInfo(BaseModel):
    """Schema for camera information"""
    camera_id: str
    name: str
    location: str
    status: str = "active"


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: str
    version: str


# ==========================================
# HEALTH CHECK ENDPOINTS
# ==========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# ==========================================
# DETECTIONS ENDPOINTS
# ==========================================

@app.get("/api/detections", response_model=List[DetectionRecord])
async def get_detections(
    limit: int = Query(100, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip")
):
    """
    Get all abandoned luggage detections
    
    Query Parameters:
    - limit: Maximum number of records (default: 100)
    - offset: Skip N records (default: 0)
    """
    try:
        df = get_all_abandoned_bags()
        
        if len(df) == 0:
            return []
        
        # Apply pagination
        df = df.iloc[offset:offset+limit]
        
        records = []
        for _, row in df.iterrows():
            records.append(DetectionRecord(
                id=int(row.get('id', 0)),
                track_id=int(row.get('track_id', 0)),
                timestamp=str(row.get('timestamp', '')),
                duration_seconds=int(row.get('duration_seconds', 0)),
                camera_id=str(row.get('camera_id', '')),
                confidence_score=float(row.get('confidence_score', 0)),
                frame_width=int(row.get('frame_width', 0)),
                frame_height=int(row.get('frame_height', 0)),
                bag_x1=int(row.get('bag_x1', 0)),
                bag_y1=int(row.get('bag_y1', 0)),
                bag_x2=int(row.get('bag_x2', 0)),
                bag_y2=int(row.get('bag_y2', 0)),
                image_filepath=row.get('image_filepath'),
                actions_taken=row.get('actions_taken')
            ))
        
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching detections: {str(e)}")


@app.get("/api/detections/camera/{camera_id}", response_model=List[DetectionRecord])
async def get_detections_by_camera(
    camera_id: str,
    limit: int = Query(50, description="Number of records to return")
):
    """
    Get detections for a specific camera
    
    Path Parameters:
    - camera_id: Camera identifier (e.g., 'Camera-001')
    
    Query Parameters:
    - limit: Maximum number of records (default: 50)
    """
    try:
        df = get_bags_by_camera(camera_id)
        
        if len(df) == 0:
            return []
        
        df = df.head(limit)
        
        records = []
        for _, row in df.iterrows():
            records.append(DetectionRecord(
                id=int(row.get('id', 0)),
                track_id=int(row.get('track_id', 0)),
                timestamp=str(row.get('timestamp', '')),
                duration_seconds=int(row.get('duration_seconds', 0)),
                camera_id=str(row.get('camera_id', '')),
                confidence_score=float(row.get('confidence_score', 0)),
                frame_width=int(row.get('frame_width', 0)),
                frame_height=int(row.get('frame_height', 0)),
                bag_x1=int(row.get('bag_x1', 0)),
                bag_y1=int(row.get('bag_y1', 0)),
                bag_x2=int(row.get('bag_x2', 0)),
                bag_y2=int(row.get('bag_y2', 0)),
                image_filepath=row.get('image_filepath'),
                actions_taken=row.get('actions_taken')
            ))
        
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching camera detections: {str(e)}")


@app.get("/api/detections/date-range", response_model=List[DetectionRecord])
async def get_detections_by_date(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get detections within a date range
    
    Query Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    """
    try:
        df = get_bags_by_date_range(start_date, end_date)
        
        if len(df) == 0:
            return []
        
        records = []
        for _, row in df.iterrows():
            records.append(DetectionRecord(
                id=int(row.get('id', 0)),
                track_id=int(row.get('track_id', 0)),
                timestamp=str(row.get('timestamp', '')),
                duration_seconds=int(row.get('duration_seconds', 0)),
                camera_id=str(row.get('camera_id', '')),
                confidence_score=float(row.get('confidence_score', 0)),
                frame_width=int(row.get('frame_width', 0)),
                frame_height=int(row.get('frame_height', 0)),
                bag_x1=int(row.get('bag_x1', 0)),
                bag_y1=int(row.get('bag_y1', 0)),
                bag_x2=int(row.get('bag_x2', 0)),
                bag_y2=int(row.get('bag_y2', 0)),
                image_filepath=row.get('image_filepath'),
                actions_taken=row.get('actions_taken')
            ))
        
        return records
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error filtering by date: {str(e)}")


@app.post("/api/detections/log")
async def log_detection(alert: AlertRequest):
    """
    Manually log a detection alert
    
    Request Body:
    ```json
    {
        "track_id": 123,
        "duration_seconds": 30,
        "camera_id": "Camera-001",
        "confidence": 0.95
    }
    ```
    """
    try:
        log_abandoned_bag(
            track_id=alert.track_id,
            duration_seconds=alert.duration_seconds,
            image_filepath="",
            camera_id=alert.camera_id,
            confidence=alert.confidence,
            frame_dims=(1920, 1080),
            bag_bbox=(0, 0, 0, 0)
        )
        return {"status": "success", "message": "Detection logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging detection: {str(e)}")


# ==========================================
# STATISTICS ENDPOINTS
# ==========================================

@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_system_statistics():
    """
    Get overall system statistics
    
    Returns:
    - total_detections: Total number of detections
    - average_duration_seconds: Average abandonment duration
    - max_duration_seconds: Maximum abandonment duration
    - average_confidence: Average confidence score
    """
    try:
        stats = get_statistics()
        return StatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@app.get("/api/statistics/daily")
async def get_daily_statistics(days: int = Query(7, description="Number of days to analyze")):
    """
    Get daily statistics for the past N days
    
    Query Parameters:
    - days: Number of days to look back (default: 7)
    """
    try:
        df = get_daily_stats(days)
        return df.to_dict(orient="records") if len(df) > 0 else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting daily stats: {str(e)}")


@app.get("/api/statistics/by-camera")
async def get_camera_statistics():
    """
    Get statistics grouped by camera
    
    Returns per-camera metrics:
    - detections: Number of detections
    - avg_duration: Average abandonment duration
    - max_duration: Maximum abandonment duration
    - avg_confidence: Average confidence
    """
    try:
        df = get_camera_stats()
        return df.to_dict(orient="records") if len(df) > 0 else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting camera stats: {str(e)}")


# ==========================================
# EXPORT ENDPOINTS
# ==========================================

@app.get("/api/export/csv")
async def export_csv():
    """
    Export all detections to CSV file
    
    Returns a CSV file for download
    """
    try:
        filename = export_to_csv()
        if filename:
            return {
                "status": "success",
                "filename": filename,
                "message": "Export completed"
            }
        else:
            raise HTTPException(status_code=404, detail="No data to export")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


# ==========================================
# DATABASE MANAGEMENT ENDPOINTS
# ==========================================

@app.delete("/api/records/clear")
async def clear_records(confirm: bool = Query(False, description="Confirmation to delete all records")):
    """
    Clear all records from database (requires confirmation)
    
    Query Parameters:
    - confirm: Must be True to proceed
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must set confirm=true to clear all records"
        )
    
    try:
        clear_all_records()
        return {"status": "success", "message": "All records cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing records: {str(e)}")


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
async def root():
    """API root endpoint with documentation links"""
    return {
        "message": "Abandoned Luggage Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "base_url": "/api"
    }


# ==========================================
# ERROR HANDLING
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
