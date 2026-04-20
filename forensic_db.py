"""
Forensic Database Module for Abandoned Luggage Detection System
Handles logging, retrieval, and analysis of detected abandoned luggage incidents
"""

import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
DB_NAME = "forensic_detections.db"
EVIDENCE_FOLDER = "evidence"

# Create evidence folder if it doesn't exist
if not os.path.exists(EVIDENCE_FOLDER):
    os.makedirs(EVIDENCE_FOLDER)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================
def init_database():
    """Initialize the forensic database with required tables"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS abandoned_bags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            track_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            image_filepath TEXT,
            camera_id TEXT,
            confidence_score REAL,
            frame_width INTEGER,
            frame_height INTEGER,
            bag_x1 INTEGER,
            bag_y1 INTEGER,
            bag_x2 INTEGER,
            bag_y2 INTEGER,
            actions_taken TEXT DEFAULT 'Logged',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index on track_id and timestamp for faster queries
    c.execute('CREATE INDEX IF NOT EXISTS idx_track_id ON abandoned_bags(track_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON abandoned_bags(timestamp)')
    
    conn.commit()
    conn.close()


# ==========================================
# LOGGING FUNCTIONS
# ==========================================
def log_abandoned_bag(user_id, track_id, duration_seconds, image_filepath, camera_id, 
                      confidence, frame_dims, bag_bbox):
    """
    Log an abandoned bag detection to the database
    
    Args:
        user_id: User ID who owns this detection
        track_id: Unique tracker ID for this bag
        duration_seconds: How long the bag was stationary
        image_filepath: Path to the evidence image
        camera_id: Which camera detected it
        confidence: Detection confidence score (0-1)
        frame_dims: Tuple of (width, height) of the frame
        bag_bbox: Tuple of (x1, y1, x2, y2) bounding box coordinates
    """
    if not os.path.exists(DB_NAME):
        init_database()
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frame_width, frame_height = frame_dims
    x1, y1, x2, y2 = bag_bbox
    
    c.execute('''
        INSERT INTO abandoned_bags 
        (user_id, track_id, timestamp, duration_seconds, image_filepath, camera_id, 
         confidence_score, frame_width, frame_height, bag_x1, bag_y1, bag_x2, bag_y2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, track_id, timestamp, duration_seconds, image_filepath, camera_id,
          confidence, frame_width, frame_height, x1, y1, x2, y2))
    
    conn.commit()
    conn.close()
    print(f"✅ Logged abandoned bag - TrackID: {track_id}, Duration: {duration_seconds}s")


# ==========================================
# RETRIEVAL FUNCTIONS
# ==========================================
def get_all_abandoned_bags(user_id: int = None):
    """
    Retrieve all abandoned bag detections from the database
    
    Args:
        user_id: Optional filter by specific user. If None, returns all records.
    
    Returns:
        DataFrame with detections
    """
    if not os.path.exists(DB_NAME):
        init_database()
        return pd.DataFrame()  # Return empty DataFrame if no data
    
    conn = sqlite3.connect(DB_NAME)
    
    if user_id:
        query = "SELECT * FROM abandoned_bags WHERE user_id = ? ORDER BY timestamp DESC"
        df = pd.read_sql_query(query, conn, params=(user_id,))
    else:
        df = pd.read_sql_query("SELECT * FROM abandoned_bags ORDER BY timestamp DESC", conn)
    
    conn.close()
    
    # Ensure proper data types
    if len(df) > 0:
        int_columns = ['track_id', 'duration_seconds', 'frame_width', 'frame_height', 
                       'bag_x1', 'bag_y1', 'bag_x2', 'bag_y2']
        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        if 'confidence_score' in df.columns:
            df['confidence_score'] = pd.to_numeric(df['confidence_score'], errors='coerce').fillna(0)
    
    return df


def get_bags_by_date_range(start_date, end_date):
    """
    Retrieve abandoned bags detected within a date range
    
    Args:
        start_date: Start date (datetime or string format YYYY-MM-DD)
        end_date: End date (datetime or string format YYYY-MM-DD)
    
    Returns:
        DataFrame with filtered detections
    """
    if not os.path.exists(DB_NAME):
        init_database()
        return pd.DataFrame()
    
    # Convert to string if datetime objects
    if hasattr(start_date, 'strftime'):
        start_date = start_date.strftime("%Y-%m-%d")
    if hasattr(end_date, 'strftime'):
        end_date = end_date.strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT * FROM abandoned_bags 
        WHERE DATE(timestamp) BETWEEN ? AND ?
        ORDER BY timestamp DESC
    """
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    
    # Ensure proper data types
    if len(df) > 0:
        int_columns = ['track_id', 'duration_seconds', 'frame_width', 'frame_height', 
                       'bag_x1', 'bag_y1', 'bag_x2', 'bag_y2']
        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        if 'confidence_score' in df.columns:
            df['confidence_score'] = pd.to_numeric(df['confidence_score'], errors='coerce').fillna(0)
    
    return df


