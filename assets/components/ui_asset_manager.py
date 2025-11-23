import os
import pygame
from typing import Optional, Tuple, Dict
from assets.cache_manager import CacheManager

class UIAssetManager(CacheManager):
    """Manages UI elements: cards, icons, and backgrounds."""
    
    def __init__(self, assets_path: str):
        super().__init__()
        self.assets_path = assets_path
        self._scaled_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
        
        self.troop_folder_map = {
            "barbarian": "barbarian",
            "archer": "archer"
        }
    
    def get_card_image(self, troop_name: str) -> Optional[pygame.Surface]:
        """Load a card image for a troop."""
        if self.has_cached(troop_name):
            return self.get_cached(troop_name)
        
        troop_folder = self.troop_folder_map.get(troop_name.lower())
        if not troop_folder:
            return None
        
        card_path = os.path.join(self.assets_path, troop_folder, "Card.png")
        card_image = self._load_image(card_path)
        
        if card_image:
            self.set_cached(troop_name, card_image)
        
        return card_image
    
    def get_scaled_card(self, troop_name: str, width: int, height: int) -> Optional[pygame.Surface]:
        """Get a scaled card image."""
        card_image = self.get_card_image(troop_name)
        if not card_image:
            return None
        
        cache_key = (troop_name, width, height)
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        scaled = pygame.transform.scale(card_image, (width, height))
        self._scaled_cache[cache_key] = scaled
        return scaled
    
    def get_arena_background(self, width: int, height: int) -> Optional[pygame.Surface]:
        """Load and scale arena background."""
        cache_key = ("arena_bg", width, height)
        
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        bg_path = os.path.join(self.assets_path, "arena", "background.png")
        background = self._load_image(bg_path, convert_alpha=False)
        
        if background:
            scaled = pygame.transform.scale(background, (width, height))
            self._scaled_cache[cache_key] = scaled
            return scaled
        
        return None
    
    def get_elixir_icon(self, size: int = 20) -> Optional[pygame.Surface]:
        """Load elixir icon at specified size."""
        cache_key = ("elixir", size, size)
        
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        icon_path = os.path.join(self.assets_path, "UI", "ElixirIcon.png")
        icon = self._load_image(icon_path)
        
        if icon:
            scaled = pygame.transform.scale(icon, (size, size))
            self._scaled_cache[cache_key] = scaled
            return scaled
        
        return None
    
    def _load_image(self, path: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """Helper to load a single image."""
        if not os.path.exists(path):
            return None
        try:
            img = pygame.image.load(path)
            return img.convert_alpha() if convert_alpha else img.convert()
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        super().clear_cache()
        self._scaled_cache.clear()