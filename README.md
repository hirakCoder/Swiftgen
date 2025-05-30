# SwiftGen MVP

An AI-powered iOS app generator that creates Swift applications from natural language descriptions.

## Features

- Natural language to iOS app generation
- Automatic Swift code generation using Claude AI
- Local Xcode project building
- Real-time build status updates
- Code preview with syntax highlighting

## Quick Start

Run the Smart Setup Agent:

```bash
python3 swiftgen_setup_agent.py
```

The agent will:
1. Check system requirements
2. Create project structure
3. Install dependencies
4. Configure everything automatically

## Requirements

- macOS with Xcode installed
- Python 3.8+
- Claude API key from Anthropic

## Usage

After setup:
1. Start the server: `cd backend && source venv/bin/activate && python main.py`
2. Open http://localhost:8000/static/index.html
3. Describe your app and click "Generate App"

## Troubleshooting

If you encounter any errors, the agent will:
1. Identify the issue automatically
2. Generate an error report
3. Suggest fixes or prompt you to share with Claude

## License

MIT
