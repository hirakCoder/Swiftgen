#!/usr/bin/env python3
"""
Swift Code Scraper - Collects high-quality Swift/iOS code for fine-tuning
"""

import os
import json
import time
import asyncio
import aiohttp
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SwiftCodeScraper:
    """Scrapes Swift code from various sources for training data"""
    
    def __init__(self, output_dir: str = "swift_training_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # GitHub API token (optional but recommended)
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        # Track scraped content
        self.scraped_urls = self._load_scraped_urls()
        
        # Categories for organization
        self.categories = {
            "swiftui_apps": [],
            "view_components": [],
            "viewmodels": [],
            "models": [],
            "networking": [],
            "utilities": [],
            "animations": [],
            "navigation": []
        }
    
    def _load_scraped_urls(self) -> set:
        """Load already scraped URLs to avoid duplicates"""
        scraped_file = self.output_dir / "scraped_urls.json"
        if scraped_file.exists():
            with open(scraped_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_scraped_urls(self):
        """Save scraped URLs"""
        with open(self.output_dir / "scraped_urls.json", 'w') as f:
            json.dump(list(self.scraped_urls), f)
    
    async def scrape_github_repos(self, query: str = "SwiftUI app", max_repos: int = 100):
        """Scrape Swift repositories from GitHub"""
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        repos_collected = 0
        page = 1
        
        async with aiohttp.ClientSession() as session:
            while repos_collected < max_repos:
                # Search for Swift repositories
                search_url = f"https://api.github.com/search/repositories"
                params = {
                    "q": f"{query} language:Swift",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 30,
                    "page": page
                }
                
                try:
                    async with session.get(search_url, headers=headers, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            for repo in data.get("items", []):
                                if repos_collected >= max_repos:
                                    break
                                
                                repo_url = repo["html_url"]
                                if repo_url not in self.scraped_urls:
                                    # Get Swift files from repo
                                    swift_files = await self._get_repo_swift_files(
                                        session, repo["owner"]["login"], repo["name"], headers
                                    )
                                    
                                    if swift_files:
                                        self._process_swift_files(swift_files, repo)
                                        self.scraped_urls.add(repo_url)
                                        repos_collected += 1
                                        logger.info(f"Scraped {repo['name']} - {repos_collected}/{max_repos}")
                                    
                                    # Rate limit handling
                                    await asyncio.sleep(1)
                        else:
                            logger.warning(f"GitHub API error: {resp.status}")
                            break
                
                except Exception as e:
                    logger.error(f"Error scraping GitHub: {e}")
                    break
                
                page += 1
                
                # Save progress
                self._save_scraped_urls()
    
    async def _get_repo_swift_files(self, session, owner: str, repo: str, headers: dict) -> List[Dict]:
        """Get Swift files from a repository"""
        swift_files = []
        
        # Get repository contents
        contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        
        try:
            async with session.get(contents_url, headers=headers) as resp:
                if resp.status == 200:
                    contents = await resp.json()
                    
                    # Find Swift files
                    for item in contents:
                        if item["type"] == "file" and item["name"].endswith(".swift"):
                            # Get file content
                            file_content = await self._get_file_content(session, item["download_url"])
                            if file_content:
                                swift_files.append({
                                    "path": item["path"],
                                    "content": file_content,
                                    "url": item["html_url"]
                                })
                        elif item["type"] == "dir" and item["name"] in ["Sources", "Source", "App"]:
                            # Recursively get files from important directories
                            subdir_files = await self._get_directory_files(
                                session, owner, repo, item["path"], headers
                            )
                            swift_files.extend(subdir_files)
        
        except Exception as e:
            logger.error(f"Error getting repo files: {e}")
        
        return swift_files
    
    async def _get_directory_files(self, session, owner: str, repo: str, path: str, headers: dict) -> List[Dict]:
        """Recursively get Swift files from a directory"""
        swift_files = []
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    contents = await resp.json()
                    
                    for item in contents:
                        if item["type"] == "file" and item["name"].endswith(".swift"):
                            file_content = await self._get_file_content(session, item["download_url"])
                            if file_content:
                                swift_files.append({
                                    "path": item["path"],
                                    "content": file_content,
                                    "url": item["html_url"]
                                })
        except:
            pass
        
        return swift_files
    
    async def _get_file_content(self, session, url: str) -> Optional[str]:
        """Get content of a file"""
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.text()
        except:
            pass
        return None
    
    def _process_swift_files(self, swift_files: List[Dict], repo_info: Dict):
        """Process and categorize Swift files"""
        repo_name = repo_info["name"]
        repo_desc = repo_info.get("description", "")
        
        for file in swift_files:
            content = file["content"]
            path = file["path"]
            
            # Categorize file
            category = self._categorize_swift_file(path, content)
            
            # Create training example
            training_example = {
                "repo": repo_name,
                "description": repo_desc,
                "file_path": path,
                "content": content,
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to appropriate category
            self._save_training_example(training_example, category)
    
    def _categorize_swift_file(self, path: str, content: str) -> str:
        """Categorize Swift file based on content and path"""
        path_lower = path.lower()
        
        # Check path patterns
        if "view" in path_lower and "model" not in path_lower:
            if "@main" in content or "App:" in content:
                return "swiftui_apps"
            return "view_components"
        elif "viewmodel" in path_lower or "vm" in path_lower:
            return "viewmodels"
        elif "model" in path_lower:
            return "models"
        elif "network" in path_lower or "api" in path_lower or "service" in path_lower:
            return "networking"
        elif "animation" in path_lower or ".animation" in content:
            return "animations"
        elif "navigation" in path_lower or "NavigationStack" in content:
            return "navigation"
        
        # Check content patterns
        if "struct.*: View" in content or "class.*: View" in content:
            return "view_components"
        elif "ObservableObject" in content or "@Published" in content:
            return "viewmodels"
        elif "URLSession" in content or "async.*throws" in content:
            return "networking"
        
        return "utilities"
    
    def _save_training_example(self, example: Dict, category: str):
        """Save training example to file"""
        # Create category directory
        category_dir = self.output_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        content_hash = hashlib.md5(example["content"].encode()).hexdigest()[:8]
        filename = f"{example['repo']}_{content_hash}.json"
        
        # Save example
        with open(category_dir / filename, 'w') as f:
            json.dump(example, f, indent=2)
    
    async def scrape_apple_documentation(self):
        """Scrape code examples from Apple documentation"""
        # Apple Developer Forums and Documentation
        # This would require more complex scraping with proper authorization
        logger.info("Apple documentation scraping requires manual curation")
        
        # Instead, we'll create a curated list of Apple's SwiftUI examples
        apple_examples = [
            {
                "name": "Landmarks",
                "description": "Apple's tutorial app for SwiftUI",
                "url": "https://developer.apple.com/tutorials/swiftui"
            },
            {
                "name": "Fruta",
                "description": "Apple's sample smoothie app",
                "url": "https://developer.apple.com/documentation/swiftui/fruta_building_a_feature-rich_app_with_swiftui"
            }
        ]
        
        # Save curated list for manual download
        with open(self.output_dir / "apple_examples.json", 'w') as f:
            json.dump(apple_examples, f, indent=2)
    
    def create_training_dataset(self):
        """Create formatted training dataset from scraped code"""
        training_data = []
        
        # Process each category
        for category in self.categories:
            category_dir = self.output_dir / category
            if category_dir.exists():
                for file_path in category_dir.glob("*.json"):
                    with open(file_path, 'r') as f:
                        example = json.load(f)
                        
                        # Create prompt-completion pairs
                        if category == "swiftui_apps":
                            # Full app generation
                            prompt = f"Create a SwiftUI app: {example['description']}"
                            completion = example['content']
                        elif category == "view_components":
                            # Component generation
                            view_name = self._extract_view_name(example['content'])
                            prompt = f"Create a SwiftUI view component: {view_name}"
                            completion = example['content']
                        else:
                            # Other categories
                            prompt = f"Create Swift code for {category}: {example['file_path']}"
                            completion = example['content']
                        
                        training_data.append({
                            "prompt": prompt,
                            "completion": completion,
                            "category": category
                        })
        
        # Save training dataset
        with open(self.output_dir / "training_dataset.jsonl", 'w') as f:
            for item in training_data:
                f.write(json.dumps(item) + '\n')
        
        logger.info(f"Created training dataset with {len(training_data)} examples")
        return training_data
    
    def _extract_view_name(self, content: str) -> str:
        """Extract view name from Swift content"""
        match = re.search(r'struct\s+(\w+)\s*:\s*View', content)
        if match:
            return match.group(1)
        return "CustomView"

async def main():
    """Run the scraper"""
    scraper = SwiftCodeScraper()
    
    # Scrape different types of Swift apps
    queries = [
        "SwiftUI app",
        "iOS app Swift",
        "SwiftUI tutorial",
        "Swift MVP architecture",
        "SwiftUI MVVM",
        "Swift Combine",
        "SwiftUI animation",
        "Swift async await"
    ]
    
    for query in queries:
        logger.info(f"Scraping for: {query}")
        await scraper.scrape_github_repos(query, max_repos=50)
        await asyncio.sleep(5)  # Be respectful of rate limits
    
    # Create training dataset
    scraper.create_training_dataset()

if __name__ == "__main__":
    asyncio.run(main())