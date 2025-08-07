import pygame
import random
import json
import os
import math
from minigames import GroceryShoppingGame, DocumentApplicationGame, RoommateAgreementGame
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
FPS = 60
UI_HEIGHT = 60  # Reduced UI height

# Colors
BACKGROUND_COLOR = (50, 50, 50)
GRID_COLOR = (70, 70, 70)
UI_BACKGROUND = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER = (150, 150, 150)
PLAYER_COLOR = (255, 0, 0)  # Red player icon
CUTSCENE_OVERLAY = (0, 0, 0, 180)  # Semi-transparent black
CUTSCENE_TEXT_BG = (20, 20, 20, 220)  # Text box background


class GameObjective:
    """Represents a game objective/mission that the player must complete"""
    def __init__(self, obj_id, title, description, target_position=None, 
                 interaction_text="Press E to interact", requires_interaction=True):
        self.id = obj_id
        self.title = title
        self.description = description
        self.target_position = target_position  # Building location for this objective
        self.interaction_text = interaction_text
        self.requires_interaction = requires_interaction
        self.completed = False
        self.active = False
        self.show_notification = True
        self.notification_timer = 0.0
        
    def activate(self):
        """Activate this objective"""
        self.active = True
        self.show_notification = True
        self.notification_timer = 3.0  # Show notification for 3 seconds
        
    def complete(self):
        """Mark objective as completed"""
        self.completed = True
        self.active = False
        
    def update(self, dt):
        """Update notification timer"""
        if self.notification_timer > 0:
            self.notification_timer -= dt


class Activity:
    """Base class for mini-game activities"""
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        
    def start(self):
        """Start the activity"""
        self.active = True
        
    def update(self, dt):
        """Update activity logic"""
        pass
        
    def draw(self, screen):
        """Draw activity UI"""
        pass
        
    def handle_key(self, key):
        """Handle keyboard input"""
        pass
        
    def handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        pass
        
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        pass
        
    def complete(self):
        """Mark activity as completed"""
        self.completed = True
        self.active = False


class TenantRightsQuiz(Activity):
    """Quiz activity for the Foster Home"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.questions = [
            {
                "question": "How much notice must a landlord give before entering your apartment?",
                "options": ["No notice needed", "24 hours", "1 week", "1 hour"],
                "correct": 1  # 24 hours
            },
            {
                "question": "Who is responsible for fixing a broken heater in winter?",
                "options": ["Tenant", "Landlord", "Nobody", "City"],
                "correct": 1  # Landlord
            },
            {
                "question": "Can a landlord raise rent in the middle of your lease?",
                "options": ["Yes, anytime", "No, not during lease", "Yes, with 30 days notice", "Only on holidays"],
                "correct": 1  # No, not during lease
            }
        ]
        self.current_question = 0
        self.selected_option = None  # Changed to None to require selection
        self.score = 0
        self.show_result = False
        self.result_timer = 0
        
        # Animation variables
        self.box_scale = 0.0
        self.fade_alpha = 0
        
        # Store submit button position for click detection
        self.submit_button_rect = None
        self.option_offsets = [0, 0, 0, 0]  # For slide-in animation
        self.result_scale = 0.0
        self.entrance_complete = False
        self.option_rects = []  # For mouse click detection
        
    def start(self):
        super().start()
        # Reset animations
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.option_offsets = [-200, -250, -300, -350]
        self.result_scale = 0.0
        self.entrance_complete = False
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Animated darkening background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, self.fade_alpha))
        screen.blit(overlay, (0, 0))
        
        # Animated quiz box
        base_width = 850
        base_height = 550
        box_width = int(base_width * self.box_scale)
        box_height = int(base_height * self.box_scale)
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        if box_width > 0 and box_height > 0:
            # Gradient background
            for i in range(5):
                color = (35 + i * 3, 35 + i * 3, 40 + i * 3)
                pygame.draw.rect(screen, color, 
                               (box_x + i, box_y + i, box_width - i*2, box_height - i*2))
            
            # Main background
            pygame.draw.rect(screen, (25, 25, 30), (box_x + 5, box_y + 5, box_width - 10, box_height - 10))
            
            # Animated border
            border_color = (255, 220, 100) if not self.show_result else ((100, 255, 100) if self.selected_option == self.questions[self.current_question]["correct"] else (255, 100, 100)) if self.current_question < len(self.questions) else (100, 255, 100)
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 4)
            
            # Corner decorations
            corner_size = 20
            for corner_x, corner_y in [(box_x, box_y), (box_x + box_width - corner_size, box_y), 
                                      (box_x, box_y + box_height - corner_size), 
                                      (box_x + box_width - corner_size, box_y + box_height - corner_size)]:
                pygame.draw.lines(screen, border_color, False, 
                                [(corner_x, corner_y + corner_size), (corner_x, corner_y), 
                                 (corner_x + corner_size, corner_y)], 3)
        
            # Title with shadow - properly aligned
            if self.entrance_complete:
                title_font = pygame.font.Font(None, 52)
                title_y = box_y + 40  # Consistent top margin
                
                # Shadow
                title_shadow = title_font.render("Tenant Rights Quiz", True, (10, 10, 10))
                screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 3, title_y + 3))
                # Main title
                title = title_font.render("Tenant Rights Quiz", True, (255, 220, 100))
                screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, title_y))
        
        if self.current_question < len(self.questions):
            # Current question
            q_data = self.questions[self.current_question]
            
            # Progress bar at top
            progress_y = box_y + 100
            progress_width = 600
            progress_x = SCREEN_WIDTH // 2 - progress_width // 2
            progress_height = 8
            
            # Progress bar background
            pygame.draw.rect(screen, (50, 50, 60), (progress_x, progress_y, progress_width, progress_height))
            # Progress bar fill
            filled_width = int(progress_width * (self.current_question + 1) / len(self.questions))
            pygame.draw.rect(screen, (100, 220, 100), (progress_x, progress_y, filled_width, progress_height))
            
            # Question number - centered
            num_font = pygame.font.Font(None, 28)
            num_text = num_font.render(f"Question {self.current_question + 1} of {len(self.questions)}", 
                                     True, (180, 180, 190))
            num_x = SCREEN_WIDTH // 2 - num_text.get_width() // 2
            screen.blit(num_text, (num_x, progress_y + 20))
            
            # Question text - centered and word-wrapped
            q_font = pygame.font.Font(None, 36)
            question_y = progress_y + 60
            
            # Word wrap for long questions
            words = q_data["question"].split()
            lines = []
            current_line = []
            max_width = box_width - 100
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if q_font.size(test_line)[0] > max_width:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw centered question lines
            for i, line in enumerate(lines):
                q_surface = q_font.render(line, True, (255, 255, 255))
                q_x = SCREEN_WIDTH // 2 - q_surface.get_width() // 2
                screen.blit(q_surface, (q_x, question_y + i * 40))
            
            # Options with mouse interaction - properly centered
            options_start_y = question_y + len(lines) * 40 + 40  # Dynamic based on question length
            option_height = 45
            option_spacing = 10
            option_width = 600  # Fixed width for all options
            option_x = SCREEN_WIDTH // 2 - option_width // 2  # Center all options
            
            self.option_rects = []  # Store option rectangles for click detection
            
            for i, option in enumerate(q_data["options"]):
                option_y = options_start_y + i * (option_height + option_spacing)
                option_rect = (option_x, option_y, option_width, option_height)
                self.option_rects.append(option_rect)
                
                # Check if hovering
                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovering = (option_x <= mouse_x <= option_x + option_width and 
                             option_y <= mouse_y <= option_y + option_height)
                
                # Draw option background with rounded corners effect
                if i == self.selected_option:
                    # Selected option
                    pygame.draw.rect(screen, (45, 45, 55), option_rect)
                    pygame.draw.rect(screen, (255, 220, 100), option_rect, 3)
                elif is_hovering and not self.show_result:
                    # Hovered option
                    pygame.draw.rect(screen, (40, 40, 50), option_rect)
                    pygame.draw.rect(screen, (150, 150, 180), option_rect, 2)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    # Normal option
                    pygame.draw.rect(screen, (35, 35, 45), option_rect)
                    pygame.draw.rect(screen, (80, 80, 90), option_rect, 1)
                
                # Option letter with circle - properly positioned
                circle_x = option_x + 30
                circle_y = option_y + option_height // 2
                circle_color = (255, 220, 100) if i == self.selected_option else (150, 150, 180) if is_hovering else (100, 100, 120)
                pygame.draw.circle(screen, circle_color, (circle_x, circle_y), 18, 2)
                
                # Letter centered in circle
                letter_font = pygame.font.Font(None, 28)
                letter = chr(65 + i)  # A, B, C, D
                letter_surface = letter_font.render(letter, True, circle_color)
                letter_x = circle_x - letter_surface.get_width() // 2
                letter_y = circle_y - letter_surface.get_height() // 2
                screen.blit(letter_surface, (letter_x, letter_y))
                
                # Option text - vertically centered
                opt_font = pygame.font.Font(None, 30)
                opt_text = opt_font.render(option, True, (255, 255, 255) if i == self.selected_option else (220, 220, 220))
                text_y = option_y + (option_height - opt_text.get_height()) // 2
                screen.blit(opt_text, (circle_x + 35, text_y))
            
            # Submit button when option is selected - properly positioned
            if self.selected_option is not None and not self.show_result:
                submit_width = 200
                submit_height = 45
                submit_x = SCREEN_WIDTH // 2 - submit_width // 2
                # Position below last option with consistent spacing
                submit_y = options_start_y + 4 * (option_height + option_spacing) + 20
                
                # Store button rect for click detection
                self.submit_button_rect = (submit_x, submit_y, submit_width, submit_height)
                
                # Check hover on submit
                submit_hover = (submit_x <= mouse_x <= submit_x + submit_width and
                              submit_y <= mouse_y <= submit_y + submit_height)
                
                button_color = (100, 200, 100) if submit_hover else (80, 150, 80)
                pygame.draw.rect(screen, button_color, (submit_x, submit_y, submit_width, submit_height))
                pygame.draw.rect(screen, (200, 200, 200), (submit_x, submit_y, submit_width, submit_height), 3)
                
                submit_font = pygame.font.Font(None, 32)
                submit_text = "Submit Answer"
                submit_surface = submit_font.render(submit_text, True, (255, 255, 255))
                text_x = submit_x + submit_width // 2 - submit_surface.get_width() // 2
                text_y = submit_y + submit_height // 2 - submit_surface.get_height() // 2
                screen.blit(submit_surface, (text_x, text_y))
                
                if submit_hover:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                # Clear submit button rect when not showing button
                self.submit_button_rect = None
            
            # Instructions
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Click an option to select • Click Submit to confirm", 
                                       True, (180, 180, 180))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 40))
            
            # Reset cursor if not hovering
            if not any(option_x <= mouse_x <= option_x + option_width and 
                      option_y - 5 <= mouse_y <= option_y - 5 + option_height 
                      for option_x, option_y, option_width, option_height in self.option_rects):
                if not (self.selected_option is not None and not self.show_result and
                       submit_x <= mouse_x <= submit_x + submit_width and
                       submit_y <= mouse_y <= submit_y + submit_height):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            # Show result if answered
            if self.show_result:
                result_y = box_y + 420
                if self.selected_option == q_data["correct"]:
                    result_text = "Correct!"
                    result_color = (100, 255, 100)
                else:
                    result_text = f"Wrong! Correct answer: {q_data['options'][q_data['correct']]}"
                    result_color = (255, 100, 100)
                
                result_font = pygame.font.Font(None, 36)
                result_surface = result_font.render(result_text, True, result_color)
                screen.blit(result_surface, (SCREEN_WIDTH // 2 - result_surface.get_width() // 2, result_y))
        else:
            # Professional completion screen
            if self.entrance_complete:
                # Calculate percentage
                percentage = int((self.score / len(self.questions)) * 100)
                
                # Title
                complete_font = pygame.font.Font(None, 56)
                complete_text = "Quiz Complete!"
                complete_color = (255, 220, 100)
                complete_surface = complete_font.render(complete_text, True, complete_color)
                screen.blit(complete_surface, (SCREEN_WIDTH // 2 - complete_surface.get_width() // 2, box_y + 120))
                
                # Score circle
                circle_x = SCREEN_WIDTH // 2
                circle_y = box_y + 220
                circle_radius = 60
                
                # Draw score circle with gradient effect
                for i in range(5):
                    color_fade = max(0, 255 - i * 30)
                    if percentage >= 100:
                        circle_color = (100, color_fade, 100)
                    elif percentage >= 67:
                        circle_color = (color_fade, color_fade, 100)
                    else:
                        circle_color = (color_fade, 100, 100)
                    pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius - i * 10, 2)
                
                # Score text in circle
                score_font = pygame.font.Font(None, 48)
                score_text = f"{self.score}/{len(self.questions)}"
                score_surface = score_font.render(score_text, True, (255, 255, 255))
                screen.blit(score_surface, (circle_x - score_surface.get_width() // 2, circle_y - 15))
                
                # Percentage below
                percent_font = pygame.font.Font(None, 36)
                percent_text = f"{percentage}%"
                percent_surface = percent_font.render(percent_text, True, (200, 200, 200))
                screen.blit(percent_surface, (circle_x - percent_surface.get_width() // 2, circle_y + 20))
                
                # Feedback message
                feedback_font = pygame.font.Font(None, 38)
                if percentage >= 100:
                    feedback = "Perfect! You know your tenant rights!"
                    feedback_color = (100, 255, 100)
                elif percentage >= 67:
                    feedback = "Good job! You understand the basics."
                    feedback_color = (100, 200, 255)
                else:
                    feedback = "Keep learning about your rights!"
                    feedback_color = (255, 200, 100)
                    
                feedback_surface = feedback_font.render(feedback, True, feedback_color)
                screen.blit(feedback_surface, (SCREEN_WIDTH // 2 - feedback_surface.get_width() // 2, box_y + 320))
                
                # Continue button
                continue_width = 200
                continue_height = 50
                continue_x = SCREEN_WIDTH // 2 - continue_width // 2
                continue_y = box_y + 380
                
                # Check hover
                mouse_x, mouse_y = pygame.mouse.get_pos()
                continue_hover = (continue_x <= mouse_x <= continue_x + continue_width and
                                continue_y <= mouse_y <= continue_y + continue_height)
                
                # Pulsing effect for button
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
                button_color = (100 + int(pulse * 50), 200 + int(pulse * 50), 100) if continue_hover else (80, 150, 80)
                
                pygame.draw.rect(screen, button_color, (continue_x, continue_y, continue_width, continue_height))
                pygame.draw.rect(screen, (200, 200, 200), (continue_x, continue_y, continue_width, continue_height), 3)
                
                cont_font = pygame.font.Font(None, 32)
                cont_text = "Continue →"
                cont_surface = cont_font.render(cont_text, True, (255, 255, 255))
                text_x = continue_x + continue_width // 2 - cont_surface.get_width() // 2
                text_y = continue_y + continue_height // 2 - cont_surface.get_height() // 2
                screen.blit(cont_surface, (text_x, text_y))
                
                if continue_hover:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for quiz"""
        super().handle_mouse_click(pos, button)
        
        if not self.active or not self.entrance_complete:
            return
            
        if button == 1:  # Left click
            mouse_x, mouse_y = pos
            
            if self.current_question >= len(self.questions):
                # Check continue button on completion screen
                box_y = SCREEN_HEIGHT // 2 - 300
                continue_x = SCREEN_WIDTH // 2 - 100
                continue_y = box_y + 380
                if (continue_x <= mouse_x <= continue_x + 200 and
                    continue_y <= mouse_y <= continue_y + 50):
                    self.complete()
                return
            
            if not self.show_result:
                # Check option clicks
                for i, (opt_x, opt_y, opt_w, opt_h) in enumerate(self.option_rects):
                    if (opt_x <= mouse_x <= opt_x + opt_w and
                        opt_y <= mouse_y <= opt_y + opt_h):
                        self.selected_option = i
                        return
                
                # Check submit button
                if self.submit_button_rect is not None:
                    submit_x, submit_y, submit_width, submit_height = self.submit_button_rect
                    if (submit_x <= mouse_x <= submit_x + submit_width and
                        submit_y <= mouse_y <= submit_y + submit_height):
                        # Check answer
                        if self.selected_option == self.questions[self.current_question]["correct"]:
                            self.score += 1
                        self.show_result = True
                        self.result_timer = 2.0
    
    def handle_key(self, key):
        if not self.active:
            return
            
        if self.current_question >= len(self.questions):
            if key == pygame.K_RETURN:
                self.complete()
            return
            
        if not self.show_result:
            if key == pygame.K_UP and self.selected_option is not None:
                self.selected_option = (self.selected_option - 1) % 4
            elif key == pygame.K_DOWN and self.selected_option is not None:
                self.selected_option = (self.selected_option + 1) % 4
            elif key == pygame.K_UP and self.selected_option is None:
                self.selected_option = 0
            elif key == pygame.K_DOWN and self.selected_option is None:
                self.selected_option = 0
            elif key == pygame.K_RETURN and self.selected_option is not None:
                # Check answer
                if self.selected_option == self.questions[self.current_question]["correct"]:
                    self.score += 1
                self.show_result = True
                self.result_timer = 2.0
        
    def update(self, dt):
        # Entrance animations
        if not self.entrance_complete:
            self.fade_alpha = min(255, self.fade_alpha + dt * 500)
            self.box_scale = min(1.0, self.box_scale + dt * 3)
            
            # Slide in options
            for i in range(4):
                target = 0
                self.option_offsets[i] += (target - self.option_offsets[i]) * dt * 8
            
            if self.box_scale >= 1.0:
                self.entrance_complete = True
                # Reset option offsets for slide-in
                self.option_offsets = [-200, -250, -300, -350]
        else:
            # Option slide-in animation
            for i in range(4):
                self.option_offsets[i] += (0 - self.option_offsets[i]) * dt * 10
        
        # Result animation
        if self.show_result:
            self.result_scale = min(1.0, self.result_scale + dt * 5)
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.current_question += 1
                self.selected_option = None  # Reset to None for mouse selection
                self.show_result = False
                self.result_scale = 0.0
                # Reset option animations for next question
                self.option_offsets = [-200, -250, -300, -350]
        
        # Pulsing continue text when quiz complete
        if self.current_question >= len(self.questions):
            self.result_scale = abs(math.sin(pygame.time.get_ticks() * 0.003))


