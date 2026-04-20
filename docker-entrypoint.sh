#!/bin/bash
# Startup script for Docker container - runs both FastAPI and Streamlit
# This script can be used for development or as an entrypoint for Docker

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Abandoned Luggage Detection System${NC}"

# Check if running in development mode or production
if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${YELLOW}Running in PRODUCTION mode${NC}"
    # Run only FastAPI in production
    exec uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo -e "${YELLOW}Running in DEVELOPMENT mode${NC}"
    # For development, you can run both services using a process manager like supervisord
    # For now, FastAPI will run as the primary service
    exec uvicorn api:app --host 0.0.0.0 --port 8000 --reload
fi
