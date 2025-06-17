"""
RAG Cache Manager for Performance Optimization
Provides caching layer for frequently accessed RAG queries
"""

import time
import hashlib
from typing import Dict, List, Optional, Any
from collections import OrderedDict
import json
import os


class RAGCacheManager:
    """Manages caching for RAG knowledge base queries"""
    
    def __init__(self, max_cache_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache manager
        
        Args:
            max_cache_size: Maximum number of cached queries
            ttl_seconds: Time to live for cache entries (default 1 hour)
        """
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_seconds
        
        # LRU cache implementation using OrderedDict
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
        # Persistent cache file
        self.cache_file = os.path.join(
            os.path.dirname(__file__), 
            'swift_knowledge', 
            'rag_cache.json'
        )
        
        # Load persistent cache
        self._load_persistent_cache()
    
    def _load_persistent_cache(self):
        """Load cache from disk if available"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cached_data = json.load(f)
                    
                # Load into cache, checking TTL
                current_time = time.time()
                for key, entry in cached_data.items():
                    if current_time - entry['timestamp'] < self.ttl_seconds:
                        self.cache[key] = entry
                        
                print(f"[RAG Cache] Loaded {len(self.cache)} entries from persistent cache")
            except Exception as e:
                print(f"[RAG Cache] Error loading cache: {e}")
    
    def _save_persistent_cache(self):
        """Save cache to disk"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            # Convert to regular dict for JSON serialization
            cache_data = dict(self.cache)
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"[RAG Cache] Error saving cache: {e}")
    
    def _generate_cache_key(self, query: str, k: int) -> str:
        """Generate cache key from query and k value"""
        key_string = f"{query}:{k}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, query: str, k: int) -> Optional[List[Dict]]:
        """
        Get cached results for a query
        
        Returns:
            Cached results if available and not expired, None otherwise
        """
        key = self._generate_cache_key(query, k)
        
        if key in self.cache:
            entry = self.cache[key]
            current_time = time.time()
            
            # Check if entry is still valid
            if current_time - entry['timestamp'] < self.ttl_seconds:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.stats['hits'] += 1
                return entry['results']
            else:
                # Entry expired, remove it
                del self.cache[key]
        
        self.stats['misses'] += 1
        return None
    
    def put(self, query: str, k: int, results: List[Dict]):
        """
        Cache query results
        
        Args:
            query: The search query
            k: Number of results requested
            results: The search results to cache
        """
        key = self._generate_cache_key(query, k)
        
        # Create cache entry
        entry = {
            'query': query,
            'k': k,
            'results': results,
            'timestamp': time.time()
        }
        
        # Add to cache
        self.cache[key] = entry
        self.cache.move_to_end(key)
        
        # Evict oldest entries if cache is full
        while len(self.cache) > self.max_cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
        
        # Periodically save to disk (every 10 puts)
        if self.stats['hits'] + self.stats['misses'] % 10 == 0:
            self._save_persistent_cache()
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
        # Remove persistent cache
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_cache_size,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'hit_rate': f"{hit_rate:.2%}",
            'total_requests': total_requests
        }
    
    def warm_cache(self, common_queries: List[str]):
        """
        Pre-populate cache with common queries
        
        Args:
            common_queries: List of common query patterns to cache
        """
        # Common k values
        k_values = [3, 5]
        
        for query in common_queries:
            for k in k_values:
                # Check if already cached
                if self.get(query, k) is None:
                    # Mark for warming (actual warming done by RAG)
                    print(f"[RAG Cache] Marked for warming: '{query}' with k={k}")


# Common queries to warm cache with
COMMON_QUERIES = [
    # Error patterns
    "reserved type Task",
    "NavigationView deprecated",
    "missing import SwiftUI",
    "string literal error",
    "iOS version compatibility",
    
    # Architecture patterns
    "architecture MVVM",
    "architecture simple app",
    "architecture complex app",
    "SwiftUI best practices",
    
    # Common app types
    "todo app patterns",
    "timer app patterns",
    "photo app patterns",
    "game app patterns",
    
    # Solutions
    "fix reserved types",
    "fix missing imports",
    "fix iOS 17 features",
    "prevent build errors"
]