class PackingActivity(Activity):
    """Packing mini-game for moving to apartment"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.items = ["Clothes", "Books", "Laptop", "Documents", "Photos"]
        self.packed_items = []
        self.current_item = 0
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Packing UI
        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (30, 30, 35), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pack Your Belongings", True, (255, 220, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
        
        # Progress
        progress_text = f"Packed: {len(self.packed_items)}/{len(self.items)}"
        prog_font = pygame.font.Font(None, 32)
        prog_surface = prog_font.render(progress_text, True, (200, 200, 200))
        screen.blit(prog_surface, (box_x + 40, box_y + 100))
        
        # Items list
        item_y = box_y + 150
        item_font = pygame.font.Font(None, 36)
        for i, item in enumerate(self.items):
            if item in self.packed_items:
                color = (100, 255, 100)
                prefix = "✓ "
            elif i == self.current_item:
                color = (255, 255, 100)
                prefix = "> "
            else:
                color = (200, 200, 200)
                prefix = "  "
            
            item_text = item_font.render(prefix + item, True, color)
            screen.blit(item_text, (box_x + 60, item_y))
            item_y += 40
            
        # Instructions
        if len(self.packed_items) < len(self.items):
            inst_text = "Press SPACE to pack each item"
        else:
            inst_text = "All packed! Press ENTER to continue"
        
        inst_font = pygame.font.Font(None, 28)
        inst_surface = inst_font.render(inst_text, True, (255, 255, 255))
        screen.blit(inst_surface, (SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, box_y + box_height - 50))
    
    def handle_key(self, key):
        if not self.active:
            return
            
        if key == pygame.K_SPACE and self.current_item < len(self.items):
            if self.items[self.current_item] not in self.packed_items:
                self.packed_items.append(self.items[self.current_item])
                self.current_item = min(self.current_item + 1, len(self.items) - 1)
        elif key == pygame.K_RETURN and len(self.packed_items) == len(self.items):
            self.complete()


class LifeSkillsWorkshop(Activity):
    """Life skills workshop at community center"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0  # 0 = intro, 1-3 = tips, 4 = complete
        self.tips_learned = []
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Workshop box
        box_width = 800
        box_height = 600
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 150, 200), (box_x, box_y, box_width, box_height), 3)
        
        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 28)
        
        # Title
        title = title_font.render("Life Skills Workshop", True, (150, 200, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
        
        if self.stage == 0:
            # Introduction
            lines = [
                "Welcome to the Life Skills Workshop!",
                "",
                "Today you'll learn essential skills for",
                "independent living in your new apartment.",
                "",
                "Topics covered:",
                "• Budgeting & Money Management",
                "• Cooking & Meal Planning", 
                "• Time Management",
                "",
                "Click or press SPACE to begin"
            ]
            
            y_offset = box_y + 120
            for line in lines:
                if line.startswith("•"):
                    color = (200, 220, 255)
                    font = small_font
                else:
                    color = (255, 255, 255)
                    font = text_font if line else small_font
                    
                text = font.render(line, True, color)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 35
                
        elif self.stage <= 3:
            # Learning tips
            tips = [
                {
                    "title": "Budgeting Basics",
                    "icon": "$",
                    "points": [
                        "Track ALL expenses, even small ones",
                        "Follow the 50/30/20 rule:",
                        "  50% needs, 30% wants, 20% savings",
                        "Use apps or spreadsheets to track spending",
                        "Set up automatic savings transfers"
                    ]
                },
                {
                    "title": "Cooking & Meal Planning",
                    "icon": "🍳",
                    "points": [
                        "Plan meals for the week ahead",
                        "Make a grocery list and stick to it",
                        "Learn 5-10 simple, healthy recipes",
                        "Batch cook and freeze portions",
                        "Buy generic brands to save money"
                    ]
                },
                {
                    "title": "Time Management",
                    "icon": "⏰",
                    "points": [
                        "Use a calendar for appointments",
                        "Set multiple alarms for important tasks",
                        "Prepare clothes/lunch the night before",
                        "Break big tasks into smaller steps",
                        "Build in buffer time between activities"
                    ]
                }
            ]
            
            current_tip = tips[self.stage - 1]
            
            # Tip header
            header_font = pygame.font.Font(None, 40)
            header = header_font.render(current_tip["title"], True, (255, 220, 100))
            screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, box_y + 100))
            
            # Tip points
            y_offset = box_y + 160
            for point in current_tip["points"]:
                if point.startswith("  "):
                    color = (180, 180, 200)
                    indent = 40
                else:
                    color = (255, 255, 255)
                    indent = 0
                    
                text = small_font.render(point.strip(), True, color)
                screen.blit(text, (box_x + 100 + indent, y_offset))
                y_offset += 35
            
            # Navigation
            nav_text = f"Tip {self.stage} of 3"
            nav = small_font.render(nav_text, True, (150, 150, 150))
            screen.blit(nav, (SCREEN_WIDTH // 2 - nav.get_width() // 2, box_y + 450))
            
            cont_text = text_font.render("Click or press SPACE to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 500))
            
        else:
            # Completion
            lines = [
                "Workshop Complete!",
                "",
                "You've learned important life skills:",
                "✓ Budgeting & Money Management",
                "✓ Cooking & Meal Planning",
                "✓ Time Management",
                "",
                "Remember: Practice makes perfect!",
                "Don't be afraid to ask for help.",
                "",
                "Click or press ENTER to continue"
            ]
            
            y_offset = box_y + 120
            for line in lines:
                if line.startswith("✓"):
                    color = (100, 255, 100)
                elif line == "Workshop Complete!":
                    color = (100, 255, 100)
                    font = title_font
                else:
                    color = (255, 255, 255)
                    font = text_font
                    
                if line != "Workshop Complete!":
                    text = text_font.render(line, True, color)
                else:
                    text = font.render(line, True, color)
                    
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40 if line == "Workshop Complete!" else 35
                
    def handle_key(self, key):
        if not self.active:
            return
            
        if self.stage < 3 and key == pygame.K_SPACE:
            self.stage += 1
        elif self.stage == 3 and key == pygame.K_SPACE:
            self.stage = 4
        elif self.stage == 4 and key == pygame.K_RETURN:
            self.complete()
            
    def handle_mouse_click(self, mouse_pos, button=1):
        """Handle mouse clicks for workshop"""
        if not self.active:
            return
            
        if self.stage < 4:
            self.stage += 1
        else:
            self.complete()


class EmergencyNoticeActivity(Activity):
    """Show emergency notices about roommate leaving"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0  # 0: roommate note, 1: 3-day notice, 2: utility notice
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Notice display
        box_width = 700
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        if self.stage == 0:
            # Roommate's note
            pygame.draw.rect(screen, (50, 50, 50), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_width, box_height), 3)
            
            title_font = pygame.font.Font(None, 42)
            title = title_font.render("Note from Roommate", True, (255, 100, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
            
            note_font = pygame.font.Font(None, 28)
            lines = [
                "Sorry, I had to leave suddenly.",
                "Family emergency back home.",
                "I can't pay my half of rent or utilities.",
                "Good luck.",
                "",
                "- Your former roommate"
            ]
            
            y_offset = box_y + 100
            for line in lines:
                text = note_font.render(line, True, (255, 255, 255))
                screen.blit(text, (box_x + 50, y_offset))
                y_offset += 35
                
        elif self.stage == 1:
            # 3-day notice
            pygame.draw.rect(screen, (80, 20, 20), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (255, 50, 50), (box_x, box_y, box_width, box_height), 3)
            
            title_font = pygame.font.Font(None, 48)
            title = title_font.render("3-DAY NOTICE TO PAY OR QUIT", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
            
            notice_font = pygame.font.Font(None, 26)
            lines = [
                "You are hereby notified that rent in the amount of",
                "$1,200 is now due and payable.",
                "",
                "You are required to pay said rent in full within",
                "THREE (3) days or quit and deliver up the premises.",
                "",
                "Failure to comply will result in eviction proceedings."
            ]
            
            y_offset = box_y + 100
            for line in lines:
                text = notice_font.render(line, True, (255, 255, 255))
                screen.blit(text, (box_x + 50, y_offset))
                y_offset += 30
                
        elif self.stage == 2:
            # Utility shutoff
            pygame.draw.rect(screen, (80, 80, 20), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (255, 255, 100), (box_x, box_y, box_width, box_height), 3)
            
            title_font = pygame.font.Font(None, 42)
            title = title_font.render("UTILITY SHUTOFF NOTICE", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
            
            notice_font = pygame.font.Font(None, 28)
            lines = [
                "Your utility services will be disconnected",
                "due to non-payment.",
                "",
                "Amount due: $150",
                "Plus reconnection fee: $75",
                "",
                "Pay immediately to avoid service interruption."
            ]
            
            y_offset = box_y + 100
            for line in lines:
                text = notice_font.render(line, True, (255, 255, 255))
                screen.blit(text, (box_x + 50, y_offset))
                y_offset += 30
        
        # Instructions
        inst_font = pygame.font.Font(None, 28)
        inst_text = inst_font.render("Press SPACE to continue", True, (255, 255, 255))
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 50))
    
    def handle_key(self, key):
        if not self.active:
            return
            
        if key == pygame.K_SPACE:
            self.stage += 1
            if self.stage > 2:
                self.complete()


class DocumentChecklistActivity(Activity):
    """Housing Services document checklist"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.documents = {
            "Foster Care Verification": False,
            "Income Proof": False,
            "TLP Agreement": False
        }
        self.all_checked = False
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Checklist box
        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (30, 30, 35), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 200, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Required Documents", True, (100, 200, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
        
        # Document list
        doc_font = pygame.font.Font(None, 32)
        y_offset = box_y + 120
        
        for i, (doc_name, is_checked) in enumerate(self.documents.items()):
            # Checkbox
            checkbox_x = box_x + 60
            checkbox_y = y_offset - 5
            checkbox_size = 30
            
            pygame.draw.rect(screen, (255, 255, 255), 
                           (checkbox_x, checkbox_y, checkbox_size, checkbox_size), 2)
            
            if is_checked:
                # Draw checkmark
                pygame.draw.line(screen, (100, 255, 100), 
                               (checkbox_x + 5, checkbox_y + 15),
                               (checkbox_x + 12, checkbox_y + 22), 3)
                pygame.draw.line(screen, (100, 255, 100),
                               (checkbox_x + 12, checkbox_y + 22),
                               (checkbox_x + 25, checkbox_y + 8), 3)
            
            # Document name
            color = (100, 255, 100) if is_checked else (255, 255, 255)
            text = doc_font.render(f"{i+1}. {doc_name}", True, color)
            screen.blit(text, (checkbox_x + 50, y_offset))
            y_offset += 60
        
        # Instructions
        if not self.all_checked:
            inst_text = "Press 1, 2, or 3 to check documents"
        else:
            inst_text = "All documents verified! Press ENTER to continue"
            
        inst_font = pygame.font.Font(None, 28)
        inst_surface = inst_font.render(inst_text, True, (255, 255, 255))
        screen.blit(inst_surface, (SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, box_y + box_height - 50))
    
    def handle_key(self, key):
        if not self.active:
            return
            
        doc_keys = list(self.documents.keys())
        
        if key == pygame.K_1 and len(doc_keys) > 0:
            self.documents[doc_keys[0]] = True
        elif key == pygame.K_2 and len(doc_keys) > 1:
            self.documents[doc_keys[1]] = True
        elif key == pygame.K_3 and len(doc_keys) > 2:
            self.documents[doc_keys[2]] = True
            
        # Check if all documents are checked
        self.all_checked = all(self.documents.values())
        
        if self.all_checked and key == pygame.K_RETURN:
            self.complete()


class WorkplaceQuiz(Activity):
    """Quiz about what to do when getting fired"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.questions = [
            {
                "question": "What should you do FIRST if you're fired?",
                "options": ["Leave immediately", "Ask for the reason in writing", "Argue with your boss", "Call the police"],
                "correct": 1  # Ask for the reason in writing
            },
            {
                "question": "Are you entitled to your final paycheck?",
                "options": ["No, you were fired", "Yes, for all hours worked", "Only if you quit", "Depends on the boss"],
                "correct": 1  # Yes, for all hours worked
            },
            {
                "question": "What benefits might you qualify for after being fired?",
                "options": ["Nothing", "Unemployment insurance", "Free housing", "Company car"],
                "correct": 1  # Unemployment insurance
            }
        ]
        self.current_question = 0
        self.selected_option = None
        self.score = 0
        self.show_result = False
        self.result_timer = 0
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.entrance_complete = False
        
    def start(self):
        super().start()
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.entrance_complete = False
        
    def update(self, dt):
        if not self.active:
            return
            
        # Entrance animation
        if self.fade_alpha < 200:
            self.fade_alpha = min(200, self.fade_alpha + dt * 400)
        if self.box_scale < 1.0:
            self.box_scale = min(1.0, self.box_scale + dt * 3)
        if self.box_scale >= 1.0 and self.fade_alpha >= 200:
            self.entrance_complete = True
            
        if self.show_result:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.show_result = False
                self.current_question += 1
                self.selected_option = None
                
                if self.current_question >= len(self.questions):
                    self.complete()
                    
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, self.fade_alpha))
        screen.blit(overlay, (0, 0))
        
        # Quiz box
        base_width = 850
        base_height = 550
        box_width = int(base_width * self.box_scale)
        box_height = int(base_height * self.box_scale)
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        if box_width > 0 and box_height > 0:
            pygame.draw.rect(screen, (25, 25, 30), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (200, 100, 100), (box_x, box_y, box_width, box_height), 4)
            
        if self.entrance_complete:
            # Title
            title_font = pygame.font.Font(None, 48)
            title = title_font.render("Employment Rights Quiz", True, (200, 100, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
            
            if self.current_question < len(self.questions):
                question = self.questions[self.current_question]
                
                # Question
                q_font = pygame.font.Font(None, 32)
                q_text = q_font.render(question["question"], True, (255, 255, 255))
                screen.blit(q_text, (SCREEN_WIDTH // 2 - q_text.get_width() // 2, box_y + 120))
                
                # Options with clickable areas
                opt_font = pygame.font.Font(None, 28)
                y_offset = box_y + 200
                
                # Store option rectangles for mouse detection
                self.option_rects = []
                
                for i, option in enumerate(question["options"]):
                    # Create clickable rectangle
                    option_rect = pygame.Rect(box_x + 80, y_offset - 10, box_width - 160, 45)
                    self.option_rects.append(option_rect)
                    
                    # Hover effect
                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering = option_rect.collidepoint(mouse_pos) and not self.show_result
                    
                    # Draw option background
                    if is_hovering:
                        pygame.draw.rect(screen, (40, 40, 50), option_rect, border_radius=5)
                        pygame.draw.rect(screen, (100, 100, 120), option_rect, 2, border_radius=5)
                    
                    # Color logic
                    color = (255, 255, 255)
                    if self.selected_option == i:
                        color = (255, 220, 100)
                    if self.show_result:
                        if i == question["correct"]:
                            color = (100, 255, 100)
                        elif i == self.selected_option:
                            color = (255, 100, 100)
                    
                    # Draw option text
                    opt_text = opt_font.render(f"{i+1}. {option}", True, color)
                    screen.blit(opt_text, (box_x + 100, y_offset))
                    y_offset += 50
                    
                # Submit button and instructions
                if not self.show_result:
                    # Submit button
                    submit_width = 150
                    submit_height = 40
                    submit_x = SCREEN_WIDTH // 2 - submit_width // 2
                    submit_y = box_y + box_height - 80
                    self.submit_rect = pygame.Rect(submit_x, submit_y, submit_width, submit_height)
                    
                    # Button appearance
                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering_submit = self.submit_rect.collidepoint(mouse_pos) and self.selected_option is not None
                    
                    button_color = (100, 150, 255) if self.selected_option is not None else (80, 80, 80)
                    if is_hovering_submit:
                        button_color = (120, 170, 255)
                    
                    pygame.draw.rect(screen, button_color, self.submit_rect, border_radius=5)
                    pygame.draw.rect(screen, (255, 255, 255), self.submit_rect, 2, border_radius=5)
                    
                    submit_font = pygame.font.Font(None, 28)
                    submit_text = submit_font.render("Submit", True, (255, 255, 255))
                    text_rect = submit_text.get_rect(center=self.submit_rect.center)
                    screen.blit(submit_text, text_rect)
                    
                    # Instructions
                    inst_font = pygame.font.Font(None, 20)
                    inst_text = inst_font.render("Click an option or press 1-4 to select", True, (180, 180, 180))
                    screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 25))
            else:
                # Show final score
                score_font = pygame.font.Font(None, 48)
                score_text = score_font.render(f"Score: {self.score}/{len(self.questions)}", True, (100, 255, 100))
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, box_y + 180))
                
                # Continue button
                continue_width = 200
                continue_height = 50
                continue_x = SCREEN_WIDTH // 2 - continue_width // 2
                continue_y = box_y + 280
                self.continue_rect = pygame.Rect(continue_x, continue_y, continue_width, continue_height)
                
                # Button appearance
                mouse_pos = pygame.mouse.get_pos()
                is_hovering = self.continue_rect.collidepoint(mouse_pos)
                
                button_color = (120, 170, 255) if is_hovering else (100, 150, 255)
                pygame.draw.rect(screen, button_color, self.continue_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 255, 255), self.continue_rect, 2, border_radius=5)
                
                button_font = pygame.font.Font(None, 32)
                button_text = button_font.render("Continue", True, (255, 255, 255))
                text_rect = button_text.get_rect(center=self.continue_rect.center)
                screen.blit(button_text, text_rect)
                
                # Instructions
                inst_font = pygame.font.Font(None, 20)
                inst_text = inst_font.render("Click Continue or press ENTER", True, (180, 180, 180))
                screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 350))
                
    def handle_key(self, key):
        if not self.active or not self.entrance_complete:
            return
            
        if self.current_question < len(self.questions) and not self.show_result:
            if key >= pygame.K_1 and key <= pygame.K_4:
                option_index = key - pygame.K_1
                if option_index < len(self.questions[self.current_question]["options"]):
                    self.selected_option = option_index
                    
            elif key == pygame.K_RETURN and self.selected_option is not None:
                # Check answer
                if self.selected_option == self.questions[self.current_question]["correct"]:
                    self.score += 1
                self.show_result = True
                self.result_timer = 2.0
                
        elif self.current_question >= len(self.questions) and key == pygame.K_RETURN:
            self.complete()
            
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or not self.entrance_complete or button != 1:
            return
            
        if self.current_question < len(self.questions) and not self.show_result:
            # Check option clicks
            for i, rect in enumerate(getattr(self, 'option_rects', [])):
                if rect.collidepoint(pos):
                    self.selected_option = i
                    return
                    
            # Check submit button
            if hasattr(self, 'submit_rect') and self.submit_rect.collidepoint(pos):
                if self.selected_option is not None:
                    # Check answer
                    if self.selected_option == self.questions[self.current_question]["correct"]:
                        self.score += 1
                    self.show_result = True
                    self.result_timer = 2.0
                    
        elif self.current_question >= len(self.questions):
            # Check continue button
            if hasattr(self, 'continue_rect') and self.continue_rect.collidepoint(pos):
                self.complete()


class JobApplicationActivity(Activity):
    """Simple job application for pizza shop"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0  # 0 = intro, 1 = form, 2 = hired
        self.form_data = {
            "name": "",
            "experience": "",
            "availability": ""
        }
        self.current_field = 0
        self.fields = ["name", "experience", "availability"]
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Application box
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 45), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 150, 255), (box_x, box_y, box_width, box_height), 3)
        
        title_font = pygame.font.Font(None, 48)
        
        if self.stage == 0:
            # Introduction
            title = title_font.render("Tony's Pizza", True, (255, 200, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 50))
            
            text_font = pygame.font.Font(None, 32)
            lines = [
                "We're hiring!",
                "Starting pay: $17.04/hour",
                "Flexible hours available"
            ]
            
            y_offset = box_y + 150
            for line in lines:
                text = text_font.render(line, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40
                
            # Apply button
            button_width = 200
            button_height = 50
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_y = box_y + 320
            self.apply_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Button appearance
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = self.apply_rect.collidepoint(mouse_pos)
            
            button_color = (120, 170, 255) if is_hovering else (100, 150, 255)
            pygame.draw.rect(screen, button_color, self.apply_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), self.apply_rect, 2, border_radius=5)
            
            button_font = pygame.font.Font(None, 32)
            button_text = button_font.render("Apply Now", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=self.apply_rect.center)
            screen.blit(button_text, text_rect)
            
            # Instructions
            inst_font = pygame.font.Font(None, 20)
            inst_text = inst_font.render("Click Apply or press ENTER", True, (180, 180, 180))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 390))
                
        elif self.stage == 1:
            # Application form
            title = title_font.render("Job Application", True, (100, 150, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
            
            form_font = pygame.font.Font(None, 28)
            y_offset = box_y + 120
            
            prompts = {
                "name": "Your Name:",
                "experience": "Any food service experience? (yes/no):",
                "availability": "Can you work evenings? (yes/no):"
            }
            
            for i, field in enumerate(self.fields):
                color = (255, 255, 100) if i == self.current_field else (200, 200, 200)
                
                # Prompt
                prompt = form_font.render(prompts[field], True, color)
                screen.blit(prompt, (box_x + 50, y_offset))
                y_offset += 30
                
                # Value
                value = self.form_data[field] + ("_" if i == self.current_field else "")
                value_text = form_font.render(value, True, (255, 255, 255))
                screen.blit(value_text, (box_x + 50, y_offset))
                y_offset += 50
                
            # Instructions
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Type to fill fields, TAB to next field, ENTER to submit", True, (150, 150, 150))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 40))
            
        elif self.stage == 2:
            # Hired!
            title = title_font.render("Congratulations!", True, (100, 255, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 100))
            
            text_font = pygame.font.Font(None, 32)
            lines = [
                "You're hired!",
                "Start tomorrow at 3:00 PM",
                "Uniform will be provided"
            ]
            
            y_offset = box_y + 200
            for line in lines:
                text = text_font.render(line, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40
                
            # Continue button
            button_width = 200
            button_height = 50
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_y = box_y + 350
            self.continue_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Button appearance
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = self.continue_rect.collidepoint(mouse_pos)
            
            button_color = (120, 255, 120) if is_hovering else (100, 255, 100)
            pygame.draw.rect(screen, button_color, self.continue_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), self.continue_rect, 2, border_radius=5)
            
            button_font = pygame.font.Font(None, 32)
            button_text = button_font.render("Continue", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=self.continue_rect.center)
            screen.blit(button_text, text_rect)
            
            # Instructions
            inst_font = pygame.font.Font(None, 20)
            inst_text = inst_font.render("Click Continue or press ENTER", True, (180, 180, 180))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 420))
                
    def handle_key(self, key):
        if not self.active:
            return
            
        if self.stage == 0:
            if key == pygame.K_RETURN:
                self.stage = 1
                
        elif self.stage == 1:
            if key == pygame.K_TAB:
                self.current_field = (self.current_field + 1) % len(self.fields)
            elif key == pygame.K_RETURN:
                # Simple validation - just check if all fields have some value
                if all(self.form_data[field] for field in self.fields):
                    self.stage = 2
            elif key == pygame.K_BACKSPACE:
                field = self.fields[self.current_field]
                if self.form_data[field]:
                    self.form_data[field] = self.form_data[field][:-1]
            elif key >= pygame.K_a and key <= pygame.K_z:
                field = self.fields[self.current_field]
                self.form_data[field] += chr(key)
            elif key == pygame.K_SPACE:
                field = self.fields[self.current_field]
                self.form_data[field] += " "
                
        elif self.stage == 2:
            if key == pygame.K_RETURN:
                self.complete()
                
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return
            
        if self.stage == 0:
            # Check apply button
            if hasattr(self, 'apply_rect') and self.apply_rect.collidepoint(pos):
                self.stage = 1
                
        elif self.stage == 2:
            # Check continue button
            if hasattr(self, 'continue_rect') and self.continue_rect.collidepoint(pos):
                self.complete()


