"""
Mailbox Sorting Mini-Game
Drag letters to "Important" or "Junk" piles
"""
import pygame
import random

class MailboxSortingGame:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Enhanced mail items with visual properties
        self.mail_items = [
            {"text": "Notice: Your Medi-Cal coverage has ended", "category": "important", "is_critical": True,
             "sender": "State of California", "mail_type": "official", "urgency": "HIGH"},
            {"text": "50% Off Pizza Special!", "category": "junk", "is_critical": False,
             "sender": "Mario's Pizza", "mail_type": "advertisement", "urgency": "LOW"},
            {"text": "Therapy Appointment Reminder", "category": "important", "is_critical": False,
             "sender": "Wellness Center", "mail_type": "appointment", "urgency": "MEDIUM"},
            {"text": "Credit Card Pre-Approval", "category": "junk", "is_critical": False,
             "sender": "Capital Bank", "mail_type": "offer", "urgency": "LOW"},
            {"text": "Bank Statement", "category": "important", "is_critical": False,
             "sender": "First National", "mail_type": "statement", "urgency": "MEDIUM"},
            {"text": "Furniture Sale - Limited Time!", "category": "junk", "is_critical": False,
             "sender": "Furniture Depot", "mail_type": "advertisement", "urgency": "LOW"},
            {"text": "Foster Youth Services Update", "category": "important", "is_critical": False,
             "sender": "Department of Services", "mail_type": "official", "urgency": "MEDIUM"},
            {"text": "Win $1000 Cash Now!", "category": "junk", "is_critical": False,
             "sender": "Lucky Sweepstakes", "mail_type": "scam", "urgency": "LOW"}
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

        # Enhanced UI elements
        self.mail_rect = pygame.Rect(450, 180, 320, 160)
        self.important_pile = pygame.Rect(120, 450, 250, 180)
        self.junk_pile = pygame.Rect(910, 450, 250, 180)

        # Mailbox visual element (decorative)
        self.mailbox_rect = pygame.Rect(50, 50, 120, 180)

        # Visual effects and animations
        self.pile_hover = None
        self.pile_glow = {'important': 0, 'junk': 0}
        self.mail_bob = 0
        self.sparkle_particles = []
        self.sort_feedback_particles = []
        self.drop_shadow_offset = 3

        # Enhanced color palette
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.RED = (220, 20, 60)
        self.GREEN = (34, 139, 34)
        self.GRAY = (128, 128, 128)
        self.LIGHT_BLUE = (173, 216, 230)
        self.LIGHT_RED = (255, 182, 193)

        # Professional mail colors
        self.CREAM = (245, 245, 220)
        self.GOLD = (255, 215, 0)
        self.DARK_RED = (139, 0, 0)
        self.NAVY = (25, 25, 112)
        self.ENVELOPE_BEIGE = (248, 248, 240)
        self.STAMP_RED = (178, 34, 34)
        self.SHADOW_GRAY = (105, 105, 105)
        self.PAPER_WHITE = (252, 252, 252)
        self.OFFICIAL_BLUE = (240, 248, 255)
        self.WARNING_YELLOW = (255, 255, 224)

        # Enhanced fonts
        self.font_title = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)

    def handle_event(self, event):
        """Handle player input"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if clicking on current mail
            if self.mail_rect.collidepoint(mouse_pos) and self.current_mail < len(self.mail_items):
                self.dragging = True
                self.drag_offset = (
                    mouse_pos[0] - self.mail_rect.x,
                    mouse_pos[1] - self.mail_rect.y
                )

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                mouse_pos = pygame.mouse.get_pos()

                # Check which pile the mail was dropped on
                current_item = self.mail_items[self.current_mail]

                if self.important_pile.collidepoint(mouse_pos):
                    self.sort_mail("important", current_item)
                elif self.junk_pile.collidepoint(mouse_pos):
                    self.sort_mail("junk", current_item)
                else:
                    # Reset position if dropped elsewhere
                    self.mail_rect.x = 500
                    self.mail_rect.y = 200

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()

            if self.dragging:
                self.mail_rect.x = mouse_pos[0] - self.drag_offset[0]
                self.mail_rect.y = mouse_pos[1] - self.drag_offset[1]

            # Update hover states for visual feedback
            self.pile_hover = None
            if self.important_pile.collidepoint(mouse_pos):
                self.pile_hover = 'important'
            elif self.junk_pile.collidepoint(mouse_pos):
                self.pile_hover = 'junk'

        return True

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events from main game engine"""
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release events from main game engine"""
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONUP, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_motion(self, pos):
        """Handle mouse motion events from main game engine"""
        event = type('Event', (), {'type': pygame.MOUSEMOTION, 'pos': pos})()
        self.handle_event(event)

    def sort_mail(self, pile, mail_item):
        """Handle mail sorting result"""
        correct = (pile == mail_item["category"])

        # Determine which pile position for visual feedback
        if pile == "important":
            pile_pos = (self.important_pile.centerx, self.important_pile.centery)
        else:
            pile_pos = (self.junk_pile.centerx, self.junk_pile.centery)

        if correct:
            self.score += 1
            if mail_item["is_critical"]:
                self.found_critical = True
                # Special effect for critical mail
                self.create_sparkle_effect(pile_pos, self.GOLD)
                self.create_feedback_particle(pile_pos, "CRITICAL!", self.DARK_RED)
            else:
                # Regular correct sorting feedback
                self.create_feedback_particle(pile_pos, "Correct!", self.GREEN)
        else:
            self.mistakes += 1
            # Wrong sorting feedback
            self.create_feedback_particle(pile_pos, "Wrong!", self.RED)

        # Move to next mail
        self.current_mail += 1

        # Reset mail position to center
        self.mail_rect.x = 450
        self.mail_rect.y = 180

        # Check if game is complete
        if self.current_mail >= len(self.mail_items):
            self.complete_game()

    def complete_game(self):
        """Complete the mailbox sorting game"""
        self.completed = True

        # Must find the critical Medi-Cal notice to progress
        if self.found_critical:
            print("[MAILBOX] Critical mail found! Completing check_mailbox objective...")
            if self.objective_manager:
                self.objective_manager.complete_current_objective()
        else:
            # Player missed the important notice - restart or hint
            self.current_mail = 0
            self.score = 0
            self.mistakes = 0
            self.found_critical = False
            random.shuffle(self.mail_items)

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update visual effects
        self.update_visual_effects(dt)

    def update_visual_effects(self, dt):
        """Update all visual effects and animations"""
        # Update mail bobbing animation
        self.mail_bob += dt * 3

        # Update pile glow effects
        for pile in ['important', 'junk']:
            if self.pile_hover == pile:
                self.pile_glow[pile] = min(1.0, self.pile_glow[pile] + dt * 4)
            else:
                self.pile_glow[pile] = max(0.0, self.pile_glow[pile] - dt * 3)

        # Update sparkle particles
        for particle in self.sparkle_particles[:]:
            particle['life'] -= dt
            particle['y'] -= particle['speed'] * dt
            particle['x'] += particle['drift'] * dt
            if particle['life'] <= 0:
                self.sparkle_particles.remove(particle)

        # Update feedback particles
        for particle in self.sort_feedback_particles[:]:
            particle['life'] -= dt
            particle['y'] -= dt * 50
            if particle['life'] <= 0:
                self.sort_feedback_particles.remove(particle)

    def create_sparkle_effect(self, pos, color=(255, 255, 255)):
        """Create sparkle particles at position"""
        import math
        for _ in range(8):
            angle = random.random() * 2 * math.pi
            speed = random.randint(20, 60)
            self.sparkle_particles.append({
                'x': pos[0] + random.randint(-10, 10),
                'y': pos[1] + random.randint(-10, 10),
                'speed': speed,
                'drift': math.cos(angle) * 30,
                'life': 0.8,
                'color': color,
                'size': random.randint(2, 6)
            })

    def create_feedback_particle(self, pos, text, color):
        """Create feedback particle for correct/incorrect sorting"""
        self.sort_feedback_particles.append({
            'x': pos[0],
            'y': pos[1],
            'text': text,
            'color': color,
            'life': 1.5
        })

    def draw(self, screen):
        """Draw the mailbox sorting interface with high-quality visuals"""
        if not self.active:
            return

        # Professional gradient background
        self.draw_gradient_background(screen)

        # Decorative mailbox in corner
        self.draw_decorative_mailbox(screen)

        # Enhanced title with shadow
        self.draw_title_with_shadow(screen)

        # Visual instruction panel
        self.draw_instruction_panel(screen)

        # Enhanced sorting piles with glow effects
        self.draw_enhanced_piles(screen)

        # High-quality mail envelope
        if self.current_mail < len(self.mail_items):
            self.draw_detailed_mail_envelope(screen)

        # Professional status panel
        self.draw_status_panel(screen)

        # Draw all particle effects
        self.draw_particle_effects(screen)

        # Completion overlay
        if self.completed:
            self.draw_completion_overlay(screen)

    def draw_gradient_background(self, screen):
        """Draw a professional gradient background"""
        # Create vertical gradient from light blue to cream
        for y in range(self.SCREEN_HEIGHT):
            ratio = y / self.SCREEN_HEIGHT
            r = int(240 + (self.CREAM[0] - 240) * ratio)
            g = int(248 + (self.CREAM[1] - 248) * ratio)
            b = int(255 + (self.CREAM[2] - 255) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))

    def draw_decorative_mailbox(self, screen):
        """Draw a decorative mailbox in the corner"""
        # Mailbox shadow
        shadow_rect = self.mailbox_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, self.SHADOW_GRAY, shadow_rect, border_radius=8)

        # Mailbox body
        pygame.draw.rect(screen, self.NAVY, self.mailbox_rect, border_radius=8)

        # Mailbox door
        door_rect = pygame.Rect(self.mailbox_rect.x + 10, self.mailbox_rect.y + 40,
                               self.mailbox_rect.width - 20, 80)
        pygame.draw.rect(screen, self.BLUE, door_rect, border_radius=5)
        pygame.draw.rect(screen, self.WHITE, door_rect, width=2, border_radius=5)

        # Mailbox handle
        handle_rect = pygame.Rect(door_rect.right - 15, door_rect.centery - 5, 10, 10)
        pygame.draw.circle(screen, self.GOLD, handle_rect.center, 5)

        # "MAIL" text on mailbox
        mail_text = self.font_tiny.render("MAIL", True, self.WHITE)
        mail_rect = mail_text.get_rect(center=(self.mailbox_rect.centerx, self.mailbox_rect.y + 20))
        screen.blit(mail_text, mail_rect)

    def draw_title_with_shadow(self, screen):
        """Draw title with professional shadow effect"""
        title_text = "Sort Your Mail"

        # Shadow
        title_shadow = self.font_title.render(title_text, True, self.SHADOW_GRAY)
        shadow_rect = title_shadow.get_rect(center=(self.SCREEN_WIDTH // 2 + 2, 52))
        screen.blit(title_shadow, shadow_rect)

        # Main title
        title_surface = self.font_title.render(title_text, True, self.NAVY)
        title_rect = title_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)

    def draw_instruction_panel(self, screen):
        """Draw a professional instruction panel"""
        panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 200, 90, 400, 80)

        # Panel background with transparency effect
        panel_surface = pygame.Surface((400, 80))
        panel_surface.set_alpha(220)
        panel_surface.fill(self.PAPER_WHITE)
        screen.blit(panel_surface, panel_rect)

        pygame.draw.rect(screen, self.BLUE, panel_rect, width=2, border_radius=5)

        instructions = [
            "Drag mail to the correct pile:",
            "• Important mail → Left pile",
            "• Junk mail → Right pile"
        ]

        y = panel_rect.y + 10
        for instruction in instructions:
            color = self.NAVY if instruction.startswith("Drag") else self.GRAY
            text = self.font_small.render(instruction, True, color)
            text_rect = text.get_rect(center=(panel_rect.centerx, y))
            screen.blit(text, text_rect)
            y += 22

    def draw_enhanced_piles(self, screen):
        """Draw sorting piles with glow and hover effects"""
        import math

        piles = [
            ('important', self.important_pile, self.LIGHT_BLUE, self.BLUE, "IMPORTANT"),
            ('junk', self.junk_pile, self.LIGHT_RED, self.RED, "JUNK MAIL")
        ]

        for pile_name, pile_rect, base_color, border_color, label in piles:
            # Calculate glow intensity
            glow_intensity = self.pile_glow[pile_name]

            # Draw shadow
            shadow_rect = pile_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(screen, self.SHADOW_GRAY, shadow_rect, border_radius=10)

            # Glow effect
            if glow_intensity > 0:
                glow_color = (*border_color, int(100 * glow_intensity))
                for i in range(5):
                    glow_rect = pile_rect.inflate(i * 8, i * 8)
                    alpha = int(50 * glow_intensity * (1 - i / 5))
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
                    glow_surface.set_alpha(alpha)
                    glow_surface.fill(border_color)
                    screen.blit(glow_surface, glow_rect)

            # Main pile area
            pile_color = base_color
            if glow_intensity > 0:
                # Brighten color when glowing
                pile_color = tuple(min(255, c + int(30 * glow_intensity)) for c in base_color)

            pygame.draw.rect(screen, pile_color, pile_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, pile_rect, width=4, border_radius=10)

            # Pile icon (folder or trash)
            icon_y = pile_rect.y + 30
            if pile_name == 'important':
                # Draw folder icon
                folder_rect = pygame.Rect(pile_rect.centerx - 25, icon_y, 50, 35)
                pygame.draw.rect(screen, border_color, folder_rect, border_radius=3)
                pygame.draw.rect(screen, pile_color, folder_rect.inflate(-6, -6), border_radius=2)
            else:
                # Draw trash icon
                trash_rect = pygame.Rect(pile_rect.centerx - 20, icon_y, 40, 35)
                pygame.draw.rect(screen, border_color, trash_rect, border_radius=5)
                # Trash lid
                lid_rect = pygame.Rect(trash_rect.x - 5, trash_rect.y - 3, 50, 8)
                pygame.draw.rect(screen, border_color, lid_rect, border_radius=2)

            # Label with enhanced styling
            label_surface = self.font_medium.render(label, True, border_color)
            label_rect = label_surface.get_rect(center=(pile_rect.centerx, pile_rect.bottom - 30))

            # Label background
            bg_rect = label_rect.copy()
            bg_rect.inflate(10, 4)
            pygame.draw.rect(screen, self.PAPER_WHITE, bg_rect, border_radius=3)

            screen.blit(label_surface, label_rect)

    def draw_detailed_mail_envelope(self, screen):
        """Draw a detailed, realistic mail envelope"""
        import math

        current_item = self.mail_items[self.current_mail]

        # Calculate bobbing effect
        bob_offset = math.sin(self.mail_bob) * 3
        envelope_rect = self.mail_rect.copy()
        envelope_rect.y += int(bob_offset)

        # Drop shadow
        shadow_rect = envelope_rect.copy()
        shadow_rect.x += self.drop_shadow_offset
        shadow_rect.y += self.drop_shadow_offset
        pygame.draw.rect(screen, self.SHADOW_GRAY, shadow_rect, border_radius=8)

        # Determine envelope color based on type
        if current_item["is_critical"]:
            envelope_color = self.WARNING_YELLOW
            border_color = self.DARK_RED
        elif current_item.get("mail_type") == "official":
            envelope_color = self.OFFICIAL_BLUE
            border_color = self.NAVY
        else:
            envelope_color = self.ENVELOPE_BEIGE
            border_color = self.GRAY

        # Main envelope
        pygame.draw.rect(screen, envelope_color, envelope_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, envelope_rect, width=3, border_radius=8)

        # Envelope flap (top triangle)
        flap_points = [
            (envelope_rect.left + 20, envelope_rect.top),
            (envelope_rect.right - 20, envelope_rect.top),
            (envelope_rect.centerx, envelope_rect.top + 25)
        ]
        pygame.draw.polygon(screen, border_color, flap_points)

        # Stamp (top right)
        stamp_rect = pygame.Rect(envelope_rect.right - 40, envelope_rect.top + 10, 25, 20)
        pygame.draw.rect(screen, self.STAMP_RED, stamp_rect, border_radius=2)
        pygame.draw.rect(screen, self.WHITE, stamp_rect, width=1, border_radius=2)

        # Postmark circle
        postmark_center = (envelope_rect.right - 60, envelope_rect.top + 35)
        pygame.draw.circle(screen, border_color, postmark_center, 15, width=2)

        # Address area background
        address_rect = pygame.Rect(envelope_rect.x + 15, envelope_rect.y + 50,
                                  envelope_rect.width - 30, envelope_rect.height - 70)
        pygame.draw.rect(screen, self.PAPER_WHITE, address_rect, border_radius=3)

        # Sender info (top of letter)
        sender = current_item.get("sender", "Unknown Sender")
        sender_surface = self.font_tiny.render(f"From: {sender}", True, self.GRAY)
        screen.blit(sender_surface, (address_rect.x + 5, address_rect.y + 5))

        # Urgency indicator
        urgency = current_item.get("urgency", "LOW")
        urgency_color = self.DARK_RED if urgency == "HIGH" else (self.RED if urgency == "MEDIUM" else self.GREEN)
        if urgency != "LOW":
            urgency_surface = self.font_tiny.render(f"{urgency} PRIORITY", True, urgency_color)
            screen.blit(urgency_surface, (address_rect.x + 5, address_rect.y + 20))

        # Main message text (wrapped and styled)
        self.draw_wrapped_text(screen, current_item["text"],
                              pygame.Rect(address_rect.x + 5, address_rect.y + 40,
                                         address_rect.width - 10, address_rect.height - 45),
                              self.font_small, self.BLACK)

    def draw_wrapped_text(self, screen, text, rect, font, color):
        """Draw text wrapped to fit within a rectangle"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = font.render(test_line, True, color)
            if test_surface.get_width() <= rect.width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        y_offset = rect.y
        line_height = font.get_height() + 2
        for line in lines:
            if y_offset + line_height > rect.bottom:
                break
            line_surface = font.render(line, True, color)
            screen.blit(line_surface, (rect.x, y_offset))
            y_offset += line_height

    def draw_status_panel(self, screen):
        """Draw professional status information panel"""
        # Panel background
        panel_rect = pygame.Rect(30, 250, 300, 120)
        panel_surface = pygame.Surface((300, 120))
        panel_surface.set_alpha(240)
        panel_surface.fill(self.PAPER_WHITE)
        screen.blit(panel_surface, panel_rect)

        pygame.draw.rect(screen, self.NAVY, panel_rect, width=2, border_radius=8)

        # Title
        title_surface = self.font_medium.render("MAIL STATUS", True, self.NAVY)
        title_rect = title_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 15))
        screen.blit(title_surface, title_rect)

        # Progress bar
        progress_rect = pygame.Rect(panel_rect.x + 20, panel_rect.y + 40, 260, 15)
        progress_fill = int(260 * (self.current_mail / len(self.mail_items)))

        pygame.draw.rect(screen, self.LIGHT_BLUE, progress_rect, border_radius=7)
        if progress_fill > 0:
            fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, progress_fill, 15)
            pygame.draw.rect(screen, self.BLUE, fill_rect, border_radius=7)

        pygame.draw.rect(screen, self.NAVY, progress_rect, width=2, border_radius=7)

        # Progress text
        progress_text = f"Mail: {self.current_mail + 1}/{len(self.mail_items)}"
        progress_surface = self.font_small.render(progress_text, True, self.BLACK)
        screen.blit(progress_surface, (panel_rect.x + 20, panel_rect.y + 65))

        # Score
        score_text = f"Correct: {self.score}"
        score_surface = self.font_small.render(score_text, True, self.GREEN)
        screen.blit(score_surface, (panel_rect.x + 20, panel_rect.y + 85))

        # Mistakes
        mistakes_text = f"Mistakes: {self.mistakes}"
        mistakes_color = self.RED if self.mistakes > 2 else self.GRAY
        mistakes_surface = self.font_small.render(mistakes_text, True, mistakes_color)
        screen.blit(mistakes_surface, (panel_rect.x + 150, panel_rect.y + 85))

    def draw_particle_effects(self, screen):
        """Draw all particle effects"""
        # Draw sparkle particles
        for particle in self.sparkle_particles:
            alpha = int(255 * particle['life'])
            size = int(particle['size'] * particle['life'])
            if size > 0:
                particle_surface = pygame.Surface((size * 2, size * 2))
                particle_surface.set_alpha(alpha)
                pygame.draw.circle(particle_surface, particle['color'], (size, size), size)
                screen.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))

        # Draw feedback particles
        for particle in self.sort_feedback_particles:
            alpha = int(255 * particle['life'])
            particle_surface = self.font_medium.render(particle['text'], True, particle['color'])
            particle_surface.set_alpha(alpha)
            text_rect = particle_surface.get_rect(center=(int(particle['x']), int(particle['y'])))
            screen.blit(particle_surface, text_rect)

    def draw_completion_overlay(self, screen):
        """Draw completion screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))

        # Result panel
        panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 300, self.SCREEN_HEIGHT // 2 - 100, 600, 200)
        pygame.draw.rect(screen, self.PAPER_WHITE, panel_rect, border_radius=15)
        pygame.draw.rect(screen, self.NAVY, panel_rect, width=4, border_radius=15)

        if self.found_critical:
            title_text = "CRITICAL NOTICE FOUND!"
            subtitle_text = "Healthcare crisis ahead..."
            title_color = self.DARK_RED
            # Add warning sparkles
            import math
            for i in range(6):
                angle = (i / 6) * 2 * math.pi
                x = panel_rect.centerx + int(math.cos(angle) * 80)
                y = panel_rect.centery - 30 + int(math.sin(angle) * 30)
                pygame.draw.polygon(screen, self.GOLD, [
                    (x, y - 8), (x - 3, y), (x, y + 8), (x + 3, y)
                ])
        else:
            title_text = "Try Again!"
            subtitle_text = "You missed something important..."
            title_color = self.NAVY

        # Title
        title_surface = self.font_title.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(panel_rect.centerx, panel_rect.centery - 20))
        screen.blit(title_surface, title_rect)

        # Subtitle
        subtitle_surface = self.font_medium.render(subtitle_text, True, self.GRAY)
        subtitle_rect = subtitle_surface.get_rect(center=(panel_rect.centerx, panel_rect.centery + 20))
        screen.blit(subtitle_surface, subtitle_rect)

    def start(self):
        """Start the mailbox sorting game"""
        self.active = True
        self.completed = False
        self.current_mail = 0
        self.dragging = False
        self.score = 0
        self.mistakes = 0
        self.found_critical = False

        # Reset mail position
        self.mail_rect.x = 500
        self.mail_rect.y = 200

        # Reshuffle mail
        random.shuffle(self.mail_items)

    def stop(self):
        """Stop the mailbox sorting game"""
        self.active = False