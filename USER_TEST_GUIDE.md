# 🚀 SwiftGen User Testing Guide

## Quick Start (3 Steps)

### 1. Start the Backend Server
```bash
cd backend
source venv/bin/activate  # or source test_venv/bin/activate
python main.py
```

Wait for:
```
Ready to create unique, world-class iOS apps!
============================================================
```

### 2. Open the Frontend UI
Open a new terminal:
```bash
cd frontend
npm install  # First time only
npm run dev
```

Then open your browser to: **http://localhost:5173**

### 3. Start Creating Apps!

---

## 📱 Test Scenarios for End Users

### Test 1: Simple App Generation
1. **In the UI, type:** "Create a todo list app"
2. **Click:** Generate
3. **Watch:** Progress updates in real-time
4. **Result:** App opens in iOS Simulator automatically

### Test 2: Complex App Generation
1. **Type:** "Create a social media app with user profiles, posts, comments, likes, and real-time chat"
2. **Click:** Generate
3. **Notice:** More generation steps due to complexity
4. **Result:** Fully functional app with multiple screens

### Test 3: App Modifications
1. **After generating any app, type:** "Add dark mode support"
2. **Click:** Send
3. **Watch:** Files being modified in real-time
4. **Result:** App rebuilds with dark mode toggle

### Test 4: Multiple Modifications
Try these one by one:
- "Add a search bar to filter items"
- "Make the UI more modern with animations"
- "Add user authentication"
- "Improve performance for large datasets"

### Test 5: Agent System in Action
1. **Generate:** "Create a weather app with beautiful animations"
2. **Watch logs for:**
   - UI Agent handling interface design
   - API Agent setting up weather API
   - Build Agent ensuring everything compiles

### Test 6: Error Recovery
1. **Intentionally cause an error:** "Create an app using NavigationView and old iOS 14 APIs"
2. **Watch:** System automatically fixes deprecated code
3. **Result:** Modern iOS 16+ compatible app

---

## 🎯 What to Look For

### In the UI:
- ✅ Real-time progress updates
- ✅ Status messages (Analyzing → Generating → Building → Launching)
- ✅ File tree showing created files
- ✅ Chat interface for modifications
- ✅ Error messages are user-friendly

### In the Simulator:
- ✅ App launches automatically
- ✅ All features work as requested
- ✅ Modifications apply without breaking the app
- ✅ Professional UI/UX

### In the Terminal (Backend):
- ✅ Agent coordination messages
- ✅ Recovery attempts when errors occur
- ✅ WebSocket notifications being sent
- ✅ LLM routing decisions

---

## 🧪 Advanced Testing

### Test Hybrid LLM Mode:
```bash
# In backend/main.py, set:
USE_HYBRID_MODE = True
```
Then generate complex apps to see different LLMs handling different parts.

### Test Specific Features:

**1. Complexity Detection:**
- Simple: "Create a counter app" (watch for 3 attempts max)
- Complex: "Create an e-commerce app" (watch for 5 attempts max)

**2. WebSocket Real-time Updates:**
- Open browser DevTools → Network → WS
- Watch messages flow during generation

**3. Modification Intelligence:**
- Ask for conflicting changes
- System should handle gracefully

---

## 🐛 Common Issues & Solutions

### Issue: "Server not responding"
**Fix:** Make sure backend is running on port 8000

### Issue: "No WebSocket connection"
**Fix:** Check if frontend is running on port 5173

### Issue: "LLM timeout"
**Fix:** System automatically retries with different LLM

### Issue: "Build failed"
**Fix:** Watch auto-recovery fix the issues

---

## 📊 Success Metrics

Your testing is successful when:
- ✅ Can generate 5 different apps without manual intervention
- ✅ Can modify each app at least 3 times
- ✅ All apps open in simulator
- ✅ No manual code fixes needed
- ✅ UI shows all progress in real-time

---

## 🎉 Fun Apps to Try

1. **"Create a Pomodoro timer with statistics"**
2. **"Build a recipe app with categories and favorites"**
3. **"Make a fitness tracker with charts"**
4. **"Create a meditation app with breathing exercises"**
5. **"Build a password manager with biometric auth"**

Then modify them:
- "Add haptic feedback"
- "Include sound effects"
- "Add data export functionality"
- "Make it work offline"

---

## 💡 Pro Tips

1. **Watch both UI and terminal** - See the full orchestration
2. **Try edge cases** - The system handles them gracefully
3. **Check the simulator** - Apps are fully functional
4. **Read WebSocket messages** - Understand the flow
5. **Break things** - Recovery system will fix them

Happy Testing! 🚀