class TransitionScene(Activity):
    """Transition from Part 1 to Part 2"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.fade_alpha = 0
        self.stage = 0  # 0 = fade in, 1 = show text, 2 = fade out
        self.timer = 0
        
    def update(self, dt):
        if not self.active:
            return
            
        self.timer += dt
        
        if self.stage == 0:
            # Fade in
            self.fade_alpha = min(255, self.timer * 200)
            if self.fade_alpha >= 255:
                self.stage = 1
                self.timer = 0
        elif self.stage == 1:
            # Show text for 3 seconds
            if self.timer > 3.0:
                self.stage = 2
                self.timer = 0
        elif self.stage == 2:
            # Fade out
            self.fade_alpha = max(0, 255 - self.timer * 200)
            if self.fade_alpha <= 0:
                self.complete()
                
    def draw(self, screen):
        if not self.active:
            return
            
        # Black background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(int(self.fade_alpha))
        screen.blit(overlay, (0, 0))
        
        if self.stage == 1:
            # Show transition text
            title_font = pygame.font.Font(None, 64)
            text_font = pygame.font.Font(None, 36)
            
            title = title_font.render("Part 2: Housing Crisis", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            
            lines = [
                "Without a job, you can't afford rent.",
                "Your housing situation becomes critical.",
                "Now you must navigate the challenges",
                "of finding stable housing..."
            ]
            
            y_offset = SCREEN_HEIGHT // 2
            for line in lines:
                text = text_font.render(line, True, (200, 200, 200))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40
                
    def handle_key(self, key):
        # Allow skipping with any key
        if self.stage == 1:
            self.stage = 2
            self.timer = 0


class SchoolEmergencyScene(Activity):
    """Scene showing school emergency"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Emergency box
        box_width = 700
        box_height = 350
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (60, 20, 20), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 100, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Flashing effect
        flash = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 50 + 205
        
        title_font = pygame.font.Font(None, 56)
        text_font = pygame.font.Font(None, 32)
        
        # Title with flash effect
        title = title_font.render("EMERGENCY!", True, (flash, 50, 50))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 40))
        
        lines = [
            "There's been an emergency at school!",
            "You need to stay and help.",
            "",
            "Time passes...",
            "",
            "Oh no! You're late for work!",
            "",
            "Press ENTER to rush to work"
        ]
        
        y_offset = box_y + 120
        for line in lines:
            if line == "Oh no! You're late for work!":
                color = (255, 150, 150)
            elif line == "Time passes...":
                color = (150, 150, 150)
            else:
                color = (255, 255, 255)
                
            text = text_font.render(line, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 30
            
    def handle_key(self, key):
        if not self.active:
            return
            
        if key == pygame.K_RETURN:
            self.complete()
            
    def handle_mouse_click(self, mouse_pos, button=1):
        """Handle mouse clicks for emergency scene"""
        if not self.active:
            return
            
        # Any click continues
        self.complete()


class FiringScene(Activity):
    """Scene where player gets fired"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0  # 0 = manager speech, 1 = fired, 2 = paycheck info
        self.text_timer = 0
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(220)
        screen.blit(overlay, (0, 0))
        
        # Scene box
        box_width = 800
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 20, 20), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (200, 50, 50), (box_x, box_y, box_width, box_height), 3)
        
        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 32)
        
        if self.stage == 0:
            # Manager speech
            title = title_font.render("Manager's Office", True, (255, 100, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
            
            lines = [
                "\"You were late to work today!\"",
                "\"This is unacceptable behavior.\"",
                "\"I'm sorry, but we have to let you go.\"",
                "",
                "Press SPACE to continue"
            ]
            
            y_offset = box_y + 120
            for line in lines:
                color = (255, 200, 200) if line.startswith('"') else (200, 200, 200)
                text = text_font.render(line, True, color)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40
                
        elif self.stage == 1:
            # Fired notice
            title = title_font.render("YOU'RE FIRED!", True, (255, 50, 50))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 100))
            
            info_font = pygame.font.Font(None, 28)
            info_text = info_font.render("Employment terminated immediately", True, (255, 150, 150))
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, box_y + 180))
            
            cont_text = text_font.render("Press SPACE to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 300))
            
        elif self.stage == 2:
            # Paycheck info
            title = title_font.render("Final Paycheck", True, (100, 200, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 50))
            
            lines = [
                "You worked 4 hours yesterday",
                "Rate: $17.81/hour",
                "Total earned: $71.24",
                "",
                "Collect your pay at the front desk",
                "",
                "Press ENTER to continue"
            ]
            
            y_offset = box_y + 120
            for line in lines:
                text = text_font.render(line, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 35
                
    def handle_key(self, key):
        if not self.active:
            return
            
        if self.stage < 2 and key == pygame.K_SPACE:
            self.stage += 1
        elif self.stage == 2 and key == pygame.K_RETURN:
            self.complete()
            
    def handle_mouse_click(self, mouse_pos, button=1):
        """Handle mouse clicks for firing scene"""
        if not self.active:
            return
            
        # Any click advances the stage
        if self.stage < 2:
            self.stage += 1
        else:
            self.complete()


class PizzaMakingGame(Activity):
    """Simple pizza making mini-game"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.pizzas_made = 0
        self.target_pizzas = 3
        self.current_pizza = None
        self.timer = 0
        self.game_timer = 60.0  # 1 minute
        self.oven_timer = 0
        self.pizza_in_oven = False
        
    def start(self):
        super().start()
        self.new_pizza()
        
    def new_pizza(self):
        """Create a new pizza order"""
        toppings = ["Pepperoni", "Mushrooms", "Olives", "Peppers"]
        self.current_pizza = {
            "required_toppings": random.sample(toppings, random.randint(1, 3)),
            "added_toppings": [],
            "stage": "topping"  # topping, oven, done
        }
        
    def update(self, dt):
        if not self.active:
            return
            
        self.game_timer -= dt
        
        if self.pizza_in_oven:
            self.oven_timer -= dt
            if self.oven_timer <= 0:
                self.pizza_in_oven = False
                self.current_pizza["stage"] = "done"
                
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Game box
        box_width = 800
        box_height = 600
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (50, 40, 30), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 150, 50), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pizza Making", True, (255, 200, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 20))
        
        # Timer and score
        info_font = pygame.font.Font(None, 32)
        timer_text = info_font.render(f"Time: {int(self.game_timer)}s", True, (255, 255, 255))
        screen.blit(timer_text, (box_x + 20, box_y + 80))
        
        score_text = info_font.render(f"Pizzas: {self.pizzas_made}/{self.target_pizzas}", True, (255, 255, 255))
        screen.blit(score_text, (box_x + box_width - 200, box_y + 80))
        
        if self.current_pizza:
            # Pizza workspace
            pizza_y = box_y + 150
            
            # Draw pizza base
            pizza_center_x = SCREEN_WIDTH // 2
            pizza_center_y = pizza_y + 100
            pygame.draw.circle(screen, (255, 220, 150), (pizza_center_x, pizza_center_y), 80)
            pygame.draw.circle(screen, (200, 100, 50), (pizza_center_x, pizza_center_y), 80, 3)
            
            # Show required toppings
            req_font = pygame.font.Font(None, 28)
            req_text = req_font.render("Order: " + ", ".join(self.current_pizza["required_toppings"]), True, (255, 255, 255))
            screen.blit(req_text, (SCREEN_WIDTH // 2 - req_text.get_width() // 2, pizza_y - 30))
            
            # Show added toppings on pizza
            for topping in self.current_pizza["added_toppings"]:
                # Simple representation
                if topping == "Pepperoni":
                    for _ in range(5):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.circle(screen, (200, 50, 50), (x, y), 8)
                elif topping == "Mushrooms":
                    for _ in range(4):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.circle(screen, (150, 100, 50), (x, y), 6)
                elif topping == "Olives":
                    for _ in range(6):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.circle(screen, (50, 50, 50), (x, y), 4)
                elif topping == "Peppers":
                    for _ in range(4):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.rect(screen, (50, 200, 50), (x-5, y-5, 10, 10))
            
            # Stage-specific UI
            if self.current_pizza["stage"] == "topping":
                # Topping buttons
                button_y = pizza_y + 250
                toppings = ["Pepperoni", "Mushrooms", "Olives", "Peppers"]
                self.topping_rects = []
                
                for i, topping in enumerate(toppings):
                    button_x = box_x + 100 + i * 150
                    button_rect = pygame.Rect(button_x, button_y, 120, 40)
                    self.topping_rects.append((button_rect, topping))
                    
                    # Hover effect
                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering = button_rect.collidepoint(mouse_pos)
                    
                    color = (100, 100, 100)
                    if topping in self.current_pizza["added_toppings"]:
                        color = (100, 200, 100)
                    elif is_hovering:
                        color = (120, 120, 120)
                        
                    pygame.draw.rect(screen, color, button_rect, border_radius=5)
                    pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, border_radius=5)
                    
                    button_text = req_font.render(f"{i+1}. {topping}", True, (255, 255, 255))
                    screen.blit(button_text, (button_x + 10, button_y + 10))
                
                # Bake button
                bake_width = 150
                bake_height = 45
                bake_x = SCREEN_WIDTH // 2 - bake_width // 2
                bake_y = button_y + 70
                self.bake_rect = pygame.Rect(bake_x, bake_y, bake_width, bake_height)
                
                # Bake button appearance
                is_hovering_bake = self.bake_rect.collidepoint(mouse_pos)
                bake_color = (255, 150, 50) if is_hovering_bake else (255, 120, 20)
                
                pygame.draw.rect(screen, bake_color, self.bake_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 255, 255), self.bake_rect, 2, border_radius=5)
                
                bake_font = pygame.font.Font(None, 32)
                bake_text = bake_font.render("Bake Pizza", True, (255, 255, 255))
                text_rect = bake_text.get_rect(center=self.bake_rect.center)
                screen.blit(bake_text, text_rect)
                    
                # Instructions
                inst_text = req_font.render("Click toppings or press 1-4, click Bake or press SPACE", True, (200, 200, 200))
                screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, button_y + 130))
                
            elif self.pizza_in_oven:
                # Oven animation
                oven_text = info_font.render(f"Baking... {int(self.oven_timer)}s", True, (255, 150, 50))
                screen.blit(oven_text, (SCREEN_WIDTH // 2 - oven_text.get_width() // 2, pizza_y + 250))
                
            elif self.current_pizza["stage"] == "done":
                # Pizza done
                done_text = info_font.render("Pizza ready! Press ENTER to serve", True, (100, 255, 100))
                screen.blit(done_text, (SCREEN_WIDTH // 2 - done_text.get_width() // 2, pizza_y + 250))
                
        # Check if time's up or target reached
        if self.game_timer <= 0 or self.pizzas_made >= self.target_pizzas:
            result_font = pygame.font.Font(None, 48)
            if self.pizzas_made >= self.target_pizzas:
                result_text = result_font.render("Great job!", True, (100, 255, 100))
            else:
                result_text = result_font.render("Time's up!", True, (255, 100, 100))
                
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, box_y + 400))
            
            cont_font = pygame.font.Font(None, 28)
            cont_text = cont_font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 450))
            
    def handle_key(self, key):
        if not self.active:
            return
            
        if self.game_timer <= 0 or self.pizzas_made >= self.target_pizzas:
            if key == pygame.K_RETURN:
                self.complete()
            return
            
        if self.current_pizza and self.current_pizza["stage"] == "topping":
            toppings = ["Pepperoni", "Mushrooms", "Olives", "Peppers"]
            
            if key >= pygame.K_1 and key <= pygame.K_4:
                index = key - pygame.K_1
                if index < len(toppings):
                    topping = toppings[index]
                    if topping not in self.current_pizza["added_toppings"]:
                        self.current_pizza["added_toppings"].append(topping)
                        
            elif key == pygame.K_SPACE:
                # Check if pizza is correct
                required = set(self.current_pizza["required_toppings"])
                added = set(self.current_pizza["added_toppings"])
                
                if required == added:
                    # Correct pizza, put in oven
                    self.pizza_in_oven = True
                    self.oven_timer = 3.0  # 3 seconds to bake
                    
        elif self.current_pizza and self.current_pizza["stage"] == "done":
            if key == pygame.K_RETURN:
                self.pizzas_made += 1
                if self.pizzas_made < self.target_pizzas:
                    self.new_pizza()
                    
    def handle_mouse_click(self, mouse_pos, button=1):
        """Handle mouse clicks for pizza making"""
        if not self.active:
            return
            
        if self.game_timer <= 0 or self.pizzas_made >= self.target_pizzas:
            # Game over, any click continues
            self.complete()
            return
            
        if self.current_pizza and self.current_pizza["stage"] == "topping":
            # Check topping button clicks
            if hasattr(self, 'topping_rects'):
                for rect, topping in self.topping_rects:
                    if rect.collidepoint(mouse_pos):
                        if topping not in self.current_pizza["added_toppings"]:
                            self.current_pizza["added_toppings"].append(topping)
                        else:
                            # Remove topping if already added (toggle)
                            self.current_pizza["added_toppings"].remove(topping)
                        return
            
            # Check bake button click
            if hasattr(self, 'bake_rect') and self.bake_rect.collidepoint(mouse_pos):
                # Check if pizza is correct
                required = set(self.current_pizza["required_toppings"])
                added = set(self.current_pizza["added_toppings"])
                
                if required == added:
                    # Correct pizza, put in oven
                    self.pizza_in_oven = True
                    self.oven_timer = 3.0  # 3 seconds to bake
                    
        elif self.current_pizza and self.current_pizza["stage"] == "done":
            # Any click serves the pizza
            self.pizzas_made += 1
            if self.pizzas_made < self.target_pizzas:
                self.new_pizza()


class BurgerMakingGame(Activity):
    """Burger flipping mini-game"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.burgers_made = 0
        self.target_burgers = 3
        self.current_burger = None
        self.game_timer = 60.0
        self.flip_timer = 0
        self.burger_flipped = False
        
    def start(self):
        super().start()
        self.new_burger()
        
    def new_burger(self):
        """Create a new burger order"""
        self.current_burger = {
            "stage": "cooking",  # cooking, flipped, done
            "cook_time": 0,
            "flip_needed": False
        }
        self.burger_flipped = False
        
    def update(self, dt):
        if not self.active:
            return
            
        self.game_timer -= dt
        
        if self.current_burger and self.current_burger["stage"] == "cooking":
            self.current_burger["cook_time"] += dt
            if self.current_burger["cook_time"] >= 3.0 and not self.burger_flipped:
                self.current_burger["flip_needed"] = True
                
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Game box
        box_width = 800
        box_height = 600
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Burger Making", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        # Progress
        info_font = pygame.font.Font(None, 32)
        progress_text = info_font.render(f"Burgers: {self.burgers_made}/{self.target_burgers}", True, (255, 255, 255))
        screen.blit(progress_text, (box_x + 50, box_y + 100))
        
        timer_text = info_font.render(f"Time: {int(self.game_timer)}s", True, (255, 255, 255))
        screen.blit(timer_text, (box_x + box_width - 150, box_y + 100))
        
        # Burger visualization
        burger_y = box_y + 250
        
        if self.current_burger:
            if self.current_burger["flip_needed"]:
                flip_text = title_font.render("FLIP THE BURGER! (Press SPACE)", True, (255, 100, 100))
                screen.blit(flip_text, (SCREEN_WIDTH // 2 - flip_text.get_width() // 2, burger_y))
            elif self.burger_flipped:
                done_text = info_font.render("Burger ready! Press ENTER to serve", True, (100, 255, 100))
                screen.blit(done_text, (SCREEN_WIDTH // 2 - done_text.get_width() // 2, burger_y))
            else:
                cook_text = info_font.render("Cooking...", True, (255, 150, 50))
                screen.blit(cook_text, (SCREEN_WIDTH // 2 - cook_text.get_width() // 2, burger_y))
                
        # End game check
        if self.game_timer <= 0 or self.burgers_made >= self.target_burgers:
            result_font = pygame.font.Font(None, 48)
            if self.burgers_made >= self.target_burgers:
                result_text = result_font.render("Great job!", True, (100, 255, 100))
            else:
                result_text = result_font.render("Time's up!", True, (255, 100, 100))
                
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, box_y + 400))
            
            cont_text = info_font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 450))
            
    def handle_key(self, key):
        if not self.active:
            return
            
        if self.game_timer <= 0 or self.burgers_made >= self.target_burgers:
            if key == pygame.K_RETURN:
                self.complete()
            return
            
        if key == pygame.K_SPACE and self.current_burger["flip_needed"]:
            self.burger_flipped = True
            self.current_burger["flip_needed"] = False
            
        elif key == pygame.K_RETURN and self.burger_flipped:
            self.burgers_made += 1
            if self.burgers_made < self.target_burgers:
                self.new_burger()


class DocumentChecklistWork(Activity):
    """Document checklist for jobs center"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.documents = {
            "ID": False,
            "SSN": False,
            "Resume": False
        }
        self.all_checked = False
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Box
        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Required Documents", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        # Checklist
        item_font = pygame.font.Font(None, 36)
        y_offset = 120
        
        for i, (doc, checked) in enumerate(self.documents.items()):
            checkbox = "[X]" if checked else "[ ]"
            text = item_font.render(f"{checkbox} {doc}", True, (255, 255, 255))
            screen.blit(text, (box_x + 150, box_y + y_offset + i * 60))
            
            # Number hints
            num_text = item_font.render(f"Press {i+1}", True, (150, 150, 150))
            screen.blit(num_text, (box_x + 400, box_y + y_offset + i * 60))
            
        # Continue button
        if self.all_checked:
            cont_font = pygame.font.Font(None, 32)
            cont_text = cont_font.render("All documents ready! Press ENTER to continue", True, (100, 255, 100))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 320))
            
    def handle_key(self, key):
        if not self.active:
            return
            
        if key == pygame.K_1:
            self.documents["ID"] = True
        elif key == pygame.K_2:
            self.documents["SSN"] = True
        elif key == pygame.K_3:
            self.documents["Resume"] = True
            
        self.all_checked = all(self.documents.values())
        
        if self.all_checked and key == pygame.K_RETURN:
            self.complete()


