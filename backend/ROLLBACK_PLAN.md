# Rollback Plan - Restore Working State

## What's Broken
1. Simple modifications failing with syntax errors
2. Error recovery creating MORE errors
3. LLMs generating broken Swift code
4. Build taking too many attempts

## Root Causes
1. Too many "fixes" layered on top of each other
2. Error recovery system too aggressive
3. LLM prompts not enforcing proper syntax
4. No validation before attempting builds

## Rollback Strategy

### Option 1: Git Reset (Nuclear)
```bash
git reset --hard 97eab87  # Before any of today's changes
```
- Pros: Guaranteed to restore working state
- Cons: Loses SSL fixes (but those can be reapplied properly)

### Option 2: Selective Revert
1. Remove build_service_patch.py
2. Remove user_communication_service integration
3. Restore original error recovery limits
4. Keep only the essential SSL fix

### Option 3: Fix Forward (Current Approach)
1. Fix the immediate syntax errors
2. Reduce error recovery attempts
3. Add syntax validation before builds
4. Test thoroughly

## Immediate Actions

1. **Disable Aggressive Error Recovery**
   - Limit to 1 retry instead of 3-5
   - Don't create new files during modifications
   - Stop if syntax errors detected

2. **Fix LLM Prompts**
   - Enforce proper Swift syntax
   - No experimental features
   - Test output before returning

3. **Add Pre-Build Validation**
   - Check for obvious syntax errors
   - Verify file structure
   - Ensure imports are correct

## Testing Protocol

After any change:
1. Generate simple calculator app
2. Add a button (simple modification)
3. Generate currency converter
4. Change colors (simple modification)

If ANY of these fail, rollback immediately.