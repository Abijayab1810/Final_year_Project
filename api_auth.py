"""
FastAPI REST API with User Authentication
Provides secure endpoints for abandoned luggage detection across multiple users
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime
import json

from forensic_db import (
    log_abandoned_bag,
    get_all_abandoned_bags,
    get_statistics,
    get_bags_by_date_range,
    EVIDENCE_FOLDER
)
from users_db import verify_token, register_user, authenticate_user, create_access_token, get_user_profile
from cameras_db import (
    add_camera,
    get_user_cameras,
    get_camera_by_id,
    delete_camera,
    update_camera,
    test_camera_connection
)

# ==========================================
# 🚀 FASTAPI INITIALIZATION
# ==========================================
app = FastAPI(
    title="Luggage Detection API",
    description="Multi-user abandoned luggage detection platform",
    version="2.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 📋 DATA MODELS
# ==========================================
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class LogDetectionRequest(BaseModel):
    track_id: int
    duration_seconds: int
    camera_id: str
    confidence: float
    frame_width: int
    frame_height: int
    bag_x1: int
    bag_y1: int
    bag_x2: int
    bag_y2: int

class DetectionResponse(BaseModel):
    track_id: int
    timestamp: str
    duration_seconds: int
    camera_id: str
    confidence_score: float
    image_filepath: Optional[str]
    actions_taken: Optional[str]

class AddCameraRequest(BaseModel):
    camera_name: str
    rtsp_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    camera_type: str = "RTSP"
    port: int = 554

class UpdateCameraRequest(BaseModel):
    camera_name: Optional[str] = None
    rtsp_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class CameraResponse(BaseModel):
    id: int
    camera_name: str
    camera_type: str
    rtsp_url: str
    connection_status: str
    is_active: bool
    created_at: str

# ==========================================
# 🔐 AUTHENTICATION DEPENDENCY
# ==========================================
async def get_current_user(authorization: Optional[str] = None):
    """
    Dependency to verify JWT token and extract user_id
    Usage: @app.post("/endpoint")
           async def my_endpoint(user: dict = Depends(get_current_user)):
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_data

# ==========================================
# 👤 AUTHENTICATION ENDPOINTS
# ==========================================

@app.post("/auth/register", tags=["Authentication"])
async def register(user: UserRegister):
    """Register a new user account"""
    result = register_user(
        username=user.username,
        email=user.email,
        password=user.password,
        full_name=user.full_name
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "status": "success",
        "message": "User registered successfully",
        "user_id": result.get("user_id")
    }

@app.post("/auth/login", tags=["Authentication"])
async def login(user: UserLogin):
    """Login with username and password"""
    user_data = authenticate_user(user.username, user.password)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({
        "sub": user.username,
        "user_id": user_data["id"]
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_data["id"],
        "username": user_data["username"]
    }

@app.get("/auth/profile", tags=["Authentication"])
async def get_profile(user: dict = Depends(get_current_user)):
    """Get current user profile"""
    profile = get_user_profile(user["user_id"])
    
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": profile["id"],
        "username": profile["username"],
        "email": profile["email"],
        "full_name": profile.get("full_name"),
        "created_at": profile.get("created_at")
    }

# ==========================================
# � CAMERA ENDPOINTS
# ==========================================

@app.post("/cameras/add", tags=["Cameras"])
async def add_camera_endpoint(
    request: AddCameraRequest,
    user: dict = Depends(get_current_user)
):
    """Add a new CCTV camera"""
    result = add_camera(
        user_id=user["user_id"],
        camera_name=request.camera_name,
        rtsp_url=request.rtsp_url,
        username=request.username,
        password=request.password,
        camera_type=request.camera_type,
        port=request.port
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "status": "success",
        "camera_id": result["camera_id"],
        "message": result["message"]
    }

