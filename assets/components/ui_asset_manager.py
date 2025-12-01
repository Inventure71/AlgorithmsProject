import os
import pygame
from typing import Optional, Tuple, Dict, List
from assets.cache_manager import CacheManager

class UIAssetManager(CacheManager):
    """
    Manages UI elements: cards, icons, and backgrounds
    Uses multiple specialized caches for different asset types
    """
    
    def __init__(self, assets_path: str):
        super().__init__()
        self.assets_path = assets_path
        self._scaled_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
        self._overlay_cache: Dict[Tuple[int, int], pygame.Surface] = {}
        self._segment_cache: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        
        
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
            "wizard": "wizard",
            "baby dragon": "baby_dragon",
        }
    
    def get_card_image(self, troop_name: str) -> Optional[pygame.Surface]:
        """
        Load a card image for a troop
        
        - Time: Worst case O(w*h), Average case O(1) cached, O(w*h) on first load
        - Space: O(w*h) per card image
        """
        if self.has_cached(troop_name):
            return self.get_cached(troop_name)
        
        troop_folder = self.troop_folder_map.get(troop_name.lower())
        if not troop_folder:
            print(f"No troop folder found for {troop_name}")
            return None
        
        card_path = os.path.join(self.assets_path, troop_folder, "card.png")
        card_image = self._load_image(card_path)
        
        if card_image:
            self.set_cached(troop_name, card_image)
        
        return card_image
    
    def get_scaled_card(self, troop_name: str, width: int, height: int) -> Optional[pygame.Surface]:
        """
        Get a scaled card image

        - Time: Worst case O(w*h), Average case O(1) cached, O(w*h) on first scale
        - Space: O(w*h) per scaled variant

        Alternative: Could use recursion for scaling; runtime scaling handles UI size changes.
        """
        card_image = self.get_card_image(troop_name)
        if not card_image:
            return None
        
        cache_key = (troop_name, width, height)
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        scaled = pygame.transform.scale(card_image, (width, height))
        self._scaled_cache[cache_key] = scaled
        return scaled
    
    def get_menu_background(self, width: int, height: int) -> Optional[pygame.Surface]:
        """
        Load and scale arena menu background
        
        - Time: O(1) cached, O(w*h) on first load and scale
        - Space: O(w*h) for background surface
        """
        cache_key = ("menu_background", width, height)
        
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        bg_path = os.path.join(self.assets_path, "UI", "menu_background.png")
        background = self._load_image(bg_path, convert_alpha=False)
        
        if background:
            scaled = pygame.transform.scale(background, (width, height))
            self._scaled_cache[cache_key] = scaled
            return scaled
        
        return None
    
    def get_arena_background(self, width: int, height: int) -> Optional[pygame.Surface]:
        """
        Load and scale arena background
        
        - Time: O(1) cached, O(w*h) on first load and scale
        - Space: O(w*h) for background surface
        """
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
    
    def get_winner_screen(self, width: int, height: int) -> Optional[pygame.Surface]:
        """
        Load winner image
        
        - Time: O(1) cached, O(w*h) on first load and scale
        - Space: O(w*h) for surface
        """
        cache_key = ("winner_screen", width, height)

        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        winner_path = os.path.join(self.assets_path, "UI", "WinnerScreen.png")
        winner = self._load_image(winner_path)
        if winner:
            scaled = pygame.transform.scale(winner, (width, height))
            self._scaled_cache[cache_key] = scaled
            return scaled
        
        return None

    def get_crown_image(self, crown_team: int, size) -> Optional[pygame.Surface]:
        """
        Load crown image for a team
        
        - Time: O(1) cached, O(size^2) on first load and scale
        - Space: O(size^2) per scaled crown
        """
        cache_key = (crown_team, size, size)

        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]

        if crown_team == 1:
            crown_path = os.path.join(self.assets_path, "UI", "crown_t1.png")
        elif crown_team == 2:
            crown_path = os.path.join(self.assets_path, "UI", "crown_t2.png")
        else:
            return None
        
        crown = self._load_image(crown_path)
        if crown:
            scaled = pygame.transform.scale(crown, (size, size))
            self._scaled_cache[cache_key] = scaled
            return scaled
        
        return None

    def get_elixir_icon(self, size: int = 20) -> Optional[pygame.Surface]:
        """
        Load elixir icon at specified size
        
        - Time: O(1) cached, O(size^2) on first load and scale
        - Space: O(size^2) for surface
        """
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

    def get_card_overlay(self, width: int, height: int,
                        color: Tuple[int, int, int, int] = (128, 128, 128, 128)) -> pygame.Surface:
        """
        Get cached transparent overlay surface for expensive cards

        - Time: Worst case O(w*h), Average case O(1) cached, O(w*h) on first create
        - Space: O(w*h) per overlay variant
        """
        cache_key = (width, height, color)
        
        if cache_key in self._overlay_cache:
            return self._overlay_cache[cache_key]
        
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(color)
        self._overlay_cache[cache_key] = overlay
        return overlay
    
    def get_elixir_segment_positions(self, bar_width: int, max_elixir: int) -> List[Tuple[int, int]]:
        """
        Get cached segment positions for elixir bar

        - Time: Worst case O(max_elixir), Average case O(1) cached, O(max_elixir) on first calculation
        - Space: O(max_elixir) for positions list
        """
        cache_key = (bar_width, max_elixir)
        
        if cache_key in self._segment_cache:
            return self._segment_cache[cache_key]
        
        segment_count = max_elixir
        segment_width = bar_width / segment_count
        segments = []
        
        for i in range(segment_count):
            seg_x = int(i * segment_width)
            seg_w = int((i + 1) * segment_width) - int(i * segment_width)
            segments.append((seg_x, seg_w))
        
        self._segment_cache[cache_key] = segments
        return segments

    def _load_image(self, path: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Helper to load a single image

        - Time: Worst case = Average case = O(w*h)
        - Space: O(w*h) for surface
        """
        if not os.path.exists(path):
            return None
        try:
            img = pygame.image.load(path)
            return img.convert_alpha() if convert_alpha else img.convert()
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """
        Clear all caches

        - Time: Worst case = Average case = O(n) where n is total cached items across all caches
        - Space: O(1)
        """
        super().clear_cache()
        self._scaled_cache.clear()
        self._overlay_cache.clear()
        self._segment_cache.clear()