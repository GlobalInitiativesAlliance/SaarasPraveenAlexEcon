import pygame
import sys
import os

class MainMenu:
    def __init__(self, screen_width=1536, screen_height=1024):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.clock = pygame.time.Clock()

        # Load landscape background - use path relative to project root
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "loadedimage.png")
        self.background = pygame.image.load(image_path).convert()
        self.background = pygame.transform.scale(self.background, (screen_width, screen_height))

        # Button hitboxes tuned for 1536x1024 layout
        self.buttons = {
            "start": pygame.Rect(310, 250, 500, 95),
            "levels": pygame.Rect(310, 375, 500, 80),
            "howto": pygame.Rect(310, 475, 500, 80),
            "credits": pygame.Rect(310, 575, 500, 80),
            "quit": pygame.Rect(560, 850, 420, 80),
        }

        self.hover_button = None
        self.selected_action = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.hover_button = None
            for name, rect in self.buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.hover_button = name

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for name, rect in self.buttons.items():
                if rect.collidepoint(mouse_pos):
                    print(f"Button clicked: {name}")
                    self.selected_action = name
                    if name == "start":
                        return "start_game"
                    elif name == "quit":
                        pygame.quit()
                        sys.exit()
                    else:
                        return name

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return "start_game"
        return None

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        # Optional visual hitbox overlay for debugging
        for name, rect in self.buttons.items():
            color = (0, 255, 0, 90) if self.hover_button == name else (255, 255, 255, 50)
            overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            overlay.fill((*color[:3], 90))
            screen.blit(overlay, rect.topleft)

    def reset(self):
        self.hover_button = None
        self.selected_action = None


# --- Example run ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1536, 1024))
    pygame.display.set_caption("EquityPlay Main Menu (Landscape)")
    menu = MainMenu()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            action = menu.handle_event(event)
            if action == "start_game":
                print("Starting game... (Transition here)")
                running = False

        menu.draw(screen)
        pygame.display.flip()

    pygame.quit()
