import pygame
from deck.card import Card
from deck.deck import Deck
from deck.stats import stats
from troops.generic_troop import Troop
from UI.components.unit_components.button import Button
from core.sorting import merge_sort_by_key 

def run_deck_builder(screen, asset_manager):
    clock = pygame.time.Clock()
    W, H = screen.get_size()
    CW, CH, SP = 70, 80, 8
    
    cards = [Card(name=n, color="gray", troop_class=Troop, troop_name=n, asset_manager=asset_manager) for n in stats]
    selected = []
    scroll_y = 0
    
    deck_y = 50
    deck_bottom = deck_y + CH * 2 + SP  # bottom of the 2x4 deck grid
    cards_area_y = deck_bottom + 60
    cards_area_h = H - cards_area_y - 70
    
    def draw_card(card, x, y, dimmed=False):
        img = card.get_card_image(CW, CH)
        if img: screen.blit(img, (x, y))
        if dimmed: screen.blit(asset_manager.get_card_overlay(CW, CH, (0, 0, 0, 160)), (x, y))
    
    confirm_ready = [False]
    def on_confirm(): confirm_ready[0] = len(selected) == 8
    def on_sort(): cards[:] = merge_sort_by_key(cards, key=lambda c: c.cost)
    
    btn_battle = Button(W//2 - 70, H - 60, 140, 45, "Battle!", asset_manager.get_font(24), (50, 150, 50), on_confirm)
    btn_sort = Button(W//2 - 50, deck_bottom + 10, 100, 35, "Sort ⇅", asset_manager.get_font(18), (100, 100, 150), on_sort)
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, scroll_y - e.y * 30)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                btn_sort.is_clicked((mx, my))
                if len(selected) == 8 and btn_battle.is_clicked((mx, my)) and confirm_ready[0]:
                    return Deck(selected.copy())
                
                # click on deck (top) to remove
                deck_x = (W - 4 * (CW + SP) + SP) // 2
                for i, c in enumerate(selected):
                    row, col = i // 4, i % 4
                    r = pygame.Rect(deck_x + col * (CW + SP), deck_y + row * (CH + SP), CW, CH)
                    if r.collidepoint(mx, my): selected.remove(c); break
                
                # click on cards area to add
                if cards_area_y <= my < cards_area_y + cards_area_h:
                    grid_x = (W - 4 * (CW + SP) + SP) // 2
                    for i, c in enumerate(cards):
                        row, col = i // 4, i % 4
                        y = cards_area_y + row * (CH + SP + 15) - scroll_y
                        if y + CH < cards_area_y or y > cards_area_y + cards_area_h: continue
                        r = pygame.Rect(grid_x + col * (CW + SP), y, CW, CH)
                        if r.collidepoint(mx, my) and c not in selected and len(selected) < 8:
                            selected.append(c); break
        
        screen.fill((25, 20, 35))
        
        # deck area (top, 2 rows of 4)
        deck_x = (W - 4 * (CW + SP) + SP) // 2
        for i in range(8):
            row, col = i // 4, i % 4
            x, y = deck_x + col * (CW + SP), deck_y + row * (CH + SP)
            pygame.draw.rect(screen, (50, 45, 60), (x, y, CW, CH), 2)
            if i < len(selected): draw_card(selected[i], x, y)
        
        btn_sort.draw(screen)
        
        # cards scroll area
        pygame.draw.rect(screen, (40, 35, 50), (0, cards_area_y, W, cards_area_h))
        grid_x = (W - 4 * (CW + SP) + SP) // 2
        for i, c in enumerate(cards):
            row, col = i // 4, i % 4
            x = grid_x + col * (CW + SP)
            y = cards_area_y + row * (CH + SP + 15) - scroll_y
            if y + CH < cards_area_y or y > cards_area_y + cards_area_h: continue
            draw_card(c, x, y, dimmed=(c in selected))
            # elixir cost
            screen.blit(asset_manager.get_text_surface(str(c.cost), 14, (255, 200, 255)), (x + CW//2 - 4, y + CH + 1))
        
        # battle button
        if len(selected) == 8: btn_battle.draw(screen)
        else: pygame.draw.rect(screen, (60, 60, 60), (btn_battle.x, btn_battle.y, btn_battle.width, btn_battle.height))
        
        pygame.display.flip()
        clock.tick(60)