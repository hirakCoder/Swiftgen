#!/usr/bin/env python3
"""
SwiftGen Comprehensive Data Collector - Covers all aspects of iOS/Swift development
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import re

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
OUTPUT_DIR = Path('/home/ubuntu/swift_dataset')
LOG_FILE = Path('/home/ubuntu/data_collection.log')

# GitHub API endpoints
SEARCH_API = 'https://api.github.com/search/repositories'
SEARCH_CODE_API = 'https://api.github.com/search/code'

# Comprehensive search queries covering ALL aspects of iOS development
SEARCH_CATEGORIES = {
    # UI/UX Design Patterns
    'ui_design': [
        'language:swift stars:>50 "Custom UI Components"',
        'language:swift stars:>50 "UIKit animations"',
        'language:swift stars:>50 "SwiftUI animations"',
        'language:swift stars:>50 "Material Design" iOS',
        'language:swift stars:>50 "Human Interface Guidelines"',
        'language:swift stars:>30 "Custom transitions"',
        'language:swift stars:>30 "Gesture recognizers"',
        'language:swift stars:>30 "Auto Layout" programmatic',
        'language:swift stars:>30 "Dynamic Type" accessibility',
        'language:swift stars:>30 "Dark mode" implementation',
        'language:swift stars:>50 "Custom navigation"',
        'language:swift stars:>30 "Collection view layouts"',
        'language:swift stars:>30 "Table view" custom cells',
        'language:swift stars:>30 "Pull to refresh" custom',
        'language:swift stars:>30 "Onboarding" UI'
    ],
    
    # SwiftUI Specific
    'swiftui': [
        'language:swift stars:>50 SwiftUI "custom views"',
        'language:swift stars:>50 SwiftUI "ViewModifier"',
        'language:swift stars:>50 SwiftUI "PreferenceKey"',
        'language:swift stars:>30 SwiftUI "GeometryReader"',
        'language:swift stars:>30 SwiftUI "custom shapes"',
        'language:swift stars:>30 SwiftUI "animation" transitions',
        'language:swift stars:>30 SwiftUI navigation',
        'language:swift stars:>30 SwiftUI "state management"',
        'language:swift stars:>30 SwiftUI charts',
        'language:swift stars:>30 SwiftUI forms'
    ],
    
    # Architecture Patterns
    'architecture': [
        'language:swift stars:>100 MVVM iOS',
        'language:swift stars:>100 "Clean Architecture" iOS',
        'language:swift stars:>50 VIPER iOS',
        'language:swift stars:>50 MVP iOS',
        'language:swift stars:>50 MVC iOS refactor',
        'language:swift stars:>50 "Coordinator pattern"',
        'language:swift stars:>50 "Redux" SwiftUI',
        'language:swift stars:>50 TCA "Composable Architecture"',
        'language:swift stars:>30 "Repository pattern" iOS',
        'language:swift stars:>30 "Factory pattern" Swift'
    ],
    
    # Performance Optimization
    'performance': [
        'language:swift stars:>50 "performance optimization"',
        'language:swift stars:>50 "memory management" iOS',
        'language:swift stars:>30 "lazy loading" images',
        'language:swift stars:>30 "cache" implementation',
        'language:swift stars:>30 "Core Data" optimization',
        'language:swift stars:>30 "async await" performance',
        'language:swift stars:>30 "Grand Central Dispatch"',
        'language:swift stars:>30 "Operation Queue"',
        'language:swift stars:>30 "Instruments" profiling',
        'language:swift stars:>30 "memory leaks" fix'
    ],
    
    # Networking & API
    'networking': [
        'language:swift stars:>100 Alamofire',
        'language:swift stars:>50 URLSession wrapper',
        'language:swift stars:>50 "REST API" client',
        'language:swift stars:>50 GraphQL iOS',
        'language:swift stars:>30 WebSocket iOS',
        'language:swift stars:>30 "API authentication"',
        'language:swift stars:>30 "Network layer" abstraction',
        'language:swift stars:>30 "Codable" JSON',
        'language:swift stars:>30 "API caching"',
        'language:swift stars:>30 "Network monitoring"'
    ],
    
    # Data Persistence
    'data_persistence': [
        'language:swift stars:>100 "Core Data"',
        'language:swift stars:>100 Realm iOS',
        'language:swift stars:>50 SQLite Swift',
        'language:swift stars:>50 UserDefaults wrapper',
        'language:swift stars:>50 Keychain wrapper',
        'language:swift stars:>30 CloudKit implementation',
        'language:swift stars:>30 "File manager" wrapper',
        'language:swift stars:>30 "Data migration" Core Data',
        'language:swift stars:>30 "Database encryption"'
    ],
    
    # Testing & Quality
    'testing': [
        'language:swift stars:>50 "unit testing" iOS',
        'language:swift stars:>50 "UI testing" XCTest',
        'language:swift stars:>50 Quick Nimble',
        'language:swift stars:>30 "snapshot testing"',
        'language:swift stars:>30 "mock" testing',
        'language:swift stars:>30 "integration testing"',
        'language:swift stars:>30 "TDD" iOS',
        'language:swift stars:>30 "test coverage"',
        'language:swift stars:>30 XCUITest automation'
    ],
    
    # Security
    'security': [
        'language:swift stars:>50 "biometric authentication"',
        'language:swift stars:>50 "Face ID" "Touch ID"',
        'language:swift stars:>30 "SSL pinning"',
        'language:swift stars:>30 "encryption" iOS',
        'language:swift stars:>30 "secure storage"',
        'language:swift stars:>30 "OAuth" implementation',
        'language:swift stars:>30 "JWT" authentication',
        'language:swift stars:>30 "App Transport Security"'
    ],
    
    # Apple Frameworks
    'apple_frameworks': [
        'language:swift stars:>50 ARKit',
        'language:swift stars:>50 CoreML "Machine Learning"',
        'language:swift stars:>50 Vision framework',
        'language:swift stars:>30 HealthKit',
        'language:swift stars:>30 HomeKit',
        'language:swift stars:>30 MapKit custom',
        'language:swift stars:>30 CoreLocation',
        'language:swift stars:>30 CoreMotion',
        'language:swift stars:>30 CoreBluetooth',
        'language:swift stars:>30 AVFoundation',
        'language:swift stars:>30 PhotoKit',
        'language:swift stars:>30 CloudKit',
        'language:swift stars:>30 SiriKit',
        'language:swift stars:>30 WidgetKit',
        'language:swift stars:>30 App Clips'
    ],
    
    # Reactive Programming
    'reactive': [
        'language:swift stars:>100 RxSwift',
        'language:swift stars:>100 Combine framework',
        'language:swift stars:>50 ReactiveSwift',
        'language:swift stars:>30 "Publisher" Combine',
        'language:swift stars:>30 "Observable" pattern',
        'language:swift stars:>30 "data binding" iOS'
    ],
    
    # Dependency Injection
    'dependency_injection': [
        'language:swift stars:>50 Swinject',
        'language:swift stars:>30 "dependency injection" iOS',
        'language:swift stars:>30 "service locator" Swift',
        'language:swift stars:>30 "container" DI'
    ],
    
    # Extensions & Utilities
    'utilities': [
        'language:swift stars:>100 "Swift extensions"',
        'language:swift stars:>50 "UIKit extensions"',
        'language:swift stars:>50 "Foundation extensions"',
        'language:swift stars:>30 "Date" extensions',
        'language:swift stars:>30 "String" extensions',
        'language:swift stars:>30 "Array" extensions'
    ],
    
    # Real-world Apps
    'complete_apps': [
        'language:swift stars:>500 iOS app',
        'language:swift stars:>300 "open source" iOS',
        'language:swift stars:>200 "production" app iOS',
        'language:swift stars:>100 "e-commerce" iOS',
        'language:swift stars:>100 "social media" iOS',
        'language:swift stars:>100 "chat app" iOS',
        'language:swift stars:>100 "weather app" iOS',
        'language:swift stars:>100 "news app" iOS',
        'language:swift stars:>100 "fitness app" iOS',
        'language:swift stars:>100 "music player" iOS'
    ],
    
    # macOS Development
    'macos': [
        'language:swift stars:>50 macOS app',
        'language:swift stars:>30 AppKit',
        'language:swift stars:>30 "menu bar" macOS',
        'language:swift stars:>30 "Catalyst" app'
    ],
    
    # watchOS & tvOS
    'other_platforms': [
        'language:swift stars:>30 watchOS',
        'language:swift stars:>30 tvOS',
        'language:swift stars:>30 "Apple Watch"',
        'language:swift stars:>30 "Apple TV"'
    ],
    
    # Server-Side Swift
    'server_side': [
        'language:swift stars:>100 Vapor',
        'language:swift stars:>50 Perfect server',
        'language:swift stars:>50 Kitura',
        'language:swift stars:>30 "server side swift"'
    ],
    
    # Modern Swift Features
    'swift_features': [
        'language:swift stars:>50 "async await"',
        'language:swift stars:>50 "property wrappers"',
        'language:swift stars:>50 "result builders"',
        'language:swift stars:>30 "function builders"',
        'language:swift stars:>30 actors concurrency',
        'language:swift stars:>30 "structured concurrency"',
        'language:swift stars:>30 generics advanced',
        'language:swift stars:>30 "protocol oriented"'
    ]
}

# File patterns to analyze
CODE_PATTERNS = {
    'ui_components': [
        r'class\s+\w+:\s*(UI\w+|NS\w+)',
        r'struct\s+\w+:\s*View\s*{',
        r'@IBDesignable',
        r'@IBInspectable',
        r'func\s+draw\(',
        r'func\s+layoutSubviews\(',
    ],
    'swiftui_patterns': [
        r'@State\s+',
        r'@Binding\s+',
        r'@ObservedObject\s+',
        r'@StateObject\s+',
        r'@EnvironmentObject\s+',
        r'@Environment\(',
        r'\.onAppear\s*{',
        r'\.onChange\(',
        r'\.task\s*{',
    ],
    'performance_patterns': [
        r'DispatchQueue\.',
        r'async\s+throws',
        r'await\s+',
        r'Task\s*{',
        r'actor\s+',
        r'@MainActor',
        r'lazy\s+var',
        r'private\(set\)',
    ],
    'testing_patterns': [
        r'import\s+XCTest',
        r'class\s+\w+:\s*XCTestCase',
        r'func\s+test\w+\(',
        r'XCTAssert',
        r'expect\(',
        r'describe\(',
    ]
}

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + '\n')

def setup_directories():
    """Create necessary directories"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Create category subdirectories
    for category in SEARCH_CATEGORIES.keys():
        (OUTPUT_DIR / category).mkdir(exist_ok=True)
    
    log_message(f"Created output directory structure: {OUTPUT_DIR}")

