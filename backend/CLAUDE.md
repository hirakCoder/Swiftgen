# CLAUDE.md - Critical Instructions for SwiftGen Development

**READ THIS FIRST IN EVERY SESSION**

## 🚨 CRITICAL RULES

### 1. Documentation Rules
- **NEVER** create separate fix/issue documents
- **ALWAYS** update `MASTER_ISSUES_AND_FIXES.md` for any issue or fix
- **CHECK** the master document before attempting any fix
- **DO NOT** repeat fixes that have already been tried

### 2. Known Issues to Check First
Before diving into any problem, check if it's already documented:
- Modification UI delays → Already fixed with WebSocket
- SwiftUI syntax errors → Already fixed with ui_enhancement_handler
- JSON parsing errors → Fallback handlers in place
- LLMs returning unchanged files → Bug fix handlers implemented

### 3. Testing Before Claiming Success
- **NEVER** claim a fix works without testing
- **ALWAYS** verify modifications actually change files
- **CHECK** the build logs for actual changes
- **TEST** with real user scenarios

### 4. Common Pitfalls to Avoid
- Don't add more validation layers for issues already caught
- Don't trust LLM responses without verification
- Don't create new fix mechanisms for problems with existing solutions
- Don't ignore the lessons learned section

## 📋 Daily Checklist

When starting work on SwiftGen:
1. [ ] Read this CLAUDE.md file
2. [ ] Review MASTER_ISSUES_AND_FIXES.md
3. [ ] Check recent session summaries
4. [ ] Verify what's actually working vs claimed to work
5. [ ] Test basic functionality before adding features

## 🔄 Recurring Issues Reference

### Issue: "Modifications don't work"
**First check**:
- Are files actually being modified? (Check logs)
- Is it a JSON parsing error? (Fallback exists)
- Is it a known bug pattern? (Handler exists)

### Issue: "UI shows no feedback"
**First check**:
- WebSocket connected? (Fixed in index.html)
- Status messages being sent? (Fixed with delays)

### Issue: "SwiftUI syntax errors"
**First check**:
- Is ui_enhancement_handler being called?
- Are syntax fixes being applied before save?

## 🎯 Current Priorities

1. **Fix what's broken** before adding new features
2. **Test modifications** with real examples
3. **Document in master file** not separate docs
4. **Verify xAI access** with proper API key

## 🚫 What NOT to Do

1. **DON'T** create new documents for issues
2. **DON'T** implement fixes without checking if they exist
3. **DON'T** trust LLM outputs without verification
4. **DON'T** claim success without testing
5. **DON'T** add complexity to solve simple problems

## 📊 Success Metrics

A successful session includes:
- Actual working modifications (verified in simulator)
- Updated MASTER_ISSUES_AND_FIXES.md
- No repeated mistakes from previous sessions
- Real progress, not circular fixes

## 🔧 Quick Command Reference

### Test a modification
```bash
# Check if files actually changed
grep -n "Files that actually changed:" logs
```

### Verify WebSocket
```bash
# Check frontend console for WebSocket connection
```

### Check validation
```bash
# Look for "[MAIN] Applying final SwiftUI syntax validation"
```

## 💡 Remember

> "We keep going in circles because we don't check what's already been done. Break the cycle by reading the master document first."

---

**Last Updated**: December 19, 2024
**Critical**: This file and MASTER_ISSUES_AND_FIXES.md are your north star. Ignore them at your own peril.