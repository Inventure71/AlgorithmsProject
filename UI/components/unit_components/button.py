import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color, callback):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.color = color
        self.callback = callback

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.x + self.width/2 - text_surface.get_width()/2, self.y + self.height/2 - text_surface.get_height()/2))

    def is_clicked(self, mouse_pos):
        """
        Checks if mouse position is inside button and triggers callback
        
        - Time: O(1) for bounds check plus O(callback) for callback execution
        - Space: O(1) no allocations
        """
        if (self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height):
            self.callback()
            return True
        return False