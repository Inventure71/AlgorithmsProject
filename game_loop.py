from UI.finish_battle_screen import FinishBattleScreen
from arena.arena import Arena
from constants import *
from deck.card import Card
from deck.deck import Deck
from player import Player
from troops.generic_troop import Troop
from assets.asset_manager import AssetManager
import pygame
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

"""
Modifiable variables for the game loop
"""
rows = int(BASE_GRID_HEIGHT*MULTIPLIER_GRID_HEIGHT)
cols = int(rows / 16 * 9)
DRAW_PLACABLE_CELLS = True

"""
Global variables for the game loop
"""
looping = True
screen = None
clock = None
arena = None
tile_size = None
selected_card = None
card_rects = []
time_location = None
arena_background_surface = None
arena_background_dirty = True
asset_manager = AssetManager()

def setup_arena():
    global screen, clock, arena, tile_size, asset_manager, time_location
    # find optimal tile size
    tile_size = 800/rows # optimal for 32 is 25

    time_location = (int(cols * tile_size) - 50, 10)

    pygame.init()

    screen = pygame.display.set_mode((int(cols * tile_size), int(rows * tile_size) + HAND_AREA_HEIGHT))
    clock = pygame.time.Clock()

    arena = Arena(rows)
    arena.asset_manager = asset_manager
    arena.world_generation()
    arena.arena_background_dirty = True

def draw_arena(DRAW_PLACABLE_CELLS=False, team=1):
    global arena_background_surface, arena
    
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
    if DRAW_PLACABLE_CELLS:
        for y, row in enumerate(arena.grid):
            for x, value in enumerate(row):
                if arena.is_placable_cell(y, x, team=team):
                    x_pos = int(x * tile_size)
                    y_pos = int(y * tile_size)
                    width = int((x + 1) * tile_size) - x_pos
                    height = int((y + 1) * tile_size) - y_pos
                    rect = pygame.Rect(x_pos, y_pos, width, height)
                    pygame.draw.rect(screen, colors[9], rect)

def game_tick():
    # only every N frames
    if arena.frame_count % TICK_RATE == 0:
        for troop in list(arena.unique_troops):
            troop.move_to_tower()

def draw_units():
    # using the set() to get unique troops (avoid drawing same troop multiple times)
    for troop in sort_for_visualization(arena.unique_troops, ascending_order=True):
        if troop.location is None:
            continue

        is_tower = troop.name.startswith("Tower")
            
        # width and height are already in grid cells, so multiply by tile_size to get pixels
        if is_tower:
            draw_tower(troop)
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
            scaled_sprite = troop.get_scaled_sprite(visual_width, visual_height)
            
            # draw the sprite at the calculated position (no offset needed since it fills the area)
            screen.blit(scaled_sprite, (image_x, image_y))

        draw_healthbar(troop)

def draw_tower(troop):
    """Draw a tower with its assets centered on the tower's grid position."""
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

def draw_healthbar(troop):
    """Draw a healthbar above a troop or tower"""
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

"""FONT"""
def get_font(font_size=24):
    """Get or create the font object"""
    return asset_manager.get_font(font_size)

def get_card_text_surfaces(card):
    """Get cached text surfaces for a card"""
    name_text = asset_manager.get_text_surface(card.name[:8], 24, (0, 0, 0))
    cost_text = asset_manager.get_text_surface(f"Cost: {card.cost}", 24, (0, 0, 0))
    return name_text, cost_text

