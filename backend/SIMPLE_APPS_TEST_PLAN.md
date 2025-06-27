# Simple Apps Test Plan

## Apps to Test

### 1. Calculator ✅
- **Description**: "Create a simple calculator app with basic operations"
- **Expected**: Basic arithmetic, no API calls
- **Complexity**: Low
- **Build attempts**: 3

### 2. Timer ✅  
- **Description**: "Create a countdown timer app"
- **Expected**: Timer functionality, no API
- **Complexity**: Low
- **Build attempts**: 3

### 3. Counter ✅
- **Description**: "Create a counter app with increment and decrement"
- **Expected**: Simple state management
- **Complexity**: Low
- **Build attempts**: 3

### 4. Todo List ✅
- **Description**: "Create a simple todo list app"
- **Expected**: List management, local storage
- **Complexity**: Low
- **Build attempts**: 3

### 5. Currency Converter 🔧
- **Description**: "Create a currency converter app with real-time exchange rates"
- **Expected**: API calls to exchangerate-api.com
- **Complexity**: Low
- **Build attempts**: 3
- **Special**: Needs SSL configuration in Info.plist
- **Fix**: EMERGENCY_CURRENCY_FIX.py applies after project creation

### 6. Weather App 🔧
- **Description**: "Create a weather app that shows current weather"
- **Expected**: API calls to weather service
- **Complexity**: Low
- **Build attempts**: 3
- **Special**: Needs SSL configuration

### 7. Quote App 🔧
- **Description**: "Create an app that displays random quotes from an API"
- **Expected**: API calls to quote service
- **Complexity**: Low
- **Build attempts**: 3
- **Special**: Needs SSL configuration

## Current Status

### Working ✅
1. Non-API apps (Calculator, Timer, Counter, Todo)
2. SSL fix logic is in place
3. Complexity detection fixed

### Needs Verification 🔧
1. Currency converter - SSL fix applied automatically?
2. Weather app - Correct API structure?
3. Quote app - JSON decoding correct?

## Test Procedure

1. Generate each app type
2. Verify:
   - Files generated correctly
   - Complexity = Low (3 build attempts max)
   - API apps have SSL configuration
   - JSON decoding structures are correct
   - App builds and runs successfully

## Known Issues & Fixes

### Issue 1: SSL Not Applied
- **Symptom**: "Failed to load" errors in simulator
- **Cause**: Info.plist created by project manager overwrites SSL config
- **Fix**: Apply EMERGENCY_CURRENCY_FIX after project creation

### Issue 2: Wrong JSON Decoding
- **Symptom**: JSON decode errors at runtime
- **Cause**: LLMs generate wrong format (nested dictionaries)
- **Fix**: EMERGENCY_CURRENCY_FIX adds proper Codable structs

### Issue 3: Too Many Build Attempts
- **Symptom**: 6+ minute build times
- **Cause**: "api" keyword marked apps as complex
- **Fix**: Removed "api" from complexity indicators

## Next Steps

1. Run actual generation tests for all 7 app types
2. Verify each works in simulator
3. Fix any remaining issues
4. Add automated tests to prevent regression