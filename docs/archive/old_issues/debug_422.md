# 422 Error Investigation

## Problem
The frontend is getting a 422 (Unprocessable Entity) error when calling `/api/generate` endpoint.

## Analysis

### Frontend Code (index.html, line 671-673)
```javascript
const payload = this.currentProjectId
    ? { project_id: this.currentProjectId, modification: input }
    : { description: input, ios_version: document.getElementById('iosVersion').value, project_id: projectId };
```

### Backend Expected Payload for `/api/generate` (models.py)
```python
class GenerateRequest(BaseModel):
    description: str  # REQUIRED
    app_name: Optional[str] = None
    project_id: Optional[str] = None
    ios_version: Optional[str] = "17.0"
```

### Potential Issues

1. **Incorrect endpoint for modifications**: 
   - When `this.currentProjectId` exists, the payload contains `modification` instead of `description`
   - But the endpoint selection (line 659) should handle this: `const endpoint = this.currentProjectId ? '/api/modify' : '/api/generate';`

2. **Missing required field**:
   - The `/api/generate` endpoint REQUIRES a `description` field
   - If the payload is missing this field, it will return 422

3. **Null/undefined values**:
   - `document.getElementById('iosVersion').value` might return null
   - The `input` variable might be empty

## Possible Causes of 422 Error

1. **Empty description**: If `input` is empty or undefined
2. **Invalid iOS version**: If the select element returns null
3. **Wrong payload to wrong endpoint**: Modification payload sent to generate endpoint
4. **Type mismatch**: String expected but different type sent

## Solution

To fix this, we need to:
1. Add better error handling and logging
2. Validate inputs before sending
3. Ensure the correct endpoint is used with the correct payload
4. Show the actual validation error from the backend to the user