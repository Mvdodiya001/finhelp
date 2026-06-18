#!/bin/bash

echo "============================================="
echo "   FinHelp - Boot Sequence  "
echo "============================================="

echo "-> Starting Infrastructure (Postgres & Redis)..."
docker compose up -d db redis

echo "-> Waiting for PostgreSQL to be ready..."
until docker exec quant_db pg_isready -U admin -d stock_predictor; do
    sleep 2
done

# 1. Start FastAPI Backend
echo "-> Booting FastAPI Backend..."
cd backend
source venv/bin/activate
export USE_REDIS=true
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Vite React Frontend
echo "-> Booting React Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Handle graceful shutdown
trap "echo 'Shutting down services...'; kill $BACKEND_PID $FRONTEND_PID; exit" EXIT INT TERM

echo ""
echo "✅ Services are running successfully."
echo "🌐 Frontend URL: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8000/docs"
echo "Press Ctrl+C to stop."
wait
