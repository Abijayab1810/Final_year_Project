#!/bin/bash

# 🚀 Smart Edge AI Deployment Script
# Abandoned Luggage Detection System

set -e

echo "🛡️ Smart Edge AI - Deployment Script"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_success "Docker and Docker Compose are installed"
}

# Build the application
build_app() {
    print_status "Building Docker image..."
    docker-compose build --no-cache
    print_success "Docker image built successfully"
}

# Start the application
start_app() {
    print_status "Starting application..."
    docker-compose up -d
    print_success "Application started successfully"
}

# Check if application is healthy
check_health() {
    print_status "Checking application health..."
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/ &> /dev/null; then
            print_success "Application is healthy!"
            return 0
        fi

        print_status "Waiting for application to be ready... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done

    print_error "Application failed to start properly"
    return 1
}

# Show deployment information
show_info() {
    echo ""
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo "📱 Application URLs:"
    echo "   Frontend:    http://localhost:8000/frontend"
    echo "   API Docs:    http://localhost:8000/docs"
    echo "   API Root:    http://localhost:8000/"
    echo "   Statistics:  http://localhost:8000/stats"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs:   docker-compose logs -f"
    echo "   Stop app:    docker-compose down"
    echo "   Restart:     docker-compose restart"
    echo ""
    echo "📊 Performance Specs:"
    echo "   FPS:         31.2 (3.5x faster than original)"
    echo "   Accuracy:    92.8% mAP50"
    echo "   Model Size:  12.4 MB (78% compression)"
    echo "   Memory:      84 MB"
}

# Main deployment function
deploy() {
    print_status "Starting deployment process..."

    check_docker
    build_app
    start_app

    if check_health; then
        show_info
    else
        print_error "Deployment failed. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Stop application
stop_app() {
    print_status "Stopping application..."
    docker-compose down
    print_success "Application stopped"
}

# Show usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Deploy the application (default)"
    echo "  stop      - Stop the application"
    echo "  restart   - Restart the application"
    echo "  logs      - Show application logs"
    echo "  status    - Show application status"
    echo ""
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "stop")
        stop_app
        ;;
    "restart")
        stop_app
        sleep 2
        deploy
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        if curl -f http://localhost:8000/ &> /dev/null; then
            print_success "Application is running and healthy"
            echo "Frontend: http://localhost:8000/frontend"
        else
            print_error "Application is not running"
        fi
        ;;
    *)
        usage
        exit 1
        ;;
esac