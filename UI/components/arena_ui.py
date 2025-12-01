import pygame
from constants import *
from core.sorting import sort_for_visualization

colors = {
    0: (0, 0, 0),  # none
    1: (0, 214, 47),  # grass
    2: (0, 157, 214),  # water
    3: (133, 133, 133),   # bridge
    4: (191, 143, 36), # tower p1
    5: (200, 100, 100), # tower p2
    9: (200, 100, 100, 100) # transparent red
}

def draw_arena(cols, rows, tile_size, asset_manager, screen, arena, selected_card=None, DRAW_PLACABLE_CELLS=False, team=1):
    """
    Draws the arena grid and optional placeable cell overlay

    - Time: Worst case O(h * w), Average case O(h * w) when rebuilding background, O(1) when using cached background
    - Space: O(h * w) for cached background surface

    TODO: what about alternative: Could use multidimensional arrays for grid storage; full redraw is simpler and GPU-accelerated blit is fast
    """
    global arena_background_surface

    arena_width = int(cols * tile_size)
    arena_height = int(rows * tile_size)
    
    # Try to load arena background image
    if ARENA_BACKGROUND_USE_IMAGE:
        arena_background_image = asset_manager.get_arena_background(arena_width, arena_height)
    else:
        arena_background_image = None

    if arena_background_image:
        # use background image instead of grid
        # blit the background image directly to screen (no caching needed as it's already cached in asset_manager)
        screen.blit(arena_background_image, (0, 0))
    else:
        # fallback to grid-based background if image not available
        # create or recreate background surface if needed
        if arena_background_surface is None or arena.arena_background_dirty:
            # create a surface for the arena background
            arena_background_surface = pygame.Surface((arena_width, arena_height))
            
            # draw static grid elements to the cached surface
            for y, row in enumerate(arena.grid):
                for x, value in enumerate(row):
                    # calculate precise pixel coordinates to avoid gaps due to float truncation
                    x_pos = int(x * tile_size)
                    y_pos = int(y * tile_size)
                    width = int((x + 1) * tile_size) - x_pos
                    height = int((y + 1) * tile_size) - y_pos

                    rect = pygame.Rect(x_pos, y_pos, width, height)
                    
                    # fill tile
                    pygame.draw.rect(arena_background_surface, colors[value], rect)

                    if DRAW_BORDERS:
                        # draw border (white, thickness 1)
                        pygame.draw.rect(arena_background_surface, (255, 255, 255), rect, 1)
            
            arena.arena_background_dirty = False
        
        # blit the cached background to screen
        screen.blit(arena_background_surface, (0, 0))
    
    # only draw placable cells overlay if needed (this changes dynamically)
    if DRAW_PLACABLE_CELLS or selected_card is not None:
        for y, row in enumerate(arena.grid):
            for x, value in enumerate(row):
                # we draw as red the cells where we CANNOT place a troop so we use not is_placable_cell
                if not arena.is_placable_cell(y, x, team=team, is_flying=False):
                    x_pos = int(x * tile_size)
                    y_pos = int(y * tile_size)
                    width = int((x + 1) * tile_size) - x_pos
                    height = int((y + 1) * tile_size) - y_pos
                    rect = pygame.Rect(x_pos, y_pos, width, height)
                    pygame.draw.rect(screen, colors[9], rect)

def draw_units(arena, screen, tile_size, asset_manager):
    """
    Draws all troops in render order (top to bottom for proper layering)

    - Time: Worst case O(n log n), Average case O(n log n) for sorting plus O(n) for drawing where n is number of troops
    - Space: O(n) for sorted list

    TODO: what about alternative: Could use linked lists for troop ordering; sorting by Y is simpler for 2D
    """
    # using the set() to get unique troops (avoid drawing same troop multiple times)
    for troop in sort_for_visualization(arena.unique_troops, ascending_order=True):
        if troop.location is None:
            continue

        is_tower = troop.name.startswith("Tower")
            
        # width and height are already in grid cells, so multiply by tile_size to get pixels
        if is_tower:
            draw_tower(troop, screen, tile_size)
        else:
            # regular troops: scale visually but keep grid size as original
            # apply visual scaling based on board scale
            visual_scale_x = arena.width / 18.0 * 2
            visual_scale_y = arena.height / 32.0 * 2
            base_visual_width = int(troop.width * visual_scale_x * tile_size)
            base_visual_height = int(troop.height * visual_scale_y * tile_size)
            
            # apply scale_multiplier for uniform scaling in all directions
            visual_width = int(base_visual_width * troop.scale_multiplier)
            visual_height = int(base_visual_height * troop.scale_multiplier)

            # calculate the center of the troop for multi-cell troops
            cell_center_x = int((troop.location[1] + troop.width / 2.0) * tile_size)  # col + width/2 for center
            cell_center_y = int((troop.location[0] + troop.height / 2.0) * tile_size)  # row + height/2 for center

            image_x = cell_center_x - visual_width // 2
            image_y = cell_center_y - visual_height // 2

            # get scaled sprite from cache - now scales to exact dimensions uniformly
            scaled_sprite = asset_manager.get_scaled_sprite(troop.sprite, troop.sprite_number, visual_width, visual_height)
            
            # draw the sprite at the calculated position (no offset needed since it fills the area)
            screen.blit(scaled_sprite, (image_x, image_y))

        draw_healthbar(troop, screen, tile_size, arena)