"""HAND"""
def draw_hand(player):
    """Draw the player's hand at the bottom of the screen"""
    if not player.hand:
        return
    
    card_width = 80
    card_height = 90
    card_spacing = 10
    elixir_icon_size = 20  # size of the elixir icon 

    hand_start_y = int(rows * tile_size)  # arena

    total_width = len(player.hand) * card_width + (len(player.hand) - 1) * card_spacing
    start_x = (int(cols * tile_size) - total_width) // 2

    draw_elixir_bar(player, hand_start_y, total_width, card_height, start_x)
    
    card_rects = []
    
    for i, card in enumerate(player.hand):
        x = start_x + i * (card_width + card_spacing)
        y = hand_start_y

        if card == selected_card:
            y -= 25
        
        card_rect = pygame.Rect(x, y, card_width, card_height)
        card_rects.append((card_rect, card))
        
        # highlight selected card
        if card == selected_card:
            pygame.draw.rect(screen, (255, 255, 0), card_rect, 3)
        
        # try to load and draw card image
        card_image = card.get_card_image(card_width, card_height)
        if card_image:
            screen.blit(card_image, (x, y))
        else:
            # fallback: draw color indicator if no image
            color_rect = pygame.Rect(x, y, card_width, 20)
            pygame.draw.rect(screen, card.color, color_rect)
        
        # draw elixir icon with cost at bottom center of card
        elixir_icon = asset_manager.get_elixir_icon(elixir_icon_size)
        
        if card.cost > player.current_elixir:
            overlay = asset_manager.get_card_overlay(card_width, card_height)
            screen.blit(overlay, (x, y))

        icon_x = x + (card_width - elixir_icon_size) // 2  # center horizontally
        icon_y = y + card_height - elixir_icon_size - 5  # 5 pixels from bottom

        draw_elixir_icon(icon_x, icon_y, elixir_icon_size, text_value=card.cost, text_size=16)

    
    return card_rects

def draw_elixir_icon(icon_x, icon_y, icon_size, text_value=None, text_size=18, text_color=(255, 255, 255)):
    elixir_icon = asset_manager.get_elixir_icon(icon_size)
    
    if elixir_icon:
        screen.blit(elixir_icon, (icon_x, icon_y))
        
        if text_value is not None:
            text_surface = asset_manager.get_text_surface(
                str(text_value),
                size=text_size,
                color=text_color
            )
            text_width, text_height = text_surface.get_size()
            text_x = icon_x + (icon_size - text_width) // 2
            text_y = icon_y + (icon_size - text_height) // 2
            screen.blit(text_surface, (text_x, text_y))

def draw_elixir_bar(player, hand_start_y, total_width, card_height, start_x):
    """Draw the purple segmented elixir bar with icon + number (Clash Royale style)."""
    if not player:
        return

    # layout
    bar_width = total_width
    bar_height = 20
    bar_margin_top = card_height    # margin of the cards - gap
    bar_x = start_x
    bar_y = hand_start_y + bar_margin_top

    # background bar (dark purple rounded rect)
    pygame.draw.rect(
        screen,
        (40, 0, 70),
        pygame.Rect(bar_x, bar_y, bar_width, bar_height),
        border_radius=10,
    )

    # segmented fill
    max_elixir = int(player.max_elixir)
    current_elixir = max(0.0, min(player.current_elixir, player.max_elixir))
    segment_count = max_elixir
    segment_width = bar_width / segment_count

    segment_positions = asset_manager.get_elixir_segment_positions(bar_width, max_elixir)

    filled_whole = int(current_elixir)          # full segments
    partial = current_elixir - filled_whole     # 0..1 for the next segment


    for i, (seg_x_base, seg_w) in enumerate(segment_positions):
        seg_x = bar_x + seg_x_base
        seg_w = int((i + 1) * segment_width) - int(i * segment_width)

        # inner rectangle for this segment
        seg_rect = pygame.Rect(seg_x + 1, bar_y + 2, seg_w - 2, bar_height - 4)

        # empty segment background (dark purple)
        pygame.draw.rect(screen, (90, 40, 140), seg_rect)

        # how much of this segment is filled (green to red gradient)
        if i < filled_whole:
            fill_frac = 1.0
        elif i == filled_whole and partial > 0:
            fill_frac = partial
        else:
            fill_frac = 0.0

        if fill_frac > 0:
            fill_w = int(seg_rect.width * fill_frac)
            fill_rect = pygame.Rect(seg_rect.x, seg_rect.y, fill_w, seg_rect.height)
            pygame.draw.rect(screen, (200, 0, 255), fill_rect)

        # segment outline (white)
        pygame.draw.rect(screen, (230, 230, 255), seg_rect, 1)

    # elixir icon with number on the left
    icon_size = bar_height + 12
    icon_x = bar_x - icon_size - 8
    icon_y = bar_y + (bar_height - icon_size) // 2

    draw_elixir_icon(icon_x, icon_y, icon_size, text_value=int(current_elixir))

"""DEBUG FUNCTIONS"""
def draw_attack_ranges():
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

