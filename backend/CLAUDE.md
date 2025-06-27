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
3. [ ] **NEW**: Check DAILY_SUMMARY_*.md from previous day
4. [ ] Check recent session summaries
5. [ ] Verify what's actually working vs claimed to work
6. [ ] Test basic functionality before adding features
7. [ ] **CRITICAL**: Review USER_STORY_TRACKER.md daily
8. [ ] **CRITICAL**: Update story status after ANY work

## 🔴 CRITICAL ACTIVE ISSUE (Dec 19, 2024)
**Modifications work initially then fail after a few attempts**
- Some mods work, then "No modifications processed due to error in chat reply"
- App rebuilds WITHOUT changes
- See TOMORROW_ACTION_PLAN.md for debug strategy

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
5. **Track user stories** - Update USER_STORY_TRACKER.md daily

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

## 📊 User Story Management Protocol

### Daily Story Review Process
1. **Start of Session**: Open USER_STORY_TRACKER.md
2. **Check Status**: Review which stories are blocked/in-progress
3. **Work on Stories**: Focus on highest priority blocked items
4. **Update Immediately**: Change status as you work
5. **Test Everything**: Run test suite after changes
6. **End of Session**: Update metrics and next actions

### Story Status Updates
- **⚠️ NOT STARTED** → **🟡 IN PROGRESS** (when you begin work)
- **🟡 IN PROGRESS** → **✅ DONE** (when ALL acceptance criteria met)
- **🟡 IN PROGRESS** → **❌ BLOCKED** (when you hit a blocker)
- **🔄 NEEDS RETEST** → Test it NOW, don't leave it hanging

### Required Documents for Story Tracking
1. **PRODUCT_USER_STORIES.md** - The requirements (what to build)
2. **USER_STORY_TRACKER.md** - The status (what's done/blocked)
3. **test_suite.py** - The validation (prove it works)

### Before Claiming ANY Story is Complete
- [ ] All acceptance criteria met
- [ ] Automated test passing
- [ ] No regressions introduced
- [ ] Updated tracker with results

## 💡 Remember

> "We keep going in circles because we don't check what's already been done. Break the cycle by reading the master document first."

> "I want to build a proper strategy and a document with all the user stories... Then I want you to make a tracker that will track the completion, issues related to each user story"

---

**Last Updated**: December 19, 2024 → Updated June 25, 2025 with User Story Tracking
**Critical**: This file, MASTER_ISSUES_AND_FIXES.md, and USER_STORY_TRACKER.md are your north star. Ignore them at your own peril.