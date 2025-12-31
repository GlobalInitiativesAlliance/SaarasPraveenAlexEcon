"""
Document Sorting Mini-Game
Sort documents into Required vs Optional piles
Always marked incomplete to show systemic barriers

UPGRADED: Manila folder bins, paper document cards,
animated stamp slam, particle effects
"""
import pygame
import random
import math
import time

from .systemic_visual_base import (
    SystemicUIColors, SystemicUIMetrics, SystemicVisualHelpers,
    SystemicVisualComponents, UIAnimation, systemic_visuals
)
from .systemic_particles import SystemicParticleSystem
from .systemic_feedback import SystemicFeedbackManager


class DocumentSortingGame:
    """Sort documents but always fail - systemic barrier demonstration"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 45.0
        self.time_remaining = self.time_limit

        # Documents with icons
        self.documents = [
            {'name': 'Birth Certificate', 'type': 'required', 'placed': False, 'icon': '📜'},
            {'name': 'Social Security Card', 'type': 'required', 'placed': False, 'icon': '🔢'},
            {'name': 'Proof of Income', 'type': 'required', 'placed': False, 'icon': '💵'},
            {'name': 'Photo ID', 'type': 'required', 'placed': False, 'icon': '🪪'},
            {'name': 'Address Verification', 'type': 'required', 'placed': False, 'icon': '🏠'},
            {'name': 'Bank Statements', 'type': 'optional', 'placed': False, 'icon': '🏦'},
            {'name': 'Medical Records', 'type': 'optional', 'placed': False, 'icon': '🏥'},
            {'name': 'Employment Letter', 'type': 'optional', 'placed': False, 'icon': '💼'},
            {'name': 'Reference Letters', 'type': 'optional', 'placed': False, 'icon': '✉️'},
            {'name': 'Foster Care Verification', 'type': 'required', 'placed': False, 'icon': '📋'},
        ]

        # Sorting bins
        self.required_bin = pygame.Rect(150, 420, 320, 200)
        self.optional_bin = pygame.Rect(810, 420, 320, 200)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Scoring
        self.correctly_sorted = 0
        self.total_documents = len(self.documents)

        # Result state
        self.show_result = False
        self.result_timer = 0
        self.stamp_triggered = False

        # Visual systems
        self.particles = SystemicParticleSystem()
        self.feedback = SystemicFeedbackManager()
        self.visuals = systemic_visuals

        # Animations
        self.bin_highlights = {'required': 0.0, 'optional': 0.0}
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)
        self.result_scale = UIAnimation(0.8, 1.0, speed=0.12)

        # Fonts
        self._init_fonts()

        # Create document rects
        self.create_document_rects()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.font_heading = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.font_body = pygame.font.SysFont('SF Pro Text', 20)
            self.font_small = pygame.font.SysFont('SF Pro Text', 16)
            self.font_doc = pygame.font.SysFont('SF Pro Text', 14)
            self.font_icon = pygame.font.SysFont('Segoe UI Emoji', 18)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_heading = pygame.font.Font(None, 32)
            self.font_body = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 20)
            self.font_doc = pygame.font.Font(None, 18)
            self.font_icon = pygame.font.Font(None, 22)

    def create_document_rects(self):
        """Create draggable document cards in a grid"""
        start_x = 280
        start_y = 130

        for i, doc in enumerate(self.documents):
            col = i % 5
            row = i // 5
            x = start_x + col * 145
            y = start_y + row * 95
            doc['rect'] = pygame.Rect(x, y, 130, 75)
            doc['original_pos'] = (x, y)
            doc['hover'] = False

    def handle_event(self, event):
        """Handle document dragging"""
        if not self.active or self.completed:
            return False

        if self.show_result:
            return True

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for doc in self.documents:
                if not doc['placed'] and doc['rect'].collidepoint(mouse_pos):
                    self.dragging = doc
                    self.drag_offset = (
                        doc['rect'].x - mouse_pos[0],
                        doc['rect'].y - mouse_pos[1]
                    )
                    # Emit paper trail
                    self.particles.emit_typing_cursor(mouse_pos[0], mouse_pos[1])
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                placed = False

                # Check required bin
                if self.required_bin.colliderect(self.dragging['rect']):
                    self.dragging['placed'] = True
                    self.dragging['placed_in'] = 'required'
                    if self.dragging['type'] == 'required':
                        self.correctly_sorted += 1
                        self.particles.emit_success(
                            self.required_bin.centerx,
                            self.required_bin.centery,
                            8
                        )
                    else:
                        self.particles.emit_frustration(
                            self.required_bin.centerx,
                            self.required_bin.y,
                            0.5
                        )
                    placed = True

                # Check optional bin
                elif self.optional_bin.colliderect(self.dragging['rect']):
                    self.dragging['placed'] = True
                    self.dragging['placed_in'] = 'optional'
                    if self.dragging['type'] == 'optional':
                        self.correctly_sorted += 1
                        self.particles.emit_success(
                            self.optional_bin.centerx,
                            self.optional_bin.centery,
                            8
                        )
                    else:
                        self.particles.emit_frustration(
                            self.optional_bin.centerx,
                            self.optional_bin.y,
                            0.5
                        )
                    placed = True

                if not placed:
                    # Return to original position
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]
                    self.dragging['placed'] = False

                self.dragging = None

                # Check if all sorted
                if all(doc['placed'] for doc in self.documents):
                    self.trigger_result()

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

                # Paper trail particles
                if int(time.time() * 15) % 3 == 0:
                    self.particles.emit_typing_cursor(mouse_pos[0], mouse_pos[1])

            # Update hover states
            for doc in self.documents:
                if not doc['placed']:
                    doc['hover'] = doc['rect'].collidepoint(mouse_pos)

            # Update bin highlights
            if self.dragging:
                self.bin_highlights['required'] = 1.0 if self.required_bin.colliderect(self.dragging['rect']) else max(0, self.bin_highlights['required'] - 0.1)
                self.bin_highlights['optional'] = 1.0 if self.optional_bin.colliderect(self.dragging['rect']) else max(0, self.bin_highlights['optional'] - 0.1)

        return True

    def trigger_result(self):
        """Show the unfair result"""
        self.show_result = True
        self.result_timer = 240  # 4 seconds
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)
        self.result_scale = UIAnimation(0.8, 1.0, speed=0.12)
        self.stamp_triggered = False

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update particles and feedback
        self.particles.update(dt)
        self.feedback.update(dt)

        # Decay bin highlights
        self.bin_highlights['required'] = max(0, self.bin_highlights['required'] - dt * 3)
        self.bin_highlights['optional'] = max(0, self.bin_highlights['optional'] - dt * 3)

        if not self.show_result:
            # Update timer
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.trigger_result()

            # Timer warning particles
            if self.time_remaining < 10 and int(time.time() * 2) % 2 == 0:
                self.particles.emit_frustration(
                    self.SCREEN_WIDTH - 80,
                    60,
                    0.3
                )
        else:
            # Update result animations
            self.result_alpha.update(dt)
            self.result_scale.update(dt)
            self.result_timer -= 1

            # Trigger stamp after delay
            if self.result_timer == 180 and not self.stamp_triggered:
                self.stamp_triggered = True
                self.feedback.add_incomplete_stamp(
                    self.SCREEN_WIDTH // 2,
                    self.SCREEN_HEIGHT // 2 + 20
                )
                self.particles.trigger_rejection_effect(
                    self.SCREEN_WIDTH // 2,
                    self.SCREEN_HEIGHT // 2
                )

            if self.result_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the document sorting interface"""
        if not self.active:
            return

        # Get shake offset from particles
        shake_x, shake_y = self.particles.render(screen)

        # Background gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = SystemicVisualHelpers.interpolate_color(
                (245, 245, 248), (235, 235, 240), progress
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Header
        self._render_header(screen)

        if not self.show_result:
            # Instructions
            self._render_instructions(screen)

            # Sorting bins
            self._render_bins(screen)

            # Documents (unplaced)
            for doc in self.documents:
                if not doc['placed'] and doc != self.dragging:
                    self._render_document(screen, doc)

            # Dragging document (on top)
            if self.dragging:
                self._render_document(screen, self.dragging, is_dragging=True)

            # Progress indicator
            self._render_progress(screen)

        else:
            # Result screen
            self._render_result(screen)

        # Particles and feedback on top
        self.particles.render(screen)
        self.feedback.render(screen)

    def _render_header(self, screen):
        """Render title and timer"""
        # Title
        title = self.font_title.render("Social Services - Document Sorting", True,
                                       SystemicUIColors.GOVERNMENT_BLUE)
        screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 25))

        # Timer
        if not self.show_result:
            self.visuals.draw_countdown_timer(
                screen,
                (self.SCREEN_WIDTH - 70, 55),
                self.time_remaining,
                self.time_limit,
                radius=38
            )

    def _render_instructions(self, screen):
        """Render instruction text"""
        inst = self.font_body.render("Sort documents into the correct folders before time runs out",
                                    True, SystemicUIColors.TEXT_SECONDARY)
        screen.blit(inst, (self.SCREEN_WIDTH // 2 - inst.get_width() // 2, 75))

    def _render_bins(self, screen):
        """Render the manila folder sorting bins"""
        # Required bin
        is_req_highlighted = self.bin_highlights['required'] > 0.3
        self.visuals.draw_manila_folder(screen, self.required_bin, "REQUIRED",
                                       is_highlighted=is_req_highlighted)

        # Highlight glow
        if self.bin_highlights['required'] > 0:
            glow_alpha = int(60 * self.bin_highlights['required'])
            glow_surf = pygame.Surface((self.required_bin.width + 20, self.required_bin.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*SystemicUIColors.GOVERNMENT_BLUE, glow_alpha),
                           (0, 0, glow_surf.get_width(), glow_surf.get_height()),
                           border_radius=SystemicUIMetrics.RADIUS_LARGE)
            screen.blit(glow_surf, (self.required_bin.x - 10, self.required_bin.y - 10))

        # Optional bin
        is_opt_highlighted = self.bin_highlights['optional'] > 0.3
        self.visuals.draw_manila_folder(screen, self.optional_bin, "OPTIONAL",
                                       is_highlighted=is_opt_highlighted)

        # Highlight glow
        if self.bin_highlights['optional'] > 0:
            glow_alpha = int(60 * self.bin_highlights['optional'])
            glow_surf = pygame.Surface((self.optional_bin.width + 20, self.optional_bin.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*SystemicUIColors.APPROVAL_GREEN, glow_alpha),
                           (0, 0, glow_surf.get_width(), glow_surf.get_height()),
                           border_radius=SystemicUIMetrics.RADIUS_LARGE)
            screen.blit(glow_surf, (self.optional_bin.x - 10, self.optional_bin.y - 10))

    def _render_document(self, screen, doc, is_dragging=False):
        """Render a document card"""
        rect = doc['rect']
        is_hover = doc.get('hover', False) and not is_dragging

        self.visuals.draw_document_card(
            screen, rect, doc['name'], doc['icon'],
            is_dragging=is_dragging, is_hover=is_hover
        )

    def _render_progress(self, screen):
        """Render sorted progress"""
        placed_count = sum(1 for d in self.documents if d['placed'])

        # Progress bar
        bar_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 150, 650, 300, 25)
        self.visuals.draw_progress_meter(
            screen, bar_rect,
            placed_count / self.total_documents,
            f"Sorted: {placed_count}/{self.total_documents}",
            show_percentage=False
        )

        # Count text
        count_text = self.font_small.render(f"{placed_count}/{self.total_documents}", True,
                                           SystemicUIColors.TEXT_LIGHT)
        screen.blit(count_text, (bar_rect.centerx - count_text.get_width() // 2,
                                bar_rect.centery - count_text.get_height() // 2))

    def _render_result(self, screen):
        """Render the result panel"""
        alpha = self.result_alpha.value
        scale = self.result_scale.value

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(160 * alpha)))
        screen.blit(overlay, (0, 0))

        # Result panel
        panel_width = int(700 * scale)
        panel_height = int(350 * scale)
        panel_x = (self.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.SCREEN_HEIGHT - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Shadow
        SystemicVisualHelpers.draw_shadow(screen, panel_rect, 15, 100,
                                         SystemicUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, SystemicUIColors.FORM_CREAM, panel_rect,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Header bar
        header_rect = pygame.Rect(panel_x, panel_y, panel_width, 60)
        pygame.draw.rect(screen, SystemicUIColors.GOVERNMENT_BLUE, header_rect,
                        border_top_left_radius=SystemicUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Header text
        header_text = self.font_heading.render("Application Review Complete", True,
                                              SystemicUIColors.TEXT_LIGHT)
        screen.blit(header_text, (panel_rect.centerx - header_text.get_width() // 2,
                                 panel_y + 15))

        # Score (but it doesn't matter)
        score_text = f"Documents correctly sorted: {self.correctly_sorted}/{self.total_documents}"
        score_surface = self.font_body.render(score_text, True, SystemicUIColors.APPROVAL_GREEN)
        screen.blit(score_surface, (panel_rect.centerx - score_surface.get_width() // 2,
                                   panel_y + 90))

        # "However..." text
        however_text = self.font_heading.render("However...", True, SystemicUIColors.STAMP_RED)
        screen.blit(however_text, (panel_rect.centerx - however_text.get_width() // 2,
                                  panel_y + 140))

        # Arbitrary reason (after stamp)
        if self.stamp_triggered and self.result_timer < 150:
            reasons = [
                "Missing Form 4B-7 (not mentioned anywhere)",
                "Signature on wrong line (line not marked)",
                "Used blue ink instead of black",
                "Document copy not notarized",
                "Missing page 3 of 3 (wasn't provided)"
            ]
            reason = reasons[int(time.time()) % len(reasons)]
            reason_text = self.font_small.render(f'Reason: "{reason}"', True,
                                                SystemicUIColors.TEXT_SECONDARY)
            screen.blit(reason_text, (panel_rect.centerx - reason_text.get_width() // 2,
                                     panel_y + 280))

        # Border
        pygame.draw.rect(screen, SystemicUIColors.INSTITUTIONAL_GRAY, panel_rect, 2,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

    def start(self):
        """Start the document sorting game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.time_remaining = self.time_limit
        self.correctly_sorted = 0
        self.result_timer = 0
        self.stamp_triggered = False

        # Reset documents
        for doc in self.documents:
            doc['placed'] = False
            doc['hover'] = False
            doc['rect'].x = doc['original_pos'][0]
            doc['rect'].y = doc['original_pos'][1]

        # Clear effects
        self.particles.clear()
        self.feedback.clear()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)
