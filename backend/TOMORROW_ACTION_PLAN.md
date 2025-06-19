# Action Plan for Fixing Modification Failures

## Critical Observation
**Some modifications worked, then they stopped working**. This suggests:
1. The modification system CAN work
2. Something degrades or breaks after multiple uses
3. It's not a fundamental design flaw but likely a state/memory issue

## Hypothesis
Possible causes for degradation:
1. **Memory/State accumulation** - Something not being cleared between modifications
2. **Token limits** - Context growing too large after multiple mods
3. **WebSocket issues** - Connection degrading over time
4. **LLM context pollution** - Previous modifications affecting new ones

## Tomorrow's Debug Plan

### Step 1: Reproduce the Issue (30 min)
1. Create fresh simple app (Todo or Counter)
2. Make 3-4 successful modifications
3. Document EXACTLY when it stops working
4. Save all logs from working AND failing attempts

### Step 2: Add Comprehensive Logging (1 hour)
Add logging at EVERY step of modification flow:

```python
# In main.py - /api/chat endpoint
logger.info(f"[MOD-1] Chat request received: {request.message[:50]}")
logger.info(f"[MOD-2] Project ID: {request.project_id}")
logger.info(f"[MOD-3] Context size: {len(str(request.context))}")

# In modification endpoint
logger.info(f"[MOD-4] Modification endpoint called")
logger.info(f"[MOD-5] Files to modify: {len(files_to_modify)}")
logger.info(f"[MOD-6] Modification request: {request.modification}")

# In enhanced_claude_service.py
logger.info(f"[MOD-7] LLM modification started")
logger.info(f"[MOD-8] Using LLM: {self.current_model}")
logger.info(f"[MOD-9] Response received, length: {len(response)}")
logger.info(f"[MOD-10] JSON parsing result: {success}")
```

### Step 3: Find the Failure Point (1 hour)
1. Run the reproduction test with new logging
2. Identify EXACTLY where the flow breaks
3. Compare logs from working vs failing modifications
4. Look for differences in:
   - Context size
   - Memory usage
   - WebSocket state
   - LLM responses

### Step 4: Common Patterns to Check

#### A. Context Size Issue
```python
# Check if context is growing unbounded
if len(str(context)) > 10000:
    logger.warning("Context very large, may cause issues")
```

#### B. WebSocket State
```python
# Check WebSocket health before each modification
if not ws_healthy:
    reconnect_websocket()
```

#### C. File State Mismatch
```python
# Ensure we're using latest files
current_files = project_manager.read_current_files()
if len(current_files) != len(expected_files):
    logger.error("File count mismatch!")
```

### Step 5: Implement Fix Based on Findings

Most likely fixes:
1. **Clear context between modifications**
2. **Reset WebSocket connection**
3. **Limit context size sent to LLM**
4. **Ensure fresh file reads**

## Key Places to Investigate

1. **`/api/chat` endpoint** (main.py ~line 1300)
   - How is context handled?
   - Is message routing working?

2. **`/api/modify` endpoint** (main.py ~line 1000)
   - Are we getting fresh files?
   - Is context being passed correctly?

3. **`enhanced_claude_service.modify_ios_app_multi_llm`**
   - Is the LLM getting the right prompt?
   - Are responses being parsed correctly?

4. **Frontend WebSocket handling**
   - Is connection stable?
   - Are messages being queued?

## Success Criteria
- [ ] Can make 10+ modifications in a row without failure
- [ ] Each modification actually appears in the app
- [ ] Clear error messages when things fail
- [ ] No "phantom successes" (app launches without changes)

## Time Estimate
- Morning: Steps 1-3 (2.5 hours) - Find the issue
- Afternoon: Steps 4-5 (2 hours) - Fix and test
- Total: 4-5 hours to completely resolve

## Remember
- Read THIS document first tomorrow
- Don't get sidetracked by other issues
- Focus ONLY on why modifications degrade over time
- Test with REAL user workflows, not individual components