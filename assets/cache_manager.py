from typing import Dict, Any, Optional

class CacheManager:
    """
    Base class providing caching functionality for asset managers
    Uses a hash table (dictionary) for O(1) average access
    """
    
    def __init__(self):
        self._cache: Dict[Any, Any] = {}

    def get_cached(self, key: Any) -> Optional[Any]:
        """
        Retrieve item from cache

        - Time: Worst case = Average case = O(1) because it's a hash table lookup
        - Space: O(1)
        """
        return self._cache.get(key)
    
    def set_cached(self, key: Any, value: Any) -> None:
        """
        Store item in cache

        - Time: Worst case = Average case = O(1) because it's a hash table insertion
        - Space: O(1) per item
        """
        self._cache[key] = value
    
    def has_cached(self, key: Any) -> bool:
        """
        Check if item exists in cache

        - Time: Worst case = Average case = O(1) because it's a hash table lookup
        - Space: O(1)
        """
        return key in self._cache
    
    def clear_cache(self) -> None:
        """
        Clear all cached items

        - Time: Worst case = Average case = O(n) where n is the number of cached items
        - Space: O(1)
        """
        self._cache.clear()
    
    def cache_size(self) -> int:
        """
        Return number of cached items

        - Time: Worst case = Average case = O(1)
        - Space: O(1)
        """
        return len(self._cache)