class BurgerTrainingActivity(Activity):
    """Burger training tutorial"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0
        self.stages = [
            "Welcome to burger training!",
            "Step 1: Place patty on grill",
            "Step 2: Cook for 3 seconds",
            "Step 3: Flip when it sizzles",
            "Step 4: Cook other side",
            "Step 5: Add toppings and serve!",
            "Training complete!"
        ]
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Box
        box_width = 700
        box_height = 300
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Burger Training", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        # Current stage
        stage_font = pygame.font.Font(None, 36)
        stage_text = stage_font.render(self.stages[self.stage], True, (255, 255, 255))
        screen.blit(stage_text, (SCREEN_WIDTH // 2 - stage_text.get_width() // 2, box_y + 130))
        
        # Progress
        progress_text = stage_font.render(f"Step {self.stage + 1} of {len(self.stages)}", True, (150, 150, 150))
        screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, box_y + 180))
        
        # Continue
        cont_font = pygame.font.Font(None, 28)
        if self.stage < len(self.stages) - 1:
            cont_text = cont_font.render("Press SPACE to continue", True, (200, 200, 200))
        else:
            cont_text = cont_font.render("Press ENTER to complete training", True, (100, 255, 100))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 240))
        
    def handle_key(self, key):
        if not self.active:
            return
            
        if key == pygame.K_SPACE and self.stage < len(self.stages) - 1:
            self.stage += 1
        elif key == pygame.K_RETURN and self.stage == len(self.stages) - 1:
            self.complete()


class JobListingsActivity(Activity):
    """View job listings and apply"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.jobs = [
            {"title": "Burger Flipper", "pay": "$18/hr", "hours": "Part-time"},
            {"title": "Cashier", "pay": "$17/hr", "hours": "Full-time"},
            {"title": "Cook Assistant", "pay": "$19/hr", "hours": "Part-time"}
        ]
        self.selected_job = 0
        self.applied = False
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Box
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Job Listings", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        # Jobs
        job_font = pygame.font.Font(None, 32)
        y_offset = 120
        
        for i, job in enumerate(self.jobs):
            color = (255, 220, 100) if i == self.selected_job else (255, 255, 255)
            prefix = "> " if i == self.selected_job else "  "
            
            job_text = job_font.render(f"{prefix}{job['title']}", True, color)
            screen.blit(job_text, (box_x + 80, box_y + y_offset + i * 80))
            
            details_text = job_font.render(f"   {job['pay']} - {job['hours']}", True, (180, 180, 180))
            screen.blit(details_text, (box_x + 80, box_y + y_offset + i * 80 + 30))
            
        # Instructions
        if not self.applied:
            inst_font = pygame.font.Font(None, 28)
            inst_text = inst_font.render("Use UP/DOWN arrows to select, ENTER to apply", True, (200, 200, 200))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 400))
        else:
            result_font = pygame.font.Font(None, 36)
            result_text = result_font.render("Application sent! You got the job!", True, (100, 255, 100))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, box_y + 400))
            
            cont_font = pygame.font.Font(None, 28)
            cont_text = cont_font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 440))
            
    def handle_key(self, key):
        if not self.active:
            return
            
        if not self.applied:
            if key == pygame.K_UP:
                self.selected_job = max(0, self.selected_job - 1)
            elif key == pygame.K_DOWN:
                self.selected_job = min(len(self.jobs) - 1, self.selected_job + 1)
            elif key == pygame.K_RETURN:
                self.applied = True
        else:
            if key == pygame.K_RETURN:
                self.complete()


class ManagerNoticeActivity(Activity):
    """Manager tells you to be at work tomorrow"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Box
        box_width = 700
        box_height = 300
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 100, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Manager message
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Manager Notice", True, (255, 100, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        msg_font = pygame.font.Font(None, 36)
        messages = [
            "Great first day!",
            "Be here tomorrow morning",
            "at 9:00 AM sharp!",
            "Don't be late!"
        ]
        
        y_offset = 100
        for msg in messages:
            msg_text = msg_font.render(msg, True, (255, 255, 255))
            screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, box_y + y_offset))
            y_offset += 35
            
        # Continue
        cont_font = pygame.font.Font(None, 28)
        cont_text = cont_font.render("Press ENTER to acknowledge", True, (200, 200, 200))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 250))
        
    def handle_key(self, key):
        if key == pygame.K_RETURN:
            self.complete()


class PanicSceneActivity(Activity):
    """Panic about missing work for mandatory meeting"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Box
        box_width = 700
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (50, 40, 40), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 100, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 56)
        title_text = title_font.render("OH NO!", True, (255, 100, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        # Messages
        msg_font = pygame.font.Font(None, 36)
        if self.stage == 0:
            messages = [
                "You have a mandatory school meeting tomorrow!",
                "But you also have work!",
                "You might get fired AGAIN!",
                "",
                "What should you do?"
            ]
        else:
            messages = [
                "Wait... you're a foster youth!",
                "You have special resources available.",
                "Maybe your ILP officer can help?",
                "",
                "Let's research this..."
            ]
            
        y_offset = 120
        for msg in messages:
            msg_text = msg_font.render(msg, True, (255, 255, 255))
            screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, box_y + y_offset))
            y_offset += 35
            
        # Continue
        cont_font = pygame.font.Font(None, 28)
        cont_text = cont_font.render("Press SPACE to continue", True, (200, 200, 200))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 340))
        
    def handle_key(self, key):
        if key == pygame.K_SPACE:
            if self.stage == 0:
                self.stage = 1
            else:
                self.complete()


class ILPOfficerCallActivity(Activity):
    """Call ILP officer for help"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.dialogue_index = 0
        self.dialogues = [
            {"speaker": "You", "text": "Hi, I need help with a work conflict..."},
            {"speaker": "ILP Officer", "text": "Of course! What's the situation?"},
            {"speaker": "You", "text": "I have a mandatory school meeting tomorrow"},
            {"speaker": "You", "text": "but my manager wants me at work."},
            {"speaker": "ILP Officer", "text": "I understand. As a foster youth, you have"},
            {"speaker": "ILP Officer", "text": "educational priority. Let me call your manager."},
            {"speaker": "You", "text": "Thank you so much!"},
            {"speaker": "ILP Officer", "text": "Give me 5 minutes. I'll call you back."}
        ]
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Phone interface
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 200, 255), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Calling ILP Officer", True, (100, 200, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        # Show dialogue history
        dialogue_font = pygame.font.Font(None, 28)
        y_offset = 100
        
        for i in range(max(0, self.dialogue_index - 5), self.dialogue_index + 1):
            if i < len(self.dialogues):
                d = self.dialogues[i]
                color = (100, 200, 255) if d["speaker"] == "ILP Officer" else (255, 255, 255)
                text = dialogue_font.render(f"{d['speaker']}: {d['text']}", True, color)
                screen.blit(text, (box_x + 50, box_y + y_offset))
                y_offset += 35
                
        # Continue or complete
        cont_font = pygame.font.Font(None, 28)
        if self.dialogue_index < len(self.dialogues) - 1:
            cont_text = cont_font.render("Press SPACE to continue conversation", True, (200, 200, 200))
        else:
            cont_text = cont_font.render("Press ENTER to wait for callback", True, (100, 255, 100))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 440))
        
    def handle_key(self, key):
        if key == pygame.K_SPACE and self.dialogue_index < len(self.dialogues) - 1:
            self.dialogue_index += 1
        elif key == pygame.K_RETURN and self.dialogue_index == len(self.dialogues) - 1:
            self.complete()


class ManagerChoiceActivity(Activity):
    """Choose how to handle the manager situation"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.choices = [
            "Call manager directly to thank them",
            "Do nothing (not recommended)",
            "Let ILP officer handle everything"
        ]
        self.selected_choice = 0
        self.choice_made = False
        self.outcome_text = ""
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Box
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Decision Time", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))
        
        if not self.choice_made:
            # Context
            context_font = pygame.font.Font(None, 28)
            context_text = context_font.render("ILP officer got you approved for tomorrow off!", True, (100, 255, 100))
            screen.blit(context_text, (SCREEN_WIDTH // 2 - context_text.get_width() // 2, box_y + 100))
            
            question_text = context_font.render("How do you want to handle this with your manager?", True, (255, 255, 255))
            screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, box_y + 140))
            
            # Choices
            choice_font = pygame.font.Font(None, 32)
            y_offset = 200
            
            for i, choice in enumerate(self.choices):
                color = (255, 220, 100) if i == self.selected_choice else (255, 255, 255)
                prefix = "> " if i == self.selected_choice else "  "
                
                choice_text = choice_font.render(f"{prefix}{choice}", True, color)
                screen.blit(choice_text, (box_x + 80, box_y + y_offset + i * 50))
                
            # Instructions
            inst_font = pygame.font.Font(None, 28)
            inst_text = inst_font.render("Use UP/DOWN to select, ENTER to choose", True, (200, 200, 200))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 420))
        else:
            # Show outcome
            outcome_font = pygame.font.Font(None, 32)
            outcome_lines = self.outcome_text.split('\n')
            y_offset = 150
            
            for line in outcome_lines:
                line_text = outcome_font.render(line, True, (255, 255, 255))
                screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, box_y + y_offset))
                y_offset += 35
                
            # Continue
            cont_font = pygame.font.Font(None, 28)
            cont_text = cont_font.render("Press ENTER to continue", True, (100, 255, 100))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 420))
            
    def handle_key(self, key):
        if not self.choice_made:
            if key == pygame.K_UP:
                self.selected_choice = max(0, self.selected_choice - 1)
            elif key == pygame.K_DOWN:
                self.selected_choice = min(len(self.choices) - 1, self.selected_choice + 1)
            elif key == pygame.K_RETURN:
                self.choice_made = True
                if self.selected_choice == 0:
                    self.outcome_text = "Great choice! You called your manager\nand thanked them for understanding.\nThey appreciated your professionalism!\n\nYou kept your job AND attended\nyour mandatory meeting!"
                elif self.selected_choice == 1:
                    self.outcome_text = "Not the best choice...\nYour manager was confused when\nyou showed up the next day.\n\nLuckily, the ILP officer had\nalready explained everything.\n\nTry to communicate better next time!"
                else:
                    self.outcome_text = "The ILP officer handled everything.\nYour manager understood the situation.\n\nNext time, consider following up\nwith a thank you - it shows maturity!"
        else:
            if key == pygame.K_RETURN:
                self.complete()


