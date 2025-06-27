#!/usr/bin/env python3
"""
UI Code Scraper - Specialized scraper for iOS UI components and libraries
Focuses on Apple HIG compliant designs and beautiful UI patterns
"""

import os
import json
import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import List, Dict, Optional
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UICodeScraper:
    """Scrapes high-quality iOS UI code following Apple design guidelines"""
    
    def __init__(self, output_dir: str = "ui_training_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        # UI-specific categories
        self.ui_categories = {
            "navigation_patterns": [],     # Navigation designs
            "list_designs": [],            # Beautiful list/table views
            "form_components": [],         # Input forms and controls
            "animations": [],              # Smooth animations
            "gestures": [],                # Gesture handling
            "custom_controls": [],         # Custom UI controls
            "onboarding": [],              # Onboarding flows
            "settings_screens": [],        # Settings UI patterns
            "modal_presentations": [],     # Modals and sheets
            "tab_bars": [],                # Tab bar designs
            "search_interfaces": [],       # Search UI
            "empty_states": [],            # Empty state designs
            "loading_states": [],          # Loading indicators
            "error_handling_ui": [],       # Error UI patterns
            "accessibility": []            # Accessible designs
        }
        
        # Popular iOS UI libraries to scrape
        self.ui_libraries = [
            ("Introspect/Introspect", "SwiftUI introspection"),
            ("SwiftUIX/SwiftUIX", "Extended SwiftUI components"),
            ("SFSafeSymbols/SFSafeSymbols", "SF Symbols wrapper"),
            ("slackhq/PanModal", "Modal presentation"),
            ("exyte/PopupView", "Popup components"),
            ("Juanpe/SkeletonView", "Loading skeletons"),
            ("ApplikeySolutions/VegaScroll", "Scroll animations"),
            ("ninjaprox/NVActivityIndicatorView", "Loading indicators"),
            ("efremidze/Magnetic", "Bubble picker UI"),
            ("Ramotion/animated-tab-bar", "Animated tab bars"),
            ("Ramotion/folding-cell", "Folding animations"),
            ("CosmicMind/Material", "Material Design"),
            ("hyperoslo/Presentation", "Onboarding"),
            ("daltoniam/Starscream", "WebSocket for real-time UI"),
            ("SwipeCellKit/SwipeCellKit", "Swipeable cells")
        ]
        
        # Apple sample code repositories
        self.apple_samples = [
            "apple/sample-food-truck",
            "apple/sample-backyard-birds",
            "apple/sample-app-dev-training"
        ]
    
    async def scrape_ui_focused_repos(self, max_repos: int = 50):
        """Scrape repositories with focus on UI/UX"""
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        ui_queries = [
            "SwiftUI design system",
            "iOS custom components",
            "SwiftUI animations",
            "iOS UI library Swift",
            "SwiftUI beautiful",
            "iOS app design Swift",
            "SwiftUI components library",
            "iOS human interface guidelines"
        ]
        
        async with aiohttp.ClientSession() as session:
            # Scrape UI libraries first
            logger.info("Scraping popular UI libraries...")
            for repo_path, description in self.ui_libraries[:10]:  # Limit for demo
                try:
                    owner, repo = repo_path.split('/')
                    files = await self._get_repo_ui_files(session, owner, repo, headers)
                    if files:
                        self._process_ui_files(files, {
                            "name": repo,
                            "description": description,
                            "type": "ui_library"
                        })
                        logger.info(f"Scraped UI library: {repo}")
                    await asyncio.sleep(2)  # Rate limit
                except Exception as e:
                    logger.error(f"Error scraping {repo_path}: {e}")
            
            # Scrape Apple samples
            logger.info("Scraping Apple sample code...")
            for repo_path in self.apple_samples:
                try:
                    owner, repo = repo_path.split('/')
                    files = await self._get_repo_ui_files(session, owner, repo, headers)
                    if files:
                        self._process_ui_files(files, {
                            "name": repo,
                            "description": "Apple official sample",
                            "type": "apple_sample"
                        })
                        logger.info(f"Scraped Apple sample: {repo}")
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error scraping {repo_path}: {e}")
            
            # Search for UI-focused repos
            for query in ui_queries[:3]:  # Limit for demo
                logger.info(f"Searching for: {query}")
                await self._search_and_scrape_ui_repos(session, headers, query, max_repos=5)
    
    async def _search_and_scrape_ui_repos(self, session, headers, query, max_repos=10):
        """Search and scrape UI-focused repositories"""
        search_url = "https://api.github.com/search/repositories"
        params = {
            "q": f"{query} language:Swift stars:>50",
            "sort": "stars",
            "order": "desc",
            "per_page": max_repos
        }
        
        try:
            async with session.get(search_url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for repo in data.get("items", []):
                        owner = repo["owner"]["login"]
                        repo_name = repo["name"]
                        
                        files = await self._get_repo_ui_files(session, owner, repo_name, headers)
                        if files:
                            self._process_ui_files(files, repo)
                            logger.info(f"Scraped {repo_name}")
                        
                        await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Search error: {e}")
    
    async def _get_repo_ui_files(self, session, owner: str, repo: str, headers: dict) -> List[Dict]:
        """Get UI-related Swift files from repository"""
        ui_files = []
        
        # UI-related paths to check
        ui_paths = [
            "Sources/Views",
            "Sources/UI",
            "Sources/Components",
            "UI",
            "Views",
            "Components",
            "Design",
            "Screens"
        ]
        
        for path in ui_paths:
            try:
                url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        contents = await resp.json()
                        for item in contents:
                            if item["name"].endswith(".swift") and self._is_ui_file(item["name"]):
                                content = await self._get_file_content(session, item["download_url"])
                                if content and self._contains_ui_code(content):
                                    ui_files.append({
                                        "path": item["path"],
                                        "content": content,
                                        "url": item["html_url"]
                                    })
            except:
                continue
        
        return ui_files
    
    def _is_ui_file(self, filename: str) -> bool:
        """Check if filename suggests UI content"""
        ui_keywords = [
            "View", "Button", "Cell", "Controller", "Screen",
            "Layout", "Design", "Style", "Theme", "Animation",
            "Transition", "Gesture", "Appearance"
        ]
        return any(keyword in filename for keyword in ui_keywords)
    
    def _contains_ui_code(self, content: str) -> bool:
        """Check if content contains UI-related code"""
        ui_patterns = [
            r"struct\s+\w+\s*:\s*View",
            r"class\s+\w+\s*:\s*UI",
            r"@IBDesignable",
            r"\.animation\(",
            r"\.transition\(",
            r"\.gesture\(",
            r"NavigationView|NavigationStack",
            r"TabView",
            r"List\s*\{",
            r"Form\s*\{",
            r"\.sheet\(",
            r"\.alert\(",
            r"\.toolbar\(",
            r"@Environment\(\\\.colorScheme\)"
        ]
        
        return any(re.search(pattern, content) for pattern in ui_patterns)
    
    def _categorize_ui_file(self, content: str, path: str) -> str:
        """Categorize UI file based on content"""
        content_lower = content.lower()
        path_lower = path.lower()
        
        # Check for specific UI patterns
        if "navigationview" in content_lower or "navigationstack" in content_lower:
            return "navigation_patterns"
        elif "list {" in content_lower or "foreach" in content_lower:
            return "list_designs"
        elif "form {" in content_lower or "textfield" in content_lower:
            return "form_components"
        elif ".animation(" in content_lower or ".transition(" in content_lower:
            return "animations"
        elif ".gesture(" in content_lower or "draggesture" in content_lower:
            return "gestures"
        elif "tabview" in content_lower:
            return "tab_bars"
        elif ".sheet(" in content_lower or ".fullscreencover(" in content_lower:
            return "modal_presentations"
        elif "onboarding" in path_lower or "welcome" in path_lower:
            return "onboarding"
        elif "settings" in path_lower:
            return "settings_screens"
        elif "search" in content_lower:
            return "search_interfaces"
        elif "empty" in content_lower and "state" in content_lower:
            return "empty_states"
        elif "loading" in content_lower or "progress" in content_lower:
            return "loading_states"
        elif "error" in content_lower:
            return "error_handling_ui"
        elif "accessible" in content_lower or "voiceover" in content_lower:
            return "accessibility"
        else:
            return "custom_controls"
    
    def _process_ui_files(self, files: List[Dict], repo_info: Dict):
        """Process and save UI files"""
        for file in files:
            category = self._categorize_ui_file(file["content"], file["path"])
            
            # Extract UI patterns and components
            ui_patterns = self._extract_ui_patterns(file["content"])
            
            training_example = {
                "repo": repo_info.get("name", "unknown"),
                "description": repo_info.get("description", ""),
                "type": repo_info.get("type", "general"),
                "file_path": file["path"],
                "content": file["content"],
                "category": category,
                "ui_patterns": ui_patterns,
                "timestamp": datetime.now().isoformat()
            }
            
            self._save_ui_example(training_example, category)
    
    def _extract_ui_patterns(self, content: str) -> Dict:
        """Extract specific UI patterns from code"""
        patterns = {
            "uses_sf_symbols": bool(re.search(r'Image\(systemName:', content)),
            "has_dark_mode": bool(re.search(r'colorScheme|\.dark|\.light', content)),
            "uses_animations": bool(re.search(r'\.animation\(|withAnimation', content)),
            "is_accessible": bool(re.search(r'\.accessibility|VoiceOver', content)),
            "uses_haptics": bool(re.search(r'UIImpactFeedback|haptic', content)),
            "has_gestures": bool(re.search(r'\.gesture\(|Gesture', content)),
            "follows_safe_area": bool(re.search(r'safeAreaInsets|\.safe', content)),
            "uses_gradients": bool(re.search(r'LinearGradient|RadialGradient', content)),
            "has_shadows": bool(re.search(r'\.shadow\(', content)),
            "uses_blur": bool(re.search(r'\.blur\(|VisualEffect', content))
        }
        return patterns
    
    def _save_ui_example(self, example: Dict, category: str):
        """Save UI training example"""
        category_dir = self.output_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Generate filename
        import hashlib
        content_hash = hashlib.md5(example["content"].encode()).hexdigest()[:8]
        filename = f"{example['repo']}_{content_hash}.json"
        
        with open(category_dir / filename, 'w') as f:
            json.dump(example, f, indent=2)
    
    def create_ui_training_dataset(self):
        """Create specialized UI training dataset"""
        training_data = []
        
        for category in self.ui_categories:
            category_dir = self.output_dir / category
            if category_dir.exists():
                for file_path in category_dir.glob("*.json"):
                    with open(file_path, 'r') as f:
                        example = json.load(f)
                        
                        # Create specialized prompts for UI
                        if category == "navigation_patterns":
                            prompt = f"Create a SwiftUI navigation interface with smooth transitions"
                        elif category == "animations":
                            prompt = f"Add smooth animations to this SwiftUI view"
                        elif category == "form_components":
                            prompt = f"Design a beautiful form interface following Apple HIG"
                        else:
                            prompt = f"Create a {category.replace('_', ' ')} UI component"
                        
                        training_data.append({
                            "prompt": prompt,
                            "completion": example["content"],
                            "category": category,
                            "ui_patterns": example.get("ui_patterns", {})
                        })
        
        # Save UI-focused training dataset
        with open(self.output_dir / "ui_training_dataset.jsonl", 'w') as f:
            for item in training_data:
                f.write(json.dumps(item) + '\n')
        
        logger.info(f"Created UI training dataset with {len(training_data)} examples")
        return training_data

async def main():
    """Run the UI code scraper"""
    scraper = UICodeScraper()
    
    logger.info("Starting UI-focused code collection...")
    await scraper.scrape_ui_focused_repos(max_repos=20)
    
    logger.info("Creating UI training dataset...")
    scraper.create_ui_training_dataset()

if __name__ == "__main__":
    asyncio.run(main())