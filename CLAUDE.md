# CLAUDE.md - SwiftGen Master Reference Document

## 🚨 CRITICAL: READ THIS FIRST
This is the MASTER REFERENCE DOCUMENT for SwiftGen. Always consult this before making any changes.

## Project Overview
SwiftGen is a world-class no-code iOS app generator that creates, modifies, and deploys Swift/SwiftUI applications based on natural language descriptions. Similar to Replit/Lovable but specifically for iOS development.

### Core Capabilities
- Generate complete iOS apps from chat descriptions
- Modify existing apps based on user requests  
- Deploy to iOS Simulator automatically
- Multi-LLM support (Claude 3.5, GPT-4, xAI Grok)
- Intelligent error recovery and auto-fixing

## 🔴 CRITICAL ISSUES & FIXES (Updated July 8, 2025)

### 1. ✅ Recovery Attempts Configuration - ALREADY FIXED
- **Status**: Already set to 5 attempts in `robust_error_recovery_system.py` line 53
- **Dynamic**: Scales with complexity (3-6 attempts based on app type)

### 2. ✅ File State Management - WORKING
- **ALWAYS** read files from disk, never from memory
- **Location**: `backend/main.py` - use `project_manager.read_project_files()`
- **Fixed**: Dec 20, 2024 - Prevents stale state issues

### 3. ✅ SSL/Certificate Errors - WORKING
- **Solution**: Use `robust_ssl_handler.py` for comprehensive fixes
- **Triggers**: External API usage, self-signed certificates
- **Fixed**: Jun 23, 2025 - Multiple detection mechanisms

### 4. ✅ NEW FIX: Semicolon Insertion Disabled
- **Issue**: Error recovery was corrupting Swift code with semicolons
- **Solution**: Disabled semicolon insertion in `robust_error_recovery_system.py`
- **Fixed**: July 8, 2025 - No more syntax corruption

### 5. ✅ NEW FIX: Forbidden iOS Features
- **Issue**: LLM generating non-existent features like `.symbolEffect(.dropShadow)`
- **Solution**: Added forbidden features list to `enhanced_prompts.py`
- **Fixed**: July 8, 2025 - Prevents generation errors

### 6. ⚠️ Modification Hanging - WORKAROUND AVAILABLE
- **Issue**: Complex modification handler causes infinite loops
- **Workaround**: Created `SimpleModificationHandler` - works perfectly
- **TODO**: Integrate into main server endpoint

## 📁 Project Structure

```
swiftgen-mvp/
├── backend/
│   ├── main.py                        # FastAPI main application
│   ├── enhanced_claude_service.py      # Multi-LLM orchestration
│   ├── intelligent_llm_router.py       # Routes to best LLM for task
│   ├── robust_error_recovery_system.py # Multi-strategy error recovery
│   ├── build_service.py               # Xcode build management
│   ├── simulator_service.py           # iOS Simulator control
│   ├── modification_handler.py        # App modification logic
│   ├── ui_enhancement_handler.py      # SwiftUI syntax fixes
│   ├── robust_ssl_handler.py          # SSL/certificate handling
│   └── rag_knowledge_base.py          # Vector DB with Swift knowledge
├── frontend/
│   └── index.html                     # Web UI with WebSocket support
└── docs/
    ├── MASTER_ISSUES_AND_FIXES.md     # All historical fixes
    └── SWIFTGEN_ENHANCEMENT_PLAN_2025.md # Future roadmap
```

## 🚦 Current Status (July 8, 2025 - Post Critical Fixes)

### ✅ Working
- Simple app generation (timer, todo, counter, calculator, weather)
- Multi-LLM failover and routing
- SSL/certificate error handling  
- Real-time UI updates via WebSocket
- Simulator deployment
- Forbidden iOS features prevention (no more .symbolEffect errors)
- Simple modification handler (no hanging)

### ⚠️ Partially Working  
- Complex modification endpoint (indentation issues in main.py)
- Full end-to-end modification through UI
- Very complex architectural changes

### ❌ Fixed Today
- ~~Timer app syntax errors (semicolon insertion)~~ ✅ FIXED
- ~~Non-existent iOS features (.symbolEffect.dropShadow)~~ ✅ FIXED
- ~~Modification requests hanging forever~~ ✅ FIXED with SimpleModificationHandler
- ~~iOS version targeting inconsistency~~ ✅ FIXED to iOS 17.0

