"""
JSON Fixer - Handles common JSON parsing issues from LLM responses
"""
import re
import json
import logging

logger = logging.getLogger(__name__)


def fix_json_escapes(json_str: str) -> str:
    """Fix common escape sequence issues in JSON strings"""
    
    # Fix invalid escape sequences by properly escaping them
    # This handles cases like \n, \t, \r that aren't in quotes
    fixed = json_str
    
    # Replace problematic patterns
    patterns = [
        # Fix unescaped backslashes before quotes
        (r'\\(?!")', r'\\\\'),
        # Fix newlines in strings
        (r'(?<!\\)\\n', r'\\n'),
        # Fix tabs in strings  
        (r'(?<!\\)\\t', r'\\t'),
        # Fix carriage returns
        (r'(?<!\\)\\r', r'\\r'),
    ]
    
    for pattern, replacement in patterns:
        fixed = re.sub(pattern, replacement, fixed)
    
    return fixed


def extract_and_fix_json(text: str) -> dict:
    """Extract JSON from text and fix common issues"""
    
    # Try to find JSON object
    json_match = re.search(r'\{[\s\S]*\}', text)
    if not json_match:
        raise ValueError("No JSON object found in text")
    
    json_str = json_match.group(0)
    
    # Try parsing as-is first
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.debug(f"Initial JSON parse failed: {e}")
    
    # Try fixing escapes
    try:
        fixed = fix_json_escapes(json_str)
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        logger.debug(f"Fixed JSON parse failed: {e}")
    
    # Try removing problematic content within strings
    try:
        # More aggressive fix - replace content in strings
        def fix_string_content(match):
            content = match.group(1)
            # Escape all backslashes
            content = content.replace('\\', '\\\\')
            # Escape quotes
            content = content.replace('"', '\\"')
            # Replace actual newlines with \n
            content = content.replace('\n', '\\n')
            content = content.replace('\r', '\\r')
            content = content.replace('\t', '\\t')
            return f'"{content}"'
        
        # Apply to all string values
        fixed = re.sub(r'"([^"]*)"', fix_string_content, json_str)
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        logger.debug(f"Aggressive fix failed: {e}")
    
    # Last resort - try to extract just the files array
    try:
        files_match = re.search(r'"files"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
        if files_match:
            files_content = files_match.group(1)
            # Try to parse just the files
            files_json = f'[{files_content}]'
            files = json.loads(fix_json_escapes(files_json))
            return {"files": files}
    except:
        pass
    
    raise ValueError(f"Could not parse JSON after all fix attempts")