class ObjectiveManager:
    """Manages game objectives and progression"""
    def __init__(self, game):
        self.game = game
        self.objectives = []
        self.current_objective_index = 0
        self.active = True
        self.game_time = "8:00 AM"  # Track in-game time
        self.current_day = 1
        self.game_part = 1  # Track which part of the game we're in
        self.player_money = 0.0  # Track player's money
        
        # Building locations (will be set after map loads)
        self.foster_home = None
        self.community_center = None
        self.tlp_apartment = None
        self.workplace = None  # Pizza shop location
        self.school = None  # School location
        self.jobs_center = None  # Jobs center location
        
        # Part 1 Activities
        self.workplace_quiz = None  # Will be initialized later
        self.job_application = None  # Will be initialized later
        self.pizza_game = None  # Will be initialized later
        
        # Part 2 Activities (original)
        self.current_activity = None
        self.quiz = TenantRightsQuiz(self)
        self.packing = PackingActivity(self)
        self.life_skills_workshop = LifeSkillsWorkshop(self)
        self.emergency_notice = EmergencyNoticeActivity(self)
        self.document_checklist = DocumentChecklistActivity(self)
        
        # Mini-games
        self.grocery_game = GroceryShoppingGame(self)
        self.application_game = DocumentApplicationGame(self)
        self.roommate_game = RoommateAgreementGame(self)
        
        # Initialize Part 1 activities
        self.init_part1_activities()
        
        # Initialize objectives
        self.setup_objectives()
        
    def init_part1_activities(self):
        """Initialize Part 1 specific activities"""
        self.workplace_quiz = WorkplaceQuiz(self)
        self.job_application = JobApplicationActivity(self)
        self.pizza_game = PizzaMakingGame(self)
        self.firing_scene = FiringScene(self)
        self.emergency_scene = SchoolEmergencyScene(self)
        self.transition_scene = TransitionScene(self)
        
        # New activities for complete employment timeline
        self.burger_game = BurgerMakingGame(self)
        self.document_checklist_work = DocumentChecklistWork(self)
        self.burger_training = BurgerTrainingActivity(self)
        self.job_listings = JobListingsActivity(self)
        self.manager_notice = ManagerNoticeActivity(self)
        self.panic_scene = PanicSceneActivity(self)
        self.ilp_officer_call = ILPOfficerCallActivity(self)
        self.manager_choice = ManagerChoiceActivity(self)
        
    def setup_objectives(self):
        """Create complete game objectives for the housing storyline"""
        if self.game_part == 1:
            self.setup_part1_objectives()
        else:
            self.setup_part2_objectives()
            
    def setup_part1_objectives(self):
        """Create Part 1 objectives - Employment storyline"""
        self.objectives = [
            # Part 1 - School and Quiz
            GameObjective(
                "school_quiz",
                "Employment Rights Class",
                "Go to School for an employment rights quiz",
                None,
                "Press E to enter school"
            ),
            # Go to workplace after school
            GameObjective(
                "go_to_workplace",
                "Visit the Workplace",
                "Head to the workplace after attending school",
                None,
                "Press E to continue"
            ),
            # Job Application
            GameObjective(
                "workplace_apply",
                "Apply for Job",
                "Apply for a job at Tony's Pizza",
                None,
                "Press E to apply"
            ),
            # Get Hired
            GameObjective(
                "get_hired",
                "You're Hired!",
                "Congratulations! You got the job!",
                None,
                "Press E to continue"
            ),
            # Start Working
            GameObjective(
                "start_work",
                "First Day at Work",
                "Start your shift - time to make pizzas!",
                None,
                "Press E to start working"
            ),
            # Go Home after work
            GameObjective(
                "go_home_day1",
                "Return Home",
                "Head back home after your shift",
                None,
                "Press E when at home"
            ),
            # Manager tells you to be in office tomorrow
            GameObjective(
                "manager_notice",
                "Important Notice",
                "Your manager says: 'Be here tomorrow morning at 9 AM sharp!'",
                None,
                "Press E to acknowledge"
            ),
            # Sleep
            GameObjective(
                "sleep_work",
                "Rest for Tomorrow",
                "Get some sleep for tomorrow's work",
                None,
                "Press E to sleep"
            ),
            # Day 2 - Wake up and go to school (time skip)
            GameObjective(
                "wake_go_school",
                "Morning Routine",
                "Wake up and go to school (time skip)",
                None,
                "Press E to continue"
            ),
            # School Emergency
            GameObjective(
                "school_emergency",
                "School Emergency!",
                "There's an emergency at school!",
                None,
                "Press E to handle emergency"
            ),
            # Late to Work
            GameObjective(
                "late_to_work",
                "Rush to Work",
                "You're late! Get to the workplace immediately",
                None,
                "Press E to enter"
            ),
            # Get Fired
            GameObjective(
                "get_fired",
                "Meeting with Manager",
                "Your manager fires you for missing the shift...",
                None,
                "Press E to continue"
            ),
            # Collect Pay
            GameObjective(
                "collect_pay",
                "Collect Final Paycheck",
                "You earned $71.24 for yesterday's work (minimum wage * 4 hours)",
                None,
                "Press E to collect"
            ),
            # Jobs Center
            GameObjective(
                "jobs_center",
                "Visit Jobs Center",
                "Go to the Jobs Center for help finding work",
                None,
                "Press E to enter"
            ),
            # Document Checklist
            GameObjective(
                "document_checklist",
                "Required Documents",
                "Check that you have: ID, SSN, Resume",
                None,
                "Press E to verify documents"
            ),
            # Burger Training Offer
            GameObjective(
                "burger_training",
                "Training Opportunity",
                "Would you like burger-making training? (You have pizza experience)",
                None,
                "Press E to accept"
            ),
            # Receive Training
            GameObjective(
                "receive_training",
                "Burger Training",
                "Learn the basics of making burgers",
                None,
                "Press E to complete training"
            ),
            # Told to come back tomorrow
            GameObjective(
                "come_back_tomorrow",
                "Return Tomorrow",
                "Come back tomorrow for job listings",
                None,
                "Press E to continue"
            ),
            # Go home and sleep
            GameObjective(
                "go_home_sleep_day2",
                "End of Day",
                "Go home and rest",
                None,
                "Press E to go home"
            ),
            # Day 3 - Go to school
            GameObjective(
                "day3_school",
                "Back to School",
                "Another day at school",
                None,
                "Press E to attend"
            ),
            # View job listings
            GameObjective(
                "view_job_listings",
                "Job Listings",
                "Check available job opportunities",
                None,
                "Press E to view listings"
            ),
            # Apply for jobs
            GameObjective(
                "apply_for_jobs",
                "Send Applications",
                "Apply to the burger restaurant job",
                None,
                "Press E to apply"
            ),
            # Get hired at burger place
            GameObjective(
                "hired_burger_place",
                "New Job!",
                "You got the burger restaurant job!",
                None,
                "Press E to continue"
            ),
            # Work at burger place
            GameObjective(
                "work_burger_place",
                "First Shift",
                "Start flipping burgers at your new job",
                None,
                "Press E to work"
            ),
            # Day off notice
            GameObjective(
                "day_off_notice",
                "Schedule Update",
                "You don't need to work tomorrow",
                None,
                "Press E to continue"
            ),
            # Grocery shopping
            GameObjective(
                "grocery_shopping_work",
                "Buy Groceries",
                "Use your earnings to buy food (meet calorie/health requirements)",
                None,
                "Press E to shop"
            ),
            # Return home from shopping
            GameObjective(
                "return_home_shopping",
                "Head Home",
                "Go back home with your groceries",
                None,
                "Press E when home"
            ),
            # Day 4 - School with mandatory meeting notice
            GameObjective(
                "school_mandatory_meeting",
                "Important Notice",
                "School: You have a mandatory meeting tomorrow!",
                None,
                "Press E to read notice"
            ),
            # Panic about missing work
            GameObjective(
                "panic_scene",
                "Work Conflict!",
                "Oh no! You might get fired again for missing work!",
                None,
                "Press E to think of solution"
            ),
            # Learn about ILP officer
            GameObjective(
                "learn_ilp_officer",
                "Foster Youth Resources",
                "Research: ILP officers can help foster youth with work conflicts",
                None,
                "Press E to learn more"
            ),
            # Call ILP officer
            GameObjective(
                "call_ilp_officer",
                "Contact ILP Officer",
                "Call your ILP officer for help",
                None,
                "Press E to make call"
            ),
            # ILP officer calls back
            GameObjective(
                "ilp_callback",
                "Good News!",
                "ILP officer: 'I spoke to your manager - you're approved for tomorrow off!'",
                None,
                "Press E to continue"
            ),
            # Choice: How to handle manager
            GameObjective(
                "manager_choice",
                "Decision Time",
                "Choose: Thank manager directly, do nothing, or let ILP handle it",
                None,
                "Press E to decide"
            ),
            # End of Part 1
            GameObjective(
                "part1_complete",
                "Part 1 Complete!",
                "You've learned about employment rights and advocacy!",
                None,
                "Press E to continue to Part 2"
            )
        ]
        
    def setup_part2_objectives(self):
        """Create Part 2 objectives - Original housing storyline"""
        self.objectives = [
            # Day 1 - Morning
            GameObjective(
                "foster_home_class",
                "Attend Tenant Rights Class",
                "Go to the Foster Home and attend the tenant rights class (8:00 AM - 3:00 PM)",
                None,
                "Press E to enter class"
            ),
            GameObjective(
                "community_center_workshop",
                "Life Skills Workshop",
                "Head to the Community Center for the Life Skills Workshop",
                None,
                "Press E to enter workshop"
            ),
            GameObjective(
                "submit_application",
                "Submit TLP Application",
                "Apply for Transitional Living Program housing",
                None,
                "Press E to submit application"
            ),
            # Day 1 - Evening
            GameObjective(
                "pack_belongings",
                "Move to TLP Apartment",
                "Pack and move into your new TLP apartment (5:00 PM - 9:00 PM)",
                None,
                "Press E to start packing"
            ),
            GameObjective(
                "meet_roommate",
                "Meet Your Roommate",
                "Return to apartment and meet your new roommate",
                None,
                "Press E to greet roommate"
            ),
            GameObjective(
                "sleep_day1",
                "Rest for Tomorrow",
                "Go to sleep in your new apartment",
                None,
                "Press E to sleep"
            ),
            # Day 2 - Crisis
            GameObjective(
                "discover_emergency",
                "Emergency: Roommate Gone!",
                "Check your apartment - something's wrong",
                None,
                "Press E to investigate"
            ),
            GameObjective(
                "receive_notices",
                "Urgent Notices",
                "You've received a 3-day pay or quit notice and utility shutoff warning",
                None,
                "Press E to read notices"
            ),
            GameObjective(
                "housing_services",
                "Visit Housing Services",
                "Go to Housing Services Office with your documents",
                None,
                "Press E to enter office"
            ),
            GameObjective(
                "emergency_assistance",
                "Emergency Housing Help",
                "Accept emergency housing assistance",
                None,
                "Press E to proceed"
            ),
            GameObjective(
                "pack_essentials",
                "Pack Essential Items",
                "Return to apartment and pack essentials for temporary housing",
                None,
                "Press E to pack"
            ),
            # Day 3 - Recovery
            GameObjective(
                "return_housing_services",
                "Return to Housing Services",
                "Come back at 3:00 PM as instructed",
                None,
                "Press E to enter"
            ),
            GameObjective(
                "select_roommate",
                "Choose New Roommate",
                "Review roommate profiles and select a compatible match",
                None,
                "Press E to view profiles"
            ),
            GameObjective(
                "roommate_agreement",
                "Set Up Living Agreement",
                "Go to apartment and establish roommate agreement",
                None,
                "Press E to start agreement"
            ),
            GameObjective(
                "grocery_shopping",
                "Shop for Groceries",
                "Visit grocery store and learn to split costs with roommate",
                None,
                "Press E to shop"
            ),
            # Day 4 - New Crisis
            GameObjective(
                "heater_broken",
                "Emergency: No Heat!",
                "Your heater is broken and you have a test tomorrow",
                None,
                "Press E to assess situation"
            ),
            GameObjective(
                "contact_help",
                "Get Help for Heater",
                "Contact TLP case manager or landlord for emergency repair",
                None,
                "Press E to make calls"
            ),
            GameObjective(
                "resolution",
                "Crisis Resolved",
                "Maintenance is on the way - you've learned to advocate for yourself",
                None,
                "Press E to continue"
            )
        ]
        
    def find_building_locations(self):
        """Find appropriate buildings for the storyline"""
        building_types = {
            'house': [],
            'bank': [],
            'building': [],
            'store': [],
            'school': [],
            'pizza': [],
            'apartment': [],
            'office': [],
            'grocery': []
        }
        
        # Scan the map for buildings
        for y in range(self.game.city_map.height):
            for x in range(self.game.city_map.width):
                tile_data = self.game.city_map.map_data[y][x]
                # Check for both regular buildings and buildings with backgrounds
                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, building_key, offset_x, offset_y, _ = tile_data
                    else:
                        _, building_key, offset_x, offset_y = tile_data
                    
                    # Only store the top-left corner of buildings
                    if offset_x == 0 and offset_y == 0:
                        # Store in specific categories first
                        building_name_lower = building_key.lower()
                        found_specific = False
                        
                        # Check for specific building types
                        for specific_type in ['school', 'pizza', 'apartment', 'office', 'grocery']:
                            if specific_type in building_name_lower:
                                building_types[specific_type].append((x, y))
                                found_specific = True
                                break
                        
                        # Then check general categories
                        if not found_specific:
                            for btype in ['house', 'bank', 'building', 'store']:
                                if btype in building_name_lower:
                                    building_types[btype].append((x, y))
                                    break
        
        # Print found buildings for debugging
        print("\nFound buildings on map:")
        for btype, locations in building_types.items():
            if locations:
                print(f"  {btype}: {len(locations)} buildings")
        
        # Assign key locations based on game part
        if self.game_part == 1:
            # Part 1 locations - prioritize specific building types
            
            # School - prefer actual school buildings
            if building_types['school']:
                self.school = random.choice(building_types['school'])
            elif building_types['building']:
                self.school = random.choice(building_types['building'])
            else:
                # Fallback to any building
                all_buildings = building_types['bank'] + building_types['office']
                if all_buildings:
                    self.school = random.choice(all_buildings)
                    
            if hasattr(self, 'school') and self.school:
                self.objectives[0].target_position = self.school  # school_quiz
                self.objectives[5].target_position = self.school  # school_emergency
                print(f"  School at: {self.school}")
                
            # Workplace (Pizza Shop) - prefer pizza buildings
            if building_types['pizza']:
                self.workplace = random.choice(building_types['pizza'])
            elif building_types['store']:
                self.workplace = random.choice(building_types['store'])
            else:
                # Fallback
                all_commercial = building_types['building'] + building_types['bank']
                if all_commercial:
                    self.workplace = random.choice(all_commercial)
                    
            if hasattr(self, 'workplace') and self.workplace:
                self.objectives[1].target_position = self.workplace  # workplace_apply
                self.objectives[2].target_position = self.workplace  # start_work
                self.objectives[6].target_position = self.workplace  # late_to_work
                self.objectives[7].target_position = self.workplace  # get_fired
                self.objectives[8].target_position = self.workplace  # collect_pay
                print(f"  Workplace at: {self.workplace}")
                
            # Player's home
            if building_types['house']:
                home = random.choice(building_types['house'])
            elif building_types['apartment']:
                home = random.choice(building_types['apartment'])
            else:
                # Fallback to any building
                all_buildings = building_types['building'] + building_types['store']
                if all_buildings:
                    home = random.choice(all_buildings)
                    
            if home:
                self.objectives[3].target_position = home  # go_home_day1
                self.objectives[4].target_position = home  # sleep_work
                print(f"  Home at: {home}")
                
            # Jobs Center - prefer office buildings
            if building_types['office']:
                self.jobs_center = random.choice(building_types['office'])
            elif building_types['building']:
                available_buildings = [b for b in building_types['building'] 
                                     if b != getattr(self, 'school', None)]
                if available_buildings:
                    self.jobs_center = random.choice(available_buildings)
            else:
                # Fallback
                all_buildings = building_types['bank'] + building_types['store']
                if all_buildings:
                    self.jobs_center = random.choice(all_buildings)
                    
            if hasattr(self, 'jobs_center') and self.jobs_center:
                self.objectives[9].target_position = self.jobs_center  # jobs_center
                self.objectives[10].target_position = self.jobs_center  # transition_part2
                print(f"  Jobs Center at: {self.jobs_center}")
                
        else:
            # Part 2 locations - housing crisis storyline
            
            # Foster home
            if building_types['house']:
                self.foster_home = random.choice(building_types['house'])
                self.objectives[0].target_position = self.foster_home
                print(f"  Foster home at: {self.foster_home}")
                
            # TLP Apartment - prefer apartment buildings
            if building_types['apartment']:
                self.tlp_apartment = random.choice(building_types['apartment'])
            elif building_types['house']:
                available_houses = [h for h in building_types['house'] 
                                  if h != getattr(self, 'foster_home', None)]
                if available_houses:
                    self.tlp_apartment = random.choice(available_houses)
            else:
                # Fallback
                all_residential = building_types['building'] + building_types['store']
                if all_residential:
                    self.tlp_apartment = random.choice(all_residential)
                    
            if hasattr(self, 'tlp_apartment') and self.tlp_apartment:
                # All apartment-related objectives
                apartment_indices = [3, 4, 5, 6, 7, 10, 13, 15, 16, 17]
                for idx in apartment_indices:
                    if idx < len(self.objectives):
                        self.objectives[idx].target_position = self.tlp_apartment
                print(f"  TLP Apartment at: {self.tlp_apartment}")
            
            # Community Center
            self.community_center = None
            if building_types['office']:
                self.community_center = random.choice(building_types['office'])
            elif building_types['bank']:
                self.community_center = random.choice(building_types['bank'])
            elif building_types['building']:
                self.community_center = random.choice(building_types['building'])
            else:
                # Ultimate fallback - use ANY building
                all_buildings = []
                for btype in building_types.values():
                    all_buildings.extend(btype)
                if all_buildings:
                    self.community_center = random.choice(all_buildings)
                    print("  WARNING: Using ANY building as community center fallback")
                
            if self.community_center:
                # Community center objectives
                cc_indices = [1, 2]
                for idx in cc_indices:
                    if idx < len(self.objectives):
                        self.objectives[idx].target_position = self.community_center
                print(f"  Community Center at: {self.community_center}")
            else:
                print("  ERROR: No Community Center found even with fallback!")
            
            # Housing Services Office (use a different building)
            housing_office = None
            if building_types['office']:
                available_offices = [o for o in building_types['office'] 
                                   if o != getattr(self, 'community_center', None)]
                if available_offices:
                    housing_office = random.choice(available_offices)
            elif building_types['building']:
                available_buildings = [b for b in building_types['building'] 
                                     if b != getattr(self, 'community_center', None)]
                if available_buildings:
                    housing_office = random.choice(available_buildings)
            elif building_types['bank']:
                available_banks = [b for b in building_types['bank'] 
                                 if b != getattr(self, 'community_center', None)]
                if available_banks:
                    housing_office = random.choice(available_banks)
                    
            if housing_office:
                # Housing office objectives
                ho_indices = [8, 9, 11, 12]
                for idx in ho_indices:
                    if idx < len(self.objectives):
                        self.objectives[idx].target_position = housing_office
                print(f"  Housing Office at: {housing_office}")
            
            # Grocery Store - prefer actual grocery stores
            grocery_store = None
            if building_types['grocery']:
                grocery_store = random.choice(building_types['grocery'])
            elif building_types['store']:
                grocery_store = random.choice(building_types['store'])
            else:
                # Fallback
                all_commercial = building_types['building'] + building_types['bank']
                if all_commercial:
                    grocery_store = random.choice(all_commercial)
                    
            if grocery_store and 14 < len(self.objectives):
                self.objectives[14].target_position = grocery_store
                print(f"  Grocery Store at: {grocery_store}")
            
    def start(self):
        """Start the objective system"""
        self.find_building_locations()
        
        # Ensure all objectives have positions
        self.ensure_all_objectives_have_positions()
        
        self.activate_current_objective()
        
    def ensure_all_objectives_have_positions(self):
        """Make sure every objective has a target position"""
        # Find any building as fallback
        fallback_position = None
        for y in range(self.game.city_map.height):
            for x in range(self.game.city_map.width):
                tile_data = self.game.city_map.map_data[y][x]
                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, _, offset_x, offset_y, _ = tile_data
                    else:
                        _, _, offset_x, offset_y = tile_data
                    if offset_x == 0 and offset_y == 0:
                        fallback_position = (x, y)
                        break
            if fallback_position:
                break
                
        # If no buildings found, use center of map
        if not fallback_position:
            fallback_position = (self.game.city_map.width // 2, self.game.city_map.height // 2)
            print(f"Warning: No buildings found on map! Using center: {fallback_position}")
            
        # Assign fallback position to any objective without one
        for i, obj in enumerate(self.objectives):
            if not obj.target_position:
                obj.target_position = fallback_position
                print(f"Warning: Objective '{obj.id}' ({obj.title}) had no position, using fallback: {fallback_position}")
            
        # Double-check that all objectives now have positions
        for i, obj in enumerate(self.objectives):
            if not obj.target_position:
                print(f"ERROR: Objective '{obj.id}' STILL has no position after fallback!")
            else:
                print(f"Objective '{obj.id}' position confirmed: {obj.target_position}")
        
    def activate_current_objective(self):
        """Activate the current objective"""
        if self.current_objective_index < len(self.objectives):
            self.objectives[self.current_objective_index].activate()
            
    def get_current_objective(self):
        """Get the current active objective"""
        if self.current_objective_index < len(self.objectives):
            return self.objectives[self.current_objective_index]
        return None
        
    def check_player_at_objective(self, player_x, player_y):
        """Check if player is at the current objective location"""
        current = self.get_current_objective()
        if not current or not current.target_position:
            return False
            
        target_x, target_y = current.target_position
        # Check if player is near the building entrance (within 1 tile)
        distance = abs(player_x - target_x) + abs(player_y - target_y)
        return distance <= 3  # Within 3 tiles
        
    def complete_current_objective(self):
        """Start activity or complete objective"""
        current = self.get_current_objective()
        if not current:
            return
            
        # Handle Part 1 objectives
        if self.game_part == 1:
            if current.id == "school_quiz":
                self.current_activity = self.workplace_quiz
                self.current_activity.start()
            elif current.id == "go_to_workplace":
                self.advance_to_next_objective()
            elif current.id == "workplace_apply":
                self.current_activity = self.job_application
                self.current_activity.start()
            elif current.id == "get_hired":
                self.advance_to_next_objective()
            elif current.id == "start_work":
                self.current_activity = self.pizza_game
                self.current_activity.start()
            elif current.id == "go_home_day1":
                self.advance_to_next_objective()
            elif current.id == "manager_notice":
                self.current_activity = self.manager_notice
                self.current_activity.start()
            elif current.id == "sleep_work":
                self.current_day = 2
                self.game_time = "8:00 AM"
                self.advance_to_next_objective()
            elif current.id == "wake_go_school":
                self.game_time = "9:00 AM"
                self.advance_to_next_objective()
            elif current.id == "school_emergency":
                self.current_activity = self.emergency_scene
                self.current_activity.start()
            elif current.id == "late_to_work":
                self.advance_to_next_objective()
            elif current.id == "get_fired":
                self.current_activity = self.firing_scene
                self.current_activity.start()
            elif current.id == "collect_pay":
                self.player_money += 71.24
                self.advance_to_next_objective()
            elif current.id == "jobs_center":
                self.advance_to_next_objective()
            elif current.id == "document_checklist":
                self.current_activity = self.document_checklist_work
                self.current_activity.start()
            elif current.id == "burger_training":
                self.advance_to_next_objective()
            elif current.id == "receive_training":
                self.current_activity = self.burger_training
                self.current_activity.start()
            elif current.id == "come_back_tomorrow":
                self.advance_to_next_objective()
            elif current.id == "go_home_sleep_day2":
                self.current_day = 3
                self.game_time = "8:00 AM"
                self.advance_to_next_objective()
            elif current.id == "day3_school":
                self.game_time = "3:00 PM"
                self.advance_to_next_objective()
            elif current.id == "view_job_listings":
                self.current_activity = self.job_listings
                self.current_activity.start()
            elif current.id == "apply_for_jobs":
                self.advance_to_next_objective()
            elif current.id == "hired_burger_place":
                self.advance_to_next_objective()
            elif current.id == "work_burger_place":
                self.current_activity = self.burger_game
                self.current_activity.start()
            elif current.id == "day_off_notice":
                self.advance_to_next_objective()
            elif current.id == "grocery_shopping_work":
                self.current_activity = self.grocery_game
                self.current_activity.start()
            elif current.id == "return_home_shopping":
                self.advance_to_next_objective()
            elif current.id == "school_mandatory_meeting":
                self.current_day = 4
                self.game_time = "9:00 AM"
                self.advance_to_next_objective()
            elif current.id == "panic_scene":
                self.current_activity = self.panic_scene
                self.current_activity.start()
            elif current.id == "learn_ilp_officer":
                self.advance_to_next_objective()
            elif current.id == "call_ilp_officer":
                self.current_activity = self.ilp_officer_call
                self.current_activity.start()
            elif current.id == "ilp_callback":
                self.advance_to_next_objective()
            elif current.id == "manager_choice":
                self.current_activity = self.manager_choice
                self.current_activity.start()
            elif current.id == "part1_complete":
                # Transition to Part 2
                self.game_part = 2
                self.current_objective_index = 0
                self.setup_part2_objectives()
                self.find_building_locations()
                self.current_activity = None
                self.activate_current_objective()
                
        # Handle Part 2 objectives (original code)
        elif current.id == "foster_home_class":
            self.current_activity = self.quiz
            self.current_activity.start()
        elif current.id == "tenant_orientation":
            # Advance after tenant orientation
            self.advance_to_next_objective()
        elif current.id == "community_center_workshop":
            # Launch life skills workshop activity
            self.current_activity = self.life_skills_workshop
            self.current_activity.start()
        elif current.id == "submit_application":
            # Launch document application mini-game
            self.current_activity = self.application_game
            self.current_activity.start()
        elif current.id == "pack_belongings":
            self.current_activity = self.packing
            self.current_activity.start()
        elif current.id == "meet_roommate":
            # Show roommate meeting
            self.advance_to_next_objective()
        elif current.id == "sleep_day1":
            # Sleep and advance to next day
            self.current_day = 2
            self.game_time = "8:00 AM"
            self.advance_to_next_objective()
        elif current.id == "discover_emergency":
            # Show emergency notices
            self.current_activity = self.emergency_notice
            self.current_activity.start()
        elif current.id == "receive_notices":
            self.advance_to_next_objective()
        elif current.id == "housing_services":
            # Document checklist
            self.current_activity = self.document_checklist
            self.current_activity.start()
        elif current.id == "emergency_assistance":
            # Force yes option (will implement later)
            self.advance_to_next_objective()
        elif current.id == "pack_essentials":
            # Quick pack
            self.advance_to_next_objective()
        elif current.id == "return_housing_services":
            # Skip to next
            self.current_day = 3
            self.game_time = "3:00 PM"
            self.advance_to_next_objective()
        elif current.id == "select_roommate":
            # Roommate selection (will implement)
            self.advance_to_next_objective()
        elif current.id == "roommate_agreement":
            # Launch roommate agreement mini-game
            self.current_activity = self.roommate_game
            self.current_activity.start()
        elif current.id == "grocery_shopping":
            # Launch grocery shopping mini-game
            self.current_activity = self.grocery_game
            self.current_activity.start()
        elif current.id == "heater_broken":
            # Start heater crisis
            self.current_day = 4
            self.advance_to_next_objective()
        elif current.id == "contact_help":
            # Contact help (will implement)
            self.advance_to_next_objective()
        elif current.id == "resolution":
            # End of simulation
            self.advance_to_next_objective()
            
    def advance_to_next_objective(self):
        """Move to the next objective"""
        current = self.get_current_objective()
        if current:
            current.complete()
            self.current_objective_index += 1
            
            # Update game time based on objective
            time_updates = {
                # Part 1 time updates
                "school_quiz": "10:00 AM",
                "workplace_apply": "2:00 PM",
                "start_work": "7:00 PM",
                "go_home_day1": "8:00 PM",
                # Part 2 time updates
                "foster_home_class": "3:00 PM",
                "submit_application": "5:00 PM", 
                "pack_belongings": "9:00 PM",
                "meet_roommate": "10:00 PM",
                "housing_services": "10:00 AM",
                "emergency_assistance": "11:00 AM",
                "pack_essentials": "12:00 PM",
                "grocery_shopping": "6:00 PM",
                "heater_broken": "7:00 PM"
            }
            
            if current.id in time_updates:
                self.game_time = time_updates[current.id]
                
            # Activate next objective
            self.activate_current_objective()
            
    def update(self, dt):
        """Update objectives and activities"""
        # Update current activity if any
        if self.current_activity and self.current_activity.active:
            self.current_activity.update(dt)
            # Check if activity completed
            if self.current_activity.completed:
                # Special handling for transition scene
                if isinstance(self.current_activity, TransitionScene):
                    # Complete the transition to Part 2
                    self.game_part = 2
                    self.current_day = 1
                    self.game_time = "8:00 AM"
                    self.current_objective_index = 0
                    self.setup_objectives()  # Reset objectives for Part 2
                    self.find_building_locations()  # Find new buildings for Part 2
                    self.current_activity = None
                    self.activate_current_objective()
                    return
                    
                self.current_activity = None
                self.advance_to_next_objective()
                return  # Important: return here to avoid re-checking the same objective
        elif self.current_activity and self.current_activity.completed:
            # Clean up completed activity
            self.current_activity = None
            self.advance_to_next_objective()
            return
        else:
            # Update current objective notification timer
            current = self.get_current_objective()
            if current:
                current.update(dt)
            
    def draw_ui(self, screen):
        """Draw professional, well-aligned HUD"""
        # Draw current activity if active
        if self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return  # Don't draw other UI when activity is active
            
        current = self.get_current_objective()
        if not current:
            return
        
        # Professional HUD design
        margin = 25
        panel_width = 320
        panel_height = 160
        corner_radius = 10
        
        # Create main panel with gradient effect
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.fill((25, 25, 30))
        
        # Draw gradient overlay
        for i in range(panel_height):
            alpha = int(255 - (i / panel_height) * 50)
            color = (30, 30, 35)
            line_surface = pygame.Surface((panel_width, 1))
            line_surface.fill(color)
            line_surface.set_alpha(alpha)
            panel_surface.blit(line_surface, (0, i))
        
        panel_surface.set_alpha(220)
        screen.blit(panel_surface, (margin, margin))
        
        # Draw elegant border
        pygame.draw.rect(screen, (70, 70, 80), 
                        (margin, margin, panel_width, panel_height), 2, 
                        border_radius=corner_radius)
        
        # Inner content positioning
        content_x = margin + 20
        content_y = margin + 20
        
        # Fonts
        header_font = pygame.font.Font(None, 26)
        value_font = pygame.font.Font(None, 24)
        label_font = pygame.font.Font(None, 20)
        
        # Row 1: Game Part and Day/Time (aligned)
        row1_y = content_y
        
        # Part indicator with better styling
        part_color = (120, 170, 255) if self.game_part == 1 else (255, 170, 120)
        part_bg = pygame.Surface((60, 24))
        part_bg.fill(part_color)
        part_bg.set_alpha(40)
        screen.blit(part_bg, (content_x, row1_y - 2))
        pygame.draw.rect(screen, part_color, (content_x, row1_y - 2, 60, 24), 1)
        
        part_text = label_font.render(f"PART {self.game_part}", True, part_color)
        screen.blit(part_text, (content_x + 8, row1_y + 2))
        
        # Day/Time aligned to the right
        day_time_text = f"Day {self.current_day} • {self.game_time}"
        day_time_surface = value_font.render(day_time_text, True, (220, 220, 220))
        day_time_x = margin + panel_width - day_time_surface.get_width() - 20
        screen.blit(day_time_surface, (day_time_x, row1_y))
        
        # Row 2: Money (if applicable)
        row2_y = row1_y + 35
        if self.game_part == 1 or self.player_money > 0:
            # Money label
            money_label = label_font.render("Balance", True, (150, 150, 150))
            screen.blit(money_label, (content_x, row2_y))
            
            # Money value aligned
            money_color = (120, 255, 120) if self.player_money > 0 else (255, 120, 120)
            money_text = f"${self.player_money:,.2f}"
            money_surface = header_font.render(money_text, True, money_color)
            screen.blit(money_surface, (content_x + 70, row2_y - 2))
            
            row3_y = row2_y + 35
        else:
            row3_y = row2_y
        
        # Divider line
        pygame.draw.line(screen, (50, 50, 55), 
                        (content_x, row3_y), 
                        (margin + panel_width - 20, row3_y), 1)
        
        # Row 3: Current Objective
        obj_y = row3_y + 10
        obj_label = label_font.render("OBJECTIVE", True, (150, 150, 150))
        screen.blit(obj_label, (content_x, obj_y))
        
        # Objective text with proper wrapping
        obj_text_y = obj_y + 20
        max_width = panel_width - 40
        words = current.title.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if value_font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw objective lines
        for i, line in enumerate(lines[:2]):  # Max 2 lines
            obj_surface = value_font.render(line, True, (255, 255, 200))
            screen.blit(obj_surface, (content_x, obj_text_y + i * 22))
        
        # Progress bar instead of dots
        if len(self.objectives) > 1:
            progress_y = margin + panel_height - 15
            progress_width = panel_width - 40
            progress_x = content_x
            
            # Background bar
            pygame.draw.rect(screen, (40, 40, 45), 
                           (progress_x, progress_y, progress_width, 6), 
                           border_radius=3)
            
            # Progress fill
            progress_percent = (self.current_objective_index + 1) / len(self.objectives)
            fill_width = int(progress_width * progress_percent)
            if fill_width > 0:
                pygame.draw.rect(screen, (100, 200, 100), 
                               (progress_x, progress_y, fill_width, 6), 
                               border_radius=3)
        
        
        # Draw objective notification if recently activated
        if current.show_notification and current.notification_timer > 0:
            notification_alpha = int(min(255, current.notification_timer * 255))
            
            # Professional notification design
            notif_font = pygame.font.Font(None, 24)
            desc_font = pygame.font.Font(None, 20)
            
            # Create notification text
            notif_text = "NEW OBJECTIVE"
            desc_text = current.title
            
            # Calculate dimensions
            desc_surface = desc_font.render(desc_text, True, (255, 255, 255))
            box_width = desc_surface.get_width() + 80
            box_height = 60
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            box_y = 120
            
            # Create notification panel with gradient
            notif_panel = pygame.Surface((box_width, box_height))
            notif_panel.fill((25, 25, 30))
            
            # Add subtle gradient
            for i in range(box_height):
                alpha = int(255 - (i / box_height) * 30)
                line = pygame.Surface((box_width, 1))
                line.fill((30, 30, 35))
                line.set_alpha(alpha)
                notif_panel.blit(line, (0, i))
            
            notif_panel.set_alpha(min(220, notification_alpha))
            screen.blit(notif_panel, (box_x, box_y))
            
            # Elegant border with glow effect
            border_color = (255, 220, 100)
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2, border_radius=8)
            
            # Left accent bar
            accent_width = 4
            accent_surface = pygame.Surface((accent_width, box_height - 20))
            accent_surface.fill(border_color)
            accent_surface.set_alpha(notification_alpha)
            screen.blit(accent_surface, (box_x + 10, box_y + 10))
            
            # Draw text
            notif_surface = notif_font.render(notif_text, True, border_color)
            notif_surface.set_alpha(notification_alpha)
            desc_surface.set_alpha(notification_alpha)
            
            # Align text properly
            text_x = box_x + 25
            screen.blit(notif_surface, (text_x, box_y + 12))
            screen.blit(desc_surface, (text_x, box_y + 35))
        
        # Draw interaction prompt if player is near objective
        if self.game.player_near_objective:
            prompt_font = pygame.font.Font(None, 22)
            prompt_text = current.interaction_text
            prompt_surface = prompt_font.render(prompt_text, True, (255, 255, 255))
            
            # Professional prompt design
            prompt_width = prompt_surface.get_width() + 40
            prompt_height = 36
            prompt_x = SCREEN_WIDTH // 2 - prompt_width // 2
            prompt_y = SCREEN_HEIGHT // 2 - 100
            
            # Pulsing effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.2 + 0.8
            
            # Create prompt panel
            prompt_panel = pygame.Surface((prompt_width, prompt_height))
            prompt_panel.fill((25, 25, 30))
            prompt_panel.set_alpha(int(220 * pulse))
            screen.blit(prompt_panel, (prompt_x, prompt_y))
            
            # Green accent border
            border_color = (120, 255, 120)
            pygame.draw.rect(screen, border_color, 
                           (prompt_x, prompt_y, prompt_width, prompt_height), 
                           2, border_radius=6)
            
            # E key indicator
            key_bg = pygame.Surface((24, 24))
            key_bg.fill((40, 40, 45))
            key_bg.set_alpha(int(255 * pulse))
            key_x = prompt_x + 8
            key_y = prompt_y + 6
            screen.blit(key_bg, (key_x, key_y))
            pygame.draw.rect(screen, border_color, (key_x, key_y, 24, 24), 1, border_radius=4)
            
            key_font = pygame.font.Font(None, 20)
            key_text = key_font.render("E", True, border_color)
            screen.blit(key_text, (key_x + 8, key_y + 4))
            
            # Interaction text
            text_x = prompt_x + 40
            text_y = prompt_y + prompt_height // 2 - prompt_surface.get_height() // 2
            screen.blit(prompt_surface, (text_x, text_y))
            
    def draw_objective_markers(self, screen, camera_x, camera_y):
        """Draw markers and path for objective locations on the map"""
        current = self.get_current_objective()
        if not current:
            return
            
        # Additional safety check and debug info
        if not current.target_position:
            print(f"WARNING: Current objective '{current.id}' has no target position!")
            # Try to ensure positions again
            self.ensure_all_objectives_have_positions()
            if not current.target_position:
                print(f"ERROR: Still no position for '{current.id}' after re-ensuring!")
                return
            
        # Get positions
        player_x = self.game.player.x
        player_y = self.game.player.y
        target_x, target_y = current.target_position
        
        # Calculate distance in tiles
        tile_distance = math.sqrt((target_x - player_x)**2 + (target_y - player_y)**2)
        
        # Draw navigation line
        if not self.game.player_near_objective and tile_distance > 2:
            # Get screen positions
            player_screen_x = self.game.player.pixel_x - camera_x + TILE_SIZE // 2
            player_screen_y = self.game.player.pixel_y - camera_y + TILE_SIZE // 2
            target_screen_x = target_x * TILE_SIZE - camera_x + TILE_SIZE // 2
            target_screen_y = target_y * TILE_SIZE - camera_y + TILE_SIZE // 2
            
            # Calculate line direction
            dx = target_screen_x - player_screen_x
            dy = target_screen_y - player_screen_y
            line_length = math.sqrt(dx * dx + dy * dy)
            
            if line_length > 0:
                # Normalize direction
                dx /= line_length
                dy /= line_length
                
                # Line starts near player
                start_offset = 50
                line_start_x = player_screen_x + dx * start_offset
                line_start_y = player_screen_y + dy * start_offset
                
                # Line ends near target (but not quite at it)
                end_offset = 40
                line_end_x = target_screen_x - dx * end_offset
                line_end_y = target_screen_y - dy * end_offset
                
                # Only draw if line would be visible
                actual_line_length = math.sqrt((line_end_x - line_start_x)**2 + (line_end_y - line_start_y)**2)
                
                if actual_line_length > 20:
                    # Draw more visible animated dotted line
                    num_dots = int(actual_line_length / 20)  # More dots
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 0.3 + 0.7
                    
                    for i in range(num_dots):
                        t = i / float(num_dots - 1) if num_dots > 1 else 0
                        dot_x = line_start_x + (line_end_x - line_start_x) * t
                        dot_y = line_start_y + (line_end_y - line_start_y) * t
                        
                        # Animated dots that "flow" toward objective
                        flow_offset = (pygame.time.get_ticks() * 0.001) % 1.0
                        if abs((i / float(max(num_dots, 1))) - flow_offset) < 0.1:
                            size = 6
                            color = (255, 255, 150)
                            glow = True
                        else:
                            size = 4
                            color = (255, 220, 100)
                            glow = False
                        
                        # Draw glow effect for active dots
                        if glow:
                            glow_surf = pygame.Surface((16, 16))
                            glow_surf.set_colorkey((0, 0, 0))
                            pygame.draw.circle(glow_surf, (255, 220, 100), (8, 8), 8)
                            glow_surf.set_alpha(int(50 * pulse))
                            screen.blit(glow_surf, (int(dot_x) - 8, int(dot_y) - 8))
                        
                        # Draw main dot
                        pygame.draw.circle(screen, color, (int(dot_x), int(dot_y)), size)
                        pygame.draw.circle(screen, (255, 255, 200), (int(dot_x), int(dot_y)), size - 1)
                    
                    # Draw larger, more visible arrow
                    arrow_length = 20
                    arrow_width = 12
                    
                    # Pulsing arrow
                    arrow_pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.4 + 0.6
                    
                    # Create arrow with glow
                    arrow_surface = pygame.Surface((60, 60))
                    arrow_surface.set_colorkey((0, 0, 0))
                    
                    # Draw glow
                    for i in range(3):
                        glow_size = 30 - i * 8
                        glow_alpha = int(30 * arrow_pulse)
                        pygame.draw.circle(arrow_surface, (255, 220, 100), (30, 30), glow_size)
                    
                    # Arrow points (centered in surface)
                    center_x, center_y = 30, 30
                    tip_x = center_x + dx * arrow_length
                    tip_y = center_y + dy * arrow_length
                    
                    # Calculate perpendicular for arrow wings
                    perp_x = -dy
                    perp_y = dx
                    
                    wing1_x = center_x + perp_x * arrow_width
                    wing1_y = center_y + perp_y * arrow_width
                    wing2_x = center_x - perp_x * arrow_width
                    wing2_y = center_y - perp_y * arrow_width
                    
                    # Draw arrow with outline
                    arrow_points = [(tip_x, tip_y), (wing1_x, wing1_y), (wing2_x, wing2_y)]
                    pygame.draw.polygon(arrow_surface, (255, 255, 150), arrow_points)
                    pygame.draw.polygon(arrow_surface, (255, 220, 100), arrow_points, 2)
                    
                    # Apply alpha and blit
                    arrow_surface.set_alpha(int(200 * arrow_pulse))
                    screen.blit(arrow_surface, (int(line_end_x) - 30, int(line_end_y) - 30))
        
        # Draw objective marker
        target_screen_x = target_x * TILE_SIZE - camera_x + TILE_SIZE // 2
        target_screen_y = target_y * TILE_SIZE - camera_y + TILE_SIZE // 2
        
        if 0 <= target_screen_x <= SCREEN_WIDTH and 0 <= target_screen_y <= SCREEN_HEIGHT - UI_HEIGHT:
            # Large, animated beacon marker
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.5 + 0.5
            
            # Draw expanding rings
            for i in range(3):
                ring_time = (pygame.time.get_ticks() * 0.001 + i * 0.3) % 1.0
                ring_size = int(20 + ring_time * 30)
                ring_alpha = int((1.0 - ring_time) * 150)
                
                ring_surface = pygame.Surface((ring_size * 2, ring_size * 2))
                ring_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(ring_surface, (255, 220, 100), 
                                 (ring_size, ring_size), ring_size, 3)
                ring_surface.set_alpha(ring_alpha)
                screen.blit(ring_surface, 
                           (int(target_screen_x) - ring_size, 
                            int(target_screen_y) - ring_size))
            
            # Central glowing marker
            marker_size = int(25 + pulse * 5)
            
            # Glow effect
            glow_surf = pygame.Surface((80, 80))
            glow_surf.set_colorkey((0, 0, 0))
            for i in range(4):
                size = 40 - i * 8
                alpha = int(60 * pulse / (i + 1))
                pygame.draw.circle(glow_surf, (255, 220, 100), (40, 40), size)
            glow_surf.set_alpha(100)
            screen.blit(glow_surf, (int(target_screen_x) - 40, int(target_screen_y) - 40))
            
            # Main marker
            pygame.draw.circle(screen, (255, 255, 150), 
                             (int(target_screen_x), int(target_screen_y)), 
                             marker_size, 3)
            pygame.draw.circle(screen, (255, 220, 100), 
                             (int(target_screen_x), int(target_screen_y)), 
                             marker_size - 3, 2)
            
            # Floating indicator above
            if not self.game.player_near_objective:
                # Draw floating arrow pointing down
                arrow_y = int(target_screen_y - 40 - abs(math.sin(pygame.time.get_ticks() * 0.002)) * 10)
                arrow_points = [
                    (int(target_screen_x), arrow_y + 15),
                    (int(target_screen_x) - 10, arrow_y),
                    (int(target_screen_x) + 10, arrow_y)
                ]
                pygame.draw.polygon(screen, (255, 255, 150), arrow_points)
                pygame.draw.polygon(screen, (255, 220, 100), arrow_points, 2)
            
    def draw_direction_arrow(self, screen):
        """Draw an arrow pointing to the current objective"""
        current = self.get_current_objective()
        if not current or not current.target_position:
            return
            
        # Calculate direction from player to objective
        player_x = self.game.player.x
        player_y = self.game.player.y
        target_x, target_y = current.target_position
        
        # Calculate angle
        dx = target_x - player_x
        dy = target_y - player_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 1:
            return
            
        # Normalize direction
        dx /= distance
        dy /= distance
        
        # Arrow position (near player but offset)
        arrow_distance = 80
        arrow_x = SCREEN_WIDTH // 2 + dx * arrow_distance
        arrow_y = (SCREEN_HEIGHT - UI_HEIGHT) // 2 + dy * arrow_distance
        
        # Create arrow shape
        arrow_length = 30
        arrow_width = 15
        
        # Calculate arrow points
        angle = math.atan2(dy, dx)
        
        # Tip of arrow
        tip_x = arrow_x + math.cos(angle) * arrow_length
        tip_y = arrow_y + math.sin(angle) * arrow_length
        
        # Base points
        base_angle1 = angle + 2.5  # ~143 degrees
        base_angle2 = angle - 2.5  # ~143 degrees
        base1_x = arrow_x + math.cos(base_angle1) * arrow_width
        base1_y = arrow_y + math.sin(base_angle1) * arrow_width
        base2_x = arrow_x + math.cos(base_angle2) * arrow_width
        base2_y = arrow_y + math.sin(base_angle2) * arrow_width
        
        # Draw arrow with glow effect
        glow_color = (255, 220, 100, 100)
        arrow_color = (255, 255, 150)
        
        # Glow
        for i in range(3):
            glow_points = [
                (tip_x, tip_y),
                (base1_x - i, base1_y - i),
                (base2_x - i, base2_y - i)
            ]
            pygame.draw.polygon(screen, (255, 220, 100, 50), glow_points)
        
        # Main arrow
        arrow_points = [
            (tip_x, tip_y),
            (base1_x, base1_y),
            (base2_x, base2_y)
        ]
        pygame.draw.polygon(screen, arrow_color, arrow_points)
        pygame.draw.polygon(screen, (255, 255, 200), arrow_points, 2)
        
        # Distance indicator
        dist_font = pygame.font.Font(None, 24)
        dist_text = f"{int(distance)}m"
        text_surface = dist_font.render(dist_text, True, (255, 255, 200))
        text_x = arrow_x - text_surface.get_width() // 2
        text_y = arrow_y + 25
        
        # Text background
        text_bg = pygame.Surface((text_surface.get_width() + 10, text_surface.get_height() + 4))
        text_bg.fill((30, 30, 30))
        text_bg.set_alpha(180)
        screen.blit(text_bg, (text_x - 5, text_y - 2))
        screen.blit(text_surface, (text_x, text_y))


