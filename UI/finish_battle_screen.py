import pygame
from UI.components.button import Button

class FinishBattleScreen:
    def __init__(self, arena, asset_manager, screen):
        self.screen = screen
        self.arena = arena
        self.asset_manager = asset_manager

        self.buttons = []

        self.restart_clicked = False
        self.main_menu_clicked = False
        
        self.winner_team = None
        self.number_of_crowns = None
        self.initiate_screen()
        
    def initiate_screen(self):
        if 0 not in self.arena.towers_P1:
            self.winner_team = 2
            self.number_of_crowns = 3
        elif 0 not in self.arena.towers_P2:
            self.winner_team = 1
            self.number_of_crowns = 3

        elif len(self.arena.towers_P1) > len(self.arena.towers_P2):
            self.winner_team = 1
            self.number_of_crowns = 3 - len(self.arena.towers_P2)
        elif len(self.arena.towers_P1) < len(self.arena.towers_P2):
            self.winner_team = 2
            self.number_of_crowns = 3 - len(self.arena.towers_P1)
        else:
            self.winner_team = 0
            self.number_of_crowns = 3 - len(self.arena.towers_P1)
       
        # placing the buttons at the bottom of the screen next to each other with spacing
        button_width = 160
        button_height = 60
        spacing = 30

        display_width, display_height = pygame.display.get_surface().get_size()
        total_width = button_width * 2 + spacing
        start_x = (display_width - total_width) // 2
        button_y = display_height - button_height - 40

        self.buttons.append(Button(
            start_x, button_y, button_width, button_height,
            "Rematch",
            self.asset_manager.get_font(24),
            (179, 176, 22),
            self.restart
        ))

        self.buttons.append(Button(
            start_x + button_width + spacing, button_y, button_width, button_height,
            "Main Menu",
            self.asset_manager.get_font(24),
            (40, 40, 199),
            self.go_to_main_menu
        ))
        
        

    def go_to_main_menu(self):
        self.main_menu_clicked = True
    
    def restart(self):
        self.restart_clicked = True

    def draw(self):
        # get size of pygame display
        display_width, display_height = pygame.display.get_surface().get_size()
        winner_screen = self.asset_manager.get_winner_screen(display_width, display_height)
        self.screen.blit(winner_screen, (0, 0))

        # calculate crowns for each team
        p1_crowns = 3 - len(self.arena.towers_P2) if 0 in self.arena.towers_P2 else 3
        p2_crowns = 3 - len(self.arena.towers_P1) if 0 in self.arena.towers_P1 else 3
        
        # crown size and positioning
        crown_size = 80
        cushion_spacing = 110  # Distance between cushions
        
        # position for P2 (red/pink couch - top)
        p2_center_y = display_height * 0.20  # Top couch
        p2_center_x = display_width / 2
        
        # position for P1 (blue couch - bottom)
        p1_center_y = display_height * 0.50  # Bottom couch
        p1_center_x = display_width / 2
        
        # draw P2 crowns (red team - top couch)
        for i in range(p2_crowns):
            crown = self.asset_manager.get_crown_image(2, crown_size)
            if crown:
                # position crowns - left, center, right
                offset = (i - 1) * cushion_spacing  # -1, 0, 1 positions
                crown_x = p2_center_x + offset - crown_size // 2
                crown_y = p2_center_y - crown_size // 2 + abs(i - 1) * 10
                self.screen.blit(crown, (crown_x, crown_y))
        
        # draw P1 crowns (blue team - bottom couch)
        for i in range(p1_crowns):
            crown = self.asset_manager.get_crown_image(1, crown_size)
            if crown:
                # position crowns - left, center, right
                offset = (i - 1) * cushion_spacing  # -1, 0, 1 positions
                crown_x = p1_center_x + offset - crown_size // 2
                crown_y = p1_center_y - crown_size // 2 + abs(i - 1) * 10
                self.screen.blit(crown, (crown_x, crown_y))
        
        # draw winner text above the winning team's couch (blue or red)
        if self.winner_team == 1:
            # p1 (blue) wins - text above blue couch
            text_color = (100, 149, 237)  # Blue
            text = self.asset_manager.get_font(48).render("VICTORY!", True, text_color)
            text_rect = text.get_rect(center=(p1_center_x, p1_center_y - 150))
            self.screen.blit(text, text_rect)
        elif self.winner_team == 2:
            # p2 (red) wins - text above red couch
            text_color = (220, 20, 60)  # Red
            text = self.asset_manager.get_font(48).render("VICTORY!", True, text_color)
            text_rect = text.get_rect(center=(p2_center_x, p2_center_y - 150))
            self.screen.blit(text, text_rect)
        else:
            # draw text - it's a draw
            text_color = (255, 255, 255)  # White
            text = self.asset_manager.get_font(48).render("DRAW!", True, text_color)
            text_rect = text.get_rect(center=(display_width / 2, display_height / 3))
            self.screen.blit(text, text_rect)

        # draw buttons
        for button in self.buttons:
            button.draw(self.screen)
       

    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.buttons:
                        if button.is_clicked(mouse_pos):
                            return True
        return False
        
