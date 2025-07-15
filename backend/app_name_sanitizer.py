import re
import unicodedata
from typing import Dict, Tuple

class AppNameSanitizer:
    """Ensures consistent app naming across all iOS development artifacts"""

    @staticmethod
    def sanitize_for_bundle_id(name: str) -> str:
        """
        Convert app name to valid bundle ID component
        Example: "Cool Timer" -> "cooltimer"
        """
        # Remove non-alphanumeric characters
        sanitized = re.sub(r'[^a-zA-Z0-9]', '', name)
        # Convert to lowercase
        return sanitized.lower()

    @staticmethod
    def sanitize_for_product_name(name: str) -> str:
        """
        Convert app name to valid product name (no spaces)
        Example: "Cool Timer" -> "CoolTimer"
        """
        # Split by spaces and capitalize each word
        words = name.strip().split()
        # Join without spaces
        return ''.join(word.capitalize() for word in words)

    @staticmethod
    def sanitize_for_display_name(name: str) -> str:
        """
        Ensure consistent display name
        Example: "cool timer" -> "Cool Timer"
        """
        # Normalize unicode characters
        normalized = unicodedata.normalize('NFKD', name)
        # Convert to ASCII
        ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
        # Title case
        return ' '.join(word.capitalize() for word in ascii_name.split())

    @staticmethod
    def sanitize_for_scheme_name(name: str) -> str:
        """
        Convert app name to valid Xcode scheme name
        Example: "Cool Timer!" -> "CoolTimer"
        """
        # Remove special characters
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        # Remove spaces
        return sanitized.replace(' ', '')

    @staticmethod
    def generate_consistent_names(app_name: str) -> Dict[str, str]:
        """
        Generate all required name variants from a single app name
        """
        sanitizer = AppNameSanitizer()

        return {
            'display_name': sanitizer.sanitize_for_display_name(app_name),
            'product_name': sanitizer.sanitize_for_product_name(app_name),
            'bundle_id_suffix': sanitizer.sanitize_for_bundle_id(app_name),
            'scheme_name': sanitizer.sanitize_for_scheme_name(app_name),
            'target_name': sanitizer.sanitize_for_scheme_name(app_name),
            'app_file_name': sanitizer.sanitize_for_product_name(app_name)
        }

    @staticmethod
    def validate_bundle_id(bundle_id: str) -> Tuple[bool, str]:
        """
        Validate a complete bundle ID
        """
        # Bundle ID pattern: com.company.appname
        pattern = r'^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*$'

        if not re.match(pattern, bundle_id):
            return False, "Invalid bundle ID format. Must be like: com.company.appname"

        # Check for reserved words
        reserved_words = ['apple', 'ios', 'iphone', 'ipad', 'watch', 'mac']
        bundle_lower = bundle_id.lower()

        for reserved in reserved_words:
            if reserved in bundle_lower.split('.'):
                return False, f"Bundle ID cannot contain reserved word: {reserved}"

        return True, "Valid"

    @staticmethod
    def fix_project_yml_names(project_yml_content: str, app_name: str) -> str:
        """
        Fix all name references in project.yml to be consistent
        """
        names = AppNameSanitizer.generate_consistent_names(app_name)

        # Replace all name variants
        fixed_content = project_yml_content

        # Fix target names
        fixed_content = re.sub(
            r'targets:\s*\n\s*\w+:',
            f'targets:\n  {names["target_name"]}:',
            fixed_content
        )

        # Fix product name
        fixed_content = re.sub(
            r'PRODUCT_NAME:\s*["\']?[^"\'\n]+["\']?',
            f'PRODUCT_NAME: "{names["product_name"]}"',
            fixed_content
        )

        # Fix display name
        fixed_content = re.sub(
            r'INFOPLIST_KEY_CFBundleDisplayName:\s*["\']?[^"\'\n]+["\']?',
            f'INFOPLIST_KEY_CFBundleDisplayName: "{names["display_name"]}"',
            fixed_content
        )

        # Fix bundle identifier
        if 'PRODUCT_BUNDLE_IDENTIFIER:' in fixed_content:
            fixed_content = re.sub(
                r'(PRODUCT_BUNDLE_IDENTIFIER:\s*["\']?[^.]+\.[^.]+\.)[^"\'\s]+(["\']?)',
                f'\\1{names["bundle_id_suffix"]}\\2',
                fixed_content
            )

        return fixed_content


