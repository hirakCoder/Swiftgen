# SwiftGen AI Quick Reference

## Common Fixes

### Task Naming Conflict
```python
# Before (WRONG)
struct Task {
    let id: UUID
    let title: String
}

# After (CORRECT)
struct TodoItem {
    let id: UUID
    let title: String
}
```

### String Quotes
```python
# Before (WRONG)
Text('Hello')
TextField("Name"", text: $name)

# After (CORRECT)
Text("Hello")
TextField("Name", text: $name)
```

### Environment
```python
# Before (WRONG)
@Environment(\.presentationMode) var presentationMode
presentationMode.wrappedValue.dismiss()

# After (CORRECT)
@Environment(\.dismiss) private var dismiss
dismiss()
```

## API Endpoints

- `POST /api/generate` - Generate new app
- `POST /api/modify` - Modify existing app
- `GET /api/projects` - List all projects
- `GET /api/project/{id}/status` - Get project status
- `WS /ws/{project_id}` - WebSocket for real-time updates

## File Locations

- Generated projects: `workspaces/proj_*/`
- Build logs: `workspaces/build_logs/`
- Swift knowledge: `backend/swift_knowledge/`
- Templates: `backend/templates/`

## Environment Variables

```bash
CLAUDE_API_KEY=your_key
OPENAI_API_KEY=your_key
XAI_API_KEY=your_key
PINECONE_API_KEY=your_key
```

## Testing Commands

```bash
# Start server
cd backend
python main.py

# Test generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a calculator app", "app_name": "CalcPro"}'

# Check logs
tail -f workspaces/build_logs/proj_*_build.log
```

## Common Error Patterns

- "cannot find type 'Task'" → Reserved type conflict
- "single-quoted string" → Quote style error
- "presentationMode deprecated" → Old SwiftUI pattern
- "NavigationView deprecated" → Use NavigationStack
- "unterminated string" → Quote mismatch

## Success Metrics

- Generation time: < 30 seconds
- Build success rate: > 95%
- Modification success: > 90%
- Error recovery rate: > 80%
- Code quality score: > 80/100