import pygame
import os
import math


class CharacterOption:
    """Represents a selectable character"""
    def __init__(self, name, sprite_path, sprite_index, description):
        self.name = name
        self.sprite_path = sprite_path
        self.sprite_index = sprite_index  # Which premade character (01-32)
        self.description = description
        self.sprite = None
        self.load_sprite()

    def load_sprite(self):
        """Load character preview sprite"""
        try:
            sprite_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
                '0_Premade_Characters', '32x32', f'Premade_Character_32x32_{self.sprite_index:02d}.png'
            )

            spritesheet = pygame.image.load(sprite_path)
            # Extract idle_down sprite (first sprite in sheet) - characters are 2 tiles tall
            sprite_width = 32
            sprite_height = 64  # Characters are 2 tiles tall (32x64 pixels)
            self.sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            self.sprite.blit(spritesheet, (0, 0), pygame.Rect(0, 0, sprite_width, sprite_height))

            # Scale up for display (maintaining aspect ratio)
            self.sprite = pygame.transform.scale(self.sprite, (sprite_width * 4, sprite_height * 4))
        except Exception as e:
            print(f"Error loading character sprite {self.sprite_index}: {e}")
            # Create placeholder (matching the 4x scaled dimensions)
            self.sprite = pygame.Surface((128, 256))
            self.sprite.fill((100, 100, 200))


