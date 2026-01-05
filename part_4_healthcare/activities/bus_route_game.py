"""
Bus Route Selection Mini-Game
Choose the correct bus route within 20 seconds to make appointment
Enhanced with visual polish: arc timer, button animations, particles, popups
"""
import pygame
import random
import math
import time

from part_4_healthcare.activities.healthcare_visual_base import (
    HealthcareUIColors, HealthcareUIMetrics, HealthcareVisualHelpers,
    HealthcareVisualComponents, UIAnimation, healthcare_visuals
)
from part_4_healthcare.activities.healthcare_particle_effects import healthcare_particles
from part_4_healthcare.activities.healthcare_feedback_popups import healthcare_feedback


class BusRouteGame:
    """Select the correct bus within time limit or miss appointment"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.failed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 20.0  # seconds
        self.time_remaining = self.time_limit
        self.last_warning_time = 0  # For warning particle emission

        # Bus routes
        self.bus_routes = [
            {'number': '14', 'route': 'Downtown → West Side', 'stops': 'School, Mall, Hospital'},
            {'number': '27', 'route': 'North Loop', 'stops': 'University, Park, Library'},
            {'number': '38', 'route': 'Cross-Town Express', 'stops': 'School, Clinic, Downtown'},
            {'number': '42', 'route': 'South Central', 'stops': 'Mall, Apartments, Market'},
            {'number': '51', 'route': 'East Circle', 'stops': 'Station, School, Shops'},
            {'number': '63', 'route': 'Medical District', 'stops': 'Hospital, Clinic, Pharmacy'}
        ]

        # Correct route (38 goes to clinic)
        self.correct_route_index = 2

        # UI elements
        self.route_buttons = []
        self.create_route_buttons()

        # Button animations
        self.button_scales = [UIAnimation(1.0, 1.0, 0.2) for _ in self.bus_routes]
        self.button_fade_delays = [i * 0.1 for i in range(len(self.bus_routes))]  # Staggered fade-in
        self.buttons_visible = False
        self.fade_in_timer = 0

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0
        self.instruction_alpha = UIAnimation(0.0, 255.0, 0.1)

        # Result display
        self.show_result = False
        self.result_timer = 0
        self.result_scale = UIAnimation(0.0, 1.0, 0.15)

        # Destination info
        self.destination = "Community Health Clinic"
        self.current_location = "School"

        # Screen shake for wrong answer
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_timer = 0

    def create_route_buttons(self):
        """Create clickable bus route buttons"""
        self.route_buttons = []

        # Arrange in 2 columns, 3 rows
        for i, route in enumerate(self.bus_routes):
            col = i % 2
            row = i // 2

            x = 340 + col * 300
            y = 250 + row * 120
            rect = pygame.Rect(x, y, 280, 100)

            self.route_buttons.append({
                'rect': rect,
                'base_rect': rect.copy(),  # Keep original for scaling
                'route': route,
                'index': i,
                'selected': False,
                'hover': False,
                'pressed': False
            })

    def handle_event(self, event):
        """Handle bus selection"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEMOTION:
            # Update hover states
            for i, button in enumerate(self.route_buttons):
                was_hover = button['hover']
                button['hover'] = button['rect'].collidepoint(mouse_pos)

                # Scale animation on hover
                if button['hover'] and not was_hover:
                    self.button_scales[i].target = 1.05
                elif not button['hover'] and was_hover:
                    self.button_scales[i].target = 1.0

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check bus selection
            for i, button in enumerate(self.route_buttons):
                if button['rect'].collidepoint(mouse_pos):
                    button['pressed'] = True
                    self.button_scales[i].target = 0.95  # Press shrink

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Release and check selection
            for i, button in enumerate(self.route_buttons):
                if button['pressed'] and button['rect'].collidepoint(mouse_pos):
                    button['selected'] = True
                    self.button_scales[i].target = 1.0

                    # Calculate time bonus
                    time_bonus = int(self.time_remaining)

                    # Check if correct
                    if button['index'] == self.correct_route_index:
                        self.completed = True
                        self.show_result = True
                        self.result_timer = 150
                        self.result_scale.current = 0.0
                        self.result_scale.target = 1.0

                        # Success effects
                        center_x = self.SCREEN_WIDTH // 2
                        center_y = self.SCREEN_HEIGHT // 2
                        healthcare_particles.emit_confetti(center_x, center_y, count=40)
                        healthcare_particles.emit_success(button['rect'].centerx, button['rect'].centery, count=20)

                        # Popups
                        healthcare_feedback.add_correct(button['rect'].centerx, button['rect'].centery - 30)
                        if time_bonus >= 10:
                            healthcare_feedback.add_time_bonus(center_x, center_y + 50, time_bonus)

                        # Achievement
                        healthcare_feedback.add_bus_caught(on_time=True)

                    else:
                        self.failed = True
                        self.completed = True
                        self.show_result = True
                        self.result_timer = 150
                        self.result_scale.current = 0.0
                        self.result_scale.target = 1.0

                        # Error effects
                        healthcare_particles.emit_error(button['rect'].centerx, button['rect'].centery, count=15)
                        healthcare_feedback.add_incorrect(button['rect'].centerx, button['rect'].centery - 30)

                        # Screen shake
                        self.shake_timer = 0.3

                        # Achievement
                        healthcare_feedback.add_bus_caught(on_time=False)

                    break

                button['pressed'] = False

        return True

    def update(self, dt):
        """Update timer and game state"""
        # Update particles and popups
        healthcare_particles.update(dt)
        healthcare_feedback.update(dt)

        # Update button scale animations
        for scale_anim in self.button_scales:
            scale_anim.update(dt)

        # Update screen shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            intensity = self.shake_timer * 20
            self.shake_offset_x = random.uniform(-intensity, intensity)
            self.shake_offset_y = random.uniform(-intensity, intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        if not self.active or self.completed:
            if self.show_result and self.result_timer > 0:
                self.result_timer -= 1
                self.result_scale.update(dt)
            return

        # Fade in buttons
        self.fade_in_timer += dt
        if self.fade_in_timer > 0.3:
            self.buttons_visible = True

        # Update instruction animation
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer < 0.5:
                self.instruction_alpha.target = 255
            if self.instruction_timer > 3:
                self.instruction_alpha.target = 0
            if self.instruction_timer > 4:
                self.show_instructions = False
        self.instruction_alpha.update(dt)

        # Update countdown timer
        self.time_remaining -= dt

        # Emit warning particles when low on time
        if self.time_remaining < 5 and self.time_remaining > 0:
            if time.time() - self.last_warning_time > 0.3:
                timer_x = self.SCREEN_WIDTH // 2
                timer_y = 180
                healthcare_particles.emit_timer_warning(timer_x, timer_y)
                self.last_warning_time = time.time()

        # Check for timeout
        if self.time_remaining <= 0:
            self.failed = True
            self.completed = True
            self.show_result = True
            self.result_timer = 150
            self.result_scale.current = 0.0
            self.result_scale.target = 1.0
            self.time_remaining = 0

            # Timeout effects
            center_x = self.SCREEN_WIDTH // 2
            center_y = self.SCREEN_HEIGHT // 2
            healthcare_particles.emit_error(center_x, center_y, count=20)
            healthcare_feedback.add_text(center_x, center_y - 50, "TIME'S UP!",
                                        HealthcareUIColors.ERROR, 'large', 2.0)
            healthcare_feedback.add_bus_caught(on_time=False)

            self.shake_timer = 0.4

    def render(self, screen):
        """Render the bus route selection interface"""
        if not self.active:
            return

        # Apply screen shake
        shake_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Background with gradient
        HealthcareVisualHelpers.draw_gradient_rect(
            shake_surface,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            (20, 30, 50),
            (10, 15, 25)
        )

        # Title with shadow
        title_font = pygame.font.Font(None, 48)
        title_text = "QUICK! Select the Right Bus!"

        # Title shadow
        shadow_surface = title_font.render(title_text, True, (0, 0, 0))
        shake_surface.blit(shadow_surface, (self.SCREEN_WIDTH//2 - shadow_surface.get_width()//2 + 2, 52))

        # Title text
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        shake_surface.blit(title_surface, (self.SCREEN_WIDTH//2 - title_surface.get_width()//2, 50))

        # ESC hint
        esc_font = pygame.font.Font(None, 24)
        esc_text = esc_font.render("Press ESC to exit", True, (100, 100, 110))
        shake_surface.blit(esc_text, (20, self.SCREEN_HEIGHT - 40))

        # Destination info panel
        info_panel_rect = pygame.Rect(self.SCREEN_WIDTH//2 - 250, 100, 500, 60)
        HealthcareVisualHelpers.draw_shadow(shake_surface, info_panel_rect, offset=4, alpha=40)
        pygame.draw.rect(shake_surface, (30, 40, 55), info_panel_rect, border_radius=10)
        pygame.draw.rect(shake_surface, HealthcareUIColors.HEALTHCARE_PRIMARY, info_panel_rect, 2, border_radius=10)

        info_font = pygame.font.Font(None, 28)
        location_text = info_font.render(f"From: {self.current_location}", True, (180, 180, 190))
        dest_text = info_font.render(f"To: {self.destination}", True, HealthcareUIColors.WARNING)
        shake_surface.blit(location_text, (info_panel_rect.x + 20, info_panel_rect.y + 10))
        shake_surface.blit(dest_text, (info_panel_rect.x + 20, info_panel_rect.y + 33))

        # Arc Timer
        timer_center = (self.SCREEN_WIDTH // 2, 200)
        timer_radius = 45
        healthcare_visuals.draw_timer_arc(
            shake_surface,
            timer_center,
            timer_radius,
            self.time_remaining,
            self.time_limit,
            show_text=True
        )

        # Timer label
        label_font = pygame.font.Font(None, 20)
        label_text = label_font.render("seconds", True, (120, 125, 140))
        shake_surface.blit(label_text, (timer_center[0] - label_text.get_width()//2, timer_center[1] + timer_radius + 10))

        if not self.show_result:
            # Bus route buttons with animations
            if self.buttons_visible:
                for i, button in enumerate(self.route_buttons):
                    self._render_button(shake_surface, button, i)

            # Instructions overlay
            if self.show_instructions and self.instruction_alpha.value > 5:
                alpha = int(self.instruction_alpha.value)
                inst_font = pygame.font.Font(None, 32)
                inst_text = inst_font.render("Click the bus that goes to the clinic!", True, (200, 255, 200))
                inst_text.set_alpha(alpha)

                # Background bar
                bar_rect = pygame.Rect(0, 580, self.SCREEN_WIDTH, 50)
                bar_surface = pygame.Surface((self.SCREEN_WIDTH, 50), pygame.SRCALPHA)
                bar_surface.fill((0, 0, 0, int(alpha * 0.6)))
                shake_surface.blit(bar_surface, (0, 580))

                shake_surface.blit(inst_text, (self.SCREEN_WIDTH//2 - inst_text.get_width()//2, 595))

        else:
            # Show result modal
            self._render_result(shake_surface)

        # Render particles on top
        healthcare_particles.render(shake_surface)

        # Render feedback popups
        healthcare_feedback.render(shake_surface)

        # Apply shake offset and blit to screen
        screen.blit(shake_surface, (self.shake_offset_x, self.shake_offset_y))

    def _render_button(self, screen, button, index):
        """Render a single bus route button with animations"""
        route = button['route']
        scale = self.button_scales[index].value

        # Calculate fade-in alpha
        fade_progress = max(0, min(1, (self.fade_in_timer - self.button_fade_delays[index]) * 3))
        alpha = int(255 * fade_progress)

        if alpha < 10:
            return

        # Calculate scaled rect
        base_rect = button['base_rect']
        scaled_width = int(base_rect.width * scale)
        scaled_height = int(base_rect.height * scale)
        scaled_rect = pygame.Rect(
            base_rect.centerx - scaled_width // 2,
            base_rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        button['rect'] = scaled_rect  # Update for hit detection

        # Create button surface
        button_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)

        # Determine colors based on state
        if button['selected']:
            if button['index'] == self.correct_route_index:
                bg_color = HealthcareUIColors.SUCCESS
                border_color = HealthcareVisualHelpers.lighten_color(HealthcareUIColors.SUCCESS)
            else:
                bg_color = HealthcareUIColors.ERROR
                border_color = HealthcareVisualHelpers.lighten_color(HealthcareUIColors.ERROR)
        elif button['pressed']:
            bg_color = HealthcareVisualHelpers.darken_color(HealthcareUIColors.HEALTHCARE_PRIMARY, 0.8)
            border_color = HealthcareUIColors.HEALTHCARE_PRIMARY
        elif button['hover']:
            bg_color = HealthcareVisualHelpers.lighten_color((50, 70, 100), 1.2)
            border_color = HealthcareUIColors.HEALTHCARE_PRIMARY
        else:
            bg_color = (50, 70, 100)
            border_color = (80, 100, 130)

        # Draw shadow
        shadow_rect = pygame.Rect(8, 8, scaled_width, scaled_height)
        pygame.draw.rect(button_surface, (0, 0, 0, 60), shadow_rect, border_radius=12)

        # Draw button background
        btn_rect = pygame.Rect(4, 4, scaled_width, scaled_height)
        pygame.draw.rect(button_surface, (*bg_color, alpha), btn_rect, border_radius=12)

        # Draw border
        pygame.draw.rect(button_surface, (*border_color, alpha), btn_rect, 3, border_radius=12)

        # Hover glow effect
        if button['hover'] and not button['selected']:
            glow_rect = btn_rect.inflate(6, 6)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*HealthcareUIColors.HEALTHCARE_PRIMARY, 40),
                           (0, 0, glow_rect.width, glow_rect.height), border_radius=14)
            button_surface.blit(glow_surface, (glow_rect.x - btn_rect.x + 4, glow_rect.y - btn_rect.y + 4))

        # Bus number badge
        badge_rect = pygame.Rect(btn_rect.x + 8, btn_rect.y + 8, 55, 35)
        pygame.draw.rect(button_surface, (*HealthcareUIColors.HEALTHCARE_PRIMARY, alpha), badge_rect, border_radius=8)

        number_font = pygame.font.Font(None, 32)
        number_text = number_font.render(f"#{route['number']}", True, (255, 255, 255))
        button_surface.blit(number_text, (badge_rect.x + badge_rect.width//2 - number_text.get_width()//2,
                                         badge_rect.y + badge_rect.height//2 - number_text.get_height()//2))

        # Route name
        route_font = pygame.font.Font(None, 24)
        route_text = route_font.render(route['route'], True, (255, 255, 255, alpha))
        button_surface.blit(route_text, (btn_rect.x + 70, btn_rect.y + 15))

        # Stops
        stops_font = pygame.font.Font(None, 20)
        stops_text = stops_font.render(f"Stops: {route['stops']}", True, (180, 185, 200, alpha))
        button_surface.blit(stops_text, (btn_rect.x + 70, btn_rect.y + 40))

        # Clinic indicator if this route goes to clinic
        if 'Clinic' in route['stops']:
            clinic_font = pygame.font.Font(None, 18)
            clinic_text = clinic_font.render("CLINIC", True, HealthcareUIColors.SUCCESS)
            clinic_rect = pygame.Rect(btn_rect.right - 60, btn_rect.y + 8, 50, 18)
            pygame.draw.rect(button_surface, (*HealthcareUIColors.SUCCESS, 40), clinic_rect, border_radius=4)
            button_surface.blit(clinic_text, (clinic_rect.x + 5, clinic_rect.y + 2))

        # Blit button to screen
        screen.blit(button_surface, (scaled_rect.x - 4, scaled_rect.y - 4))

    def _render_result(self, screen):
        """Render the result modal with animation"""
        scale = self.result_scale.value

        # Modal dimensions
        modal_width = int(500 * scale)
        modal_height = int(200 * scale)
        modal_x = self.SCREEN_WIDTH // 2 - modal_width // 2
        modal_y = self.SCREEN_HEIGHT // 2 - modal_height // 2

        if modal_width < 50:
            return

        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

        # Determine colors
        if self.failed:
            header_color = HealthcareUIColors.ERROR
            header_text = "WRONG BUS!" if self.time_remaining > 0 else "TOO SLOW!"
        else:
            header_color = HealthcareUIColors.SUCCESS
            header_text = "CORRECT!"

        # Draw modal
        healthcare_visuals.draw_modal_container(screen, modal_rect, header_color, header_text)

        # Content text
        content_y = modal_y + 70

        if self.failed:
            if self.time_remaining <= 0:
                detail_text = "You missed your appointment!"
            else:
                detail_text = "You'll be late for your appointment!"
            consequence_text = "Caseworker trust decreased"
            detail_color = (255, 200, 200)
            consequence_color = (255, 150, 150)
        else:
            detail_text = "Bus #38 will take you to the clinic!"
            consequence_text = "You'll make your appointment on time!"
            detail_color = (200, 255, 200)
            consequence_color = (150, 255, 150)

        detail_font = pygame.font.Font(None, 26)
        consequence_font = pygame.font.Font(None, 22)

        detail_surface = detail_font.render(detail_text, True, detail_color)
        consequence_surface = consequence_font.render(consequence_text, True, consequence_color)

        screen.blit(detail_surface, (self.SCREEN_WIDTH//2 - detail_surface.get_width()//2, content_y))
        screen.blit(consequence_surface, (self.SCREEN_WIDTH//2 - consequence_surface.get_width()//2, content_y + 35))

    def start(self):
        """Start the bus route mini-game"""
        self.active = True
        self.completed = False
        self.failed = False
        self.time_remaining = self.time_limit
        self.show_instructions = True
        self.instruction_timer = 0
        self.instruction_alpha.current = 0
        self.instruction_alpha.target = 255
        self.show_result = False
        self.result_timer = 0
        self.buttons_visible = False
        self.fade_in_timer = 0
        self.last_warning_time = 0
        self.shake_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # Reset button states and animations
        for i, button in enumerate(self.route_buttons):
            button['selected'] = False
            button['hover'] = False
            button['pressed'] = False
            button['rect'] = button['base_rect'].copy()
            self.button_scales[i].current = 1.0
            self.button_scales[i].target = 1.0

        # Clear any leftover particles/popups
        healthcare_particles.clear()
        healthcare_feedback.clear()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Draw method (alias for render) - standard interface"""
        self.render(screen)

    def handle_key(self, key):
        """Handle keyboard input - ESC to exit"""
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False

    def get_results(self):
        """Return results for objective manager"""
        if self.failed:
            return {
                'success': False,
                'message': 'Missed the bus to clinic',
                'stress': 10
            }
        else:
            return {
                'success': True,
                'message': 'Caught the right bus!',
                'stress': -5
            }
