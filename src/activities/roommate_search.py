"""
Roommate Search Activity - Shows the harsh reality of trying to find roommates
Visual activity for Part 2 Housing when player searches for roommates at library
"""
import pygame
import math
from src.activities.activities import Activity
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class RoommateSearchActivity(Activity):
    """Computer-based roommate search showing why sharing isn't an option"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None

        self.current_listing = 0
        self.listings_viewed = 0
        self.reality_revealed = False
        self.completion_timer = 0

        self.listings = [
            {
                "title": "Looking for Roommate - 2BR Downtown",
                "price": "$650/month (half of $1,300)",
                "description": "Seeking clean, quiet professional to share 2BR.",
                "requirements": [
                    "Credit score 650+",
                    "3x rent in income ($1,950/mo)",
                    "First + Last + Deposit",
                    "Background check $50"
                ],
                "problem": "They want someone with stable income and credit",
                "posted": "2 hours ago - 47 inquiries"
            },
            {
                "title": "Room Available in 3BR House",
                "price": "$500/month + utilities",
                "description": "Young professionals, no drama, must be on lease",
                "requirements": [
                    "Must pass landlord approval",
                    "References from previous roommates",
                    "Stable job required",
                    "No couples, no overnight guests"
                ],
                "problem": "Landlord will run same checks as any apartment",
                "posted": "Posted yesterday - 83 messages"
            },
            {
                "title": "Studio Sublet Available",
                "price": "$800/month (was $900)",
                "description": "Taking over my lease, 6 months left",
                "requirements": [
                    "Landlord approval required",
                    "Income verification",
                    "Application fee $150",
                    "Must qualify on your own"
                ],
                "problem": "Still need to qualify for the full lease yourself",
                "posted": "3 days ago - 124 interested"
            },
            {
                "title": "Couch for Rent - $400/mo",
                "price": "$400/month cash",
                "description": "It's just a couch in the living room",
                "requirements": [
                    "Cash only, no lease",
                    "Can't have mail sent here",
                    "No guests ever",
                    "Could be kicked out anytime"
                ],
                "problem": "Not even legal. No tenant rights. Still $400.",
                "posted": "1 week old - Still available"
            },
            {
                "title": "YOUR STUDIO REALITY CHECK",
                "price": "Current: $900 → New: $1,035",
                "description": "Let's be honest about your situation...",
                "requirements": [
                    "Studio is 200 sq ft - legally too small to share",
                    "Lease explicitly forbids subletting or roommates",
                    "Breaking lease = eviction record = homeless",
                    "You're trapped. There's no roommate solution."
                ],
                "problem": "THIS ISN'T AN OPTION. YOU'RE STUCK.",
                "posted": "This is your reality"
            }
        ]

        self.colors = {
            'background': (20, 20, 25),
            'window': (245, 245, 250),
            'header': (59, 130, 246),
            'text': (31, 41, 55),
            'gray': (107, 114, 128),
            'requirement': (239, 68, 68),
            'problem_bg': (254, 226, 226),
            'problem_text': (153, 27, 27),
            'button': (59, 130, 246),
            'button_hover': (37, 99, 235),
            'success': (16, 185, 129),
            'final_bg': (185, 28, 28),
            'final_text': (254, 226, 226)
        }

        self.fonts = {}
        self.browser_y_offset = 0
        self.scroll_momentum = 0
        self.hovering_next = False
        self.show_final_message = False

    def start(self):
        """Initialize the activity when it starts"""
        super().start()

        self.fonts = {
            'title': pygame.font.Font(None, 32),
            'browser': pygame.font.Font(None, 24),
            'listing_title': pygame.font.Font(None, 28),
            'body': pygame.font.Font(None, 20),
            'small': pygame.font.Font(None, 18),
            'problem': pygame.font.Font(None, 22),
            'final': pygame.font.Font(None, 36)
        }

        self.browser_y_offset = 0
        self.current_listing = 0
        self.listings_viewed = 0

    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE:
            if self.show_final_message:
                self.completed = True
            elif self.current_listing >= len(self.listings) - 1:
                self.show_final_message = True

        elif key == pygame.K_SPACE or key == pygame.K_RETURN:
            if self.show_final_message:
                self.completed = True
            else:
                self.advance_listing()

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events"""
        if button == 1:
            mouse_x, mouse_y = pos

            if self.show_final_message:
                continue_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                if continue_rect.collidepoint(mouse_x, mouse_y):
                    self.completed = True
            else:
                next_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 150, 40)
                if next_rect.collidepoint(mouse_x, mouse_y):
                    self.advance_listing()

        elif button == 4:
            self.scroll_momentum = 20
        elif button == 5:
            self.scroll_momentum = -20

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        mouse_x, mouse_y = pos
        next_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 150, 40)
        self.hovering_next = next_rect.collidepoint(mouse_x, mouse_y)

    def advance_listing(self):
        """Move to next listing"""
        if self.current_listing < len(self.listings) - 1:
            self.current_listing += 1
            self.listings_viewed += 1
            self.browser_y_offset = 0

            if self.current_listing == len(self.listings) - 1:
                self.reality_revealed = True

    def update(self, dt):
        """Update the activity state"""
        if self.scroll_momentum != 0:
            self.browser_y_offset += self.scroll_momentum
            self.scroll_momentum *= 0.9
            if abs(self.scroll_momentum) < 0.5:
                self.scroll_momentum = 0

            max_scroll = -500
            self.browser_y_offset = max(max_scroll, min(0, self.browser_y_offset))

        if self.show_final_message:
            self.completion_timer += dt

    def draw(self, screen):
        """Draw the roommate search interface"""
        screen.fill(self.colors['background'])

        if self.show_final_message:
            self.draw_final_message(screen)
        else:
            self.draw_browser_window(screen)

    def draw_browser_window(self, screen):
        """Draw the browser window with listings"""
        window_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, self.colors['window'], window_rect)
        pygame.draw.rect(screen, self.colors['header'], window_rect, 2)

        header_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, 60)
        pygame.draw.rect(screen, self.colors['header'], header_rect)

        title_text = "CraigsBook - Roommate Search"
        title_surf = self.fonts['browser'].render(title_text, True, (255, 255, 255))
        screen.blit(title_surf, (70, 70))

        url_rect = pygame.Rect(200, 75, SCREEN_WIDTH - 300, 30)
        pygame.draw.rect(screen, (255, 255, 255), url_rect)
        url_text = "www.craigsbook.com/rooms/search?max=600&desperate=true"
        url_surf = self.fonts['small'].render(url_text, True, self.colors['gray'])
        screen.blit(url_surf, (210, 82))

        content_y = 130 + self.browser_y_offset
        listing = self.listings[self.current_listing]

        if self.current_listing == len(self.listings) - 1:
            bg_rect = pygame.Rect(70, 130, SCREEN_WIDTH - 140, SCREEN_HEIGHT - 230)
            pygame.draw.rect(screen, self.colors['final_bg'], bg_rect)

            title_surf = self.fonts['listing_title'].render(listing['title'], True, self.colors['final_text'])
            screen.blit(title_surf, (90, content_y))
            content_y += 50

            for req in listing['requirements']:
                req_surf = self.fonts['body'].render(f"❌ {req}", True, self.colors['final_text'])
                screen.blit(req_surf, (90, content_y))
                content_y += 30

            content_y += 30
            problem_surf = self.fonts['problem'].render(listing['problem'], True, self.colors['final_text'])
            screen.blit(problem_surf, (90, content_y))

        else:
            title_surf = self.fonts['listing_title'].render(listing['title'], True, self.colors['text'])
            screen.blit(title_surf, (90, content_y))
            content_y += 40

            price_surf = self.fonts['body'].render(listing['price'], True, self.colors['header'])
            screen.blit(price_surf, (90, content_y))
            content_y += 30

            desc_surf = self.fonts['body'].render(listing['description'], True, self.colors['text'])
            screen.blit(desc_surf, (90, content_y))
            content_y += 40

            req_title = self.fonts['body'].render("Requirements:", True, self.colors['text'])
            screen.blit(req_title, (90, content_y))
            content_y += 30

            for req in listing['requirements']:
                req_surf = self.fonts['small'].render(f"• {req}", True, self.colors['requirement'])
                screen.blit(req_surf, (110, content_y))
                content_y += 25

            content_y += 20
            problem_rect = pygame.Rect(90, content_y, SCREEN_WIDTH - 180, 60)
            pygame.draw.rect(screen, self.colors['problem_bg'], problem_rect)
            pygame.draw.rect(screen, self.colors['requirement'], problem_rect, 1)

            problem_text = f"⚠️ Reality: {listing['problem']}"
            problem_surf = self.fonts['problem'].render(problem_text, True, self.colors['problem_text'])
            screen.blit(problem_surf, (100, content_y + 20))

            content_y += 80
            posted_surf = self.fonts['small'].render(listing['posted'], True, self.colors['gray'])
            screen.blit(posted_surf, (90, content_y))

        progress_text = f"Listing {self.current_listing + 1} of {len(self.listings)}"
        progress_surf = self.fonts['small'].render(progress_text, True, self.colors['gray'])
        screen.blit(progress_surf, (70, SCREEN_HEIGHT - 40))

        if self.current_listing < len(self.listings) - 1:
            button_color = self.colors['button_hover'] if self.hovering_next else self.colors['button']
            next_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 150, 40)
            pygame.draw.rect(screen, button_color, next_rect, border_radius=5)

            next_text = "Next Listing →"
            next_surf = self.fonts['body'].render(next_text, True, (255, 255, 255))
            next_rect_center = next_surf.get_rect(center=next_rect.center)
            screen.blit(next_surf, next_rect_center)
        else:
            instruction = "Press SPACE to face reality"
            inst_surf = self.fonts['body'].render(instruction, True, self.colors['final_text'])
            screen.blit(inst_surf, (SCREEN_WIDTH//2 - inst_surf.get_width()//2, SCREEN_HEIGHT - 80))

    def draw_final_message(self, screen):
        """Draw the final reality check message"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(self.colors['background'])
        screen.blit(overlay, (0, 0))

        messages = [
            "There is no roommate solution.",
            "Your studio is too small to legally share.",
            "Your lease forbids subletting.",
            "You're trapped with a 15% rent increase.",
            "",
            "You need a different solution..."
        ]

        y = SCREEN_HEIGHT // 2 - len(messages) * 20

        for i, msg in enumerate(messages):
            if msg:
                color = self.colors['final_text'] if i < 4 else self.colors['success']
                font = self.fonts['final'] if i == 0 else self.fonts['listing_title']
                text_surf = font.render(msg, True, color)
                x = SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                screen.blit(text_surf, (x, y))
            y += 40

        continue_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(screen, self.colors['button'], continue_rect, border_radius=5)

        continue_text = "Continue"
        continue_surf = self.fonts['body'].render(continue_text, True, (255, 255, 255))
        continue_rect_center = continue_surf.get_rect(center=continue_rect.center)
        screen.blit(continue_surf, continue_rect_center)