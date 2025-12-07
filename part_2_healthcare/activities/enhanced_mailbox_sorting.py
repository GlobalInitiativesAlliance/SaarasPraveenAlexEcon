"""
Enhanced Mailbox Sorting Mini-Game with High-Quality Graphics
Professional UI with realistic mail appearance, smooth animations, and particle effects
"""
import pygame
import random
import math

class EnhancedMailboxSortingGame:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Enhanced mail items with detailed descriptions
        self.mail_items = [
            {
                "sender": "California Department of Health",
                "subject": "URGENT: Medi-Cal Coverage Termination",
                "preview": "Your coverage under the Former Foster Youth program has ended...",
                "category": "important",
                "is_critical": True,
                "envelope_color": (255, 200, 200),  # Light red for urgent
                "stamp_color": (200, 0, 0),
                "official": True
            },
            {
                "sender": "Mario's Pizza Palace",
                "subject": "50% Off Your Next Order!",
                "preview": "Limited time offer! Order now and save big on...",
                "category": "junk",
                "is_critical": False,
                "envelope_color": (255, 255, 200),  # Yellow
                "stamp_color": (255, 150, 0),
                "official": False
            },
            {
                "sender": "Mindful Healing Center",
                "subject": "Appointment Reminder",
                "preview": "Don't forget your therapy appointment tomorrow at...",
                "category": "important",
                "is_critical": False,
                "envelope_color": (200, 230, 255),  # Light blue
                "stamp_color": (100, 150, 255),
                "official": True
            },
            {
                "sender": "Credit Solutions Inc.",
                "subject": "Pre-Approved Credit Card",
                "preview": "You've been pre-approved for a credit card with...",
                "category": "junk",
                "is_critical": False,
                "envelope_color": (230, 255, 200),  # Light green
                "stamp_color": (100, 200, 100),
                "official": False
            },
            {
                "sender": "Community Bank",
                "subject": "Monthly Statement",
                "preview": "Your account statement for the month ending...",
                "category": "important",
                "is_critical": False,
                "envelope_color": (240, 240, 240),  # Light gray
                "stamp_color": (100, 100, 200),
                "official": True
            },
            {
                "sender": "FurnitureMart",
                "subject": "MASSIVE SALE EVENT!",
                "preview": "Everything must go! 70% off all furniture...",
                "category": "junk",
                "is_critical": False,
                "envelope_color": (255, 230, 200),  # Light orange
                "stamp_color": (255, 100, 0),
                "official": False
            },
            {
                "sender": "Foster Youth Services",
                "subject": "Resources Update",
                "preview": "New resources available for former foster youth...",
                "category": "important",
                "is_critical": False,
                "envelope_color": (230, 255, 230),  # Very light green
                "stamp_color": (50, 150, 50),
                "official": True
            },
            {
                "sender": "Lucky Winner Corp",
                "subject": "YOU'VE WON $1000!!!",
                "preview": "Claim your prize now! No purchase necessary...",
                "category": "junk",
                "is_critical": False,
                "envelope_color": (255, 255, 150),  # Bright yellow
                "stamp_color": (255, 200, 0),
                "official": False
            }
        ]

        # Shuffle mail order
        random.shuffle(self.mail_items)

        # Game state
        self.current_mail = 0
        self.dragging = False
        self.drag_offset = (0, 0)
        self.score = 0
        self.mistakes = 0
        self.found_critical = False
        self.mail_position = [640, 250]  # Center of screen initially
        self.target_position = [640, 250]

        # Animation states
        self.mail_animation_time = 0
        self.sort_animation_time = 0
        self.is_animating_sort = False
        self.sort_target = None

        # Particle effects
        self.particles = []
        self.success_particles = []

        # UI elements with enhanced positioning
        self.mail_display_area = pygame.Rect(440, 180, 400, 280)
        self.important_pile = pygame.Rect(100, 480, 250, 180)
        self.junk_pile = pygame.Rect(930, 480, 250, 180)

        # Feedback areas
        self.feedback_area = pygame.Rect(440, 480, 400, 100)

        # Enhanced color palette
        self.COLORS = {
            'background': (245, 250, 255),
            'mailbox_metal': (120, 120, 140),
            'mailbox_dark': (80, 80, 100),
            'envelope_shadow': (200, 200, 200),
            'text_dark': (40, 40, 40),
            'text_light': (100, 100, 100),
            'success_green': (100, 200, 100),
            'error_red': (255, 100, 100),
            'important_blue': (100, 150, 255),
            'junk_orange': (255, 150, 100),
            'gold': (255, 215, 0),
            'paper_white': (250, 250, 250)
        }

        # Fonts with multiple sizes
        self.fonts = {
            'title': pygame.font.Font(None, 48),
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font(None, 28),
            'small': pygame.font.Font(None, 22),
            'tiny': pygame.font.Font(None, 18)
        }

        # Animation timing
        self.time = 0
        self.hover_bounce = 0
        self.pile_hover_important = False
        self.pile_hover_junk = False

    def create_particle(self, x, y, color, velocity=(0, 0)):
        """Create a particle effect"""
        particle = {
            'x': x,
            'y': y,
            'vx': velocity[0] + random.uniform(-2, 2),
            'vy': velocity[1] + random.uniform(-3, -1),
            'color': color,
            'life': 1.0,
            'size': random.uniform(2, 6)
        }
        return particle

    def update_particles(self, dt):
        """Update particle animations"""
        for particle_list in [self.particles, self.success_particles]:
            for particle in particle_list[:]:
                particle['x'] += particle['vx'] * dt * 60
                particle['y'] += particle['vy'] * dt * 60
                particle['vy'] += 300 * dt  # Gravity
                particle['life'] -= dt * 2
                particle['size'] = max(0, particle['size'] - dt * 3)

                if particle['life'] <= 0 or particle['size'] <= 0:
                    particle_list.remove(particle)

    def draw_realistic_envelope(self, surface, mail_item, x, y, scale=1.0, angle=0):
        """Draw a realistic envelope with shadows and details"""
        envelope_width = int(320 * scale)
        envelope_height = int(200 * scale)

        # Create envelope surface for rotation
        envelope_surface = pygame.Surface((envelope_width + 20, envelope_height + 20), pygame.SRCALPHA)

        # Shadow
        shadow_rect = pygame.Rect(5, 5, envelope_width, envelope_height)
        pygame.draw.rect(envelope_surface, (0, 0, 0, 30), shadow_rect, border_radius=8)

        # Main envelope
        envelope_rect = pygame.Rect(0, 0, envelope_width, envelope_height)
        pygame.draw.rect(envelope_surface, mail_item['envelope_color'], envelope_rect, border_radius=8)
        pygame.draw.rect(envelope_surface, self.COLORS['text_dark'], envelope_rect, width=2, border_radius=8)

        # Envelope flap (triangle at top)
        flap_points = [
            (envelope_width // 4, 0),
            (3 * envelope_width // 4, 0),
            (envelope_width // 2, envelope_height // 3)
        ]
        pygame.draw.polygon(envelope_surface, self.COLORS['envelope_shadow'], flap_points)
        pygame.draw.lines(envelope_surface, self.COLORS['text_dark'], False, flap_points, 2)

        # Stamp
        stamp_rect = pygame.Rect(envelope_width - 60, 15, 45, 35)
        pygame.draw.rect(envelope_surface, mail_item['stamp_color'], stamp_rect)
        pygame.draw.rect(envelope_surface, self.COLORS['text_dark'], stamp_rect, width=1)

        # Stamp perforations (tiny dots around edge)
        for i in range(0, 45, 3):
            pygame.draw.circle(envelope_surface, self.COLORS['text_dark'], (envelope_width - 60 + i, 15), 1)
            pygame.draw.circle(envelope_surface, self.COLORS['text_dark'], (envelope_width - 60 + i, 50), 1)
        for i in range(0, 35, 3):
            pygame.draw.circle(envelope_surface, self.COLORS['text_dark'], (envelope_width - 60, 15 + i), 1)
            pygame.draw.circle(envelope_surface, self.COLORS['text_dark'], (envelope_width - 15, 15 + i), 1)

        # Official seal for important mail
        if mail_item['official']:
            seal_center = (envelope_width - 35, envelope_height - 35)
            pygame.draw.circle(envelope_surface, self.COLORS['gold'], seal_center, 20)
            pygame.draw.circle(envelope_surface, self.COLORS['text_dark'], seal_center, 20, width=2)
            pygame.draw.circle(envelope_surface, self.COLORS['gold'], seal_center, 12)
            # Star in seal
            star_points = []
            for i in range(5):
                angle_deg = i * 72 - 90
                angle_rad = math.radians(angle_deg)
                star_x = seal_center[0] + math.cos(angle_rad) * 8
                star_y = seal_center[1] + math.sin(angle_rad) * 8
                star_points.append((star_x, star_y))
            pygame.draw.polygon(envelope_surface, self.COLORS['text_dark'], star_points)

        # Address lines
        sender_text = self.fonts['small'].render(mail_item['sender'], True, self.COLORS['text_dark'])
        subject_text = self.fonts['medium'].render(mail_item['subject'], True, self.COLORS['text_dark'])

        # Make critical mail subject bold and red
        if mail_item['is_critical']:
            subject_text = self.fonts['large'].render(mail_item['subject'], True, self.COLORS['error_red'])

        envelope_surface.blit(sender_text, (15, envelope_height - 80))
        envelope_surface.blit(subject_text, (15, envelope_height - 60))

        # Rotate if needed
        if angle != 0:
            envelope_surface = pygame.transform.rotate(envelope_surface, angle)

        # Blit to main surface
        final_rect = envelope_surface.get_rect(center=(x, y))
        surface.blit(envelope_surface, final_rect)

        return final_rect

    def draw_enhanced_piles(self, surface):
        """Draw enhanced sorting piles with 3D effect"""
        # Important pile
        pile_color = self.COLORS['important_blue']
        if self.pile_hover_important:
            pile_color = tuple(min(255, int(c) + 30) for c in pile_color)

        # 3D effect with multiple rectangles
        for i in range(5):
            offset_rect = pygame.Rect(
                self.important_pile.x + i,
                self.important_pile.y + i,
                self.important_pile.width,
                self.important_pile.height
            )
            color_intensity = max(50, int(pile_color[0]) - i * 10)
            shadow_color = (int(color_intensity), int(color_intensity), int(min(255, color_intensity + 50)))
            pygame.draw.rect(surface, shadow_color, offset_rect, border_radius=12)

        pygame.draw.rect(surface, pile_color, self.important_pile, border_radius=12)
        pygame.draw.rect(surface, self.COLORS['text_dark'], self.important_pile, width=3, border_radius=12)

        # Important pile icon (checkmark)
        check_center = (self.important_pile.centerx, self.important_pile.centery - 30)
        pygame.draw.circle(surface, (255, 255, 255), check_center, 25)
        pygame.draw.circle(surface, self.COLORS['success_green'], check_center, 25, width=3)

        # Draw checkmark
        check_points = [
            (check_center[0] - 8, check_center[1]),
            (check_center[0] - 3, check_center[1] + 5),
            (check_center[0] + 8, check_center[1] - 8)
        ]
        pygame.draw.lines(surface, self.COLORS['success_green'], False, check_points, 4)

        # Important label
        important_text = self.fonts['large'].render("IMPORTANT", True, (255, 255, 255))
        important_shadow = self.fonts['large'].render("IMPORTANT", True, self.COLORS['text_dark'])
        surface.blit(important_shadow, (self.important_pile.centerx - important_text.get_width()//2 + 2,
                                      self.important_pile.bottom - 40 + 2))
        surface.blit(important_text, (self.important_pile.centerx - important_text.get_width()//2,
                                    self.important_pile.bottom - 40))

        # Keyboard hint for Important pile
        key_hint = self.fonts['small'].render("Press ← (LEFT ARROW)", True, (255, 255, 255))
        key_hint_shadow = self.fonts['small'].render("Press ← (LEFT ARROW)", True, self.COLORS['text_dark'])
        surface.blit(key_hint_shadow, (self.important_pile.centerx - key_hint.get_width()//2 + 1,
                                     self.important_pile.bottom - 15 + 1))
        surface.blit(key_hint, (self.important_pile.centerx - key_hint.get_width()//2,
                              self.important_pile.bottom - 15))

        # Junk pile
        pile_color = self.COLORS['junk_orange']
        if self.pile_hover_junk:
            pile_color = tuple(min(255, int(c) + 30) for c in pile_color)

        # 3D effect
        for i in range(5):
            offset_rect = pygame.Rect(
                self.junk_pile.x + i,
                self.junk_pile.y + i,
                self.junk_pile.width,
                self.junk_pile.height
            )
            color_intensity = max(50, int(pile_color[0]) - i * 10)
            shadow_color = (int(min(255, color_intensity + 50)), int(color_intensity), int(color_intensity))
            pygame.draw.rect(surface, shadow_color, offset_rect, border_radius=12)

        pygame.draw.rect(surface, pile_color, self.junk_pile, border_radius=12)
        pygame.draw.rect(surface, self.COLORS['text_dark'], self.junk_pile, width=3, border_radius=12)

        # Junk pile icon (trash can)
        trash_center = (self.junk_pile.centerx, self.junk_pile.centery - 30)

        # Trash can body
        trash_body = pygame.Rect(trash_center[0] - 15, trash_center[1] - 10, 30, 25)
        pygame.draw.rect(surface, (255, 255, 255), trash_body, border_radius=5)
        pygame.draw.rect(surface, self.COLORS['text_dark'], trash_body, width=2, border_radius=5)

        # Trash can lid
        trash_lid = pygame.Rect(trash_center[0] - 18, trash_center[1] - 15, 36, 8)
        pygame.draw.rect(surface, (255, 255, 255), trash_lid, border_radius=4)
        pygame.draw.rect(surface, self.COLORS['text_dark'], trash_lid, width=2, border_radius=4)

        # Lid handle
        pygame.draw.circle(surface, (255, 255, 255), (trash_center[0], trash_center[1] - 18), 4)
        pygame.draw.circle(surface, self.COLORS['text_dark'], (trash_center[0], trash_center[1] - 18), 4, width=2)

        # Junk label
        junk_text = self.fonts['large'].render("JUNK MAIL", True, (255, 255, 255))
        junk_shadow = self.fonts['large'].render("JUNK MAIL", True, self.COLORS['text_dark'])
        surface.blit(junk_shadow, (self.junk_pile.centerx - junk_text.get_width()//2 + 2,
                                 self.junk_pile.bottom - 40 + 2))
        surface.blit(junk_text, (self.junk_pile.centerx - junk_text.get_width()//2,
                               self.junk_pile.bottom - 40))

        # Keyboard hint for Junk pile
        key_hint = self.fonts['small'].render("Press → (RIGHT ARROW)", True, (255, 255, 255))
        key_hint_shadow = self.fonts['small'].render("Press → (RIGHT ARROW)", True, self.COLORS['text_dark'])
        surface.blit(key_hint_shadow, (self.junk_pile.centerx - key_hint.get_width()//2 + 1,
                                     self.junk_pile.bottom - 15 + 1))
        surface.blit(key_hint, (self.junk_pile.centerx - key_hint.get_width()//2,
                              self.junk_pile.bottom - 15))

    def draw_progress_bar(self, surface):
        """Draw enhanced progress bar"""
        bar_width = 400
        bar_height = 20
        bar_x = (self.SCREEN_WIDTH - bar_width) // 2
        bar_y = 50

        # Background
        bg_rect = pygame.Rect(bar_x - 5, bar_y - 5, bar_width + 10, bar_height + 10)
        pygame.draw.rect(surface, self.COLORS['mailbox_dark'], bg_rect, border_radius=15)

        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (255, 255, 255), bar_rect, border_radius=10)

        # Progress fill
        if len(self.mail_items) > 0:
            progress = self.current_mail / len(self.mail_items)
            fill_width = int(bar_width * progress)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

            # Gradient fill
            for i in range(fill_width):
                color_ratio = i / max(1, fill_width)
                r = int(100 + (155 * color_ratio))
                g = int(200 + (55 * color_ratio))
                b = 100
                pygame.draw.line(surface, (r, g, b),
                               (bar_x + i, bar_y),
                               (bar_x + i, bar_y + bar_height))

            pygame.draw.rect(surface, self.COLORS['text_dark'], fill_rect, width=1, border_radius=10)

        pygame.draw.rect(surface, self.COLORS['text_dark'], bar_rect, width=2, border_radius=10)

        # Progress text
        progress_text = f"Mail Sorted: {self.current_mail}/{len(self.mail_items)}"
        text_surface = self.fonts['medium'].render(progress_text, True, self.COLORS['text_dark'])
        surface.blit(text_surface, (bar_x + bar_width + 15, bar_y - 5))

    def handle_event(self, event):
        """Handle enhanced input with smooth interactions"""
        if not self.active or self.completed or self.current_mail >= len(self.mail_items):
            return False

        mouse_pos = pygame.mouse.get_pos()

        # Check pile hovering
        self.pile_hover_important = self.important_pile.collidepoint(mouse_pos)
        self.pile_hover_junk = self.junk_pile.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mail_display_area.collidepoint(mouse_pos) and not self.is_animating_sort:
                self.dragging = True
                self.drag_offset = (mouse_pos[0] - self.mail_position[0],
                                  mouse_pos[1] - self.mail_position[1])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False

                # Check which pile the mail was dropped on
                mail_rect = pygame.Rect(self.mail_position[0] - 160, self.mail_position[1] - 100, 320, 200)

                if self.important_pile.colliderect(mail_rect):
                    self.sort_mail("important")
                elif self.junk_pile.colliderect(mail_rect):
                    self.sort_mail("junk")
                else:
                    # Snap back to center
                    self.target_position = [640, 250]

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.mail_position[0] = mouse_pos[0] - self.drag_offset[0]
            self.mail_position[1] = mouse_pos[1] - self.drag_offset[1]

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_j:
                self.sort_mail("important")
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_k:
                self.sort_mail("junk")
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def sort_mail(self, choice):
        """Sort mail with enhanced feedback"""
        if self.current_mail >= len(self.mail_items) or self.is_animating_sort:
            return

        mail_item = self.mail_items[self.current_mail]
        correct = (choice == mail_item["category"])

        # Start sort animation
        self.is_animating_sort = True
        self.sort_animation_time = 0
        self.sort_target = self.important_pile.center if choice == "important" else self.junk_pile.center

        # Create particles
        particle_color = self.COLORS['success_green'] if correct else self.COLORS['error_red']
        for _ in range(15):
            particle = self.create_particle(
                self.mail_position[0] + random.uniform(-50, 50),
                self.mail_position[1] + random.uniform(-50, 50),
                particle_color,
                (random.uniform(-3, 3), random.uniform(-5, -1))
            )
            self.particles.append(particle)

        if correct:
            self.score += 10
            if mail_item["is_critical"]:
                self.found_critical = True
                self.score += 20  # Bonus for finding critical mail
                # Extra success particles
                for _ in range(20):
                    particle = self.create_particle(
                        self.mail_position[0],
                        self.mail_position[1],
                        self.COLORS['gold'],
                        (random.uniform(-5, 5), random.uniform(-8, -3))
                    )
                    self.success_particles.append(particle)
        else:
            self.mistakes += 1

        self.current_mail += 1

    def update(self, dt):
        """Update enhanced animations"""
        if not self.active:
            return

        self.time += dt
        self.hover_bounce = math.sin(self.time * 3) * 5

        # Update particles
        self.update_particles(dt)

        # Handle sort animation
        if self.is_animating_sort:
            self.sort_animation_time += dt * 4  # Animation speed

            if self.sort_animation_time >= 1.0:
                self.is_animating_sort = False
                self.sort_animation_time = 0
                self.mail_position = [640, 250]  # Reset to center
                self.target_position = [640, 250]

                # Check if game is complete
                if self.current_mail >= len(self.mail_items):
                    self.complete_game()
            else:
                # Smooth animation to sort pile
                progress = self.sort_animation_time
                # Ease out animation
                eased_progress = 1 - (1 - progress) ** 3

                start_pos = [640, 250]
                self.mail_position[0] = start_pos[0] + (self.sort_target[0] - start_pos[0]) * eased_progress
                self.mail_position[1] = start_pos[1] + (self.sort_target[1] - start_pos[1]) * eased_progress

        # Smooth movement to target when not dragging
        elif not self.dragging:
            dx = self.target_position[0] - self.mail_position[0]
            dy = self.target_position[1] - self.mail_position[1]
            self.mail_position[0] += dx * dt * 8
            self.mail_position[1] += dy * dt * 8

    def complete_game(self):
        """Complete the mailbox sorting game"""
        self.completed = True

        if self.objective_manager:
            # Both cases advance to the next objective
            # The apartment interior handles the actual objective completion
            # when it detects the activity is completed
            self.objective_manager.advance_to_next_objective()

    def render(self, screen):
        """Render the enhanced mailbox sorting interface"""
        if not self.active:
            return

        # Enhanced background gradient
        for y in range(self.SCREEN_HEIGHT):
            color_ratio = y / self.SCREEN_HEIGHT
            r = int(245 + (10 * color_ratio))
            g = int(250 + (5 * color_ratio))
            b = 255
            pygame.draw.line(screen, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))

        # Title with shadow
        title_shadow = self.fonts['title'].render("Sort Your Mail", True, (100, 100, 100))
        title_text = self.fonts['title'].render("Sort Your Mail", True, self.COLORS['text_dark'])
        screen.blit(title_shadow, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 15 + 3))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 15))

        # Instructions box with clear background
        instructions = [
            "🎯 HOW TO PLAY:",
            "• DRAG mail to the correct pile OR use arrow keys",
            "• LEFT ARROW (←) = Important pile",
            "• RIGHT ARROW (→) = Junk pile",
            "",
            "📋 IMPORTANT MAIL: Government, medical, bank notices",
            "🗑️  JUNK MAIL: Ads, sales offers, spam"
        ]

        # Draw instruction background
        instruction_bg = pygame.Rect(10, 85, 500, len(instructions) * 22 + 20)
        pygame.draw.rect(screen, (30, 30, 35, 220), instruction_bg, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), instruction_bg, width=2, border_radius=10)

        for i, instruction in enumerate(instructions):
            color = (255, 255, 255) if instruction.startswith(('🎯', '📋', '🗑️')) else self.COLORS['text_light']
            font = self.fonts['medium'] if instruction.startswith(('🎯', '📋', '🗑️')) else self.fonts['small']
            text = font.render(instruction, True, color)
            screen.blit(text, (20, 95 + i * 22))

        # Progress bar
        self.draw_progress_bar(screen)

        # Enhanced sorting piles
        self.draw_enhanced_piles(screen)

        # Current mail item (if not complete)
        if self.current_mail < len(self.mail_items):
            mail_item = self.mail_items[self.current_mail]

            # Add hover effect
            hover_offset = self.hover_bounce if not self.dragging else 0
            mail_y = self.mail_position[1] + hover_offset

            # Draw envelope with realistic details
            angle = random.uniform(-2, 2) if self.dragging else 0
            self.draw_realistic_envelope(screen, mail_item, self.mail_position[0], mail_y, angle=angle)

            # Preview text box
            if not self.dragging and not self.is_animating_sort:
                preview_rect = pygame.Rect(self.mail_position[0] - 200, self.mail_position[1] + 120, 400, 60)
                pygame.draw.rect(screen, (255, 255, 255, 240), preview_rect, border_radius=8)
                pygame.draw.rect(screen, self.COLORS['text_dark'], preview_rect, width=2, border_radius=8)

                preview_text = self.fonts['small'].render(mail_item['preview'][:50] + "...", True, self.COLORS['text_dark'])
                text_rect = preview_text.get_rect(center=preview_rect.center)
                screen.blit(preview_text, text_rect)

        # Score and mistakes
        score_text = f"Score: {self.score}"
        mistakes_text = f"Mistakes: {self.mistakes}"

        score_surface = self.fonts['medium'].render(score_text, True, self.COLORS['success_green'])
        mistakes_surface = self.fonts['medium'].render(mistakes_text, True, self.COLORS['error_red'])

        screen.blit(score_surface, (self.SCREEN_WIDTH - 200, 100))
        screen.blit(mistakes_surface, (self.SCREEN_WIDTH - 200, 130))

        # Draw particles
        for particle in self.particles + self.success_particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            size = max(1, int(particle['size']))

            # Create a surface with per-pixel alpha for the particle
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            screen.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))

        # Completion message
        if self.completed:
            if self.found_critical:
                message = f"Excellent! Found the important Medi-Cal notice! Score: {self.score}"
                color = self.COLORS['success_green']
            else:
                message = f"Complete! But you missed the critical health notice. Score: {self.score}"
                color = self.COLORS['error_red']

            # Message background
            message_surface = self.fonts['large'].render(message, True, color)
            bg_rect = message_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 200))
            bg_rect.inflate_ip(40, 20)

            pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=15)
            pygame.draw.rect(screen, color, bg_rect, width=3, border_radius=15)

            message_rect = message_surface.get_rect(center=bg_rect.center)
            screen.blit(message_surface, message_rect)

    def start(self):
        """Start the enhanced mailbox sorting game"""
        self.active = True
        self.completed = False
        self.current_mail = 0
        self.score = 0
        self.mistakes = 0
        self.found_critical = False
        self.mail_position = [640, 250]
        self.target_position = [640, 250]
        self.is_animating_sort = False
        self.particles.clear()
        self.success_particles.clear()

        # Shuffle mail items for variety
        random.shuffle(self.mail_items)

    def stop(self):
        """Stop the enhanced mailbox sorting game"""
        self.active = False