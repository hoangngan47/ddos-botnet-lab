#!/bin/bash
# DDoS Lab - Quick Start Script

set -e

echo "=================================="
echo "DDoS Botnet Lab - Quick Start"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED} Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Menu
echo -e "${BLUE}Select an option:${NC}"
echo "1) Start the lab"
echo "2) Stop the lab"
echo "3) View server metrics"
echo "4) Connect to C&C console"
echo "5) View bot logs"
echo "6) View server logs"
echo "7) Clean up all containers"
echo "8) Exit"
echo ""
read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo -e "${BLUE}Starting DDoS Lab...${NC}"
        docker-compose up -d
        sleep 2
        echo ""
        echo -e "${GREEN}✓ Lab started!${NC}"
        echo ""
        echo "Services running:"
        docker-compose ps
        echo ""
        echo "Next steps:"
        echo "  1. Connect to C&C: docker exec -it cnc python cnc.py"
        echo "  2. View metrics: curl http://localhost:3000/metrics"
        echo "  3. View logs: docker logs -f server"
        ;;
    
    2)
        echo -e "${BLUE}Stopping DDoS Lab...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Lab stopped${NC}"
        ;;
    
    3)
        echo -e "${BLUE}Fetching server metrics...${NC}"
        echo ""
        curl -s http://localhost:3000/metrics | python3 -m json.tool
        ;;
    
    4)
        echo -e "${BLUE}Connecting to C&C console...${NC}"
        echo "Type 'HELP' for available commands"
        echo ""
        docker exec -it cnc python cnc.py
        ;;
    
    5)
        echo -e "${BLUE}Bot logs (last 20 lines):${NC}"
        echo ""
        for i in 1 2 3; do
            echo -e "${YELLOW}=== Bot $i ===${NC}"
            docker logs bot_$i | tail -20
            echo ""
        done
        ;;
    
    6)
        echo -e "${BLUE}Server logs (continuous):${NC}"
        docker logs -f server
        ;;
    
    7)
        echo -e "${YELLOW}WARNING: This will remove all containers and data!${NC}"
        read -p "Are you sure? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            docker-compose down -v
            echo -e "${GREEN}All cleaned up${NC}"
        else
            echo "Cancelled"
        fi
        ;;
    
    8)
        echo "Goodbye!"
        exit 0
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
