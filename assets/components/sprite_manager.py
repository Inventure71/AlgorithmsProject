import os
import pygame
from typing import Tuple, Optional, Dict
from assets.cache_manager import CacheManager

class SpriteManager(CacheManager):
    """Manages troop sprites and their scaling."""
    
    def __init__(self, assets_path: str):
        super().__init__()
        self.assets_path = assets_path
        self._scaled_cache: Dict[Tuple[int, int, int], pygame.Surface] = {}
        
        # troop name to folder mapping
        self.troop_folder_map = {
            "barbarian": "barbarian",
            "archer": "archer"
        }
    
    def get_sprite(self, troop_name: str, team: int) -> pygame.Surface:
        """Load a troop sprite for a specific team."""
        cache_key = (troop_name, team)
        
        if self.has_cached(cache_key):
            return self.get_cached(cache_key)
        
        sprite = self._load_sprite(troop_name, team)
        self.set_cached(cache_key, sprite)
        return sprite
    
    def get_scaled_sprite(self, sprite: pygame.Surface, width: int, height: int) -> pygame.Surface:
        """Get a scaled version of a sprite with uniform scaling to fill the entire area."""
        # scale uniformly to exact target dimensions (no aspect ratio preservation)
        # this ensures all troops fill their designated area consistently
        cache_key = (id(sprite), width, height)
        
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        # scale to exact dimensions for uniform filling
        scaled_sprite = pygame.transform.scale(sprite, (width, height))
        self._scaled_cache[cache_key] = scaled_sprite
        return scaled_sprite

    def _load_sprite(self, troop_name: str, team: int) -> pygame.Surface:
        """Internal method to load sprite from disk."""
        troop_folder = self.troop_folder_map.get(troop_name.lower())
        if not troop_folder:
            return self._create_fallback_surface(32, 32)
        
        sprite_path = os.path.join(self.assets_path, troop_folder, f"Team {team}")
        
        if not os.path.exists(sprite_path):
            return self._create_fallback_surface(32, 32)
        
        sprite_files = sorted([f for f in os.listdir(sprite_path) if f.endswith('.png')])
        if not sprite_files:
            return self._create_fallback_surface(32, 32)
        
        try:
            sprite_file = os.path.join(sprite_path, sprite_files[0])
            return pygame.image.load(sprite_file).convert_alpha()
        except Exception as e:
            print(f"Error loading sprite: {e}")
            return self._create_fallback_surface(32, 32)
    
    def _create_fallback_surface(self, width: int, height: int) -> pygame.Surface:
        """Create a fallback colored surface."""
        surface = pygame.Surface((width, height))
        surface.fill((128, 128, 128))
        return surface
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        super().clear_cache()
        self._scaled_cache.clear()