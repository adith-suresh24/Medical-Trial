#!/bin/bash
# Hospital Management System - Start Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🏥 Hospital Management System${NC}"
echo -e "${YELLOW}Starting all services...${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 is required but not installed.${NC}"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --break-system-packages -r backend/requirements.txt -q 2>/dev/null || pip install -r backend/requirements.txt -q

# Initialize database and seed data
echo "🗄️  Initializing database..."
cd backend
python3 -c "
from app.database import init_db
init_db()
print('✅ Database tables created')
" 2>/dev/null

python3 -m app.seed 2>/dev/null
cd ..

# Start server
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}🚀 Starting server on http://0.0.0.0:8000${NC}"
echo -e "${YELLOW}   API Docs: http://localhost:8000/api/docs${NC}"
echo -e "${YELLOW}   Frontend: http://localhost:8000/${NC}"
echo ""
echo -e "${YELLOW}Demo Credentials:${NC}"
echo -e "  Admin:  admin / admin123"
echo -e "  Doctor: doctor1 / doctor123"
echo -e "  Staff:  staff1 / staff123"
echo ""

cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
