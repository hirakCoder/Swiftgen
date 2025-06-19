# xAI Grok Setup Guide for SwiftGen

## Why xAI Grok?

xAI Grok is particularly excellent for UI/UX tasks because:
- Specialized in creative and visual design tasks
- Better at understanding modern UI patterns
- Excellent for generating interactive components
- Strong at creating visually appealing interfaces

## Setup Instructions

### 1. Get xAI API Key

1. Visit [xAI Console](https://console.x.ai)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `xai-`)

### 2. Configure Environment

Add to your `.env` file:

```bash
# xAI Configuration
XAI_API_KEY=xai-your-api-key-here
```

### 3. Verify Setup

Run the backend and check logs:

```bash
python main.py
```

You should see:
```
✓ Initialized xAI Grok
```

If you see:
```
✗ Skipped xAI Grok - No API key found (XAI_API_KEY)
```

Then the API key is not properly configured.

## How xAI is Used in SwiftGen

### Intelligent Routing

The system automatically routes requests to xAI for:
- UI/UX improvements
- Visual design enhancements
- Interactive component creation
- Animation and styling tasks

### Request Types Handled by xAI

1. **UI Design Requests**
   - "Make the UI more fancy"
   - "Improve the visual design"
   - "Add interactive elements"
   - "Make it more modern"

2. **Animation Requests**
   - "Add animations"
   - "Make it more dynamic"
   - "Add transitions"

3. **Styling Requests**
   - "Improve colors"
   - "Add gradients"
   - "Make it more visually appealing"

## Implementation Details

xAI uses the OpenAI-compatible API format:

```python
# xAI client setup
xai_client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# Model: grok-beta
response = xai_client.chat.completions.create(
    model="grok-beta",
    messages=[...],
    max_tokens=4096,
    temperature=0.7
)
```

## Benefits

1. **Better UI/UX Results**: Grok excels at creative visual tasks
2. **Cost Effective**: $25 free credits per month during beta
3. **Fast Response**: Optimized for quick iterations
4. **Compatible API**: Uses OpenAI format for easy integration

## Troubleshooting

### API Key Not Working
- Ensure key starts with `xai-`
- Check for extra spaces or quotes
- Verify key is active in xAI console

### Fallback Behavior
If xAI fails, the system automatically falls back to:
1. Claude 3.5 Sonnet
2. GPT-4 Turbo

### Rate Limits
- Beta period: Generous limits
- Monitor usage in xAI console
- System handles rate limit errors gracefully

## Testing xAI

1. Generate a simple app
2. Request: "Make the UI more fancy and interactive"
3. Check logs for: `[ROUTER] Selected xAI Grok for modification`
4. Verify UI improvements are applied

## Free Credits

During the beta period (through end of 2024):
- $25 free credits per month
- Sufficient for hundreds of UI modifications
- No credit card required

## Conclusion

xAI Grok is a crucial component for high-quality UI/UX modifications in SwiftGen. Its specialized capabilities make it the preferred choice for visual and interactive enhancements.