import pygame
from typing import Tuple, Dict
from assets.cache_manager import CacheManager

class TextRenderer(CacheManager):
    """
    Manages fonts and rendered text surfaces
    Caches rendered text to avoid repeated rendering
    """
    
    def __init__(self):
        super().__init__()
        self._font_cache: Dict[int, pygame.font.Font] = {}

    def get_font(self, size: int = 24) -> pygame.font.Font:
        """
        Get or create a font at specified size
        
        - Time: Worst case = Average case = O(1) cached and O(1) on first load because font creation is constant
        - Space: O(1) per font size
        """
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.Font(None, size)
        return self._font_cache[size]
    
    def render_text(self, text: str, size: int = 24,
                    color: Tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
        """
        Render text surface (cached)

        - Time: Worst case O(len(text)), Average case O(1) cached, O(len(text)) on first render
        - Space: O(len(text) * font_height) per unique text surface
        """
        cache_key = (text, size, color)
        
        if self.has_cached(cache_key):
            return self.get_cached(cache_key)
        
        font = self.get_font(size)
        surface = font.render(text, True, color)
        self.set_cached(cache_key, surface)
        return surface
    
    def clear_cache(self) -> None:
        """
        Clear all caches

        - Time: Worst case = Average case = O(n) where n is cached items
        - Space: O(1)
        """
        super().clear_cache()
        self._font_cache.clear()