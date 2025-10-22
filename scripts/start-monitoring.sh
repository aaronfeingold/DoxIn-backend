#!/bin/bash

# Case Study Monitoring Stack Startup Script
# This script starts the complete monitoring infrastructure

set -e

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting Case Study Monitoring Stack...${NC}"

# Change to the docker directory
cd "$(dirname "$0")/../docker"

# Check if .env file exists, use backend/api/.env if not
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found, copying from backend/api/.env...${NC}"
    if [ -f ../api/.env ]; then
        cp ../api/.env .env
        echo -e "${GREEN}.env file copied successfully${NC}"
    else
        echo -e "${RED}Error: backend/api/.env not found${NC}"
        exit 1
    fi
fi

# Start the monitoring stack
echo -e "${YELLOW}Starting monitoring services...${NC}"
docker-compose --profile monitoring up -d

echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Health check function
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}$service_name is ready${NC}"
            return 0
        fi
        echo -e "${YELLOW}Waiting for $service_name (attempt $attempt/$max_attempts)...${NC}"
        sleep 2
        ((attempt++))
    done
    echo -e "${RED}$service_name failed to start${NC}"
    return 1
}

# Check if services are ready
echo -e "${CYAN}Performing health checks...${NC}"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3001/api/health"
check_service "Node Exporter" "http://localhost:9100/metrics"

# Show service URLs
echo ""
echo -e "${GREEN}Case Study Monitoring Stack is ready!${NC}"
echo ""
echo -e "${CYAN}Monitoring Services:${NC}"
echo "  Prometheus:     http://localhost:9090"
echo "  Grafana:        http://localhost:3001 (admin/admin)"
echo "  AlertManager:   http://localhost:9093"
echo "  Node Exporter:  http://localhost:9100"
echo ""
echo -e "${BLUE}Infrastructure Services:${NC}"
echo "  PostgreSQL:     localhost:5433"
echo "  Redis:          localhost:6379"
echo ""
echo -e "${YELLOW}Application Services (if running):${NC}"
echo "  Flask API:      http://localhost:8000"
echo "  Celery Flower:  http://localhost:5555"
echo ""
echo "To start all services including the app:"
echo "  docker-compose --profile full up -d"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service-name]"