@app.get("/cameras/list", tags=["Cameras"])
async def list_cameras(
    user: dict = Depends(get_current_user),
    active_only: bool = False
):
    """Get all cameras for current user"""
    try:
        cameras = get_user_cameras(user["user_id"], active_only=active_only)
        
        return {
            "total": len(cameras),
            "cameras": cameras
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cameras: {str(e)}")

@app.get("/cameras/{camera_id}", tags=["Cameras"])
async def get_camera(
    camera_id: int,
    user: dict = Depends(get_current_user)
):
    """Get specific camera details"""
    try:
        camera = get_camera_by_id(camera_id, user["user_id"])
        
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return camera
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving camera: {str(e)}")

@app.put("/cameras/{camera_id}", tags=["Cameras"])
async def update_camera_endpoint(
    camera_id: int,
    request: UpdateCameraRequest,
    user: dict = Depends(get_current_user)
):
    """Update camera details"""
    update_data = {}
    
    if request.camera_name:
        update_data['camera_name'] = request.camera_name
    if request.rtsp_url:
        update_data['rtsp_url'] = request.rtsp_url
    if request.username is not None:
        update_data['username'] = request.username
    if request.password is not None:
        update_data['password'] = request.password
    if request.is_active is not None:
        update_data['is_active'] = request.is_active
    
    result = update_camera(camera_id, user["user_id"], **update_data)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.delete("/cameras/{camera_id}", tags=["Cameras"])
async def delete_camera_endpoint(
    camera_id: int,
    user: dict = Depends(get_current_user)
):
    """Delete a camera"""
    result = delete_camera(camera_id, user["user_id"])
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/cameras/{camera_id}/test", tags=["Cameras"])
async def test_camera_connection_endpoint(
    camera_id: int,
    user: dict = Depends(get_current_user)
):
    """Test connection to a camera"""
    result = test_camera_connection(camera_id, user["user_id"])
    
    return result

# ==========================================
# �📊 DETECTION ENDPOINTS
# ==========================================

@app.post("/detections/log", tags=["Detections"])
async def log_detection(
    request: LogDetectionRequest,
    user: dict = Depends(get_current_user)
):
    """Log a detected abandoned luggage incident"""
    try:
        log_abandoned_bag(
            user_id=user["user_id"],
            track_id=request.track_id,
            duration_seconds=request.duration_seconds,
            image_filepath=None,
            camera_id=request.camera_id,
            confidence=request.confidence,
            frame_dims=(request.frame_width, request.frame_height),
            bag_bbox=(request.bag_x1, request.bag_y1, request.bag_x2, request.bag_y2)
        )
        
        return {
            "status": "success",
            "message": "Detection logged successfully",
            "track_id": request.track_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging detection: {str(e)}")

@app.get("/detections/all", tags=["Detections"])
async def get_detections(
    user: dict = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all abandoned luggage detections for current user"""
    try:
        df = get_all_abandoned_bags(user_id=user["user_id"])
        
        if len(df) == 0:
            return {
                "total": 0,
                "detections": []
            }
        
        # Apply pagination
        df_paginated = df.iloc[offset:offset+limit]
        
        detections = []
        for _, row in df_paginated.iterrows():
            detections.append({
                "track_id": int(row['track_id']),
                "timestamp": row['timestamp'],
                "duration_seconds": int(row['duration_seconds']),
                "camera_id": row['camera_id'],
                "confidence_score": float(row['confidence_score']),
                "image_filepath": row['image_filepath'],
                "frame_width": int(row['frame_width']),
                "frame_height": int(row['frame_height']),
                "bag_bbox": {
                    "x1": int(row['bag_x1']),
                    "y1": int(row['bag_y1']),
                    "x2": int(row['bag_x2']),
                    "y2": int(row['bag_y2'])
                },
                "actions_taken": row['actions_taken']
            })
        
        return {
            "total": len(df),
            "count": len(detections),
            "offset": offset,
            "limit": limit,
            "detections": detections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving detections: {str(e)}")

@app.get("/detections/by-date-range", tags=["Detections"])
async def get_detections_by_date(
    start_date: str,  # Format: YYYY-MM-DD
    end_date: str,    # Format: YYYY-MM-DD
    user: dict = Depends(get_current_user)
):
    """Get detections within a date range"""
    try:
        df = get_bags_by_date_range(start_date, end_date, user_id=user["user_id"])
        
        detections = []
        for _, row in df.iterrows():
            detections.append({
                "track_id": int(row['track_id']),
                "timestamp": row['timestamp'],
                "duration_seconds": int(row['duration_seconds']),
                "camera_id": row['camera_id'],
                "confidence_score": float(row['confidence_score'])
            })
        
        return {
            "date_range": f"{start_date} to {end_date}",
            "total_detections": len(detections),
            "detections": detections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving detections: {str(e)}")

@app.get("/detections/{track_id}", tags=["Detections"])
async def get_detection_by_id(
    track_id: int,
    user: dict = Depends(get_current_user)
):
    """Get specific detection by track ID"""
    try:
        df = get_all_abandoned_bags(user_id=user["user_id"])
        detection = df[df['track_id'] == track_id]
        
        if len(detection) == 0:
            raise HTTPException(status_code=404, detail=f"Detection {track_id} not found")
        
        row = detection.iloc[0]
        return {
            "track_id": int(row['track_id']),
            "timestamp": row['timestamp'],
            "duration_seconds": int(row['duration_seconds']),
            "camera_id": row['camera_id'],
            "confidence_score": float(row['confidence_score']),
            "image_filepath": row['image_filepath'],
            "actions_taken": row['actions_taken']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving detection: {str(e)}")

# ==========================================
# 📈 STATISTICS ENDPOINTS
# ==========================================

@app.get("/statistics/summary", tags=["Statistics"])
async def get_summary_statistics(user: dict = Depends(get_current_user)):
    """Get statistics summary for current user"""
    try:
        df = get_all_abandoned_bags(user_id=user["user_id"])
        
        if len(df) == 0:
            return {
                "total_detections": 0,
                "avg_duration": 0,
                "max_duration": 0,
                "min_duration": 0,
                "avg_confidence": 0,
                "unique_cameras": 0
            }
        
        return {
            "total_detections": len(df),
            "avg_duration": float(df['duration_seconds'].mean()),
            "max_duration": int(df['duration_seconds'].max()),
            "min_duration": int(df['duration_seconds'].min()),
            "avg_confidence": float(df['confidence_score'].mean()),
            "unique_cameras": df['camera_id'].nunique(),
            "date_range": {
                "first_detection": df['timestamp'].min(),
                "last_detection": df['timestamp'].max()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@app.get("/statistics/by-camera", tags=["Statistics"])
async def get_statistics_by_camera(user: dict = Depends(get_current_user)):
    """Get statistics grouped by camera"""
    try:
        df = get_all_abandoned_bags(user_id=user["user_id"])
        
        if len(df) == 0:
            return {"cameras": []}
        
        camera_stats = []
        for camera_id in df['camera_id'].unique():
            camera_df = df[df['camera_id'] == camera_id]
            camera_stats.append({
                "camera_id": camera_id,
                "detection_count": len(camera_df),
                "avg_duration": float(camera_df['duration_seconds'].mean()),
                "avg_confidence": float(camera_df['confidence_score'].mean())
            })
        
        return {
            "cameras": camera_stats,
            "total_cameras": len(camera_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving camera statistics: {str(e)}")

# ==========================================
# 📥 EXPORT ENDPOINTS
# ==========================================

@app.get("/export/csv", tags=["Export"])
async def export_csv(user: dict = Depends(get_current_user)):
    """Export all detections as CSV"""
    try:
        df = get_all_abandoned_bags(user_id=user["user_id"])
        
        if len(df) == 0:
            return {"error": "No data to export"}
        
        filename = f"detections_{user['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(EVIDENCE_FOLDER, filename)
        
        df.to_csv(filepath, index=False)
        
        return FileResponse(
            filepath,
            media_type="text/csv",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting CSV: {str(e)}")

@app.get("/export/json", tags=["Export"])
async def export_json(user: dict = Depends(get_current_user)):
    """Export all detections as JSON"""
    try:
        df = get_all_abandoned_bags(user_id=user["user_id"])
        
        if len(df) == 0:
            return {"detections": []}
        
        detections = []
        for _, row in df.iterrows():
            detections.append(row.to_dict())
        
        return {
            "user_id": user["user_id"],
            "export_timestamp": datetime.now().isoformat(),
            "total_detections": len(detections),
            "detections": detections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting JSON: {str(e)}")

# ==========================================
# 🖼️ EVIDENCE ENDPOINTS
# ==========================================

@app.get("/evidence/{track_id}", tags=["Evidence"])
async def get_evidence_image(
    track_id: int,
    user: dict = Depends(get_current_user)
):
    """Get evidence image for a detection"""
    try:
        df = get_all_abandoned_bags(user_id=user["user_id"])
        detection = df[df['track_id'] == track_id]
        
        if len(detection) == 0:
            raise HTTPException(status_code=404, detail="Detection not found")
        
        image_path = detection.iloc[0]['image_filepath']
        
        if not image_path or not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Evidence image not found")
        
        return FileResponse(image_path, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving evidence: {str(e)}")

# ==========================================
# 🏥 HEALTH CHECK ENDPOINTS
# ==========================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/health/auth", tags=["Health"])
async def health_check_auth(user: dict = Depends(get_current_user)):
    """Check API health with authentication"""
    return {
        "status": "authenticated",
        "user_id": user["user_id"],
        "timestamp": datetime.now().isoformat()
    }

# ==========================================
# 📖 ROOT DOCUMENTATION
# ==========================================

@app.get("/", tags=["Documentation"])
async def root():
    """API Documentation and Information"""
    return {
        "name": "Abandoned Luggage Detection API",
        "version": "2.0.0",
        "description": "Multi-user platform for detecting and tracking abandoned luggage",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "authentication": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "profile": "GET /auth/profile"
            },
            "cameras": {
                "add": "POST /cameras/add",
                "list": "GET /cameras/list",
                "get": "GET /cameras/{camera_id}",
                "update": "PUT /cameras/{camera_id}",
                "delete": "DELETE /cameras/{camera_id}",
                "test": "POST /cameras/{camera_id}/test"
            },
            "detections": {
                "log": "POST /detections/log",
                "get_all": "GET /detections/all",
                "by_date_range": "GET /detections/by-date-range",
                "get_by_id": "GET /detections/{track_id}"
            },
            "statistics": {
                "summary": "GET /statistics/summary",
                "by_camera": "GET /statistics/by-camera"
            },
            "export": {
                "csv": "GET /export/csv",
                "json": "GET /export/json"
            },
            "evidence": {
                "image": "GET /evidence/{track_id}"
            },
            "health": {
                "check": "GET /health",
                "check_auth": "GET /health/auth"
            }
        },
        "authentication": {
            "method": "Bearer Token (JWT)",
            "header": "Authorization: Bearer <token>",
            "token_expiration": "24 hours"
        }
    }

# ==========================================
# 🚀 MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
