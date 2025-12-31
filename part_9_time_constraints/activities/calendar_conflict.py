"""
Calendar Conflict Mini-Game - Clean Version
Drag notifications into calendar slots - all three overlap at 3pm
Shows the impossibility of managing conflicting responsibilities
Clean visuals, no heavy effects
"""
import pygame
import math

from .time_visual_base import (
    PressureUIColors, PressureUIMetrics, PressureVisualHelpers,
    UIAnimation, pressure_visuals
)
from .time_particles import time_particles
from .time_feedback import time_feedback


class CalendarConflict:
    """Calendar scheduling game where all events overlap - Clean version"""

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

        # Clear feedback
        time_particles.clear()
        time_feedback.clear()

    def stop(self):
        """Stop the game"""
        self.active = False

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        self.time += dt
        self.clock_time += dt * self.clock_speed

        # Check if all placed
        if all(n["placed"] for n in self.notifications) and not self.all_placed:
            self.all_placed = True
            self.show_conflict = True
            time_feedback.add_time_conflict_banner()
            time_feedback.set_stress_level(0.8)

        # Conflict animation
        if self.show_conflict:
            self.conflict_timer += dt
            self.clock_speed = 3.0  # Speed up clock

            if self.conflict_timer > 3.5:
                self.show_result = True
                time_feedback.add_no_good_options_banner()

        # Result timer
        if self.show_result:
            self.result_timer += dt
            time_feedback.set_stress_level(0.5)
            if self.result_timer > 4.0:
                self.completed = True
                self.active = False

        # Update feedback
        time_feedback.update(dt)

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
        """Render the calendar game with clean visuals"""
        self._render_content(screen)

        # Render feedback on top
        time_feedback.render(screen)

    def _render_content(self, screen):
        """Render main game content"""
        # Background with stress tint
        stress = 0.3 if not self.show_conflict else 0.7
        pressure_visuals.draw_background(screen, stress)

        # Simple clock in corner
        self._render_clock(screen)

        # Title
        title_color = PressureUIColors.TEXT_PRIMARY
        if self.show_conflict:
            title_color = PressureUIColors.PRESSURE_RED_LIGHT
        pressure_visuals.draw_title(screen, "Schedule Your Day",
                                    self.SCREEN_WIDTH // 2, 35)

        # Instructions
        inst_text = "Drag each notification to a time slot"
        if self.show_conflict:
            inst_text = "All events overlap at the same time!"
        inst_color = PressureUIColors.TEXT_SECONDARY
        if self.show_conflict:
            inst_color = PressureUIColors.PRESSURE_RED_LIGHT
        inst_surface = pressure_visuals.fonts['body'].render(inst_text, True, inst_color)
        screen.blit(inst_surface,
                   (self.SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, 75))

        # Section labels
        notif_label = pressure_visuals.fonts['heading'].render(
            "Notifications", True, PressureUIColors.TEXT_PRIMARY
        )
        screen.blit(notif_label, (40 + self.card_width // 2 - notif_label.get_width() // 2, 145))

        cal_label = pressure_visuals.fonts['heading'].render(
            "Calendar", True, PressureUIColors.TEXT_PRIMARY
        )
        screen.blit(cal_label, (580 - cal_label.get_width() // 2, 145))

        # Draw calendar slots
        for i, slot_item in enumerate(self.slot_rects):
            slot = slot_item["slot"]
            rect = slot_item["rect"]

            is_hover = (self.hover_slot == slot_item)
            is_conflict = slot["conflict"] and len(slot_item["items"]) > 1
            is_flashing = self.show_conflict and slot["conflict"]

            self._render_calendar_slot(screen, rect, slot["time"],
                                       is_conflict, is_hover,
                                       len(slot_item["items"]) > 0,
                                       is_flashing)

        # Draw notification cards (non-dragging first)
        for i, item in enumerate(self.notification_rects):
            if item == self.dragging:
                continue
            self._render_notification_card(screen, item, is_dragging=False)

        # Draw dragging card on top
        if self.dragging:
            self._render_notification_card(screen, self.dragging, is_dragging=True)

        # Show result overlay
        if self.show_result:
            self._render_result(screen)

    def _render_clock(self, screen):
        """Render simple clock"""
        center = (self.SCREEN_WIDTH - 70, 70)
        radius = 40

        # Clock face
        pygame.draw.circle(screen, PressureUIColors.PANEL_BG, center, radius)
        pygame.draw.circle(screen, PressureUIColors.BORDER_DEFAULT, center, radius, 2)

        # Hour marks
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            inner = radius - 8
            outer = radius - 3
            x1 = center[0] + int(math.cos(angle) * inner)
            y1 = center[1] + int(math.sin(angle) * inner)
            x2 = center[0] + int(math.cos(angle) * outer)
            y2 = center[1] + int(math.sin(angle) * outer)
            pygame.draw.line(screen, PressureUIColors.TEXT_MUTED, (x1, y1), (x2, y2), 2)

        # Clock hands
        minute_angle = math.radians((self.clock_time * 6) % 360 - 90)
        hour_angle = math.radians((self.clock_time * 0.5) % 360 - 90)

        # Minute hand
        mx = center[0] + int(math.cos(minute_angle) * (radius - 12))
        my = center[1] + int(math.sin(minute_angle) * (radius - 12))
        pygame.draw.line(screen, PressureUIColors.TEXT_PRIMARY, center, (mx, my), 2)

        # Hour hand
        hx = center[0] + int(math.cos(hour_angle) * (radius - 20))
        hy = center[1] + int(math.sin(hour_angle) * (radius - 20))
        pygame.draw.line(screen, PressureUIColors.TIME_GOLD, center, (hx, hy), 3)

        # Center dot
        pygame.draw.circle(screen, PressureUIColors.TIME_GOLD, center, 4)

    def _render_calendar_slot(self, screen, rect, time_text, is_conflict,
                              is_hover, is_filled, is_flashing):
        """Render a calendar slot"""
        # Background color
        if is_conflict:
            bg_color = PressureUIColors.PRESSURE_RED_DARK
        elif is_filled:
            bg_color = PressureUIColors.PANEL_BG_LIGHT
        else:
            bg_color = PressureUIColors.PANEL_BG

        # Draw slot
        pygame.draw.rect(screen, bg_color, rect, border_radius=8)

        # Border
        if is_flashing:
            pulse = PressureVisualHelpers.get_pulse_alpha(180, 255, 4.0)
            border_color = PressureUIColors.PRESSURE_RED
        elif is_hover:
            border_color = PressureUIColors.BORDER_HOVER
        elif is_conflict:
            border_color = PressureUIColors.PRESSURE_RED
        else:
            border_color = PressureUIColors.BORDER_DEFAULT

        border_width = 3 if (is_flashing or is_conflict) else 2
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)

        # Time label
        time_color = PressureUIColors.PRESSURE_RED_LIGHT if is_conflict else PressureUIColors.TEXT_PRIMARY
        time_surface = pressure_visuals.fonts['body_bold'].render(time_text, True, time_color)
        screen.blit(time_surface, (rect.x + 10, rect.y + 8))

        # Conflict indicator
        if is_conflict and is_filled:
            conflict_text = "⚠ CONFLICT"
            conflict_surface = pressure_visuals.fonts['small'].render(
                conflict_text, True, PressureUIColors.PRESSURE_RED_LIGHT
            )
            screen.blit(conflict_surface, (rect.right - conflict_surface.get_width() - 10, rect.y + 10))

    def _render_notification_card(self, screen, item, is_dragging=False):
        """Render a notification card"""
        notif = item["notif"]
        rect = item["rect"]

        is_hover = (item == self.hover_card)
        is_placed = notif["placed"]

        # Background
        if is_dragging:
            bg_color = PressureUIColors.PANEL_BG_LIGHT
        elif is_placed:
            bg_color = tuple(c // 2 for c in PressureUIColors.PANEL_BG)
        elif is_hover:
            bg_color = PressureUIColors.PANEL_BG_LIGHT
        else:
            bg_color = PressureUIColors.PANEL_BG

        # Shadow for dragging
        if is_dragging:
            shadow_rect = rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 60), (0, 0, shadow_rect.width, shadow_rect.height),
                           border_radius=8)
            screen.blit(shadow_surf, shadow_rect)

        # Card background
        pygame.draw.rect(screen, bg_color, rect, border_radius=8)

        # Border
        border_color = notif["color"] if not is_placed else PressureUIColors.BORDER_DEFAULT
        if is_hover:
            border_color = PressureUIColors.BORDER_HOVER
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)

        # Icon circle
        icon_center = (rect.x + 30, rect.centery)
        pygame.draw.circle(screen, notif["color"], icon_center, 18)
        icon_text = pressure_visuals.fonts['body_bold'].render(notif["icon"], True, PressureUIColors.DARK_BG)
        screen.blit(icon_text, (icon_center[0] - icon_text.get_width() // 2,
                                icon_center[1] - icon_text.get_height() // 2))

        # Name and time
        name_color = PressureUIColors.TEXT_PRIMARY if not is_placed else PressureUIColors.TEXT_MUTED
        name_surface = pressure_visuals.fonts['body_bold'].render(notif["name"], True, name_color)
        screen.blit(name_surface, (rect.x + 55, rect.y + 15))

        time_surface = pressure_visuals.fonts['body'].render(notif["time"], True, notif["color"])
        screen.blit(time_surface, (rect.x + 55, rect.y + 38))

        # Description
        desc_color = PressureUIColors.TEXT_MUTED
        desc_surface = pressure_visuals.fonts['small'].render(notif["description"], True, desc_color)
        screen.blit(desc_surface, (rect.x + 55, rect.y + 62))

        # Priority badge
        if not is_placed:
            priority_text = notif["priority"]
            priority_surface = pressure_visuals.fonts['small'].render(priority_text, True, notif["color"])
            badge_x = rect.right - priority_surface.get_width() - 10
            screen.blit(priority_surface, (badge_x, rect.y + 8))

    def _render_result(self, screen):
        """Render the result overlay"""
        # Darken overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = min(180, int(self.result_timer * 150))
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        # Result panel
        panel_rect = pygame.Rect(125, 180, 550, 240)

        # Panel background
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, panel_rect, border_radius=12)
        pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED, panel_rect, 3, border_radius=12)

        # Title
        title_surface = pressure_visuals.fonts['heading'].render(
            "You Cannot Attend Everything", True, PressureUIColors.PRESSURE_RED_LIGHT
        )
        screen.blit(title_surface, (panel_rect.centerx - title_surface.get_width() // 2,
                                    panel_rect.y + 30))

        # Conflict details
        if self.result_timer > 0.5:
            details = [
                ("Work shift:", "3:00 PM", PressureUIColors.CALM_BLUE_LIGHT),
                ("Program meeting:", "3:00 PM", PressureUIColors.URGENT_ORANGE),
                ("Therapy:", "3:30 PM", PressureUIColors.STRESS_PURPLE_LIGHT)
            ]
            for i, (label, time, color) in enumerate(details):
                y = panel_rect.y + 80 + i * 30
                text = f"{label} {time}"
                text_surf = pressure_visuals.fonts['body'].render(text, True, color)
                screen.blit(text_surf, (panel_rect.centerx - text_surf.get_width() // 2, y))

        # Final message
        if self.result_timer > 1.5:
            pulse = PressureVisualHelpers.get_pulse_alpha(200, 255, 5.0)
            choose_surface = pressure_visuals.fonts['heading'].render(
                "Choose ONE.", True, PressureUIColors.PRESSURE_RED_LIGHT
            )
            choose_surface.set_alpha(pulse)
            screen.blit(choose_surface, (panel_rect.centerx - choose_surface.get_width() // 2,
                                         panel_rect.y + 190))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)
