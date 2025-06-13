# SwiftGen Recovery Analysis

## Root Cause Analysis

### 1. **Token Limit Issue**
- LLMs are set to max_tokens=4096 which is TOO SMALL for complete iOS apps
- Calculator app needs ~5000-6000 tokens for full implementation
- When limit is reached, LLM outputs "..." to indicate continuation
- This creates invalid Swift syntax: `class Calculator...`

### 2. **Error Recovery Making It Worse**
- Build fails with "Color.darkGray doesn't exist"
- Recovery system tries to fix via LLM
- LLM response is ALSO truncated due to same token limit
- Results in broken fixes that make code worse

### 3. **Multiple Recovery Attempts**
- System tries 3 times (now 2) to fix errors
- Each attempt uses same token limit
- Each fix attempt can introduce new errors
- Takes several minutes for all attempts to fail

## Immediate Fixes Applied

1. **Increased Token Limit**: 4096 → 8192 tokens
2. **Added Truncation Detection**: Check for "..." in generated code
3. **Swift Code Validator**: Pre-build validation to catch syntax errors
4. **Better Error Messages**: Show actual build errors in logs

## Why It Was Working Before

The working version likely:
- Generated simpler apps that fit within token limits
- Had different prompts that produced more concise code
- Didn't have complex error recovery that could make things worse

## Solution Strategy

### Phase 1: Prevent Truncation
- ✅ Increased token limits to 8192
- ✅ Added detection for truncated responses
- ✅ Will retry with different model if truncation detected

### Phase 2: Smarter Generation
- Enhanced prompts to generate more concise code
- Pre-validation before building
- Fix common issues (darkGray → gray) automatically

### Phase 3: Better Error Recovery
- Limit recovery attempts
- Don't use LLM for simple syntax fixes
- Use pattern-based fixes for known issues

## Testing Plan

1. Generate simple calculator app
2. Check if full code is generated (no "...")
3. Verify Color.gray is used (not darkGray)
4. Build should succeed on first attempt
5. App should launch in simulator