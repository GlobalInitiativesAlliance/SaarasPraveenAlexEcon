"""
Apartment Search Mini-Game
Following pattern from shelter_checkin and document_search
"""
import pygame
import math
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class ApartmentSearch(Activity):
    """Computer-based apartment search showing harsh reality of housing crisis"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None  # Set by parent interior

        # Search state
        self.current_listing = 0
        self.listings_viewed = 0
        self.reality_revealed = False

        # Apartment listings (all impossible for someone with $73)
        self.listings = [
            {
                "title": "Studio Apartment - Downtown",
                "price": "$1,400/month",
                "requirements": [
                    "Income: $4,200/month minimum",
                    "Credit score: 650+",
                    "First + Last + Deposit: $4,200",
                    "Co-signer required if under 21"
                ],
                "available": "Available Now",
                "reality": "You have: $0 income, no credit, $73 total"
            },
            {
                "title": "1BR Apartment - Eastside",
                "price": "$1,800/month",
                "requirements": [
                    "Income: $5,400/month minimum",
                    "Credit score: 700+",
                    "First + Last + Deposit: $5,400",
                    "References: 3 previous landlords"
                ],
                "available": "Available Next Month",
                "reality": "You've never rented before. No references."
            },
            {
                "title": "Shared Room - Near Campus",
                "price": "$800/month",
                "requirements": [
                    "Income: $2,400/month minimum",
                    "Student ID required",
                    "Deposit: $1,600",
                    "Background check: $50"
                ],
                "available": "3 people interested",
                "reality": "Not a student. Can't afford the background check."
            },
            {
                "title": "Studio - Bad Neighborhood",
                "price": "$1,200/month",
                "requirements": [
                    "Income: $3,600/month",
                    "Cash only - no credit check",
                    "First + Deposit: $2,400 cash",
                    "No questions asked"
                ],
                "available": "Immediate",
                "reality": "Sketchy. Probably unsafe. Still need $2,400."
            },
            {
                "title": "Efficiency - 45min from city",
                "price": "$950/month",
                "requirements": [
                    "Income: $2,850/month",
                    "Car required (no bus route)",
                    "First + Last: $1,900",
                    "Pet deposit: $500 (no pets allowed)"
                ],
                "available": "Next Week",
                "reality": "No car. No way to get to work from there."
            },
            {
                "title": "Room for Rent - Private Home",
                "price": "$600/month",
                "requirements": [
                    "Female only",
                    "No overnight guests",
                    "No kitchen privileges",
                    "Cash upfront: $1,200"
                ],
                "available": "Immediately",
                "reality": "Too restrictive. Still need $1,200."
            }
        ]

        # UI elements
        self.animation_timer = 0
        self.continue_button_rect = None
        self.next_button_rect = None
        self.prev_button_rect = None
        self.reality_button_rect = None

        # Load textures
        self.load_textures()

    def load_textures(self):
        """Create simple UI elements"""
        # Browser window texture
        self.browser_bg = pygame.Surface((SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200))
        self.browser_bg.fill((245, 245, 245))

        # Create cursor animation frames
        self.cursor_frames = []
        for i in range(2):
            cursor = pygame.Surface((20, 20), pygame.SRCALPHA)
            if i == 0:
                pygame.draw.lines(cursor, (0, 0, 0), False,
                                [(0, 0), (0, 15), (10, 10)], 2)
            else:
                pygame.draw.lines(cursor, (100, 100, 100), False,
                                [(0, 0), (0, 15), (10, 10)], 2)
            self.cursor_frames.append(cursor)

    def start(self):
        """Start the apartment search activity"""
        super().start()
        self.current_listing = 0
        self.listings_viewed = 0
        self.animation_timer = 0

    def draw(self, screen):
        """Main draw function"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Update animation
        self.animation_timer += 0.016

        # Main browser window
        browser_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
        pygame.draw.rect(screen, (255, 255, 255), browser_rect)
        pygame.draw.rect(screen, (100, 100, 100), browser_rect, 3)

        # Browser header
        header_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, 40)
        pygame.draw.rect(screen, (230, 230, 230), header_rect)
        pygame.draw.rect(screen, (100, 100, 100), header_rect, 2)

        # URL bar
        url_font = pygame.font.Font(None, 20)
        url_text = "craigslist.com/housing/apartments"
        url_surf = url_font.render(url_text, True, (50, 50, 50))
        screen.blit(url_surf, (120, 115))

        # Draw current listing
        self.draw_listing(screen)

        # Navigation buttons
        self.draw_navigation(screen)

        # Draw cursor
        cursor_frame = int(self.animation_timer * 2) % 2
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(self.cursor_frames[cursor_frame], (mouse_x, mouse_y))

    def draw_listing(self, screen):
        """Draw current apartment listing"""
        if self.current_listing >= len(self.listings):
            return

        listing = self.listings[self.current_listing]

        # Title
        title_font = pygame.font.Font(None, 36)
        title_surf = title_font.render(listing["title"], True, (0, 0, 0))
        screen.blit(title_surf, (120, 160))

        # Price (big and bold)
        price_font = pygame.font.Font(None, 48)
        price_surf = price_font.render(listing["price"], True, (200, 50, 50))
        screen.blit(price_surf, (120, 200))

        # Availability
        avail_font = pygame.font.Font(None, 24)
        avail_surf = avail_font.render(listing["available"], True, (50, 150, 50))
        screen.blit(avail_surf, (120, 255))

        # Requirements header
        req_header_font = pygame.font.Font(None, 28)
        req_header = req_header_font.render("Requirements:", True, (0, 0, 0))
        screen.blit(req_header, (120, 300))

        # Requirements list
        req_font = pygame.font.Font(None, 24)
        y_offset = 335
        for req in listing["requirements"]:
            # Bullet point
            pygame.draw.circle(screen, (100, 100, 100), (130, y_offset + 8), 3)
            # Requirement text
            req_surf = req_font.render(req, True, (50, 50, 50))
            screen.blit(req_surf, (145, y_offset))
            y_offset += 30

        # Reality check button
        self.reality_button_rect = pygame.Rect(120, y_offset + 20, 200, 40)
        button_color = (255, 100, 100) if self.reality_revealed else (100, 150, 255)
        pygame.draw.rect(screen, button_color, self.reality_button_rect)
        pygame.draw.rect(screen, (50, 50, 50), self.reality_button_rect, 2)

        button_font = pygame.font.Font(None, 24)
        button_text = "Can I afford this?"
        button_surf = button_font.render(button_text, True, (255, 255, 255))
        button_x = self.reality_button_rect.centerx - button_surf.get_width() // 2
        button_y = self.reality_button_rect.centery - button_surf.get_height() // 2
        screen.blit(button_surf, (button_x, button_y))

        # Show reality if button was clicked
        if self.reality_revealed:
            reality_bg = pygame.Rect(350, y_offset + 15, 450, 50)
            pygame.draw.rect(screen, (255, 240, 240), reality_bg)
            pygame.draw.rect(screen, (255, 100, 100), reality_bg, 2)

            reality_font = pygame.font.Font(None, 22)
            reality_surf = reality_font.render(listing["reality"], True, (200, 0, 0))
            screen.blit(reality_surf, (360, y_offset + 30))

    def draw_navigation(self, screen):
        """Draw navigation buttons"""
        nav_y = SCREEN_HEIGHT - 180

        # Previous button
        if self.current_listing > 0:
            self.prev_button_rect = pygame.Rect(120, nav_y, 100, 40)
            pygame.draw.rect(screen, (150, 150, 150), self.prev_button_rect)
            pygame.draw.rect(screen, (50, 50, 50), self.prev_button_rect, 2)

            nav_font = pygame.font.Font(None, 24)
            prev_text = "< Previous"
            prev_surf = nav_font.render(prev_text, True, (255, 255, 255))
            prev_x = self.prev_button_rect.centerx - prev_surf.get_width() // 2
            prev_y = self.prev_button_rect.centery - prev_surf.get_height() // 2
            screen.blit(prev_surf, (prev_x, prev_y))
        else:
            self.prev_button_rect = None

        # Next button
        if self.current_listing < len(self.listings) - 1:
            self.next_button_rect = pygame.Rect(240, nav_y, 100, 40)
            pygame.draw.rect(screen, (150, 150, 150), self.next_button_rect)
            pygame.draw.rect(screen, (50, 50, 50), self.next_button_rect, 2)

            nav_font = pygame.font.Font(None, 24)
            next_text = "Next >"
            next_surf = nav_font.render(next_text, True, (255, 255, 255))
            next_x = self.next_button_rect.centerx - next_surf.get_width() // 2
            next_y = self.next_button_rect.centery - next_surf.get_height() // 2
            screen.blit(next_surf, (next_x, next_y))
        else:
            self.next_button_rect = None

        # Continue button (after viewing enough listings)
        if self.listings_viewed >= 3:
            self.continue_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 150, nav_y, 300, 50
            )
            pygame.draw.rect(screen, (100, 150, 100), self.continue_button_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.continue_button_rect, 3)

            continue_font = pygame.font.Font(None, 28)
            continue_text = "Give Up and Leave"
            continue_surf = continue_font.render(continue_text, True, (255, 255, 255))
            cont_x = self.continue_button_rect.centerx - continue_surf.get_width() // 2
            cont_y = self.continue_button_rect.centery - continue_surf.get_height() // 2
            screen.blit(continue_surf, (cont_x, cont_y))

        # Status text
        status_font = pygame.font.Font(None, 20)
        status_text = f"Listing {self.current_listing + 1} of {len(self.listings)}"
        status_surf = status_font.render(status_text, True, (100, 100, 100))
        screen.blit(status_surf, (SCREEN_WIDTH // 2 - status_surf.get_width() // 2, nav_y - 30))

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        # Reality check button
        if self.reality_button_rect and self.reality_button_rect.collidepoint(pos):
            self.reality_revealed = True
            return

        # Navigation buttons
        if self.prev_button_rect and self.prev_button_rect.collidepoint(pos):
            self.current_listing = max(0, self.current_listing - 1)
            self.reality_revealed = False
            return

        if self.next_button_rect and self.next_button_rect.collidepoint(pos):
            self.current_listing = min(len(self.listings) - 1, self.current_listing + 1)
            self.listings_viewed = max(self.listings_viewed, self.current_listing + 1)
            self.reality_revealed = False
            return

        # Continue button
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.complete_search()

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        # Could add hover effects here
        pass

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        # ESC to close (but only after viewing some listings)
        if key == pygame.K_ESCAPE:
            if self.listings_viewed >= 3:
                self.complete_search()
            else:
                # Force them to look at the harsh reality
                pass

        # Arrow keys for navigation
        elif key == pygame.K_LEFT and self.current_listing > 0:
            self.current_listing -= 1
            self.reality_revealed = False
        elif key == pygame.K_RIGHT and self.current_listing < len(self.listings) - 1:
            self.current_listing += 1
            self.listings_viewed = max(self.listings_viewed, self.current_listing + 1)
            self.reality_revealed = False

    def complete_search(self):
        """Complete the apartment search"""
        # Update parent interior state
        if self.narrative_ref:
            self.narrative_ref.search_complete = True
            self.narrative_ref.listings_found = len(self.listings)

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            # Show completion message through parent's dialogue box
            if hasattr(self.narrative_ref, 'dialogue_box'):
                msg = f"You've searched {len(self.listings)} listings. "
                msg += "Every single one is impossible with your current situation. "
                msg += "The system isn't built for people like you."
                self.narrative_ref.dialogue_box.show(None, msg)

        # Store the viewed listings count
        self.listings_viewed = len(self.listings)

        # Mark activity complete
        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt