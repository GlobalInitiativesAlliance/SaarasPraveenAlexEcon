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

        # Colors
        self.fb_blue = (66, 103, 178)
        self.fb_light_blue = (139, 157, 195)
        self.fb_gray = (246, 247, 249)
        self.fb_dark_gray = (101, 103, 107)
        self.white = (255, 255, 255)
        self.red_flag = (255, 50, 50)

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
            "comments": [
                "Messaged!",
                "Is this still available?",
                "Finally something reasonable",
                "Interested!",
                "Sent you a message"
            ],
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
        """Draw Facebook-style header"""
        header_rect = pygame.Rect(50, 30, SCREEN_WIDTH - 100, 50)
        pygame.draw.rect(screen, self.fb_blue, header_rect)

        # Facebook "logo"
        logo_text = "facebook"
        logo_surf = self.font_large.render(logo_text, True, self.white)
        screen.blit(logo_surf, (70, 45))

        # Search bar
        search_rect = pygame.Rect(250, 40, 300, 30)
        pygame.draw.rect(screen, self.white, search_rect)
        pygame.draw.rect(screen, self.fb_light_blue, search_rect, 1)

        search_text = "🔍 roommate needed cheap rent"
        search_surf = self.font_small.render(search_text, True, self.fb_dark_gray)
        screen.blit(search_surf, (255, 47))

        # Profile area
        profile_text = "You • Home • Messages (0)"
        profile_surf = self.font_small.render(profile_text, True, self.white)
        screen.blit(profile_surf, (SCREEN_WIDTH - 250, 47))

        # Instructions banner
        if not self.alex_contacted:
            instruction_rect = pygame.Rect(60, 85, SCREEN_WIDTH - 120, 25)
            pygame.draw.rect(screen, (255, 248, 220), instruction_rect)
            pygame.draw.rect(screen, (255, 193, 7), instruction_rect, 1)

            instruction_text = "✉️ Click the 'MESSAGE' button on Alex Chen's glowing green post to contact them!"

            instruction_surf = self.font_small.render(instruction_text, True, (133, 100, 4))
            screen.blit(instruction_surf, (70, 92))

    def draw_sidebar(self, screen):
        """Draw left sidebar with groups"""
        sidebar_rect = pygame.Rect(50, 80, 200, SCREEN_HEIGHT - 110)
        pygame.draw.rect(screen, self.white, sidebar_rect)
        pygame.draw.rect(screen, (230, 230, 230), sidebar_rect, 1)

        # Groups header
        groups_text = "Housing Groups"
        groups_surf = self.font_medium.render(groups_text, True, self.fb_dark_gray)
        screen.blit(groups_surf, (60, 90))

        # Group list
        groups = [
            ("City Housing Network", "2.3k members", True),
            ("Rooms for Rent - No Scams!", "892 members", True),
            ("Emergency Housing Help", "431 members", True),
            ("Student Subletting", "1.2k members", False),
            ("Affordable Housing Action", "3.1k members", False)
        ]

        y_offset = 120
        for group_name, members, joined in groups:
            # Group name
            color = self.fb_blue if joined else self.fb_dark_gray
            name_surf = self.font_small.render(group_name, True, color)
            screen.blit(name_surf, (60, y_offset))

            # Member count
            member_surf = self.font_tiny.render(members, True, (150, 150, 150))
            screen.blit(member_surf, (60, y_offset + 18))

            # Notification dot if joined
            if joined:
                pygame.draw.circle(screen, self.red_flag, (230, y_offset + 10), 4)

            y_offset += 45

        # Sponsored ad (cruel irony)
        ad_rect = pygame.Rect(60, y_offset + 20, 180, 100)
        pygame.draw.rect(screen, (255, 250, 200), ad_rect)
        pygame.draw.rect(screen, (200, 180, 100), ad_rect, 1)

        ad_text = "Luxury Condos"
        ad_surf = self.font_small.render(ad_text, True, (100, 80, 40))
        screen.blit(ad_surf, (65, y_offset + 25))

        ad_subtext = "Starting at $3000/mo"
        ad_sub_surf = self.font_tiny.render(ad_subtext, True, (100, 80, 40))
        screen.blit(ad_sub_surf, (65, y_offset + 45))

        ad_small = "You can't afford this"
        ad_small_surf = self.font_tiny.render(ad_small, True, (150, 130, 80))
        screen.blit(ad_small_surf, (65, y_offset + 65))

    def draw_feed(self, screen):
        """Draw main feed with posts"""
        feed_rect = pygame.Rect(260, 80, SCREEN_WIDTH - 360, SCREEN_HEIGHT - 110)
        pygame.draw.rect(screen, self.fb_gray, feed_rect)

        # Create post area with scrolling
        post_area = pygame.Surface((feed_rect.width - 20, 2000), pygame.SRCALPHA)
        post_area.fill(self.fb_gray)

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

        # Scrollbar
        if y_offset > feed_rect.height:
            scrollbar_height = max(30, (feed_rect.height / y_offset) * feed_rect.height)
            scrollbar_pos = (self.scroll_offset / (y_offset - feed_rect.height)) * (feed_rect.height - scrollbar_height)
            scrollbar_rect = pygame.Rect(SCREEN_WIDTH - 105, 90 + scrollbar_pos, 8, scrollbar_height)
            pygame.draw.rect(screen, (180, 180, 180), scrollbar_rect, border_radius=4)

    def draw_post(self, surface, post, y_offset):
        """Draw a single Facebook post"""
        post_height = 250 if post['id'] == 7 else 220  # Alex's post is taller
        post_rect = pygame.Rect(10, y_offset, surface.get_width() - 20, post_height)

        # Special glowing effect for Alex's post
        if post['id'] == 7:
            # Draw multiple glowing rings
            glow_intensity = math.sin(self.animation_timer * 4) * 0.3 + 0.7
            for i in range(8, 0, -1):
                glow_alpha = int(30 * glow_intensity * (i / 8))
                glow_color = (42, 183, 72, glow_alpha)
                glow_rect = pygame.Rect(post_rect.x - i, post_rect.y - i,
                                      post_rect.width + i*2, post_rect.height + i*2)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, (0, 0, glow_rect.width, glow_rect.height), border_radius=8+i)
                surface.blit(glow_surf, (glow_rect.x, glow_rect.y))

            # Bright border for Alex's post
            pygame.draw.rect(surface, self.white, post_rect, border_radius=8)
            pygame.draw.rect(surface, (42, 183, 72), post_rect, 4, border_radius=8)
        else:
            pygame.draw.rect(surface, self.white, post_rect, border_radius=8)
            pygame.draw.rect(surface, (220, 220, 220), post_rect, 2, border_radius=8)

        # Author and metadata
        author_color = (0, 0, 0)
        if post['id'] == 7:  # Alex's post - make name stand out
            author_color = (42, 183, 72)
            # Add "CLICK HERE!" indicator for Alex
            click_here = "👆 CLICK HERE! 👆"
            click_surf = self.font_small.render(click_here, True, (42, 183, 72))
            surface.blit(click_surf, (post_rect.width - 150, y_offset + 10))

        author_surf = self.font_medium.render(post['author'], True, author_color)
        surface.blit(author_surf, (20, y_offset + 10))

        # Group and time
        meta_text = f"{post['group']} · {post['time']}"
        meta_surf = self.font_tiny.render(meta_text, True, self.fb_dark_gray)
        surface.blit(meta_surf, (20, y_offset + 35))

        # Post content
        lines = post['content'].split('\n')
        line_y = y_offset + 60
        for line in lines:
            # Highlight red flags
            color = (0, 0, 0)
            for flag in post.get('red_flags', []):
                if flag.lower() in line.lower():
                    color = self.red_flag

            line_surf = self.font_small.render(line, True, color)
            surface.blit(line_surf, (20, line_y))
            line_y += 20

        # Likes and comments count
        social_text = f"👍 {post.get('likes', 0)}    💬 {len(post.get('comments', []))} comments"
        social_surf = self.font_tiny.render(social_text, True, self.fb_dark_gray)
        surface.blit(social_surf, (20, y_offset + post_height - 60))

        # Sample comments
        if post.get('comments'):
            comment_y = y_offset + post_height - 40
            for comment in post['comments'][:2]:  # Show first 2 comments
                comment_text = f"· {comment}"
                comment_surf = self.font_tiny.render(comment_text[:50], True, (100, 100, 100))
                surface.blit(comment_surf, (30, comment_y))
                comment_y += 15

        # Message button for Alex's post
        if post['id'] == 7:
            self.message_button_rect = pygame.Rect(270 + 20, 90 + y_offset + post_height - 35, 120, 30)
            button_color = (42, 183, 72) if not self.alex_contacted else (150, 150, 150)

            # Add subtle pulse to message button if not contacted yet
            button_rect = pygame.Rect(20, y_offset + post_height - 35, 120, 30)
            if not self.alex_contacted:
                pulse = math.sin(self.animation_timer * 2) * 2 + 2
                button_rect = pygame.Rect(20 - pulse//2, y_offset + post_height - 35 - pulse//2,
                                        120 + pulse, 30 + pulse)

            pygame.draw.rect(surface, button_color, button_rect, border_radius=5)

            button_text = "📩 CLICK TO MESSAGE!" if not self.alex_contacted else "Messaged ✓"
            button_surf = self.font_small.render(button_text, True, self.white)
            text_x = button_rect.centerx - button_surf.get_width() // 2
            text_y = button_rect.centery - button_surf.get_height() // 2
            surface.blit(button_surf, (text_x, text_y))

            # Add arrow pointing to button if not contacted
            if not self.alex_contacted:
                arrow_text = "↖️ CLICK!"
                arrow_surf = self.font_tiny.render(arrow_text, True, (42, 183, 72))
                surface.blit(arrow_surf, (155, y_offset + post_height - 50))

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
                fade_surf.fill((255, 255, 255, int(255 * (1 - self.notification_timer * 2))))
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

        # Add instruction above button
        instruction_text = "✨ Alex replied! Click the button below to visit their apartment"
        instruction_surf = self.font_medium.render(instruction_text, True, (42, 183, 72))
        inst_x = SCREEN_WIDTH // 2 - instruction_surf.get_width() // 2
        screen.blit(instruction_surf, (inst_x, SCREEN_HEIGHT - 130))

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