def get_headers():
    """Get GitHub API headers"""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

def search_repositories(query, category, per_page=100, max_repos=50):
    """Search GitHub repositories with category tracking"""
    all_repos = []
    page = 1
    
    while len(all_repos) < max_repos:
        try:
            response = requests.get(
                SEARCH_API,
                headers=get_headers(),
                params={
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': per_page,
                    'page': page
                }
            )
            
            if response.status_code == 403:
                log_message("Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                continue
                
            response.raise_for_status()
            data = response.json()
            
            repos = data.get('items', [])
            if not repos:
                break
                
            # Add category info to each repo
            for repo in repos:
                repo['category'] = category
                
            all_repos.extend(repos[:max_repos - len(all_repos)])
            log_message(f"[{category}] Found {len(repos)} repositories for query: {query}")
            
            if len(all_repos) >= data.get('total_count', 0):
                break
                
            page += 1
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            log_message(f"Error searching repositories: {e}")
            break
            
    return all_repos

def analyze_code_patterns(content):
    """Analyze code for various patterns"""
    analysis = {
        'patterns': {},
        'metrics': {
            'lines_of_code': len(content.splitlines()),
            'import_count': len(re.findall(r'^import\s+', content, re.MULTILINE)),
            'class_count': len(re.findall(r'^class\s+', content, re.MULTILINE)),
            'struct_count': len(re.findall(r'^struct\s+', content, re.MULTILINE)),
            'protocol_count': len(re.findall(r'^protocol\s+', content, re.MULTILINE)),
            'function_count': len(re.findall(r'^func\s+', content, re.MULTILINE)),
        }
    }
    
    # Check for pattern matches
    for pattern_type, patterns in CODE_PATTERNS.items():
        matches = 0
        for pattern in patterns:
            matches += len(re.findall(pattern, content))
        analysis['patterns'][pattern_type] = matches
    
    # Detect frameworks used
    frameworks = []
    framework_imports = [
        'UIKit', 'SwiftUI', 'Foundation', 'CoreData', 'Combine',
        'RxSwift', 'Alamofire', 'SnapKit', 'Kingfisher', 'SwiftyJSON'
    ]
    for framework in framework_imports:
        if f'import {framework}' in content:
            frameworks.append(framework)
    analysis['frameworks'] = frameworks
    
    return analysis

def clone_repository(repo_url, repo_name, category):
    """Clone a repository to category-specific directory"""
    repo_dir = OUTPUT_DIR / category / repo_name.replace('/', '_')
    
    if repo_dir.exists():
        log_message(f"Repository already exists: {repo_name}")
        return repo_dir
        
    try:
        log_message(f"[{category}] Cloning repository: {repo_name}")
        subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, str(repo_dir)],
            check=True,
            capture_output=True,
            text=True
        )
        return repo_dir
    except subprocess.CalledProcessError as e:
        log_message(f"Failed to clone {repo_name}: {e}")
        return None