class AnimatedPlayer:
    def __init__(self, x, y, tile_size):
        self.x = x  # Tile position
        self.y = y
        self.tile_size = tile_size

        # Player display size (larger than tile)
        self.display_size = int(tile_size * 1.8)  # 80% larger

        # Pixel position for smooth movement
        self.pixel_x = float(x * tile_size)
        self.pixel_y = float(y * tile_size)
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        # Movement
        self.moving = False
        self.move_speed = tile_size / 8.0  # Faster movement (doubled speed)
        self.direction = 'down'  # 'up', 'down', 'left', 'right'
        self.movement_x = 0  # Track current movement direction
        self.movement_y = 0
        self.animation_lock_time = 0  # Prevent rapid animation changes

        # Animation
        self.animations = {}
        self.sprite_cache = {}  # Cache for converted sprites
        self.current_animation = 'idle_down'
        self.animation_frame = 0
        self.animation_speed = 0.08  # Even faster animation for smoother walk
        self.animation_timer = 0

        # Load sprites
        self.load_animations()

    def load_animations(self):
        """Load all character animations with optimization"""
        sprite_dir = os.path.join(os.path.dirname(__file__), 'sprites', 'player')

        # Define which files belong to which animations
        animation_files = {
            'idle_down': ['idle_front.png'],
            'idle_up': ['idle_back.png'],
            'idle_left': ['idle_left.png'],
            'idle_right': ['idle_right.png'],
            'walk_down': ['walk_front_1.png', 'walk_front_2.png'],
            'walk_up': ['walk_back_1.png', 'walk_back_2.png'],
            'walk_left': ['walk_left_1.png', 'walk_left_2.png'],
            'walk_right': ['walk_right_1.png', 'walk_right_2.png']
        }

        # Load each animation
        for anim_name, files in animation_files.items():
            self.animations[anim_name] = []
            for file in files:
                path = os.path.join(sprite_dir, file)
                try:
                    # Load and scale the image
                    img = pygame.image.load(path)
                    # Scale to display size
                    img = pygame.transform.scale(img, (self.display_size, self.display_size))
                    # Convert for better performance
                    img = img.convert_alpha()
                    self.animations[anim_name].append(img)
                except Exception as e:
                    print(f"Warning: Could not load {path}: {e}")
                    # Create placeholder if file missing
                    placeholder = pygame.Surface((self.display_size, self.display_size))
                    placeholder.fill((255, 0, 255))  # Magenta for missing sprites
                    self.animations[anim_name].append(placeholder)

        # Verify all animations loaded
        for anim_name in animation_files:
            if anim_name not in self.animations or not self.animations[anim_name]:
                print(f"Animation {anim_name} failed to load!")

    def move_to(self, new_x, new_y):
        """Start moving to a new tile position"""
        if self.moving:
            return False  # Already moving

        # Set new target position
        self.x = new_x
        self.y = new_y
        self.target_x = float(new_x * self.tile_size)
        self.target_y = float(new_y * self.tile_size)

        # Determine direction based on movement
        dx = self.target_x - self.pixel_x
        dy = self.target_y - self.pixel_y

        # Store movement direction
        self.movement_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
        self.movement_y = 1 if dy > 0 else (-1 if dy < 0 else 0)

        # Determine animation direction with priority system
        # For diagonal movement, prioritize the last different direction
        new_direction = self.direction
        
        if abs(dx) > abs(dy):
            # Horizontal movement is dominant
            new_direction = 'right' if dx > 0 else 'left'
        elif abs(dy) > abs(dx):
            # Vertical movement is dominant
            new_direction = 'down' if dy > 0 else 'up'
        else:
            # Equal movement - keep current direction to avoid flickering
            new_direction = self.direction

        # Only change animation if direction actually changed
        if new_direction != self.direction:
            self.direction = new_direction
            self.set_animation(f'walk_{self.direction}')
            self.animation_lock_time = 0.1  # Lock animation for 100ms
        elif not self.moving:
            # Starting to move in same direction
            self.set_animation(f'walk_{self.direction}')

        self.moving = True
        return True

    def set_animation(self, anim_name):
        """Change current animation"""
        if anim_name != self.current_animation and anim_name in self.animations:
            self.current_animation = anim_name
            self.animation_frame = 0
            self.animation_timer = 0

    def update(self, dt):
        """Update player position and animation"""
        # Update animation lock timer
        if self.animation_lock_time > 0:
            self.animation_lock_time -= dt
            
        # Update movement with proper interpolation
        if self.moving:
            # Calculate movement step based on dt
            step = self.move_speed * dt * 60  # Normalize to 60 FPS
            
            # Move towards target
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y
            
            # Calculate distance
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= step:
                # Arrived at target
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.movement_x = 0
                self.movement_y = 0
                self.set_animation(f'idle_{self.direction}')
            else:
                # Move towards target
                ratio = step / distance
                self.pixel_x += dx * ratio
                self.pixel_y += dy * ratio
                
                # Update direction only if animation isn't locked
                if self.animation_lock_time <= 0:
                    # Check if we need to update direction based on movement
                    if abs(dx) > 0.1 or abs(dy) > 0.1:
                        if abs(dx) > abs(dy) * 1.5:  # Strong horizontal movement
                            new_dir = 'right' if dx > 0 else 'left'
                        elif abs(dy) > abs(dx) * 1.5:  # Strong vertical movement
                            new_dir = 'down' if dy > 0 else 'up'
                        else:
                            new_dir = self.direction  # Keep current for diagonal
                        
                        if new_dir != self.direction:
                            self.direction = new_dir
                            self.set_animation(f'walk_{self.direction}')
                            self.animation_lock_time = 0.15  # Lock for 150ms

        # Update animation
        if self.current_animation in self.animations:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer -= self.animation_speed
                current_anim = self.animations[self.current_animation]
                if len(current_anim) > 0:
                    self.animation_frame = (self.animation_frame + 1) % len(current_anim)

    def draw(self, screen, camera_x, camera_y):
        """Draw the player with proper positioning"""
        # Calculate screen position (center the larger sprite on the tile)
        offset = (self.display_size - self.tile_size) // 2
        screen_x = int(self.pixel_x - camera_x - offset)
        screen_y = int(self.pixel_y - camera_y - offset)

        # Get current frame
        current_anim = self.animations.get(self.current_animation)
        if current_anim and 0 <= self.animation_frame < len(current_anim):
            screen.blit(current_anim[self.animation_frame], (screen_x, screen_y))
        else:
            # Fallback circle if no sprite
            pygame.draw.circle(screen, (255, 0, 0),
                               (int(self.pixel_x - camera_x + self.tile_size // 2),
                                int(self.pixel_y - camera_y + self.tile_size // 2)),
                               self.display_size // 3)


class TileManager:
    def __init__(self):
        self.sheets = {}
        self.tile_cache = {}
        self.tile_data = None
        self.building_data = None
        self.load_tile_selections()
        self.load_sheets()
        # Initialize empty tile type dicts (not used with unique items)
        self.grass_tile_types = {'center': None, 'edges': {}, 'corners': {}, 'inner_corners': {}}
        self.sidewalk_tile_types = {'center': None, 'edges': {}, 'corners': {}, 'inner_corners': {}}

    def load_tile_selections(self):
        """Load tile selections from JSON file (supports both formats)"""
        # Try loading unique items format first
        try:
            with open("tile_selections_unique.json", "r") as f:
                data = json.load(f)
                unique_items = data.get('unique_items', {})
                
                # Convert unique format to old format for compatibility
                self.tile_data = {}
                self.building_data = {}
                
                for name, item in unique_items.items():
                    if item['type'] == 'tile':
                        # Group tiles by a generic category
                        if 'tiles' not in self.tile_data:
                            self.tile_data['tiles'] = []
                        self.tile_data['tiles'].append(item['tile'])
                    else:  # building
                        self.building_data[name] = {
                            'size': item['size'],
                            'tiles': item['tiles'],
                            'category': 'building'
                        }
                
                print(f"Loaded unique items format:")
                print(f"  - {sum(1 for item in unique_items.values() if item['type'] == 'tile')} tiles")
                print(f"  - {sum(1 for item in unique_items.values() if item['type'] == 'building')} buildings")
                return
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print("Error: tile_selections_unique.json is corrupted")
            
        # Try old format
        try:
            with open("tile_selections.json", "r") as f:
                content = f.read()
                if content.strip():  # Only parse if file has content
                    data = json.loads(content)
                    self.tile_data = data.get('tiles', {})
                    self.building_data = data.get('buildings', {})
                    print(f"Loaded old format: {sum(len(tiles) for tiles in self.tile_data.values())} tiles")
                    print(f"Loaded {len(self.building_data)} building definitions")
                else:
                    raise ValueError("Empty file")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            print(f"No valid tile selections found, using defaults")
            # Set default tile data
            self.tile_data = {
                'grass': [('CP_V1.0.4.png', 31, 33)],  # Default grass tile
                'road': [('CP_V1.0.4.png', 32, 44)],   # Default road tile
                'sidewalk': [('CP_V1.0.4.png', 32, 48)] # Default sidewalk tile
            }
            self.building_data = {}

    def analyze_grass_tiles(self):
        """Analyze grass tiles to determine their types (corner, edge, center)"""
        self.grass_tile_types = {
            'center': None,
            'edges': {},
            'corners': {},
            'inner_corners': {}
        }

        if 'grass' not in self.tile_data or not self.tile_data['grass']:
            print("No grass tiles found!")
            return

        grass_tiles = self.tile_data['grass']
        print(f"\nAnalyzing {len(grass_tiles)} grass tiles...")

        # Based on the 3x3 pattern in your tileset:
        # The tiles represent how grass (green) transitions to dirt (brown/sand)
        # Looking at typical autotile patterns:

        for tile in grass_tiles:
            x, y = tile[1], tile[2]

            # Center tile (16, 50) - full grass, no dirt
            if x == 16 and y == 50:
                self.grass_tile_types['center'] = tile
                print(f"  -> Center (full grass): ({x}, {y})")

            # Edge tiles - grass with dirt on one side
            # These show where grass meets dirt in cardinal directions
            elif x == 14 and y == 50:
                self.grass_tile_types['edges']['left'] = tile
                print(f"  -> Left edge: ({x}, {y})")
            elif x == 18 and y == 50:
                self.grass_tile_types['edges']['right'] = tile
                print(f"  -> Right edge: ({x}, {y})")
            elif x == 16 and y == 48:
                self.grass_tile_types['edges']['top'] = tile
                print(f"  -> Top edge: ({x}, {y})")
            elif x == 16 and y == 52:
                self.grass_tile_types['edges']['bottom'] = tile
                print(f"  -> Bottom edge: ({x}, {y})")

            # Outer corners - grass in one corner, dirt elsewhere
            elif x == 14 and y == 48:
                self.grass_tile_types['corners']['top_left'] = tile
                print(f"  -> Top-left corner: ({x}, {y})")
            elif x == 18 and y == 48:
                self.grass_tile_types['corners']['top_right'] = tile
                print(f"  -> Top-right corner: ({x}, {y})")
            elif x == 14 and y == 52:
                self.grass_tile_types['corners']['bottom_left'] = tile
                print(f"  -> Bottom-left corner: ({x}, {y})")
            elif x == 18 and y == 52:
                self.grass_tile_types['corners']['bottom_right'] = tile
                print(f"  -> Bottom-right corner: ({x}, {y})")

        # If we don't have a center tile, use the first available grass tile
        if not self.grass_tile_types['center'] and grass_tiles:
            self.grass_tile_types['center'] = grass_tiles[0]
            print(f"  -> No center tile found, using first tile as default")

        print("\nGrass tile analysis complete:")
        print(f"  Center: {self.grass_tile_types['center'] is not None}")
        print(f"  Edges: {list(self.grass_tile_types['edges'].keys())}")
        print(f"  Corners: {list(self.grass_tile_types['corners'].keys())}")

    def analyze_sidewalk_tiles(self):
        """Analyze sidewalk tiles to determine their types (corner, edge, center)"""
        self.sidewalk_tile_types = {
            'center': None,
            'edges': {},
            'corners': {},
            'inner_corners': {}
        }

        if 'sidewalk' not in self.tile_data or not self.tile_data['sidewalk']:
            print("No sidewalk tiles found!")
            return

        sidewalk_tiles = self.tile_data['sidewalk']
        print(f"\nAnalyzing {len(sidewalk_tiles)} sidewalk tiles...")

        # Based on your tile data, sidewalk tiles are in a 4x4 grid from (13,38) to (19,44)
        # The pattern typically follows:
        # - Center tiles: full sidewalk
        # - Edge tiles: sidewalk meeting road/dirt on one side
        # - Corner tiles: sidewalk in corner configurations

        for tile in sidewalk_tiles:
            x, y = tile[1], tile[2]

            # Center tiles - these appear to be the main body tiles
            if (x, y) in [(15, 40), (17, 40), (15, 42), (17, 42)]:
                if not self.sidewalk_tile_types['center']:
                    self.sidewalk_tile_types['center'] = tile
                print(f"  -> Center sidewalk: ({x}, {y})")

            # Edge tiles
            elif x == 13 and y in [40, 41, 42]:  # Left edge
                self.sidewalk_tile_types['edges']['left'] = tile
                print(f"  -> Left edge: ({x}, {y})")
            elif x == 19 and y in [40, 41, 42]:  # Right edge
                self.sidewalk_tile_types['edges']['right'] = tile
                print(f"  -> Right edge: ({x}, {y})")
            elif y == 38 and x in [15, 16, 17]:  # Top edge
                self.sidewalk_tile_types['edges']['top'] = tile
                print(f"  -> Top edge: ({x}, {y})")
            elif y == 44 and x in [15, 16, 17]:  # Bottom edge
                self.sidewalk_tile_types['edges']['bottom'] = tile
                print(f"  -> Bottom edge: ({x}, {y})")

            # Corner tiles
            elif x == 13 and y == 38:  # Top-left
                self.sidewalk_tile_types['corners']['top_left'] = tile
                print(f"  -> Top-left corner: ({x}, {y})")
            elif x == 19 and y == 38:  # Top-right
                self.sidewalk_tile_types['corners']['top_right'] = tile
                print(f"  -> Top-right corner: ({x}, {y})")
            elif x == 13 and y == 44:  # Bottom-left
                self.sidewalk_tile_types['corners']['bottom_left'] = tile
                print(f"  -> Bottom-left corner: ({x}, {y})")
            elif x == 19 and y == 44:  # Bottom-right
                self.sidewalk_tile_types['corners']['bottom_right'] = tile
                print(f"  -> Bottom-right corner: ({x}, {y})")

        # If we don't have a center tile, use the first available sidewalk tile
        if not self.sidewalk_tile_types['center'] and sidewalk_tiles:
            self.sidewalk_tile_types['center'] = sidewalk_tiles[0]
            print(f"  -> No center tile found, using first tile as default")

        print("\nSidewalk tile analysis complete:")
        print(f"  Center: {self.sidewalk_tile_types['center'] is not None}")
        print(f"  Edges: {list(self.sidewalk_tile_types['edges'].keys())}")
        print(f"  Corners: {list(self.sidewalk_tile_types['corners'].keys())}")

    def load_sheets(self):
        """Load sprite sheets"""
        base_dir = os.path.dirname(__file__)

        # Define sheet paths
        sheet_paths = {
            'CP_V1.0.4.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "CP_V1.0.4_nyknck", "CP_V1.0.4.png"),
            'BL001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "BL001.png"),
            'BD001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "BD001.png"),
            'SL001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "SL001.png")
        }

        for sheet_name, path in sheet_paths.items():
            try:
                self.sheets[sheet_name] = pygame.image.load(path)
                print(f"Loaded {sheet_name}")
            except Exception as e:
                print(f"Failed to load {sheet_name}: {e}")
                # Create placeholder surface
                self.sheets[sheet_name] = pygame.Surface((256, 256))
                self.sheets[sheet_name].fill((255, 0, 255))

    def get_tile(self, sheet_name, x, y):
        """Get a tile from cache or create it"""
        cache_key = (sheet_name, x, y)

        if cache_key in self.tile_cache:
            return self.tile_cache[cache_key]

        if sheet_name not in self.sheets:
            return None

        sheet = self.sheets[sheet_name]
        src_rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                               ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)

        try:
            tile_surface = sheet.subsurface(src_rect)
            scaled_tile = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
            self.tile_cache[cache_key] = scaled_tile
            return scaled_tile
        except ValueError:
            return None

    def get_random_tile(self, category):
        """Get a random tile from a category"""
        if category not in self.tile_data or not self.tile_data[category]:
            return None

        tile_info = random.choice(self.tile_data[category])
        return self.get_tile(tile_info[0], tile_info[1], tile_info[2])

    def get_grass_tile_for_position(self, map_data, x, y):
        """Get appropriate grass tile based on neighboring tiles"""
        if 'grass' not in self.tile_data or not self.tile_data['grass']:
            return None

        # Check all 8 neighbors - but treat buildings as non-grass
        neighbors = {
            'top': y > 0 and self.is_grass_tile(map_data[y - 1][x]),
            'bottom': y < len(map_data) - 1 and self.is_grass_tile(map_data[y + 1][x]),
            'left': x > 0 and self.is_grass_tile(map_data[y][x - 1]),
            'right': x < len(map_data[0]) - 1 and self.is_grass_tile(map_data[y][x + 1]),
            'top_left': y > 0 and x > 0 and self.is_grass_tile(map_data[y - 1][x - 1]),
            'top_right': y > 0 and x < len(map_data[0]) - 1 and self.is_grass_tile(map_data[y - 1][x + 1]),
            'bottom_left': y < len(map_data) - 1 and x > 0 and self.is_grass_tile(map_data[y + 1][x - 1]),
            'bottom_right': y < len(map_data) - 1 and x < len(map_data[0]) - 1 and self.is_grass_tile(
                map_data[y + 1][x + 1])
        }

        # Count orthogonal neighbors
        orthogonal_count = sum([neighbors['top'], neighbors['bottom'], neighbors['left'], neighbors['right']])

        # Determine which tile to use based on neighbors
        tile_info = None

        # All neighbors are grass = use center tile (full grass)
        if orthogonal_count == 4:
            tile_info = self.grass_tile_types['center']

        # Single tile or peninsula (1 or 0 orthogonal neighbors)
        elif orthogonal_count <= 1:
            # Isolated grass tile or end of peninsula - use center
            tile_info = self.grass_tile_types['center']

        # Corners - exactly 2 orthogonal neighbors at 90 degrees
        # These are OUTER corners where grass is surrounded by dirt
        elif orthogonal_count == 2:
            # Check which two sides have grass to determine corner orientation
            if neighbors['bottom'] and neighbors['right'] and not neighbors['top'] and not neighbors['left']:
                # Grass extends down and right = top-left corner piece
                tile_info = self.grass_tile_types['corners'].get('top_left')
            elif neighbors['bottom'] and neighbors['left'] and not neighbors['top'] and not neighbors['right']:
                # Grass extends down and left = top-right corner piece
                tile_info = self.grass_tile_types['corners'].get('top_right')
            elif neighbors['top'] and neighbors['right'] and not neighbors['bottom'] and not neighbors['left']:
                # Grass extends up and right = bottom-left corner piece
                tile_info = self.grass_tile_types['corners'].get('bottom_left')
            elif neighbors['top'] and neighbors['left'] and not neighbors['bottom'] and not neighbors['right']:
                # Grass extends up and left = bottom-right corner piece
                tile_info = self.grass_tile_types['corners'].get('bottom_right')
            # Straight sections (opposite neighbors)
            elif neighbors['top'] and neighbors['bottom']:
                tile_info = self.grass_tile_types['center']
            elif neighbors['left'] and neighbors['right']:
                tile_info = self.grass_tile_types['center']

        # Edges - exactly 3 orthogonal neighbors
        elif orthogonal_count == 3:
            # The edge tiles show the transition on the side WITHOUT grass
            if not neighbors['top']:
                tile_info = self.grass_tile_types['edges'].get('top')
            elif not neighbors['bottom']:
                tile_info = self.grass_tile_types['edges'].get('bottom')
            elif not neighbors['left']:
                tile_info = self.grass_tile_types['edges'].get('left')
            elif not neighbors['right']:
                tile_info = self.grass_tile_types['edges'].get('right')

        # Default to center tile if no specific case matches
        if not tile_info:
            tile_info = self.grass_tile_types['center']

        # If we still don't have a tile, use the first grass tile
        if not tile_info and self.tile_data['grass']:
            tile_info = self.tile_data['grass'][0]

        if tile_info:
            return self.get_tile(tile_info[0], tile_info[1], tile_info[2])
        return None

    def get_sidewalk_tile_for_position(self, map_data, x, y):
        """Get appropriate sidewalk tile based on neighboring tiles"""
        if 'sidewalk' not in self.tile_data or not self.tile_data['sidewalk']:
            return None

        # Check all 8 neighbors
        neighbors = {
            'top': y > 0 and self.is_sidewalk_tile(map_data[y - 1][x]),
            'bottom': y < len(map_data) - 1 and self.is_sidewalk_tile(map_data[y + 1][x]),
            'left': x > 0 and self.is_sidewalk_tile(map_data[y][x - 1]),
            'right': x < len(map_data[0]) - 1 and self.is_sidewalk_tile(map_data[y][x + 1]),
            'top_left': y > 0 and x > 0 and self.is_sidewalk_tile(map_data[y - 1][x - 1]),
            'top_right': y > 0 and x < len(map_data[0]) - 1 and self.is_sidewalk_tile(map_data[y - 1][x + 1]),
            'bottom_left': y < len(map_data) - 1 and x > 0 and self.is_sidewalk_tile(map_data[y + 1][x - 1]),
            'bottom_right': y < len(map_data) - 1 and x < len(map_data[0]) - 1 and self.is_sidewalk_tile(
                map_data[y + 1][x + 1])
        }

        # Count orthogonal neighbors
        orthogonal_count = sum([neighbors['top'], neighbors['bottom'], neighbors['left'], neighbors['right']])

        # Determine which tile to use based on neighbors
        tile_info = None

        # All neighbors are sidewalk = use center tile
        if orthogonal_count == 4:
            tile_info = self.sidewalk_tile_types['center']

        # Single tile or peninsula (1 or 0 orthogonal neighbors)
        elif orthogonal_count <= 1:
            # Isolated sidewalk tile - use center
            tile_info = self.sidewalk_tile_types['center']

        # Corners - exactly 2 orthogonal neighbors at 90 degrees
        elif orthogonal_count == 2:
            # Check which two sides have sidewalk to determine corner orientation
            if neighbors['bottom'] and neighbors['right'] and not neighbors['top'] and not neighbors['left']:
                # Sidewalk extends down and right = top-left corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('top_left')
            elif neighbors['bottom'] and neighbors['left'] and not neighbors['top'] and not neighbors['right']:
                # Sidewalk extends down and left = top-right corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('top_right')
            elif neighbors['top'] and neighbors['right'] and not neighbors['bottom'] and not neighbors['left']:
                # Sidewalk extends up and right = bottom-left corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('bottom_left')
            elif neighbors['top'] and neighbors['left'] and not neighbors['bottom'] and not neighbors['right']:
                # Sidewalk extends up and left = bottom-right corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('bottom_right')
            # Straight sections (opposite neighbors)
            elif neighbors['top'] and neighbors['bottom']:
                tile_info = self.sidewalk_tile_types['center']
            elif neighbors['left'] and neighbors['right']:
                tile_info = self.sidewalk_tile_types['center']

        # Edges - exactly 3 orthogonal neighbors
        elif orthogonal_count == 3:
            # The edge tiles show the transition on the side WITHOUT sidewalk
            if not neighbors['top']:
                tile_info = self.sidewalk_tile_types['edges'].get('top')
            elif not neighbors['bottom']:
                tile_info = self.sidewalk_tile_types['edges'].get('bottom')
            elif not neighbors['left']:
                tile_info = self.sidewalk_tile_types['edges'].get('left')
            elif not neighbors['right']:
                tile_info = self.sidewalk_tile_types['edges'].get('right')

        # Default to center tile if no specific case matches
        if not tile_info:
            tile_info = self.sidewalk_tile_types['center']

        # If we still don't have a tile, use the first sidewalk tile
        if not tile_info and self.tile_data['sidewalk']:
            tile_info = self.tile_data['sidewalk'][0]

        if tile_info:
            return self.get_tile(tile_info[0], tile_info[1], tile_info[2])
        return None

    def is_grass_tile(self, tile_data):
        """Check if a tile is grass (not a building or other type)"""
        if isinstance(tile_data, tuple):
            # Check if it's a tile tuple with grass info
            if tile_data[0] == 'tile':
                # Could check tile_info to determine if it's a grass tile
                # For now, we'll consider tiles that aren't buildings as potentially grass
                return True
            return False  # Buildings are stored as ('building', ...)
        return tile_data == 'grass'

    def is_sidewalk_tile(self, tile_data):
        """Check if a tile is sidewalk (not a building or other type)"""
        if isinstance(tile_data, tuple):
            # Check if it's a tile tuple with sidewalk info
            if tile_data[0] == 'tile':
                # Could check tile_info to determine if it's a sidewalk tile
                # For now, we'll consider tiles that aren't buildings as potentially sidewalk
                return True
            return False  # Buildings are stored as ('building', ...)
        return tile_data == 'sidewalk'


class CityMap:
    def __init__(self):
        # First load a dummy map to get dimensions
        self.load_map_dimensions()
        self.map_data = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.tile_manager = None  # Will be set by Game class
        self.building_tiles = set()
        self.load_from_image()

    def load_map_dimensions(self):
        """Load map dimensions from the PNG file"""
        try:
            city_map_path = os.path.join(os.path.dirname(__file__), "city_map.png")
            map_image = pygame.image.load(city_map_path)
            img_width, img_height = map_image.get_size()

            # Set map dimensions based on image
            # Each pixel in the image represents one tile
            self.width = img_width
            self.height = img_height

            print(f"Map dimensions set to {self.width}x{self.height} from image")
        except Exception as e:
            print(f"Failed to load city_map.png for dimensions: {e}")
            # Fallback dimensions
            self.width = 64
            self.height = 64

    def load_from_visual_map(self):
        """Load city layout from visual map data"""
        try:
            # Try to load the visual map data first
            with open("city_map_data.json", "r") as f:
                map_data = json.load(f)
                
            self.width = map_data['width']
            self.height = map_data['height']
            saved_map = map_data['map_data']
            
            print(f"Loading visual map: {self.width}x{self.height}")
            
            # Initialize map data
            self.map_data = [['dirt' for _ in range(self.width)] for _ in range(self.height)]
            self.building_tiles = set()
            
            # Process each cell
            for y in range(self.height):
                for x in range(self.width):
                    if y < len(saved_map) and x < len(saved_map[y]):
                        cell = saved_map[y][x]
                        if cell:
                            if cell['type'] == 'tile':
                                # With unique items, store the tile data directly
                                tile_info = cell['data']
                                # For now, just store the tile info directly
                                # The renderer will handle displaying it
                                self.map_data[y][x] = ('tile', tile_info)
                                
                            elif cell['type'] in ['building_part', 'building_part_with_bg']:
                                # Part of a building
                                self.building_tiles.add((x, y))
                                
                                # If this building part has a background, store it
                                if cell['type'] == 'building_part_with_bg' and 'background' in cell:
                                    # Store the background tile info along with building info
                                    bg_info = cell['background']
                                    self.map_data[y][x] = ('building_with_bg', 
                                                          cell['building_name'], 
                                                          cell['offset_x'], 
                                                          cell['offset_y'],
                                                          bg_info)
                                else:
                                    # Regular building without background
                                    self.map_data[y][x] = ('building', 
                                                          cell['building_name'], 
                                                          cell['offset_x'], 
                                                          cell['offset_y'])
            
            print(f"Visual map loaded successfully")
            return True
            
        except FileNotFoundError:
            print("No visual map data found, falling back to image loading")
            return False
        except Exception as e:
            print(f"Error loading visual map: {e}")
            return False
    
    def load_from_image(self):
        """Load city layout from city_map.png"""
        # First try to load visual map
        if self.load_from_visual_map():
            return
            
        try:
            # Load the city map image
            city_map_path = os.path.join(os.path.dirname(__file__), "city_map.png")
            map_image = pygame.image.load(city_map_path)

            # Get image dimensions
            img_width, img_height = map_image.get_size()

            print(f"Loading map from city_map.png: {img_width}x{img_height} pixels")

            # Define color mappings to matc
            COLOR_TO_TILE = {
                # Natural terrain
                (34, 139, 34): 'grass',  # Forest green
                (0, 100, 0): 'tree',  # Dark green
                (128, 128, 128): 'rock',  # Gray
                (0, 119, 190): 'water',  # Blue
                (238, 203, 173): 'sand',  # Sandy beige
                (139, 69, 19): 'dirt',  # Brown
                (0, 80, 150): 'deep_water',  # Deep blue

                # Buildings - these will be handled separately
                (139, 90, 43): 'house',  # Brown house
                (192, 192, 192): 'bank',  # Silver/light gray
                (105, 105, 105): 'building',  # Dark gray office
                (70, 130, 180): 'skyscraper',  # Steel blue
                (255, 140, 0): 'store',  # Dark orange

                # Roads and urban
                (32, 32, 32): 'road',  # Asphalt black
                (190, 190, 190): 'sidewalk',  # Light gray concrete
            }

            # Building colors for easy lookup
            BUILDING_COLORS = {
                (139, 90, 43): 'house',
                (192, 192, 192): 'bank',
                (105, 105, 105): 'building',
                (70, 130, 180): 'skyscraper',
                (255, 140, 0): 'store',
            }

            # Initialize all tiles as dirt first
            for y in range(self.height):
                for x in range(self.width):
                    if y < len(self.map_data) and x < len(self.map_data[y]):
                        self.map_data[y][x] = 'dirt'

            # Read pixels directly - 1 pixel = 1 tile
            grass_count = 0
            building_count = 0

            # Track which tiles are part of buildings (to avoid overlaps)
            self.building_tiles = set()

            # First pass: identify all tiles
            for y in range(min(self.height, img_height)):
                for x in range(min(self.width, img_width)):
                    # Skip if this tile is already part of a building
                    if (x, y) in self.building_tiles:
                        continue

                    # Get pixel color
                    color = map_image.get_at((x, y))
                    color_tuple = (color.r, color.g, color.b)

                    # Check if it's a building color
                    if color_tuple in BUILDING_COLORS:
                        # Try to place a building starting from this position
                        building_type = BUILDING_COLORS[color_tuple]
                        if self.try_place_building_by_type(x, y, building_type, map_image, BUILDING_COLORS):
                            building_count += 1
                    else:
                        # Find closest matching color
                        tile_type = 'dirt'  # default
                        min_distance = float('inf')

                        for ref_color, ref_type in COLOR_TO_TILE.items():
                            # Calculate color distance
                            dist = sum((c1 - c2) ** 2 for c1, c2 in zip(color_tuple, ref_color))
                            if dist < min_distance:
                                min_distance = dist
                                tile_type = ref_type

                        # Apply the tile type
                        self.map_data[y][x] = tile_type

                        if tile_type == 'grass':
                            grass_count += 1

            print(f"Map loaded with {grass_count} grass tiles and {building_count} buildings")

        except Exception as e:
            print(f"Failed to load city_map.png: {e}")
            print("Please ensure city_map.png is in the same directory as this script")

    def try_place_building_by_type(self, start_x, start_y, building_type, map_image, building_colors):
        """
        Try to place a building of category `building_type` at (start_x, start_y).
        We look up all definitions in self.tile_manager.building_data with
        data['category'] == building_type, sort them by area (w*h) descending,
        then stamp the first one whose entire rectangle is the same pixel color
        and fits without overlapping existing buildings.
        """
        # No tile data? bail out
        if not hasattr(self, 'tile_manager') or not self.tile_manager:
            return False
        bdata_map = self.tile_manager.building_data
        if not bdata_map:
            return False

        # Gather all candidates of this category
        candidates = [
            (key, data) for key, data in bdata_map.items()
            if data['category'] == building_type
        ]
        if not candidates:
            print(f"Warning: no definitions for category '{building_type}'")
            return False

        # Sort by descending area so larger footprints match first
        candidates.sort(key=lambda item: item[1]['size'][0] * item[1]['size'][1],
                        reverse=True)

        # Grab the pixel color at the top‐left of the candidate
        px0 = map_image.get_at((start_x, start_y))
        expected_color = (px0.r, px0.g, px0.b)

        # Try each building definition
        for building_key, bdef in candidates:
            w, h = bdef['size']

            # 1) does it even fit on the map?
            if start_x + w > self.width or start_y + h > self.height:
                continue

            # 2) are all pixels in that w×h block the same color, and not already placed?
            ok = True
            for dy in range(h):
                for dx in range(w):
                    x, y = start_x + dx, start_y + dy
                    if (x, y) in self.building_tiles:
                        ok = False
                        break
                    c = map_image.get_at((x, y))
                    if (c.r, c.g, c.b) != expected_color:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue

            # 3) stamp it into your map_data and building_tiles
            for dy in range(h):
                for dx in range(w):
                    x, y = start_x + dx, start_y + dy
                    self.building_tiles.add((x, y))
                    self.map_data[y][x] = ('building', building_key, dx, dy)

            print(f"Placed {building_key} at ({start_x}, {start_y})")
            return True

        # nothing matched
        return False

    def smooth_map(self):
        """Smooth the map to remove isolated tiles"""
        temp_map = [row[:] for row in self.map_data]

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                tile_type = self.map_data[y][x]

                # Count neighbors of the same type
                same_neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        if self.map_data[y + dy][x + dx] == tile_type:
                            same_neighbors += 1

                # Remove isolated tiles
                if same_neighbors <= 2:
                    # Change isolated grass to dirt
                    if tile_type == 'grass':
                        temp_map[y][x] = 'dirt'

                # Fill in gaps
                elif tile_type == 'dirt':
                    grass_neighbors = sum(1 for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                                          if (dx != 0 or dy != 0) and
                                          self.map_data[y + dy][x + dx] == 'grass')
                    if grass_neighbors >= 6:
                        temp_map[y][x] = 'grass'

        self.map_data = temp_map


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Builder - Tile Based")
        self.clock = pygame.time.Clock()

        # Initialize components
        self.tile_manager = TileManager()
        self.city_map = CityMap()
        self.city_map.tile_manager = self.tile_manager  # Pass tile manager to city map
        self.city_map.load_from_image()  # Reload with tile manager available

        # Initialize animated player instead of simple position
        self.player = AnimatedPlayer(
            self.city_map.width // 2,
            self.city_map.height // 2,
            TILE_SIZE
        )

        # Initialize objective manager
        self.objective_manager = ObjectiveManager(self)
        self.player_near_objective = False

        # Camera - centered on player initially
        self.camera_x = 0
        self.camera_y = 0
        self.update_camera()

        # UI
        self.font = pygame.font.Font(None, 20)  # Smaller font
        self.show_grid = True

        # Pre-render the map
        self.render_map_cache()
        
        # Start objective system
        self.objective_manager.start()

    def update_camera(self):
        """Update camera to follow player"""
        # Normal camera follows player
        self.camera_x = self.player.pixel_x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.camera_y = self.player.pixel_y - (SCREEN_HEIGHT - UI_HEIGHT) // 2 + TILE_SIZE // 2

        # Clamp camera to map bounds
        max_camera_x = self.city_map.width * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = self.city_map.height * TILE_SIZE - (SCREEN_HEIGHT - UI_HEIGHT)

        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def render_map_cache(self):
        """Pre-render grass tiles with proper edges and buildings"""
        self.map_cache = {}
        tile_count = 0
        building_count = 0

        for y in range(self.city_map.height):
            for x in range(self.city_map.width):
                tile_data = self.city_map.map_data[y][x]

                # Handle building tiles (with or without background)
                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, building_key, offset_x, offset_y, bg_info = tile_data
                        # First, add the background tile to cache
                        bg_tile = self.tile_manager.get_tile(bg_info[0], bg_info[1], bg_info[2])
                        if bg_tile:
                            self.map_cache[(x, y)] = ('background', bg_tile)
                    else:
                        _, building_key, offset_x, offset_y = tile_data
                    
                    building = self.tile_manager.building_data.get(building_key)

                    if building and offset_y < len(building['tiles']) and offset_x < len(building['tiles'][offset_y]):
                        tile_info = building['tiles'][offset_y][offset_x]
                        tile = self.tile_manager.get_tile(tile_info[0], tile_info[1], tile_info[2])
                        if tile:
                           # Store both background and building for rendering
                            if tile_data[0] == 'building_with_bg':
                                self.map_cache[(x, y)] = ('building_with_bg', bg_tile, tile)
                            else:
                                self.map_cache[(x, y)] = ('building', tile)
                            building_count += 1

                # Handle regular tiles - now stored as ('tile', tile_info) tuples
                elif isinstance(tile_data, tuple) and tile_data[0] == 'tile':
                    _, tile_info = tile_data
                    # tile_info is [sheet_name, x, y]
                    tile = self.tile_manager.get_tile(tile_info[0], tile_info[1], tile_info[2])
                    if tile:
                        self.map_cache[(x, y)] = ('tile', tile)
                        tile_count += 1
                # Handle legacy string format (backward compatibility)
                elif tile_data == 'grass':
                    # Get appropriate grass tile based on neighbors
                    tile = self.tile_manager.get_grass_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('grass', tile)
                elif tile_data == 'sidewalk':
                    # Get appropriate sidewalk tile based on neighbors
                    tile = self.tile_manager.get_sidewalk_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('sidewalk', tile)
                elif tile_data == 'road':
                    tile = self.tile_manager.get_random_tile('road')
                    if tile:
                        self.map_cache[(x, y)] = ('road', tile)
                else:
                    # For dirt/sand background
                    self.map_cache[(x, y)] = ('dirt', None)
        
        print(f"Map cache rendered: {tile_count} tiles, {building_count} building parts")

    def handle_input(self):
        """Handle user input"""
        # Don't handle movement if activity is active
        if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
            return
            
        keys = pygame.key.get_pressed()

        # Only move if not already moving (for tile-based movement)
        if not self.player.moving:
            new_x, new_y = self.player.x, self.player.y

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if new_x > 0:
                    new_x -= 1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if new_x < self.city_map.width - 1:
                    new_x += 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                if new_y > 0:
                    new_y -= 1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if new_y < self.city_map.height - 1:
                    new_y += 1

            # Move player if position changed
            if new_x != self.player.x or new_y != self.player.y:
                self.player.move_to(new_x, new_y)

    def draw(self):
        """Draw everything"""
        self.screen.fill(BACKGROUND_COLOR)

        # Calculate visible tile range
        start_x = max(0, int(self.camera_x // TILE_SIZE))
        end_x = min(int((self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 2), self.city_map.width)
        start_y = max(0, int(self.camera_y // TILE_SIZE))
        end_y = min(int((self.camera_y + (SCREEN_HEIGHT - UI_HEIGHT)) // TILE_SIZE + 2), self.city_map.height)

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - int(self.camera_x)
                screen_y = y * TILE_SIZE - int(self.camera_y)

                # Get cached tile
                if (x, y) in self.map_cache:
                    cache_data = self.map_cache[(x, y)]
                    
                    if cache_data[0] == 'dirt':
                        # Draw brown background for dirt
                        pygame.draw.rect(self.screen, (139, 90, 43),
                                         (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif cache_data[0] == 'building_with_bg':
                        # Draw background tile first, then building tile
                        _, bg_tile, building_tile = cache_data
                        if bg_tile:
                            self.screen.blit(bg_tile, (screen_x, screen_y))
                        if building_tile:
                            self.screen.blit(building_tile, (screen_x, screen_y))
                    else:
                        # Regular tiles and buildings
                        tile_type, tile_surface = cache_data
                        if tile_surface:
                            self.screen.blit(tile_surface, (screen_x, screen_y))

                # Draw grid
                if self.show_grid:
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Draw player using animated player
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw objective markers
        self.objective_manager.draw_objective_markers(self.screen, self.camera_x, self.camera_y)

        # Draw UI
        self.draw_ui()
        
        # Draw objective UI
        self.objective_manager.draw_ui(self.screen)

    def draw_ui(self):
        """Draw professional UI overlay"""
        # Minimal bottom-right controls hint
        controls_font = pygame.font.Font(None, 18)
        
        # Create semi-transparent background for controls
        controls_texts = [
            "WASD - Move",
            "E - Interact",
            "G - Toggle Grid"
        ]
        
        controls_height = len(controls_texts) * 20 + 15
        controls_width = 120
        controls_x = SCREEN_WIDTH - controls_width - 20
        controls_y = SCREEN_HEIGHT - controls_height - 20
        
        # Controls background
        controls_bg = pygame.Surface((controls_width, controls_height))
        controls_bg.fill((20, 20, 25))
        controls_bg.set_alpha(120)
        self.screen.blit(controls_bg, (controls_x - 5, controls_y - 5))
        
        # Draw control texts
        for i, text in enumerate(controls_texts):
            text_surface = controls_font.render(text, True, (180, 180, 180))
            self.screen.blit(text_surface, (controls_x, controls_y + i * 20))
        
        # Draw objectives UI from ObjectiveManager
        self.objective_manager.draw_ui(self.screen)

    def run(self):
        """Main game loop"""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_r:
                        # Reload from image
                        self.city_map.load_from_image()
                        self.render_map_cache()
                    elif event.key == pygame.K_e:
                        # Handle E key for interactions
                        if self.player_near_objective:
                            self.objective_manager.complete_current_objective()
                    else:
                        # Pass key events to current activity
                        if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                            self.objective_manager.current_activity.handle_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    # Pass mouse motion to current activity
                    if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        self.objective_manager.current_activity.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Pass mouse clicks to current activity
                    if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        self.objective_manager.current_activity.handle_mouse_click(event.pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Pass mouse release to current activity (for drag and drop)
                    if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        if hasattr(self.objective_manager.current_activity, 'handle_mouse_release'):
                            self.objective_manager.current_activity.handle_mouse_release(event.pos, event.button)

            # Handle input
            self.handle_input()

            # Update player animation
            self.player.update(dt)
            
            # Check if player is near objective
            self.player_near_objective = self.objective_manager.check_player_at_objective(
                self.player.x, self.player.y
            )
            
            # Update objectives
            self.objective_manager.update(dt)

            # Update camera to follow player
            self.update_camera()

            # Draw
            self.draw()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
game.run()