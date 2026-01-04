"""
Text Messaging Mini-Game for Couch Surfing Chapter
Used in objective: text_everyone
"""
import pygame
import random

class TextMessaging:
    """Text messaging interface for desperately reaching out to contacts"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Phone UI dimensions
        self.phone_width = 350
        self.phone_height = 700
        self.phone_x = (self.SCREEN_WIDTH - self.phone_width) // 2
        self.phone_y = (self.SCREEN_HEIGHT - self.phone_height) // 2

        # Contacts list
        self.contacts = [
            {'name': 'Sarah (classmate)', 'status': 'unread', 'response': None, 'will_help': True, 'delay': 2.5},
            {'name': 'Mike (old friend)', 'status': 'unread', 'response': None, 'will_help': False, 'delay': 3.0},
            {'name': 'Jordan (work)', 'status': 'unread', 'response': None, 'will_help': False, 'delay': 4.0},
            {'name': 'Ashley (foster sib)', 'status': 'unread', 'response': None, 'will_help': False, 'delay': 5.5},
            {'name': 'Marcus (neighbor)', 'status': 'unread', 'response': None, 'will_help': False, 'delay': 3.5},
            {'name': 'Emma (study group)', 'status': 'unread', 'response': None, 'will_help': False, 'delay': 6.0},
            {'name': 'David (ex-roommate)', 'status': 'unread', 'response': None, 'will_help': False, 'delay': 4.5},
        ]

        # Message to send
        self.mass_message = "Hey, weird question but can I crash for a few nights? Emergency situation, I'll explain in person. Really need help."

        # UI state
        self.message_sent = False
        self.send_animation_timer = 0
        self.response_timer = 0
        self.all_responses_received = False
        self.sarah_highlighted = False

        # Battery level (adds urgency)
        self.battery_level = 47

        # Response messages
        self.negative_responses = [
            "Sorry, wish I could help but my place is full",
            "Can't do it, roommates would freak",
            "I'm actually out of town right now",
            "My landlord is super strict about guests",
            "Wish I could but my parents are visiting",
            "Sorry, going through my own stuff right now",
            "Read 2:34 PM"  # The dreaded 'read' with no response
        ]

        self.sarah_response = "OMG yes! 3 nights max though. Parents can't know. Come after 11pm"

        # Anxiety meter
        self.anxiety_level = 30
        self.max_anxiety = 100

        # Button states
        self.send_button_rect = pygame.Rect(self.phone_x + 50, self.phone_y + 600, self.phone_width - 100, 50)
        self.continue_button_rect = None
        self.hovering_send = False

    def start(self):
        """Start the text messaging activity"""
        self.active = True
        self.completed = False

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if button != 1:  # Left click only
            return

        if not self.message_sent and self.send_button_rect.collidepoint(pos):
            # Send the mass message
            self.send_mass_message()

        elif self.all_responses_received and self.continue_button_rect:
            if self.continue_button_rect.collidepoint(pos):
                self.complete_activity()

    def handle_mouse_motion(self, pos):
        """Handle mouse hover effects"""
        if not self.message_sent:
            self.hovering_send = self.send_button_rect.collidepoint(pos)

    def send_mass_message(self):
        """Initiate sending messages to all contacts"""
        self.message_sent = True
        self.send_animation_timer = 0
        self.response_timer = 0

        # Mark all as 'sending'
        for contact in self.contacts:
            contact['status'] = 'sending'

    def update(self, dt):
        """Update the messaging state"""
        if not self.active:
            return

        if self.message_sent:
            # Update send animation
            self.send_animation_timer += dt

            # Mark messages as sent after delay
            for i, contact in enumerate(self.contacts):
                if contact['status'] == 'sending' and self.send_animation_timer > (i * 0.3 + 0.5):
                    contact['status'] = 'sent'

            # Start receiving responses
            self.response_timer += dt

            # Check for responses
            for contact in self.contacts:
                if contact['status'] == 'sent' and self.response_timer > contact['delay']:
                    contact['status'] = 'responded'

                    if contact['will_help']:
                        contact['response'] = self.sarah_response
                        self.sarah_highlighted = True
                        # Decrease anxiety when help is found
                        self.anxiety_level = max(10, self.anxiety_level - 40)
                    else:
                        contact['response'] = random.choice(self.negative_responses)
                        # Increase anxiety with each rejection
                        self.anxiety_level = min(self.max_anxiety, self.anxiety_level + 8)

            # Check if all responses received
            if all(c['status'] == 'responded' for c in self.contacts):
                self.all_responses_received = True

                # Create continue button
                if not self.continue_button_rect:
                    self.continue_button_rect = pygame.Rect(
                        self.phone_x + 50,
                        self.phone_y + 620,
                        self.phone_width - 100,
                        40
                    )

        # Battery drain
        self.battery_level = max(5, self.battery_level - dt * 2)

    def draw(self, screen):
        """Draw the text messaging interface"""
        if not self.active:
            return

        # Draw dark background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill((20, 20, 30))
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Draw phone frame
        pygame.draw.rect(screen, (40, 40, 50),
                        (self.phone_x - 10, self.phone_y - 10, self.phone_width + 20, self.phone_height + 20),
                        border_radius=20)
        pygame.draw.rect(screen, (20, 20, 25),
                        (self.phone_x, self.phone_y, self.phone_width, self.phone_height),
                        border_radius=15)

        # Draw status bar
        self.draw_status_bar(screen)

        # Draw message interface
        if not self.message_sent:
            self.draw_compose_screen(screen)
        else:
            self.draw_responses_screen(screen)

        # Draw anxiety meter
        self.draw_anxiety_meter(screen)

        # Show exit instruction when ESC is available
        if self.all_responses_received:
            exit_font = pygame.font.Font(None, 24)
            exit_text = exit_font.render("Press ESC to exit", True, (150, 150, 150))
            screen.blit(exit_text, (20, self.SCREEN_HEIGHT - 40))

    def draw_status_bar(self, screen):
        """Draw phone status bar with battery"""
        font = pygame.font.Font(None, 18)

        # Carrier and time
        carrier_text = font.render("Struggling Network", True, (200, 200, 200))
        screen.blit(carrier_text, (self.phone_x + 10, self.phone_y + 10))

        time_text = font.render("2:31 PM", True, (200, 200, 200))
        time_rect = time_text.get_rect(center=(self.phone_x + self.phone_width // 2, self.phone_y + 18))
        screen.blit(time_text, time_rect)

        # Battery indicator
        battery_color = (255, 100, 100) if self.battery_level < 20 else (255, 200, 100) if self.battery_level < 50 else (100, 255, 100)
        battery_text = font.render(f"{int(self.battery_level)}%", True, battery_color)
        battery_rect = battery_text.get_rect(right=self.phone_x + self.phone_width - 10, y=self.phone_y + 10)
        screen.blit(battery_text, battery_rect)

        # Battery icon
        battery_icon_rect = pygame.Rect(battery_rect.left - 25, self.phone_y + 12, 20, 10)
        pygame.draw.rect(screen, battery_color, battery_icon_rect, 2)
        battery_fill = int((self.battery_level / 100) * 18)
        pygame.draw.rect(screen, battery_color, (battery_icon_rect.x + 1, battery_icon_rect.y + 1, battery_fill, 8))

    def draw_compose_screen(self, screen):
        """Draw the message composition screen"""
        font_title = pygame.font.Font(None, 24)
        font_body = pygame.font.Font(None, 18)

        # Title
        title = font_title.render("New Message", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.phone_x + self.phone_width // 2, self.phone_y + 50))
        screen.blit(title, title_rect)

        # Recipients count
        recipients = font_body.render(f"To: {len(self.contacts)} contacts", True, (150, 150, 200))
        screen.blit(recipients, (self.phone_x + 20, self.phone_y + 80))

        # Message box
        msg_box = pygame.Rect(self.phone_x + 20, self.phone_y + 120, self.phone_width - 40, 150)
        pygame.draw.rect(screen, (50, 50, 60), msg_box, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), msg_box, 2, border_radius=10)

        # Message text (wrapped)
        y_offset = 0
        words = self.mass_message.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if font_body.size(test_line)[0] < msg_box.width - 20:
                line = test_line
            else:
                if line:
                    text_surf = font_body.render(line, True, (220, 220, 230))
                    screen.blit(text_surf, (msg_box.x + 10, msg_box.y + 10 + y_offset))
                    y_offset += 25
                line = word + " "
        if line:
            text_surf = font_body.render(line, True, (220, 220, 230))
            screen.blit(text_surf, (msg_box.x + 10, msg_box.y + 10 + y_offset))

        # Contact preview
        preview_y = self.phone_y + 300
        preview_title = font_body.render("Sending to:", True, (150, 150, 150))
        screen.blit(preview_title, (self.phone_x + 20, preview_y))

        for i, contact in enumerate(self.contacts[:4]):  # Show first 4
            contact_text = font_body.render(f"• {contact['name']}", True, (180, 180, 190))
            screen.blit(contact_text, (self.phone_x + 30, preview_y + 25 + i * 22))

        if len(self.contacts) > 4:
            more_text = font_body.render(f"...and {len(self.contacts) - 4} more", True, (120, 120, 130))
            screen.blit(more_text, (self.phone_x + 30, preview_y + 25 + 4 * 22))

        # Send button
        button_color = (100, 150, 255) if self.hovering_send else (80, 120, 220)
        pygame.draw.rect(screen, button_color, self.send_button_rect, border_radius=25)

        send_text = font_title.render("Send to All", True, (255, 255, 255))
        send_rect = send_text.get_rect(center=self.send_button_rect.center)
        screen.blit(send_text, send_rect)

    def draw_responses_screen(self, screen):
        """Draw the responses from contacts"""
        font_title = pygame.font.Font(None, 22)
        font_body = pygame.font.Font(None, 16)

        # Title
        title = font_title.render("Messages", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.phone_x + self.phone_width // 2, self.phone_y + 50))
        screen.blit(title, title_rect)

        # Scroll area for messages
        msg_area_y = self.phone_y + 80
        msg_height = 500

        for i, contact in enumerate(self.contacts):
            y_pos = msg_area_y + i * 65

            if y_pos > self.phone_y + msg_height:
                break

            # Contact bubble
            bubble_rect = pygame.Rect(self.phone_x + 10, y_pos, self.phone_width - 20, 55)

            if contact['will_help'] and contact['status'] == 'responded':
                # Highlight Sarah's positive response
                pygame.draw.rect(screen, (50, 80, 50), bubble_rect, border_radius=10)
                pygame.draw.rect(screen, (100, 255, 100), bubble_rect, 2, border_radius=10)
            else:
                pygame.draw.rect(screen, (40, 40, 50), bubble_rect, border_radius=10)

            # Contact name
            name_text = font_body.render(contact['name'], True, (200, 200, 210))
            screen.blit(name_text, (bubble_rect.x + 10, bubble_rect.y + 5))

            # Status/Response
            if contact['status'] == 'sending':
                status_text = font_body.render("Sending...", True, (150, 150, 160))
                screen.blit(status_text, (bubble_rect.x + 10, bubble_rect.y + 25))
            elif contact['status'] == 'sent':
                status_text = font_body.render("Delivered ✓", True, (120, 120, 130))
                screen.blit(status_text, (bubble_rect.x + 10, bubble_rect.y + 25))
            elif contact['status'] == 'responded':
                if contact['response']:
                    # Truncate response if too long
                    response = contact['response']
                    if len(response) > 40:
                        response = response[:37] + "..."

                    color = (100, 255, 100) if contact['will_help'] else (200, 150, 150)
                    response_text = font_body.render(response, True, color)
                    screen.blit(response_text, (bubble_rect.x + 10, bubble_rect.y + 25))

        # Continue button if all responded
        if self.all_responses_received and self.continue_button_rect:
            pygame.draw.rect(screen, (100, 200, 100), self.continue_button_rect, border_radius=20)
            continue_text = font_title.render("Sarah Can Help!", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=self.continue_button_rect.center)
            screen.blit(continue_text, continue_rect)

    def draw_anxiety_meter(self, screen):
        """Draw anxiety level indicator"""
        meter_x = self.phone_x - 100
        meter_y = self.phone_y + 200
        meter_width = 20
        meter_height = 200

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (meter_x, meter_y, meter_width, meter_height))

        # Anxiety level
        anxiety_height = int((self.anxiety_level / self.max_anxiety) * meter_height)
        anxiety_color = (255, 100, 100) if self.anxiety_level > 70 else (255, 200, 100) if self.anxiety_level > 40 else (100, 200, 100)

        pygame.draw.rect(screen, anxiety_color,
                        (meter_x, meter_y + meter_height - anxiety_height, meter_width, anxiety_height))

        # Border
        pygame.draw.rect(screen, (100, 100, 100), (meter_x, meter_y, meter_width, meter_height), 2)

        # Label
        font = pygame.font.Font(None, 18)
        label = font.render("ANXIETY", True, (200, 200, 200))
        label_rotated = pygame.transform.rotate(label, 90)
        screen.blit(label_rotated, (meter_x - 20, meter_y + meter_height // 2 - 30))

    def complete_activity(self):
        """Complete the text messaging activity"""
        self.completed = True
        self.active = False

        # Mark the interaction as completed in the narrative interior
        if hasattr(self, 'narrative_ref') and self.narrative_ref:
            # Mark the computer interaction as completed so objective can progress
            if hasattr(self.narrative_ref, 'completed_interactions'):
                self.narrative_ref.completed_interactions.add('computer')
                print("[TEXT_MESSAGING] Marked 'computer' interaction as completed")

    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE and self.all_responses_received:
            self.complete_activity()