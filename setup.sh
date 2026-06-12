#!/bin/bash
set -e

echo "=== HealthBridge Setup ==="

# 1. Copy env
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env — edit SECRET_KEY before deploying to prod"
fi

# 2. Start DB
echo "\n[1/4] Starting PostgreSQL..."
docker-compose up db -d
echo "Waiting for DB to be ready..."
sleep 4

# 3. Backend virtualenv + deps
echo "\n[2/4] Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# 4. Migrations
echo "\n[3/4] Running database migrations..."
alembic revision --autogenerate -m "init" 2>/dev/null || true
alembic upgrade head

# 5. Seed
echo "\n[4/4] Seeding database..."
python seed.py

cd ..

echo "\n=== Done! ==="
echo ""
echo "Start the backend:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Test OTP login:"
echo "  curl -X POST http://localhost:8000/auth/send-otp -H 'Content-Type: application/json' -d '{\"phone\": \"9000000001\"}'"
