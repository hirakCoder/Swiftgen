# Intelligent Multi-LLM Routing System

## Overview

The SwiftGen backend now implements an intelligent multi-LLM routing system that strategically utilizes different Language Learning Models (Claude 3.5, GPT-4, and xAI) based on their specific strengths. This approach maximizes success rates and provides better user experiences by matching request types to the most suitable LLM.

## Architecture

### Components

1. **IntelligentLLMRouter** (`intelligent_llm_router.py`)
   - Analyzes incoming requests to determine their type
   - Routes requests to the most appropriate LLM
   - Provides fallback strategies when initial attempts fail
   - Tracks success rates for continuous learning

2. **Enhanced Claude Service** (`enhanced_claude_service.py`)
   - Integrates the router for intelligent LLM selection
   - Manages multiple LLM providers (Anthropic, OpenAI, xAI)
   - Handles fallback with specialized prompts
   - Records results for improving future routing

## Request Analysis

The system analyzes requests to categorize them:

### Request Types
- **UI_DESIGN**: Color, layout, animation, visual elements
- **ALGORITHM**: Sorting, searching, computational logic
- **DATA_MODEL**: Database, storage, API integration
- **NAVIGATION**: Screen transitions, routing
- **BUG_FIX**: Error fixes, crash resolution
- **SIMPLE_MODIFICATION**: Basic text/label changes
- **COMPLEX_MODIFICATION**: Multi-file architectural changes

### Keyword Analysis
```python
ui_keywords = ['color', 'background', 'animation', 'layout', 'design', 'theme', ...]
algorithm_keywords = ['algorithm', 'sort', 'search', 'calculate', 'optimize', ...]
data_keywords = ['model', 'data', 'database', 'storage', 'cache', 'api', ...]
```

## Routing Strategy

### Initial Routing Map
```python
RequestType.UI_DESIGN → Claude (excels at UI/UX)
RequestType.ALGORITHM → GPT-4 (strong at algorithms)
RequestType.DATA_MODEL → GPT-4 (good at data structures)
RequestType.NAVIGATION → Claude (understands context)
RequestType.BUG_FIX → GPT-4 (good at debugging)
RequestType.SIMPLE_MODIFICATION → xAI (fast for simple tasks)
RequestType.COMPLEX_MODIFICATION → Claude (handles complexity)
```

### Fallback Chains

When an LLM fails, the system uses intelligent fallback strategies:

#### UI Design Fallback
1. Claude (standard approach)
2. GPT-4 (component-based approach)
3. Claude (step-by-step with examples)
4. xAI (simplified implementation)

#### Algorithm Fallback
1. GPT-4 (standard implementation)
2. Claude (explain then implement)
3. GPT-4 (alternative algorithm)
4. xAI (basic implementation)

## Specialized Prompts

Each LLM receives tailored prompts based on the strategy:

### Claude - Step-by-Step
```
Please implement this step-by-step:
1. First, identify all files that need modification
2. For each file, explain what changes are needed
3. Implement the changes with clear comments
4. Provide usage examples in comments

IMPORTANT: For UI modifications, especially colors:
- Use .listRowBackground() for List items, not .background()
- Define colors clearly (e.g., Color.blue, Color("CustomColor"))
- Test with both light and dark modes in mind
```

### GPT-4 - Component-Based
```
Break this down into components:
1. Identify each component that needs modification
2. Implement changes component by component
3. Ensure proper data flow between components
4. Add appropriate comments explaining the implementation
```

### xAI - Simplified
```
Implement this in the simplest way possible:
- Focus on making it work first
- Use standard SwiftUI patterns
- Avoid complex abstractions
- Add clear comments
```

## Success Rate Tracking

The system continuously learns from results:

```python
# Initial success rates (based on analysis)
success_rates = {
    "claude": {"ui_design": 0.85, "algorithm": 0.75, "default": 0.80},
    "gpt4": {"ui_design": 0.70, "algorithm": 0.90, "default": 0.82},
    "xai": {"ui_design": 0.65, "algorithm": 0.78, "default": 0.75}
}
```

Success rates are updated using a moving average:
```python
new_rate = (current_rate * 0.9) + (success ? 1.0 : 0.0) * 0.1
```

## Implementation Flow

### App Generation
1. Router analyzes the app description
2. Selects initial LLM based on request type
3. If generation fails, uses intelligent fallback
4. Records success/failure for learning

### App Modification
1. Router analyzes the modification request
2. Selects LLM best suited for the modification type
3. Creates specialized prompts based on LLM and strategy
4. Falls back intelligently if needed
5. Tracks results for improvement

## Usage Examples

### Example 1: UI Color Modification
```
User: "Add red background color to task categories"
→ Analyzed as: UI_DESIGN
→ Routed to: Claude
→ Strategy: Standard approach with SwiftUI-specific guidance
→ Specialized prompt includes: .listRowBackground() usage
```

### Example 2: Sorting Algorithm
```
User: "Implement efficient task sorting by priority and date"
→ Analyzed as: ALGORITHM
→ Routed to: GPT-4
→ Strategy: Standard implementation
→ Fallback available: Claude with "explain then implement"
```

### Example 3: Simple Text Change
```
User: "Change app title from 'Tasks' to 'My Tasks'"
→ Analyzed as: SIMPLE_MODIFICATION
→ Routed to: xAI
→ Strategy: Direct modification
→ Fast execution for simple change
```

## Benefits

1. **Higher Success Rates**: Each LLM handles what it does best
2. **Intelligent Recovery**: Strategic fallbacks instead of random retries
3. **Continuous Learning**: System improves routing over time
4. **Better User Experience**: Fewer failures, faster responses
5. **Resource Optimization**: Simple tasks use fast/cheap models

## Testing

Run the intelligent routing tests:
```bash
cd backend/tests
python3 test_intelligent_routing.py
```

## Configuration

Set environment variables for each LLM:
```bash
export CLAUDE_API_KEY="your-claude-key"
export OPENAI_API_KEY="your-openai-key"
export XAI_API_KEY="your-xai-key"
```

## Future Enhancements

1. **Dynamic Success Rate Updates**: Real-time learning from production usage
2. **Cost Optimization**: Route based on cost/performance trade-offs
3. **Custom Routing Rules**: Allow users to specify preferred LLMs
4. **A/B Testing**: Compare strategies systematically
5. **Prompt Evolution**: Automatically improve prompts based on success patterns