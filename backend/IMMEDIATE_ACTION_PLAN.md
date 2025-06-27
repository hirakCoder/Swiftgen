# Immediate Action Plan - Fix LLM Code Quality

## Week 1: Prompt Simplification & Testing

### Day 1-2: Simplify Prompts
1. **Create minimal_prompts.py** with:
   ```python
   SIMPLE_SYSTEM_PROMPT = """
   You are an iOS developer. Create a SwiftUI app for iOS 16.0.
   
   Key requirements:
   - Complete, working Swift code
   - Use @StateObject and ObservableObject (not @Observable)
   - Return JSON format shown in the example
   
   Example structure:
   {
     "files": [
       {"path": "Sources/App.swift", "content": "full code here"},
       {"path": "Sources/ContentView.swift", "content": "full code here"}
     ]
   }
   """
   ```

2. **Test with 5 common apps**:
   - Todo List
   - Calculator  
   - Weather
   - Notes
   - Timer

3. **Compare results** with current complex prompts

### Day 3-4: Template System
1. **Create swift_templates.py**:
   - Dark mode template
   - Navigation template
   - List/Detail template
   - Form input template
   - API call template

2. **Hybrid approach**:
   - Use templates for structure
   - LLM fills in specific logic
   - Validate with swift_validator

### Day 5: Model Comparison
1. **Test same prompts on**:
   - GPT-4-turbo
   - Claude 3 Opus
   - Llama 3 70B (via Groq/Together)
   - CodeLlama 34B
   - Mixtral-8x7B

2. **Measure**:
   - Success rate (builds without errors)
   - Cost per successful generation
   - Response time
   - Code quality score

## Week 2: Fine-Tuning Experiment

### Option A: Llama 3 Fine-Tuning
1. **Prepare training data**:
   - 500 successful app generations
   - Input: description → Output: working code
   - Format: JSONL with prompt/completion pairs

2. **Fine-tune using**:
   - Replicate
   - Modal
   - Or local GPU if available

3. **Test on same 5 apps**

### Option B: OpenAI Fine-Tuning
1. **Prepare data in OpenAI format**
2. **Fine-tune GPT-3.5-turbo**
3. **Compare cost/quality**

## Immediate Quick Wins (Do Today)

### 1. Fix JSON Parsing
```python
def extract_json_from_llm_response(response: str) -> dict:
    # Remove markdown blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    
    # Find JSON boundaries
    start = response.find('{')
    end = response.rfind('}') + 1
    
    if start >= 0 and end > start:
        try:
            return json.loads(response[start:end])
        except:
            # Try fixing common issues
            fixed = response[start:end]
            fixed = re.sub(r',\s*}', '}', fixed)  # trailing commas
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
    
    raise ValueError("No valid JSON found")
```

### 2. Add Success Tracking
```python
# In enhanced_claude_service.py
def track_generation_metrics(self, model: str, success: bool, 
                           time_taken: float, cost: float):
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "success": success,
        "time_taken": time_taken,
        "cost": cost
    }
    
    with open("generation_metrics.jsonl", "a") as f:
        f.write(json.dumps(metrics) + "\n")
```

### 3. Create Test Suite
```python
# test_llm_quality.py
TEST_APPS = [
    ("Todo List", "Create a simple todo list with add, delete, and mark complete"),
    ("Calculator", "Basic calculator with +, -, *, / operations"),
    ("Dark Mode", "Any app with a dark mode toggle"),
    ("API Weather", "Weather app using a real weather API"),
    ("Navigation", "Multi-screen app with navigation")
]

async def test_all_models():
    results = {}
    for model in ["gpt-4", "claude-3", "llama-3"]:
        results[model] = {
            "success": 0,
            "total": len(TEST_APPS),
            "avg_time": 0,
            "avg_cost": 0
        }
        
        for app_name, description in TEST_APPS:
            success = await test_generation(model, app_name, description)
            results[model]["success"] += success
    
    print_comparison_table(results)
```

## Decision Matrix

| Solution | Time to Implement | Cost | Expected Success Rate | Maintenance |
|----------|------------------|------|---------------------|-------------|
| Simplify Prompts | 1 day | $0 | 60% → 75% | Low |
| Template System | 3 days | $0 | 85%+ | Medium |
| Fine-tune Llama | 1 week | ~$50 | 80%+ | Medium |
| Fine-tune GPT | 3 days | ~$100/mo | 85%+ | Low |
| Custom Model | 1 month | ~$500 | 90%+ | High |

## Recommended Path

1. **Today**: Implement JSON fix and metrics tracking
2. **This Week**: Simplify prompts and build templates
3. **Next Week**: Test Llama/CodeLlama
4. **Decision Point**: Based on metrics, either:
   - Fine-tune Llama (if success rate < 80%)
   - Stick with templates + simplified prompts (if > 80%)

## Success Criteria

The new system should achieve:
- **80%+ first-try success rate** (no recovery needed)
- **< $0.10 per successful generation**
- **< 30 seconds generation time**
- **Zero manual fixes needed**

If we can't hit these metrics with prompt engineering, fine-tuning becomes necessary.