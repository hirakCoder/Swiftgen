#!/usr/bin/env python3
"""Real-time log monitor for SwiftGen"""

import subprocess
import sys
import time
import re
from datetime import datetime

def monitor_logs():
    print("📊 SwiftGen Log Monitor")
    print("=" * 60)
    print("Monitoring server.log for important events...")
    print("Press Ctrl+C to stop\n")
    
    # Patterns to highlight
    patterns = {
        'error': (r'ERROR|Exception|Failed|error', '❌'),
        'warning': (r'WARNING|warning|Warn', '⚠️'),
        'success': (r'Success|success|✅|Generated|completed', '✅'),
        'info': (r'INFO|Generating|Starting', 'ℹ️'),
        'ios_version': (r'ios_version.*16\.0|ios_version.*17\.0', '📱'),
        'json': (r'JSON|json|parsing', '📄'),
        'llm': (r'Claude|GPT-4|xAI|anthropic|openai', '🤖'),
        'websocket': (r'WebSocket|websocket|ws/', '🔌'),
        'build': (r'Building|build|xcodebuild', '🔨'),
        'quality': (r'UI Quality|Score:|anti-pattern', '🎨')
    }
    
    try:
        # Start tailing the log file
        process = subprocess.Popen(
            ['tail', '-f', 'server.log'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        for line in process.stdout:
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Check for patterns
            matched = False
            for name, (pattern, emoji) in patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    print(f"[{timestamp}] {emoji} {line.strip()}")
                    matched = True
                    break
            
            # Print unmatched lines in gray (dimmed)
            if not matched and line.strip():
                print(f"[{timestamp}]   {line.strip()}")
                
    except KeyboardInterrupt:
        print("\n\n👋 Stopping log monitor...")
        process.terminate()
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    monitor_logs()