"""
Approval Notification Mini-Game
Visual notification system showing approval with 2-week waiting period
Features celebration effects and timeline visualization
"""

import pygame
import math
import random
import datetime

class ApprovalNotificationGame:
    """Interactive approval notification with waiting period visualization"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Animation states
        self.animation_time = 0
        self.phase = "loading"  # loading -> approval -> timeline -> completed
        self.phase_timer = 0

        # Approval details
        self.approval_data = {
            'status': 'APPROVED',
            'effective_date': 'Immediate for Emergency Services',
            'full_coverage_date': '2 weeks from approval',
            'coverage_type': 'Former Foster Youth Medi-Cal',
            'member_id': 'FFY' + str(random.randint(100000, 999999))
        }

        # Timeline visualization
        self.timeline_days = 14
        self.current_day = 0
        self.day_progress = 0

        # Fonts
        self.title_font = pygame.font.Font(None, 54)
        self.header_font = pygame.font.Font(None, 42)
        self.content_font = pygame.font.Font(None, 32)
        self.detail_font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 22)

        # Visual effects
        self.celebration_particles = []
        self.loading_particles = []
        self.timeline_particles = []

        # Colors
        self.colors = {
            'success': (100, 255, 100),
            'warning': (255, 200, 100),
            'info': (100, 200, 255),
            'background': (25, 35, 50),
            'card': (45, 55, 75),
            'text': (255, 255, 255),
            'secondary': (200, 200, 200)
        }

    def start(self):
        """Start the approval notification sequence"""
        self.active = True
        self.completed = False
        self.animation_time = 0
        self.phase = "loading"
        self.phase_timer = 0
        self.current_day = 0
        self.day_progress = 0

        # Clear all particles
        self.celebration_particles = []
        self.loading_particles = []
        self.timeline_particles = []

        # Generate random member ID
        self.approval_data['member_id'] = 'FFY' + str(random.randint(100000, 999999))

    def update(self, dt):
        """Update animation states and effects"""
        if not self.active:
            return

        self.animation_time += dt
        self.phase_timer += dt

        # Phase transitions
        if self.phase == "loading" and self.phase_timer > 2.0:
            self.transition_to_approval()
        elif self.phase == "approval" and self.phase_timer > 4.0:
            self.transition_to_timeline()
        elif self.phase == "timeline" and self.phase_timer > 8.0:
            self.complete_notification()

        # Update particles
        self.update_particles(dt)

        # Update timeline animation in timeline phase
        if self.phase == "timeline":
            timeline_progress = (self.phase_timer - 4.0) / 4.0  # 4 seconds for timeline
            self.current_day = min(self.timeline_days, timeline_progress * self.timeline_days)

    def transition_to_approval(self):
        """Transition to approval display phase"""
        self.phase = "approval"
        self.phase_timer = 0
        self.create_celebration_particles()

    def transition_to_timeline(self):
        """Transition to timeline visualization phase"""
        self.phase = "timeline"
        self.phase_timer = 4.0  # Offset for smooth transition

    def complete_notification(self):
        """Complete the notification sequence"""
        self.phase = "completed"
        self.completed = True

        # Notify objective manager
        if self.objective_manager and hasattr(self.objective_manager, 'show_notification'):
            self.objective_manager.show_notification("Application Processed! Your application has been approved! Full coverage begins in 2 weeks.")

    def create_celebration_particles(self):
        """Create celebration particle effects for approval"""
        center_x = self.SCREEN_WIDTH // 2
        center_y = 300

        # Confetti particles
        for _ in range(100):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 400)
            self.celebration_particles.append({
                'x': center_x,
                'y': center_y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed - 200,
                'life': random.uniform(3.0, 5.0),
                'max_life': 5.0,
                'color': random.choice([
                    self.colors['success'],
                    self.colors['info'],
                    (255, 255, 100),
                    (255, 100, 255),
                    (100, 255, 255)
                ]),
                'size': random.randint(3, 8),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-300, 300)
            })

    def update_particles(self, dt):
        """Update all particle systems"""
        # Update celebration particles
        for particle in self.celebration_particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vel_x'] * dt
            particle['y'] += particle['vel_y'] * dt
            particle['vel_y'] += 500 * dt  # Gravity
            particle['rotation'] += particle['rot_speed'] * dt

            if particle['life'] <= 0:
                self.celebration_particles.remove(particle)

        # Update loading particles (spinning dots)
        if self.phase == "loading":
            if len(self.loading_particles) < 8:
                for i in range(8):
                    self.loading_particles.append({
                        'angle': i * 45,
                        'radius': 50,
                        'life': float('inf')
                    })

            for particle in self.loading_particles:
                particle['angle'] += 180 * dt

    def handle_click(self, pos):
        """Handle mouse clicks"""
        if not self.active:
            return

        # Allow skipping to next phase with clicks
        if self.phase == "loading":
            self.transition_to_approval()
        elif self.phase == "approval":
            self.transition_to_timeline()
        elif self.phase == "timeline":
            self.complete_notification()

    def draw(self, screen):
        """Draw the approval notification interface"""
        if not self.active:
            return

        # Background
        self.draw_background(screen)

        # Draw current phase
        if self.phase == "loading":
            self.draw_loading_phase(screen)
        elif self.phase == "approval":
            self.draw_approval_phase(screen)
        elif self.phase == "timeline":
            self.draw_timeline_phase(screen)

        # Draw particles
        self.draw_particles(screen)

        # Click hint
        if self.phase != "completed":
            self.draw_click_hint(screen)

    def draw_background(self, screen):
        """Draw animated background"""
        # Gradient background
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = (
                int(self.colors['background'][0] + progress * 10),
                int(self.colors['background'][1] + progress * 15),
                int(self.colors['background'][2] + progress * 20)
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Animated background elements
        wave_offset = self.animation_time * 50
        for i in range(0, self.SCREEN_WIDTH + 100, 100):
            wave_y = 100 + 30 * math.sin((i + wave_offset) * 0.01)
            pygame.draw.circle(screen, (40, 50, 70, 50), (i, int(wave_y)), 20)

    def draw_loading_phase(self, screen):
        """Draw the loading/processing phase"""
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        # Loading title
        title = "Processing Your Application..."
        title_surf = self.header_font.render(title, True, self.colors['text'])
        title_rect = title_surf.get_rect(center=(center_x, center_y - 100))
        screen.blit(title_surf, title_rect)

        # Loading spinner (drawn with particles)
        for i, particle in enumerate(self.loading_particles):
            angle_rad = math.radians(particle['angle'])
            x = center_x + particle['radius'] * math.cos(angle_rad)
            y = center_y + particle['radius'] * math.sin(angle_rad)

            # Dot size varies to create trailing effect
            size = 8 - (i % 8)
            alpha = 255 - (i * 20)
            color = (*self.colors['info'], max(50, alpha))

            pygame.draw.circle(screen, color[:3], (int(x), int(y)), size)

        # Loading text
        loading_texts = [
            "Verifying foster care history...",
            "Checking eligibility requirements...",
            "Processing application data...",
            "Generating approval decision..."
        ]

        text_index = int(self.phase_timer * 2) % len(loading_texts)
        loading_surf = self.detail_font.render(loading_texts[text_index], True, self.colors['secondary'])
        loading_rect = loading_surf.get_rect(center=(center_x, center_y + 50))
        screen.blit(loading_surf, loading_rect)

    def draw_approval_phase(self, screen):
        """Draw the approval notification"""
        center_x = self.SCREEN_WIDTH // 2

        # Approval status card
        card_width = 800
        card_height = 500
        card_x = center_x - card_width // 2
        card_y = 150

        # Card background with glow effect
        glow_size = 10
        for i in range(glow_size):
            alpha = 20 - i * 2
            glow_rect = pygame.Rect(card_x - i, card_y - i, card_width + i * 2, card_height + i * 2)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
            glow_surface.set_alpha(alpha)
            glow_surface.fill(self.colors['success'])
            screen.blit(glow_surface, glow_rect)

        # Main card
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(screen, self.colors['card'], card_rect, 0, 15)
        pygame.draw.rect(screen, self.colors['success'], card_rect, 3, 15)

        # Approval header
        header_y = card_y + 50

        # Success icon
        icon_surf = self.title_font.render("✅", True, self.colors['success'])
        icon_rect = icon_surf.get_rect(center=(center_x - 100, header_y))
        screen.blit(icon_surf, icon_rect)

        # Approval text
        approval_surf = self.title_font.render("APPROVED!", True, self.colors['success'])
        approval_rect = approval_surf.get_rect(center=(center_x + 50, header_y))

        # Pulsing effect
        pulse = 1.0 + 0.1 * math.sin(self.animation_time * 6)
        scaled_surf = pygame.transform.scale(approval_surf,
            (int(approval_surf.get_width() * pulse), int(approval_surf.get_height() * pulse)))
        scaled_rect = scaled_surf.get_rect(center=approval_rect.center)
        screen.blit(scaled_surf, scaled_rect)

        # Application details
        details = [
            f"Coverage Type: {self.approval_data['coverage_type']}",
            f"Member ID: {self.approval_data['member_id']}",
            f"Emergency Coverage: {self.approval_data['effective_date']}",
            f"Full Coverage: {self.approval_data['full_coverage_date']}"
        ]

        detail_y = header_y + 100
        for i, detail in enumerate(details):
            detail_surf = self.content_font.render(detail, True, self.colors['text'])
            detail_rect = detail_surf.get_rect(center=(center_x, detail_y + i * 40))
            screen.blit(detail_surf, detail_rect)

        # Important notice
        notice_y = detail_y + len(details) * 40 + 40
        notice_text = "Important: Full coverage begins in 2 weeks"
        notice_surf = self.detail_font.render(notice_text, True, self.colors['warning'])
        notice_rect = notice_surf.get_rect(center=(center_x, notice_y))

        # Notice background
        notice_bg = notice_rect.inflate(20, 10)
        pygame.draw.rect(screen, (100, 80, 0), notice_bg, 0, 5)
        screen.blit(notice_surf, notice_rect)

    def draw_timeline_phase(self, screen):
        """Draw the 2-week waiting period timeline"""
        center_x = self.SCREEN_WIDTH // 2

        # Timeline title
        title = "Coverage Timeline - 14 Day Waiting Period"
        title_surf = self.header_font.render(title, True, self.colors['text'])
        title_rect = title_surf.get_rect(center=(center_x, 100))
        screen.blit(title_surf, title_rect)

        # Timeline visualization
        timeline_y = 250
        timeline_width = 1000
        timeline_height = 200
        timeline_x = center_x - timeline_width // 2

        # Timeline background
        timeline_rect = pygame.Rect(timeline_x, timeline_y, timeline_width, timeline_height)
        pygame.draw.rect(screen, self.colors['card'], timeline_rect, 0, 10)
        pygame.draw.rect(screen, self.colors['info'], timeline_rect, 2, 10)

        # Draw days
        day_width = timeline_width / self.timeline_days
        for day in range(self.timeline_days):
            day_x = timeline_x + day * day_width
            day_rect = pygame.Rect(day_x, timeline_y + 20, day_width - 2, timeline_height - 40)

            # Day color based on current progress
            if day < self.current_day:
                color = self.colors['success']  # Completed days
            elif day == int(self.current_day):
                # Current day with progress animation
                progress = self.current_day - int(self.current_day)
                color = (
                    int(self.colors['warning'][0] + (self.colors['success'][0] - self.colors['warning'][0]) * progress),
                    int(self.colors['warning'][1] + (self.colors['success'][1] - self.colors['warning'][1]) * progress),
                    int(self.colors['warning'][2] + (self.colors['success'][2] - self.colors['warning'][2]) * progress)
                )
            else:
                color = (80, 80, 100)  # Waiting days

            pygame.draw.rect(screen, color, day_rect, 0, 3)

            # Day number
            day_text = str(day + 1)
            day_surf = self.small_font.render(day_text, True, self.colors['text'])
            day_text_rect = day_surf.get_rect(center=(day_x + day_width // 2, timeline_y + timeline_height + 20))
            screen.blit(day_surf, day_text_rect)

        # Progress indicators
        progress_y = timeline_y + timeline_height + 60

        # Current status
        current_day_int = int(self.current_day)
        if current_day_int < self.timeline_days:
            status_text = f"Day {current_day_int + 1} of {self.timeline_days} - Emergency coverage active"
            status_color = self.colors['warning']
        else:
            status_text = "Full coverage now active!"
            status_color = self.colors['success']

        status_surf = self.content_font.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(center=(center_x, progress_y))
        screen.blit(status_surf, status_rect)

        # Coverage explanation
        explain_y = progress_y + 50
        explanations = [
            "Emergency services: Covered immediately",
            "Routine care: Available after 14-day waiting period",
            "Prescription medications: Emergency coverage only initially"
        ]

        for i, explanation in enumerate(explanations):
            exp_surf = self.detail_font.render(explanation, True, self.colors['secondary'])
            exp_rect = exp_surf.get_rect(center=(center_x, explain_y + i * 30))
            screen.blit(exp_surf, exp_rect)

    def draw_particles(self, screen):
        """Draw all particle effects"""
        # Celebration particles
        for particle in self.celebration_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            if alpha > 0:
                color = (*particle['color'], min(alpha, 255))

                # Draw rotated square for confetti effect
                size = particle['size']
                x, y = int(particle['x']), int(particle['y'])

                # Simple circle for performance
                pygame.draw.circle(screen, color[:3], (x, y), size)

    def draw_click_hint(self, screen):
        """Draw click to continue hint"""
        hint_text = "Click anywhere to continue"
        hint_surf = self.small_font.render(hint_text, True, self.colors['secondary'])

        # Pulsing alpha
        alpha = int(128 + 127 * math.sin(self.animation_time * 3))
        hint_surf.set_alpha(alpha)

        hint_rect = hint_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50))
        screen.blit(hint_surf, hint_rect)

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def get_results(self):
        """Return results for the objective system"""
        return {
            'completed': self.completed,
            'approved': True,
            'member_id': self.approval_data['member_id'],
            'waiting_period': 14,
            'message': "Application approved! Emergency coverage active, full coverage in 2 weeks.",
            'color': self.colors['success']
        }

    def render(self, screen):
        """Render method for compatibility with activity system"""
        self.draw(screen)