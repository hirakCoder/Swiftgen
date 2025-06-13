# Implementation Tasks for Claude Code

## Task 1: Fix Task Naming Conflicts

### Files to Modify

1. **project_manager.py**
   - Add `_protect_reserved_types()` method
   - Update `_deduplicate_and_fix_code()` to call protection
   - Add semantic name generation

2. **enhanced_claude_service.py**
   - Update all prompts to include naming rules
   - Add validation in `_ensure_response_has_content()`

3. **base_llm_service.py** (NEW FILE)
   - Create base class with common functionality
   - Implement `_create_safe_bundle_id()`
   - Add `_normalize_app_name_in_code()`

### Implementation Steps
```python
# 1. In project_manager.py, add this method:
def _protect_reserved_types(self, files: List[Dict]) -> Tuple[List[Dict], Dict[str, str]]:
    """Protect reserved Swift types by renaming them with semantic names"""
    reserved_types = {'Task', 'State', 'Action', 'Result', 'Error', 'Never'}
    type_mappings = {}
    
    for file in files:
        content = file.get("content", "")
        
        # Find and replace reserved types
        for reserved in reserved_types:
            if f'struct {reserved}' in content:
                new_name = self._generate_semantic_name(reserved, content)
                content = content.replace(f'struct {reserved}', f'struct {new_name}')
                type_mappings[reserved] = new_name
                
        file["content"] = content
        
    return files, type_mappings
```

## Task 2: Implement Swift Syntax Validator

Create new file: `swift_syntax_validator.py`

```python
# Key validations to implement:
1. Replace single quotes with double quotes
2. Fix @Environment issues
3. Fix NavigationView → NavigationStack
4. Balance braces
5. Add missing imports
```

## Task 3: Implement RAG Knowledge Base

1. Create new file: `rag_knowledge_base.py`
2. Set up Pinecone vector database
3. Create embedding model initialization
4. Implement knowledge loading from JSON files
5. Add search functionality
6. Integrate with LLM services

Create knowledge files in `swift_knowledge/patterns/`:
```json
// naming_conflicts.json
{
  "title": "Avoiding Swift Reserved Type Conflicts",
  "content": "// Swift code examples...",
  "tags": ["naming", "reserved-types", "conflicts"]
}
```

## Task 4: Update Build Service

Modify `build_service.py`:
1. Add `pre_build_validation()` method
2. Integrate swift_syntax_validator
3. Enhance error recovery with multi-LLM support
4. Add detailed progress reporting

## Task 5: Implement Advanced Prompt Templates

Create new file: `advanced_prompt_templates.py`
1. Create template manager class
2. Add templates for different scenarios
3. Include dynamic components
4. Ensure consistent formatting

## Task 6: Add Project Health Monitoring

Create new file: `project_health_monitor.py`
1. Implement code quality metrics
2. Add architecture compliance checks
3. Create performance analysis
4. Generate quality reports

## Testing Protocol

### After Each Implementation:
1. Test basic app generation
2. Test modification flow
3. Verify error recovery
4. Check simulator launch
5. Validate generated code quality

### Integration Tests:
```python
# Test reserved type handling
test_cases = [
    "Create a todo app with Task management",
    "Build a state machine with State pattern",
    "Make an app with Action handlers"
]

for test in test_cases:
    result = await generate_app(test)
    assert "struct Task" not in result
    assert build_succeeds(result)
```

## Deployment Checklist

- [ ] All syntax validators working
- [ ] RAG system initialized with knowledge
- [ ] Multi-LLM recovery tested
- [ ] 30+ modifications tested
- [ ] Error patterns documented
- [ ] Performance metrics acceptable
- [ ] Documentation updated