# Fix for SwiftGen File Structure Issues

## Problem Identified

From the logs, I can see the exact issue:

1. **File Structure Generated**:
   ```
   Sources/Views/ContentView.swift
   Sources/Views/Components/ErrorView.swift
   Sources/Views/Components/ResultView.swift
   ```

2. **Build Errors**:
   ```
   error: cannot find 'ErrorView' in scope
   error: cannot find 'ResultView' in scope
   ```

## Root Cause

The files ARE being generated correctly in `Views/Components/` but ContentView can't find them because:
- Swift doesn't automatically import files from subdirectories
- No module system like other languages
- All files need to be in the same module target

## Solutions

### Solution 1: Move Component Files (Quick Fix)
Move all component files to the same directory as ContentView:
```
Sources/Views/
  ContentView.swift
  ErrorView.swift
  ResultView.swift
  HeaderView.swift
```

### Solution 2: Fix File Organization in file_structure_manager.py
The file_structure_manager is reorganizing files into Components/ subdirectory which breaks imports.

Look at line from logs:
```
INFO:file_structure_manager:Reorganizing Sources/Utilities/CurrencyAppError.swift -> Sources/Services/CurrencyAppError.swift
```

### Solution 3: Fix project.yml Generation
Ensure all Swift files are included in the sources list regardless of subdirectory.

## Immediate Fix Script

```python
def fix_file_organization(project_path):
    """Fix file organization to ensure all views are findable"""
    
    # Move all files from Views/Components/ to Views/
    components_dir = os.path.join(project_path, "Sources/Views/Components")
    views_dir = os.path.join(project_path, "Sources/Views")
    
    if os.path.exists(components_dir):
        for file in os.listdir(components_dir):
            if file.endswith('.swift'):
                src = os.path.join(components_dir, file)
                dst = os.path.join(views_dir, file)
                shutil.move(src, dst)
                print(f"Moved {file} to Views/")
```

## Test Case

The current test case from logs shows:
- Currency converter app with ErrorView and ResultView
- Files exist but can't be found
- Multiple recovery attempts fail because they don't address the root cause

## Action Items

1. **Disable file_structure_manager reorganization** for Views
2. **Keep all view files in Views/ directory** (no subdirectories)
3. **Test with simple app first**
4. **Update project.yml generation** to include all subdirectories