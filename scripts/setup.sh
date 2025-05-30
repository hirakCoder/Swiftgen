#!/bin/bash

echo "Setting up SwiftGen MVP..."

# Check for required tools
echo "Checking requirements..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.8 or later."
    exit 1
fi

# Check for xcodebuild
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is required. Please install Xcode from the App Store."
    exit 1
fi

# Check for xcodegen
if ! command -v xcodegen &> /dev/null; then
    echo "⚠️  xcodegen is not installed. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew is required to install xcodegen. Please install Homebrew first."
        exit 1
    fi
    brew install xcodegen
fi

# Create virtual environment
echo "Creating Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file from example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update the CLAUDE_API_KEY in backend/.env"
fi

# Create workspaces directory
cd ..
mkdir -p workspaces

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update the CLAUDE_API_KEY in backend/.env"
echo "2. Run the server: cd backend && source venv/bin/activate && python main.py"
echo "3. Open http://localhost:8000/static/index.html in your browser"
