import pygame
from assets.asset_manager import AssetManager

def draw_hand(player, rows, cols, tile_size, asset_manager, screen, selected_card=None):
    """
    Draw the player's hand at the bottom of the screen

    - Time: Worst case O(h), Average case O(h) where h is hand size (4) draws each card
    - Space: O(h) for card_rects list
    """
    if not player.hand:
        return
    
    card_width = 80
    card_height = 90
    card_spacing = 10
    elixir_icon_size = 20  # size of the elixir icon 

    hand_start_y = int(rows * tile_size)  # arena

    total_width = len(player.hand) * card_width + (len(player.hand) - 1) * card_spacing
    start_x = (int(cols * tile_size) - total_width) // 2

    draw_elixir_bar(player, hand_start_y, total_width, card_height, start_x, asset_manager, screen)
    
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

        draw_elixir_icon(icon_x, icon_y, elixir_icon_size, asset_manager, screen, text_value=card.cost, text_size=16)

    
    return card_rects

def draw_elixir_icon(icon_x, icon_y, icon_size, asset_manager, screen, text_value=None, text_size=18, text_color=(255, 255, 255)):
    """
    Draw elixir icon with optional text overlay

    - Time: Worst case O(1), Average case O(1) cached sprite and text lookups
    - Space: O(1) uses cached surfaces
    """
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

def draw_elixir_bar(player, hand_start_y, total_width, card_height, start_x, asset_manager, screen):
    """
    Draw the purple segmented elixir bar with icon plus number Clash Royale style

    - Time: Worst case O(e), Average case O(e) where e is max_elixir (10) draws each segment
    - Space: O(1) uses cached segment positions
    """
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

    draw_elixir_icon(icon_x, icon_y, icon_size, asset_manager, screen, text_value=int(current_elixir))