def draw_tower(troop, screen, tile_size):
    """
    Draw a tower with its assets centered on the tower's grid position

    - Time: Worst case O(1), Average case O(1) cached sprite lookup and single blit operation
    - Space: O(1) uses cached sprites

    TODO: what about alternative: Could use arrays for asset storage; direct blitting is simpler for static towers
    """
    if not troop.asset_manager or troop.tower_number is None:
        # Fallback to colored rectangle
        visual_width = int(troop.width * tile_size)
        visual_height = int(troop.height * tile_size)
        x_pos = int(troop.location[1] * tile_size)
        y_pos = int(troop.location[0] * tile_size)
        pygame.draw.rect(screen, troop.color, (x_pos, y_pos, visual_width, visual_height))
        return
    
    # Get tower type from tower_number
    tower_type = troop.tower_number
    
    # Get tower assets
    tower_assets = troop.asset_manager.get_tower_assets(tower_type, troop.team, troop.is_alive)
    
    # calculate tower's grid center position (in pixels)
    # troop.location is (row, col) - top-left corner
    tower_top_left_x = int(troop.location[1] * tile_size)  # col * tile_size
    tower_top_left_y = int(troop.location[0] * tile_size)  # row * tile_size
    tower_width = int(troop.width * tile_size)
    tower_height = int(troop.height * tile_size)
    
    # calculate center of tower's grid area
    tower_center_x = tower_top_left_x + tower_width // 2
    tower_center_y = tower_top_left_y + tower_height // 2
    
    if not troop.is_alive and tower_assets['destroyed']:
        # draw destroyed tower sprite (scaled and centered)
        scaled_destroyed = troop.asset_manager.get_scaled_tower_sprite(
            tower_assets['destroyed'], 
            tower_width, 
            tower_height,
            tower_type,
            'destroyed'
        )
        scaled_width, scaled_height = scaled_destroyed.get_size()
        
        # Center the sprite on the tower's grid center
        sprite_x = tower_center_x - scaled_width // 2
        sprite_y = tower_center_y - scaled_height // 2
        screen.blit(scaled_destroyed, (sprite_x, sprite_y))
    
    elif troop.is_alive and tower_assets['building']:
        # draw building (scaled and centered)
        scaled_building = troop.asset_manager.get_scaled_tower_sprite(
            tower_assets['building'], 
            tower_width, 
            tower_height,
            tower_type,
            'building'
        )
        scaled_width, scaled_height = scaled_building.get_size()
        
        # center the building sprite on the tower's grid center
        building_x = tower_center_x - scaled_width // 2 
        building_y = tower_center_y - scaled_height // 2
        
        screen.blit(scaled_building, (building_x, building_y))
        
        # Draw character on top (for king tower only)
        if tower_assets['character']:
            # character is scaled separately and positioned at top center
            # use a smaller target size for character (about 40% of tower)
            char_target_width = int(tower_width * 0.4)
            char_target_height = int(tower_height * 0.4)
            
            scaled_character = troop.asset_manager.get_scaled_tower_sprite(
                tower_assets['character'],
                char_target_width,
                char_target_height,
                tower_type,
                'character'
            )
            char_scaled_width, char_scaled_height = scaled_character.get_size()
            
            # center character horizontally on tower center, position near top
            char_x = tower_center_x - char_scaled_width // 2
            # position character at top of tower (10% from top of tower grid)
            char_y = tower_top_left_y + int(tower_height * 0.1) - char_scaled_height // 2
            screen.blit(scaled_character, (char_x, char_y))
    else:
        # fallback to colored rectangle if assets not loaded
        pygame.draw.rect(screen, troop.color, (tower_top_left_x, tower_top_left_y, tower_width, tower_height))

def draw_healthbar(troop, screen, tile_size, arena):
    """
    Draw a healthbar above a troop or tower

    - Time: Worst case O(1), Average case O(1) constant calculations and rectangle draws
    - Space: O(1) no allocations
    """
    if not troop.is_alive or troop.location is None:
        return
    
    # calculate health percentage
    if not hasattr(troop, 'max_health') or troop.max_health <= 0:
        health_percentage = 1.0  # default to full if max_health not set
    else:
        health_percentage = max(0.0, min(1.0, troop.health / troop.max_health))
    
    is_tower = troop.name.startswith("Tower")
    
    # calculate position based on unit type
    if is_tower:
        # towers: position at top of tower
        visual_width = int(troop.width * tile_size)
        x_pos = int(troop.location[1] * tile_size)
        y_pos = int(troop.location[0] * tile_size)
        bar_y = y_pos - 8  # 8 pixels above the tower (TODO: make this a variable)
    else:
        # regular troops: position above the sprite
        visual_scale_x = arena.width / 18.0 * 2
        visual_scale_y = arena.height / 32.0 * 2
        visual_width = int(troop.width * visual_scale_x * tile_size)
        visual_height = int(troop.height * visual_scale_y * tile_size)
        
        cell_center_x = int((troop.location[1] + troop.width / 2.0) * tile_size)
        cell_center_y = int((troop.location[0] + troop.height / 2.0) * tile_size)
        
        image_y = cell_center_y - visual_height // 2
        bar_y = image_y - 8  # 8 pixels above the sprite (TODO: make this a variable)
        x_pos = cell_center_x - visual_width // 2
    
    # healthbar dimensions
    bar_width = max(30, visual_width * 0.8)  # 80% of unit width, minimum 30px
    bar_height = 4
    bar_x = x_pos + (visual_width - bar_width) / 2  # center the bar
    
    # draw background (dark red/black)
    pygame.draw.rect(screen, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    
    # draw health bar (green to red gradient based on health)
    if health_percentage > 0.6:
        health_color = (0, 255, 0)  # green
    elif health_percentage > 0.3:
        health_color = (255, 255, 0)  # yellow
    else:
        health_color = (255, 0, 0)  # red
    
    health_width = int(bar_width * health_percentage)
    if health_width > 0:
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
    
    # draw border
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)  
