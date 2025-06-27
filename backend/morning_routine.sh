#!/bin/bash
# SwiftGen Morning Routine - Parallel Execution
# Run all morning checks in parallel for faster startup

echo "☀️ SwiftGen Morning Routine Starting..."
echo "Time: $(date)"
echo "=" * 60

# Create temp directory for outputs
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Function to run command and save output
run_task() {
    local task_name=$1
    local command=$2
    local output_file=$3
    
    echo "🔄 Starting: $task_name"
    eval "$command" > "$output_file" 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Completed: $task_name"
    else
        echo "❌ Failed: $task_name (exit code: $exit_code)"
    fi
    
    return $exit_code
}

# Start all tasks in parallel
echo -e "\n📋 Running parallel checks..."

# Task 1: Check git status
run_task "Git Status" "git status --short" "$TEMP_DIR/git_status.txt" &
PID1=$!

# Task 2: Pull latest changes
run_task "Git Pull" "git pull --rebase" "$TEMP_DIR/git_pull.txt" &
PID2=$!

# Task 3: Check Python dependencies
run_task "Check Dependencies" "pip list | grep -E 'fastapi|pyyaml|openai'" "$TEMP_DIR/deps.txt" &
PID3=$!

# Task 4: Run quick test validation
run_task "Test Validation" "python3 -c 'from test_suite import SwiftGenTestSuite; print(\"Test suite OK\")'" "$TEMP_DIR/test_check.txt" &
PID4=$!

# Task 5: Check for TODO items
run_task "TODO Check" "grep -r 'TODO\\|FIXME' --include='*.py' ." "$TEMP_DIR/todos.txt" &
PID5=$!

# Wait for all background jobs
echo -e "\n⏳ Waiting for all tasks to complete..."
wait $PID1 $PID2 $PID3 $PID4 $PID5

# Display results
echo -e "\n📊 Morning Routine Results:"
echo "=" * 60

# Git Status
echo -e "\n🔸 Git Status:"
if [ -s "$TEMP_DIR/git_status.txt" ]; then
    cat "$TEMP_DIR/git_status.txt"
else
    echo "Working directory clean"
fi

# Git Pull Results
echo -e "\n🔸 Git Pull Results:"
cat "$TEMP_DIR/git_pull.txt" | grep -E "Already up to date|Fast-forward|Updating" || echo "No updates"

# Dependencies
echo -e "\n🔸 Key Dependencies:"
cat "$TEMP_DIR/deps.txt"

# TODOs
echo -e "\n🔸 TODO/FIXME Count:"
TODO_COUNT=$(wc -l < "$TEMP_DIR/todos.txt")
echo "Found $TODO_COUNT TODO/FIXME items"

# Story Status Check
echo -e "\n📈 Checking Story Status..."
python3 -c "
import re

# Quick parse of USER_STORY_TRACKER.md
try:
    with open('USER_STORY_TRACKER.md', 'r') as f:
        content = f.read()
    
    # Count story statuses
    blocked = content.count('❌ BLOCKED')
    done = content.count('✅ DONE')
    in_progress = content.count('🟡 IN PROGRESS')
    not_started = content.count('⚠️ NOT STARTED')
    
    print(f'Stories Overview:')
    print(f'  ✅ Done: {done}')
    print(f'  🟡 In Progress: {in_progress}')
    print(f'  ❌ Blocked: {blocked}')
    print(f'  ⚠️ Not Started: {not_started}')
    
    # Extract metrics
    metrics = re.search(r'Stories Complete: (\d+)/(\d+)', content)
    if metrics:
        complete, total = metrics.groups()
        print(f'\\nProgress: {complete}/{total} ({int(complete)/int(total)*100:.1f}%)')
        
except Exception as e:
    print(f'Could not read story tracker: {e}')
"

# Run baseline tests if requested
if [ "$1" == "--with-tests" ]; then
    echo -e "\n🧪 Running Baseline Tests..."
    python3 run_tests.py basic --parallel
fi

# Final summary
echo -e "\n✨ Morning Routine Complete!"
echo "Time: $(date)"
echo -e "\n📝 Next Steps:"
echo "1. Review blocked stories in USER_STORY_TRACKER.md"
echo "2. Check MASTER_ISSUES_AND_FIXES.md for known issues"
echo "3. Run 'python3 run_tests.py' to verify current state"
echo "4. Focus on highest priority blocked stories"

# Create morning report
REPORT_FILE="morning_report_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "SwiftGen Morning Report - $(date)"
    echo "=" * 60
    echo -e "\nGit Status:"
    cat "$TEMP_DIR/git_status.txt" || echo "Clean"
    echo -e "\nDependencies OK: $([ -s "$TEMP_DIR/deps.txt" ] && echo "Yes" || echo "No")"
    echo -e "\nTODO Count: $TODO_COUNT"
} > "$REPORT_FILE"

echo -e "\n📄 Report saved to: $REPORT_FILE"