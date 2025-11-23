from typing import Dict, Any, Optional

class CacheManager:
    """Base class providing caching functionality for asset managers."""
    
    def __init__(self):
        self._cache: Dict[Any, Any] = {}
    
    def get_cached(self, key: Any) -> Optional[Any]:
        """Retrieve item from cache."""
        return self._cache.get(key)
    
    def set_cached(self, key: Any, value: Any) -> None:
        """Store item in cache."""
        self._cache[key] = value
    
    def has_cached(self, key: Any) -> bool:
        """Check if item exists in cache."""
        return key in self._cache
    
    def clear_cache(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
    
    def cache_size(self) -> int:
        """Return number of cached items."""
        return len(self._cache)