# Instructions for Claude Code

## Project Context

You are working on SwiftGen AI, a world-class no-code iOS app builder. The system uses multiple LLMs to generate Swift/SwiftUI code from natural language descriptions.

## Current State Analysis

1. **First, examine these core files**:
   - `main.py` - Understand the API structure
   - `build_service.py` - See how builds work
   - `project_manager.py` - Understand project creation
   - `enhanced_claude_service.py` - Multi-LLM orchestration

2. **Identify the Task naming bug**:
   - Search for "struct Task" in generated code
   - This conflicts with Swift's built-in Task type
   - Causes build failures

## Implementation Guidelines

### Code Style
- Use type hints for all Python functions
- Add comprehensive error handling
- Use async/await for I/O operations
- Add logging for debugging
- Write clear comments

### Swift Code Generation Rules
1. **NEVER** use these as struct names:
   - Task → Use TodoItem, UserTask, WorkItem
   - State → Use AppState, ViewState
   - Action → Use AppAction, ViewAction

2. **String Handling**:
   - Always use double quotes "
   - Never use single quotes '
   - Fix: TextField('text') → TextField("text")

3. **Modern SwiftUI**:
   - NavigationStack not NavigationView
   - @Environment(\.dismiss) not presentationMode
   - iOS 16.0+ patterns only

### Testing Your Changes

After implementing each feature:

1. **Test Generation**:
   ```bash
   curl -X POST http://localhost:8000/api/generate \
     -H "Content-Type: application/json" \
     -d '{"description": "Create a todo list app", "app_name": "TodoMaster"}'
   ```

2. **Check for Task conflicts**:
   - Examine generated files in `workspaces/`
   - Ensure no "struct Task" exists
   - Verify build succeeds

3. **Test Modifications**:
   ```bash
   curl -X POST http://localhost:8000/api/modify \
     -H "Content-Type: application/json" \
     -d '{"project_id": "proj_xxx", "modification": "Add dark mode support"}'
   ```

## Priority Implementation Order

### Day 1: Fix Task naming conflicts
- Update project_manager.py
- Update all LLM service prompts
- Test thoroughly

### Day 2: Add syntax validation
- Create swift_syntax_validator.py
- Integrate with build_service.py
- Add pre-build validation

### Day 3: Implement RAG system
- Create rag_knowledge_base.py
- Add Swift knowledge patterns
- Integrate with LLM services

### Day 4: Enhanced error recovery
- Update robust_error_recovery_system.py
- Add multi-LLM fallbacks
- Test error scenarios

### Day 5: Quality monitoring
- Create project_health_monitor.py
- Add metrics tracking
- Generate quality reports

## Debugging Tips

1. **Enable verbose logging**:
   ```python
   # In files you're debugging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check WebSocket messages**:
   - Monitor browser console
   - Look for status updates

3. **Examine build logs**:
   - Check `workspaces/build_logs/`
   - Look for specific error patterns

## Success Criteria

Your implementation is successful when:
- No more Task/State/Action naming conflicts
- Build success rate > 95%
- Can handle 30+ modifications without degradation
- Error recovery works reliably
- Generated apps follow Apple HIG

## Questions to Ask Yourself

Before implementing:
1. Will this break existing functionality?
2. Is the error handling comprehensive?
3. Are the prompts clear and specific?
4. Is the code maintainable?
5. Have I tested edge cases?

## Red Flags to Avoid

- Don't use generic prompts - be specific
- Don't ignore error patterns - learn from them
- Don't skip validation - catch errors early
- Don't hardcode values - use configuration
- Don't forget accessibility - it's required

Remember: The goal is a world-class product that "just works" for users. Every line of code should contribute to that goal.