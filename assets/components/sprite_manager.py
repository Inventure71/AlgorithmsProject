import os
import pygame
from typing import Tuple, Optional, Dict
from assets.cache_manager import CacheManager

class SpriteManager(CacheManager):
    """Manages troop sprites and their scaling."""

    STANDARD_SPRITE_SIZE = 256  # 256x256 pixels
    
    def __init__(self, assets_path: str):
        super().__init__()
        self.assets_path = assets_path
        self._scaled_cache: Dict[Tuple[int, int, int, int], pygame.Surface] = {}
        self._standardized_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
        
        # troop name to folder mapping
        self.troop_folder_map = {
            "barbarian": "barbarian",
            "archer": "archer",
            "giant": "giant",
            "goblins": "goblins",
            "dart goblin": "dart_goblin",
            "elite barbs": "elite_barbs",
            "knight": "knight",
            "mini pekka": "mini_pekka",
            "musketeer": "musketeer",
            "pekka": "pekka",
            "royal giant": "royal_giant",
            "skeletons": "skeletons",
            "spear goblin": "spear_goblin",
            "bats": "bats",
        }
    
    def get_sprite(self, troop_name: str, team: int, sprite_number: int) -> pygame.Surface:
        """
        load a troop sprite for a specific team and sprite variant, standardized to STANDARD_SPRITE_SIZE.
        
        Args:
            troop_name: Name of the troop
            team: Team number (1 or 2)
            sprite_number: Which sprite to load (1, 2, or 3 for walking1, walking2, attack)
        """
        cache_key = (troop_name, team, sprite_number)
        
        if self.has_cached(cache_key):
            return self.get_cached(cache_key)
        
        sprite = self._load_sprite(troop_name, team, sprite_number)
        standardized_sprite = self._standardize_sprite(sprite, troop_name, team, sprite_number)
        self.set_cached(cache_key, standardized_sprite)
        return standardized_sprite

    def _standardize_sprite(self, sprite: pygame.Surface, troop_name: str, team: int, sprite_number: int) -> pygame.Surface:
        """Standardize a sprite to STANDARD_SPRITE_SIZE while preserving aspect ratio."""
        cache_key = (troop_name, team, sprite_number)
        
        if cache_key in self._standardized_cache:
            return self._standardized_cache[cache_key]
        
        original_width, original_height = sprite.get_size()
        standard_size = self.STANDARD_SPRITE_SIZE
        
        # if already standard size, return as-is
        if original_width == standard_size and original_height == standard_size:
            self._standardized_cache[cache_key] = sprite
            return sprite
        
        # Calculate scale to fit within standard size while preserving aspect ratio
        scale = min(standard_size / original_width, standard_size / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # scale the sprite
        scaled_sprite = pygame.transform.smoothscale(sprite, (new_width, new_height))
        
        # create a standard-sized surface with transparent background
        standardized_sprite = pygame.Surface((standard_size, standard_size), pygame.SRCALPHA)
        
        # center the scaled sprite on the standard-sized surface
        offset_x = (standard_size - new_width) // 2
        offset_y = (standard_size - new_height) // 2
        standardized_sprite.blit(scaled_sprite, (offset_x, offset_y))
        
        self._standardized_cache[cache_key] = standardized_sprite
        return standardized_sprite
    
    def get_scaled_sprite(self, sprite: pygame.Surface, sprite_number: int, width: int, height: int) -> pygame.Surface:
        """Get a scaled version of a sprite with uniform scaling to fill the entire area."""
        # scale uniformly to exact target dimensions (no aspect ratio preservation)
        # this ensures all troops fill their designated area consistently
        cache_key = (id(sprite), sprite_number, width, height)
        
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        # scale to exact dimensions for uniform filling
        scaled_sprite = pygame.transform.scale(sprite, (width, height))
        self._scaled_cache[cache_key] = scaled_sprite
        return scaled_sprite

    def _load_sprite(self, troop_name: str, team: int, sprite_number: int) -> pygame.Surface:
        """Internal method to load sprite from disk."""
        troop_folder = self.troop_folder_map.get(troop_name.lower())
        if not troop_folder:
            return self._create_fallback_surface(self.STANDARD_SPRITE_SIZE, self.STANDARD_SPRITE_SIZE)
        
        sprite_path = os.path.join(self.assets_path, troop_folder, f"Team{team}")
        
        if not os.path.exists(sprite_path):
            return self._create_fallback_surface(self.STANDARD_SPRITE_SIZE, self.STANDARD_SPRITE_SIZE)
        
        sprite_files = sorted([f for f in os.listdir(sprite_path) if f.endswith('.png')]) #TODO: use a core sorting algorithm

        if not sprite_files:
            return self._create_fallback_surface(self.STANDARD_SPRITE_SIZE, self.STANDARD_SPRITE_SIZE)
        
        # sprite_index = sprite_number 
        if len(sprite_files) > sprite_number:
            sprite_index = sprite_number
        else:
            sprite_index = 0 # fallback to first sprite
            print(f"Sprite number {sprite_number} not found, falling back to first sprite for troop {troop_name}")

        try:
            sprite_file = os.path.join(sprite_path, sprite_files[sprite_index])
            return pygame.image.load(sprite_file).convert_alpha()
        except Exception as e:
            print(f"Error loading sprite: {e}")
            return self._create_fallback_surface(self.STANDARD_SPRITE_SIZE, self.STANDARD_SPRITE_SIZE)
    
    
    def _create_fallback_surface(self, width: int, height: int) -> pygame.Surface:
        """Create a fallback colored surface."""
        surface = pygame.Surface((width, height))
        surface.fill((128, 128, 128))
        return surface
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        super().clear_cache()
        self._scaled_cache.clear()
        self._standardized_cache.clear()