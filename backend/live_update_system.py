"""
Live Update System for SwiftGen AI
Monitors Apple announcements, iOS updates, and Swift language changes
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import feedparser
import re
from rag_knowledge_base import RAGKnowledgeBase


class LiveUpdateSystem:
    """System to keep SwiftGen AI updated with latest iOS/Swift developments"""
    
    def __init__(self, rag_kb: RAGKnowledgeBase):
        self.rag_kb = rag_kb
        self.update_cache_dir = "update_cache"
        os.makedirs(self.update_cache_dir, exist_ok=True)
        
        # Sources to monitor
        self.sources = {
            "apple_developer_news": "https://developer.apple.com/news/rss/news.rss",
            "swift_blog": "https://swift.org/blog/rss.xml",
            "apple_releases": "https://developer.apple.com/news/releases/rss/releases.rss",
            "wwdc_announcements": "https://developer.apple.com/wwdc/rss/wwdc.rss"
        }
        
        # GitHub repositories to monitor for updates
        self.monitored_repos = [
            "apple/swift",
            "apple/swift-evolution",
            "apple/swift-package-manager",
            "swiftlang/swift"
        ]
        
    async def start_monitoring(self):
        """Start the live monitoring system"""
        print("[LIVE UPDATE] Starting live monitoring system")
        
        # Check for updates every hour
        while True:
            try:
                await self._check_for_updates()
                await asyncio.sleep(3600)  # 1 hour
            except Exception as e:
                print(f"[LIVE UPDATE] Error in monitoring: {e}")
                await asyncio.sleep(300)  # 5 minutes on error
                
    async def _check_for_updates(self):
        """Check all sources for updates"""
        print("[LIVE UPDATE] Checking for updates...")
        
        # Check RSS feeds
        for source_name, rss_url in self.sources.items():
            try:
                await self._check_rss_feed(source_name, rss_url)
            except Exception as e:
                print(f"[LIVE UPDATE] Error checking {source_name}: {e}")
                
        # Check GitHub repositories
        for repo in self.monitored_repos:
            try:
                await self._check_github_releases(repo)
            except Exception as e:
                print(f"[LIVE UPDATE] Error checking {repo}: {e}")
                
    async def _check_rss_feed(self, source_name: str, rss_url: str):
        """Check RSS feed for new content"""
        cache_file = os.path.join(self.update_cache_dir, f"{source_name}_last_check.json")
        
        # Get last check time
        last_check = datetime.now() - timedelta(days=7)  # Default to 7 days ago
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                last_check = datetime.fromisoformat(cache_data.get("last_check", last_check.isoformat()))
        
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        
        new_items = []
        for entry in feed.entries:
            # Check if entry is newer than last check
            entry_date = datetime(*entry.published_parsed[:6])
            if entry_date > last_check:
                new_items.append(entry)
                
        if new_items:
            print(f"[LIVE UPDATE] Found {len(new_items)} new items from {source_name}")
            await self._process_new_items(source_name, new_items)
            
        # Update cache
        with open(cache_file, 'w') as f:
            json.dump({"last_check": datetime.now().isoformat()}, f)
            
    async def _process_new_items(self, source_name: str, items: List):
        """Process new items and update knowledge base"""
        for item in items:
            # Extract relevant information
            title = item.title
            content = item.get('summary', item.get('description', ''))
            link = item.link
            
            # Check if it's relevant to iOS/Swift development
            if self._is_ios_swift_relevant(title, content):
                # Create knowledge entry
                knowledge_entry = {
                    "title": f"Latest Update: {title}",
                    "content": f"{content}\n\nSource: {link}",
                    "tags": ["latest", "update", source_name, "ios", "swift"],
                    "severity": "important",
                    "solutions": [f"Stay updated with latest {source_name} announcements"],
                    "source": source_name,
                    "date": item.published,
                    "url": link
                }
                
                # Add to knowledge base
                filename = f"latest_{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                file_path = os.path.join(self.rag_kb.solutions_dir, filename)
                
                with open(file_path, 'w') as f:
                    json.dump(knowledge_entry, f, indent=2)
                    
                self.rag_kb._add_document(knowledge_entry, "solution", filename)
                print(f"[LIVE UPDATE] Added: {title}")
                
    def _is_ios_swift_relevant(self, title: str, content: str) -> bool:
        """Check if content is relevant to iOS/Swift development with enhanced filtering"""
        text = f"{title} {content}".lower()
        
        # High priority keywords - must have at least one
        high_priority_keywords = [
            "ios", "swift", "swiftui", "xcode", "app store", "iphone", "ipad",
            "watchos", "macos", "tvos", "objective-c", "cocoa", "uikit",
            "core data", "cloudkit", "wwdc", "beta", "api", "framework", "sdk"
        ]
        
        # Development-specific keywords - add relevance
        dev_keywords = [
            "deprecat", "new in", "bug fix", "security", "performance",
            "compatibility", "build", "compile", "syntax", "error",
            "crash", "memory", "thread", "async", "await", "combine"
        ]
        
        # Exclude irrelevant content
        exclude_keywords = [
            "marketing", "press release", "financial", "earnings", "stock",
            "acquisition", "legal", "lawsuit", "privacy policy update",
            "terms of service", "hiring", "job", "career", "office",
            "retail", "store opening", "executive", "ceo", "management"
        ]
        
        # Must have at least one high priority keyword
        has_high_priority = any(keyword in text for keyword in high_priority_keywords)
        if not has_high_priority:
            return False
            
        # Exclude if contains exclusion keywords
        has_exclusion = any(keyword in text for keyword in exclude_keywords)
        if has_exclusion:
            return False
            
        # Bonus points for development keywords
        has_dev_content = any(keyword in text for keyword in dev_keywords)
        
        # Additional filtering for SwiftUI/iOS app development specifically
        swiftui_specific = [
            "view", "modifier", "binding", "state", "observ", "navigation",
            "sheet", "alert", "picker", "list", "form", "button", "text",
            "image", "color", "font", "animation", "gesture", "accessibility"
        ]
        
        has_swiftui_content = any(keyword in text for keyword in swiftui_specific)
        
        # Must be relevant to iOS development
        return has_high_priority and (has_dev_content or has_swiftui_content or 
                                    "swift" in text or "ios" in text or "xcode" in text)
        
    async def _check_github_releases(self, repo: str):
        """Check GitHub repository for new releases"""
        async with aiohttp.ClientSession() as session:
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        release_data = await response.json()
                        
                        # Check if this is a new release
                        cache_file = os.path.join(self.update_cache_dir, f"{repo.replace('/', '_')}_release.json")
                        
                        is_new = True
                        if os.path.exists(cache_file):
                            with open(cache_file, 'r') as f:
                                cached_data = json.load(f)
                                if cached_data.get("tag_name") == release_data.get("tag_name"):
                                    is_new = False
                                    
                        if is_new:
                            await self._process_github_release(repo, release_data)
                            
                            # Update cache
                            with open(cache_file, 'w') as f:
                                json.dump(release_data, f, indent=2)
                                
            except Exception as e:
                print(f"[LIVE UPDATE] Error checking {repo} releases: {e}")
                
    async def _process_github_release(self, repo: str, release_data: Dict):
        """Process a new GitHub release"""
        title = f"{repo} - {release_data.get('name', release_data.get('tag_name'))}"
        content = release_data.get('body', '')
        
        # Create knowledge entry for the release
        knowledge_entry = {
            "title": f"New Release: {title}",
            "content": f"Release Notes:\n{content}\n\nDownload: {release_data.get('html_url')}",
            "tags": ["release", "github", repo.split('/')[1], "latest"],
            "severity": "normal",
            "solutions": [f"Consider updating to latest {repo} version"],
            "source": "github",
            "repo": repo,
            "version": release_data.get('tag_name'),
            "url": release_data.get('html_url')
        }
        
        # Add to knowledge base
        filename = f"release_{repo.replace('/', '_')}_{release_data.get('tag_name', 'latest')}.json"
        file_path = os.path.join(self.rag_kb.solutions_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(knowledge_entry, f, indent=2)
            
        self.rag_kb._add_document(knowledge_entry, "solution", filename)
        print(f"[LIVE UPDATE] Added release: {title}")
        
    async def get_latest_ios_updates(self) -> List[Dict]:
        """Get the latest iOS/Swift updates from knowledge base"""
        results = self.rag_kb.search("latest iOS Swift update", k=10)
        
        # Filter for recent updates (last 30 days)
        recent_updates = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for result in results:
            if result.get('date'):
                try:
                    update_date = datetime.fromisoformat(result['date'].replace('Z', '+00:00'))
                    if update_date > cutoff_date:
                        recent_updates.append(result)
                except:
                    continue
                    
        return recent_updates[:5]  # Return top 5 recent updates
        
    def force_update_check(self):
        """Force an immediate update check"""
        asyncio.create_task(self._check_for_updates())
        
    def get_update_summary(self) -> Dict:
        """Get a summary of the update system status"""
        cache_files = os.listdir(self.update_cache_dir) if os.path.exists(self.update_cache_dir) else []
        
        return {
            "sources_monitored": len(self.sources),
            "repos_monitored": len(self.monitored_repos),
            "cache_files": len(cache_files),
            "last_update_check": "Active monitoring",
            "status": "Running"
        }


# Integration with main system
async def start_live_updates(rag_kb: RAGKnowledgeBase):
    """Start the live update system"""
    update_system = LiveUpdateSystem(rag_kb)
    await update_system.start_monitoring()