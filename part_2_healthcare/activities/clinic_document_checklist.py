"""
Clinic Document Checklist Mini-Game
High-quality interactive checklist for verifying required documents
"""

import pygame
import math
import random

class ClinicDocumentChecklistGame:
    """Interactive document verification mini-game"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game state
        self.documents_verified = 0
        self.total_documents = 3
        self.animation_time = 0
        self.success_animation = False

        # Document items with visual elements
        self.documents = [
            {
                'name': 'Valid ID (Driver\'s License/State ID)',
                'description': 'Government-issued photo identification',
                'verified': False,
                'icon': '🪪',
                'color': (70, 130, 180),
                'hover': False,
                'animation_offset': 0,
                'check_animation': 0
            },
            {
                'name': 'Previous Medi-Cal Card',
                'description': 'Shows your previous coverage history',
                'verified': False,
                'icon': '🏥',
                'color': (60, 179, 113),
                'hover': False,
                'animation_offset': 0,
                'check_animation': 0
            },
            {
                'name': 'Proof of Income',
                'description': 'Pay stubs, bank statements, or benefits letter',
                'verified': False,
                'icon': '📄',
                'color': (205, 133, 63),
                'hover': False,
                'animation_offset': 0,
                'check_animation': 0
            }
        ]

        # UI elements
        self.title = "Document Verification Checklist"
        self.instructions = "Click each document to verify you have it with you"

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)

        # Visual effects
        self.particles = []
        self.completed_particles = []
        self.completion_timer = 0

    def start(self):
        """Start the document checklist"""
        self.active = True
        self.completed = False
        self.documents_verified = 0
        self.animation_time = 0
        self.success_animation = False

        # Reset all documents
        for doc in self.documents:
            doc['verified'] = False
            doc['hover'] = False
            doc['animation_offset'] = 0
            doc['check_animation'] = 0

        # Clear particles
        self.particles = []
        self.completed_particles = []
        self.completion_timer = 0

    def update(self, dt):
        """Update game state and animations"""
        if not self.active:
            return

        self.animation_time += dt

        # Update document animations
        for i, doc in enumerate(self.documents):
            # Hover animation
            if doc['hover']:
                doc['animation_offset'] = min(doc['animation_offset'] + dt * 300, 10)
            else:
                doc['animation_offset'] = max(doc['animation_offset'] - dt * 300, 0)

            # Check animation
            if doc['verified'] and doc['check_animation'] < 1.0:
                doc['check_animation'] = min(doc['check_animation'] + dt * 4, 1.0)

        # Update particles
        self.update_particles(dt)

        # Handle completion timer
        if self.success_animation and self.completion_timer > 0:
            self.completion_timer -= dt
            if self.completion_timer <= 0:
                self.complete_game()

        # Check completion
        if self.documents_verified == self.total_documents and not self.success_animation:
            self.trigger_success_animation()

    def update_particles(self, dt):
        """Update particle systems"""
        # Update regular particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            particle['y'] -= particle['speed'] * dt
            particle['x'] += math.sin(particle['life'] * 10) * 20 * dt

            if particle['life'] <= 0:
                self.particles.remove(particle)

        # Update completion particles
        for particle in self.completed_particles[:]:
            particle['life'] -= dt
            particle['y'] -= particle['speed'] * dt
            particle['x'] += particle['vel_x'] * dt
            particle['vel_y'] += 200 * dt  # Gravity
            particle['y'] += particle['vel_y'] * dt

            if particle['life'] <= 0:
                self.completed_particles.remove(particle)

    def handle_click(self, pos):
        """Handle mouse clicks on documents"""
        if not self.active or self.success_animation:
            return

        mx, my = pos

        # Check clicks on document items
        for i, doc in enumerate(self.documents):
            doc_rect = self.get_document_rect(i)
            if doc_rect.collidepoint(mx, my) and not doc['verified']:
                self.verify_document(i)

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return

        mx, my = pos

        # Update hover states
        for i, doc in enumerate(self.documents):
            doc_rect = self.get_document_rect(i)
            doc['hover'] = doc_rect.collidepoint(mx, my) and not doc['verified']

    def get_document_rect(self, index):
        """Get the rectangle for a document item"""
        start_y = 200
        item_height = 120
        margin = 20

        y = start_y + (item_height + margin) * index
        return pygame.Rect(200, y, 880, item_height)

    def verify_document(self, index):
        """Verify a document and trigger effects"""
        doc = self.documents[index]
        if doc['verified']:
            return

        doc['verified'] = True
        self.documents_verified += 1

        # Create verification particles
        doc_rect = self.get_document_rect(index)
        for _ in range(15):
            self.particles.append({
                'x': doc_rect.centerx + random.randint(-50, 50),
                'y': doc_rect.centery,
                'speed': random.randint(50, 150),
                'life': random.uniform(1.0, 2.0),
                'color': doc['color']
            })

    def trigger_success_animation(self):
        """Trigger the completion animation"""
        self.success_animation = True

        # Create celebration particles
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        for _ in range(50):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300)
            self.completed_particles.append({
                'x': center_x,
                'y': center_y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed - 100,
                'speed': speed,
                'life': random.uniform(2.0, 4.0),
                'color': (random.randint(100, 255), random.randint(150, 255), random.randint(100, 255))
            })

        # Set completion timer for animation
        self.completion_timer = 2.0  # 2 seconds for animation

    def complete_game(self):
        """Complete the mini-game"""
        self.active = False
        self.completed = True

        # Store results for manager
        self.results = {
            'documents_verified': self.documents_verified,
            'total_documents': self.total_documents,
            'message': 'All required documents verified successfully'
        }

    def get_results(self):
        """Get results from the document checklist"""
        if hasattr(self, 'results'):
            return self.results
        return {
            'documents_verified': self.documents_verified,
            'total_documents': self.total_documents,
            'message': 'Document verification in progress'
        }

    def draw(self, screen):
        """Draw the document checklist interface"""
        if not self.active:
            return

        # Background gradient
        self.draw_gradient_background(screen)

        # Title
        title_surf = self.title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 80))
        screen.blit(title_surf, title_rect)

        # Instructions
        inst_surf = self.subtitle_font.render(self.instructions, True, (200, 200, 200))
        inst_rect = inst_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 130))
        screen.blit(inst_surf, inst_rect)

        # Progress indicator
        self.draw_progress_bar(screen)

        # Document items
        for i, doc in enumerate(self.documents):
            self.draw_document_item(screen, doc, i)

        # Draw particles
        self.draw_particles(screen)

        # Success message
        if self.success_animation:
            self.draw_success_message(screen)

    def draw_gradient_background(self, screen):
        """Draw modern medical facility gradient background"""
        # Medical-grade clean background with subtle patterns
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT

            # Clean medical whites and soft blues
            base_r = int(240 + progress * 15)  # Very light blue-white
            base_g = int(245 + progress * 10)  # Clean white
            base_b = int(250 + progress * 5)   # Pristine white

            # Add subtle medical facility accent
            accent_strength = math.sin(progress * math.pi) * 0.1
            r = min(255, int(base_r - accent_strength * 20))
            g = min(255, int(base_g - accent_strength * 15))
            b = min(255, int(base_b - accent_strength * 10))

            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Add subtle grid pattern for medical aesthetic
        grid_color = (220, 230, 235, 30)
        for x in range(0, self.SCREEN_WIDTH, 40):
            pygame.draw.line(screen, grid_color[:3], (x, 0), (x, self.SCREEN_HEIGHT), 1)
        for y in range(0, self.SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, grid_color[:3], (0, y), (self.SCREEN_WIDTH, y), 1)

    def draw_progress_bar(self, screen):
        """Draw the progress indicator"""
        bar_width = 400
        bar_height = 20
        bar_x = (self.SCREEN_WIDTH - bar_width) // 2
        bar_y = 160

        # Background
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), 0, 5)

        # Progress fill
        progress = self.documents_verified / self.total_documents
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(screen, (100, 255, 100), (bar_x, bar_y, fill_width, bar_height), 0, 5)

        # Border
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 2, 5)

        # Progress text
        progress_text = f"{self.documents_verified}/{self.total_documents} Documents Verified"
        text_surf = self.small_font.render(progress_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.SCREEN_WIDTH // 2, bar_y + bar_height + 15))
        screen.blit(text_surf, text_rect)

    def draw_document_item(self, screen, doc, index):
        """Draw modern medical-grade document card with professional styling"""
        doc_rect = self.get_document_rect(index)

        # Apply hover animation with smooth easing
        animated_rect = doc_rect.copy()
        hover_offset = doc['animation_offset'] * (1 - math.cos(doc['animation_offset'] / 10 * math.pi)) / 2
        animated_rect.x -= int(hover_offset)

        # Medical-grade card shadow
        shadow_rect = animated_rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 25))
        screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

        # Card background based on verification state
        card_surface = pygame.Surface((animated_rect.width, animated_rect.height), pygame.SRCALPHA)

        if doc['verified']:
            # Verified - medical green gradient
            for y in range(animated_rect.height):
                progress = y / animated_rect.height
                r = int(245 + progress * 10)
                g = int(255 - progress * 5)
                b = int(245 + progress * 10)
                pygame.draw.line(card_surface, (r, g, b), (0, y), (animated_rect.width, y))
            border_color = (40, 180, 40)
            accent_color = (60, 200, 60)
        elif doc['hover']:
            # Hover state - soft blue medical highlight
            for y in range(animated_rect.height):
                progress = y / animated_rect.height
                r = int(240 + progress * 15)
                g = int(248 + progress * 7)
                b = int(255 - progress * 5)
                pygame.draw.line(card_surface, (r, g, b), (0, y), (animated_rect.width, y))
            border_color = (70, 130, 220)
            accent_color = (100, 160, 255)
        else:
            # Default state - clean medical white
            for y in range(animated_rect.height):
                progress = y / animated_rect.height
                r = int(255 - progress * 8)
                g = int(255 - progress * 5)
                b = int(255 - progress * 3)
                pygame.draw.line(card_surface, (r, g, b), (0, y), (animated_rect.width, y))
            border_color = (200, 210, 220)
            accent_color = (180, 190, 200)

        screen.blit(card_surface, (animated_rect.x, animated_rect.y))

        # Medical-grade border with subtle glow
        pygame.draw.rect(screen, border_color, animated_rect, 2, border_radius=12)
        if doc['hover'] or doc['verified']:
            pygame.draw.rect(screen, accent_color, animated_rect, 1, border_radius=12)

        # Medical status stripe
        stripe_width = 8
        stripe_rect = pygame.Rect(animated_rect.x, animated_rect.y, stripe_width, animated_rect.height)
        if doc['verified']:
            pygame.draw.rect(screen, (40, 180, 40), stripe_rect, border_radius=12)
        elif doc['hover']:
            pygame.draw.rect(screen, (70, 130, 220), stripe_rect, border_radius=12)
        else:
            pygame.draw.rect(screen, (200, 210, 220), stripe_rect, border_radius=12)

        # Professional icon with medical styling
        icon_size = 56
        icon_x = animated_rect.x + stripe_width + 25
        icon_y = animated_rect.centery - icon_size // 2

        # Icon background circle
        icon_bg_color = (240, 245, 250) if not doc['verified'] else (235, 255, 235)
        pygame.draw.circle(screen, icon_bg_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2 - 2)
        pygame.draw.circle(screen, border_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2 - 2, 2)

        # Enhanced icon
        icon_font = pygame.font.Font(None, 40)
        icon_surf = icon_font.render(doc['icon'], True, doc['color'])
        icon_rect = icon_surf.get_rect(center=(icon_x + icon_size // 2, icon_y + icon_size // 2))
        screen.blit(icon_surf, icon_rect)

        # Professional typography
        text_x = animated_rect.x + stripe_width + icon_size + 40
        text_color = (50, 60, 70) if not doc['verified'] else (40, 120, 40)

        # Document name with improved spacing
        name_font = pygame.font.Font(None, 30)
        name_surf = name_font.render(doc['name'], True, text_color)
        name_y = animated_rect.y + 18
        screen.blit(name_surf, (text_x, name_y))

        # Description with medical professional styling
        desc_color = (100, 110, 120) if not doc['verified'] else (80, 140, 80)
        desc_surf = self.small_font.render(doc['description'], True, desc_color)
        desc_y = animated_rect.y + 52
        screen.blit(desc_surf, (text_x, desc_y))

        # Status indicator
        status_y = animated_rect.y + 76
        if doc['verified']:
            status_surf = self.small_font.render("✓ Verified and accepted", True, (40, 150, 40))
            screen.blit(status_surf, (text_x, status_y))
        elif doc['hover']:
            status_surf = self.small_font.render("Click to verify document", True, (70, 130, 220))
            screen.blit(status_surf, (text_x, status_y))
        else:
            status_surf = self.small_font.render("Pending verification", True, (150, 160, 170))
            screen.blit(status_surf, (text_x, status_y))

        # Enhanced checkmark animation
        if doc['verified']:
            self.draw_professional_checkmark(screen, animated_rect, doc['check_animation'])

    def draw_professional_checkmark(self, screen, rect, animation_progress):
        """Draw professional medical-grade checkmark with smooth animation"""
        check_size = 50
        check_x = rect.right - 80
        check_y = rect.centery - check_size // 2

        # Animated background circle with medical styling
        if animation_progress > 0:
            circle_radius = int((check_size // 2) * min(animation_progress * 1.2, 1.0))
            circle_color = (40, 180, 40, int(200 * min(animation_progress, 1.0)))

            # Draw layered circles for depth
            for i in range(3):
                radius_adjust = i * 2
                alpha_adjust = i * 30
                color = (40 + i * 20, 180 + i * 20, 40 + i * 20)

                if circle_radius > radius_adjust:
                    pygame.draw.circle(screen, color,
                                     (check_x + check_size // 2, check_y + check_size // 2),
                                     circle_radius - radius_adjust, max(1, 3 - i))

        # Professional checkmark with smooth animation
        if animation_progress > 0.4:
            check_progress = min((animation_progress - 0.4) / 0.6, 1.0)

            # Draw checkmark with professional styling
            check_font = pygame.font.Font(None, 38)
            check_surf = check_font.render("✓", True, (255, 255, 255))
            check_surf.set_alpha(int(255 * check_progress))

            # Add subtle glow effect
            glow_surf = check_font.render("✓", True, (200, 255, 200))
            glow_surf.set_alpha(int(100 * check_progress))

            check_rect = check_surf.get_rect(center=(check_x + check_size // 2, check_y + check_size // 2))
            glow_rect = glow_surf.get_rect(center=(check_x + check_size // 2 + 1, check_y + check_size // 2 + 1))

            screen.blit(glow_surf, glow_rect)
            screen.blit(check_surf, check_rect)

    def draw_checkmark(self, screen, rect, animation_progress):
        """Draw an animated checkmark"""
        check_size = 40
        check_x = rect.right - 80
        check_y = rect.centery - check_size // 2

        # Checkmark background circle
        circle_radius = int(check_size // 2 * animation_progress)
        if circle_radius > 0:
            pygame.draw.circle(screen, (100, 255, 100), (check_x + check_size // 2, check_y + check_size // 2), circle_radius)
            pygame.draw.circle(screen, (50, 150, 50), (check_x + check_size // 2, check_y + check_size // 2), circle_radius, 3)

        # Animated checkmark
        if animation_progress > 0.5:
            check_progress = (animation_progress - 0.5) * 2
            check_surf = self.font.render("✓", True, (255, 255, 255))
            check_surf.set_alpha(int(255 * check_progress))
            check_rect = check_surf.get_rect(center=(check_x + check_size // 2, check_y + check_size // 2))
            screen.blit(check_surf, check_rect)

    def draw_particles(self, screen):
        """Draw particle effects"""
        # Regular verification particles
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            if alpha > 0:
                color = (*particle['color'], min(alpha, 255))
                size = max(1, int(particle['life'] * 8))
                pygame.draw.circle(screen, color[:3], (int(particle['x']), int(particle['y'])), size)

        # Completion celebration particles
        for particle in self.completed_particles:
            alpha = int(255 * min(particle['life'], 1.0))
            if alpha > 0:
                color = (*particle['color'], min(alpha, 255))
                size = max(1, int(particle['life'] * 6))
                pygame.draw.circle(screen, color[:3], (int(particle['x']), int(particle['y'])), size)

    def draw_success_message(self, screen):
        """Draw the success completion message"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Success message
        success_text = "All Documents Verified!"
        success_surf = self.title_font.render(success_text, True, (100, 255, 100))
        success_rect = success_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50))

        # Pulsing effect
        pulse = 1.0 + 0.1 * math.sin(self.animation_time * 8)
        scaled_surf = pygame.transform.scale(success_surf, (int(success_surf.get_width() * pulse), int(success_surf.get_height() * pulse)))
        scaled_rect = scaled_surf.get_rect(center=success_rect.center)
        screen.blit(scaled_surf, scaled_rect)

        # Sub-message
        sub_text = "Ready to proceed with your application"
        sub_surf = self.subtitle_font.render(sub_text, True, (255, 255, 255))
        sub_rect = sub_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 20))
        screen.blit(sub_surf, sub_rect)

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)

    def render(self, screen):
        """Render method for compatibility with activity system"""
        self.draw(screen)

    def get_results(self):
        """Return results for the objective system"""
        return {
            'completed': self.completed,
            'message': "Document verification complete! All required documents confirmed.",
            'color': (100, 255, 100) if self.completed else (255, 100, 100)
        }