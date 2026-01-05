"""
Healthcare Mail Sorting Mini-Game
Drag and drop mail into Important or Junk piles
Reveals Medi-Cal termination notice
UPGRADED with healthcare visual system - drag effects, particles, polish
"""
import pygame
import random
import math

from part_4_healthcare.activities.healthcare_visual_base import (
    HealthcareUIColors, HealthcareUIMetrics, HealthcareVisualHelpers,
    HealthcareVisualComponents, UIAnimation, healthcare_visuals
)
from part_4_healthcare.activities.healthcare_particle_effects import healthcare_particles
from part_4_healthcare.activities.healthcare_feedback_popups import healthcare_feedback


class HealthcareMailGame:
    """Sort mail to find the Medi-Cal termination notice"""

    # Mail type colors with healthcare theme
    MAIL_COLORS = {
        'junk': (255, 220, 100),        # Yellow - promotional
        'important': (180, 200, 255),   # Light blue - bills/statements
        'medicaid': (255, 120, 120),    # Red - urgent/healthcare
    }

    MAIL_EDGE_COLORS = {
        'junk': (200, 160, 50),
        'important': (100, 130, 200),
        'medicaid': (200, 60, 60),
    }

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Mail pieces
        self.mail_pieces = []

        # Zones
        self.junk_zone = pygame.Rect(80, 480, 280, 170)
        self.important_zone = pygame.Rect(920, 480, 280, 170)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)
        self.drag_rotation = 0
        self.drag_start_time = 0
        self.last_drag_pos = (0, 0)
        self.particle_emit_timer = 0

        # Sorting progress
        self.correctly_sorted = 0
        self.total_to_sort = 8
        self.found_medicaid_notice = False

        # Zone hover states
        self.junk_zone_glow = UIAnimation(0.0, 0.0, 0.2)
        self.important_zone_glow = UIAnimation(0.0, 0.0, 0.2)
        self.junk_sorted_count = 0
        self.important_sorted_count = 0

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0
        self.instruction_alpha = UIAnimation(1.0, 1.0, 0.5)

        # Special notice reveal
        self.reveal_timer = 0
        self.showing_notice = False
        self.notice_scale = UIAnimation(0.0, 0.0, 0.3)
        self.notice_shake = 0
        self.flash_alpha = 0

        # Screen shake
        self.shake_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # Mail animations
        self.mail_animations = {}  # mail_id -> animation data

        # Progress counter animation
        self.progress_scale = UIAnimation(1.0, 1.0, 0.15)
        self.score = 0
        self.score_display = UIAnimation(0.0, 0.0, 0.3)

        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.label_font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 20)
        self.notice_title_font = pygame.font.Font(None, 44)
        self.notice_font = pygame.font.Font(None, 26)

    def create_mail_pieces(self):
        """Create various mail pieces including the Medi-Cal notice"""
        self.mail_pieces = []
        self.mail_animations = {}

        mail_types = [
            {'type': 'junk', 'label': 'PIZZA DEAL!', 'sublabel': 'Dominos'},
            {'type': 'junk', 'label': '50% OFF SALE', 'sublabel': 'Target'},
            {'type': 'junk', 'label': 'CREDIT OFFER', 'sublabel': 'Bank'},
            {'type': 'junk', 'label': 'BUY NOW!', 'sublabel': 'Amazon'},
            {'type': 'important', 'label': 'BANK STMT', 'sublabel': 'Chase'},
            {'type': 'important', 'label': 'RENT DUE', 'sublabel': 'Landlord'},
            {'type': 'important', 'label': 'TLP NOTICE', 'sublabel': 'Housing'},
            {'type': 'medicaid', 'label': 'MEDI-CAL', 'sublabel': 'URGENT'},
        ]

        # Grid positions with slight randomization
        positions = []
        for row in range(2):
            for col in range(4):
                x = 320 + col * 170 + random.randint(-10, 10)
                y = 180 + row * 130 + random.randint(-5, 5)
                positions.append((x, y))
        random.shuffle(positions)

        # Create mail pieces
        for i, mail_data in enumerate(mail_types):
            rect = pygame.Rect(positions[i][0], positions[i][1], 150, 90)
            mail_id = f"mail_{i}"

            self.mail_pieces.append({
                'id': mail_id,
                'rect': rect,
                'type': mail_data['type'],
                'label': mail_data['label'],
                'sublabel': mail_data['sublabel'],
                'sorted': False,
                'original_pos': (rect.x, rect.y),
                'rotation': random.uniform(-3, 3),
            })

            # Animation for this mail piece
            self.mail_animations[mail_id] = {
                'scale': UIAnimation(0.0, 1.0, 0.3),  # Entrance animation
                'alpha': UIAnimation(0.0, 1.0, 0.4),
                'hover_scale': UIAnimation(1.0, 1.0, 0.1),
                'shake_offset': 0,
            }

    def handle_event(self, event):
        """Handle mouse events for dragging mail"""
        if not self.active or self.showing_notice:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()

                # Check mail in reverse order (top-most first)
                for mail in reversed(self.mail_pieces):
                    if not mail['sorted'] and mail['rect'].collidepoint(mouse_pos):
                        self.dragging = mail
                        self.drag_offset = (
                            mail['rect'].x - mouse_pos[0],
                            mail['rect'].y - mouse_pos[1]
                        )
                        self.drag_rotation = 0
                        self.drag_start_time = pygame.time.get_ticks()
                        self.last_drag_pos = mouse_pos

                        # Lift animation
                        anim = self.mail_animations.get(mail['id'])
                        if anim:
                            anim['hover_scale'].target = 1.08

                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                mail = self.dragging
                dropped_correctly = False
                is_wrong_zone = False

                # Check junk zone
                if self.junk_zone.colliderect(mail['rect']):
                    if mail['type'] == 'junk':
                        dropped_correctly = True
                        self.junk_sorted_count += 1
                        self._place_in_zone(mail, self.junk_zone, self.junk_sorted_count)
                    else:
                        is_wrong_zone = True

                # Check important zone
                elif self.important_zone.colliderect(mail['rect']):
                    if mail['type'] in ['important', 'medicaid']:
                        dropped_correctly = True
                        self.important_sorted_count += 1
                        self._place_in_zone(mail, self.important_zone, self.important_sorted_count)

                        # Found the Medi-Cal notice!
                        if mail['type'] == 'medicaid':
                            self.found_medicaid_notice = True
                            self.reveal_timer = 150
                            self.flash_alpha = 200

                            # Special effects
                            healthcare_particles.emit_mail_important(mail['rect'].centerx, mail['rect'].centery)
                            healthcare_particles.emit_confetti(mail['rect'].centerx, mail['rect'].centery, count=40)
                            healthcare_feedback.add_mail_found(mail['rect'].centerx, mail['rect'].centery - 50, "Medi-Cal")
                    else:
                        is_wrong_zone = True

                if dropped_correctly:
                    mail['sorted'] = True
                    self.correctly_sorted += 1
                    self.score += 10

                    # Success feedback
                    healthcare_particles.emit_success(mail['rect'].centerx, mail['rect'].centery)
                    healthcare_feedback.add_sorted(mail['rect'].centerx, mail['rect'].centery - 30)

                    # Progress pulse
                    self.progress_scale.current = 1.2
                    self.progress_scale.target = 1.0
                    self.score_display.target = self.score

                elif is_wrong_zone:
                    # Wrong zone - shake and return
                    self._return_to_original(mail)
                    self.shake_timer = 0.3
                    healthcare_particles.emit_error(mail['rect'].centerx, mail['rect'].centery)
                    healthcare_feedback.add_incorrect(mail['rect'].centerx, mail['rect'].centery - 30)
                    self.score = max(0, self.score - 5)
                    self.score_display.target = self.score

                else:
                    # Dropped outside zones - just return
                    self._return_to_original(mail)

                # Reset drag state
                anim = self.mail_animations.get(mail['id'])
                if anim:
                    anim['hover_scale'].target = 1.0

                self.dragging = None
                self.drag_rotation = 0
                self.junk_zone_glow.target = 0.0
                self.important_zone_glow.target = 0.0

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()

                # Calculate velocity for rotation effect
                dx = mouse_pos[0] - self.last_drag_pos[0]
                self.drag_rotation = max(-15, min(15, dx * 0.5))

                # Update position
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

                # Paper trail particles
                self.particle_emit_timer += 1
                if self.particle_emit_timer >= 3:
                    healthcare_particles.emit_paper_trail(
                        mouse_pos[0], mouse_pos[1],
                        count=1
                    )
                    self.particle_emit_timer = 0

                # Update zone glow based on overlap
                self._update_zone_highlights()

                self.last_drag_pos = mouse_pos

        return True

    def _place_in_zone(self, mail, zone, count):
        """Place mail in a sorted zone with stacking effect"""
        # Stack with slight offset
        offset_x = (count % 3) * 8 - 8
        offset_y = (count // 3) * 6
        mail['rect'].centerx = zone.centerx + offset_x
        mail['rect'].centery = zone.centery - 20 + offset_y
        mail['rotation'] = random.uniform(-5, 5)

    def _return_to_original(self, mail):
        """Return mail to original position with animation"""
        mail['rect'].x = mail['original_pos'][0]
        mail['rect'].y = mail['original_pos'][1]

        # Shake animation
        anim = self.mail_animations.get(mail['id'])
        if anim:
            anim['shake_offset'] = 10

    def _update_zone_highlights(self):
        """Update zone glow based on dragged mail"""
        if not self.dragging:
            self.junk_zone_glow.target = 0.0
            self.important_zone_glow.target = 0.0
            return

        mail_type = self.dragging['type']

        # Check junk zone
        if self.junk_zone.colliderect(self.dragging['rect']):
            if mail_type == 'junk':
                self.junk_zone_glow.target = 1.0  # Valid
            else:
                self.junk_zone_glow.target = 0.5  # Invalid (will show red)
        else:
            self.junk_zone_glow.target = 0.0

        # Check important zone
        if self.important_zone.colliderect(self.dragging['rect']):
            if mail_type in ['important', 'medicaid']:
                self.important_zone_glow.target = 1.0
            else:
                self.important_zone_glow.target = 0.5
        else:
            self.important_zone_glow.target = 0.0

    def update(self, dt):
        """Update game state and animations"""
        if not self.active:
            return

        # Update animations
        self.junk_zone_glow.update(dt)
        self.important_zone_glow.update(dt)
        self.progress_scale.update(dt)
        self.score_display.update(dt)
        self.notice_scale.update(dt)

        # Update mail animations
        for mail_id, anim in self.mail_animations.items():
            anim['scale'].update(dt)
            anim['alpha'].update(dt)
            anim['hover_scale'].update(dt)

            # Decay shake
            if anim['shake_offset'] > 0:
                anim['shake_offset'] *= 0.85
                if anim['shake_offset'] < 0.5:
                    anim['shake_offset'] = 0

        # Screen shake decay
        if self.shake_timer > 0:
            self.shake_timer -= dt
            intensity = self.shake_timer * 20
            self.shake_offset_x = random.uniform(-intensity, intensity)
            self.shake_offset_y = random.uniform(-intensity, intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        # Flash decay
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 8)

        # Instruction fade
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 2.5:
                self.instruction_alpha.target = 0.0
            if self.instruction_timer > 3.5:
                self.show_instructions = False

        self.instruction_alpha.update(dt)

        # Notice reveal
        if self.found_medicaid_notice and self.reveal_timer > 0:
            self.reveal_timer -= 1

            if self.reveal_timer <= 90:
                self.showing_notice = True
                self.notice_scale.target = 1.0

            if self.reveal_timer == 0:
                self.completed = True

        # Check completion
        if self.correctly_sorted >= self.total_to_sort and not self.found_medicaid_notice:
            # All sorted but didn't find notice - shouldn't happen with proper game design
            pass

        # Update particles and feedback
        healthcare_particles.update(dt)
        healthcare_feedback.update(dt)

    def render(self, screen):
        """Render the mail sorting game with visual polish"""
        if not self.active:
            return

        # Apply screen shake
        shake_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)

        # Background with gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = HealthcareVisualHelpers.color_lerp(
                (30, 35, 50),
                (20, 25, 40),
                progress
            )
            pygame.draw.line(shake_surface, (*color, 250), (0, y), (self.SCREEN_WIDTH, y))

        # Title area
        title_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH, 60)
        pygame.draw.rect(shake_surface, (25, 30, 45, 200), title_rect)

        # Title
        title_text = self.title_font.render("Sort Your Mail", True, (255, 255, 255))
        shake_surface.blit(title_text, (40, 18))

        # Score display
        score_value = int(self.score_display.current)
        score_text = self.title_font.render(f"Score: {score_value}", True, HealthcareUIColors.WARNING)
        shake_surface.blit(score_text, (self.SCREEN_WIDTH - score_text.get_width() - 40, 18))

        # Progress counter with scale animation
        progress_scale = self.progress_scale.current
        progress_str = f"Sorted: {self.correctly_sorted}/{self.total_to_sort}"
        progress_text = self.label_font.render(progress_str, True, (200, 200, 200))

        if progress_scale != 1.0:
            scaled_text = pygame.transform.scale(
                progress_text,
                (int(progress_text.get_width() * progress_scale),
                 int(progress_text.get_height() * progress_scale))
            )
            progress_text = scaled_text

        progress_x = self.SCREEN_WIDTH // 2 - progress_text.get_width() // 2
        shake_surface.blit(progress_text, (progress_x, 20))

        # Draw drop zones
        self._draw_zone(shake_surface, self.junk_zone, "JUNK MAIL",
                       HealthcareUIColors.ERROR, self.junk_zone_glow.current,
                       self.junk_sorted_count, 4)

        self._draw_zone(shake_surface, self.important_zone, "IMPORTANT",
                       HealthcareUIColors.SUCCESS, self.important_zone_glow.current,
                       self.important_sorted_count, 4)

        # Draw unsorted mail pieces (sorted ones are in zones)
        for mail in self.mail_pieces:
            if mail['sorted'] and mail != self.dragging:
                # Draw sorted mail in zones (simplified)
                self._draw_mail_simple(shake_surface, mail)

        # Draw unsorted mail on top
        for mail in self.mail_pieces:
            if not mail['sorted'] and mail != self.dragging:
                self._draw_mail(shake_surface, mail, is_dragging=False)

        # Draw dragged mail on top of everything
        if self.dragging:
            self._draw_mail(shake_surface, self.dragging, is_dragging=True)

        # Instructions overlay
        if self.show_instructions and self.instruction_alpha.current > 0.01:
            alpha = int(self.instruction_alpha.current * 255)
            inst_surface = pygame.Surface((600, 50), pygame.SRCALPHA)
            pygame.draw.rect(inst_surface, (0, 0, 0, int(alpha * 0.7)),
                           inst_surface.get_rect(), border_radius=10)

            inst_text = self.label_font.render("Drag mail to JUNK or IMPORTANT pile", True, (255, 255, 255))
            inst_text.set_alpha(alpha)
            inst_surface.blit(inst_text, (inst_surface.get_width() // 2 - inst_text.get_width() // 2, 15))

            shake_surface.blit(inst_surface, (self.SCREEN_WIDTH // 2 - 300, 100))

        # ESC hint
        esc_text = self.small_font.render("Press ESC to exit", True, (100, 100, 100))
        shake_surface.blit(esc_text, (20, self.SCREEN_HEIGHT - 30))

        # Blit with shake offset
        screen.blit(shake_surface, (self.shake_offset_x, self.shake_offset_y))

        # Flash effect (on top)
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, int(self.flash_alpha)))
            screen.blit(flash_surface, (0, 0))

        # Medi-Cal notice reveal
        if self.showing_notice:
            self._draw_notice(screen)

        # Particles and feedback on top
        healthcare_particles.draw(screen)
        healthcare_feedback.draw(screen)

    def _draw_zone(self, surface, rect, label, color, glow_amount, sorted_count, max_count):
        """Draw a drop zone with glow effect"""
        # Glow effect
        if glow_amount > 0.01:
            glow_color = color if glow_amount >= 0.8 else HealthcareUIColors.ERROR
            glow_rect = rect.inflate(20, 20)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_alpha = int(glow_amount * 80)
            pygame.draw.rect(glow_surface, (*glow_color, glow_alpha),
                           glow_surface.get_rect(), border_radius=15)
            surface.blit(glow_surface, glow_rect.topleft)

        # Zone background
        zone_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(zone_surface, (*color, 30), zone_surface.get_rect(), border_radius=12)

        # Dashed border
        HealthcareVisualHelpers.draw_dashed_rect(zone_surface, (*color, 150),
                                                 zone_surface.get_rect().inflate(-4, -4),
                                                 dash_length=10, gap_length=6, width=2)
        surface.blit(zone_surface, rect.topleft)

        # Label
        label_text = self.label_font.render(label, True, color)
        label_x = rect.centerx - label_text.get_width() // 2
        surface.blit(label_text, (label_x, rect.y + 15))

        # Fill indicator (sorted count)
        fill_y = rect.bottom - 25
        for i in range(max_count):
            dot_x = rect.centerx - (max_count * 12) // 2 + i * 12 + 6
            dot_color = color if i < sorted_count else (60, 60, 70)
            pygame.draw.circle(surface, dot_color, (dot_x, fill_y), 4)

    def _draw_mail(self, surface, mail, is_dragging=False):
        """Draw a mail piece with full effects"""
        anim = self.mail_animations.get(mail['id'], {})
        scale = anim.get('scale', UIAnimation(1.0, 1.0, 0.1)).current
        alpha = anim.get('alpha', UIAnimation(1.0, 1.0, 0.1)).current
        hover_scale = anim.get('hover_scale', UIAnimation(1.0, 1.0, 0.1)).current
        shake = anim.get('shake_offset', 0)

        if scale < 0.01 or alpha < 0.01:
            return

        total_scale = scale * hover_scale
        if is_dragging:
            total_scale *= 1.1  # Lift effect

        # Calculate dimensions
        base_rect = mail['rect']
        width = int(base_rect.width * total_scale)
        height = int(base_rect.height * total_scale)

        # Mail surface
        mail_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)

        # Shadow (larger when dragging)
        shadow_offset = 8 if is_dragging else 4
        shadow_rect = pygame.Rect(10 + shadow_offset, 10 + shadow_offset, width, height)
        pygame.draw.rect(mail_surface, (0, 0, 0, int(60 * alpha)), shadow_rect, border_radius=6)

        # Mail body
        mail_rect = pygame.Rect(10, 10, width, height)
        mail_color = self.MAIL_COLORS.get(mail['type'], (200, 200, 200))
        pygame.draw.rect(mail_surface, (*mail_color, int(255 * alpha)), mail_rect, border_radius=6)

        # Edge stripe (type indicator)
        edge_color = self.MAIL_EDGE_COLORS.get(mail['type'], (150, 150, 150))
        edge_rect = pygame.Rect(10, 10, 8, height)
        pygame.draw.rect(mail_surface, (*edge_color, int(255 * alpha)), edge_rect,
                        border_top_left_radius=6, border_bottom_left_radius=6)

        # Border
        border_color = (80, 80, 90) if not is_dragging else HealthcareUIColors.PRIMARY
        pygame.draw.rect(mail_surface, (*border_color, int(200 * alpha)), mail_rect, 2, border_radius=6)

        # Label
        label_text = self.label_font.render(mail['label'], True, (40, 40, 50))
        label_text.set_alpha(int(255 * alpha))
        mail_surface.blit(label_text, (mail_rect.x + 15, mail_rect.y + 12))

        # Sublabel
        sublabel_text = self.small_font.render(mail['sublabel'], True, (100, 100, 110))
        sublabel_text.set_alpha(int(200 * alpha))
        mail_surface.blit(sublabel_text, (mail_rect.x + 15, mail_rect.y + 35))

        # Urgent badge for Medi-Cal
        if mail['type'] == 'medicaid':
            badge_text = self.small_font.render("!", True, (255, 255, 255))
            badge_rect = pygame.Rect(mail_rect.right - 25, mail_rect.y + 8, 18, 18)
            pygame.draw.circle(mail_surface, (*HealthcareUIColors.ERROR, int(255 * alpha)),
                             badge_rect.center, 9)
            mail_surface.blit(badge_text, (badge_rect.centerx - badge_text.get_width() // 2,
                                          badge_rect.centery - badge_text.get_height() // 2))

        # Apply rotation
        rotation = mail['rotation'] + (self.drag_rotation if is_dragging else 0)
        if abs(rotation) > 0.1:
            mail_surface = pygame.transform.rotate(mail_surface, rotation)

        # Position
        x = base_rect.centerx - mail_surface.get_width() // 2 + shake
        y = base_rect.centery - mail_surface.get_height() // 2

        surface.blit(mail_surface, (x, y))

    def _draw_mail_simple(self, surface, mail):
        """Draw simplified mail in sorted zones"""
        mail_color = self.MAIL_COLORS.get(mail['type'], (200, 200, 200))
        edge_color = self.MAIL_EDGE_COLORS.get(mail['type'], (150, 150, 150))

        # Simple rotated rectangle
        mail_surface = pygame.Surface((mail['rect'].width, mail['rect'].height), pygame.SRCALPHA)
        pygame.draw.rect(mail_surface, mail_color, mail_surface.get_rect(), border_radius=4)
        pygame.draw.rect(mail_surface, edge_color, pygame.Rect(0, 0, 6, mail['rect'].height),
                        border_top_left_radius=4, border_bottom_left_radius=4)

        rotated = pygame.transform.rotate(mail_surface, mail['rotation'])
        x = mail['rect'].centerx - rotated.get_width() // 2
        y = mail['rect'].centery - rotated.get_height() // 2
        surface.blit(rotated, (x, y))

    def _draw_notice(self, screen):
        """Draw the Medi-Cal termination notice reveal"""
        scale = self.notice_scale.current
        if scale < 0.01:
            return

        # Dim background
        dim_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, int(180 * scale)))
        screen.blit(dim_surface, (0, 0))

        # Notice card
        card_width = int(580 * scale)
        card_height = int(340 * scale)
        card_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - card_width // 2,
            self.SCREEN_HEIGHT // 2 - card_height // 2,
            card_width,
            card_height
        )

        # Shadow
        HealthcareVisualHelpers.draw_shadow(screen, card_rect, offset=15, blur_radius=20, alpha=100)

        # Card background
        card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)

        # Gradient
        for y in range(card_rect.height):
            progress = y / card_rect.height
            color = HealthcareVisualHelpers.color_lerp(
                HealthcareUIColors.ERROR,
                (180, 60, 60),
                progress * 0.4
            )
            pygame.draw.line(card_surface, color, (0, y), (card_rect.width, y))

        pygame.draw.rect(card_surface, (255, 255, 255), card_surface.get_rect(), 4, border_radius=15)
        screen.blit(card_surface, card_rect.topleft)

        # Content (only show when scale > 0.5)
        if scale > 0.5:
            # Header
            header_rect = pygame.Rect(card_rect.x, card_rect.y, card_rect.width, 60)
            pygame.draw.rect(screen, (180, 50, 50), header_rect,
                           border_top_left_radius=15, border_top_right_radius=15)

            title_text = self.notice_title_font.render("NOTICE OF TERMINATION", True, (255, 255, 255))
            screen.blit(title_text, (card_rect.centerx - title_text.get_width() // 2, card_rect.y + 15))

            # Content lines
            lines = [
                "Your Medi-Cal coverage has ended",
                "due to age eligibility (21 years).",
                "",
                "You may reapply under the",
                "Former Foster Youth program",
                "(ages 21-26).",
                "",
                "Visit your local clinic for assistance."
            ]

            y_offset = 80
            for line in lines:
                if line:
                    line_text = self.notice_font.render(line, True, (255, 255, 255))
                    screen.blit(line_text, (card_rect.centerx - line_text.get_width() // 2,
                                           card_rect.y + y_offset))
                y_offset += 28

            # Warning icon
            warning_text = self.notice_title_font.render("!", True, (255, 255, 255))
            pygame.draw.circle(screen, (150, 40, 40),
                             (card_rect.x + 40, card_rect.y + 35), 20)
            screen.blit(warning_text, (card_rect.x + 33, card_rect.y + 18))

    def start(self):
        """Start the mini-game"""
        self.active = True
        self.completed = False
        self.show_instructions = True
        self.instruction_timer = 0
        self.instruction_alpha = UIAnimation(1.0, 1.0, 0.5)

        self.correctly_sorted = 0
        self.junk_sorted_count = 0
        self.important_sorted_count = 0
        self.found_medicaid_notice = False
        self.showing_notice = False
        self.reveal_timer = 0
        self.notice_scale = UIAnimation(0.0, 0.0, 0.3)
        self.flash_alpha = 0
        self.score = 0
        self.score_display = UIAnimation(0.0, 0.0, 0.3)

        self.dragging = None
        self.shake_timer = 0

        # Create fresh mail pieces
        self.create_mail_pieces()

        # Clear particles/feedback
        healthcare_particles.particles.clear()
        healthcare_feedback.popups.clear()
        healthcare_feedback.achievements.clear()

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
