"""
Emergency Shelter Check-In Mini-Game
Uses ActivityUIBase for dynamic sizing and consistent UI.
"""
import pygame
import math
from src.activities.activities import Activity
from src.ui.activity_ui_base import ActivityUIBase, UIColors, UIHelpers, Align


class EmergencyShelterCheckIn(Activity):
    """Emergency shelter intake process with 3 phases - using dynamic UI"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None
        self.ui = None  # Initialized in start() when we have screen access

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
            "last_address": {"value": "", "rect": None, "filled": False},
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
        self.available_beds = [12, 23, 31, 38, 40]
        self.bed_info = {
            12: {"desc": "Near bathroom", "quality": "noisy",
                 "impact": "You'll be tired from poor sleep"},
            23: {"desc": "By the door", "quality": "cold",
                 "impact": "Cold and restless nights"},
            31: {"desc": "Corner bed", "quality": "safer",
                 "impact": "Better rest but more isolated"},
            38: {"desc": "Middle row", "quality": "no privacy",
                 "impact": "Social but overwhelming"},
            40: {"desc": "Near staff desk", "quality": "monitored",
                 "impact": "Safer but restrictive"}
        }
        self.selected_bed = None
        self.bed_rects = {}

        # Visual state
        self.animation_timer = 0
        self.hover_element = None
        self.shake_timer = 0

    def start(self):
        """Start the shelter check-in activity"""
        super().start()
        self.current_phase = 1
        self.animation_timer = 0
        pygame.event.clear()
        pygame.key.start_text_input()

        # Auto-focus first empty field
        for field_name in ["name", "age", "last_address", "emergency_contact"]:
            if not self.form_fields[field_name]["filled"]:
                self.active_field = field_name
                break

    def _ensure_ui(self, screen):
        """Ensure UI is initialized with current screen"""
        if self.ui is None or self.ui.screen != screen:
            self.ui = ActivityUIBase(screen)

    def draw(self, screen):
        """Main draw using dynamic UI framework"""
        if not self.active:
            return

        self._ensure_ui(screen)
        m = self.ui.metrics  # Shorthand for metrics

        # Dark overlay
        self.ui.draw_overlay(screen, alpha=200)

        # Update animation
        self.animation_timer += 0.016

        # Main container - 90% width, 90% height, centered
        container = self.ui.centered_rect(90, 90)
        UIHelpers.draw_rounded_rect(screen, container, (40, 35, 30), m.radius_lg)
        pygame.draw.rect(screen, (200, 180, 160), container, 3, border_radius=m.radius_lg)

        # Draw phase progress bar at top
        self._draw_phase_progress(screen, container)

        # Draw current phase content
        if self.current_phase == 1:
            self._draw_phase1_intake(screen, container)
        elif self.current_phase == 2:
            self._draw_phase2_rules(screen, container)
        elif self.current_phase == 3:
            self._draw_phase3_beds(screen, container)
        elif self.current_phase == 4:
            self._draw_phase4_sleep(screen)

    def _draw_phase_progress(self, screen, container):
        """Draw phase progress indicator"""
        m = self.ui.metrics
        phase_names = ["Intake Form", "Shelter Rules", "Bed Selection"]

        # Progress bar - 60% of container width, at top
        bar_width = int(container.width * 0.6)
        bar_height = m.grid * 5
        bar_x = container.centerx - bar_width // 2
        bar_y = container.y + m.padding_md

        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (60, 50, 40), bar_rect, border_radius=m.radius_sm)
        pygame.draw.rect(screen, (150, 130, 110), bar_rect, 2, border_radius=m.radius_sm)

        # Phase indicators - divide bar into 3 steps
        step_width = (bar_width - m.padding_sm * 4) // 3
        step_height = bar_height - m.padding_xs * 2

        for i, phase_name in enumerate(phase_names):
            phase_num = i + 1
            step_x = bar_x + m.padding_sm + i * (step_width + m.padding_sm)
            step_y = bar_y + m.padding_xs
            step_rect = pygame.Rect(step_x, step_y, step_width, step_height)

            # Color based on completion
            if phase_num < self.current_phase:
                color, text_color, status = (100, 150, 100), UIColors.TEXT_LIGHT, "✓"
            elif phase_num == self.current_phase:
                color, text_color, status = (180, 140, 60), UIColors.TEXT_LIGHT, "●"
            else:
                color, text_color, status = (80, 70, 60), UIColors.TEXT_MUTED, "○"

            pygame.draw.rect(screen, color, step_rect, border_radius=m.radius_sm)

            # Phase text
            phase_text = f"{status} {phase_num}. {phase_name}"
            text_surf = self.ui.fonts.small.render(phase_text, True, text_color)
            text_rect = text_surf.get_rect(center=step_rect.center)
            screen.blit(text_surf, text_rect)

        # Title below progress bar
        title_y = bar_y + bar_height + m.padding_sm
        title = f"Emergency Shelter Check-In - Step {self.current_phase} of 3"
        self.ui.draw_text(screen, title, (container.centerx, title_y),
                         'subheading', (255, 220, 180), Align.CENTER)

    def _draw_phase1_intake(self, screen, container):
        """Draw intake form with dynamic layout"""
        m = self.ui.metrics

        # Content area starts below progress bar
        content_top = container.y + m.grid * 12
        content_rect = pygame.Rect(
            container.x + m.padding_lg,
            content_top,
            container.width - m.padding_lg * 2,
            container.height - m.grid * 14 - m.padding_lg
        )

        # Title
        self.ui.draw_text(screen, "Shelter Intake Form",
                         (container.centerx, content_rect.y),
                         'heading', (255, 220, 180), Align.CENTER)

        # Form card - 70% of content width, centered
        card_width = int(content_rect.width * 0.7)
        card_height = int(content_rect.height * 0.75)
        card_x = content_rect.centerx - card_width // 2
        card_y = content_rect.y + m.grid * 6
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

        # Draw card with shadow
        UIHelpers.draw_shadow(screen, card_rect, 4, 30, m.radius_lg)
        pygame.draw.rect(screen, UIColors.CARD_BG, card_rect, border_radius=m.radius_lg)
        pygame.draw.rect(screen, UIColors.INPUT_BORDER, card_rect, 2, border_radius=m.radius_lg)

        # Form fields - stack vertically with padding
        field_x = card_x + m.padding_lg
        field_width = card_width - m.padding_lg * 2 - 150  # Leave room for label
        field_height = m.input_height
        label_width = 140

        field_y = card_y + m.padding_lg
        field_spacing = field_height + m.padding_md

        for field_name, field_data in self.form_fields.items():
            # Label
            label = field_name.replace("_", " ").title() + ":"
            label_surf = self.ui.fonts.body.render(label, True, UIColors.TEXT_SECONDARY)
            screen.blit(label_surf, (field_x, field_y + (field_height - label_surf.get_height()) // 2))

            # Input field
            input_x = field_x + label_width
            input_rect = pygame.Rect(input_x, field_y, field_width, field_height)
            field_data["rect"] = input_rect

            # Determine state
            if self.active_field == field_name:
                state = 'focus'
            elif field_data["filled"]:
                state = 'filled'
            elif self.hover_element == field_name:
                state = 'focus'
            else:
                state = 'normal'

            # Draw input (without label since we drew it separately)
            pygame.draw.rect(screen, UIColors.INPUT_BG, input_rect, border_radius=m.radius_sm)

            if state == 'focus':
                pygame.draw.rect(screen, UIColors.INPUT_FOCUS, input_rect, 3, border_radius=m.radius_sm)
            elif state == 'filled':
                pygame.draw.rect(screen, UIColors.SUCCESS, input_rect, 2, border_radius=m.radius_sm)
            else:
                pygame.draw.rect(screen, UIColors.INPUT_BORDER, input_rect, 1, border_radius=m.radius_sm)

            # Value
            value_color = UIColors.ERROR if (field_name == "emergency_contact" and field_data["value"] == "None") else UIColors.TEXT_PRIMARY
            value_surf = self.ui.fonts.body.render(field_data["value"], True, value_color)
            screen.blit(value_surf, (input_rect.x + m.padding_sm, input_rect.centery - value_surf.get_height() // 2))

            # Cursor for active field
            if self.active_field == field_name and (pygame.time.get_ticks() // 500) % 2:
                cursor_x = input_rect.x + m.padding_sm + value_surf.get_width() + 2
                pygame.draw.line(screen, UIColors.TEXT_PRIMARY,
                               (cursor_x, input_rect.y + 8),
                               (cursor_x, input_rect.bottom - 8), 2)

            field_y += field_spacing

        # Instructions at bottom
        all_have_content = all(f["value"].strip() for f in self.form_fields.values())
        if all_have_content:
            inst_text, inst_color = "Press ENTER to continue", UIColors.SUCCESS
        else:
            inst_text, inst_color = "Fill out all fields to continue", UIColors.TEXT_SECONDARY

        inst_y = card_rect.bottom + m.padding_md
        self.ui.draw_text(screen, inst_text, (container.centerx, inst_y),
                         'small', inst_color, Align.CENTER)

    def _draw_phase2_rules(self, screen, container):
        """Draw rules with dynamic layout"""
        m = self.ui.metrics

        content_top = container.y + m.grid * 12
        content_rect = pygame.Rect(
            container.x + m.padding_lg,
            content_top,
            container.width - m.padding_lg * 2,
            container.height - m.grid * 14 - m.padding_lg
        )

        # Title
        self.ui.draw_text(screen, "SHELTER RULES - MUST ACKNOWLEDGE ALL",
                         (container.centerx, content_rect.y),
                         'heading', (255, 200, 100), Align.CENTER)

        # Warning
        self.ui.draw_text(screen, "Violation of any rule results in immediate removal",
                         (container.centerx, content_rect.y + m.grid * 4),
                         'body', UIColors.ERROR, Align.CENTER)

        # Rules list
        rules_start_y = content_rect.y + m.grid * 8
        rule_height = m.grid * 6
        rule_spacing = m.grid * 2
        checkbox_size = m.grid * 3

        for i, rule in enumerate(self.shelter_rules):
            rule_y = rules_start_y + i * (rule_height + rule_spacing)

            # Checkbox
            checkbox_rect = pygame.Rect(
                content_rect.x + m.padding_lg,
                rule_y + (rule_height - checkbox_size) // 2,
                checkbox_size,
                checkbox_size
            )
            rule["rect"] = checkbox_rect

            if rule["acknowledged"]:
                pygame.draw.rect(screen, UIColors.SUCCESS, checkbox_rect, border_radius=m.radius_sm)
                # Checkmark
                cx, cy = checkbox_rect.center
                pygame.draw.lines(screen, UIColors.TEXT_LIGHT, False, [
                    (cx - 6, cy), (cx - 2, cy + 5), (cx + 8, cy - 6)
                ], 3)
            else:
                pygame.draw.rect(screen, UIColors.INPUT_BG, checkbox_rect, border_radius=m.radius_sm)
                border_color = UIColors.PRIMARY if self.hover_element == f"rule_{i}" else UIColors.INPUT_BORDER
                pygame.draw.rect(screen, border_color, checkbox_rect, 2, border_radius=m.radius_sm)

            # Rule text
            text_color = UIColors.TEXT_PRIMARY if rule["acknowledged"] else UIColors.TEXT_SECONDARY
            text_surf = self.ui.fonts.body.render(rule["text"], True, text_color)
            screen.blit(text_surf, (checkbox_rect.right + m.padding_md,
                                   checkbox_rect.centery - text_surf.get_height() // 2))

        # Update phase completion
        all_acknowledged = all(r["acknowledged"] for r in self.shelter_rules)
        self.phase_complete[2] = all_acknowledged

        # Instructions
        if all_acknowledged:
            inst_text, inst_color = "Press ENTER to continue", UIColors.SUCCESS
        else:
            inst_text, inst_color = "Click checkboxes to acknowledge all rules", UIColors.TEXT_SECONDARY

        inst_y = container.bottom - m.padding_lg * 2
        self.ui.draw_text(screen, inst_text, (container.centerx, inst_y),
                         'small', inst_color, Align.CENTER)

    def _draw_phase3_beds(self, screen, container):
        """Draw bed selection with dynamic card grid"""
        m = self.ui.metrics

        content_top = container.y + m.grid * 12
        content_rect = pygame.Rect(
            container.x + m.padding_lg,
            content_top,
            container.width - m.padding_lg * 2,
            container.height - m.grid * 14 - m.padding_lg
        )

        # Title
        self.ui.draw_text(screen, "Choose Your Bed (Only 5 Available)",
                         (container.centerx, content_rect.y),
                         'heading', (255, 220, 180), Align.CENTER)

        # Subtitle
        self.ui.draw_text(screen, "Hover over available beds to see details",
                         (container.centerx, content_rect.y + m.grid * 4),
                         'small', UIColors.TEXT_MUTED, Align.CENTER)

        # Bed cards - use grid layout
        self.bed_rects = {}
        num_beds = len(self.available_beds)
        card_area_y = content_rect.y + m.grid * 7
        card_area_height = int(content_rect.height * 0.4)

        # Calculate card dimensions
        total_gap = m.padding_md * (num_beds - 1)
        card_width = (content_rect.width - total_gap) // num_beds
        card_height = card_area_height

        for i, bed_num in enumerate(self.available_beds):
            card_x = content_rect.x + i * (card_width + m.padding_md)
            card_rect = pygame.Rect(card_x, card_area_y, card_width, card_height)
            self.bed_rects[bed_num] = card_rect

            is_selected = (bed_num == self.selected_bed)
            is_hovered = (self.hover_element == bed_num)

            # Card styling
            if is_selected:
                bg_color = UIColors.SUCCESS
                border_color = UIColors.TEXT_LIGHT
                border_width = 4
            elif is_hovered:
                bg_color = UIColors.PRIMARY
                border_color = UIColors.TEXT_LIGHT
                border_width = 3
            else:
                bg_color = UIColors.CARD_BG
                border_color = UIColors.INPUT_BORDER
                border_width = 2

            # Shadow and card
            UIHelpers.draw_shadow(screen, card_rect, 3, 40, m.radius_md)
            pygame.draw.rect(screen, bg_color, card_rect, border_radius=m.radius_md)
            pygame.draw.rect(screen, border_color, card_rect, border_width, border_radius=m.radius_md)

            # Bed number
            text_color = UIColors.TEXT_LIGHT if (is_selected or is_hovered) else UIColors.TEXT_PRIMARY
            num_text = f"#{bed_num}"
            num_surf = self.ui.fonts.heading.render(num_text, True, text_color)
            num_rect = num_surf.get_rect(centerx=card_rect.centerx, top=card_rect.y + m.padding_md)
            screen.blit(num_surf, num_rect)

            # Bed info
            info = self.bed_info[bed_num]
            desc_color = UIColors.TEXT_LIGHT if (is_selected or is_hovered) else UIColors.TEXT_SECONDARY

            desc_surf = self.ui.fonts.small.render(info['desc'], True, desc_color)
            desc_rect = desc_surf.get_rect(centerx=card_rect.centerx, centery=card_rect.centery)
            screen.blit(desc_surf, desc_rect)

            quality_surf = self.ui.fonts.tiny.render(f"({info['quality']})", True, desc_color)
            quality_rect = quality_surf.get_rect(centerx=card_rect.centerx, top=desc_rect.bottom + m.padding_xs)
            screen.blit(quality_surf, quality_rect)

        # Selected bed info
        info_y = card_area_y + card_height + m.padding_lg
        if self.selected_bed:
            info = self.bed_info[self.selected_bed]
            self.ui.draw_text(screen, f"Selected: Bed #{self.selected_bed} - {info['desc']}",
                             (container.centerx, info_y), 'subheading', UIColors.SUCCESS, Align.CENTER)
            self.ui.draw_text(screen, f"Impact: {info['impact']}",
                             (container.centerx, info_y + m.grid * 3), 'small', UIColors.WARNING, Align.CENTER)
            self.phase_complete[3] = True
            inst_text, inst_color = "Press ENTER to confirm bed selection", UIColors.SUCCESS
        else:
            inst_text, inst_color = "Click on a bed card to select it", UIColors.TEXT_SECONDARY

        inst_y = container.bottom - m.padding_lg * 2
        self.ui.draw_text(screen, inst_text, (container.centerx, inst_y),
                         'small', inst_color, Align.CENTER)

    def _draw_phase4_sleep(self, screen):
        """Draw sleep animation with fade"""
        m = self.ui.metrics
        w, h = screen.get_size()

        self.sleep_animation_timer += 0.016

        # Calculate fade alpha
        if self.sleep_animation_timer < 2:
            self.sleep_fade_alpha = int((self.sleep_animation_timer / 2) * 255)
        elif self.sleep_animation_timer < 4:
            self.sleep_fade_alpha = 255
        elif self.sleep_animation_timer < 6:
            self.sleep_fade_alpha = int((1 - (self.sleep_animation_timer - 4) / 2) * 255)
        else:
            self.sleep_fade_alpha = 0
            self.phase_complete[4] = True

        # Draw fade overlay
        if self.sleep_fade_alpha > 0:
            fade_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, self.sleep_fade_alpha))
            screen.blit(fade_surface, (0, 0))

        # Show text during middle phase
        if 2 <= self.sleep_animation_timer < 4:
            center_y = h // 2

            self.ui.draw_text(screen, "Night 1 at the Shelter",
                             (w // 2, center_y - m.grid * 8), 'title', UIColors.TEXT_LIGHT, Align.CENTER)

            self.ui.draw_text(screen, f"Bed #{self.selected_bed}",
                             (w // 2, center_y - m.grid * 3), 'heading', UIColors.TEXT_MUTED, Align.CENTER)

            # Time progression
            elapsed = self.sleep_animation_timer - 2
            if elapsed < 0.5:
                time_text = "10:00 PM - Lights Out"
            elif elapsed < 1.0:
                time_text = "12:00 AM - Midnight"
            elif elapsed < 1.5:
                time_text = "3:00 AM - Still Dark"
            else:
                time_text = "5:30 AM - Wake Up Call"

            self.ui.draw_text(screen, time_text,
                             (w // 2, center_y + m.grid * 3), 'subheading', (200, 200, 150), Align.CENTER)

            self.ui.draw_text(screen, "Day 1 Complete - 29 Days Remaining",
                             (w // 2, center_y + m.grid * 10), 'body', UIColors.TEXT_MUTED, Align.CENTER)

        # Auto-complete
        if self.sleep_animation_timer >= 6.5:
            self.complete_checkin()

    # === Event Handlers ===

    def handle_mouse_click(self, pos, button):
        if not self.active or button != 1:
            return

        if self.current_phase == 1:
            for field_name, field_data in self.form_fields.items():
                if field_data["rect"] and field_data["rect"].collidepoint(pos):
                    if self.active_field and self.active_field in self.form_fields:
                        prev = self.form_fields[self.active_field]
                        if prev["value"].strip():
                            prev["filled"] = True
                    self.active_field = field_name
                    if field_name == "emergency_contact":
                        self.shake_timer = 1.0
                    return

        elif self.current_phase == 2:
            for i, rule in enumerate(self.shelter_rules):
                if rule["rect"] and rule["rect"].collidepoint(pos):
                    rule["acknowledged"] = not rule["acknowledged"]
                    return

        elif self.current_phase == 3:
            for bed_num, bed_rect in self.bed_rects.items():
                if bed_rect.collidepoint(pos):
                    self.selected_bed = bed_num
                    return

    def handle_mouse_motion(self, pos):
        if not self.active:
            return

        self.hover_element = None

        if self.current_phase == 1:
            for field_name, field_data in self.form_fields.items():
                if field_data["rect"] and field_data["rect"].collidepoint(pos):
                    self.hover_element = field_name
                    break

        elif self.current_phase == 2:
            for i, rule in enumerate(self.shelter_rules):
                if rule["rect"] and rule["rect"].collidepoint(pos):
                    self.hover_element = f"rule_{i}"
                    break

        elif self.current_phase == 3:
            for bed_num, bed_rect in self.bed_rects.items():
                if bed_rect.collidepoint(pos):
                    self.hover_element = bed_num
                    break

    def handle_key(self, key):
        if not self.active:
            return

        if key == pygame.K_ESCAPE and self.current_phase > 1:
            self.current_phase -= 1
            return

        if key == pygame.K_RETURN:
            if self.current_phase == 1:
                if all(f["value"].strip() for f in self.form_fields.values()):
                    for f in self.form_fields.values():
                        f["filled"] = True
                    self.current_phase = 2
                    self.active_field = None
                else:
                    self.shake_timer = 0.5
                return

            elif self.phase_complete[self.current_phase]:
                if self.current_phase < 4:
                    self.current_phase += 1
                    if self.current_phase == 4:
                        self.sleep_animation_timer = 0
                else:
                    self.complete_checkin()
                return

        # Text input for phase 1
        if self.current_phase == 1 and self.active_field:
            field = self.form_fields[self.active_field]

            if key == pygame.K_BACKSPACE:
                field["value"] = field["value"][:-1]
                return

            if len(field["value"]) < 30:
                char = None
                mods = pygame.key.get_mods()
                shift = mods & pygame.KMOD_SHIFT

                if 97 <= key <= 122:  # a-z
                    char = chr(key).upper() if shift else chr(key)
                elif 48 <= key <= 57:  # 0-9
                    char = chr(key)
                elif key == 32:  # space
                    char = ' '

                if char:
                    field["value"] += char

    def handle_text_input(self, unicode_char):
        if not self.active or self.current_phase != 1 or not self.active_field:
            return

        field = self.form_fields[self.active_field]
        if unicode_char.isprintable() and len(field["value"]) < 30:
            field["value"] += unicode_char

    def complete_checkin(self):
        """Complete the shelter check-in"""
        pygame.key.stop_text_input()

        if self.narrative_ref:
            self.narrative_ref.intake_complete = True
            self.narrative_ref.bed_assigned = True
            self.narrative_ref.assigned_bed = self.selected_bed
            self.narrative_ref.days_remaining = 30

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            bed_narratives = {
                12: "Bed 12, near the bathroom. The constant noise will make sleep difficult.",
                23: "Bed 23, by the entrance door. Cold drafts and constant foot traffic.",
                31: "Bed 31, tucked in the corner. Feels safer but darker here.",
                38: "Bed 38, right in the middle row. No privacy whatsoever.",
                40: "Bed 40, near the staff desk. They'll keep an eye on you."
            }

            bed_message = bed_narratives.get(self.selected_bed, f"Bed {self.selected_bed}.")
            self.narrative_ref.dialogue_box.show(None, f"{bed_message}\n\nYou're officially checked in.")

        self.complete()

    def update(self, dt):
        if not self.active:
            return
        self.animation_timer += dt
        if self.shake_timer > 0:
            self.shake_timer -= dt
