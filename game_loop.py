from re import I
from arena.arena import Arena
from constants import BASE_GRID_HEIGHT, MULTIPLIER_GRID_HEIGHT
from deck.card import Card
from deck.deck import Deck
from player import Player
from troops.generic_troop import Troop
import pygame

colors = {
    0: (0, 0, 0),  # none
    1: (0, 214, 47),  # grass
    2: (0, 157, 214),  # water
    3: (133, 133, 133),   # bridge
    4: (191, 143, 36), # tower p1
    5: (200, 100, 100), # tower p2
    9: (200, 100, 100, 100) # transparent red
}

cards = [Card(name="barbarian 1", cost=1, color="red", troop_class=Troop, troop_name="barbarian"), 
    Card(name="barbarian 2", cost=2, color="blue", troop_class=Troop, troop_name="barbarian"),
    Card(name="barbarian 3", cost=3, color="green", troop_class=Troop, troop_name="barbarian"),
    Card(name="barbarian 4", cost=4, color="yellow", troop_class=Troop, troop_name="barbarian"),
    Card(name="barbarian 5", cost=5, color="purple", troop_class=Troop, troop_name="barbarian"),
    Card(name="archer 1", cost=6, color="orange", troop_class=Troop, troop_name="archer"),
    Card(name="archer 2", cost=7, color="red", troop_class=Troop, troop_name="archer"),
    Card(name="archer 3", cost=8, color="blue", troop_class=Troop, troop_name="archer"),
    Card(name="archer 4", cost=9, color="green", troop_class=Troop, troop_name="archer"),
    Card(name="archer 5", cost=10, color="yellow", troop_class=Troop, troop_name="archer")]

deck = Deck(cards)
deck.shuffle_cards()

"""
Modifiable variables for the game loop
"""
rows = int(BASE_GRID_HEIGHT*MULTIPLIER_GRID_HEIGHT)
cols = int(rows / 16 * 9)
draw_borders = True
hand_area_height = 100
draw_placable_cells = True
tick_rate = 1 # N frames per tick (meaning if N = 5, we will tick every 5 frames)


"""
Global variables for the game loop
"""
screen = None
clock = None
arena = None
tile_size = None
selected_card = None
frame_count = 0
card_rects = []
arena_background_surface = None
arena_background_dirty = True
_font_cache = None
_card_text_cache = {}  # key = (card_name, card_cost), value = (name_surface, cost_surface)


def setup_arena():
    global screen, clock, arena, tile_size
    # find optimal tile size
    tile_size = 800/rows # optimal for 32 is 25

    pygame.init()

    screen = pygame.display.set_mode((int(cols * tile_size), int(rows * tile_size) + hand_area_height))
    clock = pygame.time.Clock()

    arena = Arena(rows)
    arena.world_generation()
    arena_background_dirty = True

def add_test_troops():
    global arena
    location = (10, 2)
    simple_troop = Troop(name="simple_troop", health=100, damage=1, range=1, movement_speed=1, attack_type="melee", attack_speed=1, attack_range=1, attack_cooldown=1, size=1, color=(255, 0, 0), team=2, location=location, arena=arena)
    arena.spawn_unit(simple_troop, location)

    location = (rows-10, 2)
    simple_troop_team_2 = Troop(name="simple_troop", health=100, damage=1, range=1, movement_speed=2, attack_type="melee", attack_speed=1, attack_range=1, attack_cooldown=1, size=1, color=(255, 0, 0), team=1, location=location, arena=arena)
    arena.spawn_unit(simple_troop_team_2, location)

def draw_arena(draw_placable_cells=False, team=1):
    global arena_background_surface, arena_background_dirty
    
    # create or recreate background surface if needed
    if arena_background_surface is None or arena_background_dirty:
        # create a surface for the arena background
        arena_background_surface = pygame.Surface((int(cols * tile_size), int(rows * tile_size)))
        
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

                if draw_borders:
                    # draw border (white, thickness 1)
                    pygame.draw.rect(arena_background_surface, (255, 255, 255), rect, 1)
        
        arena_background_dirty = False
    
    # Blit the cached background to screen
    screen.blit(arena_background_surface, (0, 0))
    
    # Only draw placable cells overlay if needed (this changes dynamically)
    if draw_placable_cells:
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
    if frame_count % tick_rate == 0:
        for troop in arena.unique_troops:
            troop.move_to_tower()

def draw_units():
    # using the set() to get unique troops (avoid drawing same troop multiple times)
    for troop in arena.unique_troops:
        if troop.location is None:
            continue

        is_tower = troop.name.startswith("Tower")
            
        # width and height are already in grid cells, so multiply by tile_size to get pixels
        if is_tower:
            # towers: use actual grid dimensions
            visual_width = int(troop.width * tile_size)
            visual_height = int(troop.height * tile_size)

            x_pos = int(troop.location[1] * tile_size)
            y_pos = int(troop.location[0] * tile_size)

            color = troop.color
            pygame.draw.rect(screen, color, (x_pos, y_pos, visual_width, visual_height))
    
        else:
            # regular troops: scale visually but keep grid size as original
            # apply visual scaling based on board scale
            visual_scale_x = arena.width / 18.0 * 2
            visual_scale_y = arena.height / 32.0 * 2
            visual_width = int(troop.width * visual_scale_x * tile_size)
            visual_height = int(troop.height * visual_scale_y * tile_size)

            cell_center_x = int((troop.location[1] + 0.5) * tile_size)  # col + 0.5 for center
            cell_center_y = int((troop.location[0] + 0.5) * tile_size)  # row + 0.5 for center

            image_x = cell_center_x - visual_width // 2
            image_y = cell_center_y - visual_height // 2

            # et scaled sprite from cache
            scaled_sprite = troop.get_scaled_sprite(visual_width, visual_height)
            scaled_width, scaled_height = scaled_sprite.get_size()
            
            # center the scaled sprite
            offset_x = (visual_width - scaled_width) // 2
            offset_y = (visual_height - scaled_height) // 2
            screen.blit(scaled_sprite, (image_x + offset_x, image_y + offset_y))
        
"""FONT"""
def get_font():
    """Get or create the font object"""
    global _font_cache
    if _font_cache is None:
        _font_cache = pygame.font.Font(None, 24)
    return _font_cache

def get_card_text_surfaces(card):
    """Get cached text surfaces for a card"""
    cache_key = (card.name, card.cost)
    if cache_key in _card_text_cache:
        return _card_text_cache[cache_key]
    
    font = get_font()
    name_text = font.render(card.name[:8], True, (0, 0, 0))
    cost_text = font.render(f"Cost: {card.cost}", True, (0, 0, 0))
    
    _card_text_cache[cache_key] = (name_text, cost_text)
    return name_text, cost_text

"""HAND"""
def draw_hand(player):
    """Draw the player's hand at the bottom of the screen"""
    if not player.hand:
        return
    
    card_width = 80
    card_height = 90
    card_spacing = 10
    hand_start_y = int(rows * tile_size) + 5  # start just below arena
    
    # calculate starting x to center the hand
    total_width = len(player.hand) * card_width + (len(player.hand) - 1) * card_spacing
    start_x = (int(cols * tile_size) - total_width) // 2
    
    card_rects = []  # store rects for click detection
    
    for i, card in enumerate(player.hand):
        x = start_x + i * (card_width + card_spacing)
        y = hand_start_y
        
        # card background
        card_rect = pygame.Rect(x, y, card_width, card_height)
        card_rects.append((card_rect, card))
        
        # highlight selected card
        if card == selected_card:
            pygame.draw.rect(screen, (255, 255, 0), card_rect, 3)  # yellow border
            pygame.draw.rect(screen, (100, 100, 100), card_rect)  # darker background
        else:
            pygame.draw.rect(screen, (150, 150, 150), card_rect)  # gray background
            pygame.draw.rect(screen, (200, 200, 200), card_rect, 2)  # light border
        
        # draw card color indicator (top portion)
        color_rect = pygame.Rect(x, y, card_width, 20)
        pygame.draw.rect(screen, card.color, color_rect)
        
        # draw card name and cost using cached surfaces
        name_text, cost_text = get_card_text_surfaces(card)
        screen.blit(name_text, (x + 5, y + 25))
        screen.blit(cost_text, (x + 5, y + 50))
    
    return card_rects


setup_arena()
player_1 = Player(name="Player 1", deck=deck, team=1, arena=arena)
player_2 = Player(name="Player 2", deck=deck, team=2, arena=arena)
player_1.setup_hand()
player_2.setup_hand()


# the loop only works for player 1 input for now
while True:
    frame_count += 1
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
                            selected_card = card
                            print(f"Selected: {card.name}")
                        
                        click_handled = True
                        break # found the event, stop searching
                
                if not click_handled and selected_card is not None: # which means not in the cards area and we have a selected card
                    # we convert to the grid, but now we need to check if it is in that grid
                    clicked_row = int(mouse_pos[1] // tile_size)
                    clicked_col = int(mouse_pos[0] // tile_size)

                    # check boundaries 
                    if arena.is_placable_cell(clicked_row, clicked_col, 1):
                        print(f"Placing troop at {clicked_row}, {clicked_col}")
                        
                        # player 
                        if not player_1.place_troop((clicked_row, clicked_col), selected_card):
                            continue
                        
                        # deselect after playing
                        selected_card = None

                        click_handled = True # in case we add other statments later 
                
    if frame_count % 100 == 0 and selected_card is not None:
        player_2.place_troop((0, 0), selected_card)

    screen.fill((0, 0, 0))
    draw_arena(selected_card, team=1)
    game_tick()
    draw_units()

    card_rects = draw_hand(player_1)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()