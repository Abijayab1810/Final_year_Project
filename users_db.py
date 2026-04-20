"""
User Management Database Module
Handles user registration, login, and JWT tokens
"""

import sqlite3
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import pandas as pd

# ==========================================
# SECURITY CONFIGURATION
# ==========================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-min-32-chars-1234567890")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
USERS_DB = "users.db"


# ==========================================
# DATABASE INITIALIZATION
# ==========================================
def init_users_database():
    """Initialize users database with required tables"""
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()


# ==========================================
# PASSWORD HASHING
# ==========================================
def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ==========================================
# USER REGISTRATION & LOGIN
# ==========================================
def register_user(username: str, email: str, password: str, full_name: str = None) -> dict:
    """
    Register a new user
    
    Args:
        username: Unique username
        email: Unique email address
        password: Plain text password (will be hashed)
        full_name: Optional full name
    
    Returns:
        Result dictionary with success status
    """
    if not os.path.exists(USERS_DB):
        init_users_database()
    
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        hashed_password = hash_password(password)
        
        c.execute('''
            INSERT INTO users (username, email, full_name, hashed_password)
            VALUES (?, ?, ?, ?)
        ''', (username, email, full_name, hashed_password))
        
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": f"User {username} registered successfully",
            "user_id": user_id
        }
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return {"status": "error", "message": "Username already exists"}
        elif "email" in str(e):
            return {"status": "error", "message": "Email already exists"}
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_user_by_username(username: str) -> dict:
    """Get user by username"""
    if not os.path.exists(USERS_DB):
        return None
    
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    
    c.execute("SELECT id, username, email, hashed_password, is_active FROM users WHERE username = ?", 
              (username,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "email": result[2],
            "hashed_password": result[3],
            "is_active": result[4]
        }
    return None


def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user and return user info if valid"""
    user = get_user_by_username(username)
    
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    if not user["is_active"]:
        return None
    
    return user


# ==========================================
# JWT TOKEN MANAGEMENT
# ==========================================
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
        
        return {"username": username, "user_id": payload.get("user_id")}
    except JWTError:
        return None


# ==========================================
# USER PROFILE
# ==========================================
def get_user_profile(user_id: int) -> dict:
    """Get user profile information"""
    if not os.path.exists(USERS_DB):
        return None
    
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, username, email, full_name, created_at, is_active 
        FROM users WHERE id = ?
    ''', (user_id,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "email": result[2],
            "full_name": result[3],
            "created_at": result[4],
            "is_active": result[5]
        }
    return None


def update_user_profile(user_id: int, full_name: str = None, email: str = None) -> dict:
    """Update user profile"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)
        
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if not updates:
            return {"status": "error", "message": "No updates provided"}
        
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        c.execute(query, params)
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Profile updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ==========================================
# INITIALIZATION
# ==========================================
init_users_database()
