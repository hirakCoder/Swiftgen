#!/bin/bash
# SwiftGen Development Setup Script

set -e

echo "🚀 SwiftGen Development Setup"
echo "============================"

# Check Python version
echo "📦 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install pre-commit

# Install pre-commit hooks
echo "📦 Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Run pre-commit on all files
echo "📦 Running pre-commit checks..."
pre-commit run --all-files || true

# Create necessary directories
echo "📦 Creating necessary directories..."
mkdir -p workspaces logs backend/tests/__pycache__

# Check for API keys
echo "🔑 Checking for API keys..."
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOL
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
XAI_API_KEY=your-xai-api-key-here
ENVIRONMENT=development
LOG_LEVEL=INFO
EOL
    echo "✅ Created .env template. Please add your API keys."
else
    echo "✅ .env file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to .env file"
echo "2. Run tests: ./run_tests.py"
echo "3. Start the server: python backend/main.py"
echo ""
echo "Pre-commit hooks are now installed and will run on every commit."
echo "To run tests manually: pytest"
echo "To run specific test categories: pytest -m unit"
echo ""