def get_bags_by_camera(camera_id):
    """
    Retrieve abandoned bags detected by a specific camera
    
    Args:
        camera_id: Camera identifier
    
    Returns:
        DataFrame with filtered detections
    """
    if not os.path.exists(DB_NAME):
        init_database()
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM abandoned_bags WHERE camera_id = ? ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn, params=(camera_id,))
    conn.close()
    
    # Ensure proper data types
    if len(df) > 0:
        int_columns = ['track_id', 'duration_seconds', 'frame_width', 'frame_height', 
                       'bag_x1', 'bag_y1', 'bag_x2', 'bag_y2']
        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        if 'confidence_score' in df.columns:
            df['confidence_score'] = pd.to_numeric(df['confidence_score'], errors='coerce').fillna(0)
    
    return df


# ==========================================
# STATISTICS FUNCTIONS
# ==========================================
def get_statistics():
    """
    Calculate comprehensive statistics about abandoned luggage detections
    
    Returns:
        Dictionary with various statistics
    """
    if not os.path.exists(DB_NAME):
        init_database()
        return {
            'total_detections': 0,
            'average_duration_seconds': 0,
            'max_duration_seconds': 0,
            'average_confidence': 0
        }
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Total detections
        c.execute("SELECT COUNT(*) FROM abandoned_bags")
        result = c.fetchone()
        total_detections = result[0] if result and result[0] else 0
        
        # Average duration
        c.execute("SELECT AVG(duration_seconds) FROM abandoned_bags")
        result = c.fetchone()
        average_duration = result[0] if result and result[0] else 0
        
        # Max duration
        c.execute("SELECT MAX(duration_seconds) FROM abandoned_bags")
        result = c.fetchone()
        max_duration = result[0] if result and result[0] else 0
        
        # Average confidence
        c.execute("SELECT AVG(confidence_score) FROM abandoned_bags")
        result = c.fetchone()
        avg_conf = result[0] if result and result[0] else 0
        avg_conf = float(avg_conf) if avg_conf else 0
        
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        avg_conf = 0
        average_duration = 0
        max_duration = 0
        total_detections = 0
    finally:
        conn.close()
    
    return {
        'total_detections': total_detections,
        'average_duration_seconds': average_duration if average_duration else 0,
        'max_duration_seconds': max_duration if max_duration else 0,
        'average_confidence': avg_conf / 100 if avg_conf > 1 else avg_conf
    }


def get_daily_stats(days=7):
    """
    Get daily statistics for the last N days
    
    Args:
        days: Number of days to look back (default 7)
    
    Returns:
        DataFrame with daily statistics
    """
    if not os.path.exists(DB_NAME):
        init_database()
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as count,
            AVG(duration_seconds) as avg_duration,
            MAX(duration_seconds) as max_duration
        FROM abandoned_bags
        WHERE DATE(timestamp) >= DATE('now', '-' || ? || ' days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """
    df = pd.read_sql_query(query, conn, params=(days,))
    conn.close()
    
    return df


def get_camera_stats():
    """
    Get statistics grouped by camera
    
    Returns:
        DataFrame with per-camera statistics
    """
    if not os.path.exists(DB_NAME):
        init_database()
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT 
            camera_id,
            COUNT(*) as detections,
            AVG(duration_seconds) as avg_duration,
            MAX(duration_seconds) as max_duration,
            AVG(confidence_score) as avg_confidence
        FROM abandoned_bags
        GROUP BY camera_id
        ORDER BY detections DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


# ==========================================
# MANAGEMENT FUNCTIONS
# ==========================================
def clear_all_records():
    """Clear all records from the database"""
    if not os.path.exists(DB_NAME):
        return
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM abandoned_bags")
    conn.commit()
    conn.close()
    print("✅ All records cleared from database")


def delete_old_records(days=30):
    """
    Delete records older than specified days
    
    Args:
        days: Delete records older than this many days (default 30)
    """
    if not os.path.exists(DB_NAME):
        return
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        DELETE FROM abandoned_bags 
        WHERE DATE(timestamp) < DATE('now', '-' || ? || ' days')
    """, (days,))
    conn.commit()
    rows_deleted = c.rowcount
    conn.close()
    print(f"✅ Deleted {rows_deleted} records older than {days} days")


def update_action_status(bag_id, action_status):
    """
    Update the action status of a detection record
    
    Args:
        bag_id: ID of the detection record
        action_status: New status (e.g., 'Logged', 'Investigated', 'Resolved')
    """
    if not os.path.exists(DB_NAME):
        return
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE abandoned_bags SET actions_taken = ? WHERE id = ?", 
              (action_status, bag_id))
    conn.commit()
    conn.close()


def export_to_csv(filename=None):
    """
    Export all records to a CSV file
    
    Args:
        filename: Output CSV filename (default: forensic_export_TIMESTAMP.csv)
    
    Returns:
        Path to the exported file
    """
    if filename is None:
        filename = f"forensic_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    df = get_all_abandoned_bags()
    
    if len(df) > 0:
        df.to_csv(filename, index=False)
        print(f"✅ Exported {len(df)} records to {filename}")
        return filename
    else:
        print("⚠️ No records to export")
        return None


# ==========================================
# INITIALIZATION
# ==========================================
# Initialize database on module import
init_database()
