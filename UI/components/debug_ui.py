import pygame

"""DEBUG FUNCTIONS"""
def draw_attack_ranges(arena, tile_size, screen):
    """Draw semi-transparent attack range circles for all troops"""
    if not arena:
        return
    
    # Create a surface with per-pixel alpha for transparency
    for troop in arena.unique_troops:
        if troop.location is None or not troop.is_alive or not troop.is_active:
            continue
        
        # get troop center position in pixels
        # troop.location is (row, col)
        cell_center_x = int((troop.location[1] + troop.width / 2.0) * tile_size)  # col + width/2 for center
        cell_center_y = int((troop.location[0] + troop.height / 2.0) * tile_size)  # row + height/2 for center
       
        
        # convert attack_range from grid cells to pixels
        attack_range_pixels = int(troop.attack_range * tile_size)
        
        # create a surface for the circle with alpha
        # make it slightly larger than the range for visibility
        circle_surface = pygame.Surface((attack_range_pixels * 2 + 10, attack_range_pixels * 2 + 10), pygame.SRCALPHA)
        
        # draw semi-transparent circle (RGBA: red with 50% opacity)
        # use different colors for different teams
        if troop.team == 1:
            color = (255, 0, 0, 80)  # red, semi-transparent
        else:
            color = (0, 0, 255, 80)  # blue, semi-transparent
        
        # draw circle centered on the surface
        center_x = attack_range_pixels + 5
        center_y = attack_range_pixels + 5
        pygame.draw.circle(circle_surface, color, (center_x, center_y), attack_range_pixels, 2)  # 2 pixel border
        
        # also draw a filled circle with lower opacity for area visualization
        fill_color = (color[0], color[1], color[2], 30)  # even more transparent
        pygame.draw.circle(circle_surface, fill_color, (center_x, center_y), attack_range_pixels)
        
        # blit the circle surface to screen, offset by the center position
        screen.blit(circle_surface, (cell_center_x - center_x, cell_center_y - center_y))
        
        # optional: draw aggro range as well (outer circle)
        if hasattr(troop, 'attack_aggro_range') and troop.attack_aggro_range > troop.attack_range:
            aggro_range_pixels = int(troop.attack_aggro_range * tile_size)
            aggro_surface = pygame.Surface((aggro_range_pixels * 2 + 10, aggro_range_pixels * 2 + 10), pygame.SRCALPHA)
            aggro_color = (255, 255, 0, 60)  # yellow, semi-transparent for aggro range
            aggro_center_x = aggro_range_pixels + 5
            aggro_center_y = aggro_range_pixels + 5
            pygame.draw.circle(aggro_surface, aggro_color, (aggro_center_x, aggro_center_y), aggro_range_pixels, 1)
            screen.blit(aggro_surface, (cell_center_x - aggro_center_x, cell_center_y - aggro_center_y))
