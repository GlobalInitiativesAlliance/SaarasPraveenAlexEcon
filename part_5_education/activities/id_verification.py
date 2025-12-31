"""
ID Verification Mini-Game
Match ID and foster verification documents to correct forms
Library laptop request process

UPGRADED: Colored document icons, dashed borders,
state indicators, and animated result screen
"""
import pygame
import math
import time

from .education_visual_base import (
    EducationUIColors, EducationUIMetrics, EducationVisualHelpers,
    EducationVisualComponents, UIAnimation, education_visuals
)
from .particle_effects import ParticleSystem
from .feedback_popups import FeedbackPopupManager


class IDVerificationGame:
    """Match documents to correct form fields for laptop request"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Documents with colors and icons
        self.documents = [
            {'type': 'id', 'name': 'State ID', 'icon': '🪪',
             'color': EducationUIColors.EDUCATION_PRIMARY, 'placed': False},
            {'type': 'foster', 'name': 'Foster Care Letter', 'icon': '📋',
             'color': EducationUIColors.EDUCATION_PURPLE, 'placed': False},
            {'type': 'address', 'name': 'Proof of Address', 'icon': '🏠',
             'color': EducationUIColors.EDUCATION_SECONDARY, 'placed': False},
            {'type': 'income', 'name': 'Income Statement', 'icon': '💰',
             'color': EducationUIColors.EDUCATION_ACCENT, 'placed': False},
        ]

        # Form requirements
        self.form_slots = [
            {'label': 'Photo ID Required', 'accepts': 'id', 'filled': None, 'required': True},
            {'label': 'Foster Youth Verification', 'accepts': 'foster', 'filled': None, 'required': True},
            {'label': 'Current Address Proof', 'accepts': 'address', 'filled': None, 'required': False},
        ]

        # Create UI elements
        self.create_document_cards()
        self.create_form_slots()

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Result state
        self.verification_complete = False
        self.show_result = False
        self.laptop_available = False

        # Submit button
        self.submit_button = pygame.Rect(540, 530, 200, 50)
        self.button_hover = False
        self.button_scale = 1.0

        # Visual systems
        self.particles = ParticleSystem()
        self.popups = FeedbackPopupManager()
        self.visuals = education_visuals

        # Animations
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)
        self.result_scale = UIAnimation(0.5, 1.0, speed=0.15)
        self.typewriter_progress = 0
        self.typewriter_active = False

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.font_slot_label = pygame.font.SysFont('SF Pro Display', 18)
            self.font_doc_name = pygame.font.SysFont('SF Pro Text', 16)
            self.font_small = pygame.font.SysFont('SF Pro Text', 14)
            self.font_button = pygame.font.SysFont('SF Pro Display', 18, bold=True)
            self.font_result = pygame.font.SysFont('SF Pro Display', 26, bold=True)
            self.font_message = pygame.font.SysFont('SF Pro Text', 18)
            self.font_icon = pygame.font.SysFont('Segoe UI Emoji', 24)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_slot_label = pygame.font.Font(None, 22)
            self.font_doc_name = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 16)
            self.font_button = pygame.font.Font(None, 22)
            self.font_result = pygame.font.Font(None, 30)
            self.font_message = pygame.font.Font(None, 20)
            self.font_icon = pygame.font.Font(None, 28)

    def create_document_cards(self):
        """Create draggable document cards"""
        start_x = 100
        start_y = 220

        for i, doc in enumerate(self.documents):
            x = start_x
            y = start_y + (i * 85)
            doc['rect'] = pygame.Rect(x, y, 180, 70)
            doc['original_pos'] = (x, y)
            doc['hover'] = False

    def create_form_slots(self):
        """Create form slot areas"""
        start_x = 520
        start_y = 200

        for i, slot in enumerate(self.form_slots):
            slot['rect'] = pygame.Rect(start_x, start_y + (i * 110), 400, 85)

    def handle_event(self, event):
        """Handle document dragging and placement"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check submit button
            if self.submit_button.collidepoint(mouse_pos) and not self.show_result:
                self.check_verification()
                return True

            # Check document dragging
            for doc in self.documents:
                if not doc['placed'] and doc['rect'].collidepoint(mouse_pos):
                    self.dragging = doc
                    self.drag_offset = (
                        doc['rect'].x - mouse_pos[0],
                        doc['rect'].y - mouse_pos[1]
                    )
                    self.particles.emit_paper_trail(mouse_pos[0], mouse_pos[1])
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped on a form slot
                placed = False
                for slot in self.form_slots:
                    if slot['rect'].colliderect(self.dragging['rect']):
                        # Check if slot already filled
                        if slot['filled']:
                            # Return previous document
                            slot['filled']['placed'] = False
                            slot['filled']['rect'].x = slot['filled']['original_pos'][0]
                            slot['filled']['rect'].y = slot['filled']['original_pos'][1]

                        # Place document
                        slot['filled'] = self.dragging
                        self.dragging['placed'] = True
                        self.dragging['rect'].center = slot['rect'].center

                        # Check if correct placement
                        is_correct = self.dragging['type'] == slot['accepts']
                        if is_correct:
                            self.particles.emit_success(
                                self.dragging['rect'].centerx,
                                self.dragging['rect'].centery
                            )
                        else:
                            self.particles.emit_error(
                                self.dragging['rect'].centerx,
                                self.dragging['rect'].centery
                            )

                        placed = True
                        break

                if not placed:
                    # Return to original position
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]
                    self.dragging['placed'] = False

                self.dragging = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

                # Emit trail particles occasionally
                if int(time.time() * 10) % 3 == 0:
                    self.particles.emit_paper_trail(mouse_pos[0], mouse_pos[1], 2)

            # Update button hover
            self.button_hover = self.submit_button.collidepoint(mouse_pos)

            # Update document hover states
            for doc in self.documents:
                if not doc['placed']:
                    doc['hover'] = doc['rect'].collidepoint(mouse_pos)

        return True

    def check_verification(self):
        """Check if documents are correctly placed"""
        correct = True

        for slot in self.form_slots:
            if slot['required']:
                if not slot['filled'] or slot['filled']['type'] != slot['accepts']:
                    correct = False
                    break

        self.verification_complete = correct
        self.show_result = True
        self.laptop_available = False  # Always out of stock for narrative
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)
        self.result_scale = UIAnimation(0.5, 1.0, speed=0.15)
        self.typewriter_progress = 0
        self.typewriter_active = True

        if correct:
            self.particles.emit_confetti(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2, 30)
            self.popups.add_verification_achievement(True)

        self.completed = True

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update particles and popups
        self.particles.update(dt)
        self.popups.update(dt)

        # Update button scale
        target_scale = 1.05 if self.button_hover else 1.0
        self.button_scale += (target_scale - self.button_scale) * 0.2

        # Update result animations
        if self.show_result:
            self.result_alpha.update(dt)
            self.result_scale.update(dt)

            # Typewriter effect
            if self.typewriter_active:
                self.typewriter_progress += dt * 30  # Characters per second

    def render(self, screen):
        """Render the ID verification interface"""
        if not self.active:
            return

        # Background gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = EducationVisualHelpers.interpolate_color(
                (242, 245, 252), (230, 235, 248), progress
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Title
        self._render_header(screen)

        # Form slots (render first, behind documents)
        for slot in self.form_slots:
            self._render_form_slot(screen, slot)

        # Document cards (unplaced)
        for doc in self.documents:
            if not doc['placed'] and doc != self.dragging:
                self._render_document_card(screen, doc)

        # Placed documents
        for doc in self.documents:
            if doc['placed'] and doc != self.dragging:
                self._render_document_card(screen, doc, in_slot=True)

        # Dragging document (on top)
        if self.dragging:
            self._render_document_card(screen, self.dragging, is_dragging=True)

        # Submit button
        if not self.show_result:
            self._render_submit_button(screen)

        # Result modal
        if self.show_result:
            self._render_result(screen)

        # Particles and popups
        self.particles.render(screen)
        self.popups.render(screen)

    def _render_header(self, screen):
        """Render title area"""
        title_text = self.font_title.render("Library Laptop Request", True,
                                           EducationUIColors.EDUCATION_PRIMARY)
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

        subtitle = self.font_small.render("Match documents to form requirements",
                                         True, EducationUIColors.TEXT_SECONDARY)
        screen.blit(subtitle, (self.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 75))

        # Document section label
        doc_label = self.font_slot_label.render("Your Documents", True,
                                               EducationUIColors.TEXT_PRIMARY)
        screen.blit(doc_label, (100, 180))

        # Form section label
        form_label = self.font_slot_label.render("Required Documents", True,
                                                EducationUIColors.TEXT_PRIMARY)
        screen.blit(form_label, (520, 160))

    def _render_form_slot(self, screen, slot):
        """Render a form slot with state indicators"""
        rect = slot['rect']
        is_filled = slot['filled'] is not None
        is_correct = is_filled and slot['filled']['type'] == slot['accepts']
        is_highlighted = self.dragging and rect.colliderect(self.dragging['rect'])

        # Background color based on state
        if is_correct:
            bg_color = (230, 255, 230)
            border_color = EducationUIColors.VERIFIED
        elif is_filled and not is_correct:
            bg_color = (255, 235, 235)
            border_color = EducationUIColors.BLOCKED
        elif is_highlighted:
            bg_color = (235, 245, 255)
            border_color = EducationUIColors.EDUCATION_PRIMARY
        else:
            bg_color = EducationUIColors.FORM_FIELD_BG
            border_color = EducationUIColors.FORM_FIELD_BORDER

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, rect, 4, 30,
                                          EducationUIMetrics.RADIUS_MEDIUM)

        # Background
        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Border (dashed for empty slots)
        if not is_filled and not is_highlighted:
            EducationVisualHelpers.draw_dashed_rect(screen, rect, border_color, 2, 10)
        else:
            pygame.draw.rect(screen, border_color, rect, 2,
                            border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Slot label
        label_text = self.font_slot_label.render(slot['label'], True,
                                                EducationUIColors.TEXT_PRIMARY)
        screen.blit(label_text, (rect.x + 15, rect.y - 25))

        # Required indicator
        if slot['required']:
            req_badge = pygame.Rect(rect.x + 15 + label_text.get_width() + 10, rect.y - 22, 8, 8)
            pygame.draw.circle(screen, EducationUIColors.BLOCKED, req_badge.center, 4)

        # Status icon in corner
        if is_filled:
            icon_pos = (rect.right - 25, rect.top + 25)
            if is_correct:
                self.visuals.draw_checkmark(screen, icon_pos, 15, EducationUIColors.VERIFIED)
            else:
                self.visuals.draw_x_mark(screen, icon_pos, 15, EducationUIColors.BLOCKED)

        # Placeholder text if empty
        if not is_filled:
            placeholder = self.font_small.render("Drop document here", True,
                                                EducationUIColors.TEXT_MUTED)
            screen.blit(placeholder, (rect.centerx - placeholder.get_width() // 2,
                                     rect.centery - placeholder.get_height() // 2))

    def _render_document_card(self, screen, doc, is_dragging=False, in_slot=False):
        """Render a document card with professional styling"""
        rect = doc['rect']
        color = doc['color']

        # Shadow (larger when dragging)
        shadow_offset = 10 if is_dragging else (3 if not in_slot else 4)
        shadow_alpha = 80 if is_dragging else 40
        EducationVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                          EducationUIMetrics.RADIUS_MEDIUM)

        # Card background
        if is_dragging:
            bg_color = (245, 250, 255)
            border_color = EducationUIColors.EDUCATION_PRIMARY
            border_width = 3
        elif doc.get('hover'):
            bg_color = (250, 252, 255)
            border_color = color
            border_width = 2
        else:
            bg_color = EducationUIColors.PAPER_BG
            border_color = EducationUIColors.PANEL_BORDER
            border_width = 1

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Icon area
        icon_size = 45
        icon_rect = pygame.Rect(rect.x + 12, rect.centery - icon_size // 2,
                               icon_size, icon_size)
        pygame.draw.rect(screen, color, icon_rect,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)

        # Icon
        icon_text = self.font_icon.render(doc['icon'], True, (255, 255, 255))
        icon_x = icon_rect.centerx - icon_text.get_width() // 2
        icon_y = icon_rect.centery - icon_text.get_height() // 2
        screen.blit(icon_text, (icon_x, icon_y))

        # Document name
        name_text = self.font_doc_name.render(doc['name'], True,
                                             EducationUIColors.TEXT_PRIMARY)
        screen.blit(name_text, (rect.x + icon_size + 25,
                               rect.centery - name_text.get_height() // 2))

        # Type indicator stripe
        stripe_rect = pygame.Rect(rect.right - 8, rect.y + 5, 4, rect.height - 10)
        pygame.draw.rect(screen, color, stripe_rect, border_radius=2)

    def _render_submit_button(self, screen):
        """Render the submit button"""
        # Calculate scaled rect
        width = int(200 * self.button_scale)
        height = int(50 * self.button_scale)
        x = self.SCREEN_WIDTH // 2 - width // 2
        y = 530 - (height - 50) // 2

        scaled_rect = pygame.Rect(x, y, width, height)

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, scaled_rect, 4, 40,
                                          scaled_rect.height // 2)

        # Button
        color = EducationUIColors.EDUCATION_PRIMARY if self.button_hover else EducationUIColors.BUTTON_DEFAULT
        pygame.draw.rect(screen, color, scaled_rect, border_radius=scaled_rect.height // 2)

        # Text
        btn_text = self.font_button.render("Submit Request", True, EducationUIColors.TEXT_LIGHT)
        screen.blit(btn_text, (scaled_rect.centerx - btn_text.get_width() // 2,
                              scaled_rect.centery - btn_text.get_height() // 2))

        # Update actual button rect for click detection
        self.submit_button = scaled_rect

    def _render_result(self, screen):
        """Render result modal with typewriter effect"""
        scale = self.result_scale.value
        alpha = self.result_alpha.value

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(150 * alpha)))
        screen.blit(overlay, (0, 0))

        # Modal dimensions
        modal_width = int(550 * scale)
        modal_height = int(280 * scale)
        modal_x = (self.SCREEN_WIDTH - modal_width) // 2
        modal_y = (self.SCREEN_HEIGHT - modal_height) // 2

        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, modal_rect, 10, 80,
                                          EducationUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, modal_rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        if self.verification_complete:
            # Header strip (yellow for "wait" status)
            header_color = EducationUIColors.PENDING
            header_rect = pygame.Rect(modal_x, modal_y, modal_width, 55)
            pygame.draw.rect(screen, header_color, header_rect,
                            border_top_left_radius=EducationUIMetrics.RADIUS_LARGE,
                            border_top_right_radius=EducationUIMetrics.RADIUS_LARGE)

            # Title with checkmark
            title_text = self.font_result.render("✓ Documents Verified!", True,
                                                EducationUIColors.TEXT_LIGHT)
            screen.blit(title_text, (modal_rect.centerx - title_text.get_width() // 2,
                                    modal_y + 12))

            # Messages with typewriter effect
            messages = [
                "Your documents are in order.",
                "Unfortunately, all laptops are currently checked out.",
                "",
                "You've been added to the waitlist.",
                "We'll notify you when one is available."
            ]

            y = modal_y + 80
            chars_shown = int(self.typewriter_progress)
            total_chars = 0

            for msg in messages:
                if not msg:
                    y += 15
                    continue

                # Calculate how much of this message to show
                msg_start = total_chars
                msg_end = total_chars + len(msg)

                if chars_shown >= msg_start:
                    visible_chars = min(chars_shown - msg_start, len(msg))
                    visible_text = msg[:visible_chars]

                    if visible_text:
                        color = EducationUIColors.TEXT_PRIMARY if messages.index(msg) == 0 else EducationUIColors.TEXT_SECONDARY
                        text_surface = self.font_message.render(visible_text, True, color)
                        screen.blit(text_surface, (modal_rect.centerx - self.font_message.size(msg)[0] // 2, y))

                total_chars = msg_end + 1
                y += 30

            # Stop typewriter when done
            if chars_shown >= total_chars:
                self.typewriter_active = False

        else:
            # Header strip (red for error)
            header_color = EducationUIColors.BLOCKED
            header_rect = pygame.Rect(modal_x, modal_y, modal_width, 55)
            pygame.draw.rect(screen, header_color, header_rect,
                            border_top_left_radius=EducationUIMetrics.RADIUS_LARGE,
                            border_top_right_radius=EducationUIMetrics.RADIUS_LARGE)

            # Title
            title_text = self.font_result.render("✗ Incorrect Documents", True,
                                                EducationUIColors.TEXT_LIGHT)
            screen.blit(title_text, (modal_rect.centerx - title_text.get_width() // 2,
                                    modal_y + 12))

            # Message
            msg = "Please provide the correct required documents."
            msg_text = self.font_message.render(msg, True, EducationUIColors.BLOCKED)
            screen.blit(msg_text, (modal_rect.centerx - msg_text.get_width() // 2,
                                  modal_y + 100))

            # Hint
            hint = "Check that Photo ID and Foster Verification are correct."
            hint_text = self.font_small.render(hint, True, EducationUIColors.TEXT_SECONDARY)
            screen.blit(hint_text, (modal_rect.centerx - hint_text.get_width() // 2,
                                   modal_y + 150))

        # Border
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, modal_rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def start(self):
        """Start the ID verification game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.verification_complete = False
        self.typewriter_progress = 0
        self.typewriter_active = False

        # Reset documents
        for doc in self.documents:
            doc['placed'] = False
            doc['hover'] = False
            doc['rect'].x = doc['original_pos'][0]
            doc['rect'].y = doc['original_pos'][1]

        # Reset form slots
        for slot in self.form_slots:
            slot['filled'] = None

        # Clear effects
        self.particles.clear()
        self.popups.clear()

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False
