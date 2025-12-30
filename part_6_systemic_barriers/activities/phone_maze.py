"""
Phone Maze Mini-Game
Navigate automated phone system that always loops back
Demonstrates digital barriers in accessing services
"""
import pygame


class PhoneMazeGame:
    """Phone menu navigation that never reaches a human"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Phone menu state
        self.current_menu = 'main'
        self.menu_history = []
        self.loops_completed = 0
        self.max_loops = 3  # After 3 loops, show frustration ending

        # Hold time simulation
        self.hold_time = 0
        self.max_hold_time = 300  # 5 seconds simulated as 5 minutes

        # Menu definitions - all paths loop back
        self.menus = {
            'main': {
                'prompt': "Welcome to California Benefits Hotline.",
                'subtext': "Your call is important to us.",
                'options': [
                    ('1', 'For English, press 1', 'english'),
                    ('2', 'Para Espanol, oprima 2', 'spanish'),
                    ('0', 'To repeat this menu, press 0', 'main'),
                ]
            },
            'english': {
                'prompt': "Main Menu",
                'subtext': "Please listen carefully as our options have changed.",
                'options': [
                    ('1', 'For new applications, press 1', 'applications'),
                    ('2', 'For existing cases, press 2', 'existing'),
                    ('3', 'For general information, press 3', 'info'),
                    ('0', 'To return to main menu, press 0', 'main'),
                ]
            },
            'spanish': {
                'prompt': "Menu Principal",
                'subtext': "Por favor escuche con atencion.",
                'options': [
                    ('1', 'Para aplicaciones nuevas, oprima 1', 'applications'),
                    ('2', 'Para casos existentes, oprima 2', 'existing'),
                    ('0', 'Para volver al menu principal, oprima 0', 'main'),
                ]
            },
            'applications': {
                'prompt': "New Applications",
                'subtext': "Current wait time: approximately 45 minutes.",
                'options': [
                    ('1', 'For CalFresh, press 1', 'calfresh'),
                    ('2', 'For Medi-Cal, press 2', 'medical'),
                    ('3', 'For CalWORKs, press 3', 'calworks'),
                    ('0', 'To return to previous menu, press 0', 'english'),
                ]
            },
            'existing': {
                'prompt': "Existing Cases",
                'subtext': "Please have your case number ready.",
                'options': [
                    ('1', 'To check case status, press 1', 'status'),
                    ('2', 'To report changes, press 2', 'changes'),
                    ('0', 'To return to previous menu, press 0', 'english'),
                ]
            },
            'info': {
                'prompt': "General Information",
                'subtext': "Visit our website at benefits.ca.gov",
                'options': [
                    ('1', 'For office hours, press 1', 'hours'),
                    ('2', 'For office locations, press 2', 'locations'),
                    ('0', 'To return to previous menu, press 0', 'english'),
                ]
            },
            'calfresh': {
                'prompt': "CalFresh Applications",
                'subtext': "All representatives are currently busy.",
                'options': [
                    ('1', 'To apply online, press 1', 'online_redirect'),
                    ('2', 'To speak to a representative, press 2', 'hold'),
                    ('0', 'To return to previous menu, press 0', 'applications'),
                ]
            },
            'medical': {
                'prompt': "Medi-Cal Applications",
                'subtext': "Due to high call volume, wait times are extended.",
                'options': [
                    ('1', 'For eligibility information, press 1', 'info'),
                    ('2', 'To speak to a representative, press 2', 'hold'),
                    ('0', 'To return to previous menu, press 0', 'applications'),
                ]
            },
            'calworks': {
                'prompt': "CalWORKs Applications",
                'subtext': "Office hours are Monday-Friday, 8am-5pm.",
                'options': [
                    ('1', 'To speak to a representative, press 2', 'hold'),
                    ('0', 'To return to previous menu, press 0', 'applications'),
                ]
            },
            'status': {
                'prompt': "Case Status",
                'subtext': "Enter your 9-digit case number.",
                'options': [
                    ('1', 'I don\'t have my case number', 'no_case'),
                    ('0', 'To return to previous menu, press 0', 'existing'),
                ]
            },
            'changes': {
                'prompt': "Report Changes",
                'subtext': "Changes must be reported within 10 days.",
                'options': [
                    ('1', 'To report income changes, press 1', 'hold'),
                    ('2', 'To report address changes, press 2', 'hold'),
                    ('0', 'To return to previous menu, press 0', 'existing'),
                ]
            },
            'hours': {
                'prompt': "Office Hours",
                'subtext': "Monday-Friday 8:00 AM - 5:00 PM",
                'options': [
                    ('0', 'To return to previous menu, press 0', 'info'),
                ]
            },
            'locations': {
                'prompt': "Office Locations",
                'subtext': "Visit benefits.ca.gov/offices for locations.",
                'options': [
                    ('0', 'To return to previous menu, press 0', 'info'),
                ]
            },
            'online_redirect': {
                'prompt': "Online Applications",
                'subtext': "Please visit benefits.ca.gov to apply online.",
                'options': [
                    ('0', 'To return to main menu, press 0', 'main'),
                ]
            },
            'no_case': {
                'prompt': "Case Number Required",
                'subtext': "You need your case number to check status.",
                'options': [
                    ('1', 'To request case number by mail, press 1', 'mail_wait'),
                    ('0', 'To return to main menu, press 0', 'main'),
                ]
            },
            'mail_wait': {
                'prompt': "Mail Request",
                'subtext': "Your case number will arrive in 7-10 business days.",
                'options': [
                    ('0', 'To return to main menu, press 0', 'main'),
                ]
            },
            'hold': {
                'prompt': "Please Hold",
                'subtext': "Your estimated wait time is... 45 minutes.",
                'options': [],
                'is_hold': True
            },
            'disconnected': {
                'prompt': "Call Disconnected",
                'subtext': "We're sorry, all circuits are busy. Please try again later.",
                'options': [],
                'is_end': True
            }
        }

        # Animation state
        self.blink_timer = 0
        self.dots_count = 0

        # Result state
        self.show_result = False
        self.result_timer = 0

    def handle_event(self, event):
        """Handle phone button presses"""
        if not self.active or self.completed:
            return False

        if self.show_result:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.completed = True
            return True

        menu = self.menus.get(self.current_menu, {})

        # Handle hold state
        if menu.get('is_hold'):
            if event.type == pygame.KEYDOWN:
                # Any key during hold = disconnect
                self.current_menu = 'disconnected'
                self.loops_completed += 1
            return True

        # Handle end state
        if menu.get('is_end'):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if self.loops_completed >= self.max_loops:
                    self.show_result = True
                    self.result_timer = 180
                else:
                    # Start over
                    self.current_menu = 'main'
            return True

        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)

            # Check for number key press
            for option_key, _, next_menu in menu.get('options', []):
                if key_name == option_key or key_name == f'[{option_key}]':
                    self.menu_history.append(self.current_menu)
                    self.current_menu = next_menu

                    # Track if we've looped back to main
                    if next_menu == 'main' and len(self.menu_history) > 3:
                        self.loops_completed += 1
                    break

        return True

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Animation updates
        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.blink_timer = 0
            self.dots_count = (self.dots_count + 1) % 4

        menu = self.menus.get(self.current_menu, {})

        # Handle hold timer
        if menu.get('is_hold'):
            self.hold_time += 1
            if self.hold_time >= self.max_hold_time:
                # Disconnect after hold
                self.current_menu = 'disconnected'
                self.loops_completed += 1
                self.hold_time = 0

        # Handle result timer
        if self.show_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the phone interface"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(250)
        overlay.fill((30, 30, 40))
        screen.blit(overlay, (0, 0))

        if self.show_result:
            self.render_result(screen)
            return

        # Phone frame
        phone_rect = pygame.Rect(390, 80, 500, 560)
        pygame.draw.rect(screen, (50, 50, 60), phone_rect, border_radius=20)
        pygame.draw.rect(screen, (80, 80, 90), phone_rect, 3, border_radius=20)

        # Screen area
        screen_rect = pygame.Rect(410, 100, 460, 280)
        pygame.draw.rect(screen, (200, 220, 200), screen_rect)

        menu = self.menus.get(self.current_menu, {})

        # Render menu content
        self.render_menu(screen, screen_rect, menu)

        # Render keypad
        self.render_keypad(screen, phone_rect)

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst_text = "Press number keys to navigate the phone menu"
        inst_surface = inst_font.render(inst_text, True, (150, 150, 160))
        screen.blit(inst_surface, (self.SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, 660))

        # Loop counter
        if self.loops_completed > 0:
            loop_text = f"Times returned to start: {self.loops_completed}"
            loop_surface = inst_font.render(loop_text, True, (200, 100, 100))
            screen.blit(loop_surface, (self.SCREEN_WIDTH // 2 - loop_surface.get_width() // 2, 685))

    def render_menu(self, screen, rect, menu):
        """Render current menu on phone screen"""
        # Title
        title_font = pygame.font.Font(None, 28)
        prompt = menu.get('prompt', '')
        title_surface = title_font.render(prompt, True, (30, 30, 40))
        screen.blit(title_surface, (rect.x + 20, rect.y + 15))

        # Subtext
        sub_font = pygame.font.Font(None, 22)
        subtext = menu.get('subtext', '')
        sub_surface = sub_font.render(subtext, True, (80, 80, 90))
        screen.blit(sub_surface, (rect.x + 20, rect.y + 45))

        # Options or special states
        if menu.get('is_hold'):
            self.render_hold_screen(screen, rect)
        elif menu.get('is_end'):
            self.render_end_screen(screen, rect)
        else:
            # Menu options
            option_font = pygame.font.Font(None, 24)
            y_offset = 90
            for key, text, _ in menu.get('options', []):
                option_text = f"[{key}] {text}"
                option_surface = option_font.render(option_text, True, (40, 40, 50))
                screen.blit(option_surface, (rect.x + 20, rect.y + y_offset))
                y_offset += 35

    def render_hold_screen(self, screen, rect):
        """Render hold music screen"""
        # Hold message
        hold_font = pygame.font.Font(None, 32)
        dots = "." * self.dots_count
        hold_text = f"Please wait{dots}"
        hold_surface = hold_font.render(hold_text, True, (100, 100, 110))
        screen.blit(hold_surface, (rect.centerx - hold_surface.get_width() // 2, rect.y + 100))

        # Music notes animation
        note_font = pygame.font.Font(None, 36)
        notes = ["~", "~", "~"]
        for i, note in enumerate(notes):
            offset = (self.blink_timer + i * 10) % 30
            y_pos = rect.y + 150 + (offset // 10) * 5
            note_surface = note_font.render(note, True, (150, 150, 160))
            screen.blit(note_surface, (rect.x + 150 + i * 60, y_pos))

        # Wait time
        wait_font = pygame.font.Font(None, 24)
        wait_text = f"Estimated wait: {45 - (self.hold_time // 7)} minutes"
        wait_surface = wait_font.render(wait_text, True, (80, 80, 90))
        screen.blit(wait_surface, (rect.centerx - wait_surface.get_width() // 2, rect.y + 200))

        # Hint
        hint_font = pygame.font.Font(None, 20)
        hint_text = "(Press any key to hang up)"
        hint_surface = hint_font.render(hint_text, True, (120, 120, 130))
        screen.blit(hint_surface, (rect.centerx - hint_surface.get_width() // 2, rect.y + 240))

    def render_end_screen(self, screen, rect):
        """Render disconnected screen"""
        # Disconnected message
        end_font = pygame.font.Font(None, 36)
        end_text = "CALL ENDED"
        end_surface = end_font.render(end_text, True, (200, 50, 50))
        screen.blit(end_surface, (rect.centerx - end_surface.get_width() // 2, rect.y + 100))

        # Reason
        reason_font = pygame.font.Font(None, 24)
        reason_text = "Connection lost due to high call volume"
        reason_surface = reason_font.render(reason_text, True, (100, 50, 50))
        screen.blit(reason_surface, (rect.centerx - reason_surface.get_width() // 2, rect.y + 150))

        # Hint
        hint_font = pygame.font.Font(None, 22)
        hint_text = "Press any key to try again..."
        hint_surface = hint_font.render(hint_text, True, (80, 80, 90))
        screen.blit(hint_surface, (rect.centerx - hint_surface.get_width() // 2, rect.y + 200))

    def render_keypad(self, screen, phone_rect):
        """Render phone keypad"""
        keypad_start_x = phone_rect.x + 100
        keypad_start_y = phone_rect.y + 400
        button_size = 60
        spacing = 80

        keys = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['*', '0', '#']
        ]

        key_font = pygame.font.Font(None, 32)

        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                x = keypad_start_x + col_idx * spacing
                y = keypad_start_y + row_idx * 35

                # Button
                button_rect = pygame.Rect(x, y, button_size, 30)
                pygame.draw.rect(screen, (70, 70, 80), button_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 100, 110), button_rect, 1, border_radius=5)

                # Key label
                key_surface = key_font.render(key, True, (200, 200, 210))
                key_x = button_rect.centerx - key_surface.get_width() // 2
                key_y = button_rect.centery - key_surface.get_height() // 2
                screen.blit(key_surface, (key_x, key_y))

    def render_result(self, screen):
        """Render the frustration result"""
        # Result panel
        panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 350, 180, 700, 360)
        pygame.draw.rect(screen, (40, 40, 50), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 110), panel_rect, 2, border_radius=10)

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = "Phone System Navigation Failed"
        title_surface = title_font.render(title_text, True, (255, 100, 100))
        title_x = panel_rect.centerx - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, panel_rect.y + 30))

        # Summary
        summary_font = pygame.font.Font(None, 28)
        summaries = [
            f"Times disconnected: {self.loops_completed}",
            f"Menus navigated: {len(self.menu_history)}",
            "Humans reached: 0",
            "",
            "The automated system is designed to",
            "discourage callers and reduce staff workload.",
            "",
            "Many people give up after multiple attempts.",
        ]

        y = panel_rect.y + 90
        for text in summaries:
            if text:
                color = (200, 200, 210) if not text.startswith("Humans") else (255, 150, 150)
                summary_surface = summary_font.render(text, True, color)
                summary_x = panel_rect.centerx - summary_surface.get_width() // 2
                screen.blit(summary_surface, (summary_x, y))
            y += 32

        # Continue prompt
        if self.result_timer < 120:
            prompt_font = pygame.font.Font(None, 24)
            prompt_text = "Press any key to continue..."
            prompt_surface = prompt_font.render(prompt_text, True, (150, 150, 160))
            prompt_x = panel_rect.centerx - prompt_surface.get_width() // 2
            screen.blit(prompt_surface, (prompt_x, panel_rect.y + 320))

    def start(self):
        """Start the phone maze game"""
        self.active = True
        self.completed = False
        self.current_menu = 'main'
        self.menu_history = []
        self.loops_completed = 0
        self.hold_time = 0
        self.show_result = False

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)
