#!/bin/bash
# Quick Start Script for Linux/macOS
# This script helps you get started with Docker deployment

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "========================================="
echo -e "${GREEN} Abandoned Luggage Detection System${NC}"
echo " Docker Quick Start"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed${NC}"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}ERROR: Docker Compose is not installed${NC}"
    echo "Please install Docker Desktop which includes Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed!${NC}"
echo ""

# Show menu
echo "Select an option:"
echo "1. Build and start all services"
echo "2. Start services"
echo "3. Stop services"
echo "4. View logs"
echo "5. Run API client example"
echo "6. Clean up and remove containers"
echo ""

read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo -e "${YELLOW}Building and starting services...${NC}"
        docker-compose build
        docker-compose up -d
        echo ""
        echo -e "${GREEN}Services started!${NC}"
        echo "- API: http://localhost:8000"
        echo "- API Docs: http://localhost:8000/docs"
        echo "- Streamlit: http://localhost:8501"
        echo "- Nginx: http://localhost:80"
        echo ""
        echo "Check status with: docker-compose ps"
        echo "View logs with: docker-compose logs -f"
        ;;
    2)
        echo -e "${YELLOW}Starting services...${NC}"
        docker-compose up -d
        docker-compose ps
        ;;
    3)
        echo -e "${YELLOW}Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}Services stopped${NC}"
        ;;
    4)
        echo -e "${YELLOW}Showing logs (Ctrl+C to exit)...${NC}"
        docker-compose logs -f
        ;;
    5)
        echo -e "${YELLOW}Running API client example...${NC}"
        python api_client_example.py
        ;;
    6)
        echo -e "${YELLOW}Removing all containers and volumes...${NC}"
        docker-compose down -v
        echo -e "${GREEN}Cleanup complete${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        ;;
esac
