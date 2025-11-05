#!/bin/bash

echo "🚀 Starting Agentic Wazuh SOC Dashboard..."

# Check if .env file exists and has API key
if [ ! -f "backend/.env" ]; then
    echo "❌ Please create backend/.env file with your configuration"
    exit 1
fi

if grep -q "your_gemini_api_key_here" backend/.env; then
    echo "❌ Please update your GEMINI_API_KEY in backend/.env"
    echo "Get your API key from: https://aistudio.google.com/"
    exit 1
fi

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Both servers started!"
echo "📊 Dashboard: http://localhost:5173"
echo "🔌 API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait