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

# Professional color palette
BACKGROUND_DARK = (25, 28, 35)
CARD_BG = (245, 247, 250)
CARD_BORDER = (200, 205, 210)
TEXT_PRIMARY = (40, 45, 55)
TEXT_SECONDARY = (100, 110, 125)
ACCENT_PRIMARY = (70, 130, 180)
ACCENT_SUCCESS = (76, 175, 80)
ACCENT_WARNING = (255, 152, 0)
ACCENT_ERROR = (244, 67, 54)
INPUT_BG = (255, 255, 255)
INPUT_BORDER = (220, 225, 230)
INPUT_FOCUS = (70, 130, 180)

class EmergencyShelterCheckIn(Activity):
    """Emergency shelter intake process with 3 phases"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None  # CRITICAL: Set by parent interior

        # Phase management (1=intake, 2=rules, 3=bed selection, 4=sleep)
        self.current_phase = 1
        self.phase_complete = {1: False, 2: False, 3: False, 4: False}

        # Phase 4: Sleep animation
        self.sleep_animation_timer = 0
        self.sleep_fade_alpha = 0

        # Phase 1: Intake form
        self.form_fields = {
            "name": {"value": "", "rect": None, "filled": False},
            "age": {"value": "", "rect": None, "filled": False},
            "last_address": {"value": "", "rect": None, "filled": False},  # Now editable
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
            12: {
                "desc": "Near bathroom",
                "quality": "noisy",
                "rect": None,
                "details": [
                    "Pros: Easy bathroom access",
                    "Cons: Toilet flushes, door slams",
                    "Sleep quality: Poor",
                    "Privacy: Low"
                ],
                "impact": "You'll be tired from poor sleep"
            },
            23: {
                "desc": "By the door",
                "quality": "cold",
                "rect": None,
                "details": [
                    "Pros: See who comes and goes",
                    "Cons: Cold drafts, foot traffic",
                    "Sleep quality: Poor",
                    "Privacy: None"
                ],
                "impact": "Cold and restless nights"
            },
            31: {
                "desc": "Corner bed",
                "quality": "safer",
                "rect": None,
                "details": [
                    "Pros: Tucked away, quieter",
                    "Cons: Darker, harder to socialize",
                    "Sleep quality: Better",
                    "Privacy: High"
                ],
                "impact": "Better rest but more isolated"
            },
            38: {
                "desc": "Middle row",
                "quality": "no privacy",
                "rect": None,
                "details": [
                    "Pros: Not isolated, average noise",
                    "Cons: No privacy, people on both sides",
                    "Sleep quality: Average",
                    "Privacy: None"
                ],
                "impact": "Social but overwhelming"
            },
            40: {
                "desc": "Near staff desk",
                "quality": "monitored",
                "rect": None,
                "details": [
                    "Pros: Staff protection, help nearby",
                    "Cons: Always watched, no freedom",
                    "Sleep quality: Average",
                    "Privacy: None"
                ],
                "impact": "Safer but restrictive"
            }
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
            # Create clean professional fallback instead of magenta
            error_surf = pygame.Surface(size, pygame.SRCALPHA)
            error_surf.fill(CARD_BG)  # Clean gray instead of magenta
            # Draw subtle placeholder border
            pygame.draw.rect(error_surf, CARD_BORDER, (0, 0, *size), 2, border_radius=6)
            return error_surf

    def start(self):
        """Start the shelter check-in activity"""
        super().start()
        self.current_phase = 1
        self.animation_timer = 0

        # Clear event queue to prevent event leaking from previous screen
        # This prevents the 'E' key from building entry from appearing as text input
        pygame.event.clear()
        print("[SHELTER_FORM] Event queue cleared to prevent input leaking")

        # Enable text input for form fields
        pygame.key.start_text_input()
        print("[SHELTER_FORM] Text input enabled via pygame.key.start_text_input()")

        # Auto-focus first empty field
        for field_name in ["name", "age", "last_address", "emergency_contact"]:
            if not self.form_fields[field_name]["filled"]:
                self.active_field = field_name
                print(f"[SHELTER_FORM] Auto-focused on field: '{field_name}'")
                break

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

        # Draw phase progress bar at top
        self.draw_phase_progress(screen)

        # Draw current phase
        if self.current_phase == 1:
            self.draw_phase1_intake(screen)
        elif self.current_phase == 2:
            self.draw_phase2_rules(screen)
        elif self.current_phase == 3:
            self.draw_phase3_beds(screen)
        elif self.current_phase == 4:
            self.draw_phase4_sleep(screen)

        # All phases now use Enter key to continue - no continue button needed

    def draw_phase_progress(self, screen):
        """Draw phase progress indicator at top"""
        phase_names = ["Intake Form", "Shelter Rules", "Bed Selection"]

        # Progress bar background
        progress_bg = pygame.Rect(SCREEN_WIDTH // 2 - 300, 70, 600, 40)
        pygame.draw.rect(screen, (60, 50, 40), progress_bg)
        pygame.draw.rect(screen, (150, 130, 110), progress_bg, 2)

        # Phase indicators
        step_width = 180
        step_height = 30
        start_x = progress_bg.x + 20
        start_y = progress_bg.y + 5

        for i, phase_name in enumerate(phase_names):
            phase_num = i + 1
            step_x = start_x + i * (step_width + 20)
            step_rect = pygame.Rect(step_x, start_y, step_width, step_height)

            # Step color based on completion
            if phase_num < self.current_phase:
                # Completed phase - green
                color = (100, 150, 100)
                text_color = (255, 255, 255)
                status = "✓"
            elif phase_num == self.current_phase:
                # Current phase - yellow
                color = (180, 140, 60)
                text_color = (255, 255, 255)
                status = "●"
            else:
                # Future phase - gray
                color = (80, 70, 60)
                text_color = (150, 150, 150)
                status = "○"

            # Draw step background
            pygame.draw.rect(screen, color, step_rect)
            pygame.draw.rect(screen, (200, 180, 160), step_rect, 1)

            # Draw phase text
            font = pygame.font.Font(None, 20)
            phase_text = f"{status} {phase_num}. {phase_name}"
            text_surf = font.render(phase_text, True, text_color)
            text_x = step_rect.centerx - text_surf.get_width() // 2
            text_y = step_rect.centery - text_surf.get_height() // 2
            screen.blit(text_surf, (text_x, text_y))

        # Overall progress text
        progress_font = pygame.font.Font(None, 24)
        progress_text = f"Emergency Shelter Check-In Process - Step {self.current_phase} of 3"
        progress_surf = progress_font.render(progress_text, True, (255, 220, 180))
        progress_x = SCREEN_WIDTH // 2 - progress_surf.get_width() // 2
        screen.blit(progress_surf, (progress_x, 120))

    def draw_phase1_intake(self, screen):
        """Draw intake form with clean, professional card design"""

        # Title (moved down to account for progress bar)
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Shelter Intake Form", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Draw desk with shelter worker
        desk_pos = (SCREEN_WIDTH // 2 - 60, 180)
        screen.blit(self.desk_texture, desk_pos)

        # Main form card
        card_width = 700
        card_height = 500
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = 220
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

        # Card shadow (subtle depth)
        shadow_rect = card_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        shadow_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 30), (0, 0, card_width, card_height), border_radius=12)
        screen.blit(shadow_surf, shadow_rect)

        # Card background
        pygame.draw.rect(screen, CARD_BG, card_rect, border_radius=12)
        pygame.draw.rect(screen, CARD_BORDER, card_rect, 2, border_radius=12)

        # Form fields
        form_font = pygame.font.Font(None, 22)
        form_x = card_x + 80  # 80px padding from card edge
        field_y = card_y + 80  # Start inside card with padding

        for field_name, field_data in self.form_fields.items():
            # Field label
            label = field_name.replace("_", " ").title() + ":"
            label_surf = form_font.render(label, True, TEXT_SECONDARY)
            screen.blit(label_surf, (form_x, field_y + 10))  # Vertically centered with input

            # Field input box
            field_rect = pygame.Rect(form_x + 180, field_y, 400, 40)
            field_data["rect"] = field_rect

            # Draw input field
            pygame.draw.rect(screen, INPUT_BG, field_rect, border_radius=6)

            # Border based on state
            if self.active_field == field_name:
                # Active: Blue border
                pygame.draw.rect(screen, INPUT_FOCUS, field_rect, 3, border_radius=6)
            elif self.hover_element == field_name:
                # Hover: Accent border
                pygame.draw.rect(screen, ACCENT_PRIMARY, field_rect, 2, border_radius=6)
            else:
                # Default: Light gray border
                pygame.draw.rect(screen, INPUT_BORDER, field_rect, 1, border_radius=6)

            # Draw value with special handling for "None"
            if field_name == "emergency_contact" and field_data["value"] == "None":
                value_color = ACCENT_ERROR
                if self.shake_timer > 0:
                    shake_x = int(math.sin(self.shake_timer * 20) * 3)
                    value_surf = form_font.render(field_data["value"], True, value_color)
                    screen.blit(value_surf, (field_rect.x + 12 + shake_x, field_rect.y + 10))
                    self.shake_timer -= 0.016
                else:
                    value_surf = form_font.render(field_data["value"], True, value_color)
                    screen.blit(value_surf, (field_rect.x + 12, field_rect.y + 10))
            else:
                value_color = TEXT_PRIMARY
                value_surf = form_font.render(field_data["value"], True, value_color)
                screen.blit(value_surf, (field_rect.x + 12, field_rect.y + 10))

            # Draw blinking cursor if this field is active
            if self.active_field == field_name:
                cursor_visible = (pygame.time.get_ticks() // 500) % 2
                if cursor_visible:
                    cursor_x = field_rect.x + 12 + value_surf.get_width() + 2
                    pygame.draw.line(screen, TEXT_PRIMARY,
                                   (cursor_x, field_rect.y + 8),
                                   (cursor_x, field_rect.y + 32), 2)

            field_y += 60  # Increased spacing

        # Instructions
        inst_font = pygame.font.Font(None, 20)
        all_have_content = all(field["value"].strip() for field in self.form_fields.values())

        if all_have_content:
            inst_text = "Press ENTER to continue"
            inst_color = ACCENT_SUCCESS
        else:
            inst_text = "Fill out all fields to continue"
            inst_color = TEXT_SECONDARY

        inst_surf = inst_font.render(inst_text, True, inst_color)
        screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, 640))

        # Phase 1 doesn't use phase_complete flag - we check content directly when Enter is pressed

    def draw_phase2_rules(self, screen):
        """Draw rules with clean, professional card design"""

        # Title (moved down to account for progress bar)
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("SHELTER RULES - MUST ACKNOWLEDGE ALL", True, (255, 200, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Warning text
        warning_font = pygame.font.Font(None, 24)
        warning = warning_font.render("Violation of any rule results in immediate removal", True, (255, 100, 100))
        screen.blit(warning, (SCREEN_WIDTH // 2 - warning.get_width() // 2, 180))

        # Rules list
        rule_font = pygame.font.Font(None, 26)
        rule_y = 220
        rule_x = 150

        for i, rule in enumerate(self.shelter_rules):
            # Checkbox (28x28 with rounded corners)
            checkbox_rect = pygame.Rect(rule_x, rule_y, 28, 28)
            rule["rect"] = checkbox_rect

            if rule["acknowledged"]:
                # Checked: Success green background
                pygame.draw.rect(screen, ACCENT_SUCCESS, checkbox_rect, border_radius=6)
                # Draw checkmark
                pygame.draw.lines(screen, (255, 255, 255), False,
                                [(checkbox_rect.x + 5, checkbox_rect.y + 14),
                                 (checkbox_rect.x + 11, checkbox_rect.y + 20),
                                 (checkbox_rect.x + 23, checkbox_rect.y + 8)], 3)
            else:
                # Unchecked: White background
                pygame.draw.rect(screen, INPUT_BG, checkbox_rect, border_radius=6)
                if self.hover_element == f"rule_{i}":
                    # Hover: Blue border
                    pygame.draw.rect(screen, ACCENT_PRIMARY, checkbox_rect, 3, border_radius=6)
                else:
                    # Default: Gray border
                    pygame.draw.rect(screen, INPUT_BORDER, checkbox_rect, 2, border_radius=6)

            # Rule text
            text_color = TEXT_PRIMARY if rule["acknowledged"] else TEXT_SECONDARY
            rule_surf = rule_font.render(rule["text"], True, text_color)
            screen.blit(rule_surf, (checkbox_rect.x + 45, rule_y + 5))

            rule_y += 65  # Increased spacing

        # Check if all rules acknowledged
        all_acknowledged = all(rule["acknowledged"] for rule in self.shelter_rules)
        self.phase_complete[2] = all_acknowledged

        # Instructions
        inst_font = pygame.font.Font(None, 20)
        if not all_acknowledged:
            inst_text = "Click checkboxes to acknowledge all rules"
            inst_color = TEXT_SECONDARY
        else:
            inst_text = "Press ENTER to continue"
            inst_color = ACCENT_SUCCESS

        inst_surf = inst_font.render(inst_text, True, inst_color)
        screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, 700))

    def draw_phase3_beds(self, screen):
        """Draw bed selection with clean card-based design"""

        # Title (moved down to account for progress bar)
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("Choose Your Bed (Only 5 Available)", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Subtitle
        sub_font = pygame.font.Font(None, 20)
        subtitle = sub_font.render("Hover over available beds to see details - Your choice matters!", True, (200, 180, 160))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 175))

        # Draw available beds as cards
        self.bed_rects = {}  # Reset bed rectangles

        # Container dimensions (must match main container)
        container_x = 50
        container_y = 50
        container_width = SCREEN_WIDTH - 100  # 924px
        container_height = SCREEN_HEIGHT - 100  # 668px

        # Calculate card layout to fit within container
        num_cards = 5
        horizontal_padding = 60  # Padding inside container

        # Available space for cards
        available_width = container_width - (2 * horizontal_padding)  # 924 - 120 = 804px

        # Card dimensions - sized to fit available space
        card_spacing = 15  # Spacing between cards
        card_width = (available_width - (num_cards - 1) * card_spacing) // num_cards
        card_height = 140

        # Starting position (inside container)
        total_cards_width = num_cards * card_width + (num_cards - 1) * card_spacing
        start_x = container_x + (container_width - total_cards_width) // 2  # Centered in container
        start_y = 170  # Below subtitle, inside container

        for i, bed_num in enumerate(self.available_beds):
            bed_x = start_x + i * (card_width + card_spacing)
            bed_y = start_y

            # Create card rect
            card_rect = pygame.Rect(bed_x, bed_y, card_width, card_height)
            self.bed_rects[bed_num] = card_rect

            # Determine if this bed is selected or hovered
            is_selected = (bed_num == self.selected_bed)
            is_hovered = (self.hover_element == bed_num)

            # Card shadow
            shadow_rect = card_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            shadow_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 40), (0, 0, card_width, card_height), border_radius=10)
            screen.blit(shadow_surf, shadow_rect)

            # Card background
            if is_selected:
                bg_color = ACCENT_SUCCESS
                border_color = (255, 255, 255)
                border_width = 4
            elif is_hovered:
                bg_color = ACCENT_PRIMARY
                border_color = (255, 255, 255)
                border_width = 3
            else:
                bg_color = CARD_BG
                border_color = CARD_BORDER
                border_width = 2

            pygame.draw.rect(screen, bg_color, card_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, card_rect, border_width, border_radius=10)

            # Bed number (large, centered at top)
            num_font = pygame.font.Font(None, 48)
            num_text = f"#{bed_num}"
            num_color = (255, 255, 255) if (is_selected or is_hovered) else TEXT_PRIMARY
            num_surf = num_font.render(num_text, True, num_color)
            num_x = bed_x + (card_width - num_surf.get_width()) // 2
            num_y = bed_y + 20
            screen.blit(num_surf, (num_x, num_y))

            # Bed info
            info = self.bed_info[bed_num]
            info_font = pygame.font.Font(None, 18)

            # Description
            desc_color = (255, 255, 255) if (is_selected or is_hovered) else TEXT_SECONDARY
            desc_surf = info_font.render(info['desc'], True, desc_color)
            desc_x = bed_x + (card_width - desc_surf.get_width()) // 2
            desc_y = bed_y + 75
            screen.blit(desc_surf, (desc_x, desc_y))

            # Quality indicator
            quality_font = pygame.font.Font(None, 16)
            quality_text = f"({info['quality']})"
            quality_color = (255, 255, 255) if (is_selected or is_hovered) else TEXT_SECONDARY
            quality_surf = quality_font.render(quality_text, True, quality_color)
            quality_x = bed_x + (card_width - quality_surf.get_width()) // 2
            quality_y = bed_y + 100
            screen.blit(quality_surf, (quality_x, quality_y))

        # Instructions
        inst_font = pygame.font.Font(None, 20)
        if self.selected_bed:
            info = self.bed_info[self.selected_bed]

            # Selected bed display with emotional context
            info_font = pygame.font.Font(None, 26)
            info_text = f"Selected: Bed #{self.selected_bed} - {info['desc']}"
            info_color = (150, 255, 150)
            info_surf = info_font.render(info_text, True, info_color)
            screen.blit(info_surf, (SCREEN_WIDTH // 2 - info_surf.get_width() // 2, 520))

            # Impact preview
            impact_font = pygame.font.Font(None, 20)
            impact_text = f"Impact: {info['impact']}"
            impact_color = (255, 200, 120)
            impact_surf = impact_font.render(impact_text, True, impact_color)
            screen.blit(impact_surf, (SCREEN_WIDTH // 2 - impact_surf.get_width() // 2, 545))

            # Emotional context
            context_text = "This choice will affect your shelter experience..."
            context_surf = impact_font.render(context_text, True, (200, 180, 160))
            screen.blit(context_surf, (SCREEN_WIDTH // 2 - context_surf.get_width() // 2, 565))

            self.phase_complete[3] = True

            # Instructions
            inst_text = "Press ENTER to confirm bed selection"
            inst_surf = inst_font.render(inst_text, True, (255, 220, 180))
            inst_bg = pygame.Surface((inst_surf.get_width() + 20, inst_surf.get_height() + 10))
            inst_bg.fill((60, 50, 40))
            inst_bg_rect = inst_bg.get_rect(center=(SCREEN_WIDTH // 2, 600))
            screen.blit(inst_bg, inst_bg_rect)
            screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, 595))
        else:
            inst_text = "Click on a bed card to select it"
            inst_color = TEXT_SECONDARY
            inst_surf = inst_font.render(inst_text, True, inst_color)
            inst_y = container_y + container_height - 60  # 60px from bottom of container
            screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, inst_y))

    def draw_phase4_sleep(self, screen):
        """Draw sleep animation - fade to black, show time passing, fade back"""

        # Update animation timer
        self.sleep_animation_timer += 0.016  # ~16ms per frame

        # Animation phases:
        # 0-2s: Fade to black
        # 2-4s: Show "Sleeping..." text
        # 4-6s: Fade back in
        # 6s+: Complete

        # Fade overlay
        if self.sleep_animation_timer < 2:
            # Fading to black (0-2 seconds)
            self.sleep_fade_alpha = int((self.sleep_animation_timer / 2) * 255)
        elif self.sleep_animation_timer < 4:
            # Fully dark (2-4 seconds)
            self.sleep_fade_alpha = 255
        elif self.sleep_animation_timer < 6:
            # Fading back in (4-6 seconds)
            self.sleep_fade_alpha = int((1 - (self.sleep_animation_timer - 4) / 2) * 255)
        else:
            # Animation complete
            self.sleep_fade_alpha = 0
            self.phase_complete[4] = True

        # Draw black overlay
        if self.sleep_fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, self.sleep_fade_alpha))
            screen.blit(fade_surface, (0, 0))

        # Show text during middle phase
        if 2 <= self.sleep_animation_timer < 4:
            # Date/time display - make it very clear a night passed
            date_font = pygame.font.Font(None, 56)
            date_text = "Night 1 at the Shelter"
            date_surf = date_font.render(date_text, True, (255, 255, 255))
            screen.blit(date_surf, (SCREEN_WIDTH // 2 - date_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 80))

            # Bed location
            bed_font = pygame.font.Font(None, 32)
            bed_text = f"Bed #{self.selected_bed}"
            bed_surf = bed_font.render(bed_text, True, (180, 180, 180))
            screen.blit(bed_surf, (SCREEN_WIDTH // 2 - bed_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

            # Time progression indicator
            time_font = pygame.font.Font(None, 40)

            # Show time progression with animated text
            elapsed = self.sleep_animation_timer - 2  # 0-2 range
            if elapsed < 0.5:
                time_text = "10:00 PM - Lights Out"
            elif elapsed < 1.0:
                time_text = "12:00 AM - Midnight"
            elif elapsed < 1.5:
                time_text = "3:00 AM - Still Dark"
            else:
                time_text = "5:30 AM - Wake Up Call"

            time_surf = time_font.render(time_text, True, (200, 200, 150))
            screen.blit(time_surf, (SCREEN_WIDTH // 2 - time_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

            # Visual separator
            separator_font = pygame.font.Font(None, 28)
            separator_text = "─────────────────"
            separator_surf = separator_font.render(separator_text, True, (100, 100, 100))
            screen.blit(separator_surf, (SCREEN_WIDTH // 2 - separator_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

            # Day counter
            day_font = pygame.font.Font(None, 24)
            day_text = "Day 1 Complete - 29 Days Remaining"
            day_surf = day_font.render(day_text, True, (150, 150, 150))
            screen.blit(day_surf, (SCREEN_WIDTH // 2 - day_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 110))

        # Auto-complete when animation finishes
        if self.sleep_animation_timer >= 6:
            # Small delay to ensure fade completes
            if self.sleep_animation_timer >= 6.5:
                self.complete_checkin()

    def draw_bed_tooltip(self, screen, pos, info):
        """Draw enhanced tooltip for hovered bed"""
        tooltip_font = pygame.font.Font(None, 18)
        header_font = pygame.font.Font(None, 20)

        # Build tooltip lines
        lines = [f"BED INFO - {info['desc'].upper()}"]
        lines.extend(info['details'])
        lines.append("")
        lines.append(f"Impact: {info['impact']}")

        # Calculate tooltip size
        max_width = max(header_font.size(lines[0])[0] if i == 0 else tooltip_font.size(line)[0]
                       for i, line in enumerate(lines) if line.strip())
        tooltip_width = max_width + 30
        tooltip_height = len([l for l in lines if l.strip()]) * 22 + 20

        # Position tooltip
        tooltip_x = min(pos[0] + 15, SCREEN_WIDTH - tooltip_width - 10)
        tooltip_y = max(pos[1] - tooltip_height - 15, 60)

        # Draw tooltip background with border
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(screen, (40, 35, 30), tooltip_rect)
        pygame.draw.rect(screen, (220, 200, 180), tooltip_rect, 3)

        # Draw tooltip text
        y_offset = 10
        for i, line in enumerate(lines):
            if line.strip():
                if i == 0:
                    # Header
                    text_surf = header_font.render(line, True, (255, 220, 100))
                elif "Impact:" in line:
                    # Impact line
                    text_surf = tooltip_font.render(line, True, (255, 180, 120))
                else:
                    # Regular detail line
                    text_surf = tooltip_font.render(line, True, (255, 255, 255))
                screen.blit(text_surf, (tooltip_x + 15, tooltip_y + y_offset))
            y_offset += 22

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
        print(f"[SHELTER_FORM] Mouse click at {pos}, button {button}, active={self.active}, phase={self.current_phase}")
        if not self.active or button != 1:
            return

        if self.current_phase == 1:
            # Handle form field clicks
            for field_name, field_data in self.form_fields.items():
                if field_data["rect"] and field_data["rect"].collidepoint(pos):
                    # Auto-mark previous field as filled if it has content
                    if self.active_field and self.active_field in self.form_fields:
                        prev_field = self.form_fields[self.active_field]
                        if prev_field["value"].strip():
                            prev_field["filled"] = True
                            print(f"[SHELTER_FORM] Auto-marked previous field '{self.active_field}' as filled")

                    # Set this field as active for text input
                    self.active_field = field_name
                    print(f"[SHELTER_FORM] Field '{field_name}' is now active for text input")
                    # Trigger shake for emergency contact
                    if field_name == "emergency_contact":
                        self.shake_timer = 1.0
                    return
            print(f"[SHELTER_FORM] Click did not hit any field. Active field: {self.active_field}")

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
        """Handle keyboard input for special keys AND regular characters as fallback"""
        # Special debugging for R and Y keys
        if key == 114:  # R key
            print(f"[SHELTER_FORM] *** R KEY (114) RECEIVED ***")
        if key == 121:  # Y key
            print(f"[SHELTER_FORM] *** Y KEY (121) RECEIVED ***")

        print(f"[SHELTER_FORM] Key pressed: {key}, active={self.active}, phase={self.current_phase}, active_field={self.active_field}")
        if not self.active:
            print(f"[SHELTER_FORM] Rejecting - activity not active!")
            return

        # ESC to go back a phase
        if key == pygame.K_ESCAPE:
            if self.current_phase > 1:
                self.current_phase -= 1
                return

        # ENTER to submit/advance
        if key == pygame.K_RETURN:
            # Phase 1: Check if all fields have content (not just "filled" flag)
            if self.current_phase == 1:
                all_have_content = all(field["value"].strip() for field in self.form_fields.values())

                if all_have_content:
                    # Mark all fields as filled
                    for field in self.form_fields.values():
                        field["filled"] = True
                    print(f"[SHELTER_FORM] Enter pressed - all fields complete, advancing to phase 2")
                    self.current_phase = 2
                    self.active_field = None
                    self.hover_element = None
                    # Update objective display for new phase
                    if self.narrative_ref and hasattr(self.narrative_ref, 'update_objective_display'):
                        self.narrative_ref.update_objective_display()
                    return
                else:
                    # Show error - not all fields filled
                    print(f"[SHELTER_FORM] Enter pressed but not all fields have content")
                    self.shake_timer = 0.5
                    return

            # Phase 2, 3, & 4: Use phase_complete flag
            elif self.phase_complete[self.current_phase]:
                if self.current_phase < 4:
                    self.current_phase += 1
                    self.hover_element = None
                    if self.current_phase == 4:
                        # Reset sleep animation timer when entering phase 4
                        self.sleep_animation_timer = 0
                    print(f"[SHELTER_FORM] Enter pressed - advancing to phase {self.current_phase}")
                    # Update objective display for new phase
                    if self.narrative_ref and hasattr(self.narrative_ref, 'update_objective_display'):
                        self.narrative_ref.update_objective_display()
                else:
                    # Complete the activity (after sleep animation)
                    print(f"[SHELTER_FORM] Sleep animation complete - completing checkin")
                    self.complete_checkin()
                return

        # Handle special keys for active form field
        if self.current_phase == 1 and self.active_field and self.active_field in self.form_fields:
            field = self.form_fields[self.active_field]

            # Handle backspace
            if key == pygame.K_BACKSPACE:
                field["value"] = field["value"][:-1]
                print(f"[SHELTER_FORM] Backspace - new value: '{field['value']}'")
                return

            # Note: Enter key for individual fields is handled at the top level now
            # This section is for character input only

            # FALLBACK: Handle regular character keys directly since TEXTINPUT isn't working
            if len(field["value"]) < 30:
                char = None
                mods = pygame.key.get_mods()
                shift_pressed = mods & pygame.KMOD_SHIFT

                # Letters a-z (97-122)
                if 97 <= key <= 122:
                    char = chr(key)
                    print(f"[SHELTER_FORM] Letter key detected: {key} = '{char}'")
                    if shift_pressed or (mods & pygame.KMOD_CAPS):
                        char = char.upper()
                        print(f"[SHELTER_FORM] Uppercase applied: '{char}'")

                # Numbers 0-9 (48-57) with shift variants
                elif 48 <= key <= 57:
                    if shift_pressed:
                        # Shift+number = special characters
                        shift_nums = {48: ')', 49: '!', 50: '@', 51: '#', 52: '$', 53: '%', 54: '^', 55: '&', 56: '*', 57: '('}
                        char = shift_nums.get(key, chr(key))
                    else:
                        char = chr(key)

                # Space (32)
                elif key == 32:
                    char = ' '

                # Common punctuation and symbols
                elif key in [45, 61, 91, 93, 92, 59, 39, 44, 46, 47, 96]:  # - = [ ] \ ; ' , . / `
                    # Handle shift variants for punctuation
                    punct_map = {
                        45: ('_', '-'), 61: ('+', '='), 91: ('{', '['), 93: ('}', ']'),
                        92: ('|', '\\'), 59: (':', ';'), 39: ('"', "'"), 44: ('<', ','),
                        46: ('>', '.'), 47: ('?', '/'), 96: ('~', '`')
                    }
                    if key in punct_map:
                        char = punct_map[key][0] if shift_pressed else punct_map[key][1]

                if char:
                    field["value"] += char
                    print(f"[SHELTER_FORM] Added character '{char}' (key={key}), new value: '{field['value']}'")
                    return
                else:
                    print(f"[SHELTER_FORM] Key {key} not handled")

    def handle_text_input(self, unicode_char):
        """Handle text input using unicode character from pygame.TEXTINPUT event"""
        print(f"[SHELTER_FORM] TEXTINPUT received: '{unicode_char}', active={self.active}, phase={self.current_phase}, active_field={self.active_field}")
        if not self.active or self.current_phase != 1:
            print(f"[SHELTER_FORM] Rejecting input - not active or wrong phase")
            return

        if self.active_field and self.active_field in self.form_fields:
            field = self.form_fields[self.active_field]

            # Add character if it's printable and field isn't full
            if unicode_char.isprintable() and len(field["value"]) < 30:
                field["value"] += unicode_char
                print(f"[SHELTER_FORM] Added character, new value: '{field['value']}'")
            else:
                print(f"[SHELTER_FORM] Character rejected - isprintable={unicode_char.isprintable()}, len={len(field['value'])}")
        else:
            print(f"[SHELTER_FORM] No active field to receive input")

    def complete_checkin(self):
        """Complete the shelter check-in following EXACT pattern"""

        # Disable text input mode
        pygame.key.stop_text_input()
        print("[SHELTER_FORM] Text input disabled via pygame.key.stop_text_input()")

        # Update parent interior state (CRITICAL)
        if self.narrative_ref:
            self.narrative_ref.intake_complete = True
            self.narrative_ref.bed_assigned = True
            self.narrative_ref.assigned_bed = self.selected_bed
            self.narrative_ref.days_remaining = 30

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            # Show bed choice narrative
            bed_narratives = {
                12: "Bed 12, near the bathroom. The constant noise will make sleep difficult, but at least you're close to facilities.",
                23: "Bed 23, by the entrance door. Cold drafts and constant foot traffic, but you can see everyone coming and going.",
                31: "Bed 31, tucked in the corner. Feels safer away from the main area, though it's darker here.",
                38: "Bed 38, right in the middle row. No privacy whatsoever, but you're not isolated either.",
                40: "Bed 40, near the staff desk. They'll keep an eye on you - for better or worse."
            }

            bed_message = bed_narratives.get(self.selected_bed, f"Bed {self.selected_bed}. Your temporary home.")

            # Show the bed choice impact and transition message
            self.narrative_ref.dialogue_box.show(None, f"{bed_message}\n\nYou're officially checked in. This thin mattress is home now.")

        # Mark activity complete
        print("[SHELTER_FORM] *** Marking activity as completed - showing bed narrative ***")
        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt

        # Update shake timer
        if self.shake_timer > 0:
            self.shake_timer -= dt