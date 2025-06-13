# SwiftGen Daily Issues Tracker

## December 13, 2024 - Morning Session

### Critical Issues Found:

1. **WebSocket Connection Failure**
   - Status: CRITICAL
   - Issue: "No active connections for proj_XXX" messages throughout generation
   - Impact: UI doesn't receive any progress updates
   - Root Cause: Frontend WebSocket connection timing issue
   
2. **LLM Code Generation Quality**
   - Status: HIGH
   - Issue: Generated code has multiple build errors from the start
   - Example: Scientific Calculator had 4 errors on first attempt
   - Impact: Requires multiple recovery attempts
   
3. **Auto-Fix System Failure**
   - Status: CRITICAL
   - Issue: Recovery system runs twice but still fails to fix all errors
   - Example Errors:
     - "cannot find 'CalculatorButtonView' in scope"
     - "switch must be exhaustive"
   - Impact: Build fails after 3 attempts
   
4. **UI Progress Display**
   - Status: HIGH
   - Issue: Progress bar doesn't show during generation
   - Impact: User has no visibility into generation status
   
5. **UI Error Handling**
   - Status: CRITICAL
   - Issue: UI doesn't reflect backend failures
   - Impact: User thinks generation is still running when it has failed

### Previous Issues (Fixed on Dec 12):
- ✅ Multiple simulator launches
- ✅ App launching loop
- ✅ Favicon 404 error

### Action Items:
1. ✅ Fix WebSocket connection timing - Made API async with background tasks
2. ✅ Improve prompt engineering - Added rules for exhaustive switches and type consistency
3. ✅ Enhance error recovery - Added patterns for "type not found" and "switch exhaustive" errors
4. ✅ Debug UI progress - Fixed element IDs (statusPanel vs progressContainer)
5. ✅ Implement error propagation - Enhanced complete/error message handlers

### Fixes Applied Today:

1. **WebSocket Connection**
   - Made `/api/generate` endpoint async using BackgroundTasks
   - Frontend sends project_id with request
   - Backend accepts frontend's project_id
   - WebSocket connects before API call completes

2. **LLM Prompt Improvements**
   - Added rule: Switch statements MUST be exhaustive
   - Added rule: All referenced types MUST be defined
   - Added rule: Component interfaces must be consistent
   - Added validation section to verify code will compile

3. **Error Recovery Enhancements**
   - Added new error patterns: exhaustive_switch, type_not_found
   - Updated error analysis to categorize new error types
   - Enhanced recovery prompt with specific instructions for each error type

4. **UI Progress Display**
   - Fixed element ID mismatch (statusPanel vs progressContainer)
   - Updated progress methods to work with stage-based UI
   - Added timer functionality
   - Progress now shows during generation

5. **Error Handling in UI**
   - Enhanced 'complete' message handler to check for failed status
   - Improved 'error' message handler with proper UI updates
   - Errors now properly displayed with build logs
   - UI state correctly updated on failures

## December 13, 2024 - Afternoon Session

### New Issue Found:
1. **App Launching in Loop**
   - Status: FIXED
   - Issue: App was being launched multiple times after installation
   - Root Cause: 
     - iOS Simulator auto-launches apps after installation
     - `xcrun simctl launch --console` was timing out
     - Retry mechanism was terminating and relaunching the app
   
### Fix Applied:

1. **Smart Launch Detection**
   - Added `is_app_running()` method to check if app is already running
   - Check if app auto-launched after installation before attempting manual launch
   - Only launch if app is not already running
   
2. **Launch Command Optimization**
   - Removed `--console` flag which was causing hangs
   - Reduced launch timeout from 60s to 10s
   - Added fallback check to verify app is running even if launch command fails

### Code Changes:
- `simulator_service.py:295-312` - Added `is_app_running()` method
- `simulator_service.py:246-261` - Modified install flow to check for auto-launch
- `simulator_service.py:180-194` - Optimized launch command and added fallback

## December 13, 2024 - Late Afternoon Session

### Issues Found:
1. **Chat Not Understanding Modifications**
   - Status: FIXED
   - Issue: Users had to explicitly say "modify" for modifications to work
   - Root Cause: Chat handler was properly detecting modifications but UI wasn't clear
   
2. **Modification Build Failures**
   - Status: FIXED  
   - Issue: Duplicate SettingsView.swift files causing build errors
   - Root Cause: Project manager wasn't checking for duplicate filenames
   - Error: "Filename 'SettingsView.swift' used twice"
   
3. **UI Progress Not Meaningful for Modifications**
   - Status: FIXED
   - Issue: Progress stages showed creation messages during modifications
   - UI stage labels were too small and gray (hard to see)
   
### Fixes Applied:

1. **Enhanced Modification Error Handling**
   - Modified `/api/modify` endpoint to return proper error responses instead of HTTPException
   - Frontend now handles failed status properly with error display
   - Better error messages shown to users

2. **Duplicate File Prevention** (via GitHub fix)
   - Project manager now detects duplicate filenames before writing
   - Keeps first occurrence, skips duplicates
   - Cleans up existing duplicate files

3. **Improved Modification UI Progress**
   - Added `initializeModificationProgress()` with modification-specific messages
   - Progress stages now show: Analyzing → Updating → Rebuilding → Reinstalling → Relaunching
   - Enhanced `handleStatusUpdate()` to recognize modification-specific status messages

4. **Enhanced Stage Label Visibility**
   - Active stages now show with blue text and medium font weight
   - Completed stages show with green text
   - Labels update dynamically during progress
   - Reset properly clears all styling

