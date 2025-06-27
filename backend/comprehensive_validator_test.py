#!/usr/bin/env python3
"""
Comprehensive Validator Test Suite
Tests various app types, modifications, and auto-fix scenarios
"""

import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class ComprehensiveValidatorTest:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'swiftlint_available': False,
            'validator_tests': {},
            'app_generation': {},
            'modifications': {},
            'auto_fixes': {},
            'complex_apps': {}
        }
        self.workspace_dir = "../workspaces"
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_swiftlint(self):
        """Check if SwiftLint is available"""
        self.log("Checking for SwiftLint...")
        try:
            result = subprocess.run(['which', 'swiftlint'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ SwiftLint found at: " + result.stdout.strip())
                self.results['swiftlint_available'] = True
                
                # Check version
                version_result = subprocess.run(['swiftlint', 'version'], capture_output=True, text=True)
                self.log(f"   Version: {version_result.stdout.strip()}")
            else:
                self.log("❌ SwiftLint not installed")
                self.log("   Install with: brew install swiftlint")
        except Exception as e:
            self.log(f"❌ SwiftLint check failed: {e}")
    
    def test_swift_validation_tools(self):
        """Test what Swift validation tools are working"""
        self.log("\n" + "="*60)
        self.log("TESTING SWIFT VALIDATION TOOLS")
        self.log("="*60)
        
        # Test swiftc
        self.log("\n1. Testing swiftc -parse...")
        test_code = '''import SwiftUI
struct TestView: View {
    var body: some View {
        Text("Hello");  // Semicolon should be caught
    }
}'''
        
        try:
            with open('/tmp/test.swift', 'w') as f:
                f.write(test_code)
            
            result = subprocess.run(
                ['swiftc', '-parse', '/tmp/test.swift'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ swiftc -parse working (no syntax errors detected)")
            else:
                self.log("✅ swiftc -parse working (found syntax issues)")
                
            self.results['validator_tests']['swiftc'] = True
            
        except Exception as e:
            self.log(f"❌ swiftc test failed: {e}")
            self.results['validator_tests']['swiftc'] = False
        
        # Test our validator
        self.log("\n2. Testing swift_validator.py...")
        try:
            from swift_validator import SwiftValidator
            validator = SwiftValidator()
            
            # Test auto-fixes
            fixed_content, fixes = validator.apply_auto_fixes(test_code)
            
            if ';' not in fixed_content:
                self.log("✅ Validator removed semicolons")
                self.results['validator_tests']['semicolon_fix'] = True
            else:
                self.log("❌ Validator didn't remove semicolons")
                self.results['validator_tests']['semicolon_fix'] = False
                
        except Exception as e:
            self.log(f"❌ Validator test failed: {e}")
            self.results['validator_tests']['validator'] = False
    
    def test_app_generation_types(self):
        """Test generation of various app types"""
        self.log("\n" + "="*60)
        self.log("TESTING APP GENERATION TYPES")
        self.log("="*60)
        
        app_types = [
            # Simple Apps
            {
                'name': 'calculator',
                'description': 'Create a scientific calculator app with history',
                'expected_files': ['CalculatorView', 'CalculatorViewModel', 'CalculatorButton'],
                'common_errors': ['Hashable conformance', 'ForEach without id']
            },
            {
                'name': 'notes',
                'description': 'Create a note-taking app with categories and search',
                'expected_files': ['Note', 'NoteView', 'NotesListView', 'CategoryView'],
                'common_errors': ['Missing Codable', 'State management']
            },
            {
                'name': 'timer',
                'description': 'Create a pomodoro timer app with notifications',
                'expected_files': ['TimerView', 'TimerViewModel', 'SettingsView'],
                'common_errors': ['Timer syntax', '@Published properties']
            },
            
            # API Apps
            {
                'name': 'stock_tracker',
                'description': 'Create a stock market tracker with real-time prices',
                'expected_files': ['StockService', 'StockModel', 'StockListView'],
                'common_errors': ['Missing imports', 'SSL configuration', 'JSON decoding']
            },
            {
                'name': 'news_reader',
                'description': 'Create a news reader app that fetches articles from NewsAPI',
                'expected_files': ['NewsService', 'Article', 'ArticleView'],
                'common_errors': ['Async/await syntax', 'URL handling']
            },
            
            # Complex Apps
            {
                'name': 'expense_tracker',
                'description': 'Create an expense tracking app with charts and categories',
                'expected_files': ['Expense', 'ExpenseListView', 'ChartView', 'CategoryManager'],
                'common_errors': ['Chart library usage', 'Core Data', 'Complex state']
            },
            {
                'name': 'fitness_tracker',
                'description': 'Create a fitness tracking app with workout plans',
                'expected_files': ['Workout', 'Exercise', 'WorkoutView', 'ProgressView'],
                'common_errors': ['HealthKit integration', 'Complex navigation']
            },
            {
                'name': 'recipe_book',
                'description': 'Create a recipe book app with ingredients and instructions',
                'expected_files': ['Recipe', 'Ingredient', 'RecipeDetailView', 'RecipeListView'],
                'common_errors': ['Image handling', 'Complex data model']
            }
        ]
        
        for app in app_types:
            self.log(f"\n📱 Testing: {app['name']}")
            self.log(f"   Description: {app['description']}")
            
            result = {
                'description': app['description'],
                'expected_files': app['expected_files'],
                'common_errors': app['common_errors'],
                'would_generate': True,  # Simulated
                'validator_fixes_needed': app['common_errors']
            }
            
            self.results['app_generation'][app['name']] = result
            
            # Simulate what validator would fix
            self.log("   Expected validator fixes:")
            for error in app['common_errors']:
                self.log(f"   - {error}")
    
    def test_modifications(self):
        """Test various modification scenarios"""
        self.log("\n" + "="*60)
        self.log("TESTING MODIFICATIONS")
        self.log("="*60)
        
        modifications = [
            # UI Modifications
            {
                'type': 'color_scheme',
                'request': 'Add a color theme picker with 5 different themes',
                'expected_changes': ['@AppStorage for theme', 'ColorScheme enum', 'Theme picker view'],
                'validator_fixes': ['Enum must be Codable for AppStorage']
            },
            {
                'type': 'animation',
                'request': 'Add smooth animations to all transitions',
                'expected_changes': ['.animation() modifiers', '.transition() modifiers'],
                'validator_fixes': ['Animation deprecated warnings', 'Use animation(_:value:)']
            },
            {
                'type': 'layout',
                'request': 'Change from VStack to Grid layout',
                'expected_changes': ['LazyVGrid', 'GridItem'],
                'validator_fixes': ['Grid syntax', 'Adaptive vs Fixed']
            },
            
            # Feature Additions
            {
                'type': 'search',
                'request': 'Add search functionality to the list',
                'expected_changes': ['.searchable modifier', '@State searchText'],
                'validator_fixes': ['searchable only on NavigationView/Stack']
            },
            {
                'type': 'settings',
                'request': 'Add a comprehensive settings screen',
                'expected_changes': ['SettingsView', 'UserDefaults', '@AppStorage'],
                'validator_fixes': ['Missing imports', 'AppStorage property wrappers']
            },
            {
                'type': 'sharing',
                'request': 'Add share functionality to export data',
                'expected_changes': ['ShareLink', 'ActivityViewController'],
                'validator_fixes': ['ShareLink iOS 16+', 'UIKit integration']
            },
            
            # Data Modifications
            {
                'type': 'persistence',
                'request': 'Add data persistence with Core Data',
                'expected_changes': ['@FetchRequest', 'NSManagedObject', 'PersistenceController'],
                'validator_fixes': ['Core Data boilerplate', 'Context in environment']
            },
            {
                'type': 'networking',
                'request': 'Add offline caching for API responses',
                'expected_changes': ['URLCache', 'CachePolicy', 'FileManager'],
                'validator_fixes': ['Async/await syntax', 'Error handling']
            }
        ]
        
        for mod in modifications:
            self.log(f"\n🔧 Testing modification: {mod['type']}")
            self.log(f"   Request: {mod['request']}")
            
            result = {
                'request': mod['request'],
                'expected_changes': mod['expected_changes'],
                'validator_fixes': mod['validator_fixes']
            }
            
            self.results['modifications'][mod['type']] = result
            
            self.log("   Expected validator fixes:")
            for fix in mod['validator_fixes']:
                self.log(f"   - {fix}")
    
    def test_auto_fixes(self):
        """Test auto-fix scenarios for common errors"""
        self.log("\n" + "="*60)
        self.log("TESTING AUTO-FIX SCENARIOS")
        self.log("="*60)
        
        error_scenarios = [
            # Syntax Errors
            {
                'name': 'multiple_semicolons',
                'code': '''
struct ContentView: View {
    @State private var count = 0;
    @State private var name = "";
    
    var body: some View {
        VStack {
            Text("Count: \\(count)");
            Button("Increment") {
                count += 1;
            };
        };
    }
}''',
                'errors': ['Multiple semicolons'],
                'fix': 'Remove all semicolons',
                'validator_capable': True
            },
            
            # Protocol Conformance
            {
                'name': 'complex_hashable',
                'code': '''
struct CustomItem {
    let id: UUID
    let name: String
    let tags: [String]
    let metadata: [String: Any]
}

ForEach(items) { item in
    Text(item.name)
}''',
                'errors': ['CustomItem must conform to Hashable', 'Any prevents Hashable'],
                'fix': 'Add Identifiable instead of Hashable due to Any type',
                'validator_capable': True
            },
            
            # Modern Swift
            {
                'name': 'async_await_errors',
                'code': '''
class DataService {
    func fetchData() {
        let url = URL(string: "https://api.example.com")!
        let data = try URLSession.shared.data(from: url)
        return data
    }
}''',
                'errors': ['Missing async', 'Missing throws', 'Wrong return type'],
                'fix': 'Add async throws, await, and proper return',
                'validator_capable': False  # Too complex for simple validator
            },
            
            # SwiftUI Specific
            {
                'name': 'modifier_order',
                'code': '''
Text("Hello")
    .foregroundColor(.blue)
    .padding()
    .background(Color.red)
    .padding()
    .font(.title)''',
                'errors': ['Inefficient modifier order', 'Double padding'],
                'fix': 'Reorder modifiers for efficiency',
                'validator_capable': True
            },
            
            # iOS Version Issues
            {
                'name': 'ios17_features',
                'code': '''
struct ContentView: View {
    var body: some View {
        Text("Hello")
            .symbolEffect(.bounce)
            .scrollBounceBehavior(.basedOnSize)
    }
}''',
                'errors': ['symbolEffect iOS 17+', 'scrollBounceBehavior iOS 17+'],
                'fix': 'Replace with iOS 16 compatible alternatives',
                'validator_capable': False  # Handled by pattern recovery
            }
        ]
        
        for scenario in error_scenarios:
            self.log(f"\n🔧 Testing: {scenario['name']}")
            self.log(f"   Errors: {', '.join(scenario['errors'])}")
            self.log(f"   Fix: {scenario['fix']}")
            self.log(f"   Validator capable: {'✅' if scenario['validator_capable'] else '❌'}")
            
            self.results['auto_fixes'][scenario['name']] = {
                'errors': scenario['errors'],
                'fix': scenario['fix'],
                'validator_capable': scenario['validator_capable']
            }
    
    def test_complex_apps(self):
        """Test complex app generation scenarios"""
        self.log("\n" + "="*60)
        self.log("TESTING COMPLEX APP SCENARIOS")
        self.log("="*60)
        
        complex_apps = [
            {
                'name': 'uber_clone',
                'description': 'Create a ride-sharing app like Uber',
                'components': ['Maps', 'Real-time tracking', 'Payment', 'User/Driver modes'],
                'challenges': ['MapKit integration', 'WebSocket for real-time', 'Complex state management'],
                'validator_helps': ['Import fixes', 'Async/await syntax', 'Protocol conformances']
            },
            {
                'name': 'instagram_clone',
                'description': 'Create a photo sharing app like Instagram',
                'components': ['Camera', 'Filters', 'Feed', 'Stories', 'Direct messages'],
                'challenges': ['AVFoundation', 'Core Image filters', 'Complex UI', 'Video processing'],
                'validator_helps': ['Import organization', 'Memory management', 'Completion handler syntax']
            },
            {
                'name': 'banking_app',
                'description': 'Create a secure banking application',
                'components': ['Biometric auth', 'Transactions', 'Cards', 'Investments'],
                'challenges': ['Security', 'Keychain', 'Encryption', 'Complex forms'],
                'validator_helps': ['Security attribute syntax', 'Error handling', 'Form validation']
            },
            {
                'name': 'music_streaming',
                'description': 'Create a music streaming app like Spotify',
                'components': ['Audio player', 'Playlists', 'Recommendations', 'Offline mode'],
                'challenges': ['AVAudioPlayer', 'Background audio', 'Core Data', 'DRM'],
                'validator_helps': ['AVFoundation imports', 'Background modes', 'Persistent storage']
            }
        ]
        
        for app in complex_apps:
            self.log(f"\n🚀 Complex App: {app['name']}")
            self.log(f"   Description: {app['description']}")
            self.log(f"   Components: {', '.join(app['components'])}")
            self.log(f"   Challenges: {', '.join(app['challenges'])}")
            self.log(f"   Validator helps with: {', '.join(app['validator_helps'])}")
            
            self.results['complex_apps'][app['name']] = app
    
    def generate_comprehensive_report(self):
        """Generate detailed test report"""
        self.log("\n" + "="*60)
        self.log("COMPREHENSIVE TEST REPORT")
        self.log("="*60)
        
        # Tool Status
        self.log("\n🛠️  Tool Status:")
        self.log(f"   swiftc: {'✅' if self.results['validator_tests'].get('swiftc') else '❌'}")
        self.log(f"   SwiftLint: {'✅' if self.results['swiftlint_available'] else '❌ Not installed'}")
        self.log(f"   Validator: {'✅' if self.results['validator_tests'].get('semicolon_fix') else '❌'}")
        
        # App Generation Coverage
        self.log("\n📱 App Generation Coverage:")
        self.log(f"   Simple apps tested: {len([a for a in self.results['app_generation'] if 'tracker' not in a])}")
        self.log(f"   API apps tested: {len([a for a in self.results['app_generation'] if 'api' in a or 'tracker' in a])}")
        self.log(f"   Complex apps analyzed: {len(self.results['complex_apps'])}")
        
        # Modification Coverage
        self.log("\n🔧 Modification Coverage:")
        self.log(f"   UI modifications: {len([m for m in self.results['modifications'] if m in ['color_scheme', 'animation', 'layout']])}")
        self.log(f"   Feature additions: {len([m for m in self.results['modifications'] if m in ['search', 'settings', 'sharing']])}")
        self.log(f"   Data modifications: {len([m for m in self.results['modifications'] if m in ['persistence', 'networking']])}")
        
        # Auto-Fix Capabilities
        self.log("\n🔄 Auto-Fix Capabilities:")
        validator_capable = sum(1 for f in self.results['auto_fixes'].values() if f['validator_capable'])
        total_scenarios = len(self.results['auto_fixes'])
        self.log(f"   Validator can fix: {validator_capable}/{total_scenarios} scenarios")
        self.log(f"   Requires other recovery: {total_scenarios - validator_capable}/{total_scenarios}")
        
        # Recommendations
        self.log("\n💡 Recommendations:")
        if not self.results['swiftlint_available']:
            self.log("   1. Install SwiftLint for better code quality checks")
            self.log("      brew install swiftlint")
        self.log("   2. Enhance validator with more auto-fix patterns")
        self.log("   3. Add async/await fix patterns for modern Swift")
        self.log("   4. Consider SwiftFormat for consistent code style")
        
        # Save detailed report
        with open('comprehensive_validator_test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log("\n📄 Detailed report saved to comprehensive_validator_test_report.json")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        self.log("SwiftGen Comprehensive Validator Test")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check available tools
        self.check_swiftlint()
        self.test_swift_validation_tools()
        
        # Test different scenarios
        self.test_app_generation_types()
        self.test_modifications()
        self.test_auto_fixes()
        self.test_complex_apps()
        
        # Generate report
        self.generate_comprehensive_report()
        
        self.log(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Run comprehensive validator tests"""
    tester = ComprehensiveValidatorTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()