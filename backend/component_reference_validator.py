"""
Component Reference Validator for SwiftGen
Ensures all referenced Swift components exist before building
"""

import re
from typing import List, Dict, Tuple, Set
import os

class ComponentReferenceValidator:
    """Validates that all referenced components exist in the project"""
    
    def __init__(self):
        self.swift_type_pattern = re.compile(r'\b([A-Z][a-zA-Z0-9]*)\s*\{|\b([A-Z][a-zA-Z0-9]*)\s*\(')
        self.import_pattern = re.compile(r'import\s+(\w+)')
        self.standard_types = {
            # SwiftUI Views
            'View', 'Text', 'Button', 'Image', 'VStack', 'HStack', 'ZStack', 'List',
            'NavigationView', 'NavigationStack', 'NavigationLink', 'Form', 'Section',
            'Spacer', 'Divider', 'ScrollView', 'LazyVStack', 'LazyHStack', 'Grid',
            'Toggle', 'TextField', 'SecureField', 'TextEditor', 'Picker', 'DatePicker',
            'Slider', 'Stepper', 'ProgressView', 'Label', 'Link', 'Menu', 'ColorPicker',
            'TabView', 'Sheet', 'Alert', 'ActionSheet', 'GeometryReader', 'EmptyView',
            'Group', 'AsyncImage', 'Canvas', 'DisclosureGroup', 'OutlineGroup',
            
            # SwiftUI Modifiers & Properties
            'Color', 'Font', 'EdgeInsets', 'Alignment', 'Animation', 'AnyView',
            'CGFloat', 'CGSize', 'CGPoint', 'CGRect', 'LinearGradient', 'RadialGradient',
            'AngularGradient', 'Gradient', 'GradientStop',
            
            # Swift Standard Types
            'String', 'Int', 'Double', 'Float', 'Bool', 'Array', 'Dictionary', 'Set',
            'Optional', 'Result', 'Error', 'Date', 'URL', 'UUID', 'Data', 'Any',
            'AnyObject', 'Character', 'Range', 'ClosedRange', 'TimeInterval',
            'Void', 'Never', 'Int8', 'Int16', 'Int32', 'Int64', 'UInt', 'UInt8',
            'UInt16', 'UInt32', 'UInt64', 'Decimal', 'NSNumber', 'NSString',
            
            # Swift Control Flow & Protocols
            'ForEach', 'if', 'else', 'switch', 'case', 'while', 'for', 'repeat',
            'Equatable', 'Hashable', 'Codable', 'Identifiable', 'ObservableObject',
            'Publisher', 'Cancellable', 'CaseIterable', 'CustomStringConvertible',
            'Comparable', 'RawRepresentable', 'Encodable', 'Decodable',
            
            # Swift Foundation Types
            'JSONEncoder', 'JSONDecoder', 'UserDefaults', 'NotificationCenter',
            'Timer', 'DispatchQueue', 'FileManager', 'Bundle', 'DateFormatter',
            'NumberFormatter', 'ByteCountFormatter', 'DateComponentsFormatter',
            'MeasurementFormatter', 'PersonNameComponentsFormatter', 'NSPredicate',
            
            # Common Frameworks
            'UIKit', 'Foundation', 'Combine', 'CoreData', 'CoreLocation', 'MapKit',
            'SwiftUI', 'AVFoundation', 'CoreGraphics', 'CoreAnimation', 'CoreImage',
            'PhotosUI', 'WebKit', 'SafariServices', 'MessageUI', 'StoreKit',
            
            # Combine Types
            'AnyCancellable', 'PassthroughSubject', 'CurrentValueSubject',
            'Published', 'ObservableObjectPublisher', 'Future', 'Just', 'Empty',
            'Fail', 'Record', 'Share', 'Multicast',
            
            # Property Wrappers
            'State', 'Binding', 'ObservedObject', 'StateObject', 'EnvironmentObject',
            'Environment', 'AppStorage', 'SceneStorage', 'FocusState', 'Published',
            'FetchRequest', 'GestureState', 'ScaledMetric', 'UIApplicationDelegateAdaptor',
            
            # Common Patterns
            'ContentView', 'MainView', 'HomeView', 'SettingsView', 'DetailView',
            'ListView', 'GridView', 'ProfileView', 'LoginView', 'OnboardingView',
            
            # SwiftUI Scenes & Apps
            'App', 'Scene', 'WindowGroup', 'DocumentGroup', 'Settings',
            'WKNotificationScene', 'UIApplicationDelegate',
            
            # SwiftUI Shapes
            'Rectangle', 'RoundedRectangle', 'Circle', 'Ellipse', 'Capsule', 'Path',
            'Shape', 'InsettableShape', 'ContainerRelativeShape',
            
            # SwiftUI Layout
            'Frame', 'Padding', 'Background', 'Overlay', 'Border', 'GeometryProxy',
            'CoordinateSpace', 'Anchor', 'GeometryPreference',
            
            # Common View Components
            'NavigationBar', 'TabBar', 'ToolbarItem', 'ToolbarItemGroup', 'ToolbarItemPlacement',
            
            # SwiftUI Gestures
            'TapGesture', 'LongPressGesture', 'DragGesture', 'MagnificationGesture',
            'RotationGesture', 'Gesture', 'GestureStateGesture',
            
            # Foundation Classes
            'NSObject', 'NSArray', 'NSDictionary', 'NSSet', 'NSDate', 'NSURL',
            'NSError', 'NSException', 'NSNotification', 'NSNull', 'NSValue',
            
            # Common Button/Control Styles
            'ButtonStyle', 'PrimitiveButtonStyle', 'ToggleStyle', 'PickerStyle',
            'TextFieldStyle', 'ListStyle', 'NavigationViewStyle', 'TabViewStyle',
            'GroupBoxStyle', 'LabelStyle', 'ProgressViewStyle', 'MenuStyle',
            
            # Preview Types
            'PreviewProvider', 'PreviewDevice', 'PreviewLayout', 'PreviewContext',
            
            # Additional System Types
            'MainActor', 'Task', 'AsyncSequence', 'AsyncStream', 'CheckedContinuation',
            'UnsafeContinuation', 'Actor', 'GlobalActor', 'Sendable'
        }
    
    def validate_references(self, files: List[Dict[str, str]]) -> Tuple[bool, List[Dict[str, any]]]:
        """
        Validate that all referenced components exist
        Returns: (is_valid, missing_components_info)
        """
        print("[COMPONENT VALIDATOR] Starting validation...")
        
        # First, collect all defined types
        defined_types = self._collect_defined_types(files)
        defined_types.update(self.standard_types)
        
        # Then, collect all referenced types
        referenced_types = self._collect_referenced_types(files)
        
        # Find missing types
        missing_types = referenced_types - defined_types
        
        # Filter out false positives
        missing_types = self._filter_false_positives(missing_types, files)
        
        if not missing_types:
            print("[COMPONENT VALIDATOR] All components validated successfully")
            return True, []
        
        # Generate component info for missing types
        missing_info = []
        for missing_type in missing_types:
            component_info = self._generate_component_info(missing_type, files)
            if component_info:
                missing_info.append(component_info)
        
        print(f"[COMPONENT VALIDATOR] Found {len(missing_info)} missing components")
        return False, missing_info
    
    def _collect_defined_types(self, files: List[Dict[str, str]]) -> Set[str]:
        """Collect all types defined in the project"""
        defined_types = set()
        
        for file_info in files:
            content = file_info.get('content', '')
            
            # Find struct/class/enum definitions
            type_definitions = re.findall(
                r'(?:struct|class|enum|protocol|extension)\s+([A-Z][a-zA-Z0-9]*)',
                content
            )
            defined_types.update(type_definitions)
            
            # Find typealiases
            typealiases = re.findall(r'typealias\s+([A-Z][a-zA-Z0-9]*)', content)
            defined_types.update(typealiases)
        
        return defined_types
    
    def _collect_referenced_types(self, files: List[Dict[str, str]]) -> Set[str]:
        """Collect all types referenced in the project"""
        referenced_types = set()
        
        for file_info in files:
            content = file_info.get('content', '')
            
            # Find type references
            matches = self.swift_type_pattern.findall(content)
            for match in matches:
                # match is a tuple, get the non-empty group
                type_name = match[0] or match[1]
                if type_name:
                    referenced_types.add(type_name)
            
            # Find types in variable declarations
            var_types = re.findall(r'(?:var|let)\s+\w+\s*:\s*([A-Z][a-zA-Z0-9]*)', content)
            referenced_types.update(var_types)
            
            # Find types in function parameters and returns
            func_types = re.findall(r'->\s*([A-Z][a-zA-Z0-9]*)', content)
            referenced_types.update(func_types)
        
        return referenced_types
    
    def _filter_false_positives(self, missing_types: Set[str], files: List[Dict[str, str]]) -> Set[str]:
        """Filter out false positives from missing types"""
        filtered = set()
        
        for missing_type in missing_types:
            # Skip if it's likely a generic parameter
            if len(missing_type) == 1:  # Like T, U, V
                continue
            
            # Skip if it's a common abbreviation or partial match
            if missing_type in ['UI', 'CG', 'NS', 'CF']:
                continue
            
            # Check if it's imported from a framework
            is_imported = False
            for file_info in files:
                content = file_info.get('content', '')
                imports = self.import_pattern.findall(content)
                
                # Check if type might come from an imported framework
                for imported in imports:
                    if missing_type.startswith(imported):
                        is_imported = True
                        break
                
                if is_imported:
                    break
            
            if not is_imported:
                filtered.add(missing_type)
        
        return filtered
    
    def _generate_component_info(self, component_name: str, files: List[Dict[str, str]]) -> Dict[str, any]:
        """Generate information about a missing component"""
        # Determine component type based on usage context
        component_type = self._infer_component_type(component_name, files)
        
        if not component_type:
            return None
        
        # Generate appropriate template
        if component_type == 'View':
            return {
                'name': component_name,
                'type': 'View',
                'file_name': f"{component_name}.swift",
                'content': self._generate_view_template(component_name)
            }
        elif component_type == 'Model':
            return {
                'name': component_name,
                'type': 'Model',
                'file_name': f"{component_name}.swift",
                'content': self._generate_model_template(component_name)
            }
        elif component_type == 'ViewModifier':
            return {
                'name': component_name,
                'type': 'ViewModifier',
                'file_name': f"{component_name}.swift",
                'content': self._generate_view_modifier_template(component_name)
            }
        
        return None
    
    def _infer_component_type(self, component_name: str, files: List[Dict[str, str]]) -> str:
        """Infer the type of component based on its usage"""
        # Check usage patterns
        for file_info in files:
            content = file_info.get('content', '')
            
            # Check if used as a View
            if re.search(rf'{component_name}\s*\{{', content) or \
               re.search(rf'{component_name}\s*\(\)', content):
                # Check if it's in a View context
                if 'body:' in content and 'some View' in content:
                    return 'View'
            
            # Check if used as a model/data type
            if re.search(rf'@StateObject.*{component_name}', content) or \
               re.search(rf'@ObservedObject.*{component_name}', content) or \
               re.search(rf'let.*:\s*{component_name}', content):
                return 'Model'
            
            # Check if used as a ViewModifier
            if re.search(rf'\.modifier\({component_name}', content):
                return 'ViewModifier'
        
        # Default based on naming convention
        if component_name.endswith('View'):
            return 'View'
        elif component_name.endswith('Model') or component_name.endswith('Manager'):
            return 'Model'
        elif component_name.endswith('Modifier'):
            return 'ViewModifier'
        
        # Default to View for unknown types
        return 'View'
    
    def _generate_view_template(self, view_name: str) -> str:
        """Generate a template for a missing View component"""
        return f'''import SwiftUI

struct {view_name}: View {{
    var body: some View {{
        VStack {{
            Text("{view_name}")
                .font(.title)
                .padding()
            
            // TODO: Implement {view_name} content
            Text("This view needs to be implemented")
                .foregroundColor(.secondary)
        }}
        .padding()
    }}
}}

#Preview {{
    {view_name}()
}}'''
    
    def _generate_model_template(self, model_name: str) -> str:
        """Generate a template for a missing Model component"""
        return f'''import Foundation
import SwiftUI

class {model_name}: ObservableObject {{
    // TODO: Add published properties
    @Published var isLoading = false
    
    init() {{
        // TODO: Initialize {model_name}
    }}
    
    // TODO: Add methods for {model_name}
}}'''
    
    def _generate_view_modifier_template(self, modifier_name: str) -> str:
        """Generate a template for a missing ViewModifier"""
        return f'''import SwiftUI

struct {modifier_name}: ViewModifier {{
    func body(content: Content) -> some View {{
        content
            // TODO: Implement {modifier_name} modifications
    }}
}}

extension View {{
    func {modifier_name[0].lower() + modifier_name[1:]}() -> some View {{
        modifier({modifier_name}())
    }}
}}'''
    
    def fix_missing_components(self, files: List[Dict[str, str]], missing_components: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """Fix missing components by generating them"""
        if not missing_components:
            return files
        
        # Create a copy of files to modify
        updated_files = files.copy()
        
        # Generate files for each missing component
        for component_info in missing_components:
            if component_info and 'file_name' in component_info and 'content' in component_info:
                # Check if file already exists
                file_exists = any(f.get('path', '').endswith(component_info['file_name']) for f in updated_files)
                
                if not file_exists:
                    # Determine appropriate directory
                    if component_info['type'] == 'Model':
                        path = f"Sources/Models/{component_info['file_name']}"
                    elif component_info['type'] == 'ViewModifier':
                        path = f"Sources/ViewModifiers/{component_info['file_name']}"
                    else:
                        path = f"Sources/Views/{component_info['file_name']}"
                    
                    # Add the new file
                    updated_files.append({
                        'path': path,
                        'content': component_info['content']
                    })
                    
                    print(f"[COMPONENT VALIDATOR] Generated missing {component_info['type']}: {component_info['name']}")
        
        return updated_files