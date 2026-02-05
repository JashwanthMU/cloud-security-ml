"""
Simple caching for LLM responses
Reduces API costs and improves speed
"""

import hashlib
import json
import os
from datetime import datetime, timedelta

class SimpleCache:
    """In-memory cache with file persistence"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        self.cache = {}
        self.max_age_hours = 24
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing cache
        self._load_cache()
    
    def get(self, key):
        """Get cached value if exists and not expired"""
        
        cache_key = self._hash_key(key)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # Check expiration
            created = datetime.fromisoformat(entry['created'])
            age = datetime.now() - created
            
            if age < timedelta(hours=self.max_age_hours):
                return entry['value']
            else:
                # Expired, remove
                del self.cache[cache_key]
        
        return None
    
    def set(self, key, value):
        """Store value in cache"""
        
        cache_key = self._hash_key(key)
        
        self.cache[cache_key] = {
            'value': value,
            'created': datetime.now().isoformat()
        }
        
        # Persist to disk
        self._save_cache()
    
    def _hash_key(self, key):
        """Generate hash for cache key"""
        return hashlib.md5(str(key).encode()).hexdigest()
    
    def _load_cache(self):
        """Load cache from disk"""
        
        cache_file = os.path.join(self.cache_dir, 'llm_cache.json')
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        
        cache_file = os.path.join(self.cache_dir, 'llm_cache.json')
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
        self._save_cache()
    
    def stats(self):
        """Get cache statistics"""
        
        total = len(self.cache)
        
        # Count expired
        expired = 0
        for entry in self.cache.values():
            created = datetime.fromisoformat(entry['created'])
            age = datetime.now() - created
            if age >= timedelta(hours=self.max_age_hours):
                expired += 1
        
        return {
            'total_entries': total,
            'valid_entries': total - expired,
            'expired_entries': expired,
            'cache_dir': self.cache_dir
        }

# Global cache instance
llm_cache = SimpleCache()