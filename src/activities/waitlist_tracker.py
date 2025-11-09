"""Waitlist Tracker - Shows the harsh reality of waiting for transitional housing"""

import pygame
import random
from src.activities.activities import Activity
from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class WaitlistTracker(Activity):
    def __init__(self, game):
        super().__init__(game.objective_manager if hasattr(game, 'objective_manager') else game)
        self.game = game
        self.phase = 0
        self.animation_timer = 0
        self.phase_complete = False
        self.waitlist_position = 47
        self.months_to_wait = "6-8"
        self.days_survived = 0
        self.survival_log = []
        
        # Visual settings
        self.bg_color = (20, 20, 25)
        self.text_color = (255, 255, 255)
        self.accent_color = (150, 200, 255)
        self.warning_color = (255, 100, 100)
        self.success_color = (100, 255, 100)

        # Create font objects
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
    def start(self):
        """Initialize the waitlist tracker"""
        super().start()  # This sets self.active = True
        self.phase = 0
        self.animation_timer = 0
        self.phase_complete = False
        self.days_survived = 0
        self.survival_log = []
        print("Starting waitlist tracker activity")
        
    def update(self, dt):
        """Update the waitlist visualization"""
        self.animation_timer += 1

        # Phase-specific updates
        if self.phase == 1:
            # Animate survival log
            if self.animation_timer % 60 == 0 and len(self.survival_log) < 8:
                self.add_survival_entry()
                if len(self.survival_log) >= 8:
                    self.phase_complete = True

    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_e:
            if self.phase_complete:
                self.advance_phase()
            elif self.phase == 1:  # Can skip survival log animation
                self.phase_complete = True
        elif key == pygame.K_ESCAPE:
            self.complete()
                    
    def add_survival_entry(self):
        """Add a survival log entry"""
        entries = [
            ("Day 3: Slept in emergency shelter - full, turned away", self.warning_color),
            ("Day 15: Sarah's couch - 3 nights max", self.accent_color),
            ("Day 28: Mike's floor - 5 roommates, no privacy", self.accent_color),
            ("Day 45: Car in Walmart parking lot", self.warning_color),
            ("Day 67: Back to shelter - got a bed this time", self.success_color),
            ("Day 92: Library during day, 24hr laundromat at night", self.warning_color),
            ("Day 134: Friend of a friend - 2 nights only", self.accent_color),
            ("Day 180: FINALLY - TLP acceptance call!", self.success_color)
        ]
        
        if len(self.survival_log) < len(entries):
            self.survival_log.append(entries[len(self.survival_log)])
            self.days_survived = 180  # Final count
            
    def advance_phase(self):
        """Move to next phase"""
        self.phase += 1
        self.phase_complete = False
        self.animation_timer = 0
        
        if self.phase >= 3:
            self.complete()
            
    def complete(self):
        """Complete the activity"""
        print("Completing waitlist tracker")
        super().complete()  # This sets self.completed = True and self.active = False
        # The parent interior will handle cleanup when it detects completed = True
        
    def draw(self, screen):
        """Render the waitlist tracker screen"""
        screen.fill(self.bg_color)
        
        if self.phase == 0:
            self.draw_waitlist_position(screen)
        elif self.phase == 1:
            self.draw_survival_timeline(screen)
        elif self.phase == 2:
            self.draw_acceptance(screen)
            
    def draw_waitlist_position(self, screen):
        """Phase 1: Show waitlist position"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Title
        title = self.font_large.render("TRANSITIONAL LIVING PROGRAM", True, self.text_color)
        title_rect = title.get_rect(center=(center_x, center_y - 200))
        screen.blit(title, title_rect)

        # Waitlist position - HUGE
        pos_text = self.font_large.render("WAITLIST POSITION", True, self.accent_color)
        pos_rect = pos_text.get_rect(center=(center_x, center_y - 100))
        screen.blit(pos_text, pos_rect)
        
        # The number - even bigger
        number_font = pygame.font.Font(None, 120)
        number_text = number_font.render(f"#{self.waitlist_position}", True, self.warning_color)
        number_rect = number_text.get_rect(center=(center_x, center_y))
        screen.blit(number_text, number_rect)
        
        # Wait time
        wait_text = self.font_medium.render(
            f"Estimated wait: {self.months_to_wait} months",
            True, self.text_color
        )
        wait_rect = wait_text.get_rect(center=(center_x, center_y + 80))
        screen.blit(wait_text, wait_rect)

        # The harsh reality
        reality_text = self.font_medium.render(
            "But you need shelter TONIGHT",
            True, self.warning_color
        )
        reality_rect = reality_text.get_rect(center=(center_x, center_y + 140))
        screen.blit(reality_text, reality_rect)

        # Continue prompt
        self.phase_complete = True
        prompt = self.font_medium.render("Press E to see survival timeline", True, self.success_color)
        prompt_rect = prompt.get_rect(center=(center_x, SCREEN_HEIGHT - 50))
        screen.blit(prompt, prompt_rect)
        
    def draw_survival_timeline(self, screen):
        """Phase 2: Show 6 months of survival"""
        center_x = SCREEN_WIDTH // 2
        start_y = 100
        
        # Title
        title = self.font_large.render("6 MONTHS OF SURVIVAL", True, self.text_color)
        title_rect = title.get_rect(center=(center_x, 50))
        screen.blit(title, title_rect)
        
        # Render survival log entries
        for i, (entry, color) in enumerate(self.survival_log):
            y_pos = start_y + (i * 60)
            
            # Fade in effect
            alpha = min(255, (self.animation_timer - i * 60) * 4)
            text_surface = self.font_medium.render(entry, True, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(center_x, y_pos))
            screen.blit(text_surface, text_rect)
            
        # Continue prompt (only after animation)
        if self.phase_complete:
            prompt = self.font_medium.render(
                "Press E to continue",
                True, self.success_color
            )
            prompt_rect = prompt.get_rect(center=(center_x, SCREEN_HEIGHT - 50))
            screen.blit(prompt, prompt_rect)
            
    def draw_acceptance(self, screen):
        """Phase 3: Finally accepted"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Success message
        success = self.font_large.render("ACCEPTANCE CALL!", True, self.success_color)
        success_rect = success.get_rect(center=(center_x, center_y - 100))
        screen.blit(success, success_rect)

        # Days survived
        days_text = self.font_medium.render(
            f"After {self.days_survived} days of homelessness",
            True, self.text_color
        )
        days_rect = days_text.get_rect(center=(center_x, center_y))
        screen.blit(days_text, days_rect)

        # Moving in message
        move_text = self.font_medium.render(
            "You can finally move into transitional housing",
            True, self.accent_color
        )
        move_rect = move_text.get_rect(center=(center_x, center_y + 50))
        screen.blit(move_text, move_rect)
        
        # Rules preview
        rules = [
            "Shared room • Curfew 10pm • Mandatory meetings",
            "But it's STABLE. It's SAFE. It's a chance."
        ]
        
        for i, rule in enumerate(rules):
            rule_text = self.font_small.render(rule, True, self.text_color)
            rule_rect = rule_text.get_rect(center=(center_x, center_y + 120 + i * 30))
            screen.blit(rule_text, rule_rect)

        # Complete
        self.phase_complete = True
        prompt = self.font_medium.render("Press E to continue", True, self.success_color)
        prompt_rect = prompt.get_rect(center=(center_x, SCREEN_HEIGHT - 50))
        screen.blit(prompt, prompt_rect)