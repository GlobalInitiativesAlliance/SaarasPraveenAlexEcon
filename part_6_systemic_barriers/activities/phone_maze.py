"""
Phone Maze Mini-Game
Navigate automated phone system that always loops back
Demonstrates digital barriers in accessing services

UPGRADED: Realistic phone device, LCD screen with scan lines,
3D keypad buttons, signal bars, hold music visualization
"""
import pygame
import math
import time

from .systemic_visual_base import (
    SystemicUIColors, SystemicUIMetrics, SystemicVisualHelpers,
    SystemicVisualComponents, UIAnimation, systemic_visuals
)
from .systemic_particles import SystemicParticleSystem
from .systemic_feedback import SystemicFeedbackManager


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
        self.max_loops = 3

        # Hold time simulation
        self.hold_time = 0
        self.max_hold_time = 300

        # Menu definitions
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
                'subtext': "We're sorry, all circuits are busy.",
                'options': [],
                'is_end': True
            }
        }

        # Animation state
        self.blink_timer = 0
        self.dots_count = 0
        self.typewriter_progress = 0
        self.key_pressed = None
        self.key_press_timer = 0

        # Result state
        self.show_result = False
        self.result_timer = 0

        # Visual systems
        self.particles = SystemicParticleSystem()
        self.feedback = SystemicFeedbackManager()
        self.visuals = systemic_visuals

        # Phone geometry
        self.phone_rect = pygame.Rect(390, 60, 500, 600)
        self.screen_rect = pygame.Rect(420, 100, 440, 260)

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.font_lcd = pygame.font.SysFont('Monaco', 18)
            self.font_lcd_large = pygame.font.SysFont('Monaco', 22)
            self.font_body = pygame.font.SysFont('SF Pro Text', 16)
            self.font_key = pygame.font.SysFont('SF Pro Display', 24, bold=True)
            self.font_small = pygame.font.SysFont('SF Pro Text', 14)
        except:
            self.font_title = pygame.font.Font(None, 32)
            self.font_lcd = pygame.font.Font(None, 20)
            self.font_lcd_large = pygame.font.Font(None, 26)
            self.font_body = pygame.font.Font(None, 18)
            self.font_key = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 16)

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
                self.current_menu = 'disconnected'
                self.loops_completed += 1
                self.feedback.increment_loop_counter()
                self.particles.emit_disconnect(self.phone_rect.centerx, self.screen_rect.centery)
                self.feedback.add_disconnect_banner()
            return True

        # Handle end state
        if menu.get('is_end'):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if self.loops_completed >= self.max_loops:
                    self.show_result = True
                    self.result_timer = 240
                else:
                    self.current_menu = 'main'
                    self.typewriter_progress = 0
            return True

        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)

            # Check for number key press
            for option_key, _, next_menu in menu.get('options', []):
                if key_name == option_key or key_name == f'[{option_key}]':
                    self.key_pressed = option_key
                    self.key_press_timer = 10
                    self.menu_history.append(self.current_menu)
                    self.current_menu = next_menu
                    self.typewriter_progress = 0

                    # Track loops
                    if next_menu == 'main' and len(self.menu_history) > 3:
                        self.loops_completed += 1
                        self.feedback.increment_loop_counter()
                        self.particles.emit_frustration(
                            self.phone_rect.centerx,
                            self.phone_rect.y,
                            0.8
                        )
                    break

        return True

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update particles and feedback
        self.particles.update(dt)
        self.feedback.update(dt)

        # Animation updates
        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.blink_timer = 0
            self.dots_count = (self.dots_count + 1) % 4

        # Typewriter effect
        self.typewriter_progress = min(100, self.typewriter_progress + 2)

        # Key press animation
        if self.key_press_timer > 0:
            self.key_press_timer -= 1

        menu = self.menus.get(self.current_menu, {})

        # Handle hold timer
        if menu.get('is_hold'):
            self.hold_time += 1
            if self.hold_time >= self.max_hold_time:
                self.current_menu = 'disconnected'
                self.loops_completed += 1
                self.feedback.increment_loop_counter()
                self.hold_time = 0
                self.particles.emit_disconnect(self.phone_rect.centerx, self.screen_rect.centery)
                self.feedback.add_disconnect_banner()

        # Handle result timer
        if self.show_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the phone interface"""
        if not self.active:
            return

        # Dark background
        screen.fill(SystemicUIColors.BACKGROUND_DARK)

        if self.show_result:
            self._render_result(screen)
        else:
            self._render_phone(screen)
            self._render_instructions(screen)

        # Particles and feedback
        self.particles.render(screen)
        self.feedback.render(screen)

    def _render_phone(self, screen):
        """Render the phone device"""
        # Phone body shadow
        SystemicVisualHelpers.draw_shadow(screen, self.phone_rect, 15, 60,
                                         SystemicUIMetrics.RADIUS_XLARGE)

        # Phone body
        pygame.draw.rect(screen, SystemicUIColors.PHONE_BODY, self.phone_rect,
                        border_radius=SystemicUIMetrics.RADIUS_XLARGE)

        # Phone edge highlight (bevel effect)
        highlight_rect = pygame.Rect(self.phone_rect.x, self.phone_rect.y,
                                    self.phone_rect.width, self.phone_rect.height // 3)
        pygame.draw.rect(screen, SystemicUIColors.PHONE_BODY_LIGHT, highlight_rect,
                        border_top_left_radius=SystemicUIMetrics.RADIUS_XLARGE,
                        border_top_right_radius=SystemicUIMetrics.RADIUS_XLARGE)

        # Earpiece
        earpiece_rect = pygame.Rect(self.phone_rect.centerx - 40, self.phone_rect.y + 15, 80, 8)
        pygame.draw.rect(screen, (30, 30, 35), earpiece_rect, border_radius=4)

        # LCD Screen
        self._render_lcd_screen(screen)

        # Signal bars
        self.visuals.draw_signal_bars(screen, (self.screen_rect.right - 40, self.screen_rect.y + 10),
                                     signal_level=2 if not self.menus.get(self.current_menu, {}).get('is_hold') else 1)

        # Keypad
        self._render_keypad(screen)

        # Phone border
        pygame.draw.rect(screen, (70, 70, 80), self.phone_rect, 2,
                        border_radius=SystemicUIMetrics.RADIUS_XLARGE)

    def _render_lcd_screen(self, screen):
        """Render the LCD phone screen"""
        # Screen background
        pygame.draw.rect(screen, SystemicUIColors.LCD_GREEN, self.screen_rect)

        # Scanlines
        for y in range(self.screen_rect.y, self.screen_rect.bottom, 3):
            pygame.draw.line(screen, SystemicUIColors.LCD_GREEN_DARK,
                           (self.screen_rect.x, y), (self.screen_rect.right, y))

        menu = self.menus.get(self.current_menu, {})

        # Render content based on state
        if menu.get('is_hold'):
            self._render_hold_screen(screen)
        elif menu.get('is_end'):
            self._render_end_screen(screen)
        else:
            self._render_menu_screen(screen, menu)

        # Screen border (inset)
        pygame.draw.rect(screen, (100, 130, 100), self.screen_rect, 3)

    def _render_menu_screen(self, screen, menu):
        """Render menu options on LCD"""
        # Title with typewriter effect
        prompt = menu.get('prompt', '')
        visible_chars = int(len(prompt) * self.typewriter_progress / 100)
        visible_prompt = prompt[:visible_chars]

        title_text = self.font_lcd_large.render(visible_prompt, True, (30, 50, 30))
        screen.blit(title_text, (self.screen_rect.x + 15, self.screen_rect.y + 15))

        # Subtext
        if self.typewriter_progress > 30:
            subtext = menu.get('subtext', '')
            sub_text = self.font_lcd.render(subtext, True, (50, 70, 50))
            screen.blit(sub_text, (self.screen_rect.x + 15, self.screen_rect.y + 45))

        # Options
        if self.typewriter_progress > 50:
            y_offset = 85
            for key, text, _ in menu.get('options', []):
                # Truncate long text
                display_text = f"[{key}] {text}"
                if len(display_text) > 45:
                    display_text = display_text[:42] + "..."

                option_text = self.font_lcd.render(display_text, True, (40, 60, 40))
                screen.blit(option_text, (self.screen_rect.x + 15, self.screen_rect.y + y_offset))
                y_offset += 28

    def _render_hold_screen(self, screen):
        """Render hold/waiting screen"""
        # Hold message
        dots = "." * self.dots_count
        hold_text = self.font_lcd_large.render(f"Please wait{dots}", True, (30, 50, 30))
        screen.blit(hold_text, (self.screen_rect.centerx - hold_text.get_width() // 2,
                               self.screen_rect.y + 40))

        # Hold music visualization (wave)
        wave_y = self.screen_rect.y + 100
        for i in range(20):
            wave_height = int(15 * abs(math.sin(time.time() * 3 + i * 0.5)))
            bar_rect = pygame.Rect(
                self.screen_rect.x + 50 + i * 18,
                wave_y + 20 - wave_height,
                12,
                wave_height * 2
            )
            pygame.draw.rect(screen, (50, 80, 50), bar_rect, border_radius=2)

        # Wait time
        remaining = max(0, 45 - (self.hold_time // 7))
        wait_text = self.font_lcd.render(f"Est. wait: {remaining} min", True, (50, 70, 50))
        screen.blit(wait_text, (self.screen_rect.centerx - wait_text.get_width() // 2,
                               self.screen_rect.y + 170))

        # Hint
        hint_text = self.font_lcd.render("(Press any key to hang up)", True, (70, 90, 70))
        screen.blit(hint_text, (self.screen_rect.centerx - hint_text.get_width() // 2,
                               self.screen_rect.y + 210))

    def _render_end_screen(self, screen):
        """Render disconnected screen"""
        # Error icon
        icon_text = self.font_title.render("X", True, (120, 40, 40))
        screen.blit(icon_text, (self.screen_rect.centerx - icon_text.get_width() // 2,
                               self.screen_rect.y + 30))

        # Disconnected text
        end_text = self.font_lcd_large.render("CALL ENDED", True, (100, 40, 40))
        screen.blit(end_text, (self.screen_rect.centerx - end_text.get_width() // 2,
                              self.screen_rect.y + 80))

        # Reason
        reason_text = self.font_lcd.render("Connection lost - high volume", True, (80, 50, 50))
        screen.blit(reason_text, (self.screen_rect.centerx - reason_text.get_width() // 2,
                                 self.screen_rect.y + 130))

        # Hint
        hint_text = self.font_lcd.render("Press any key to redial...", True, (50, 70, 50))
        screen.blit(hint_text, (self.screen_rect.centerx - hint_text.get_width() // 2,
                               self.screen_rect.y + 200))

    def _render_keypad(self, screen):
        """Render phone keypad with 3D buttons"""
        keypad_x = self.phone_rect.x + 85
        keypad_y = self.phone_rect.y + 390
        button_width = 85
        button_height = 40
        spacing_x = 95
        spacing_y = 48

        keys = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['*', '0', '#']
        ]

        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                x = keypad_x + col_idx * spacing_x
                y = keypad_y + row_idx * spacing_y

                button_rect = pygame.Rect(x, y, button_width, button_height)
                is_pressed = (self.key_pressed == key and self.key_press_timer > 0)

                self.visuals.draw_phone_button(screen, button_rect, key, is_pressed)

    def _render_instructions(self, screen):
        """Render instruction text"""
        inst_text = self.font_body.render("Press number keys to navigate the phone menu",
                                         True, SystemicUIColors.TEXT_MUTED)
        screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 680))

    def _render_result(self, screen):
        """Render the frustration result"""
        # Result panel
        panel_width = 700
        panel_height = 380
        panel_x = (self.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.SCREEN_HEIGHT - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Shadow
        SystemicVisualHelpers.draw_shadow(screen, panel_rect, 15, 80,
                                         SystemicUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, (45, 45, 55), panel_rect,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Title
        title_text = self.font_title.render("Phone System Navigation Failed", True,
                                           SystemicUIColors.ERROR_RED)
        screen.blit(title_text, (panel_rect.centerx - title_text.get_width() // 2,
                                panel_rect.y + 30))

        # Statistics
        stats = [
            f"Times disconnected: {self.loops_completed}",
            f"Menus navigated: {len(self.menu_history)}",
            "Humans reached: 0",
        ]

        y = panel_rect.y + 90
        for stat in stats:
            color = SystemicUIColors.ERROR_RED if "0" in stat and "Humans" in stat else SystemicUIColors.TEXT_LIGHT
            stat_text = self.font_body.render(stat, True, color)
            screen.blit(stat_text, (panel_rect.centerx - stat_text.get_width() // 2, y))
            y += 35

        # Divider
        pygame.draw.line(screen, (70, 70, 80),
                        (panel_rect.x + 50, y + 10),
                        (panel_rect.right - 50, y + 10), 2)

        # Message
        messages = [
            "The automated system is designed to",
            "discourage callers and reduce staff workload.",
            "",
            "Many people give up after multiple attempts."
        ]

        y += 30
        for msg in messages:
            if msg:
                msg_text = self.font_body.render(msg, True, SystemicUIColors.TEXT_MUTED)
                screen.blit(msg_text, (panel_rect.centerx - msg_text.get_width() // 2, y))
            y += 28

        # Continue prompt
        if self.result_timer < 180:
            prompt_text = self.font_small.render("Press any key to continue...", True,
                                                SystemicUIColors.TEXT_MUTED)
            screen.blit(prompt_text, (panel_rect.centerx - prompt_text.get_width() // 2,
                                     panel_rect.bottom - 40))

        # Border
        pygame.draw.rect(screen, (80, 80, 90), panel_rect, 2,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

    def start(self):
        """Start the phone maze game"""
        self.active = True
        self.completed = False
        self.current_menu = 'main'
        self.menu_history = []
        self.loops_completed = 0
        self.hold_time = 0
        self.show_result = False
        self.typewriter_progress = 0
        self.key_pressed = None

        # Initialize loop counter
        self.feedback.init_loop_counter()

        # Clear effects
        self.particles.clear()
        self.feedback.clear()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)
