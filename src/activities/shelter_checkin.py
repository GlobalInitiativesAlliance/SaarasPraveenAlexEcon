"""
Emergency Shelter Check-In Mini-Game
Following exact pattern from ClothesPacking, PhotoSelection, and DocumentSearch
"""
import pygame
import math
import random
import os
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class EmergencyShelterCheckIn(Activity):
    """Emergency shelter intake process with 3 phases"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None  # CRITICAL: Set by parent interior

        # Phase management (1=intake, 2=rules, 3=bed selection)
        self.current_phase = 1
        self.phase_complete = {1: False, 2: False, 3: False}

        # Phase 1: Intake form
        self.form_fields = {
            "name": {"value": "", "rect": None, "filled": False},
            "age": {"value": "", "rect": None, "filled": False},
            "last_address": {"value": "Foster Home", "rect": None, "filled": False},
            "emergency_contact": {"value": "", "rect": None, "filled": False}
        }
        self.active_field = None

        # Phase 2: Rules
        self.shelter_rules = [
            {"text": "No weapons or drugs allowed", "acknowledged": False, "rect": None},
            {"text": "Curfew at 9 PM sharp - no exceptions", "acknowledged": False, "rect": None},
            {"text": "Wake up at 5 AM for morning count", "acknowledged": False, "rect": None},
            {"text": "No guests or visitors permitted", "acknowledged": False, "rect": None},
            {"text": "Mandatory chore assignments", "acknowledged": False, "rect": None},
            {"text": "30-day maximum stay limit", "acknowledged": False, "rect": None}
        ]

        # Phase 3: Bed assignment
        self.total_beds = 40
        self.available_beds = [12, 23, 31, 38, 40]  # Only these are free
        self.bed_info = {
            12: {"desc": "Near bathroom", "quality": "noisy", "rect": None},
            23: {"desc": "By the door", "quality": "cold", "rect": None},
            31: {"desc": "Corner bed", "quality": "safer", "rect": None},
            38: {"desc": "Middle row", "quality": "no privacy", "rect": None},
            40: {"desc": "Near staff desk", "quality": "monitored", "rect": None}
        }
        self.selected_bed = None
        self.bed_rects = {}  # Store bed rectangles for click detection

        # Visual elements
        self.animation_timer = 0
        self.hover_element = None
        self.shake_timer = 0  # For emotional moments
        self.continue_button_rect = None

        # Load textures
        self.load_all_textures()

    def load_all_textures(self):
        """Load ALL real textures - NO FALLBACKS"""

        # Character sprites for other shelter residents
        self.character_sprites = {}
        character_files = {
            "shelter_worker": "assets/moderninteriors-win/2_Characters/Character_Generator/0_Premade_Characters/16x16/Premade_Character_15.png",
            "resident_1": "assets/moderninteriors-win/2_Characters/Character_Generator/0_Premade_Characters/16x16/Premade_Character_08.png",
            "resident_2": "assets/moderninteriors-win/2_Characters/Character_Generator/0_Premade_Characters/16x16/Premade_Character_19.png",
            "resident_3": "assets/moderninteriors-win/2_Characters/Character_Generator/0_Premade_Characters/16x16/Premade_Character_11.png",
            "resident_4": "assets/moderninteriors-win/2_Characters/Character_Generator/0_Premade_Characters/16x16/Premade_Character_20.png"
        }

        for name, path in character_files.items():
            size = (64, 64) if name == "shelter_worker" else (48, 48)
            self.character_sprites[name] = self.load_sprite(path, size)

        # Bed textures - use actual bed sprites
        bed_files = {
            "occupied": "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter_Shadowless_Singles/4_Bedroom_Singles_Shadowless/Bedroom_Singles_Shadowless_11.png",
            "available": "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter_Shadowless_Singles/4_Bedroom_Singles_Shadowless/Bedroom_Singles_Shadowless_10.png",
            "selected": "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter_Shadowless_Singles/4_Bedroom_Singles_Shadowless/Bedroom_Singles_Shadowless_12.png"
        }

        self.bed_textures = {}
        for name, path in bed_files.items():
            self.bed_textures[name] = self.load_sprite(path, (60, 80))

        # Office/desk textures for intake
        self.desk_texture = self.load_sprite(
            "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter_Shadowless_Singles/18_Office_Singles_Shadowless/Office_Singles_Shadowless_49.png",
            (120, 80)
        )

        # Clipboard/form texture
        self.clipboard_texture = self.load_sprite(
            "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter_Shadowless_Singles/18_Office_Singles_Shadowless/Office_Singles_Shadowless_384.png",
            (80, 100)
        )

    def load_sprite(self, path, size):
        """Load and scale sprite - MUST work, no fallback"""
        try:
            sprite = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(sprite, size)
        except:
            # Create error texture that makes it obvious something's wrong
            error_surf = pygame.Surface(size, pygame.SRCALPHA)
            error_surf.fill((255, 0, 255, 100))  # Magenta = missing texture
            # Draw X to indicate missing
            pygame.draw.line(error_surf, (255, 255, 255), (0, 0), size, 2)
            pygame.draw.line(error_surf, (255, 255, 255), (0, size[1]), (size[0], 0), 2)
            return error_surf

    def start(self):
        """Start the shelter check-in activity"""
        super().start()
        self.current_phase = 1
        self.animation_timer = 0

    def draw(self, screen):
        """Main draw following exact overlay pattern"""
        if not self.active:
            return

        # Dark overlay (EXACT same as other mini-games)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Update animation
        self.animation_timer += 0.016

        # Main container (EXACT same styling)
        container_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (40, 35, 30), container_rect)
        pygame.draw.rect(screen, (200, 180, 160), container_rect, 3)

        # Draw current phase
        if self.current_phase == 1:
            self.draw_phase1_intake(screen)
        elif self.current_phase == 2:
            self.draw_phase2_rules(screen)
        elif self.current_phase == 3:
            self.draw_phase3_beds(screen)

        # Continue button when phase complete
        if self.phase_complete[self.current_phase]:
            self.draw_continue_button(screen)

    def draw_phase1_intake(self, screen):
        """Draw intake form with real office textures"""

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Shelter Intake Form", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Draw desk with shelter worker
        desk_pos = (SCREEN_WIDTH // 2 - 60, 150)
        screen.blit(self.desk_texture, desk_pos)

        # Draw shelter worker behind desk
        worker_pos = (desk_pos[0] + 30, desk_pos[1] - 40)
        screen.blit(self.character_sprites["shelter_worker"], worker_pos)

        # Draw clipboard/form
        form_x = SCREEN_WIDTH // 2 - 200
        form_y = 280
        screen.blit(self.clipboard_texture, (form_x - 10, form_y - 10))

        # Form fields with typewriter font
        form_font = pygame.font.Font(None, 20)

        field_y = form_y + 20
        for field_name, field_data in self.form_fields.items():
            # Field label
            label = field_name.replace("_", " ").title() + ":"
            label_surf = form_font.render(label, True, (255, 255, 255))
            screen.blit(label_surf, (form_x, field_y))

            # Field box
            field_rect = pygame.Rect(form_x + 180, field_y - 2, 200, 25)
            field_data["rect"] = field_rect

            # Draw field background
            if field_data["filled"]:
                pygame.draw.rect(screen, (230, 230, 230), field_rect)
            else:
                pygame.draw.rect(screen, (255, 255, 255), field_rect)

            # Active field effect (blue border) or hover effect
            if self.active_field == field_name:
                pygame.draw.rect(screen, (100, 150, 255), field_rect, 3)
            elif self.hover_element == field_name:
                pygame.draw.rect(screen, (255, 220, 100), field_rect, 2)
            else:
                pygame.draw.rect(screen, (100, 100, 100), field_rect, 1)

            # Draw value with special handling for "None"
            if field_name == "emergency_contact" and field_data["value"] == "None":
                # Red color and shake for emotional impact
                value_color = (200, 50, 50)
                if self.shake_timer > 0:
                    shake_x = int(math.sin(self.shake_timer * 20) * 3)
                    value_surf = form_font.render(field_data["value"], True, value_color)
                    screen.blit(value_surf, (field_rect.x + 5 + shake_x, field_rect.y + 3))
                    self.shake_timer -= 0.016
                else:
                    value_surf = form_font.render(field_data["value"], True, value_color)
                    screen.blit(value_surf, (field_rect.x + 5, field_rect.y + 3))
            else:
                value_color = (0, 0, 0)
                value_surf = form_font.render(field_data["value"], True, value_color)
                screen.blit(value_surf, (field_rect.x + 5, field_rect.y + 3))

                # Draw blinking cursor if this field is active
                if self.active_field == field_name:
                    cursor_visible = (pygame.time.get_ticks() // 500) % 2  # Blink every 500ms
                    if cursor_visible:
                        cursor_x = field_rect.x + 5 + value_surf.get_width() + 2
                        pygame.draw.line(screen, (0, 0, 0),
                                       (cursor_x, field_rect.y + 5),
                                       (cursor_x, field_rect.y + 20), 2)

            field_y += 40

        # Instructions
        inst_font = pygame.font.Font(None, 22)
        if self.active_field:
            inst_text = "Type to edit field, press ENTER when done"
        else:
            inst_text = "Click a field to edit it, then type your information"
        inst_surf = inst_font.render(inst_text, True, (200, 180, 160))
        screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, 500))

        # Check if all fields are filled
        all_filled = all(field["filled"] for field in self.form_fields.values())
        self.phase_complete[1] = all_filled

    def draw_phase2_rules(self, screen):
        """Draw rules with checkboxes"""

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("SHELTER RULES - MUST ACKNOWLEDGE ALL", True, (255, 200, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        # Warning text
        warning_font = pygame.font.Font(None, 24)
        warning = warning_font.render("Violation of any rule results in immediate removal", True, (255, 100, 100))
        screen.blit(warning, (SCREEN_WIDTH // 2 - warning.get_width() // 2, 120))

        # Rules list
        rule_font = pygame.font.Font(None, 26)
        rule_y = 180

        for i, rule in enumerate(self.shelter_rules):
            # Checkbox
            checkbox_rect = pygame.Rect(180, rule_y, 24, 24)
            rule["rect"] = checkbox_rect

            if rule["acknowledged"]:
                pygame.draw.rect(screen, (100, 200, 100), checkbox_rect)
                # Draw checkmark
                pygame.draw.lines(screen, (255, 255, 255), False,
                                [(checkbox_rect.x + 4, checkbox_rect.y + 12),
                                 (checkbox_rect.x + 10, checkbox_rect.y + 18),
                                 (checkbox_rect.x + 20, checkbox_rect.y + 6)], 3)
            else:
                pygame.draw.rect(screen, (200, 100, 100), checkbox_rect)
                if self.hover_element == f"rule_{i}":
                    pygame.draw.rect(screen, (255, 220, 100), checkbox_rect, 2)

            pygame.draw.rect(screen, (50, 50, 50), checkbox_rect, 2)

            # Rule text
            text_color = (100, 255, 100) if rule["acknowledged"] else (255, 255, 255)
            rule_surf = rule_font.render(rule["text"], True, text_color)
            screen.blit(rule_surf, (checkbox_rect.x + 35, rule_y + 2))

            # Add emphasis to harsh rules
            if "5 AM" in rule["text"] or "9 PM" in rule["text"] or "30-day" in rule["text"]:
                emphasis_color = (255, 200, 100) if not rule["acknowledged"] else (100, 200, 100)
                pygame.draw.line(screen, emphasis_color,
                               (checkbox_rect.x + 35, rule_y + 25),
                               (checkbox_rect.x + 35 + rule_surf.get_width(), rule_y + 25), 1)

            rule_y += 50

        # Check if all rules acknowledged
        all_acknowledged = all(rule["acknowledged"] for rule in self.shelter_rules)
        self.phase_complete[2] = all_acknowledged

        # Bottom text
        if not all_acknowledged:
            inst_font = pygame.font.Font(None, 22)
            inst_text = "You must acknowledge all rules to proceed"
            inst_surf = inst_font.render(inst_text, True, (255, 200, 150))
            screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, 520))

    def draw_phase3_beds(self, screen):
        """Draw shelter layout with actual bed sprites"""

        # Title
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("Choose Your Bed (Only 5 Available)", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Subtitle
        sub_font = pygame.font.Font(None, 22)
        subtitle = sub_font.render("Hover over available beds to see details", True, (200, 180, 160))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 105))

        # Draw shelter floor (grid of beds)
        start_x = 140
        start_y = 150
        bed_spacing_x = 75
        bed_spacing_y = 95
        beds_per_row = 8

        self.bed_rects = {}  # Reset bed rectangles

        for bed_num in range(1, self.total_beds + 1):
            row = (bed_num - 1) // beds_per_row
            col = (bed_num - 1) % beds_per_row

            bed_x = start_x + col * bed_spacing_x
            bed_y = start_y + row * bed_spacing_y

            bed_rect = pygame.Rect(bed_x, bed_y, 60, 80)

            # Determine bed sprite
            if bed_num in self.available_beds:
                self.bed_rects[bed_num] = bed_rect  # Store for click detection

                if bed_num == self.selected_bed:
                    sprite = self.bed_textures["selected"]
                else:
                    sprite = self.bed_textures["available"]
            else:
                sprite = self.bed_textures["occupied"]

            # Draw bed
            screen.blit(sprite, (bed_x, bed_y))

            # Draw resident on occupied beds
            if bed_num not in self.available_beds:
                # Random resident sprite
                resident_idx = bed_num % 4 + 1
                resident_sprite_key = f"resident_{resident_idx}"
                if resident_sprite_key in self.character_sprites:
                    resident_sprite = self.character_sprites[resident_sprite_key]
                    screen.blit(resident_sprite, (bed_x + 6, bed_y - 15))

            # Highlight available beds
            if bed_num in self.available_beds:
                if bed_num == self.selected_bed:
                    pygame.draw.rect(screen, (100, 255, 100), bed_rect, 3)
                else:
                    pygame.draw.rect(screen, (255, 255, 100), bed_rect, 2)

                # Show bed number
                num_font = pygame.font.Font(None, 20)
                num_surf = num_font.render(f"#{bed_num}", True, (255, 255, 255))
                num_bg = pygame.Surface((num_surf.get_width() + 4, num_surf.get_height() + 2))
                num_bg.fill((50, 50, 50))
                screen.blit(num_bg, (bed_x + 30 - num_surf.get_width() // 2 - 2, bed_y + 60 - 1))
                screen.blit(num_surf, (bed_x + 30 - num_surf.get_width() // 2, bed_y + 60))

        # Show selected bed info
        if self.selected_bed:
            info = self.bed_info[self.selected_bed]
            info_font = pygame.font.Font(None, 28)
            info_text = f"Bed #{self.selected_bed} selected - {info['desc']} ({info['quality']})"
            info_color = (100, 255, 100)
            info_surf = info_font.render(info_text, True, info_color)
            screen.blit(info_surf, (SCREEN_WIDTH // 2 - info_surf.get_width() // 2, 520))

            self.phase_complete[3] = True

        # Hover tooltip
        if self.hover_element and isinstance(self.hover_element, int) and self.hover_element in self.available_beds:
            self.draw_bed_tooltip(screen, pygame.mouse.get_pos(), self.bed_info[self.hover_element])

    def draw_bed_tooltip(self, screen, pos, info):
        """Draw tooltip for hovered bed"""
        tooltip_font = pygame.font.Font(None, 20)

        lines = [
            f"Location: {info['desc']}",
            f"Quality: {info['quality'].upper()}"
        ]

        # Calculate tooltip size
        max_width = max(tooltip_font.size(line)[0] for line in lines)
        tooltip_width = max_width + 20
        tooltip_height = len(lines) * 25 + 10

        # Position tooltip
        tooltip_x = min(pos[0] + 10, SCREEN_WIDTH - tooltip_width - 60)
        tooltip_y = max(pos[1] - tooltip_height - 10, 60)

        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(screen, (50, 50, 50), tooltip_rect)
        pygame.draw.rect(screen, (200, 200, 200), tooltip_rect, 2)

        # Draw tooltip text
        y_offset = 10
        for line in lines:
            text_surf = tooltip_font.render(line, True, (255, 255, 255))
            screen.blit(text_surf, (tooltip_x + 10, tooltip_y + y_offset))
            y_offset += 25

    def draw_continue_button(self, screen):
        """Draw continue button when phase is complete"""
        button_font = pygame.font.Font(None, 32)

        if self.current_phase == 1:
            button_text = "Submit Form"
        elif self.current_phase == 2:
            button_text = "I Agree to All Rules"
        else:
            button_text = "Confirm Bed Selection"

        button_surf = button_font.render(button_text, True, (255, 255, 255))

        self.continue_button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 120, 240, 50
        )

        # Button color based on phase
        if self.current_phase == 2:
            button_color = (150, 100, 50)  # Orange for rules
        else:
            button_color = (100, 150, 100)  # Green for others

        pygame.draw.rect(screen, button_color, self.continue_button_rect)

        if self.hover_element == "continue":
            pygame.draw.rect(screen, (255, 255, 255), self.continue_button_rect, 3)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self.continue_button_rect, 2)

        button_x = self.continue_button_rect.centerx - button_surf.get_width() // 2
        button_y = self.continue_button_rect.centery - button_surf.get_height() // 2
        screen.blit(button_surf, (button_x, button_y))

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        if self.current_phase == 1:
            # Handle form field clicks
            for field_name, field_data in self.form_fields.items():
                if field_data["rect"] and field_data["rect"].collidepoint(pos):
                    # Set this field as active for text input
                    self.active_field = field_name
                    # Trigger shake for emergency contact
                    if field_name == "emergency_contact":
                        self.shake_timer = 1.0
                    return

        elif self.current_phase == 2:
            # Handle rule checkbox clicks
            for i, rule in enumerate(self.shelter_rules):
                if rule["rect"] and rule["rect"].collidepoint(pos):
                    rule["acknowledged"] = not rule["acknowledged"]

        elif self.current_phase == 3:
            # Handle bed selection
            for bed_num, bed_rect in self.bed_rects.items():
                if bed_rect.collidepoint(pos):
                    self.selected_bed = bed_num
                    break

        # Handle continue button
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            if self.phase_complete[self.current_phase]:
                if self.current_phase < 3:
                    self.current_phase += 1
                    self.hover_element = None
                else:
                    # Complete the activity
                    self.complete_checkin()

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return

        self.hover_element = None

        if self.current_phase == 1:
            # Check form field hovers
            for field_name, field_data in self.form_fields.items():
                if field_data["rect"] and field_data["rect"].collidepoint(pos):
                    self.hover_element = field_name
                    break

        elif self.current_phase == 2:
            # Check rule checkbox hovers
            for i, rule in enumerate(self.shelter_rules):
                if rule["rect"] and rule["rect"].collidepoint(pos):
                    self.hover_element = f"rule_{i}"
                    break

        elif self.current_phase == 3:
            # Check bed hovers (only available beds)
            for bed_num, bed_rect in self.bed_rects.items():
                if bed_rect.collidepoint(pos):
                    self.hover_element = bed_num
                    break

        # Check continue button hover
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.hover_element = "continue"

    def handle_key(self, key):
        """Handle keyboard input for special keys only"""
        if not self.active:
            return

        # ESC to go back a phase
        if key == pygame.K_ESCAPE:
            if self.current_phase > 1:
                self.current_phase -= 1
                return

        # Handle special keys for active form field
        if self.current_phase == 1 and self.active_field and self.active_field in self.form_fields:
            field = self.form_fields[self.active_field]

            # Handle backspace
            if key == pygame.K_BACKSPACE:
                field["value"] = field["value"][:-1]
                return

            # Handle enter to confirm field
            if key == pygame.K_RETURN:
                if field["value"]:  # Only mark filled if not empty
                    field["filled"] = True
                    self.active_field = None
                return

    def handle_text_input(self, unicode_char):
        """Handle text input using unicode character from pygame.TEXTINPUT event"""
        if not self.active or self.current_phase != 1:
            return

        if self.active_field and self.active_field in self.form_fields:
            field = self.form_fields[self.active_field]

            # Add character if it's printable and field isn't full
            if unicode_char.isprintable() and len(field["value"]) < 30:
                field["value"] += unicode_char

    def complete_checkin(self):
        """Complete the shelter check-in following EXACT pattern"""

        # Update parent interior state (CRITICAL)
        if self.narrative_ref:
            self.narrative_ref.checkin_completed = True
            self.narrative_ref.assigned_bed = self.selected_bed
            self.narrative_ref.days_remaining = 30

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            # Show completion message through parent's dialogue box
            if hasattr(self.narrative_ref, 'dialogue_box'):
                bed_info = self.bed_info[self.selected_bed]
                msg = f"You're assigned bed {self.selected_bed} ({bed_info['desc']}). "
                msg += f"Remember: Curfew at 9 PM, wake at 5 AM. You have 30 days maximum."
                self.narrative_ref.dialogue_box.show("Shelter Worker", msg)

        # Mark activity complete
        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt

        # Update shake timer
        if self.shake_timer > 0:
            self.shake_timer -= dt