## 🏗️ Architecture Decisions

### Multi-LLM Strategy
- **Primary**: Claude 3.5 Sonnet (best for architecture)
- **Secondary**: GPT-4 Turbo (algorithms, bug fixes)
- **Tertiary**: xAI Grok (UI design, simple tasks)
- **Routing**: Based on task type and success history

### Error Recovery Layers
1. **Prevention**: Enhanced prompts with Swift rules
2. **Validation**: Pre-build syntax and compatibility checks
3. **Pattern Recovery**: Known error → specific fix
4. **AI Recovery**: LLM-based intelligent fixes

### Agent Architecture (Planned)
- **UI Agent**: SwiftUI modifiers, animations, layouts
- **API Agent**: Network, SSL, authentication
- **Build Agent**: Xcode, provisioning, deployment
- **Architecture Agent**: MVVM, navigation, state
- **Coordinator**: Orchestrates agent collaboration

## 🛠️ Common Tasks

### Adding New Error Pattern
1. Add pattern to `robust_error_recovery_system.py`
2. Create specific fix in appropriate handler
3. Test with real error scenario
4. Document in MASTER_ISSUES_AND_FIXES.md

### Testing Modifications
```bash
# Simple modification test
"Add a dark mode toggle"

# Complex modification test  
"Add user authentication with email and password"

# Bug fix test
"Fix the count bug where beverages start at 0"
```

### Debugging Build Errors
1. Check `backend/logs/` for detailed logs
2. Look for error patterns in recovery system
3. Verify SSL fixes if using external APIs
4. Check simulator logs for runtime errors

## 🎯 Enhancement Priorities

### Immediate (This Week)
1. ✅ Create this CLAUDE.md document
2. Increase recovery attempts to 5
3. Add complexity detection
4. Document agent architecture

### Short Term (2 Weeks)
1. Implement specialized agents
2. Add template system for common patterns
3. Improve modification success rate
4. Create learning system

### Long Term (1 Month)
1. Integrate fine-tuned model
2. Add comprehensive testing suite
3. Implement caching for performance
4. Production deployment guide

## 💡 Best Practices

### When Modifying Code
1. **ALWAYS** check this document first
2. Read relevant code from disk, not memory
3. Test with simple AND complex apps
4. Update MASTER_ISSUES_AND_FIXES.md for new issues
5. Maintain backward compatibility

### LLM Prompt Engineering
1. Be explicit about Swift/SwiftUI versions (iOS 16+)
2. Include working examples in prompts
3. Specify exact file structure expected
4. Add validation rules to prevent common errors

### Error Handling
1. Never fail silently - always notify UI
2. Log detailed error information
3. Attempt recovery before failing
4. Provide actionable error messages

## 🚀 Resources

### Available Infrastructure
- **RunPod Credits**: $20 remaining
- **Oracle Free VM**: Available for services
- **Local Development**: Mac with Xcode

### API Keys Required
- CLAUDE_API_KEY (Anthropic)
- OPENAI_API_KEY (OpenAI)  
- XAI_API_KEY (xAI)
- GITHUB_TOKEN (optional, for RAG updates)

### Testing Endpoints
- Frontend: http://localhost:8000
- API: http://localhost:8000/api/
- WebSocket: ws://localhost:8000/ws/{client_id}

## 📝 Version History

### Nov 2025
- Created CLAUDE.md as master reference
- Planning agent architecture implementation
- Preparing to increase recovery attempts

### Jun 2025
- Fixed SSL/certificate handling
- Fixed infinite retry loops
- Improved error recovery

### Dec 2024
- Fixed modification state issues
- Added intelligent retry system
- Improved UI feedback

## ⚠️ WARNING: Common Pitfalls

1. **Don't Trust Memory State** - Always read from disk
2. **Don't Skip Validation** - Even if LLM claims success
3. **Don't Ignore User Feedback** - They know when it's not working
4. **Don't Create New Files During Mods** - Only modify existing
5. **Don't Assume LLM Success** - Verify actual changes

---

**Remember**: This is a production system with real users. Every change should improve reliability, not just add features.