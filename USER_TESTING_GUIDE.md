# SwiftGen User Testing Guide

## 🚀 Quick Start

### 1. Install Dependencies (One Time)
```bash
cd backend
pip3 install -r requirements.txt
```

### 2. Set API Keys
Create a `.env` file in the backend directory:
```bash
CLAUDE_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
XAI_API_KEY=your_xai_api_key  # Optional
```

### 3. Start the Server
```bash
cd backend
python3 main.py
```

You should see:
```
🚀 SwiftGen AI - World-Class iOS App Generator
✓ Enhanced Claude Service: 3 LLMs available
✓ Self-Healing Generator: Enabled
✓ Real-time WebSocket: Active
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 4. Open the UI
Open your browser to: **http://localhost:8000**

## 🧪 Testing the System Like an End User

### Test 1: Simple App Generation
1. **In the chat box, type:**
   ```
   Create a todo list app
   ```

2. **What you should see:**
   - Immediate response: "I'll create a todo list app for you..."
   - Progress panel appears showing stages: Design → Code → Validate → Build → Launch
   - Real-time status updates in the panel
   - Code appears on the right side with multiple files
   - Success modal when complete
   - iOS Simulator launches automatically (if on Mac)

3. **Success indicators:**
   - ✅ All progress stages turn green
   - ✅ Multiple Swift files displayed
   - ✅ "App launched successfully" message
   - ✅ Timer shows completion time (usually 30-60 seconds)

### Test 2: App Modification
1. **After creating the todo app, type:**
   ```
   Add dark mode support
   ```

2. **What you should see:**
   - Response: "I'll add dark mode support to your Todo List app..."
   - Progress panel shows "Modification Progress"
   - Files update in real-time on the right
   - App rebuilds and relaunches

3. **Try more modifications:**
   ```
   Make the buttons bigger
   Change the color scheme to blue
   Add a search bar
   ```

### Test 3: Natural Language Chat
1. **Ask questions:**
   ```
   What features does my app have?
   Can you explain how the todo storage works?
   What can I modify?
   ```

2. **Expected behavior:**
   - Immediate, context-aware responses
   - No progress panel for questions
   - Helpful suggestions and explanations

### Test 4: Complex App Generation
1. **Request a complex app:**
   ```
   Build an e-commerce app with products, cart, and checkout
   ```

2. **What's different:**
   - Longer generation time (45-90 seconds)
   - More files generated (10+)
   - Multiple agents working (UI Agent, API Agent)
   - Comprehensive features implemented

### Test 5: Error Recovery
1. **Test SSL error handling:**
   ```
   Add a feature to fetch weather data from api.openweathermap.org
   ```

2. **If SSL errors occur:**
   - System automatically detects and explains the issue
   - Applies fixes automatically
   - Rebuilds and retests

### Test 6: Edge Cases
1. **Vague requests:**
   ```
   Make something cool
   ```
   - Should ask for clarification or make reasonable choice

2. **Impossible requests:**
   ```
   Create an Android app
   ```
   - Should politely explain it's iOS-only

3. **Very specific requests:**
   ```
   Create a timer that counts down from 5 minutes with a purple gradient background
   ```
   - Should implement exact specifications

## 📊 Monitoring & Verification

### Real-Time Monitoring (Optional)
In a separate terminal:
```bash
cd backend
python3 realtime_monitor.py
```

This shows:
- Active generations
- Success rates
- Error logs
- System health

### Run Automated Tests
```bash
# Test all components
cd backend
python3 comprehensive_system_test.py

# Test user request handling
python3 test_user_requests.py

# Test end-to-end UI flow
python3 test_end_to_end_ui.py
```

### Check Data Collection
```bash
cd backend
python3 export_training_data.py --stats
```

## ✅ Success Criteria

### Frontend-Backend Integration
- [x] WebSocket connects immediately on page load
- [x] Real-time status updates appear in UI
- [x] Progress stages update correctly
- [x] Code displays in right panel
- [x] No console errors in browser

### User Experience
- [x] Response time < 2 seconds for chat
- [x] Generation completes in 30-90 seconds
- [x] Modifications apply correctly
- [x] Context maintained between requests
- [x] Clear error messages when issues occur

### System Features Working
- [x] Template guidance (not direct returns)
- [x] Every app is unique
- [x] Agent system active
- [x] Data collection functioning
- [x] Error recovery working

## 🐛 Troubleshooting

### "WebSocket connection failed"
- Check server is running
- Verify no firewall blocking port 8000
- Try refreshing the page

### "Generation failed"
- Check API keys are set correctly
- Verify internet connection
- Check server logs for details

### "No code displayed"
- Check browser console for errors
- Verify WebSocket is connected
- Try a simpler app request

### "Modifications not applying"
- Ensure you have an active project
- Try more specific modification requests
- Check if files are updating in UI

## 📱 What Makes SwiftGen Special

1. **Unique Every Time**: No two apps are identical
2. **Context Aware**: Remembers your app and modifications
3. **Intelligent Recovery**: Fixes its own errors
4. **Multi-LLM**: Uses best AI for each task
5. **Real iOS Apps**: Launches in actual simulator

## 🎯 Advanced Testing

### Test LLM Routing
Watch which LLM handles each request:
- Claude 3.5: Architecture & complex logic
- GPT-4: Algorithms & bug fixes
- xAI Grok: UI design & simple tasks

### Test Data Collection
Every generation is saved for future model training:
```bash
ls generation_data/generations/
ls generation_data/modifications/
```

### Test Agent Collaboration
Complex apps trigger multiple agents:
- UI Agent: SwiftUI generation
- API Agent: Networking code
- Build Agent: Error analysis

## 📝 Feedback

If you encounter issues:
1. Check `backend/logs/` for detailed logs
2. Run `validate_system.py` to check setup
3. Try the automated test suites
4. Report issues with specific error messages

---

**Remember**: SwiftGen is designed to feel magical - describe any iOS app and watch it come to life!