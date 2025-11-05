#!/bin/bash

echo "🔧 Setting up Agentic Wazuh SOC Dashboard..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Setup backend
echo "📦 Setting up backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Backend dependencies installed"
cd ..

# Setup frontend
echo "🎨 Setting up frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys and Wazuh credentials"
echo "2. Run: ./start.sh"
echo ""
echo "📖 See README.md for detailed instructions"