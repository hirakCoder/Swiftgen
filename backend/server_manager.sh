#!/bin/bash
# Server Manager for SwiftGen

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if server is running
check_server() {
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to find server PID
find_server_pid() {
    ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}' | head -1
}

# Function to start server
start_server() {
    echo -e "${GREEN}Starting SwiftGen server...${NC}"
    
    # Check if already running
    if check_server; then
        echo -e "${YELLOW}Server is already running${NC}"
        PID=$(find_server_pid)
        if [ ! -z "$PID" ]; then
            echo "Server PID: $PID"
        fi
        return 0
    fi
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Start server in background
    nohup python main.py > server.log 2>&1 &
    SERVER_PID=$!
    echo "Started server with PID: $SERVER_PID"
    
    # Wait for server to be ready
    echo -n "Waiting for server to start"
    for i in {1..30}; do
        if check_server; then
            echo -e "\n${GREEN}✅ Server started successfully${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    echo -e "\n${RED}❌ Server failed to start${NC}"
    echo "Check server.log for details"
    return 1
}

# Function to stop server
stop_server() {
    echo -e "${YELLOW}Stopping SwiftGen server...${NC}"
    
    KILLED_COUNT=0
    
    # Kill all Python processes running main.py
    for pid in $(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}'); do
        kill -9 $pid 2>/dev/null && {
            echo "Killed server process: PID $pid"
            KILLED_COUNT=$((KILLED_COUNT + 1))
        }
    done
    
    if [ $KILLED_COUNT -eq 0 ]; then
        echo "No server processes found"
    else
        echo -e "${GREEN}✅ Stopped $KILLED_COUNT server process(es)${NC}"
    fi
}

# Function to restart server
restart_server() {
    stop_server
    sleep 2
    start_server
}

# Function to show server status
status_server() {
    echo -e "${YELLOW}SwiftGen Server Status${NC}"
    echo "======================="
    
    if check_server; then
        echo -e "Status: ${GREEN}Running${NC}"
        PID=$(find_server_pid)
        if [ ! -z "$PID" ]; then
            echo "PID: $PID"
            # Show process info
            ps aux | grep "python.*main.py" | grep -v grep | head -1
        fi
    else
        echo -e "Status: ${RED}Not Running${NC}"
    fi
    
    # Check for orphaned processes
    ORPHANS=$(ps aux | grep "python.*main.py" | grep -v grep | wc -l)
    if [ $ORPHANS -gt 1 ]; then
        echo -e "\n${YELLOW}Warning: Found $ORPHANS Python processes running main.py${NC}"
        echo "Run './server_manager.sh stop' to clean up"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "server.log" ]; then
        echo -e "${YELLOW}Last 50 lines of server.log:${NC}"
        echo "============================"
        tail -n 50 server.log
    else
        echo -e "${RED}No server.log file found${NC}"
    fi
}

# Main script logic
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        status_server
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "SwiftGen Server Manager"
        echo "======================="
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server"
        echo "  stop    - Stop all server processes"
        echo "  restart - Restart the server"
        echo "  status  - Show server status"
        echo "  logs    - Show recent server logs"
        exit 1
        ;;
esac