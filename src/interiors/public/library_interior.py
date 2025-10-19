import pygame
import random
from src.interiors.base_interior import BaseInterior

class LibraryInterior(BaseInterior):
    def __init__(self, game, room_name):
        super().__init__(game, room_name)
        self.librarian = Librarian(10, 8, self)
        self.dialogue_active = False
        self.dialogue_text = ""
        self.dialogue_timer = 0
        self.computers_available = 3
        self.study_areas = [(5, 5), (15, 5), (5, 12), (15, 12)]

    def enter(self):
        """Called when entering the library"""
        super().enter()
        self.player_x = 12
        self.player_y = 18

        # Check current objective for specific dialogue
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id == "go_to_library":
            self.start_dialogue("Welcome! Looking for housing resources? The computers are free to use, and we have guides on tenant rights.")

    def handle_event(self, event):
        """Handle library-specific events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # Check if near librarian
                if self.is_near_librarian():
                    self.interact_with_librarian()
                # Check if near computer
                elif self.is_near_computer():
                    self.use_computer()
                # Check if near study area
                elif self.is_near_study_area():
                    self.use_study_area()
            elif event.key == pygame.K_ESCAPE:
                if self.dialogue_active:
                    self.dialogue_active = False
                else:
                    self.exit()

    def is_near_librarian(self):
        """Check if player is near the librarian"""
        dist = abs(self.player_x - self.librarian.x) + abs(self.player_y - self.librarian.y)
        return dist <= 2

    def is_near_computer(self):
        """Check if near computer stations"""
        computer_positions = [(3, 3), (6, 3), (9, 3)]
        for comp_x, comp_y in computer_positions:
            if abs(self.player_x - comp_x) <= 1 and abs(self.player_y - comp_y) <= 1:
                return True
        return False

    def is_near_study_area(self):
        """Check if near study area"""
        for study_x, study_y in self.study_areas:
            if abs(self.player_x - study_x) <= 1 and abs(self.player_y - study_y) <= 1:
                return True
        return False

    def interact_with_librarian(self):
        """Interact with the librarian"""
        dialogues = [
            "The computers have free internet access. Great for housing searches!",
            "We have a bulletin board with local housing resources by the entrance.",
            "Need help printing documents? I can assist you with that.",
            "Our housing resource section is in aisle 3. Lots of helpful guides there.",
            "We're open until 8 PM on weekdays if you need a quiet place to make calls."
        ]

        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id == "go_to_library":
            self.start_dialogue("I've set up a computer for you to search for housing. We also have printouts of tenant rights and local resources.")
            self.game.show_notification("Obtained: Housing Resource Packet")
            # Progress objective
            self.game.objective_manager.complete_current_objective()
        else:
            self.start_dialogue(random.choice(dialogues))

    def use_computer(self):
        """Use a library computer"""
        self.start_dialogue("You search for affordable housing options and tenant resources online...")
        self.game.player_energy -= 5

        # If on library objective, provide specific help
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id == "go_to_library":
            self.start_dialogue("You find several housing programs and print out applications. The librarian helps you understand the requirements.")

    def use_study_area(self):
        """Use a study area"""
        self.start_dialogue("You sit down to review housing documents and make a plan...")
        self.game.player_stress -= 10
        self.game.player_energy -= 5

    def start_dialogue(self, text):
        """Start showing dialogue"""
        self.dialogue_active = True
        self.dialogue_text = text
        self.dialogue_timer = 3.0

    def update(self, dt):
        """Update the library interior"""
        super().update(dt)

        # Update librarian
        self.librarian.update(dt)

        # Update dialogue timer
        if self.dialogue_active:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.dialogue_active = False

    def draw(self, screen):
        """Draw the library interior"""
        super().draw(screen)

        # Draw librarian
        self.librarian.draw(screen, self.camera_x, self.camera_y)

        # Draw interaction prompts
        if self.is_near_librarian():
            self.draw_interaction_prompt(screen, "Press E to talk to librarian")
        elif self.is_near_computer():
            self.draw_interaction_prompt(screen, "Press E to use computer")
        elif self.is_near_study_area():
            self.draw_interaction_prompt(screen, "Press E to study")

        # Draw dialogue
        if self.dialogue_active:
            self.draw_dialogue(screen)

    def draw_dialogue(self, screen):
        """Draw dialogue box"""
        # Create dialogue background
        dialogue_bg = pygame.Surface((700, 100))
        dialogue_bg.fill((40, 40, 40))
        dialogue_bg.set_alpha(230)

        x = (screen.get_width() - 700) // 2
        y = screen.get_height() - 150

        screen.blit(dialogue_bg, (x, y))

        # Draw text
        font = pygame.font.Font(None, 24)

        # Word wrap the text
        words = self.dialogue_text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] < 680:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Draw each line
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (x + 10, y + 10 + i * 30))

    def draw_interaction_prompt(self, screen, text):
        """Draw interaction prompt above player"""
        font = pygame.font.Font(None, 20)
        text_surface = font.render(text, True, (255, 255, 200))

        # Position above player
        player_screen_x = self.player_x * 32 - self.camera_x
        player_screen_y = self.player_y * 32 - self.camera_y - 40

        # Draw background
        bg = pygame.Surface((text_surface.get_width() + 10, 25))
        bg.fill((40, 40, 40))
        bg.set_alpha(200)

        x = player_screen_x - text_surface.get_width() // 2
        y = player_screen_y

        screen.blit(bg, (x - 5, y))
        screen.blit(text_surface, (x, y + 2))


class Librarian:
    """NPC Librarian character"""
    def __init__(self, x, y, interior):
        self.x = x
        self.y = y
        self.interior = interior
        self.animation_timer = 0
        self.facing = "down"

    def update(self, dt):
        """Update librarian animation"""
        self.animation_timer += dt

        # Simple idle animation - occasionally look around
        if random.random() < 0.01:
            self.facing = random.choice(["down", "left", "right"])

    def draw(self, screen, camera_x, camera_y):
        """Draw the librarian"""
        screen_x = self.x * 32 - camera_x
        screen_y = self.y * 32 - camera_y

        # Draw librarian sprite (purple/professional colors)
        pygame.draw.rect(screen, (80, 50, 120),
                        (screen_x + 8, screen_y + 8, 16, 24))

        # Draw head
        pygame.draw.circle(screen, (255, 220, 200),
                         (screen_x + 16, screen_y + 12), 6)

        # Draw glasses
        pygame.draw.line(screen, (50, 50, 50),
                        (screen_x + 12, screen_y + 12),
                        (screen_x + 20, screen_y + 12), 2)

        # Draw name tag
        font = pygame.font.Font(None, 16)
        name = font.render("Librarian", True, (255, 255, 255))
        screen.blit(name, (screen_x - 8, screen_y - 10))