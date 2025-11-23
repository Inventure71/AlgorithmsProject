# assets/asset_manager.py
import os
import pygame
from typing import Dict, Optional, Tuple

class AssetManager:
    """
    Centralized asset management with caching.
    Handles sprites, card images, fonts, and text surfaces.
    """
    
    def __init__(self, assets_base_path: str = "assets"):
        self.assets_base_path = assets_base_path
        self.usable_assets_path = os.path.join(assets_base_path, "usable_assets")
        
        # Caches
        self._sprite_cache: Dict[Tuple[str, int], pygame.Surface] = {}
        self._scaled_sprite_cache: Dict[Tuple[int, int, int], pygame.Surface] = {}
        self._card_image_cache: Dict[str, pygame.Surface] = {}
        self._scaled_card_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
        self._font_cache: Optional[pygame.font.Font] = None
        self._text_surface_cache: Dict[Tuple[str, int, Tuple[int, int, int]], pygame.Surface] = {}
        
        # Troop name to folder mapping (case-sensitive)
        self.troop_folder_map = {
            "barbarian": "barbarian",
            "archer": "Archer"
        }
    
    def get_arena_background(self, width: int, height: int) -> Optional[pygame.Surface]:
        """
        Load and scale the arena background image to fit the specified dimensions.
        Returns None if background image doesn't exist.
        """
        cache_key = ("arena_background", width, height)
        if cache_key in self._scaled_card_cache:  # Reuse card cache for arena background
            return self._scaled_card_cache[cache_key]
        
        # Build path to arena background
        background_path = os.path.join(self.usable_assets_path, "arena", "background.png")
        
        if not os.path.exists(background_path):
            return None
        
        try:
            background_image = pygame.image.load(background_path).convert()
            # Scale to fit the arena dimensions exactly
            scaled_background = pygame.transform.scale(background_image, (width, height))
            self._scaled_card_cache[cache_key] = scaled_background
            return scaled_background
        except Exception as e:
            print(f"Error loading arena background {background_path}: {e}")
            return None

    def get_elixir_icon(self, size: int = 20) -> Optional[pygame.Surface]:
        """
        Load the elixir icon, scaled to specified size.
        Returns None if icon doesn't exist.
        """
        cache_key = ("elixir_icon", size)
        if cache_key in self._scaled_card_cache:  # Reuse card cache for UI icons
            return self._scaled_card_cache[cache_key]
        
        # Build path to elixir icon
        elixir_path = os.path.join(self.usable_assets_path, "UI", "ElixirIcon.png")
        
        if not os.path.exists(elixir_path):
            return None
        
        try:
            elixir_icon = pygame.image.load(elixir_path).convert_alpha()
            # Scale to square size (size x size)
            scaled_icon = pygame.transform.scale(elixir_icon, (size, size))
            self._scaled_card_cache[cache_key] = scaled_icon
            return scaled_icon
        except Exception as e:
            print(f"Error loading elixir icon {elixir_path}: {e}")
            return None
    
    def get_troop_sprite(self, troop_name: str, team: int) -> pygame.Surface:
        """
        Load a troop sprite for a specific team.
        Returns cached sprite if available, otherwise loads and caches it.
        """
        cache_key = (troop_name, team)
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        
        # Map troop name to folder
        troop_folder = self.troop_folder_map.get(troop_name)
        if not troop_folder:
            # Fallback: create colored surface
            surface = pygame.Surface((32, 32))
            surface.fill((128, 128, 128))
            self._sprite_cache[cache_key] = surface
            return surface
        
        # Build path to sprite directory
        team_folder = f"Team {team}"
        sprite_path = os.path.join(self.usable_assets_path, troop_folder, team_folder)
        
        if not os.path.exists(sprite_path):
            # Fallback: create colored surface
            surface = pygame.Surface((32, 32))
            surface.fill((128, 128, 128))
            self._sprite_cache[cache_key] = surface
            return surface
        
        # Get first PNG file in the directory
        sprite_files = [f for f in os.listdir(sprite_path) if f.endswith('.png')]
        if not sprite_files:
            # Fallback: create colored surface
            surface = pygame.Surface((32, 32))
            surface.fill((128, 128, 128))
            self._sprite_cache[cache_key] = surface
            return surface
        
        # Load the first sprite
        sprite_file = os.path.join(sprite_path, sorted(sprite_files)[0])
        try:
            sprite = pygame.image.load(sprite_file).convert_alpha()
            self._sprite_cache[cache_key] = sprite
            return sprite
        except Exception as e:
            print(f"Error loading sprite {sprite_file}: {e}")
            # Fallback: create colored surface
            surface = pygame.Surface((32, 32))
            surface.fill((128, 128, 128))
            self._sprite_cache[cache_key] = surface
            return surface
    
    def get_scaled_sprite(self, sprite: pygame.Surface, visual_width: int, visual_height: int) -> pygame.Surface:
        """
        Get a scaled version of a sprite, using cache to avoid repeated scaling.
        """
        sprite_width, sprite_height = sprite.get_size()
        scale_x = visual_width / sprite_width
        scale_y = visual_height / sprite_height
        scale = min(scale_x, scale_y)  # Use smaller scale to fit within bounds
        
        scaled_width = int(sprite_width * scale)
        scaled_height = int(sprite_height * scale)
        
        # Create cache key using sprite id and target size
        cache_key = (id(sprite), scaled_width, scaled_height)
        
        if cache_key in self._scaled_sprite_cache:
            return self._scaled_sprite_cache[cache_key]
        
        # Scale and cache
        scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
        self._scaled_sprite_cache[cache_key] = scaled_sprite
        return scaled_sprite
    
    def get_card_image(self, troop_name: str) -> Optional[pygame.Surface]:
        """
        Load a card image for a troop type.
        Returns None if card image doesn't exist.
        """
        if troop_name in self._card_image_cache:
            return self._card_image_cache[troop_name]
        
        # Map troop name to folder
        troop_folder = self.troop_folder_map.get(troop_name)
        if not troop_folder:
            return None
        
        # Build path to card image
        card_path = os.path.join(self.usable_assets_path, troop_folder, "Card.png")
        
        if not os.path.exists(card_path):
            return None
        
        try:
            card_image = pygame.image.load(card_path).convert_alpha()
            self._card_image_cache[troop_name] = card_image
            return card_image
        except Exception as e:
            print(f"Error loading card image {card_path}: {e}")
            return None
    
    def get_scaled_card_image(self, troop_name: str, width: int, height: int) -> Optional[pygame.Surface]:
        """
        Get a scaled version of a card image.
        """
        card_image = self.get_card_image(troop_name)
        if card_image is None:
            return None
        
        cache_key = (troop_name, width, height)
        if cache_key in self._scaled_card_cache:
            return self._scaled_card_cache[cache_key]
        
        scaled_card = pygame.transform.scale(card_image, (width, height))
        self._scaled_card_cache[cache_key] = scaled_card
        return scaled_card
    
    def get_font(self, size: int = 24) -> pygame.font.Font:
        """
        Get or create a font object (cached).
        """
        if self._font_cache is None or self._font_cache.get_height() != size:
            self._font_cache = pygame.font.Font(None, size)
        return self._font_cache
    
    def get_text_surface(self, text: str, size: int = 24, color: Tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
        """
        Get a rendered text surface (cached).
        """
        cache_key = (text, size, color)
        if cache_key in self._text_surface_cache:
            return self._text_surface_cache[cache_key]
        
        font = self.get_font(size)
        surface = font.render(text, True, color)
        self._text_surface_cache[cache_key] = surface
        return surface
    
    def clear_cache(self):
        """Clear all caches (useful for memory management or testing)."""
        self._sprite_cache.clear()
        self._scaled_sprite_cache.clear()
        self._card_image_cache.clear()
        self._scaled_card_cache.clear()
        self._text_surface_cache.clear()
        self._font_cache = None