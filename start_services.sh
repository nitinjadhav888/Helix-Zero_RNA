#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Helix-Zero V8 Production Startup Script (Linux/macOS)
# ═══════════════════════════════════════════════════════════════════════════
# This script starts all three services for local testing
# For production, use Docker Compose or Systemd services

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     HELIX-ZERO V8 - Multi-Service Startup                         ║${NC}"
echo -e "${BLUE}║     Consolidated Production Build                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}\n"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 not found! Please install Python 3.9+${NC}"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════
# Kill Any Existing Processes on Required Ports
# ═══════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}[1/6] Cleaning up existing processes on ports 5000, 5001, 8000...${NC}"
for port in 5000 5001 8000; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -Pi :$port -sTCP:LISTEN -t)
        kill -9 $PID 2>/dev/null || true
        echo "      Killed process on port $port (PID: $PID)"
    fi
done
echo -e "${GREEN}[✓] Port cleanup complete${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# Launch Web App (Port 5000)
# ═══════════════════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[2/6] Starting Main Web App on http://127.0.0.1:5000...${NC}"
cd web_app
nohup python3 app.py > ../logs/webapp.log 2>&1 &
WEBAPP_PID=$!
echo -e "${GREEN}[✓] Web App started (PID: $WEBAPP_PID)${NC}"
cd ..
sleep 2

# ═══════════════════════════════════════════════════════════════════════════
# Launch CMS Service (Port 5001)
# ═══════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}[3/6] Starting CMS Service on http://127.0.0.1:5001...${NC}"
cd cms_service
nohup python3 app.py > ../logs/cms.log 2>&1 &
CMS_PID=$!
echo -e "${GREEN}[✓] CMS Service started (PID: $CMS_PID)${NC}"
cd ..
sleep 2

# ═══════════════════════════════════════════════════════════════════════════
# Launch FastAPI Backend (Port 8000)
# ═══════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}[4/6] Starting FastAPI Backend on http://127.0.0.1:8000...${NC}"
cd backend
nohup python3 main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}[✓] Backend started (PID: $BACKEND_PID)${NC}"
cd ..
sleep 2

# ═══════════════════════════════════════════════════════════════════════════
# Verify Services
# ═══════════════════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[5/6] Verifying service ports...${NC}"
sleep 2

for port in 5000 5001 8000; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "    ${GREEN}[✓]${NC} Port $port is listening"
    else
        echo -e "    ${YELLOW}[⚠]${NC} Port $port is NOT listening - check service logs"
    fi
done

# ═══════════════════════════════════════════════════════════════════════════
# Final Message
# ═══════════════════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[6/6] Startup Complete!${NC}\n"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SERVICES RUNNING - Access Dashboard                              ║${NC}"
echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║  🌐  Web App:         http://127.0.0.1:5000                       ║${NC}"
echo -e "${BLUE}║  🧪  CMS Service:    http://127.0.0.1:5001                       ║${NC}"
echo -e "${BLUE}║  ⚙️  DL Backend:      http://127.0.0.1:8000/docs                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}Service PIDs:${NC}"
echo "  Web App: $WEBAPP_PID"
echo "  CMS Service: $CMS_PID"
echo "  Backend: $BACKEND_PID"
echo ""
echo -e "${YELLOW}To stop services, run: pkill -f 'python3 app.py' && pkill -f 'python3 main.py'${NC}"
echo -e "${YELLOW}To view logs: tail -f logs/webapp.log (and cms.log, backend.log)${NC}\n"

# Save PIDs for easy shutdown
echo "$WEBAPP_PID" > .pids/webapp.pid
echo "$CMS_PID" > .pids/cms.pid
echo "$BACKEND_PID" > .pids/backend.pid

# Keep script running
wait