def extract_swift_files(repo_dir, category):
    """Extract and analyze Swift files from repository"""
    swift_files = []
    
    try:
        for swift_file in repo_dir.rglob('*.swift'):
            # Skip hidden directories and build artifacts
            if any(part.startswith('.') for part in swift_file.parts):
                continue
            if any(part in ['build', 'DerivedData', 'Pods', 'Carthage', '.build'] for part in swift_file.parts):
                continue
                
            try:
                content = swift_file.read_text(encoding='utf-8')
                
                # Analyze the code
                analysis = analyze_code_patterns(content)
                
                swift_files.append({
                    'path': str(swift_file.relative_to(repo_dir)),
                    'content': content,
                    'size': len(content),
                    'category': category,
                    'analysis': analysis
                })
            except Exception as e:
                log_message(f"Error reading {swift_file}: {e}")
                
    except Exception as e:
        log_message(f"Error extracting Swift files: {e}")
        
    return swift_files

def extract_project_structure(repo_dir):
    """Extract project structure and configuration"""
    structure = {
        'has_xcodeproj': any(repo_dir.rglob('*.xcodeproj')),
        'has_xcworkspace': any(repo_dir.rglob('*.xcworkspace')),
        'has_package_swift': (repo_dir / 'Package.swift').exists(),
        'has_podfile': (repo_dir / 'Podfile').exists(),
        'has_cartfile': (repo_dir / 'Cartfile').exists(),
        'has_readme': any(repo_dir.glob('README*')),
        'has_tests': any(repo_dir.rglob('*Test*.swift')) or any(repo_dir.rglob('*Tests')),
        'has_ci': any(repo_dir.rglob('.github/workflows/*')) or (repo_dir / '.travis.yml').exists(),
    }
    
    # Extract dependencies if possible
    dependencies = []
    
    # From Package.swift
    package_file = repo_dir / 'Package.swift'
    if package_file.exists():
        try:
            content = package_file.read_text()
            deps = re.findall(r'\.package\(.*?url:\s*"(.*?)"', content)
            dependencies.extend([{'source': 'SPM', 'url': dep} for dep in deps])
        except:
            pass
    
    # From Podfile
    podfile = repo_dir / 'Podfile'
    if podfile.exists():
        try:
            content = podfile.read_text()
            pods = re.findall(r"pod\s+'(.*?)'", content)
            dependencies.extend([{'source': 'CocoaPods', 'name': pod} for pod in pods])
        except:
            pass
    
    structure['dependencies'] = dependencies
    return structure

