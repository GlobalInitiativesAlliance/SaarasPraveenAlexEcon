"""
Facebook Housing Search Mini-Game
Shows the desperation and risks of informal housing searches
"""
import pygame
import math
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class FacebookSearch(Activity):
    """Facebook-style interface for searching housing groups"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None  # Set by parent interior

        # Search state
        self.current_post = 0
        self.posts_viewed = set()
        self.alex_post_unlocked = False
        self.alex_contacted = False
        self.scroll_offset = 0
        self.target_scroll = 0
        self.scroll_velocity = 0

        # UI state
        self.hovering_button = None
        self.animation_timer = 0
        self.notification_timer = 0
        self.notification_message = ""

        # Create posts
        self.create_posts()

        # UI elements
        self.post_rects = []
        self.message_button_rect = None
        self.continue_button_rect = None

        # Modern Facebook-inspired colors
        self.primary_blue = (24, 119, 242)      # Modern FB blue #1877F2
        self.dark_blue = (10, 102, 194)         # Darker accent #0A66C2
        self.bg_gray = (240, 242, 245)          # Soft background #F0F2F5
        self.card_white = (255, 255, 255)       # Card background
        self.success_green = (49, 162, 76)      # Alex's post #31A24C
        self.text_dark = (5, 5, 5)              # Primary text #050505
        self.text_medium = (101, 103, 107)      # Secondary text #65676B
        self.text_light = (144, 148, 156)       # Tertiary text #90949C
        self.border_light = (228, 230, 235)     # Subtle borders #E4E6EB
        self.hover_bg = (242, 242, 242)         # Hover background #F2F2F2
        self.red_flag = (231, 76, 60)           # Warning red #E74C3C

        # Legacy references (for backwards compatibility during transition)
        self.white = self.card_white
        self.fb_gray = self.bg_gray
        self.fb_dark_gray = self.text_medium
        self.fb_blue = self.primary_blue

        # Load textures
        self.load_textures()

    def create_posts(self):
        """Create all Facebook posts with housing listings"""
        self.posts = [
            {
                "id": 1,
                "author": "Mike Thompson",
                "group": "City Housing Network",
                "time": "3 hours ago",
                "content": "ROOM AVAILABLE - $400/month\nMales only, shared bathroom with 3 others.\nCASH ONLY - No questions asked!\nMust be comfortable with 'flexible' living arrangements.\nImmediate move-in required.",
                "likes": 2,
                "comments": [
                    "Is this still available?",
                    "Messaged you!",
                    "Interested, please DM"
                ],
                "red_flags": ["Cash only", "No questions", "Immediate move-in"],
                "reality_check": "Overcrowded, possibly illegal, no tenant rights"
            },
            {
                "id": 2,
                "author": "Jennifer Sweet",
                "group": "Rooms for Rent - No Scams!",
                "time": "5 hours ago",
                "content": "🌟 LUXURY CONDO SHARE - Only $300/month! 🌟\nFemale roommate wanted (18-25 preferred)\nBeautiful downtown location!\nMust be comfortable with security cameras\nInterview required - send photos!",
                "likes": 45,
                "comments": [
                    "This seems too good to be true...",
                    "Why so many cameras?",
                    "DMed you my photos!"
                ],
                "red_flags": ["Too cheap for luxury", "Age/gender specific", "Photo requirement"],
                "reality_check": "This is 100% a scam or something worse"
            },
            {
                "id": 3,
                "author": "Property Manager",
                "group": "Emergency Housing Help",
                "time": "1 day ago",
                "content": "Converted closet space - $900/month\nIt's small but it's shelter!\n- 4x6 feet 'bedroom'\n- Shared kitchen (limited hours)\n- No guests allowed\n- First + Last + Security = $2700",
                "likes": 0,
                "comments": [
                    "How is a closet $900?!",
                    "I'll take it if available",
                    "Desperate, please respond"
                ],
                "red_flags": ["Not legally a bedroom", "Exploitative pricing"],
                "reality_check": "Literally a closet for almost $1000"
            },
            {
                "id": 4,
                "author": "Brad K.",
                "group": "Student Subletting",
                "time": "6 hours ago",
                "content": "Room near campus - $650/month\nMust show valid student ID\nNo overnight guests\n$50 background check fee (non-refundable)\n3 other roommates already here",
                "likes": 12,
                "comments": [
                    "Still a student?",
                    "Can recent grads apply?",
                    "Background check seems sketchy"
                ],
                "red_flags": ["Student only", "Upfront fees", "Guest restrictions"],
                "reality_check": "You're not a student anymore"
            },
            {
                "id": 5,
                "author": "Dave Landlord",
                "group": "City Housing Network",
                "time": "2 days ago",
                "content": "Efficiency apartment - 45min from downtown\n$950/month + utilities\nMust have car (no public transit)\nNo pets, no smoking, no visitors after 9pm\n6 month minimum lease\nIncome requirement: 3x rent",
                "likes": 3,
                "comments": [
                    "Any flexibility on income requirement?",
                    "How do I get there without a car?",
                    "These requirements are insane"
                ],
                "red_flags": ["No transit access", "Strict income requirement"],
                "reality_check": "No car, no income, no chance"
            },
            {
                "id": 6,
                "author": "Sandra M.",
                "group": "Rooms for Rent - No Scams!",
                "time": "12 hours ago",
                "content": "Room in family home - $600/month\nFEMALES ONLY - Must be quiet & clean\nNo kitchen privileges after 7pm\nNo guests EVER\nMust attend weekly 'family meetings'\nCash upfront: First + Last = $1200",
                "likes": 1,
                "comments": [
                    "Why no kitchen access?",
                    "Sounds controlling...",
                    "What are these meetings about?"
                ],
                "red_flags": ["Excessive restrictions", "Controlling environment"],
                "reality_check": "Too restrictive and still need $1200 upfront"
            }
        ]

        # Alex's post (shows after viewing 6+ others)
        self.alex_post = {
            "id": 7,
            "author": "Alex Chen",
            "group": "City Housing Network",
            "time": "2 hours ago",
            "content": "Spare room in my 2BR apartment - $600/month\nPretty chill situation, just need help with rent\nDowntown area, close to everything\nNo lease needed - month to month is fine\nMove in whenever!",
            "likes": 8,
            "red_flags": ["No lease", "Informal arrangement"],
            "reality_check": "No lease means no tenant rights, but it's your only option"
        }

        # More posts that appear after Alex
        self.additional_posts = [
            {
                "id": 8,
                "author": "Management Company",
                "group": "Emergency Housing Help",
                "time": "4 hours ago",
                "content": "Studio Apartment - $1400/month\nCredit check required (750+)\nIncome verification (pay stubs)\nFirst + Last + Security\nNo co-signers accepted\nProfessional references only",
                "likes": 0,
                "comments": [
                    "These requirements are impossible",
                    "Who has 750 credit at 18?",
                    "This is why people are homeless"
                ],
                "red_flags": ["Impossible requirements for young adults"],
                "reality_check": "The 'legitimate' option you can never qualify for"
            },
            {
                "id": 9,
                "author": "Tom Wilson",
                "group": "Rooms for Rent - No Scams!",
                "time": "1 hour ago",
                "content": "Couch for rent - $500/month\nYes, just a couch in living room\nNo privacy, no storage\nMust be out 7am-7pm (I work from home)\nWeekly payment required\nNo mail/packages allowed",
                "likes": 0,
                "comments": [
                    "A COUCH for $500?!",
                    "This is insulting",
                    "People are really this desperate..."
                ],
                "red_flags": ["Not even a room", "Daily displacement"],
                "reality_check": "The housing crisis has reached this point"
            }
        ]

    def load_textures(self):
        """Create UI textures and elements"""
        # Create font objects
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)

        # Create notification surface
        self.notification_surf = pygame.Surface((350, 60), pygame.SRCALPHA)

    def start(self):
        """Start the Facebook search activity"""
        super().start()
        self.current_post = 0
        self.posts_viewed.clear()
        self.scroll_offset = 0
        self.target_scroll = 0
        self.animation_timer = 0

    def draw(self, screen):
        """Main draw function"""
        if not self.active:
            return

        # Update animation timer
        self.animation_timer += 0.016

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Main Facebook container
        main_rect = pygame.Rect(50, 30, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 60)
        pygame.draw.rect(screen, self.fb_gray, main_rect)
        pygame.draw.rect(screen, (200, 200, 200), main_rect, 2)

        # Draw Facebook header
        self.draw_header(screen)

        # Draw sidebar
        self.draw_sidebar(screen)

        # Draw main feed
        self.draw_feed(screen)

        # Draw notifications
        self.draw_notifications(screen)

        # Draw continue button if Alex contacted
        if self.alex_contacted:
            self.draw_continue_button(screen)

        # Draw exit hint
        exit_text = "Press ESC to exit" if self.alex_contacted else "Use ↑↓ arrows to scroll • Press ESC to exit"
        exit_surf = self.font_tiny.render(exit_text, True, (120, 120, 120))
        screen.blit(exit_surf, (60, SCREEN_HEIGHT - 25))

    def draw_header(self, screen):
        """Draw header with modern gradient design"""
        # Gradient background from primary to dark blue
        for i in range(60):
            blend = i / 60
            color = (
                int(self.primary_blue[0] + (self.dark_blue[0] - self.primary_blue[0]) * blend),
                int(self.primary_blue[1] + (self.dark_blue[1] - self.primary_blue[1]) * blend),
                int(self.primary_blue[2] + (self.dark_blue[2] - self.primary_blue[2]) * blend)
            )
            pygame.draw.line(screen, color, (0, i), (SCREEN_WIDTH, i))

        # Subtle bottom shadow
        shadow = pygame.Surface((SCREEN_WIDTH, 3), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 30))
        screen.blit(shadow, (0, 60))

        # Logo
        logo_surf = self.font_large.render("facebook", True, self.card_white)
        screen.blit(logo_surf, (20, 18))

        # Rounded search bar
        search_rect = pygame.Rect(250, 15, 400, 35)
        pygame.draw.rect(screen, self.bg_gray, search_rect, border_radius=20)

        # Search text
        search_text = "🔍 Search housing groups..."
        search_surf = self.font_small.render(search_text, True, self.text_light)
        screen.blit(search_surf, (265, 22))

        # Profile area
        profile_surf = self.font_small.render("You", True, self.card_white)
        screen.blit(profile_surf, (SCREEN_WIDTH - 80, 22))

    def draw_sidebar(self, screen):
        """Draw sidebar with modern card design"""
        sidebar_x = 50
        sidebar_y = 80

        # Groups section - rounded card with shadow
        groups_card = pygame.Rect(sidebar_x, sidebar_y, 240, 300)

        # Draw card shadow
        shadow_surf = pygame.Surface((240, 300), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 15), (0, 2, 240, 300), border_radius=8)
        screen.blit(shadow_surf, (sidebar_x, sidebar_y))

        # Draw card
        pygame.draw.rect(screen, self.card_white, groups_card, border_radius=8)

        # Groups header with better typography
        groups_text = "Your Groups"
        groups_surf = self.font_medium.render(groups_text, True, self.text_dark)
        screen.blit(groups_surf, (sidebar_x + 16, sidebar_y + 16))

        # Group list with hover states
        groups = [
            ("City Housing Network", "2.3k members", True),
            ("Affordable Rooms", "892 members", True),
            ("Student Housing", "1.5k members", False),
        ]

        y_pos = sidebar_y + 55
        for group_name, members, has_notification in groups:
            # Hover background (simulate with slight color)
            if has_notification:
                item_rect = pygame.Rect(sidebar_x + 8, y_pos - 5, 224, 40)
                pygame.draw.rect(screen, self.hover_bg, item_rect, border_radius=4)

            # Group name
            color = self.text_dark if has_notification else self.text_medium
            name_surf = self.font_small.render(group_name, True, color)
            screen.blit(name_surf, (sidebar_x + 16, y_pos))

            # Member count
            member_surf = self.font_tiny.render(members, True, self.text_light)
            screen.blit(member_surf, (sidebar_x + 16, y_pos + 18))

            # Notification dot
            if has_notification:
                pygame.draw.circle(screen, self.success_green,
                                 (sidebar_x + 220, y_pos + 8), 5)

            y_pos += 50

    def draw_feed(self, screen):
        """Draw main feed with posts"""
        feed_rect = pygame.Rect(260, 80, SCREEN_WIDTH - 360, SCREEN_HEIGHT - 110)
        pygame.draw.rect(screen, self.bg_gray, feed_rect)

        # Create post area with scrolling
        post_area = pygame.Surface((feed_rect.width - 20, 2000), pygame.SRCALPHA)
        post_area.fill(self.bg_gray)

        # Determine which posts to show - Alex's post is always first now
        all_posts = [self.alex_post] + list(self.posts) + self.additional_posts
        self.alex_post_unlocked = True

        # Draw each post
        y_offset = 10
        self.post_rects = []

        for post in all_posts:
            post_rect = self.draw_post(post_area, post, y_offset)
            self.post_rects.append((post, post_rect))
            y_offset += post_rect.height + 15

            # Track viewed posts
            if post['id'] not in self.posts_viewed:
                # Check if post is visible
                if -self.scroll_offset <= y_offset <= -self.scroll_offset + feed_rect.height:
                    self.posts_viewed.add(post['id'])

        # Apply scrolling
        screen.blit(post_area, (270, 90), (0, self.scroll_offset, feed_rect.width - 20, feed_rect.height - 20))

        # Scrollbar with better styling
        if y_offset > feed_rect.height:
            scrollbar_height = max(30, (feed_rect.height / y_offset) * feed_rect.height)
            scrollbar_pos = (self.scroll_offset / (y_offset - feed_rect.height)) * (feed_rect.height - scrollbar_height)
            scrollbar_rect = pygame.Rect(SCREEN_WIDTH - 105, 90 + scrollbar_pos, 6, scrollbar_height)
            pygame.draw.rect(screen, (150, 150, 150), scrollbar_rect, border_radius=3)

    def draw_post(self, surface, post, y_offset):
        """Draw post with modern card design"""
        post_height = 270 if post['id'] == 7 else 240
        post_rect = pygame.Rect(10, y_offset, surface.get_width() - 20, post_height)

        # ALL posts get modern shadow (not just Alex's)
        shadow_surf = pygame.Surface((post_rect.width, post_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 2, post_rect.width, post_rect.height),
                        border_radius=12)
        surface.blit(shadow_surf, (post_rect.x, post_rect.y))

        # Enhanced glow for Alex's post
        if post['id'] == 7:
            glow_surf = pygame.Surface((post_rect.width + 8, post_rect.height + 8), pygame.SRCALPHA)
            for i in range(4):
                alpha = 40 - (i * 10)
                pygame.draw.rect(glow_surf, (*self.success_green, alpha),
                               (i, i, post_rect.width + 8 - i*2, post_rect.height + 8 - i*2),
                               border_radius=12)
            surface.blit(glow_surf, (post_rect.x - 4, post_rect.y - 4))

            # Accent border
            pygame.draw.rect(surface, self.success_green, post_rect, 3, border_radius=12)

        # Card background (white)
        pygame.draw.rect(surface, self.card_white, post_rect, border_radius=12)

        # Subtle border for non-Alex posts
        if post['id'] != 7:
            pygame.draw.rect(surface, self.border_light, post_rect, 1, border_radius=12)

        # Author section with better spacing
        author_color = self.success_green if post['id'] == 7 else self.text_dark

        # Author name (larger, bolder visual weight)
        author_surf = self.font_medium.render(post['author'], True, author_color)
        surface.blit(author_surf, (25, y_offset + 20))

        # Metadata (group + time) - lighter color
        meta_text = f"{post['group']} · {post['time']}"
        meta_surf = self.font_tiny.render(meta_text, True, self.text_light)
        surface.blit(meta_surf, (25, y_offset + 45))

        # Separator line (subtle)
        pygame.draw.line(surface, self.border_light,
                        (25, y_offset + 70), (post_rect.width - 15, y_offset + 70), 1)

        # Post content with better spacing
        lines = post['content'].split('\n')
        line_y = y_offset + 85
        for line in lines:
            color = self.text_dark
            for flag in post.get('red_flags', []):
                if flag.lower() in line.lower():
                    color = self.red_flag

            line_surf = self.font_small.render(line, True, color)
            surface.blit(line_surf, (25, line_y))
            line_y += 28  # Increased spacing

        # DYNAMIC POSITIONING - calculate based on where content actually ends
        content_end_y = line_y  # Track where content ended

        # Calculate minimum height needed for all elements
        # Social section needs: separator line + social text (30px) + comment (25px) + button (45px) = 100px
        min_bottom_space = 100

        # Position social section with proper spacing after content
        social_y = max(content_end_y + 15, y_offset + post_height - min_bottom_space)

        # Draw social separator line
        pygame.draw.line(surface, self.border_light,
                        (25, social_y), (post_rect.width - 15, social_y), 1)

        # Social text (likes/comments)
        social_text = f"👍 {post.get('likes', 0)}    💬 {len(post.get('comments', []))} comments"
        social_surf = self.font_tiny.render(social_text, True, self.text_medium)
        surface.blit(social_surf, (25, social_y + 12))

        # Comments positioned AFTER social text with proper gap
        if post.get('comments'):
            comment_y = social_y + 30  # 30px below social separator
            comment = post['comments'][0]
            comment_surf = self.font_tiny.render(f"💬 {comment[:45]}...", True, self.text_light)
            surface.blit(comment_surf, (35, comment_y))

        # Message button for Alex's post positioned AFTER comment
        if post['id'] == 7:
            button_y = social_y + 60  # Position after social text and comment
            button_rect = pygame.Rect(25, button_y, 120, 36)

            # Button with pulse animation
            if not self.alex_contacted:
                pulse = math.sin(self.animation_timer * 2) * 2 + 2
                button_rect = pygame.Rect(25 - pulse//2, button_y - pulse//2,
                                        120 + pulse, 36 + pulse)

            # Button background
            button_color = self.success_green if not self.alex_contacted else self.text_light
            pygame.draw.rect(surface, button_color, button_rect, border_radius=8)

            # Button shadow
            if not self.alex_contacted:
                shadow = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 40),
                               (0, 2, button_rect.width, button_rect.height), border_radius=8)
                surface.blit(shadow, (button_rect.x, button_rect.y))

            # Button text
            button_text = "💬 Message" if not self.alex_contacted else "✓ Sent"
            button_surf = self.font_small.render(button_text, True, self.card_white)
            text_x = button_rect.centerx - button_surf.get_width() // 2
            text_y = button_rect.centery - button_surf.get_height() // 2
            surface.blit(button_surf, (text_x, text_y))

            self.message_button_rect = pygame.Rect(270 + button_rect.x, 90 + button_rect.y,
                                                   button_rect.width, button_rect.height)

        # Adjust post_height dynamically to fit all content
        actual_height = max(button_y + 50 if post['id'] == 7 else social_y + 70, post_height)
        post_rect.height = actual_height

        return post_rect

    def draw_notifications(self, screen):
        """Draw notification popups"""
        if self.notification_timer > 0:
            self.notification_timer -= 0.016

            # Notification popup
            notif_rect = pygame.Rect(SCREEN_WIDTH - 400, 100, 350, 60)
            pygame.draw.rect(screen, self.white, notif_rect, border_radius=5)
            pygame.draw.rect(screen, self.fb_blue, notif_rect, 2, border_radius=5)

            # Notification text
            notif_surf = self.font_small.render(self.notification_message, True, self.fb_dark_gray)
            screen.blit(notif_surf, (SCREEN_WIDTH - 390, 120))

            # Fade out
            if self.notification_timer < 0.5:
                fade_surf = pygame.Surface((350, 60), pygame.SRCALPHA)
                alpha = max(0, min(255, int(255 * (1 - self.notification_timer * 2))))
                fade_surf.fill((255, 255, 255, alpha))
                screen.blit(fade_surf, (SCREEN_WIDTH - 400, 100))

    def draw_continue_button(self, screen):
        """Draw continue button after contacting Alex"""
        self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 100, 300, 50)

        # Pulse animation
        pulse = math.sin(self.animation_timer * 3) * 5 + 5
        button_rect = pygame.Rect(self.continue_button_rect.x - pulse//2,
                                 self.continue_button_rect.y - pulse//2,
                                 self.continue_button_rect.width + pulse,
                                 self.continue_button_rect.height + pulse)

        pygame.draw.rect(screen, (42, 183, 72), button_rect, border_radius=5)
        pygame.draw.rect(screen, self.white, button_rect, 3, border_radius=5)

        button_text = "Click to Go Meet Alex"
        button_surf = self.font_large.render(button_text, True, self.white)
        text_x = button_rect.centerx - button_surf.get_width() // 2
        text_y = button_rect.centery - button_surf.get_height() // 2
        screen.blit(button_surf, (text_x, text_y))

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks and mouse wheel"""
        if not self.active:
            return

        # Handle mouse wheel scrolling
        if button == 4:  # Mouse wheel up
            self.target_scroll -= 50
            self.target_scroll = max(0, self.target_scroll)
        elif button == 5:  # Mouse wheel down
            self.target_scroll += 50
        elif button == 1:  # Left click
            # Check message button for Alex's post
            if self.message_button_rect and self.message_button_rect.collidepoint(pos):
                if not self.alex_contacted:
                    self.alex_contacted = True
                    self.notification_message = "Message sent to Alex Chen!"
                    self.notification_timer = 3.0

                    # Show Alex's reply after delay
                    pygame.time.set_timer(pygame.USEREVENT + 1, 2000)

            # Check continue button
            if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
                self.complete_search()

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        # Check if hovering over buttons
        if self.message_button_rect and self.message_button_rect.collidepoint(pos):
            self.hovering_button = "message"
        elif self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.hovering_button = "continue"
        else:
            self.hovering_button = None

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        # Scroll with arrow keys
        if key == pygame.K_DOWN:
            self.target_scroll += 100
        elif key == pygame.K_UP:
            self.target_scroll -= 100
            self.target_scroll = max(0, self.target_scroll)
        elif key == pygame.K_ESCAPE:
            if self.alex_contacted:
                self.complete_search()

    def update(self, dt):
        """Update animations and scrolling"""
        if not self.active:
            return

        self.animation_timer += dt

        # Smooth scrolling
        if abs(self.scroll_offset - self.target_scroll) > 1:
            self.scroll_offset += (self.target_scroll - self.scroll_offset) * 0.15
        else:
            self.scroll_offset = self.target_scroll

        # Handle Alex reply notification
        for event in pygame.event.get(pygame.USEREVENT + 1):
            self.notification_message = "Alex Chen: 'Hey! Yeah it's available! Come check it out?'"
            self.notification_timer = 4.0
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel timer

    def complete_search(self):
        """Complete the Facebook search"""
        # Update parent interior state
        if self.narrative_ref:
            self.narrative_ref.search_complete = True
            self.narrative_ref.alex_found = True

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            # Show completion message
            if hasattr(self.narrative_ref, 'dialogue_box'):
                msg = "You've found Alex's listing. No lease, no security... but it's something. "
                msg += "Time to meet them and see the apartment."
                self.narrative_ref.dialogue_box.show(None, msg)

        # Mark activity complete
        self.complete()