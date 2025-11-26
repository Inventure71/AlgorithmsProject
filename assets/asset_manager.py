import os
from typing import Dict, Optional, Tuple, List

import pygame
from assets.components.sprite_manager import SpriteManager
from assets.components.tower_asset_manager import TowerAssetManager
from assets.components.ui_asset_manager import UIAssetManager
from assets.components.text_renderer import TextRenderer

class AssetManager:
    """
    Facade for all asset management.
    Delegates to specialized managers following Single Responsibility Principle.
    """
    
    def __init__(self, assets_base_path: str = "assets"):
        self.assets_base_path = assets_base_path
        usable_assets_path = os.path.join(assets_base_path, "usable_assets")
        
        # Initialize specialized managers
        self.sprites = SpriteManager(usable_assets_path)
        self.towers = TowerAssetManager(usable_assets_path)
        self.ui = UIAssetManager(usable_assets_path)
        self.text = TextRenderer()
    
    
    # these delegate to the appropriate specialized manager
    def get_troop_sprite(self, troop_name: str, team: int, sprite_number: int = 1):
        """Get troop sprite (delegates to SpriteManager)."""
        return self.sprites.get_sprite(troop_name, team, sprite_number)
    
    def get_scaled_sprite(self, sprite, sprite_number, width: int, height: int):
        """Scale sprite (delegates to SpriteManager)."""
        return self.sprites.get_scaled_sprite(sprite, sprite_number, width, height)
    
    def get_tower_assets(self, tower_type: int, team: int, is_alive: bool = True):
        """Get tower assets (delegates to TowerAssetManager)."""
        return self.towers.get_tower_assets(tower_type, team, is_alive)
    
    def get_scaled_tower_sprite(self, sprite, width: int, height: int, tower_type: int, layer: str = "building"):
        """Scale tower sprite (delegates to TowerAssetManager)."""
        return self.towers.get_scaled_tower_sprite(sprite, width, height, tower_type, layer)
    
    def get_crown_image(self, crown_team: str, size: int):
        """Get card image (delegates to UIAssetManager)."""
        return self.ui.get_crown_image(crown_team, size)

    def get_winner_screen(self, width: int, height: int):
        """Get winner screen (delegates to UIAssetManager)."""
        return self.ui.get_winner_screen(width, height)

    def get_card_image(self, troop_name: str):
        """Get card image (delegates to UIAssetManager)."""
        return self.ui.get_card_image(troop_name)
    
    def get_scaled_card_image(self, troop_name: str, width: int, height: int):
        """Get scaled card (delegates to UIAssetManager)."""
        return self.ui.get_scaled_card(troop_name, width, height)
    
    def get_arena_background(self, width: int, height: int):
        """Get arena background (delegates to UIAssetManager)."""
        return self.ui.get_arena_background(width, height)
    
    def get_elixir_icon(self, size: int = 20):
        """Get elixir icon (delegates to UIAssetManager)."""
        return self.ui.get_elixir_icon(size)

    def get_card_overlay(self, width: int, height: int, 
                        color: Tuple[int, int, int, int] = (128, 128, 128, 128)) -> pygame.Surface:
        """Get cached card overlay surface (delegates to UIAssetManager)."""
        return self.ui.get_card_overlay(width, height, color)
    
    def get_elixir_segment_positions(self, bar_width: int, max_elixir: int) -> List[Tuple[int, int]]:
        """Get cached elixir bar segment positions (delegates to UIAssetManager)."""
        return self.ui.get_elixir_segment_positions(bar_width, max_elixir)
    
    def get_font(self, size: int = 24):
        """Get font (delegates to TextRenderer)."""
        return self.text.get_font(size)
    
    def get_text_surface(self, text: str, size: int = 24, color=(0, 0, 0)):
        """Render text (delegates to TextRenderer)."""
        return self.text.render_text(text, size, color)
    
    """MANAGEMENT METHODS"""
    def clear_cache(self, manager: Optional[str] = None):
        """
        Clear caches.
        Args:
            manager: specific manager ('sprites', 'towers', 'ui', 'text') or None for all
        """
        managers = {
            'sprites': self.sprites,
            'towers': self.towers,
            'ui': self.ui,
            'text': self.text
        }
        
        if manager and manager in managers:
            managers[manager].clear_cache()
        elif manager is None:
            for mgr in managers.values():
                mgr.clear_cache()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for all managers."""
        return {
            'sprites': self.sprites.cache_size(),
            'sprites_scaled': len(self.sprites._scaled_cache),
            'towers': self.towers.cache_size(),
            'towers_scaled': len(self.towers._scaled_cache),
            'ui': self.ui.cache_size(),
            'ui_scaled': len(self.ui._scaled_cache),
            'ui_overlays': len(self.ui._overlay_cache),
            'ui_segments': len(self.ui._segment_cache),
            'text': self.text.cache_size(),
            'fonts': len(self.text._font_cache)
        }