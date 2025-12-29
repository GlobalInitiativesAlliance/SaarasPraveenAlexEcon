"""
Backpack Investigation Activity - Professional Version
Discovering lost belongings with high-quality graphics and animations
"""
import pygame
import random
import math
import os
import time
from src.activities.activities import Activity

class BackpackInvestigation(Activity):
    """Professional backpack investigation with real sprites and animations"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)  # Call parent Activity init
        self.narrative_ref = None  # Set by parent interior
        self.start_time = time.time()

        # Screen dimensions
        self.SCREEN_WIDTH = 1024
        self.SCREEN_HEIGHT = 768

        # Professional scene composition
        self.SCENE_WIDTH = 800
        self.SCENE_HEIGHT = 600
        self.scene_x = (self.SCREEN_WIDTH - self.SCENE_WIDTH) // 2
        self.scene_y = (self.SCREEN_HEIGHT - self.SCENE_HEIGHT) // 2

        # Backpack centered position
        self.backpack_x = self.scene_x + self.SCENE_WIDTH // 2 - 150
        self.backpack_y = self.scene_y + 120
        self.backpack_width = 300
        self.backpack_height = 280

        # Animation states
        self.pocket_glow = 0
        self.glow_direction = 1
        self.zipper_animation = 0
        self.opening_pocket = None
        self.item_float_offset = {}

        # Load sprites
        self.load_sprites()

        # Pockets with better positioning
        self.pockets = {
            'main': {
                'rect': pygame.Rect(self.backpack_x + 75, self.backpack_y + 100, 150, 120),
                'searched': False,
                'label': 'Main Compartment',
                'opening': False
            },
            'top': {
                'rect': pygame.Rect(self.backpack_x + 100, self.backpack_y + 30, 100, 50),
                'searched': False,
                'label': 'Top Pocket',
                'opening': False
            },
            'left': {
                'rect': pygame.Rect(self.backpack_x + 20, self.backpack_y + 120, 50, 80),
                'searched': False,
                'label': 'Side',
                'opening': False
            },
            'right': {
                'rect': pygame.Rect(self.backpack_x + 230, self.backpack_y + 120, 50, 80),
                'searched': False,
                'label': 'Side',
                'opening': False
            }
        }

        # Items with better organization
        self.items_present = [
            {'name': 'Notebook', 'pocket': 'main', 'sprite_pos': (0, 0), 'found': False},
            {'name': 'Pen', 'pocket': 'top', 'sprite_pos': (1, 0), 'found': False},
            {'name': 'Shelter Card', 'pocket': 'main', 'sprite_pos': (2, 0), 'found': False},
            {'name': 'Bus Pass', 'pocket': 'left', 'sprite_pos': (3, 0), 'found': False},
            {'name': 'Snack', 'pocket': 'right', 'sprite_pos': (4, 0), 'found': False}
        ]

        self.items_missing = [
            {
                'name': 'Work Uniform',
                'pocket': 'main',
                'sprite_pos': (5, 0),
                'location': "Mike's bathroom",
                'consequence': "Can't work = No income",
                'discovered': False
            },
            {
                'name': 'Phone Charger',
                'pocket': 'top',
                'sprite_pos': (6, 0),
                'location': "Sarah's couch",
                'consequence': "Phone dying = Can't call for help",
                'discovered': False
            },
            {
                'name': 'Toothbrush',
                'pocket': 'left',
                'sprite_pos': (7, 0),
                'location': "Alex's sink",
                'consequence': "No hygiene = Health issues",
                'discovered': False
            },
            {
                'name': 'ID Card',
                'pocket': 'right',
                'sprite_pos': (8, 0),
                'location': "Lost in chaos",
                'consequence': "No ID = Can't prove identity",
                'discovered': False
            }
        ]

        # Game state
        self.stress_level = 20
        self.phone_battery = 12
        self.current_realization = None
        self.realization_timer = 0
        self.show_consequences = False
        self.completion_timer = 0

        # Colors (professional palette)
        self.BG_COLOR = (25, 22, 20)
        self.PANEL_COLOR = (45, 40, 35)
        self.BORDER_COLOR = (80, 70, 60)
        self.TEXT_COLOR = (220, 200, 180)
        self.ACCENT_COLOR = (200, 170, 120)
        self.WARNING_COLOR = (180, 60, 60)
        self.SUCCESS_COLOR = (60, 140, 60)

    def load_sprites(self):
        """Load actual sprites from game assets"""
        # For now, we'll create placeholder sprites
        # In production, load from assets/moderninteriors/
        self.sprites = {}

        # Create simple colored rectangles as placeholders for sprites
        sprite_size = 48
        colors = {
            'notebook': (100, 120, 140),
            'pen': (60, 60, 80),
            'shelter_card': (200, 180, 160),
            'bus_pass': (180, 200, 100),
            'snack': (160, 120, 80),
            'uniform': (100, 100, 180),
            'charger': (80, 80, 80),
            'toothbrush': (100, 180, 200),
            'id': (200, 200, 100)
        }

        for name, color in colors.items():
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, color, (0, 0, sprite_size, sprite_size), 0, 5)
            pygame.draw.rect(sprite, (color[0]//2, color[1]//2, color[2]//2),
                           (0, 0, sprite_size, sprite_size), 2, 5)
            self.sprites[name] = sprite

    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check pocket clicks
            for pocket_name, pocket_data in self.pockets.items():
                if pocket_data['rect'].collidepoint(mouse_pos) and not pocket_data['searched']:
                    self.search_pocket(pocket_name)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print(f"[BACKPACK] ESC in handle_event - completing activity")
                self.complete_activity()

    def handle_mouse_click(self, pos, button):
        """Handle mouse click for compatibility"""
        if not self.active:
            return

        for pocket_name, pocket_data in self.pockets.items():
            if pocket_data['rect'].collidepoint(pos) and not pocket_data['searched']:
                self.search_pocket(pocket_name)

    def handle_key(self, key):
        """Handle key press"""
        if not self.active:
            return

        if key == pygame.K_ESCAPE:
            print(f"[BACKPACK] ESC pressed - completing activity early (searched: {self.all_pockets_searched()})")
            # Allow ESC to exit even if not all pockets searched
            self.complete_activity()

    def handle_mouse_motion(self, pos):
        """Handle mouse hover effects"""
        pass

    def handle_mouse_release(self, pos, button):
        """Handle mouse release"""
        pass

    def handle_text_input(self, text):
        """Handle text input - not used in this activity but required for compatibility"""
        pass

    def start(self):
        """Start the backpack investigation activity"""
        super().start()  # This sets self.active = True
        self.start_time = time.time()
        print("[BACKPACK] Activity started successfully")

    def search_pocket(self, pocket_name):
        """Search a pocket with animation"""
        pocket = self.pockets[pocket_name]
        pocket['searched'] = True
        pocket['opening'] = True
        self.opening_pocket = pocket_name
        self.zipper_animation = 0

        # Find items in this pocket
        for item in self.items_present:
            if item['pocket'] == pocket_name:
                item['found'] = True

        # Check for missing items
        for item in self.items_missing:
            if item['pocket'] == pocket_name and not item['discovered']:
                item['discovered'] = True
                self.trigger_realization(item)
                self.stress_level = min(100, self.stress_level + 20)
                if item['name'] == 'Phone Charger':
                    self.phone_battery = max(0, self.phone_battery - 3)

        # Auto-complete when all pockets are searched
        if self.all_pockets_searched():
            self.complete_activity()

    def trigger_realization(self, item):
        """Trigger realization animation"""
        self.current_realization = item
        self.realization_timer = 180

    def all_pockets_searched(self):
        """Check if all pockets searched"""
        return all(pocket['searched'] for pocket in self.pockets.values())

    def complete_activity(self):
        """Complete the activity"""
        # Update narrative ref state if available
        if self.narrative_ref:
            if hasattr(self.narrative_ref, 'backpack_investigation_complete'):
                self.narrative_ref.backpack_investigation_complete = True

        # Show completion message through narrative dialogue
        if self.narrative_ref and hasattr(self.narrative_ref, 'dialogue_box'):
            msg = "You check your backpack and realize how much you've lost while couch surfing. "
            msg += "Phone charger, work uniform, small belongings... all scattered across different places."
            self.narrative_ref.dialogue_box.show(None, msg)

        # Complete the activity using parent method
        self.complete()

    def update(self, dt):
        """Update animations and state"""
        # Continue updating if showing consequences, even if not active
        if not self.active and not self.show_consequences:
            return

        # Update glow animation
        self.pocket_glow += self.glow_direction * 2
        if self.pocket_glow >= 30 or self.pocket_glow <= 0:
            self.glow_direction *= -1

        # Update zipper animation
        if self.opening_pocket:
            self.zipper_animation = min(1.0, self.zipper_animation + dt * 3)
            if self.zipper_animation >= 1.0:
                self.opening_pocket = None

        # Update realization timer
        if self.realization_timer > 0:
            self.realization_timer -= 1

        # Update phone battery drain
        if random.random() < 0.005:
            self.phone_battery = max(0, self.phone_battery - 1)

        # Handle completion
        if self.show_consequences and self.completion_timer > 0:
            self.completion_timer -= 1
            if self.completion_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw professional investigation interface"""
        if not self.active and not self.show_consequences:
            return

        # Semi-transparent background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 30, 200))
        screen.blit(overlay, (0, 0))

        # Main panel
        panel = pygame.Surface((self.SCENE_WIDTH, self.SCENE_HEIGHT), pygame.SRCALPHA)
        panel.fill((*self.PANEL_COLOR, 240))

        # Panel border
        pygame.draw.rect(panel, self.BORDER_COLOR, panel.get_rect(), 3, 10)

        # Title
        self.draw_title(panel)

        # Draw backpack
        self.draw_backpack(panel)

        # Draw pockets with glow
        self.draw_pockets(panel)

        # Draw item grids
        self.draw_item_grid(panel)

        # Draw status elements
        self.draw_status_bar(panel)

        # Draw realization if active
        if self.current_realization and self.realization_timer > 0:
            self.draw_realization(panel)

        # Draw consequences if showing
        if self.show_consequences:
            self.draw_consequences_panel(panel)

        # Blit panel to screen
        screen.blit(panel, (self.scene_x, self.scene_y))

    def draw_title(self, panel):
        """Draw scene title"""
        font = pygame.font.Font(None, 36)
        title = "Checking Your Belongings"
        title_surf = font.render(title, True, self.TEXT_COLOR)
        title_rect = title_surf.get_rect(centerx=self.SCENE_WIDTH // 2, y=20)
        panel.blit(title_surf, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 20)
        subtitle = "What did you lose while couch surfing?"
        subtitle_surf = subtitle_font.render(subtitle, True, self.ACCENT_COLOR)
        subtitle_rect = subtitle_surf.get_rect(centerx=self.SCENE_WIDTH // 2, y=55)
        panel.blit(subtitle_surf, subtitle_rect)

    def draw_backpack(self, panel):
        """Draw professional backpack visual"""
        # Adjust coordinates for panel
        x = self.backpack_x - self.scene_x
        y = self.backpack_y - self.scene_y

        # Main backpack shape
        backpack_color = (55, 50, 65)
        highlight_color = (75, 70, 85)
        shadow_color = (35, 30, 45)

        # Shadow
        shadow_points = [
            (x + 15, y + 35), (x + 285, y + 35),
            (x + 285, y + 285), (x + 15, y + 285)
        ]
        pygame.draw.polygon(panel, shadow_color, shadow_points)

        # Main body
        main_points = [
            (x + 30, y + 20), (x + 270, y + 20),
            (x + 280, y + 50), (x + 280, y + 250),
            (x + 270, y + 270), (x + 30, y + 270),
            (x + 20, y + 250), (x + 20, y + 50)
        ]
        pygame.draw.polygon(panel, backpack_color, main_points)

        # Highlight
        pygame.draw.lines(panel, highlight_color, False,
                         [(x + 30, y + 20), (x + 270, y + 20), (x + 280, y + 50)], 2)

        # Zipper line
        zipper_color = (140, 140, 140)
        if self.zipper_animation > 0:
            # Animated zipper opening
            zipper_y = y + 80 + (self.zipper_animation * 120)
            pygame.draw.line(panel, zipper_color, (x + 150, y + 80), (x + 150, zipper_y), 3)
            # Zipper pull
            pygame.draw.circle(panel, (180, 180, 180), (x + 150, int(zipper_y)), 6)
        else:
            pygame.draw.line(panel, zipper_color, (x + 150, y + 80), (x + 150, y + 200), 3)
            pygame.draw.circle(panel, (160, 160, 160), (x + 150, y + 140), 5)

        # Straps
        strap_color = (45, 40, 55)
        pygame.draw.lines(panel, strap_color, False,
                         [(x + 80, y + 5), (x + 70, y + 60), (x + 80, y + 100)], 5)
        pygame.draw.lines(panel, strap_color, False,
                         [(x + 220, y + 5), (x + 230, y + 60), (x + 220, y + 100)], 5)

    def draw_pockets(self, panel):
        """Draw interactive pocket zones"""
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse = (mouse_pos[0] - self.scene_x, mouse_pos[1] - self.scene_y)

        for pocket_name, pocket_data in self.pockets.items():
            # Adjust rect for panel coordinates
            rect = pygame.Rect(
                pocket_data['rect'].x - self.scene_x,
                pocket_data['rect'].y - self.scene_y,
                pocket_data['rect'].width,
                pocket_data['rect'].height
            )

            if pocket_data['searched']:
                # Open pocket visual
                pygame.draw.rect(panel, (30, 30, 40), rect, 0, 5)
                pygame.draw.rect(panel, (60, 60, 70), rect, 2, 5)
            else:
                # Hovering effect
                if rect.collidepoint(adjusted_mouse):
                    # Glowing border
                    glow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
                    glow_color = (*self.ACCENT_COLOR, 30 + self.pocket_glow)
                    pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), 0, 8)
                    panel.blit(glow_surf, (rect.x - 5, rect.y - 5))

                    # Cursor hint
                    font = pygame.font.Font(None, 16)
                    hint = f"Click to search {pocket_data['label']}"
                    hint_surf = font.render(hint, True, self.ACCENT_COLOR)
                    panel.blit(hint_surf, (rect.x, rect.y - 20))

                # Subtle outline
                pygame.draw.rect(panel, (*self.ACCENT_COLOR, 100), rect, 1, 5)

    def draw_item_grid(self, panel):
        """Draw organized item display"""
        # Found items section
        found_x = 50
        found_y = 320

        font_title = pygame.font.Font(None, 24)
        font_item = pygame.font.Font(None, 18)

        # Found header
        found_title = font_title.render("Found:", True, self.SUCCESS_COLOR)
        panel.blit(found_title, (found_x, found_y - 30))

        # Draw found items
        for i, item in enumerate(self.items_present):
            if item['found']:
                item_y = found_y + (i * 35)
                # Item sprite placeholder
                sprite_rect = pygame.Rect(found_x, item_y, 30, 30)
                pygame.draw.rect(panel, self.SUCCESS_COLOR, sprite_rect, 0, 3)
                # Item name
                name_surf = font_item.render(item['name'], True, self.TEXT_COLOR)
                panel.blit(name_surf, (found_x + 40, item_y + 7))

        # Missing items section
        missing_x = self.SCENE_WIDTH - 250
        missing_y = 320

        # Missing header
        missing_title = font_title.render("Missing:", True, self.WARNING_COLOR)
        panel.blit(missing_title, (missing_x, missing_y - 30))

        # Draw missing items
        for i, item in enumerate(self.items_missing):
            if item['discovered']:
                item_y = missing_y + (i * 35)
                # Ghost sprite
                sprite_rect = pygame.Rect(missing_x, item_y, 30, 30)
                ghost_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.rect(ghost_surf, (*self.WARNING_COLOR, 80), (0, 0, 30, 30), 0, 3)
                panel.blit(ghost_surf, sprite_rect)
                # Red X
                pygame.draw.line(panel, self.WARNING_COLOR,
                               (missing_x + 5, item_y + 5),
                               (missing_x + 25, item_y + 25), 2)
                pygame.draw.line(panel, self.WARNING_COLOR,
                               (missing_x + 25, item_y + 5),
                               (missing_x + 5, item_y + 25), 2)
                # Item name
                name_surf = font_item.render(item['name'], True, self.WARNING_COLOR)
                panel.blit(name_surf, (missing_x + 40, item_y + 7))

    def draw_status_bar(self, panel):
        """Draw status information"""
        bar_y = self.SCENE_HEIGHT - 80

        font = pygame.font.Font(None, 20)

        # Stress meter
        stress_rect = pygame.Rect(50, bar_y, 200, 20)
        pygame.draw.rect(panel, (60, 20, 20), stress_rect, 0, 3)
        fill_width = int((self.stress_level / 100) * 200)
        pygame.draw.rect(panel, self.WARNING_COLOR, (50, bar_y, fill_width, 20), 0, 3)
        pygame.draw.rect(panel, self.BORDER_COLOR, stress_rect, 2, 3)
        stress_text = font.render(f"Stress: {self.stress_level}%", True, self.TEXT_COLOR)
        panel.blit(stress_text, (55, bar_y + 2))

        # Phone battery
        battery_x = self.SCENE_WIDTH - 250
        battery_rect = pygame.Rect(battery_x, bar_y, 100, 20)
        pygame.draw.rect(panel, (20, 20, 20), battery_rect, 0, 3)
        battery_fill = int((self.phone_battery / 100) * 100)
        battery_color = self.WARNING_COLOR if self.phone_battery < 20 else (100, 180, 100)
        pygame.draw.rect(panel, battery_color, (battery_x, bar_y, battery_fill, 20), 0, 3)
        pygame.draw.rect(panel, self.BORDER_COLOR, battery_rect, 2, 3)
        battery_text = font.render(f"Phone: {self.phone_battery}%", True, self.TEXT_COLOR)
        panel.blit(battery_text, (battery_x + 5, bar_y + 2))

        # Instructions
        inst_y = bar_y + 35
        instruction = "Click pockets to search"
        inst_surf = font.render(instruction, True, self.ACCENT_COLOR)
        inst_rect = inst_surf.get_rect(centerx=self.SCENE_WIDTH // 2, y=inst_y)
        panel.blit(inst_surf, inst_rect)

    def draw_realization(self, panel):
        """Draw realization overlay"""
        if self.realization_timer > 120:
            alpha = min(200, (180 - self.realization_timer) * 10)
        else:
            alpha = min(200, self.realization_timer * 2)

        # Realization box
        box_width = 500
        box_height = 120
        box_x = (self.SCENE_WIDTH - box_width) // 2
        box_y = 200

        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surf.fill((*self.BG_COLOR, alpha))
        pygame.draw.rect(box_surf, (*self.WARNING_COLOR, alpha), box_surf.get_rect(), 3, 10)

        font_title = pygame.font.Font(None, 28)
        font_text = pygame.font.Font(None, 20)

        # Item name
        title = f"Missing: {self.current_realization['name']}"
        title_surf = font_title.render(title, True, self.WARNING_COLOR)
        title_rect = title_surf.get_rect(centerx=box_width // 2, y=15)
        box_surf.blit(title_surf, title_rect)

        # Location
        location = f"Left at: {self.current_realization['location']}"
        location_surf = font_text.render(location, True, self.TEXT_COLOR)
        location_rect = location_surf.get_rect(centerx=box_width // 2, y=50)
        box_surf.blit(location_surf, location_rect)

        # Consequence
        consequence = self.current_realization['consequence']
        consequence_surf = font_text.render(consequence, True, self.ACCENT_COLOR)
        consequence_rect = consequence_surf.get_rect(centerx=box_width // 2, y=80)
        box_surf.blit(consequence_surf, consequence_rect)

        panel.blit(box_surf, (box_x, box_y))

    def draw_consequences_panel(self, panel):
        """Draw final consequences"""
        # Dark overlay
        overlay = pygame.Surface((self.SCENE_WIDTH, self.SCENE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 220))
        panel.blit(overlay, (0, 0))

        font_title = pygame.font.Font(None, 42)
        font_subtitle = pygame.font.Font(None, 28)
        font_text = pygame.font.Font(None, 22)

        # Title
        title = "The Cost of Instability"
        title_surf = font_title.render(title, True, self.WARNING_COLOR)
        title_rect = title_surf.get_rect(centerx=self.SCENE_WIDTH // 2, y=100)
        panel.blit(title_surf, title_rect)

        # List consequences
        y_offset = 200
        for item in self.items_missing:
            if item['discovered']:
                # Item and consequence
                text = f"{item['name']}: {item['consequence']}"
                text_surf = font_text.render(text, True, self.TEXT_COLOR)
                text_rect = text_surf.get_rect(centerx=self.SCENE_WIDTH // 2, y=y_offset)
                panel.blit(text_surf, text_rect)
                y_offset += 40

        # Bottom message
        message = "You're not just losing things..."
        message_surf = font_subtitle.render(message, True, self.ACCENT_COLOR)
        message_rect = message_surf.get_rect(centerx=self.SCENE_WIDTH // 2, y=420)
        panel.blit(message_surf, message_rect)

        message2 = "You're losing pieces of yourself."
        message2_surf = font_subtitle.render(message2, True, self.TEXT_COLOR)
        message2_rect = message2_surf.get_rect(centerx=self.SCENE_WIDTH // 2, y=460)
        panel.blit(message2_surf, message2_rect)