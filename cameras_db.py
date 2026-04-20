"""
Camera Management Database Module
Handles CCTV camera registration, authentication, and connection details
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict
import re

# Database path
DB_PATH = "cameras.db"

# ==========================================
# 🎥 DATABASE INITIALIZATION
# ==========================================

def init_cameras_database():
    """Initialize cameras database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create cameras table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cameras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        camera_name TEXT NOT NULL,
        camera_type TEXT DEFAULT 'RTSP',
        rtsp_url TEXT NOT NULL,
        username TEXT,
        password TEXT,
        port INTEGER DEFAULT 554,
        is_active BOOLEAN DEFAULT 1,
        created_at TEXT NOT NULL,
        last_accessed TEXT,
        connection_status TEXT DEFAULT 'untested',
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, camera_name)
    );
    """)
    
    # Create index for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cameras_user_id ON cameras(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cameras_active ON cameras(is_active);")
    
    conn.commit()
    conn.close()

# ==========================================
# 📹 CAMERA MANAGEMENT FUNCTIONS
# ==========================================

def add_camera(user_id: int, camera_name: str, rtsp_url: str, 
               username: str = None, password: str = None,
               camera_type: str = "RTSP", port: int = 554) -> Dict:
    """
    Add a new camera for a user
    
    Args:
        user_id: User ID (from users table)
        camera_name: Name/label for the camera
        rtsp_url: RTSP stream URL (e.g., rtsp://192.168.1.100:554/stream)
        username: Optional camera username
        password: Optional camera password
        camera_type: Type of camera (RTSP, HTTP, USB, etc.)
        port: Port number (default 554 for RTSP)
    
    Returns:
        {"status": "success", "camera_id": id} or {"status": "error", "message": "..."}
    """
    try:
        # Validate RTSP URL format
        if not validate_rtsp_url(rtsp_url):
            return {
                "status": "error",
                "message": "Invalid RTSP URL format. Expected: rtsp://host:port/path"
            }
        
        # Check for duplicate camera name
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM cameras WHERE user_id = ? AND camera_name = ?",
            (user_id, camera_name)
        )
        
        if cursor.fetchone():
            conn.close()
            return {
                "status": "error",
                "message": f"Camera name '{camera_name}' already exists for this user"
            }
        
        # Insert new camera
        created_at = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO cameras 
        (user_id, camera_name, camera_type, rtsp_url, username, password, port, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, camera_name, camera_type, rtsp_url, username, password, port, created_at))
        
        conn.commit()
        camera_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success",
            "camera_id": camera_id,
            "message": f"Camera '{camera_name}' added successfully"
        }
    
    except sqlite3.IntegrityError as e:
        return {
            "status": "error",
            "message": f"Database integrity error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error adding camera: {str(e)}"
        }

def get_user_cameras(user_id: int, active_only: bool = False) -> List[Dict]:
    """
    Get all cameras for a user
    
    Args:
        user_id: User ID
        active_only: Only return active cameras if True
    
    Returns:
        List of camera dictionaries
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute(
                "SELECT * FROM cameras WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC",
                (user_id,)
            )
        else:
            cursor.execute(
                "SELECT * FROM cameras WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        cameras = []
        for row in rows:
            cameras.append({
                "id": row["id"],
                "camera_name": row["camera_name"],
                "camera_type": row["camera_type"],
                "rtsp_url": row["rtsp_url"],
                "username": row["username"],
                "password": row["password"],
                "port": row["port"],
                "is_active": row["is_active"],
                "created_at": row["created_at"],
                "last_accessed": row["last_accessed"],
                "connection_status": row["connection_status"]
            })
        
        return cameras
    
    except Exception as e:
        print(f"Error retrieving cameras: {str(e)}")
        return []

def get_camera_by_id(camera_id: int, user_id: int = None) -> Optional[Dict]:
    """
    Get a specific camera by ID
    
    Args:
        camera_id: Camera ID
        user_id: Optional user_id for security verification
    
    Returns:
        Camera dictionary or None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute(
                "SELECT * FROM cameras WHERE id = ? AND user_id = ?",
                (camera_id, user_id)
            )
        else:
            cursor.execute("SELECT * FROM cameras WHERE id = ?", (camera_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "camera_name": row["camera_name"],
            "camera_type": row["camera_type"],
            "rtsp_url": row["rtsp_url"],
            "username": row["username"],
            "password": row["password"],
            "port": row["port"],
            "is_active": row["is_active"],
            "created_at": row["created_at"],
            "last_accessed": row["last_accessed"],
            "connection_status": row["connection_status"]
        }
    
    except Exception as e:
        print(f"Error retrieving camera: {str(e)}")
        return None

def update_camera(camera_id: int, user_id: int, **kwargs) -> Dict:
    """
    Update camera details
    
    Args:
        camera_id: Camera ID
        user_id: User ID (for security verification)
        **kwargs: Fields to update (camera_name, rtsp_url, username, password, is_active, etc.)
    
    Returns:
        {"status": "success/error", "message": "..."}
    """
    try:
        # Verify camera belongs to user
        camera = get_camera_by_id(camera_id, user_id)
        if not camera:
            return {
                "status": "error",
                "message": "Camera not found or doesn't belong to this user"
            }
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Build update query dynamically
        allowed_fields = {
            'camera_name', 'rtsp_url', 'username', 'password', 
            'port', 'is_active', 'connection_status'
        }
        
        updates = {}
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates[key] = value
        
        if not updates:
            conn.close()
            return {
                "status": "error",
                "message": "No valid fields to update"
            }
        
        # If RTSP URL is being updated, validate it
        if 'rtsp_url' in updates and not validate_rtsp_url(updates['rtsp_url']):
            conn.close()
            return {
                "status": "error",
                "message": "Invalid RTSP URL format"
            }
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [camera_id, user_id]
        
        cursor.execute(
            f"UPDATE cameras SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Camera updated successfully"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating camera: {str(e)}"
        }

def delete_camera(camera_id: int, user_id: int) -> Dict:
    """
    Delete a camera
    
    Args:
        camera_id: Camera ID
        user_id: User ID (for security verification)
    
    Returns:
        {"status": "success/error", "message": "..."}
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verify camera belongs to user before deleting
        cursor.execute(
            "SELECT id FROM cameras WHERE id = ? AND user_id = ?",
            (camera_id, user_id)
        )
        
        if not cursor.fetchone():
            conn.close()
            return {
                "status": "error",
                "message": "Camera not found or doesn't belong to this user"
            }
        
        cursor.execute(
            "DELETE FROM cameras WHERE id = ? AND user_id = ?",
            (camera_id, user_id)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Camera deleted successfully"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting camera: {str(e)}"
        }

def update_last_accessed(camera_id: int):
    """Update last accessed timestamp for a camera"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE cameras SET last_accessed = ? WHERE id = ?",
            (datetime.now().isoformat(), camera_id)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating last accessed: {str(e)}")

def update_connection_status(camera_id: int, status: str):
    """Update connection status for a camera"""
    try:
        valid_statuses = ['connected', 'disconnected', 'error', 'untested']
        if status not in valid_statuses:
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE cameras SET connection_status = ? WHERE id = ?",
            (status, camera_id)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating connection status: {str(e)}")

# ==========================================
# ✅ VALIDATION FUNCTIONS
# ==========================================

def validate_rtsp_url(rtsp_url: str) -> bool:
    """
    Validate RTSP URL format
    
    Valid formats:
    - rtsp://host:port/path
    - rtsp://user:pass@host:port/path
    - rtsp://host/path
    """
    rtsp_pattern = r'^rtsp://([a-zA-Z0-9\-._~%!$&\'()*+,;=:@]+@)?[a-zA-Z0-9\-._~%!$&\'()*+,;=:]+(/[a-zA-Z0-9\-._~%!$&\'()*+,;=:@/]*)?$'
    return bool(re.match(rtsp_pattern, rtsp_url))

def test_camera_connection(camera_id: int, user_id: int = None) -> Dict:
    """
    Test connection to a camera (returns connection status)
    
    Args:
        camera_id: Camera ID
        user_id: Optional user_id for security
    
    Returns:
        {"status": "connected/error", "message": "..."}
    """
    try:
        import cv2
        
        camera = get_camera_by_id(camera_id, user_id)
        if not camera:
            return {
                "status": "error",
                "message": "Camera not found"
            }
        
        # Try to open camera stream
        rtsp_url = camera['rtsp_url']
        
        # If credentials provided, embed them in URL
        if camera['username'] and camera['password']:
            # rtsp://user:pass@host:port/path
            rtsp_url = camera['rtsp_url'].replace(
                'rtsp://',
                f"rtsp://{camera['username']}:{camera['password']}@"
            )
        
        cap = cv2.VideoCapture(rtsp_url)
        
        # Try to read a frame with timeout
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            update_connection_status(camera_id, 'connected')
            update_last_accessed(camera_id)
            return {
                "status": "connected",
                "message": "✅ Camera connection successful"
            }
        else:
            update_connection_status(camera_id, 'error')
            return {
                "status": "error",
                "message": "Cannot read frames from camera. Check credentials and URL."
            }
    
    except Exception as e:
        update_connection_status(camera_id, 'error')
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)}"
        }

# Initialize database on import
if not os.path.exists(DB_PATH):
    init_cameras_database()
