"""
Calendar Conflict Mini-Game - Pressure/Urgency Version
Drag notifications into calendar slots - all three overlap at 3pm
Shows the impossibility of managing conflicting responsibilities
Features: Clock animation, conflict pulses, stress vignette, professional styling
"""
import pygame
import math
import random

from .time_visual_base import (
    PressureUIColors, PressureUIMetrics, PressureVisualHelpers,
    PressureVisualComponents, UIAnimation, pressure_visuals
)
from .time_particles import pressure_particles
from .time_feedback import pressure_feedback


class CalendarConflict:
    """Calendar scheduling game where all events overlap - Pressure themed"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Notifications to schedule with icons
        self.notifications = [
            {
                "name": "Work Shift",
                "time": "3:00 PM",
                "color": PressureUIColors.CALM_BLUE_LIGHT,
                "icon": "W",
                "icon_color": PressureUIColors.CALM_BLUE,
                "description": "Mandatory shift - need the money",
                "placed": False,
                "slot": None,
                "priority": "URGENT"
            },
            {
                "name": "Program Meeting",
                "time": "3:00 PM",
                "color": PressureUIColors.URGENT_ORANGE,
                "icon": "P",
                "icon_color": PressureUIColors.URGENT_ORANGE_DARK,
                "description": "Mandatory - benefits depend on it",
                "placed": False,
                "slot": None,
                "priority": "REQUIRED"
            },
            {
                "name": "Therapy Session",
                "time": "3:30 PM",
                "color": PressureUIColors.STRESS_PURPLE_LIGHT,
                "icon": "T",
                "icon_color": PressureUIColors.STRESS_PURPLE,
                "description": "Mental health appointment",
                "placed": False,
                "slot": None,
                "priority": "IMPORTANT"
            }
        ]

        # Notification card positions and rects
        self.notification_rects = []
        self.card_width = 200
        self.card_height = 90

        # Calendar time slots
        self.time_slots = [
            {"time": "2:00 PM", "y": 180, "conflict": False},
            {"time": "3:00 PM", "y": 265, "conflict": True},
            {"time": "4:00 PM", "y": 350, "conflict": False},
            {"time": "5:00 PM", "y": 435, "conflict": False},
        ]
        self.slot_rects = []

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)
        self.hover_slot = None
        self.hover_card = None

        # Game state
        self.show_conflict = False
        self.conflict_timer = 0
        self.all_placed = False
        self.time = 0

        # Result
        self.show_result = False
        self.result_timer = 0

        # Clock animation
        self.clock_time = 0
        self.clock_speed = 1.0

        # Animation states
        self.card_animations = []

    def start(self):
        """Start the calendar game"""
        self.active = True
        self.completed = False
        self.show_conflict = False
        self.conflict_timer = 0
        self.show_result = False
        self.result_timer = 0
        self.dragging = None
        self.hover_slot = None
        self.hover_card = None
        self.all_placed = False
        self.time = 0
        self.clock_time = 0
        self.clock_speed = 1.0

        # Reset notifications
        for notif in self.notifications:
            notif["placed"] = False
            notif["slot"] = None

        # Initialize notification positions (left side)
        start_x = 40
        start_y = 175
        self.notification_rects = []
        self.card_animations = []
        for i, notif in enumerate(self.notifications):
            rect = pygame.Rect(
                start_x,
                start_y + i * (self.card_height + 15),
                self.card_width,
                self.card_height
            )
            self.notification_rects.append({
                "notif": notif,
                "rect": rect,
                "original_pos": (rect.x, rect.y)
            })
            self.card_animations.append(UIAnimation(
                phase=i * 0.5,
                speed=0.8 + i * 0.1
            ))

        # Initialize calendar slot positions (right side)
        calendar_x = 420
        self.slot_rects = []
        for i, slot in enumerate(self.time_slots):
            rect = pygame.Rect(
                calendar_x,
                slot["y"],
                320,
                75
            )
            self.slot_rects.append({
                "slot": slot,
                "rect": rect,
                "items": []
            })

        # Initialize particles and feedback
        pressure_particles.clear()
        pressure_particles.enable_ambient(
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            stress_level=0.2
        )
        pressure_feedback.clear()

    def stop(self):
        """Stop the game"""
        self.active = False
        pressure_particles.disable_ambient()

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        self.time += dt
        self.clock_time += dt * self.clock_speed

        # Update animations
        for anim in self.card_animations:
            anim.update(dt)

        # Check if all placed
        if all(n["placed"] for n in self.notifications) and not self.all_placed:
            self.all_placed = True
            self.show_conflict = True

            # Trigger conflict effects
            conflict_slot = self.slot_rects[1]  # 3:00 PM slot
            pressure_particles.emit_conflict_pulse(
                conflict_slot["rect"].centerx,
                conflict_slot["rect"].centery
            )
            pressure_particles.emit_alarm_particles(
                conflict_slot["rect"].centerx,
                conflict_slot["rect"].centery,
                count=12
            )
            pressure_feedback.add_time_conflict_banner()
            pressure_feedback.trigger_screen_shake(10)
            pressure_feedback.set_stress_level(0.8)

        # Conflict animation
        if self.show_conflict:
            self.conflict_timer += dt
            self.clock_speed = 3.0  # Speed up clock

            # Increase stress particles
            pressure_particles.set_stress_level(0.9)

            # Periodic conflict pulses
            if int(self.conflict_timer * 2) != int((self.conflict_timer - dt) * 2):
                conflict_slot = self.slot_rects[1]
                pressure_particles.emit_overlap_warning(conflict_slot["rect"])

            if self.conflict_timer > 3.5:
                self.show_result = True
                pressure_feedback.add_no_good_options_banner()

        # Result timer
        if self.show_result:
            self.result_timer += dt
            pressure_feedback.set_stress_level(0.5)
            if self.result_timer > 4.0:
                self.completed = True
                self.active = False

        # Emit drag trail
        if self.dragging:
            rect = self.dragging["rect"]
            pressure_particles.emit_drag_trail(
                rect.centerx, rect.centery,
                self.dragging["notif"]["color"]
            )

        # Update particles and feedback
        pressure_particles.update(dt)
        pressure_feedback.update(dt)

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_result:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Check if clicking on a notification card
            for item in self.notification_rects:
                if item["rect"].collidepoint(pos) and not item["notif"]["placed"]:
                    self.dragging = item
                    self.drag_offset = (
                        pos[0] - item["rect"].x,
                        pos[1] - item["rect"].y
                    )
                    # Selection burst
                    pressure_particles.emit_selection_burst(
                        item["rect"].centerx,
                        item["rect"].centery,
                        item["notif"]["color"]
                    )
                    break

        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos

            if self.dragging:
                self.dragging["rect"].x = pos[0] - self.drag_offset[0]
                self.dragging["rect"].y = pos[1] - self.drag_offset[1]

                # Update hover slot
                self.hover_slot = None
                for slot_item in self.slot_rects:
                    if slot_item["rect"].colliderect(self.dragging["rect"]):
                        self.hover_slot = slot_item
                        break
            else:
                # Update hover card
                self.hover_card = None
                for item in self.notification_rects:
                    if item["rect"].collidepoint(pos) and not item["notif"]["placed"]:
                        self.hover_card = item
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                notif = self.dragging["notif"]
                rect = self.dragging["rect"]

                # Check if dropped in a slot
                dropped = False
                for slot_item in self.slot_rects:
                    if slot_item["rect"].colliderect(rect):
                        # Place in slot
                        notif["placed"] = True
                        notif["slot"] = slot_item["slot"]["time"]
                        slot_item["items"].append(notif)

                        # Position in slot
                        offset_y = len(slot_item["items"]) * 8
                        rect.x = slot_item["rect"].x + 10
                        rect.y = slot_item["rect"].y + 8 + offset_y
                        dropped = True

                        # Placement effect
                        pressure_particles.emit_clock_ticks(
                            (rect.centerx, rect.centery), 30, 8
                        )
                        pressure_feedback.add_clock_pulse(
                            rect.centerx, rect.centery, 50
                        )

                        # Check if this creates a conflict (3pm slot)
                        if slot_item["slot"]["conflict"] and len(slot_item["items"]) > 1:
                            pressure_feedback.trigger_screen_flash(
                                PressureUIColors.PRESSURE_RED, 80
                            )
                            pressure_particles.emit_alarm_particles(
                                slot_item["rect"].centerx,
                                slot_item["rect"].centery, 5
                            )
                        break

                if not dropped:
                    # Return to original position
                    rect.x = self.dragging["original_pos"][0]
                    rect.y = self.dragging["original_pos"][1]

                self.dragging = None
                self.hover_slot = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.show_conflict:
                    self.show_result = True

    def render(self, screen):
        """Render the calendar game with pressure visuals"""
        # Get screen shake offset
        shake_offset = pressure_feedback.get_screen_shake_offset()

        # Create shifted surface for shake effect
        if shake_offset != (0, 0):
            temp_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self._render_content(temp_surface)
            screen.fill(PressureUIColors.DARK_BG)
            screen.blit(temp_surface, shake_offset)
        else:
            self._render_content(screen)

        # Render particles and feedback (not affected by shake)
        pressure_particles.render(screen)
        pressure_feedback.render(screen)

    def _render_content(self, screen):
        """Render main game content"""
        # Background with pressure gradient
        pressure_visuals.draw_pressure_background(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            stress_level=0.3 if not self.show_conflict else 0.7
        )

        # Clock in corner
        clock_center = (self.SCREEN_WIDTH - 70, 70)
        clock_minutes = (self.clock_time * 2) % 60
        pressure_visuals.draw_clock_face(
            screen, clock_center, 45, clock_minutes
        )

        # Title with warning glow if conflict
        title_color = PressureUIColors.HIGHLIGHT_WHITE
        title_glow = PressureUIColors.TIME_GOLD
        if self.show_conflict:
            title_glow = PressureUIColors.PRESSURE_RED

        PressureVisualHelpers.draw_text_with_glow(
            screen, "Schedule Your Day",
            (self.SCREEN_WIDTH // 2, 35),
            pressure_visuals.fonts['title'],
            title_color, title_glow
        )

        # Instructions
        inst_text = "Drag each notification to a time slot"
        if self.show_conflict:
            inst_text = "All events overlap at the same time!"
        PressureVisualHelpers.draw_text_with_glow(
            screen, inst_text,
            (self.SCREEN_WIDTH // 2, 75),
            pressure_visuals.fonts['small'],
            PressureUIColors.HIGHLIGHT_DIM,
            PressureUIColors.CALM_BLUE
        )

        # Section labels
        PressureVisualHelpers.draw_text_with_glow(
            screen, "Notifications",
            (40 + self.card_width // 2, 145),
            pressure_visuals.fonts['heading'],
            PressureUIColors.HIGHLIGHT_WHITE,
            PressureUIColors.URGENT_ORANGE
        )

        PressureVisualHelpers.draw_text_with_glow(
            screen, "Calendar",
            (580, 145),
            pressure_visuals.fonts['heading'],
            PressureUIColors.HIGHLIGHT_WHITE,
            PressureUIColors.TIME_GOLD
        )

        # Draw calendar slots
        for i, slot_item in enumerate(self.slot_rects):
            slot = slot_item["slot"]
            rect = slot_item["rect"]

            is_hover = (self.hover_slot == slot_item)
            is_conflict = slot["conflict"] and len(slot_item["items"]) > 1
            is_flashing = self.show_conflict and slot["conflict"]

            pressure_visuals.draw_calendar_slot(
                screen, rect, slot["time"],
                is_conflict=is_conflict,
                is_hover=is_hover,
                is_filled=len(slot_item["items"]) > 0,
                flash_phase=self.conflict_timer * 4 if is_flashing else 0
            )

        # Draw notification cards (non-dragging first)
        for i, item in enumerate(self.notification_rects):
            if item == self.dragging:
                continue
            self._render_notification_card(screen, item, i)

        # Draw dragging card on top
        if self.dragging:
            idx = self.notification_rects.index(self.dragging)
            self._render_notification_card(screen, self.dragging, idx, is_dragging=True)

        # Show result overlay
        if self.show_result:
            self._render_result(screen)

    def _render_notification_card(self, screen, item, index, is_dragging=False):
        """Render a notification card with pressure styling"""
        notif = item["notif"]
        rect = item["rect"]

        is_hover = (item == self.hover_card)
        is_placed = notif["placed"]

        # Get float offset from animation
        float_offset = 0
        if not is_placed and not is_dragging and index < len(self.card_animations):
            float_offset = int(math.sin(self.card_animations[index].phase) * 3)

        draw_rect = pygame.Rect(rect.x, rect.y + float_offset, rect.width, rect.height)

        pressure_visuals.draw_notification_card(
            screen, draw_rect,
            notif["name"],
            notif["time"],
            notif["description"],
            notif["color"],
            icon=notif["icon"],
            priority=notif["priority"],
            is_dragging=is_dragging,
            is_hover=is_hover
        )

    def _render_result(self, screen):
        """Render the result overlay"""
        # Darken overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = min(180, int(self.result_timer * 150))
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        # Result panel
        panel_rect = pygame.Rect(125, 180, 550, 240)
        pressure_visuals.draw_pressure_panel(
            screen, panel_rect,
            glow_color=PressureUIColors.PRESSURE_RED,
            glow_intensity=0.6
        )

        # Title
        result_alpha = min(255, int(self.result_timer * 200))
        PressureVisualHelpers.draw_text_with_glow(
            screen, "You Cannot Attend Everything",
            (panel_rect.centerx, panel_rect.y + 40),
            pressure_visuals.fonts['heading'],
            PressureUIColors.PRESSURE_RED_LIGHT,
            PressureUIColors.PRESSURE_RED
        )

        # Conflict details
        if self.result_timer > 0.5:
            details = [
                ("Work shift:", "3:00 PM", PressureUIColors.CALM_BLUE_LIGHT),
                ("Program meeting:", "3:00 PM", PressureUIColors.URGENT_ORANGE),
                ("Therapy:", "3:30 PM", PressureUIColors.STRESS_PURPLE_LIGHT)
            ]
            for i, (label, time, color) in enumerate(details):
                y = panel_rect.y + 90 + i * 30
                text = f"{label} {time}"
                text_surf = pressure_visuals.fonts['body'].render(text, True, color)
                screen.blit(text_surf, (panel_rect.centerx - text_surf.get_width() // 2, y))

        # Final message
        if self.result_timer > 1.5:
            pulse = 0.8 + math.sin(self.time * 5) * 0.2
            choose_color = tuple(int(c * pulse) for c in PressureUIColors.PRESSURE_RED_LIGHT)
            PressureVisualHelpers.draw_text_with_glow(
                screen, "Choose ONE.",
                (panel_rect.centerx, panel_rect.y + 200),
                pressure_visuals.fonts['heading'],
                choose_color,
                PressureUIColors.PRESSURE_RED
            )

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)