class CharacterSelect:
    """Character selection screen"""
    def __init__(self, screen_width=1536, screen_height=1024):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Character options
        self.characters = [
            CharacterOption("Alex", "", 1, "A determined young person ready to learn"),
            CharacterOption("Jordan", "", 2, "An optimistic student exploring the city"),
            CharacterOption("Taylor", "", 3, "A resourceful individual seeking opportunity"),
            CharacterOption("Casey", "", 4, "An ambitious worker building their future"),
            CharacterOption("Morgan", "", 5, "A thoughtful person navigating life's challenges"),
            CharacterOption("Riley", "", 6, "A creative soul finding their path"),
        ]

        self.selected_index = 0
        self.locked_index = None  # Track which character is locked/clicked
        self.animation_time = 0

        # Card positions
        self.card_width = 200
        self.card_height = 380  # Increased to accommodate taller sprites
        self.card_spacing = 40  # Back to original spacing
        self.cards_per_row = 3

        # Scrolling
        self.scroll_offset = 0
        self.max_scroll = 0  # Will be calculated
        self.scroll_speed = 30

        # Animation properties
        self.card_scales = [1.0] * len(self.characters)
        self.card_hover_offsets = [0.0] * len(self.characters)

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.name_font = pygame.font.Font(None, 36)
        self.desc_font = pygame.font.Font(None, 20)
        self.button_font = pygame.font.Font(None, 32)

        # Confirm button
        self.confirm_button = pygame.Rect(
            screen_width // 2 - 150,
            screen_height - 120,
            300,
            60
        )
        self.confirm_hover = False
        self.confirm_scale = 1.0

        self.selected_character = None

    def get_card_rect(self, index):
        """Calculate the rect for a character card (with scroll offset applied)"""
        row = index // self.cards_per_row
        col = index % self.cards_per_row

        # Center the grid
        total_width = self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_spacing
        start_x = (self.screen_width - total_width) // 2
        start_y = 200

        x = start_x + col * (self.card_width + self.card_spacing)
        y = start_y + row * (self.card_height + self.card_spacing) - self.scroll_offset

        return pygame.Rect(x, y, self.card_width, self.card_height)

    def calculate_max_scroll(self):
        """Calculate the maximum scroll offset"""
        num_rows = (len(self.characters) + self.cards_per_row - 1) // self.cards_per_row
        total_height = num_rows * (self.card_height + self.card_spacing) + 200  # Start position

        # Max scroll is content height minus visible area (leaving room for button and instructions)
        visible_area = self.screen_height - 200  # Leave room at bottom for button
        self.max_scroll = max(0, total_height - visible_area)

    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()

            # Check card hovers - only change selection if nothing is locked
            if self.locked_index is None:
                for i in range(len(self.characters)):
                    card_rect = self.get_card_rect(i)
                    if card_rect.collidepoint(mouse_pos):
                        self.selected_index = i

            # Check confirm button hover
            self.confirm_hover = self.confirm_button.collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll up/down with mouse wheel
            self.scroll_offset -= event.y * self.scroll_speed
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if clicked on a card - this locks the selection
            for i in range(len(self.characters)):
                card_rect = self.get_card_rect(i)
                if card_rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    self.locked_index = i  # Lock this selection
                    break

            # Check confirm button
            if self.confirm_button.collidepoint(mouse_pos):
                # Use locked selection if available, otherwise fall back to selected_index
                final_index = self.locked_index if self.locked_index is not None else self.selected_index
                self.selected_character = self.characters[final_index]
                return 'character_selected'

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Use locked selection if available, otherwise fall back to selected_index
                final_index = self.locked_index if self.locked_index is not None else self.selected_index
                self.selected_character = self.characters[final_index]
                return 'character_selected'
            elif event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.characters)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.characters)
            elif event.key == pygame.K_UP:
                # Navigate up or scroll up if shift is held
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                else:
                    self.selected_index = (self.selected_index - self.cards_per_row) % len(self.characters)
            elif event.key == pygame.K_DOWN:
                # Navigate down or scroll down if shift is held
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
                else:
                    self.selected_index = (self.selected_index + self.cards_per_row) % len(self.characters)
            elif event.key == pygame.K_ESCAPE:
                return 'back_to_menu'

        return None

    def update_animations(self, dt):
        """Update animation values"""
        self.animation_time += dt

        # Update card animations
        for i in range(len(self.characters)):
            # Highlight both hovered and locked characters
            is_selected = (i == self.selected_index) or (i == self.locked_index)

            # Scale animation
            target_scale = 1.1 if is_selected else 1.0
            self.card_scales[i] += (target_scale - self.card_scales[i]) * 0.15

            # Hover offset (floating effect)
            if is_selected:
                self.card_hover_offsets[i] = math.sin(self.animation_time * 3) * 8
            else:
                self.card_hover_offsets[i] *= 0.9

        # Confirm button animation
        target_confirm_scale = 1.1 if self.confirm_hover else 1.0
        self.confirm_scale += (target_confirm_scale - self.confirm_scale) * 0.15

    def draw(self, screen):
        """Draw the character selection screen"""
        # Background
        screen.fill((30, 30, 40))

        # Calculate scrolling limits
        self.calculate_max_scroll()

        # Update animations
        self.update_animations(0.016)

        # Draw animated background pattern
        for i in range(20):
            x = (i * 80 + self.animation_time * 20) % self.screen_width
            for j in range(15):
                y = j * 80
                alpha = int(20 + math.sin(self.animation_time + i + j) * 10)
                color = (50, 50, 60, alpha)
                surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                surf.fill(color)
                screen.blit(surf, (x, y))

        # Title
        title_text = self.title_font.render("Choose Your Character", True, (255, 255, 255))
        title_glow = self.title_font.render("Choose Your Character", True, (100, 150, 255))

        title_x = self.screen_width // 2 - title_text.get_width() // 2
        title_y = 60

        # Glow effect
        screen.blit(title_glow, (title_x + 2, title_y + 2))
        screen.blit(title_text, (title_x, title_y))

        # Draw character cards
        for i, character in enumerate(self.characters):
            card_rect = self.get_card_rect(i)
            # Highlight both hovered and locked characters
            is_selected = (i == self.selected_index) or (i == self.locked_index)

            scale = self.card_scales[i]
            offset = self.card_hover_offsets[i]

            # Calculate scaled dimensions
            scaled_width = int(card_rect.width * scale)
            scaled_height = int(card_rect.height * scale)
            scaled_x = card_rect.centerx - scaled_width // 2
            scaled_y = card_rect.centery - scaled_height // 2 - int(offset)

            # Draw glow for selected card
            if is_selected:
                for j in range(3):
                    glow_scale = scale + 0.03 * (j + 1)
                    glow_width = int(card_rect.width * glow_scale)
                    glow_height = int(card_rect.height * glow_scale)
                    glow_x = card_rect.centerx - glow_width // 2
                    glow_y = card_rect.centery - glow_height // 2 - int(offset)

                    glow_alpha = 30 - j * 8
                    glow_surf = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
                    glow_surf.fill((100, 150, 255, glow_alpha))
                    screen.blit(glow_surf, (glow_x, glow_y))

            # Card background
            card_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            if is_selected:
                pygame.draw.rect(card_surf, (60, 70, 90), (0, 0, scaled_width, scaled_height), border_radius=15)
                pygame.draw.rect(card_surf, (100, 150, 255), (0, 0, scaled_width, scaled_height), 3, border_radius=15)
            else:
                pygame.draw.rect(card_surf, (50, 55, 70), (0, 0, scaled_width, scaled_height), border_radius=15)
                pygame.draw.rect(card_surf, (80, 80, 100), (0, 0, scaled_width, scaled_height), 2, border_radius=15)

            screen.blit(card_surf, (scaled_x, scaled_y))

            # Character sprite
            if character.sprite:
                sprite_x = scaled_x + scaled_width // 2 - character.sprite.get_width() // 2
                sprite_y = scaled_y + 15  # Position at top of card
                screen.blit(character.sprite, (sprite_x, sprite_y))

            # Character name
            name_text = self.name_font.render(character.name, True, (255, 255, 255))
            name_x = scaled_x + scaled_width // 2 - name_text.get_width() // 2
            name_y = scaled_y + 280  # Position below the taller sprite
            screen.blit(name_text, (name_x, name_y))

            # Description (wrapped)
            desc_words = character.description.split()
            lines = []
            current_line = []
            for word in desc_words:
                test_line = ' '.join(current_line + [word])
                test_surf = self.desc_font.render(test_line, True, (200, 200, 200))
                if test_surf.get_width() <= scaled_width - 20:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            desc_y = scaled_y + 315  # Position below the name
            for line in lines:
                line_surf = self.desc_font.render(line, True, (200, 200, 200))
                line_x = scaled_x + scaled_width // 2 - line_surf.get_width() // 2
                screen.blit(line_surf, (line_x, desc_y))
                desc_y += 22  # Reduced line spacing from 25

        # Confirm button
        button_width = int(self.confirm_button.width * self.confirm_scale)
        button_height = int(self.confirm_button.height * self.confirm_scale)
        button_x = self.confirm_button.centerx - button_width // 2
        button_y = self.confirm_button.centery - button_height // 2

        # Button glow
        if self.confirm_hover:
            for i in range(3):
                glow_scale = self.confirm_scale + 0.05 * (i + 1)
                glow_w = int(self.confirm_button.width * glow_scale)
                glow_h = int(self.confirm_button.height * glow_scale)
                glow_x = self.confirm_button.centerx - glow_w // 2
                glow_y = self.confirm_button.centery - glow_h // 2

                glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
                glow_surf.fill((100, 255, 100, 30 - i * 8))
                screen.blit(glow_surf, (glow_x, glow_y))

        # Button background
        button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        if self.confirm_hover:
            pygame.draw.rect(button_surf, (50, 200, 50), (0, 0, button_width, button_height), border_radius=10)
            pygame.draw.rect(button_surf, (100, 255, 100), (0, 0, button_width, button_height), 3, border_radius=10)
        else:
            pygame.draw.rect(button_surf, (40, 120, 40), (0, 0, button_width, button_height), border_radius=10)
            pygame.draw.rect(button_surf, (80, 180, 80), (0, 0, button_width, button_height), 2, border_radius=10)

        screen.blit(button_surf, (button_x, button_y))

        # Button text
        button_text = self.button_font.render("Start Adventure", True, (255, 255, 255))
        text_x = button_x + button_width // 2 - button_text.get_width() // 2
        text_y = button_y + button_height // 2 - button_text.get_height() // 2
        screen.blit(button_text, (text_x, text_y))

        # Draw scrollbar if content is scrollable
        if self.max_scroll > 0:
            scrollbar_x = self.screen_width - 20
            scrollbar_y = 160
            scrollbar_height = 400

            # Scrollbar background
            pygame.draw.rect(screen, (60, 60, 70), (scrollbar_x, scrollbar_y, 10, scrollbar_height), border_radius=5)

            # Scrollbar handle
            handle_height = max(30, int(scrollbar_height * (scrollbar_height / (scrollbar_height + self.max_scroll))))
            handle_y = scrollbar_y + int((scrollbar_height - handle_height) * (self.scroll_offset / self.max_scroll))

            pygame.draw.rect(screen, (100, 150, 255), (scrollbar_x, handle_y, 10, handle_height), border_radius=5)

            # Scroll hint text
            hint_font = pygame.font.Font(None, 18)
            hint_text = hint_font.render("Scroll with Mouse Wheel", True, (150, 150, 150))
            screen.blit(hint_text, (self.screen_width - 180, scrollbar_y + scrollbar_height + 10))

        # Instructions
        inst_font = pygame.font.Font(None, 20)
        inst_text = inst_font.render("Arrow Keys/Mouse to select • Mouse Wheel/Shift+Arrows to scroll • ENTER/Click to confirm • ESC to go back", True, (150, 150, 150))
        inst_x = self.screen_width // 2 - inst_text.get_width() // 2
        screen.blit(inst_text, (inst_x, self.screen_height - 40))

    def reset(self):
        """Reset the character selection"""
        self.selected_index = 0
        self.locked_index = None  # Reset locked selection
        self.selected_character = None
        self.animation_time = 0
        self.scroll_offset = 0