# Usage example in your project manager
def apply_consistent_naming(project_config: dict, app_name: str) -> dict:
    """
    Apply consistent naming to project configuration
    """
    names = AppNameSanitizer.generate_consistent_names(app_name)

    # Update all relevant fields
    if 'name' in project_config:
        project_config['name'] = names['product_name']

    if 'targets' in project_config:
        # Rename target key
        old_targets = project_config['targets']
        project_config['targets'] = {}

        for target_name, target_config in old_targets.items():
            new_target_name = names['target_name']
            project_config['targets'][new_target_name] = target_config

            # Update settings
            if 'settings' in target_config:
                settings = target_config['settings']
                if 'base' in settings:
                    base = settings['base']
                    base['PRODUCT_NAME'] = names['product_name']
                    base['INFOPLIST_KEY_CFBundleDisplayName'] = names['display_name']

                    # Fix bundle ID
                    if 'PRODUCT_BUNDLE_IDENTIFIER' in base:
                        bundle_parts = base['PRODUCT_BUNDLE_IDENTIFIER'].split('.')
                        if len(bundle_parts) >= 3:
                            bundle_parts[-1] = names['bundle_id_suffix']
                            base['PRODUCT_BUNDLE_IDENTIFIER'] = '.'.join(bundle_parts)

    if 'schemes' in project_config:
        # Update scheme names
        old_schemes = project_config['schemes']
        project_config['schemes'] = {}

        for scheme_name, scheme_config in old_schemes.items():
            new_scheme_name = names['scheme_name']
            project_config['schemes'][new_scheme_name] = scheme_config

            # Update build targets
            if 'build' in scheme_config and 'targets' in scheme_config['build']:
                build_targets = scheme_config['build']['targets']
                if isinstance(build_targets, dict):
                    new_build_targets = {}
                    for target, settings in build_targets.items():
                        new_build_targets[names['target_name']] = settings
                    scheme_config['build']['targets'] = new_build_targets

            # Update run target
            if 'run' in scheme_config and 'target' in scheme_config['run']:
                scheme_config['run']['target'] = names['target_name']

            # Update test target
            if 'test' in scheme_config and 'target' in scheme_config['test']:
                scheme_config['test']['target'] = names['target_name']

    return project_config


# Integration with Info.plist generation
def generate_info_plist_with_consistent_names(app_name: str, bundle_id_prefix: str = "com.swiftgen") -> dict:
    """
    Generate Info.plist with consistent naming
    """
    names = AppNameSanitizer.generate_consistent_names(app_name)

    return {
        'CFBundleDevelopmentRegion': 'en',
        'CFBundleDisplayName': names['display_name'],
        'CFBundleExecutable': '$(EXECUTABLE_NAME)',
        'CFBundleIdentifier': f"{bundle_id_prefix}.{names['bundle_id_suffix']}",
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleName': names['product_name'],
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '1.0',
        'CFBundleVersion': '1',
        'LSRequiresIPhoneOS': True,
        'UIApplicationSceneManifest': {
            'UIApplicationSupportsMultipleScenes': False,
            'UISceneConfigurations': {
                'UIWindowSceneSessionRoleApplication': [{
                    'UISceneConfigurationName': 'Default Configuration',
                    'UISceneDelegateClassName': '$(PRODUCT_MODULE_NAME).SceneDelegate'
                }]
            }
        },
        'UILaunchStoryboardName': 'LaunchScreen',
        'UIRequiredDeviceCapabilities': ['armv7'],
        'UISupportedInterfaceOrientations': [
            'UIInterfaceOrientationPortrait',
            'UIInterfaceOrientationLandscapeLeft',
            'UIInterfaceOrientationLandscapeRight'
        ],
        'UISupportedInterfaceOrientations~ipad': [
            'UIInterfaceOrientationPortrait',
            'UIInterfaceOrientationPortraitUpsideDown',
            'UIInterfaceOrientationLandscapeLeft',
            'UIInterfaceOrientationLandscapeRight'
        ]
    }