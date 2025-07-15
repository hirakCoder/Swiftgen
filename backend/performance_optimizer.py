"""
Performance Optimizer for SwiftGen
Optimizes generation speed and reduces unnecessary processing
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from functools import lru_cache
import hashlib
import json

class PerformanceOptimizer:
    """Optimizes SwiftGen performance through caching, parallel processing, and smart defaults"""
    
    def __init__(self):
        # Cache for generated code patterns
        self.generation_cache = {}
        self.validation_cache = {}
        self.build_cache = {}
        
        # Performance metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'parallel_tasks': 0,
            'total_time_saved': 0
        }
        
        # Common app templates for fast generation
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Dict]:
        """Load optimized templates for common app types"""
        return {
            'timer': {
                'keywords': ['timer', 'countdown', 'stopwatch', 'clock'],
                'base_structure': {
                    'files': [
                        {'path': 'Sources/App.swift', 'template': 'timer_app'},
                        {'path': 'Sources/ContentView.swift', 'template': 'timer_content'},
                        {'path': 'Sources/TimerViewModel.swift', 'template': 'timer_viewmodel'}
                    ],
                    'features': ['Timer functionality', 'Start/Stop controls', 'Time display'],
                    'complexity': 'low'
                }
            },
            'todo': {
                'keywords': ['todo', 'task', 'list', 'checklist'],
                'base_structure': {
                    'files': [
                        {'path': 'Sources/App.swift', 'template': 'todo_app'},
                        {'path': 'Sources/ContentView.swift', 'template': 'todo_content'},
                        {'path': 'Sources/TodoViewModel.swift', 'template': 'todo_viewmodel'},
                        {'path': 'Sources/TodoItem.swift', 'template': 'todo_model'}
                    ],
                    'features': ['Add/Remove tasks', 'Mark as complete', 'Task persistence'],
                    'complexity': 'low'
                }
            },
            'calculator': {
                'keywords': ['calculator', 'calc', 'math', 'compute'],
                'base_structure': {
                    'files': [
                        {'path': 'Sources/App.swift', 'template': 'calc_app'},
                        {'path': 'Sources/ContentView.swift', 'template': 'calc_content'},
                        {'path': 'Sources/CalculatorViewModel.swift', 'template': 'calc_viewmodel'}
                    ],
                    'features': ['Basic operations', 'Clear function', 'Decimal support'],
                    'complexity': 'low'
                }
            }
        }
    
    def get_cached_generation(self, description: str) -> Optional[Dict]:
        """Check if we have a cached generation for similar description"""
        # Create cache key from normalized description
        cache_key = self._create_cache_key(description)
        
        if cache_key in self.generation_cache:
            self.metrics['cache_hits'] += 1
            print(f"[PERFORMANCE] Cache hit for generation: {cache_key[:8]}...")
            return self.generation_cache[cache_key].copy()
        
        self.metrics['cache_misses'] += 1
        return None
    
    def cache_generation(self, description: str, generated_code: Dict):
        """Cache successful generation for reuse"""
        cache_key = self._create_cache_key(description)
        self.generation_cache[cache_key] = generated_code.copy()
        
        # Limit cache size
        if len(self.generation_cache) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self.generation_cache))
            del self.generation_cache[oldest_key]
    
    def _create_cache_key(self, text: str) -> str:
        """Create normalized cache key from text"""
        # Normalize text
        normalized = text.lower().strip()
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        # Hash for consistent key
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def detect_app_type(self, description: str) -> Optional[str]:
        """Quickly detect app type from description for template usage"""
        description_lower = description.lower()
        
        for app_type, config in self.templates.items():
            if any(keyword in description_lower for keyword in config['keywords']):
                print(f"[PERFORMANCE] Detected app type: {app_type}")
                return app_type
        
        return None
    
    def get_template_structure(self, app_type: str) -> Optional[Dict]:
        """Get optimized template structure for quick generation"""
        if app_type in self.templates:
            return self.templates[app_type]['base_structure'].copy()
        return None
    
    async def parallel_validate(self, files: List[Dict], validators: List[Any]) -> Dict[str, List]:
        """Run multiple validators in parallel"""
        start_time = time.time()
        
        # Create validation tasks
        tasks = []
        for validator in validators:
            if hasattr(validator, 'validate_files'):
                task = asyncio.create_task(self._run_validator(validator, files))
                tasks.append(task)
        
        # Run all validators in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_issues = []
        for result in results:
            if isinstance(result, list):
                all_issues.extend(result)
            elif isinstance(result, Exception):
                print(f"[PERFORMANCE] Validator error: {result}")
        
        elapsed = time.time() - start_time
        print(f"[PERFORMANCE] Parallel validation completed in {elapsed:.2f}s")
        self.metrics['parallel_tasks'] += len(tasks)
        
        return {'issues': all_issues, 'time': elapsed}
    
    async def _run_validator(self, validator: Any, files: List[Dict]) -> List:
        """Run a single validator asynchronously"""
        try:
            # If validator is sync, run in executor
            if asyncio.iscoroutinefunction(validator.validate_files):
                return await validator.validate_files(files)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, validator.validate_files, files)
        except Exception as e:
            print(f"[PERFORMANCE] Validator {type(validator).__name__} failed: {e}")
            return []
    
    @lru_cache(maxsize=128)
    def is_complex_app(self, description: str) -> bool:
        """Cached complexity detection"""
        description_lower = description.lower()
        
        # Quick checks for simple apps
        simple_indicators = ['simple', 'basic', 'minimal', 'hello world', 'demo']
        if any(indicator in description_lower for indicator in simple_indicators):
            return False
        
        # Complex indicators
        complex_indicators = [
            'api', 'backend', 'database', 'authentication', 'real-time',
            'payment', 'complex', 'advanced', 'professional', 'enterprise'
        ]
        
        return any(indicator in description_lower for indicator in complex_indicators)
    
    def optimize_file_generation(self, files: List[Dict]) -> List[Dict]:
        """Optimize generated files by removing duplicates and empty files"""
        seen_paths = set()
        optimized_files = []
        
        for file in files:
            path = file.get('path', '')
            content = file.get('content', '')
            
            # Skip empty files
            if not content or len(content.strip()) < 10:
                continue
            
            # Skip duplicates
            if path in seen_paths:
                continue
            
            seen_paths.add(path)
            optimized_files.append(file)
        
        print(f"[PERFORMANCE] Optimized {len(files)} files to {len(optimized_files)}")
        return optimized_files
    
    def get_performance_report(self) -> Dict:
        """Get performance metrics report"""
        total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (self.metrics['cache_hits'] / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        return {
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'parallel_tasks_run': self.metrics['parallel_tasks'],
            'estimated_time_saved': f"{self.metrics['total_time_saved']:.1f}s"
        }
    
    def should_skip_validation(self, app_type: str, complexity: str) -> bool:
        """Determine if we can skip certain validations for performance"""
        # For simple template-based apps, we can skip some validations
        if app_type in self.templates and complexity == 'low':
            return True
        return False
    
    async def optimize_build_process(self, project_path: str, app_complexity: str) -> Dict:
        """Optimize build process based on app complexity"""
        optimizations = {
            'parallel_builds': app_complexity != 'high',  # Disable for complex apps
            'skip_warnings': app_complexity == 'low',     # Skip non-critical warnings for simple apps
            'cache_dependencies': True,                   # Always cache dependencies
            'optimize_level': 'size' if app_complexity == 'low' else 'speed'
        }
        
        return optimizations
    
    def preload_common_imports(self) -> Dict[str, str]:
        """Preload common import statements for faster generation"""
        return {
            'swiftui': 'import SwiftUI',
            'combine': 'import Combine',
            'foundation': 'import Foundation',
            'standard_imports': 'import SwiftUI\nimport Foundation',
            'viewmodel_imports': 'import SwiftUI\nimport Combine'
        }
    
    def estimate_generation_time(self, description: str) -> float:
        """Estimate generation time based on complexity"""
        if self.is_complex_app(description):
            return 30.0  # 30 seconds for complex apps
        
        app_type = self.detect_app_type(description)
        if app_type:
            return 10.0  # 10 seconds for template-based apps
        
        return 20.0  # 20 seconds for medium complexity