def save_dataset(repo_name, swift_files, project_structure, category):
    """Save Swift files and analysis to dataset"""
    if not swift_files:
        return
        
    dataset_file = OUTPUT_DIR / category / f"{repo_name.replace('/', '_')}_dataset.json"
    
    # Calculate aggregate metrics
    total_patterns = {}
    for file_data in swift_files:
        for pattern_type, count in file_data['analysis']['patterns'].items():
            total_patterns[pattern_type] = total_patterns.get(pattern_type, 0) + count
    
    dataset = {
        'repository': repo_name,
        'category': category,
        'timestamp': datetime.now().isoformat(),
        'file_count': len(swift_files),
        'total_size': sum(f['size'] for f in swift_files),
        'project_structure': project_structure,
        'aggregate_patterns': total_patterns,
        'files': swift_files
    }
    
    with open(dataset_file, 'w') as f:
        json.dump(dataset, f, indent=2)
        
    log_message(f"[{category}] Saved {len(swift_files)} Swift files from {repo_name}")

def collect_data():
    """Main data collection function"""
    log_message("Starting SwiftGen Comprehensive Data Collection")
    setup_directories()
    
    if not GITHUB_TOKEN:
        log_message("WARNING: No GitHub token found. API rate limits will be restrictive.")
        log_message("Set GITHUB_TOKEN environment variable for better performance.")
    
    # Track all processed repos to avoid duplicates
    all_processed_repos = set()
    
    # Statistics tracking
    stats = {
        'start_time': datetime.now().isoformat(),
        'categories': {}
    }
    
    # Process each category
    for category, queries in SEARCH_CATEGORIES.items():
        log_message(f"\n{'='*60}")
        log_message(f"Processing category: {category}")
        log_message(f"{'='*60}")
        
        category_repos = 0
        category_files = 0
        
        for query in queries:
            log_message(f"\n[{category}] Searching: {query}")
            repos = search_repositories(query, category, max_repos=30)
            
            for repo in repos:
                repo_full_name = repo['full_name']
                
                # Skip if already processed
                if repo_full_name in all_processed_repos:
                    continue
                    
                all_processed_repos.add(repo_full_name)
                
                # Clone and process repository
                repo_dir = clone_repository(repo['clone_url'], repo_full_name, category)
                if repo_dir:
                    swift_files = extract_swift_files(repo_dir, category)
                    project_structure = extract_project_structure(repo_dir)
                    
                    if swift_files:
                        save_dataset(repo_full_name, swift_files, project_structure, category)
                        category_repos += 1
                        category_files += len(swift_files)
                    
                    # Clean up to save space
                    subprocess.run(['rm', '-rf', str(repo_dir)], capture_output=True)
                    
                time.sleep(3)  # Rate limiting
        
        stats['categories'][category] = {
            'repositories': category_repos,
            'files': category_files
        }
        
        log_message(f"\n[{category}] Complete: {category_repos} repos, {category_files} files")
    
    # Save collection summary
    stats['end_time'] = datetime.now().isoformat()
    stats['total_repositories'] = len(all_processed_repos)
    stats['total_categories'] = len(SEARCH_CATEGORIES)
    
    with open(OUTPUT_DIR / 'collection_summary.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Create detailed report
    create_collection_report(stats)
    
    log_message(f"\n{'='*60}")
    log_message(f"Data collection complete!")
    log_message(f"Total repositories: {len(all_processed_repos)}")
    log_message(f"Total categories: {len(SEARCH_CATEGORIES)}")
    log_message(f"Output directory: {OUTPUT_DIR}")
    log_message(f"{'='*60}")

def create_collection_report(stats):
    """Create a detailed collection report"""
    report_file = OUTPUT_DIR / 'collection_report.md'
    
    with open(report_file, 'w') as f:
        f.write("# SwiftGen Data Collection Report\n\n")
        f.write(f"**Start Time:** {stats['start_time']}\n")
        f.write(f"**End Time:** {stats['end_time']}\n")
        f.write(f"**Total Repositories:** {stats['total_repositories']}\n\n")
        
        f.write("## Category Breakdown\n\n")
        f.write("| Category | Repositories | Files |\n")
        f.write("|----------|-------------|-------|\n")
        
        for category, data in stats['categories'].items():
            f.write(f"| {category} | {data['repositories']} | {data['files']} |\n")
        
        f.write("\n## Collection Coverage\n\n")
        f.write("This collection covers:\n")
        f.write("- UI/UX Design patterns and custom components\n")
        f.write("- SwiftUI advanced implementations\n")
        f.write("- Architecture patterns (MVVM, Clean, VIPER, etc.)\n")
        f.write("- Performance optimization techniques\n")
        f.write("- Networking and API integrations\n")
        f.write("- Data persistence solutions\n")
        f.write("- Testing strategies and implementations\n")
        f.write("- Security best practices\n")
        f.write("- Apple framework integrations\n")
        f.write("- Reactive programming patterns\n")
        f.write("- Complete production apps\n")
        f.write("- Server-side Swift\n")
        f.write("- Modern Swift features and concurrency\n")

if __name__ == '__main__':
    try:
        collect_data()
    except KeyboardInterrupt:
        log_message("Data collection interrupted by user")
    except Exception as e:
        log_message(f"Fatal error: {e}")
        sys.exit(1)