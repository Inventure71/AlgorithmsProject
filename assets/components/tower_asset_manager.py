import os
import pygame
from typing import Dict, Optional, Tuple
from assets.cache_manager import CacheManager

class TowerAssetManager(CacheManager):
    """
    Manages tower-specific assets: buildings, characters, and destroyed states
    Uses hash table caching for O(1) lookups
    """
    
    # scaling multipliers for tower images
    PRINCESS_TOWER_SCALE = 3.0
    KING_TOWER_SCALE = 2.5
    
    def __init__(self, assets_path: str):
        super().__init__()
        self.assets_path = assets_path
        self._scaled_cache: Dict[Tuple[int, int, int, str, float], pygame.Surface] = {}
    
    def get_tower_assets(self, tower_type: int, team: int, is_alive: bool = True) -> Dict[str, Optional[pygame.Surface]]:
        """
        Load complete tower asset set

        Args:
            tower_type: -1 (left princess), 0 (king), 1 (right princess)
            team: 1 or 2
            is_alive: True for active, False for destroyed

        Returns:
            Dict with 'building', 'character', 'destroyed' keys

        - Time: Worst case O(w*h), Average case O(1) cached, O(w*h) on first load per asset
        - Space: O(assets * w * h) for tower surfaces
        """
        cache_key = (tower_type, team, is_alive)
        
        if self.has_cached(cache_key):
            return self.get_cached(cache_key)
        
        assets = self._load_tower_assets(tower_type, team, is_alive)
        self.set_cached(cache_key, assets)
        return assets
    
    def get_scaled_tower_sprite(self, tower_sprite: pygame.Surface, target_width: int,
                                target_height: int, tower_type: int, layer: str = "building") -> pygame.Surface:
        """
        Scale a tower sprite proportionally to fit within target dimensions.
        Maintains aspect ratio.

        Args:
            tower_sprite: The original sprite surface
            target_width: Target width in pixels (tower's grid width)
            target_height: Target height in pixels (tower's grid height)
            tower_type: -1 or 1 for princess, 0 for king
            layer: Identifier for caching ('building', 'character', 'destroyed')

        Returns:
            Scaled sprite that fits within target dimensions while maintaining aspect ratio

        - Time: Worst case O(w*h), Average case O(1) cached, O(w*h) on first scale
        - Space: O(w*h) per scaled variant
        """
        # get original sprite dimensions
        original_width, original_height = tower_sprite.get_size()
        
        # calculate scale to fit within target dimensions while maintaining aspect ratio
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = min(scale_x, scale_y)  # we use smaller scale to maintain aspect ratio
        
        # calculate final scaled dimensions
        scaled_width = int(original_width * scale)
        scaled_height = int(original_height * scale)
        
        cache_key = (id(tower_sprite), scaled_width, scaled_height, layer)
        
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        scaled_sprite = pygame.transform.scale(tower_sprite, (scaled_width, scaled_height))
        self._scaled_cache[cache_key] = scaled_sprite
        return scaled_sprite
        
    def _load_tower_assets(self, tower_type: int, team: int, is_alive: bool) -> Dict[str, Optional[pygame.Surface]]:
        """
        Internal method to load tower assets from disk.

        - Time: Worst case = Average case = O(w*h) where w/h are the width and height of the tower sprite
        - Space: O(w*h) per loaded surface
        """
        result = {'building': None, 'character': None, 'destroyed': None}
        
        if not is_alive:
            result['destroyed'] = self._load_destroyed_tower(tower_type)
        else:
            tower_folder = "king_tower" if tower_type == 0 else "princess_tower"
            tower_path = os.path.join(self.assets_path, "tower", f"Team{team}", tower_folder)
            
            if os.path.exists(tower_path):
                sprite_files = sorted([f for f in os.listdir(tower_path) if f.endswith('.png')])
                
                if tower_type == 0 and len(sprite_files) >= 2:
                    # King tower: building + character
                    result['building'] = self._load_image(os.path.join(tower_path, sprite_files[0]))
                    result['character'] = self._load_image(os.path.join(tower_path, sprite_files[1]))
                elif len(sprite_files) >= 1:
                    # Princess tower: building only
                    result['building'] = self._load_image(os.path.join(tower_path, sprite_files[0]))
        
        return result
    
    def _load_destroyed_tower(self, tower_type: int) -> Optional[pygame.Surface]:
        """
        Load destroyed tower sprite (team-agnostic).

        - Time: Worst case = Average case = O(w*h) where w/h are the width and height of the tower sprite
        - Space: O(w*h) for surface
        """
        destroyed_name = "destroyed_king.png" if tower_type == 0 else "destroyed_princess.png"
        destroyed_path = os.path.join(self.assets_path, "tower", "any", destroyed_name)
        return self._load_image(destroyed_path)
    
    def _load_image(self, path: str) -> Optional[pygame.Surface]:
        """
        Helper to load a single image

        - Time: Worst case = Average case = O(w*h) where w/h are the width and height of the tower sprite
        - Space: O(w*h) for surface
        """
        if not os.path.exists(path):
            return None
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """
        Clear all caches

        - Time: Worst case = Average case = O(n) where n is cached items
        - Space: O(1)
        """
        super().clear_cache()
        self._scaled_cache.clear()