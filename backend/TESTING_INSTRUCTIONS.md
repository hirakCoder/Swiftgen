# CRITICAL TESTING INSTRUCTIONS

## 🚨 NEVER LIE ABOUT TESTING RESULTS

### What "Testing" Actually Means:
1. **End-to-End Verification**: Apps must actually BUILD and RUN in iOS Simulator
2. **Wait for Completion**: Never claim success until build is 100% complete
3. **Visual Verification**: Must see the app actually working in simulator
4. **Real Modifications**: Test actual modifications on working apps
5. **Build Log Verification**: Check actual build success/failure in logs

### Before Any Testing Claims:
1. **Always check if server is running** - `ps aux | grep "python main.py"`
2. **Start server if needed** - `source venv/bin/activate && python main.py`
3. **Wait for actual build completion** - Don't just check API responses
4. **Verify in simulator** - Apps must actually launch and be functional
5. **Check build logs** - Look for actual success/failure messages

### What NOT to Do:
- ❌ Claim success based on API responses alone
- ❌ Assume generation worked without verification
- ❌ Test only request initiation and call it "testing"
- ❌ Make up test results or exaggerate success
- ❌ Rush through testing without waiting for completion

### What TO Do:
- ✅ Wait for complete build process
- ✅ Verify apps launch in iOS Simulator
- ✅ Test actual app functionality
- ✅ Check modification results visually
- ✅ Report actual failures honestly
- ✅ Only claim success when fully verified

### Testing Sequence:
1. Check server status
2. Start server if needed
3. Submit generation request
4. Wait for WebSocket completion messages
5. Verify app launches in simulator
6. Test app functionality
7. Try modifications
8. Report HONEST results

## Remember: Real testing = Real apps running in simulator