"""GAME LOOP"""
while looping: # bigger loop for the game loop

    cards = [
    Card(name="barbarian 1", color="red", troop_class=Troop, troop_name="barbarian", asset_manager=asset_manager), 
    Card(name="barbarian 2", color="blue", troop_class=Troop, troop_name="barbarian", asset_manager=asset_manager),
    Card(name="barbarian 3", color="green", troop_class=Troop, troop_name="barbarian", asset_manager=asset_manager),
    Card(name="archer 1", color="orange", troop_class=Troop, troop_name="archer", asset_manager=asset_manager),
    Card(name="archer 2", color="red", troop_class=Troop, troop_name="archer", asset_manager=asset_manager),
    Card(name="archer 3", color="blue", troop_class=Troop, troop_name="archer", asset_manager=asset_manager),
    Card(name="giant 1", color="yellow", troop_class=Troop, troop_name="giant", asset_manager=asset_manager),
    Card(name="giant 2", color="green", troop_class=Troop, troop_name="giant", asset_manager=asset_manager)
    ]

    deck_p1 = Deck(cards)
    deck_p1.shuffle_cards()
    deck_p2 = Deck(cards)
    deck_p2.shuffle_cards()

    finish_battle_screen = None
    setup_arena()
    player_1 = Player(name="Player 1", deck=deck_p1, team=1, arena=arena)
    player_2 = Player(name="Player 2", deck=deck_p2, team=2, arena=arena)
    player_1.setup_hand()
    player_2.setup_hand()


    # the loop only works for player 1 input for now
    while True:
        if not arena.tick():
            print("Match over")
            break

        # here we handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # left click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left Mouse Button
                    mouse_pos = pygame.mouse.get_pos() # get position on screen
                    click_handled = False

                    for rect, card in card_rects:
                        if rect.collidepoint(mouse_pos):
                            if selected_card == card:
                                selected_card = None
                                print(f"De selected: {card.name}")
                            else:
                                if card.cost <= player_1.current_elixir:
                                    selected_card = card
                                    print(f"Selected: {card.name}")
                                else:
                                    print(f"Not enough elixir to select: {card.name}")
                            
                            click_handled = True
                            break # found the event, stop searching
                    
                    if not click_handled and selected_card is not None: # which means not in the cards area and we have a selected card
                        # we convert to the grid, but now we need to check if it is in that grid
                        clicked_row = int(mouse_pos[1] // tile_size)
                        clicked_col = int(mouse_pos[0] // tile_size)

                        # check boundaries 
                        if arena.is_placable_cell(clicked_row, clicked_col, 1):
                            print(f"Trying to place troop at {clicked_row}, {clicked_col}")
                            
                            # player 
                            if not player_1.place_troop((clicked_row, clicked_col), selected_card):
                                continue
                            
                            # deselect after playing
                            selected_card = None

                            click_handled = True # in case we add other statments later 
                    
        if arena.frame_count % 100 == 0 and selected_card is not None:
            player_2.place_troop((3, 3), selected_card)
            

        player_1.increase_elixir()    
        player_2.increase_elixir()

        screen.fill((66, 49, 22))
        draw_arena(selected_card, team=1)
        game_tick()
        draw_units()

        if DRAW_ATTACK_RANGES_DEBUG:
            draw_attack_ranges()

        card_rects = draw_hand(player_1)

        font = get_font(30)
        fps_surface = font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
        screen.blit(fps_surface, (10, 10))

        """TIME LEFT"""
        time_left_surface = font.render(f"{(arena.time_left//arena.one_minute)}:{((arena.time_left%arena.one_minute)//TICKS_PER_SECOND):02d}", True, (255, 255, 255))
        screen.blit(time_left_surface, time_location)
        
        """ELIXIR MULTIPLIER"""
        if arena.elixir_multiplier != 1:
            draw_elixir_icon(time_location[0], time_location[1] + 20, 40, f"x{arena.elixir_multiplier:.1f}")

        pygame.display.flip()
        clock.tick(TICKS_PER_SECOND+1) # we add 1 to have a bit of a margin, sometimes it goes a bit slow
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in finish_battle_screen.buttons:
                        button.is_clicked(mouse_pos)

        print("Match over")
        draw_arena(selected_card, team=1)
        draw_units()

        if finish_battle_screen is None:
            finish_battle_screen = FinishBattleScreen(arena, asset_manager, screen)

        if finish_battle_screen.restart_clicked:
            break
        
        if finish_battle_screen.main_menu_clicked:
            looping = False
            break

        finish_battle_screen.draw()
        pygame.display.flip()

        clock.tick(TICKS_PER_SECOND+1)

pygame.quit()
exit()