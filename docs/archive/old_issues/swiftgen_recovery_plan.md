# SwiftGen Recovery Plan: From Broken to Working

## Executive Summary
SwiftGen was a working iOS app generator that could create, build, launch, and modify apps. Through attempted enhancements, multiple breaking changes were introduced. This document provides a systematic approach to restore full functionality.

## Current State Assessment

### What Was Working (Original System)
- ✅ App generation from natural language descriptions
- ✅ Swift code generation via Claude API
- ✅ Xcode project building
- ✅ iOS Simulator launching
- ✅ App modification capabilities
- ✅ Real-time status updates via WebSocket

### What's Currently Broken
1. **WebSocket 403 Errors** - Frontend connecting to `/ws` instead of `/ws/{project_id}`
2. **JSON Module Shadowing** - Variable named `json` shadowing the module import
3. **Missing Method Errors** - `_fix_with_claude` doesn't exist
4. **Parameter Mismatches** - `project_files` vs `swift_files`
5. **Pydantic Validation** - `BuildResult` expecting `log_path` field
6. **Claude API Model** - Using deprecated model name
7. **Method Not Found** - `generate_ios_app_multi_llm` doesn't exist

## Recovery Strategy

### Phase 1: Critical Fixes (Get Basic Functionality Working)

#### Fix 1: BuildResult Model (Immediate Fix)
**File**: `backend/models.py`
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BuildResult(BaseModel):
    success: bool
    errors: List[str] = []
    warnings: List[str] = []
    build_time: float
    output_path: Optional[str] = None
    simulator_launched: bool = False
    log_path: Optional[str] = None  # Add this field with default None
```

#### Fix 2: build_service.py Parameter Fix
**Line ~246**: Change `project_files=swift_files` to `swift_files=swift_files`

#### Fix 3: WebSocket Connection Fix
**File**: `frontend/index.html` or `app.js`
- Change WebSocket connection from `/ws` to `/ws/${projectId}` after project creation

### Phase 2: Method Compatibility Fixes

#### Fix 4: Enhanced Claude Service
Create a compatibility layer in `enhanced_claude_service.py`:
```python
async def generate_ios_app_multi_llm(self, description: str, app_name: str = None):
    """Compatibility method"""
    if hasattr(self, 'generate_ios_app'):
        return await self.generate_ios_app(description, app_name)
    else:
        # Fallback to generate_text with proper prompt
        prompt = f"Generate iOS app: {description}"
        result = self.generate_text(prompt)
        return json.loads(result["text"]) if result["success"] else None

async def _fix_with_claude(self, *args, **kwargs):
    """Compatibility method for error recovery"""
    return await self.modify_ios_app(*args, **kwargs)
```

#### Fix 5: Update Claude Model Name
**File**: `enhanced_claude_service.py`
```python
model_id="claude-3-5-sonnet-20241022"  # Current model (not the deprecated one)
```

### Phase 3: Restoration Testing Checklist

1. **Start Server Test**
   ```bash
   cd backend
   python main.py
   ```
   - [ ] Server starts without syntax errors
   - [ ] No import errors
   - [ ] API endpoints available

2. **Generate App Test**
   - [ ] Create simple calculator app
   - [ ] WebSocket connects properly
   - [ ] Status updates display
   - [ ] Code generation completes
   - [ ] Files have content

3. **Build Test**
   - [ ] Xcode project generates
   - [ ] Build process completes
   - [ ] No parameter mismatch errors
   - [ ] Error recovery works if needed

4. **Simulator Test**
   - [ ] App launches in simulator
   - [ ] No crash on launch

5. **Modification Test**
   - [ ] Can modify existing app
   - [ ] Changes are applied
   - [ ] Rebuild succeeds

## Implementation Order

1. **Day 1 - Critical Fixes**
   - Fix models.py (add log_path)
   - Fix build_service.py parameter
   - Test server startup

2. **Day 2 - Method Compatibility**
   - Add compatibility methods
   - Fix Claude model name
   - Test generation flow

3. **Day 3 - WebSocket & Frontend**
   - Fix WebSocket connection
   - Test real-time updates
   - Verify UI functionality

4. **Day 4 - Full Integration Test**
   - End-to-end testing
   - Document any remaining issues
   - Create rollback plan

## Rollback Strategy

If fixes don't work, revert to last known working state:

1. **Identify Working Commit**
   ```bash
   git log --oneline | head -20
   # Find commit before enhancement attempts
   ```

2. **Create Backup Branch**
   ```bash
   git checkout -b recovery-backup
   git checkout main
   ```

3. **Revert Files Selectively**
   ```bash
   git checkout <working-commit> -- backend/build_service.py
   git checkout <working-commit> -- backend/models.py
   git checkout <working-commit> -- backend/enhanced_claude_service.py
   ```

## Claude Code Implementation Guide

### Task 1: Fix Immediate Errors
```
Please fix the SwiftGen project. The main issues are:
1. In models.py, BuildResult is missing log_path field - add it with Optional[str] = None
2. In build_service.py line ~246, change project_files=swift_files to swift_files=swift_files
3. Test that the server starts without errors
```

### Task 2: Add Compatibility Methods
```
In enhanced_claude_service.py, add these compatibility methods:
- generate_ios_app_multi_llm() that calls generate_ios_app()
- _fix_with_claude() that calls modify_ios_app()
Update the Claude model to: claude-3-5-sonnet-20241022
```

### Task 3: Fix WebSocket
```
In the frontend JavaScript, update WebSocket connection:
- Change from: new WebSocket('/ws')
- Change to: new WebSocket(`/ws/${projectId}`)
- Ensure projectId is available after project creation
```

## Success Criteria

The system is considered "recovered" when:
1. Can generate a calculator app from description
2. App builds without errors
3. App launches in simulator
4. Can modify the app (e.g., "change button color to blue")
5. No WebSocket 403 errors
6. No missing method errors
7. No parameter mismatch errors

## Lessons Learned

1. **Never modify all systems at once** - Changes should be incremental
2. **Maintain backwards compatibility** - Add new methods, don't remove old ones
3. **Test each change** - Don't accumulate multiple untested changes
4. **Version control discipline** - Commit working states before major changes
5. **Error handling** - Add try/catch blocks around new features

## Contact for Support

If you encounter issues during recovery:
1. Document the exact error message
2. Note which step you were on
3. Check if reverting the specific file helps
4. Consider rolling back to last working commit as final option

---

**Remember**: The goal is to get back to a working state first, then carefully add enhancements one at a time with proper testing.