### Code Changes:
- `main.py:901-920` - Return error response instead of HTTPException
- `app.js:336-347` - Added modification progress initialization
- `app.js:98-112` - Added `initializeModificationProgress()` method
- `app.js:669-702` - Enhanced status message handling for modifications
- `app.js:382-414` - Improved error handling in modification response
- `app.js:793-850` - Enhanced stage UI updates with label color changes
- `app.js:761-792` - Updated reset to clear label styling

## December 13, 2024 - Evening Session

### Critical Issue Found:
1. **Chat Not Understanding Modifications AT ALL**
   - Status: FIXED
   - Issue: When user said "can you add dark theme?", bot responded with generic "I can create iOS apps" message
   - Root Cause: DUPLICATE IMPLEMENTATION! 
     - index.html had old SwiftGenApp class (lines 396-1354)
     - app.js had new SwiftGenChat class
     - app.js was NOT being loaded in HTML
     - Old implementation was handling all chat, ignoring project context
   
### Fix Applied:

1. **Removed Duplicate Implementation**
   - Added `<script src="app.js" defer></script>` to index.html
   - Renamed SwiftGenApp to SwiftGenApp_DISABLED to prevent conflicts
   - Modified initialization to use SwiftGenChat from app.js
   
2. **Fixed Intent Analysis**
   - Updated analyzeIntent() to ALWAYS treat messages as modifications when project exists
   - Added debug logging to track WebSocket vs local handling
   - Enhanced handleQuestion() to redirect to modifications when project active

3. **Enhanced Backend Keywords**
   - Added 'dark', 'theme', 'mode', 'style' to recognized UI elements

### Code Changes:
- `index.html:12` - Added app.js script tag
- `index.html:397` - Disabled old SwiftGenApp class
- `index.html:1356` - Changed initialization to use SwiftGenChat
- `app.js:238-249` - Fixed analyzeIntent to prioritize modifications
- `app.js:188-204` - Added debug logging for chat handling
- `app.js:449-455` - Made handleQuestion context-aware
- `main.py:1037-1038` - Added theme-related keywords

### Immediate Hotfix Applied:

1. **Fixed Breaking Changes**
   - Status: FIXED
   - Issue: app.js file was 404 (not being served by FastAPI)
   - Issue: SwiftGenChat not defined error
   - Fix: 
     - Added `/app.js` endpoint to serve the file
     - Reverted to original SwiftGenApp implementation temporarily
     - Fixed question detection to prioritize modifications when project active

### Code Changes:
- `main.py:223-229` - Added app.js endpoint to serve the file
- `index.html:616-637` - Fixed handleSubmit to treat all inputs as modifications when project exists

## June 13, 2025 - Morning Session

### CRITICAL BREAKING ISSUE:
1. **Core Data Entity Generation Failure**
   - Status: FIXED (temporarily by avoiding Core Data)
   - Issue: Apps using Core Data fail with "cannot find type 'ReminderEntity' in scope"
   - Root Cause: LLM generates Core Data setup but NOT the entity classes
   - Example: Reminder app had PersistenceController but no ReminderEntity class
   - Impact: Build fails after multiple recovery attempts
   
2. **JSON Parsing Error in Modifications**
   - Status: FIXED
   - Issue: Modification requests failing with "Invalid \escape" JSON error
   - Root Cause: LLM response contained unescaped characters in JSON
   - Impact: Modifications stuck on "AI analyzing" with backend error

3. **Careless Code Changes**
   - Status: ACKNOWLEDGED
   - Issue: Multiple changes made without proper testing
   - Examples:
     - Indentation error in main.py line 737
     - Not maintaining daily documentation
     - Creating random files instead of organized tracking
   
### Why It Broke:
The Core Data issue wasn't directly caused by recent changes. It's been a latent issue where:
1. The LLM sometimes generates Core Data boilerplate
2. But doesn't generate the actual entity classes
3. The error recovery system wasn't handling this specific case
4. Recent prompt changes may have made Core Data generation more likely

### Fixes Applied:

1. **JSON Parsing Enhancement**
   - Added multi-stage JSON parsing in `enhanced_claude_service.py`
   - Better error handling with fallback strategies
   - Clear error messages instead of crashes
   
2. **Core Data Avoidance (Temporary)**
   - Updated `simple_generation_prompts.py` - Added Core Data to forbidden patterns
   - Updated `enhanced_prompts.py` - Added instruction to avoid Core Data
   - This ensures apps use simple in-memory storage
   
3. **Fixed Indentation Error**
   - Fixed main.py line 737 indentation issue
   
### Code Changes:
- `enhanced_claude_service.py:361-413` - Added robust JSON parsing with error handling
- `enhanced_claude_service.py:344-350` - Added JSON formatting rules to prompt
- `main.py:736-752` - Fixed indentation in else block
- `main.py:754-775` - Added try-except for JSON errors
- `simple_generation_prompts.py:30-31` - Added Core Data to forbidden patterns
- `enhanced_prompts.py:27-30` - Added Core Data avoidance instruction

### Files Created (Need Consolidation):
- ERROR_RECOVERY_IMPROVEMENTS.md
- test_recovery_comprehensive.py
- demo_recovery.py
- test_json_fix.py
- test_modification_fix.py
- QUICK_FIX.md
- FIX_SUMMARY.md

### Lessons Learned:
1. ALWAYS test core functionality before making enhancements
2. Maintain DAILY_ISSUES.md religiously
3. Don't create random documentation files
4. Test with various app types (including Core Data apps)
5. Handle LLM response parsing more robustly

### Action Items:
- [ ] Consolidate all random .md files into proper documentation
- [ ] Add Core Data entity generation to error recovery
- [ ] Improve LLM prompts to generate complete Core Data implementations
- [ ] Add integration tests for various app types