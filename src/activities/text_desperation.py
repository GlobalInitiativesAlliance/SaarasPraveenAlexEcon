"""
Text Messaging Desperation - Day 15 of Couch Surfing
Shows the collapse of social safety net when everyone has already helped
"""
import pygame
import random
import time
import math

class TextDesperation:
    """Interactive phone showing failed attempts to find housing"""

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.active = False  # Start inactive until start() is called
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 1024
        self.SCREEN_HEIGHT = 768

        # Phone interface dimensions - iPhone-like proportions
        self.phone_width = 375
        self.phone_height = 667
        self.phone_x = (self.SCREEN_WIDTH - self.phone_width) // 2
        self.phone_y = (self.SCREEN_HEIGHT - self.phone_height) // 2

        # Contacts with relationship degradation
        self.contacts = [
            {
                'name': 'Sarah',
                'avatar_color': (180, 130, 200),
                'messages': [
                    {'sent': True, 'text': 'Hey Sarah, thanks again for letting me stay', 'time': '3 days ago'},
                    {'sent': True, 'text': 'I know I already asked but...', 'time': '3 days ago'},
                    {'sent': True, 'text': 'Is there any chance I could come back?', 'time': '3 days ago'},
                    {'sent': False, 'text': '...', 'typing': True, 'time': '3 days ago'},
                ],
                'status': 'Read 3 days ago',
                'relationship': 40,  # Was 85, now degraded
                'helped_before': True,
                'active': True
            },
            {
                'name': 'Mike',
                'avatar_color': (130, 180, 130),
                'messages': [
                    {'sent': True, 'text': 'Sorry about all the chaos last night', 'time': '1 day ago'},
                    {'sent': True, 'text': 'Any chance I could crash again?', 'time': '1 day ago'},
                    {'sent': False, 'text': "Can't man, landlord is watching", 'time': '1 day ago'},
                    {'sent': False, 'text': 'Good luck though', 'time': '1 day ago'},
                ],
                'status': 'Delivered',
                'relationship': 30,  # Was 70
                'helped_before': True,
                'active': True
            },
            {
                'name': 'Alex',
                'avatar_color': (130, 130, 180),
                'messages': [
                    {'sent': True, 'text': 'Hey Alex, you around?', 'time': '1 week ago'},
                    {'sent': True, 'text': 'Really need to talk', 'time': '1 week ago'},
                    {'sent': True, 'text': 'Please?', 'time': '1 week ago'},
                ],
                'status': 'Delivered',  # Not even read
                'relationship': 0,  # Completely burned bridge
                'helped_before': True,
                'active': False  # Possibly blocked
            },
            {
                'name': 'Jordan (classmate)',
                'avatar_color': (200, 150, 100),
                'messages': [
                    {'sent': True, 'text': 'Hey! Long time no talk!', 'time': '2 days ago'},
                    {'sent': True, 'text': 'How have you been?', 'time': '2 days ago'},
                    {'sent': True, 'text': 'Actually... I need help. Lost my housing', 'time': '2 days ago'},
                    {'sent': False, 'text': 'Oh no! Sorry to hear that', 'time': '2 days ago'},
                    {'sent': False, 'text': 'Wish I could help but my place is tiny', 'time': '2 days ago'},
                    {'sent': False, 'text': 'Good luck!', 'time': '2 days ago'},
                ],
                'status': 'Read',
                'relationship': 10,
                'helped_before': False,
                'active': True
            },
            {
                'name': 'Cousin Pat',
                'avatar_color': (150, 170, 140),
                'messages': [
                    {'sent': True, 'text': 'Hey cuz, family emergency', 'time': '2 weeks ago'},
                    {'sent': True, 'text': 'Need a place to stay for a bit', 'time': '2 weeks ago'},
                    {'sent': True, 'text': 'Hello?', 'time': '1 week ago'},
                ],
                'status': 'Delivered',  # Ignored
                'relationship': 0,
                'helped_before': False,
                'active': False
            }
        ]

        # Currently selected contact
        self.selected_contact = 0
        self.showing_messages = False
        self.contacts_viewed = set()  # Track which contacts have been viewed

        # Phone state
        self.phone_battery = 8  # Very low from losing_stuff
        self.signal_bars = 2
        self.current_time = "9:47 PM"

        # Emotional state
        self.isolation_level = 80
        self.hope_level = 15
        self.days_homeless = 15

        # UI state
        self.scroll_offset = 0
        self.typing_animation = 0
        self.show_network_collapse = False
        self.network_animation_timer = 0

        # Professional iOS-style colors
        self.PHONE_BG = (248, 248, 248)
        self.STATUS_BAR_BG = (247, 247, 247)
        self.MESSAGE_SENT = (0, 122, 255)
        self.MESSAGE_RECEIVED = (229, 229, 234)
        self.TEXT_PRIMARY = (0, 0, 0)
        self.TEXT_SECONDARY = (142, 142, 147)
        self.ONLINE_DOT = (76, 217, 100)
        self.SEPARATOR = (200, 199, 204)
        self.NAV_BG = (249, 249, 249)
        self.BATTERY_RED = (255, 59, 48)
        self.BADGE_RED = (255, 59, 48)

        # Animation states
        self.animation_time = 0
        self.message_send_animation = 0
        self.bubble_scale = {}
        self.typing_dots = 0

        # Screen effects
        self.screen_brightness = 255
        self.signal_flicker = 0

        # Pre-render expensive gradients for performance
        self._prerender_phone_gradients()
        self._prerender_avatar_gradients()

    def _prerender_phone_gradients(self):
        """Pre-render phone gradients once at init to eliminate 889 draw calls per frame"""
        # Phone screen gradient (667 lines → 1 blit)
        self._phone_screen_surf = pygame.Surface(
            (self.phone_width, self.phone_height),
            pygame.SRCALPHA
        )
        for i in range(self.phone_height):
            color_value = int(248 - (i / self.phone_height) * 8)
            pygame.draw.line(
                self._phone_screen_surf,
                (color_value, color_value, color_value + 2),
                (0, i), (self.phone_width, i)
            )

        # Glass reflection gradient (222 lines → 1 blit)
        self._phone_reflection_surf = pygame.Surface(
            (self.phone_width, self.phone_height // 3),
            pygame.SRCALPHA
        )
        for i in range(self.phone_height // 3):
            alpha = int(20 * (1 - i / (self.phone_height // 3)))
            pygame.draw.line(
                self._phone_reflection_surf,
                (255, 255, 255, alpha),
                (0, i), (self.phone_width, i)
            )

    def _prerender_avatar_gradients(self):
        """Pre-render avatar circles for each color to eliminate 120 draw calls per frame"""
        self._avatar_cache = {}

        for contact in self.contacts:
            color_key = tuple(contact['avatar_color'])
            if color_key not in self._avatar_cache:
                surf = pygame.Surface((56, 56), pygame.SRCALPHA)

                # Render gradient circles once (24 circles)
                for r in range(24, 0, -1):
                    color = tuple(
                        min(255, c + (24 - r) * 2)
                        for c in contact['avatar_color']
                    )
                    pygame.draw.circle(surf, color, (28, 28), r)

                self._avatar_cache[color_key] = surf

    def start(self):
        """Start the text messaging activity"""
        self.active = True
        self.completed = False
        self.showing_messages = False
        self.selected_contact = 0
        self.animation_time = 0
        self.network_animation_timer = 0
        self.show_network_collapse = False

    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.showing_messages:
                    self.showing_messages = False
                else:
                    self.complete_activity()

            elif event.key == pygame.K_UP:
                if not self.showing_messages:
                    self.selected_contact = max(0, self.selected_contact - 1)

            elif event.key == pygame.K_DOWN:
                if not self.showing_messages:
                    self.selected_contact = min(len(self.contacts) - 1, self.selected_contact + 1)

            elif event.key == pygame.K_RETURN:
                if not self.showing_messages:
                    self.showing_messages = True
                    self.contacts_viewed.add(self.selected_contact)
                    self.add_desperation_message()
                    # Check for auto-completion after viewing contact
                    if self.check_all_contacts_messaged():
                        self.complete_activity()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check if clicking on a contact
            for i, contact in enumerate(self.contacts):
                contact_y = self.phone_y + 120 + (i * 80)
                contact_rect = pygame.Rect(self.phone_x, contact_y, self.phone_width, 80)
                if contact_rect.collidepoint(mouse_pos):
                    self.selected_contact = i
                    self.showing_messages = True
                    self.contacts_viewed.add(i)
                    self.add_desperation_message()
                    # Check for auto-completion after viewing contact
                    if self.check_all_contacts_messaged():
                        self.complete_activity()

    def handle_mouse_click(self, pos, button):
        """Handle mouse click for compatibility"""
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': button})
        self.handle_event(event)

    def handle_key(self, key):
        """Handle key press"""
        event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
        self.handle_event(event)

    def handle_mouse_motion(self, pos):
        """Handle mouse motion"""
        pass

    def handle_mouse_release(self, pos, button):
        """Handle mouse release"""
        pass

    def add_desperation_message(self):
        """Add a new desperate message to selected contact"""
        contact = self.contacts[self.selected_contact]

        # Only add if they might respond
        if contact['relationship'] > 5 and len(contact['messages']) < 10:
            desperate_messages = [
                "I really need help. Just one night?",
                "I know I keep asking but I'm desperate",
                "Please, I have nowhere else to go",
                "I'll sleep on the floor, I don't mind",
                "Just until I figure something out?",
                "I'm at the shelter but it's full"
            ]

            # Add sent message
            new_message = {
                'sent': True,
                'text': random.choice(desperate_messages),
                'time': 'Now'
            }
            contact['messages'].append(new_message)

            # Degrade relationship
            contact['relationship'] = max(0, contact['relationship'] - 10)

            # Maybe get a response
            if contact['relationship'] > 20 and random.random() < 0.3:
                responses = [
                    "I'm sorry, I really can't",
                    "My roommate said no",
                    "I wish I could help",
                    "Have you tried the shelter?",
                    "..."
                ]
                response = {
                    'sent': False,
                    'text': random.choice(responses),
                    'time': 'Now'
                }
                contact['messages'].append(response)

    def check_all_contacts_messaged(self):
        """Check if user has viewed enough contacts to auto-complete"""
        # Auto-complete after viewing 3+ contacts
        if len(self.contacts_viewed) >= 3:
            return True
        return False

    def complete_activity(self):
        """Complete the activity"""
        if not self.completed:
            self.completed = True
            self.active = False  # Immediate completion - no 3-second wait

    def update(self, dt):
        """Update animation states"""
        if not self.active:
            return

        # General animation time
        self.animation_time += dt

        # Typing animation
        self.typing_animation = (self.typing_animation + dt * 3) % 4
        self.typing_dots = (self.typing_dots + dt * 2) % 3

        # Network collapse animation removed - activity completes immediately now

        # Battery drain
        if random.random() < 0.01:
            self.phone_battery = max(0, self.phone_battery - 1)

        # Signal flicker when low battery
        if self.phone_battery < 20:
            self.signal_flicker = (self.signal_flicker + dt * 5) % (3.14159 * 2)

        # Message bubble animations
        for key in list(self.bubble_scale.keys()):
            self.bubble_scale[key] = min(1.0, self.bubble_scale[key] + dt * 8)

    def draw(self, screen):
        """Draw the phone interface"""
        if not self.active:
            return

        # Dark background with blur effect
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 240))
        screen.blit(overlay, (0, 0))

        # Draw phone frame
        self.draw_phone_frame(screen)

        # Draw navigation bar
        self.draw_navigation_bar(screen)

        # Draw phone screen content (network collapse animation removed)
        if self.showing_messages:
            self.draw_message_thread(screen)
        else:
            self.draw_contact_list(screen)

        # Draw emotional indicators
        self.draw_emotional_state(screen)

    def draw_phone_frame(self, screen):
        """Draw realistic iPhone-style device"""
        # Phone shadow
        shadow_surf = pygame.Surface((self.phone_width + 60, self.phone_height + 60), pygame.SRCALPHA)
        for i in range(20):
            alpha = 10 - (i // 2)
            pygame.draw.rect(shadow_surf, (0, 0, 0, alpha),
                           (i, i, self.phone_width + 60 - 2*i, self.phone_height + 60 - 2*i), 0, 25)
        screen.blit(shadow_surf, (self.phone_x - 30, self.phone_y - 25))

        # Phone body - space gray aluminum
        phone_rect = pygame.Rect(self.phone_x - 15, self.phone_y - 15,
                                self.phone_width + 30, self.phone_height + 30)
        pygame.draw.rect(screen, (64, 64, 68), phone_rect, 0, 22)
        pygame.draw.rect(screen, (88, 88, 92), phone_rect, 2, 22)

        # Side buttons
        # Volume buttons
        pygame.draw.rect(screen, (54, 54, 58),
                        (self.phone_x - 17, self.phone_y + 100, 4, 30), 0, 2)
        pygame.draw.rect(screen, (54, 54, 58),
                        (self.phone_x - 17, self.phone_y + 140, 4, 30), 0, 2)
        # Power button
        pygame.draw.rect(screen, (54, 54, 58),
                        (self.phone_x + self.phone_width + 13, self.phone_y + 120, 4, 50), 0, 2)

        # Screen bezel
        bezel_rect = pygame.Rect(self.phone_x - 8, self.phone_y - 8,
                                self.phone_width + 16, self.phone_height + 16)
        pygame.draw.rect(screen, (20, 20, 22), bezel_rect, 0, 18)

        # Screen with subtle gradient (pre-rendered: 667 lines → 1 blit)
        screen.blit(self._phone_screen_surf, (self.phone_x, self.phone_y))

        # Glass reflection effect (pre-rendered: 222 lines → 1 blit)
        screen.blit(self._phone_reflection_surf, (self.phone_x, self.phone_y))

        # Home indicator bar
        indicator_width = 134
        indicator_x = self.phone_x + (self.phone_width - indicator_width) // 2
        indicator_y = self.phone_y + self.phone_height - 15
        pygame.draw.rect(screen, (0, 0, 0),
                        (indicator_x, indicator_y, indicator_width, 4), 0, 2)

        # Status bar
        self.draw_ios_status_bar(screen)

        # Screen damage (cracks) - REMOVED per user request (weird lines)

    def draw_ios_status_bar(self, screen):
        """Draw iOS-style status bar"""
        # Status bar background
        status_rect = pygame.Rect(self.phone_x, self.phone_y, self.phone_width, 44)
        pygame.draw.rect(screen, self.STATUS_BAR_BG, status_rect)

        font_time = pygame.font.Font(None, 17)
        font_small = pygame.font.Font(None, 14)

        # Time (centered)
        time_surf = font_time.render(self.current_time, True, self.TEXT_PRIMARY)
        time_rect = time_surf.get_rect(center=(self.phone_x + self.phone_width // 2, self.phone_y + 14))
        screen.blit(time_surf, time_rect)

        # Left side - Carrier and signal
        left_x = self.phone_x + 8

        # Signal dots (modern style)
        signal_y = self.phone_y + 10
        for i in range(4):
            radius = 3
            color = self.TEXT_PRIMARY if i < self.signal_bars else self.SEPARATOR
            # Fixed: rotate expects degrees, signal_flicker is in radians, so convert
            # Also removed RGBA to avoid rendering issues
            pygame.draw.circle(screen, color, (left_x + i * 8, signal_y), radius)

        # Carrier text
        carrier_text = "T-Mobile"
        carrier_surf = font_small.render(carrier_text, True, self.TEXT_PRIMARY)
        screen.blit(carrier_surf, (left_x + 35, signal_y - 4))

        # WiFi icon (simplified)
        wifi_x = left_x + 95
        wifi_points = [
            (wifi_x, signal_y + 2),
            (wifi_x - 6, signal_y - 4),
            (wifi_x + 6, signal_y - 4)
        ]
        pygame.draw.lines(screen, self.TEXT_SECONDARY, False, wifi_points, 2)

        # Right side - Battery
        right_x = self.phone_x + self.phone_width - 30

        # Battery icon
        battery_width = 25
        battery_height = 12
        battery_y = signal_y - 3

        # Battery body
        battery_rect = pygame.Rect(right_x - battery_width, battery_y, battery_width, battery_height)
        pygame.draw.rect(screen, self.TEXT_PRIMARY, battery_rect, 1, 2)

        # Battery terminal
        pygame.draw.rect(screen, self.TEXT_PRIMARY,
                        (right_x + 1, battery_y + 3, 2, 6))

        # Battery fill (with gradient for low battery)
        fill_width = int((self.phone_battery / 100) * (battery_width - 2))
        if self.phone_battery <= 20:
            fill_color = self.BATTERY_RED
        elif self.phone_battery <= 50:
            fill_color = (255, 204, 0)  # Yellow
        else:
            fill_color = self.ONLINE_DOT

        if fill_width > 0:
            pygame.draw.rect(screen, fill_color,
                           (right_x - battery_width + 1, battery_y + 1, fill_width, battery_height - 2), 0, 1)

        # Battery percentage
        battery_text = font_small.render(f"{self.phone_battery}%", True,
                                        self.BATTERY_RED if self.phone_battery <= 20 else self.TEXT_PRIMARY)
        screen.blit(battery_text, (right_x - battery_width - 30, signal_y - 4))

        # Notification icons
        if len([c for c in self.contacts if c['status'] == 'unread']) > 0:
            # Message icon with badge
            msg_x = right_x - battery_width - 65
            self.draw_notification_icon(screen, msg_x, signal_y)

    def draw_contact_list(self, screen):
        """Draw iOS-style contact list"""
        # Content area
        content_y = self.phone_y + 88  # After navigation bar
        content_height = self.phone_height - 88 - 30  # Leave space for home indicator

        # Set clipping region to phone screen
        clip_rect = pygame.Rect(self.phone_x, content_y, self.phone_width, content_height)
        screen.set_clip(clip_rect)

        # Contacts
        font_name = pygame.font.Font(None, 17)
        font_preview = pygame.font.Font(None, 15)
        font_time = pygame.font.Font(None, 14)

        contact_height = 65  # Reduced from 72 to fit all contacts

        for i, contact in enumerate(self.contacts):
            y_pos = content_y + (i * contact_height)

            # Skip contacts that would be completely outside the visible area
            if y_pos > content_y + content_height:
                break

            # Hover/selection effect
            if i == self.selected_contact:
                select_rect = pygame.Rect(self.phone_x, y_pos, self.phone_width, contact_height)
                select_surf = pygame.Surface((self.phone_width, contact_height), pygame.SRCALPHA)
                select_surf.fill((0, 122, 255, 20))
                screen.blit(select_surf, (self.phone_x, y_pos))

            # Avatar with initials (adjusted for smaller height)
            avatar_x = self.phone_x + 16
            avatar_y = y_pos + 32  # Adjusted from 36

            # Draw avatar circle with gradient (pre-rendered: 24 circles → 1 blit)
            avatar_surf = self._avatar_cache[tuple(contact['avatar_color'])]
            screen.blit(avatar_surf, (avatar_x - 28, avatar_y - 28))

            # Add initials
            initials = ''.join([n[0].upper() for n in contact['name'].split()[:2]])
            font_initials = pygame.font.Font(None, 18)  # Slightly smaller
            initials_surf = font_initials.render(initials, True, (255, 255, 255))
            initials_rect = initials_surf.get_rect(center=(avatar_x, avatar_y))
            screen.blit(initials_surf, initials_rect)

            # Online status dot
            if contact['active'] and contact['relationship'] > 20:
                pygame.draw.circle(screen, (255, 255, 255), (avatar_x + 16, avatar_y + 16), 5)
                pygame.draw.circle(screen, self.ONLINE_DOT, (avatar_x + 16, avatar_y + 16), 3)

            # Contact name (adjusted positioning)
            name_surf = font_name.render(contact['name'], True, self.TEXT_PRIMARY)
            screen.blit(name_surf, (avatar_x + 36, y_pos + 12))

            # Last message preview (adjusted positioning)
            if contact['messages']:
                last_msg = contact['messages'][-1]
                preview = last_msg['text'][:40] + "..." if len(last_msg['text']) > 40 else last_msg['text']

                # Different color for sent vs received
                if last_msg['sent']:
                    preview = "You: " + preview
                    preview_color = self.TEXT_SECONDARY
                else:
                    preview_color = self.TEXT_PRIMARY if contact['status'] != 'Read' else self.TEXT_SECONDARY

                preview_surf = font_preview.render(preview, True, preview_color)
                screen.blit(preview_surf, (avatar_x + 36, y_pos + 31))

            # Time and status
            time_text = contact['messages'][-1].get('time', '') if contact['messages'] else ''
            time_surf = font_time.render(time_text, True, self.TEXT_SECONDARY)
            time_rect = time_surf.get_rect(right=self.phone_x + self.phone_width - 16, y=y_pos + 12)
            screen.blit(time_surf, time_rect)

            # Unread badge
            if contact['status'] != 'Read' and not any(msg['sent'] for msg in contact['messages'][-1:]):
                badge_x = self.phone_x + self.phone_width - 30
                badge_y = y_pos + 32  # Adjusted
                pygame.draw.circle(screen, self.BADGE_RED, (badge_x, badge_y), 9)  # Slightly smaller
                font_badge = pygame.font.Font(None, 13)
                badge_text = "1"
                badge_surf = font_badge.render(badge_text, True, (255, 255, 255))
                badge_rect = badge_surf.get_rect(center=(badge_x, badge_y))
                screen.blit(badge_surf, badge_rect)

            # Separator line
            if i < len(self.contacts) - 1:
                pygame.draw.line(screen, self.SEPARATOR,
                               (avatar_x + 36, y_pos + contact_height - 1),
                               (self.phone_x + self.phone_width - 16, y_pos + contact_height - 1), 1)

        # Reset clipping
        screen.set_clip(None)

    def draw_message_thread(self, screen):
        """Draw iOS-style message conversation"""
        contact = self.contacts[self.selected_contact]

        # Content area
        content_y = self.phone_y + 88
        content_height = self.phone_height - 88 - 60  # Leave space for input field

        # Set clipping region to phone screen
        clip_rect = pygame.Rect(self.phone_x, content_y, self.phone_width, content_height)
        screen.set_clip(clip_rect)

        # Messages background
        msg_bg = pygame.Surface((self.phone_width, content_height), pygame.SRCALPHA)
        msg_bg.fill((255, 255, 255, 255))
        screen.blit(msg_bg, (self.phone_x, content_y))

        # Messages
        font = pygame.font.Font(None, 16)
        y_offset = content_y + 20

        for msg_idx, msg in enumerate(contact['messages']):
            # Get or create bubble scale
            bubble_key = f"{self.selected_contact}_{msg_idx}"
            if bubble_key not in self.bubble_scale:
                self.bubble_scale[bubble_key] = 0.0

            scale = self.bubble_scale[bubble_key]

            # Message bubble
            text_lines = self.wrap_text(msg['text'], 220, font)
            bubble_height = len(text_lines) * 20 + 16
            bubble_width = max(60, min(240, max(font.size(line)[0] for line in text_lines) + 24))

            if msg['sent']:
                # Sent message (blue, right side)
                bubble_x = self.phone_x + self.phone_width - bubble_width - 12
                bubble_color = self.MESSAGE_SENT
                text_color = (255, 255, 255)
                tail_side = 'right'
            else:
                # Received message (gray, left side)
                bubble_x = self.phone_x + 12
                bubble_color = self.MESSAGE_RECEIVED
                text_color = self.TEXT_PRIMARY
                tail_side = 'left'

            # Scale animation
            if scale < 1.0:
                scaled_width = int(bubble_width * scale)
                scaled_height = int(bubble_height * scale)
                if msg['sent']:
                    bubble_x = self.phone_x + self.phone_width - scaled_width - 12
            else:
                scaled_width = bubble_width
                scaled_height = bubble_height

            # Draw bubble with tail
            self.draw_message_bubble(screen, bubble_x, y_offset, scaled_width, scaled_height,
                                    bubble_color, tail_side, scale)

            # Message text (only show when scaled enough)
            if scale > 0.5:
                text_alpha = int(255 * min(1.0, (scale - 0.5) * 2))
                for i, line in enumerate(text_lines):
                    text_surf = font.render(line, True, text_color)
                    if text_alpha < 255:
                        text_surf.set_alpha(text_alpha)
                    screen.blit(text_surf, (bubble_x + 12, y_offset + 8 + (i * 20)))

            # Time and status
            if scale >= 1.0:
                font_time = pygame.font.Font(None, 12)
                time_text = msg.get('time', '')

                if msg['sent'] and msg_idx == len(contact['messages']) - 1:
                    # Show delivery status for last sent message
                    if contact['status'] == 'Read':
                        time_text += " · Read"
                    else:
                        time_text += " · Delivered"

                time_surf = font_time.render(time_text, True, self.TEXT_SECONDARY)
                time_y = y_offset + scaled_height + 4

                if msg['sent']:
                    time_rect = time_surf.get_rect(right=bubble_x + scaled_width, y=time_y)
                else:
                    time_rect = time_surf.get_rect(left=bubble_x, y=time_y)
                screen.blit(time_surf, time_rect)

            # Typing indicator
            if msg.get('typing'):
                self.draw_typing_indicator(screen, bubble_x + 12, y_offset + 10)

            y_offset += scaled_height + 20

        # Reset clipping before drawing input field
        screen.set_clip(None)

        # Input field at bottom
        self.draw_message_input(screen)

    def draw_network_collapse(self, screen):
        """Draw visualization of social network collapse"""
        center_x = self.phone_x + self.phone_width // 2
        center_y = self.phone_y + self.phone_height // 2

        font = pygame.font.Font(None, 32)
        title = "Social Network: COLLAPSED"
        title_surf = font.render(title, True, (200, 50, 50))
        title_rect = title_surf.get_rect(center=(center_x, center_y - 100))
        screen.blit(title_surf, title_rect)

        # Draw breaking connections
        for i, contact in enumerate(self.contacts):
            angle = (i / len(self.contacts)) * 3.14159 * 2
            # Fixed: use angle in radians correctly
            end_x = center_x + int(150 * math.cos(angle))
            end_y = center_y + int(150 * math.sin(angle))

            # Fading line (removed alpha to avoid RGBA issues)
            alpha_factor = max(0, 100 - self.network_animation_timer * 30) / 100.0
            if alpha_factor > 0:
                # Fade color by blending with background instead of using alpha
                faded_color = tuple(int(c * alpha_factor) for c in contact['avatar_color'])
                pygame.draw.line(screen, faded_color,
                               (center_x, center_y), (end_x, end_y), 2)

                # Contact name fading (font.render doesn't support RGBA)
                font_name = pygame.font.Font(None, 16)
                name_surf = font_name.render(contact['name'], True, faded_color)
                screen.blit(name_surf, (end_x - 20, end_y - 10))

        # Bottom text
        font_bottom = pygame.font.Font(None, 20)
        bottom_text = "You've exhausted every option"
        bottom_surf = font_bottom.render(bottom_text, True, (150, 150, 150))
        bottom_rect = bottom_surf.get_rect(center=(center_x, center_y + 150))
        screen.blit(bottom_surf, bottom_rect)

    def draw_emotional_state(self, screen):
        """Draw emotional indicators"""
        # Panel on the side
        panel_x = self.phone_x - 200
        panel_y = self.phone_y + 100
        panel_width = 180
        panel_height = 300

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (25, 25, 30), panel_rect, 0, 5)
        pygame.draw.rect(screen, (50, 50, 55), panel_rect, 2, 5)

        font = pygame.font.Font(None, 20)
        font_small = pygame.font.Font(None, 16)

        # Title
        title = "Day 15"
        title_surf = font.render(title, True, (200, 200, 200))
        screen.blit(title_surf, (panel_x + 10, panel_y + 10))

        # Isolation level
        y_offset = panel_y + 50
        isolation_text = f"Isolation: {self.isolation_level}%"
        isolation_surf = font_small.render(isolation_text, True, (200, 100, 100))
        screen.blit(isolation_surf, (panel_x + 10, y_offset))

        bar_rect = pygame.Rect(panel_x + 10, y_offset + 20, 160, 15)
        pygame.draw.rect(screen, (40, 20, 20), bar_rect, 0, 3)
        fill_width = int((self.isolation_level / 100) * 160)
        pygame.draw.rect(screen, (200, 50, 50), (panel_x + 10, y_offset + 20, fill_width, 15), 0, 3)

        # Hope level
        y_offset += 50
        hope_text = f"Hope: {self.hope_level}%"
        hope_surf = font_small.render(hope_text, True, (100, 200, 100))
        screen.blit(hope_surf, (panel_x + 10, y_offset))

        bar_rect = pygame.Rect(panel_x + 10, y_offset + 20, 160, 15)
        pygame.draw.rect(screen, (20, 40, 20), bar_rect, 0, 3)
        fill_width = int((self.hope_level / 100) * 160)
        pygame.draw.rect(screen, (50, 150, 50), (panel_x + 10, y_offset + 20, fill_width, 15), 0, 3)

        # Stats
        y_offset += 50
        stats = [
            "Friends helped: 5",
            "Times rejected: 12",
            "Nights in shelter: 8",
            "Nights on couches: 7",
            "Messages ignored: 23"
        ]

        for stat in stats:
            stat_surf = font_small.render(stat, True, (140, 140, 140))
            screen.blit(stat_surf, (panel_x + 10, y_offset))
            y_offset += 25

    def wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    def draw_navigation_bar(self, screen):
        """Draw iOS-style navigation bar"""
        # Navigation bar background
        nav_rect = pygame.Rect(self.phone_x, self.phone_y + 44, self.phone_width, 44)
        nav_surf = pygame.Surface((self.phone_width, 44), pygame.SRCALPHA)
        nav_surf.fill((249, 249, 249, 250))
        screen.blit(nav_surf, (self.phone_x, self.phone_y + 44))

        # Bottom border
        pygame.draw.line(screen, self.SEPARATOR,
                        (self.phone_x, self.phone_y + 87),
                        (self.phone_x + self.phone_width, self.phone_y + 87), 1)

        font_title = pygame.font.Font(None, 20)
        font_button = pygame.font.Font(None, 17)

        if self.showing_messages:
            # Message thread navigation
            contact = self.contacts[self.selected_contact]

            # Back button
            back_text = "< Messages"
            back_surf = font_button.render(back_text, True, self.MESSAGE_SENT)
            screen.blit(back_surf, (self.phone_x + 12, self.phone_y + 58))

            # Contact name centered
            name_surf = font_title.render(contact['name'], True, self.TEXT_PRIMARY)
            name_rect = name_surf.get_rect(center=(self.phone_x + self.phone_width // 2, self.phone_y + 66))
            screen.blit(name_surf, name_rect)

            # Info button
            info_text = "ⓘ"
            info_surf = font_button.render(info_text, True, self.MESSAGE_SENT)
            info_rect = info_surf.get_rect(right=self.phone_x + self.phone_width - 12, y=self.phone_y + 58)
            screen.blit(info_surf, info_rect)
        else:
            # Contact list navigation
            title = "Messages"
            title_surf = font_title.render(title, True, self.TEXT_PRIMARY)
            title_rect = title_surf.get_rect(center=(self.phone_x + self.phone_width // 2, self.phone_y + 66))
            screen.blit(title_surf, title_rect)

            # Edit button
            edit_text = "Edit"
            edit_surf = font_button.render(edit_text, True, self.MESSAGE_SENT)
            screen.blit(edit_surf, (self.phone_x + 12, self.phone_y + 58))

            # Compose button
            compose_text = "✎"
            compose_surf = font_button.render(compose_text, True, self.MESSAGE_SENT)
            compose_rect = compose_surf.get_rect(right=self.phone_x + self.phone_width - 12, y=self.phone_y + 58)
            screen.blit(compose_surf, compose_rect)

    def draw_message_bubble(self, screen, x, y, width, height, color, tail_side, scale=1.0):
        """Draw message bubble with tail"""
        if scale <= 0:
            return

        # Main bubble
        bubble_rect = pygame.Rect(x, y, width, height)
        bubble_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Bubble with rounded corners
        radius = min(18, height // 2)
        pygame.draw.rect(bubble_surf, color, (0, 0, width, height), 0, radius)

        # Add tail
        if scale >= 1.0:  # Only show tail when fully scaled
            tail_points = []
            if tail_side == 'right':
                tail_points = [
                    (width - 2, height - 10),
                    (width + 8, height - 5),
                    (width - 2, height - 18)
                ]
                # Draw on screen, not bubble_surf
                pygame.draw.polygon(screen, color,
                                   [(x + p[0], y + p[1]) for p in tail_points])
            else:
                tail_points = [
                    (2, height - 10),
                    (-8, height - 5),
                    (2, height - 18)
                ]
                pygame.draw.polygon(screen, color,
                                   [(x + p[0], y + p[1]) for p in tail_points])

        screen.blit(bubble_surf, (x, y))

    def draw_typing_indicator(self, screen, x, y):
        """Draw animated typing dots"""
        for i in range(3):
            # Animated bounce effect - fixed rotation
            angle_rad = (self.animation_time * 5 + i * 120) * (math.pi / 180)  # Convert to radians
            offset = abs(3 * math.sin(angle_rad))
            dot_y = y + offset

            # Simple pulsing without rotation issues
            pulse = abs(math.sin(self.typing_dots * math.pi + i * (math.pi / 3)))
            brightness = int(128 + 127 * pulse)
            color = (brightness, brightness, brightness)

            pygame.draw.circle(screen, color, (x + i * 12, int(dot_y)), 3)

    def draw_message_input(self, screen):
        """Draw message input field at bottom"""
        input_y = self.phone_y + self.phone_height - 60
        input_height = 40

        # Background
        input_bg = pygame.Surface((self.phone_width, 60), pygame.SRCALPHA)
        input_bg.fill((247, 247, 247, 250))
        screen.blit(input_bg, (self.phone_x, input_y))

        # Top border
        pygame.draw.line(screen, self.SEPARATOR,
                        (self.phone_x, input_y),
                        (self.phone_x + self.phone_width, input_y), 1)

        # Input field
        field_rect = pygame.Rect(self.phone_x + 45, input_y + 10,
                                self.phone_width - 100, 40)
        pygame.draw.rect(screen, (255, 255, 255), field_rect, 0, 20)
        pygame.draw.rect(screen, self.SEPARATOR, field_rect, 1, 20)

        # Placeholder text
        font = pygame.font.Font(None, 16)
        placeholder = "iMessage"
        placeholder_surf = font.render(placeholder, True, self.TEXT_SECONDARY)
        screen.blit(placeholder_surf, (field_rect.x + 12, field_rect.y + 12))

        # Camera button
        cam_x = self.phone_x + 12
        cam_y = input_y + 20
        pygame.draw.circle(screen, self.TEXT_SECONDARY, (cam_x, cam_y), 14, 2)
        pygame.draw.circle(screen, self.TEXT_SECONDARY, (cam_x, cam_y), 6)

        # Send button (disabled since no text)
        send_x = self.phone_x + self.phone_width - 30
        send_y = input_y + 20
        pygame.draw.circle(screen, self.SEPARATOR, (send_x, send_y), 14)
        # Arrow
        arrow_points = [
            (send_x - 5, send_y),
            (send_x + 5, send_y),
            (send_x, send_y - 5)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), arrow_points)

    def draw_notification_icon(self, screen, x, y):
        """Draw message notification icon with badge"""
        # Message bubble icon
        bubble_rect = pygame.Rect(x, y - 4, 16, 12)
        pygame.draw.rect(screen, self.TEXT_SECONDARY, bubble_rect, 0, 4)

        # Badge
        pygame.draw.circle(screen, self.BADGE_RED, (x + 14, y - 2), 5)
        font = pygame.font.Font(None, 10)
        badge_surf = font.render("3", True, (255, 255, 255))
        badge_rect = badge_surf.get_rect(center=(x + 14, y - 2))
        screen.blit(badge_surf, badge_rect)