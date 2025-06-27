# Error Recovery System Fix Plan

## Critical Issues to Fix

### 1. Destructive Recovery Strategies

#### Pattern-Based Recovery (Line 898)
**Problem**: Comments out duplicate toolbars instead of fixing them
```python
lines[idx] = '// ' + lines[idx]  # Comment out duplicate toolbars
```
**Fix**: Properly merge toolbar content or use correct syntax

#### Last Resort Recovery (Line 1535)
**Problem**: Replaces entire app with "Hello World"
**Fix**: Should only fix syntax errors, never replace user functionality

### 2. Recovery Strategy Order

**Current Order**:
1. _pattern_based_recovery (destructive)
2. _swift_validator_recovery (accurate)
3. _swift_syntax_recovery (redundant)
4. _dependency_recovery (should be earlier)
5. _rag_based_recovery (unreliable)
6. _llm_based_recovery (expensive)

**Optimal Order**:
1. _swift_validator_recovery (most accurate, non-destructive)
2. _dependency_recovery (add missing imports early)
3. _pattern_based_recovery (only non-destructive fixes)
4. _rag_based_recovery (if validated)
5. _llm_based_recovery (last resort for complex issues)

### 3. Specific Fixes Needed

#### A. Fix Toolbar Ambiguity Properly
Instead of commenting out, fix the syntax:
```python
# Replace .toolbar(content: { }) with .toolbar { }
content = re.sub(r'\.toolbar\s*\(\s*content\s*:\s*\{', '.toolbar {', content)
# Don't comment out duplicates - merge them or keep the most complete one
```

#### B. Remove Destructive Last Resort
Replace the entire _last_resort_recovery with a method that:
- Only adds missing imports
- Fixes obvious syntax errors
- Never removes or replaces user code

#### C. Add Validation After Each Fix
```python
# After each recovery strategy
if success:
    # Validate the fix didn't make things worse
    validation_result = await self.validate_fix(modified_files)
    if not validation_result.improved:
        # Rollback to previous state
        modified_files = previous_files
```

#### D. Prevent Unnecessary Recovery
Add checks before running recovery:
```python
# Check if it's a false positive
if "ambiguous use of 'toolbar'" in errors:
    # First check if it's actually a problem
    if self.is_valid_toolbar_usage(swift_files):
        return True, swift_files, ["No actual error - toolbar usage is valid"]
```

### 4. Implementation Priority

1. **HIGH**: Fix destructive patterns (toolbar commenting, last resort)
2. **HIGH**: Reorder recovery strategies 
3. **MEDIUM**: Add validation after fixes
4. **MEDIUM**: Remove redundant strategies
5. **LOW**: Improve RAG validation

### 5. Code Changes Required

#### robust_error_recovery_system.py
1. Fix line 898 - Don't comment toolbars
2. Replace _last_resort_recovery entirely
3. Reorder strategies in _get_dynamic_recovery_strategies
4. Add validation loop after each strategy

#### swift_validator_integration.py
1. Move swift_validator to first position
2. Ensure it runs before pattern-based

#### build_service.py
1. Add pre-check to avoid unnecessary recovery
2. Validate errors are real before recovery

### 6. Testing Plan

1. Test with app that has valid duplicate toolbars
2. Test with syntax errors that should be fixed
3. Test with complex errors requiring LLM
4. Ensure no user code is ever deleted/replaced
5. Verify fixes actually improve the build

## Next Steps

1. Create non-destructive versions of all recovery strategies
2. Add rollback mechanism if fixes make things worse
3. Track which fixes actually work for learning
4. Never trust LLM output without validation
5. Preserve user intent above all else