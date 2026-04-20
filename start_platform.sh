#!/bin/bash
# Start Luggage Detection Platform - Linux/Mac Shell Script
# This script starts both the FastAPI backend and Streamlit frontend

echo ""
echo "========================================"
echo "  Luggage Detection Platform - Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version detected"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import streamlit; import fastapi; import ultralytics" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "  Starting Services..."
echo "========================================"
echo ""
echo "This will open TWO terminal windows:"
echo "   1. FastAPI Backend (Port 8000)"
echo "   2. Streamlit Frontend (Port 8501)"
echo ""
echo "IMPORTANT: Keep BOTH windows open while testing!"
echo ""
read -p "Press Enter to continue..."

# Use tmux if available, otherwise use separate terminals or backgrounding
if command -v tmux &> /dev/null; then
    # Using tmux for clean separation
    echo "Starting with tmux..."
    
    # Create new tmux session
    tmux new-session -d -s luggage
    
    # Start FastAPI in first pane
    tmux send-keys -t luggage "echo 'Starting FastAPI Backend on port 8000...'; python3 api_auth.py" Enter
    
    # Split window and start Streamlit in second pane
    tmux split-window -h -t luggage
    tmux send-keys -t luggage "sleep 3; echo 'Starting Streamlit Frontend on port 8501...'; streamlit run app_auth.py" Enter
    
    # Attach to session
    tmux attach -t luggage
else
    # Fallback: Use separate terminal windows or background processes
    echo "Starting FastAPI Backend..."
    python3 api_auth.py &
    API_PID=$!
    
    # Wait for API to start
    sleep 3
    
    echo "Starting Streamlit Frontend..."
    streamlit run app_auth.py &
    STREAMLIT_PID=$!
    
    # Display access information
    echo ""
    echo "========================================"
    echo "  ✅ Platform Started Successfully!"
    echo "========================================"
    echo ""
    echo "Access the platform:"
    echo "   🌐 Dashboard:  http://localhost:8501"
    echo "   🔧 API Docs:  http://localhost:8000/docs"
    echo ""
    echo "First Time Setup:"
    echo "   1. Go to http://localhost:8501"
    echo "   2. Click 'Sign Up' tab"
    echo "   3. Create your account"
    echo "   4. Login"
    echo "   5. Add a camera in 'Camera Management'"
    echo ""
    echo "To Stop: Press Ctrl+C here or close browser tabs"
    echo ""
    
    # Wait for background processes
    wait
fi
