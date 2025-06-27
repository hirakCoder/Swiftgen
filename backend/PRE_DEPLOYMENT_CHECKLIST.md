# Pre-Deployment Checklist

## ⚠️ STOP - DO NOT DEPLOY WITHOUT COMPLETING THIS CHECKLIST

### 1. Run Automated Tests
```bash
cd backend
python run_tests.py
```

**All tests MUST pass before proceeding!**

### 2. Verify Critical User Stories

#### US-1.1: Calculator Generation
- [ ] Generates without syntax errors
- [ ] Builds in < 2 minutes
- [ ] All arithmetic operations work

#### US-2.1: Currency Converter
- [ ] SSL configuration applied automatically
- [ ] Real-time data fetches successfully
- [ ] No "Failed to load" errors

#### US-3.1: Color Modifications
- [ ] Modifications complete without syntax errors
- [ ] Only requested changes are made
- [ ] App still builds successfully

### 3. Performance Metrics
- [ ] Build time < 2 minutes for simple apps
- [ ] Modifications complete in < 1 minute
- [ ] No infinite retry loops

### 4. Error Handling
- [ ] User-friendly error messages displayed
- [ ] No technical jargon in user-facing errors
- [ ] Recovery attempts limited to prevent loops

### 5. Regression Tests
Run specific regression tests for previously broken features:

```bash
# Test calculator generation (was broken with syntax errors)
python run_tests.py calculator

# Test currency converter (was broken with SSL issues)
python run_tests.py currency

# Test modifications (was broken with syntax errors)
python run_tests.py modifications
```

### 6. Manual Smoke Tests
Perform these manual tests before deployment:

1. **Generate Simple App**:
   - Description: "Create a simple calculator app"
   - Verify: Opens in simulator, all buttons work

2. **Generate API App**:
   - Description: "Create a currency converter with real-time rates"
   - Verify: Data loads, no SSL errors

3. **Modify App**:
   - Request: "Change the background color to blue"
   - Verify: Only color changes, app still works

### 7. Documentation Updates
- [ ] USER_STORY_TRACKER.md updated with test results
- [ ] Any new issues added to tracker
- [ ] Test report saved with timestamp

### 8. Final Verification
```bash
# Run full test suite one more time
python run_tests.py

# Check test report
cat test_report.json | jq '.summary'
```

## 🚫 DO NOT DEPLOY IF:
- Any test fails
- Build time > 6 minutes
- Modifications introduce syntax errors
- SSL configuration not working
- Error recovery creates more errors

## ✅ SAFE TO DEPLOY WHEN:
- All automated tests pass (100%)
- Manual smoke tests verified
- No regression from previous fixes
- Performance metrics met
- Documentation updated

---

**Remember**: The user explicitly stated they're "tired of doing the same things again and again". Breaking production again will destroy trust completely. Test everything!