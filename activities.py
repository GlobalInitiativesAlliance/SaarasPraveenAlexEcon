import pygame
import math
import random
from constants import *


class GameObjective:
    """Represents a game objective/mission that the player must complete"""

    def __init__(self, obj_id, title, description, target_position=None,
                 interaction_text="Press E to interact", requires_interaction=True):
        self.id = obj_id
        self.title = title
        self.description = description
        self.target_position = target_position
        self.interaction_text = interaction_text
        self.requires_interaction = requires_interaction
        self.completed = False
        self.active = False
        self.show_notification = True
        self.notification_timer = 0.0

    def activate(self):
        self.active = True
        self.show_notification = True
        self.notification_timer = 3.0

    def complete(self):
        self.completed = True
        self.active = False

    def update(self, dt):
        if self.notification_timer > 0:
            self.notification_timer -= dt


class Activity:
    """Base class for mini-game activities"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

    def start(self):
        self.active = True

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

    def handle_key(self, key):
        pass

    def handle_mouse_motion(self, pos):
        pass

    def handle_mouse_click(self, pos, button):
        pass

    def complete(self):
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
                "correct": 1
            },
            {
                "question": "Who is responsible for fixing a broken heater in winter?",
                "options": ["Tenant", "Landlord", "Nobody", "City"],
                "correct": 1
            },
            {
                "question": "Can a landlord raise rent in the middle of your lease?",
                "options": ["Yes, anytime", "No, not during lease", "Yes, with 30 days notice", "Only on holidays"],
                "correct": 1
            }
        ]
        self.current_question = 0
        self.selected_option = None
        self.score = 0
        self.show_result = False
        self.result_timer = 0
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.option_offsets = [0, 0, 0, 0]
        self.result_scale = 0.0
        self.entrance_complete = False
        self.option_rects = []

    def start(self):
        super().start()
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.option_offsets = [-200, -250, -300, -350]
        self.result_scale = 0.0
        self.entrance_complete = False

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, self.fade_alpha))
        screen.blit(overlay, (0, 0))

        base_width = 850
        base_height = 550
        box_width = int(base_width * self.box_scale)
        box_height = int(base_height * self.box_scale)
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        if box_width > 0 and box_height > 0:
            for i in range(5):
                color = (35 + i * 3, 35 + i * 3, 40 + i * 3)
                pygame.draw.rect(screen, color,
                                 (box_x + i, box_y + i, box_width - i * 2, box_height - i * 2))

            pygame.draw.rect(screen, (25, 25, 30), (box_x + 5, box_y + 5, box_width - 10, box_height - 10))

            border_color = (255, 220, 100) if not self.show_result else (
                (100, 255, 100) if self.selected_option == self.questions[self.current_question]["correct"] else (
                255, 100, 100)) if self.current_question < len(self.questions) else (100, 255, 100)
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 4)

            corner_size = 20
            for corner_x, corner_y in [(box_x, box_y), (box_x + box_width - corner_size, box_y),
                                       (box_x, box_y + box_height - corner_size),
                                       (box_x + box_width - corner_size, box_y + box_height - corner_size)]:
                pygame.draw.lines(screen, border_color, False,
                                  [(corner_x, corner_y + corner_size), (corner_x, corner_y),
                                   (corner_x + corner_size, corner_y)], 3)

            if self.entrance_complete:
                title_font = pygame.font.Font(None, 52)
                title_y = box_y + 40

                title_shadow = title_font.render("Tenant Rights Quiz", True, (10, 10, 10))
                screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 3, title_y + 3))
                title = title_font.render("Tenant Rights Quiz", True, (255, 220, 100))
                screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, title_y))

        if self.current_question < len(self.questions):
            q_data = self.questions[self.current_question]

            progress_y = box_y + 100
            progress_width = 600
            progress_x = SCREEN_WIDTH // 2 - progress_width // 2
            progress_height = 8

            pygame.draw.rect(screen, (50, 50, 60), (progress_x, progress_y, progress_width, progress_height))
            filled_width = int(progress_width * (self.current_question + 1) / len(self.questions))
            pygame.draw.rect(screen, (100, 220, 100), (progress_x, progress_y, filled_width, progress_height))

            num_font = pygame.font.Font(None, 28)
            num_text = num_font.render(f"Question {self.current_question + 1} of {len(self.questions)}",
                                       True, (180, 180, 190))
            num_x = SCREEN_WIDTH // 2 - num_text.get_width() // 2
            screen.blit(num_text, (num_x, progress_y + 20))

            q_font = pygame.font.Font(None, 36)
            question_y = progress_y + 60

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

            for i, line in enumerate(lines):
                q_surface = q_font.render(line, True, (255, 255, 255))
                q_x = SCREEN_WIDTH // 2 - q_surface.get_width() // 2
                screen.blit(q_surface, (q_x, question_y + i * 40))

            options_start_y = question_y + len(lines) * 40 + 40
            option_height = 45
            option_spacing = 10
            option_width = 600
            option_x = SCREEN_WIDTH // 2 - option_width // 2

            self.option_rects = []

            for i, option in enumerate(q_data["options"]):
                option_y = options_start_y + i * (option_height + option_spacing)
                option_rect = (option_x, option_y, option_width, option_height)
                self.option_rects.append(option_rect)

                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovering = (option_x <= mouse_x <= option_x + option_width and
                               option_y <= mouse_y <= option_y + option_height)

                if i == self.selected_option:
                    pygame.draw.rect(screen, (45, 45, 55), option_rect)
                    pygame.draw.rect(screen, (255, 220, 100), option_rect, 3)
                elif is_hovering and not self.show_result:
                    pygame.draw.rect(screen, (40, 40, 50), option_rect)
                    pygame.draw.rect(screen, (150, 150, 180), option_rect, 2)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.draw.rect(screen, (35, 35, 45), option_rect)
                    pygame.draw.rect(screen, (80, 80, 90), option_rect, 1)

                circle_x = option_x + 30
                circle_y = option_y + option_height // 2
                circle_color = (255, 220, 100) if i == self.selected_option else (150, 150, 180) if is_hovering else (
                100, 100, 120)
                pygame.draw.circle(screen, circle_color, (circle_x, circle_y), 18, 2)

                letter_font = pygame.font.Font(None, 28)
                letter = chr(65 + i)
                letter_surface = letter_font.render(letter, True, circle_color)
                letter_x = circle_x - letter_surface.get_width() // 2
                letter_y = circle_y - letter_surface.get_height() // 2
                screen.blit(letter_surface, (letter_x, letter_y))

                opt_font = pygame.font.Font(None, 30)
                opt_text = opt_font.render(option, True,
                                           (255, 255, 255) if i == self.selected_option else (220, 220, 220))
                text_y = option_y + (option_height - opt_text.get_height()) // 2
                screen.blit(opt_text, (circle_x + 35, text_y))

            if self.selected_option is not None and not self.show_result:
                submit_width = 200
                submit_height = 45
                submit_x = SCREEN_WIDTH // 2 - submit_width // 2
                submit_y = options_start_y + 4 * (option_height + option_spacing) + 20

                self.submit_button_rect = (submit_x, submit_y, submit_width, submit_height)

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
                self.submit_button_rect = None

            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Click an option to select • Click Submit to confirm",
                                         True, (180, 180, 180))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 40))

            if not any(option_x <= mouse_x <= option_x + option_width and
                       option_y - 5 <= mouse_y <= option_y - 5 + option_height
                       for option_x, option_y, option_width, option_height in self.option_rects):
                if not (self.selected_option is not None and not self.show_result and
                        submit_x <= mouse_x <= submit_x + submit_width and
                        submit_y <= mouse_y <= submit_y + submit_height):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

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
            if self.entrance_complete:
                percentage = int((self.score / len(self.questions)) * 100)

                complete_font = pygame.font.Font(None, 56)
                complete_text = "Quiz Complete!"
                complete_color = (255, 220, 100)
                complete_surface = complete_font.render(complete_text, True, complete_color)
                screen.blit(complete_surface, (SCREEN_WIDTH // 2 - complete_surface.get_width() // 2, box_y + 120))

                circle_x = SCREEN_WIDTH // 2
                circle_y = box_y + 220
                circle_radius = 60

                for i in range(5):
                    color_fade = max(0, 255 - i * 30)
                    if percentage >= 100:
                        circle_color = (100, color_fade, 100)
                    elif percentage >= 67:
                        circle_color = (color_fade, color_fade, 100)
                    else:
                        circle_color = (color_fade, 100, 100)
                    pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius - i * 10, 2)

                score_font = pygame.font.Font(None, 48)
                score_text = f"{self.score}/{len(self.questions)}"
                score_surface = score_font.render(score_text, True, (255, 255, 255))
                screen.blit(score_surface, (circle_x - score_surface.get_width() // 2, circle_y - 15))

                percent_font = pygame.font.Font(None, 36)
                percent_text = f"{percentage}%"
                percent_surface = percent_font.render(percent_text, True, (200, 200, 200))
                screen.blit(percent_surface, (circle_x - percent_surface.get_width() // 2, circle_y + 20))

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

                continue_width = 200
                continue_height = 50
                continue_x = SCREEN_WIDTH // 2 - continue_width // 2
                continue_y = box_y + 380

                mouse_x, mouse_y = pygame.mouse.get_pos()
                continue_hover = (continue_x <= mouse_x <= continue_x + continue_width and
                                  continue_y <= mouse_y <= continue_y + continue_height)

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
        super().handle_mouse_click(pos, button)

        if not self.active or not self.entrance_complete:
            return

        if button == 1:
            mouse_x, mouse_y = pos

            if self.current_question >= len(self.questions):
                box_y = SCREEN_HEIGHT // 2 - 300
                continue_x = SCREEN_WIDTH // 2 - 100
                continue_y = box_y + 380
                if (continue_x <= mouse_x <= continue_x + 200 and
                        continue_y <= mouse_y <= continue_y + 50):
                    self.complete()
                return

            if not self.show_result:
                for i, (opt_x, opt_y, opt_w, opt_h) in enumerate(self.option_rects):
                    if (opt_x <= mouse_x <= opt_x + opt_w and
                            opt_y <= mouse_y <= opt_y + opt_h):
                        self.selected_option = i
                        return

                if self.submit_button_rect is not None:
                    submit_x, submit_y, submit_width, submit_height = self.submit_button_rect
                    if (submit_x <= mouse_x <= submit_x + submit_width and
                            submit_y <= mouse_y <= submit_y + submit_height):
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
                if self.selected_option == self.questions[self.current_question]["correct"]:
                    self.score += 1
                self.show_result = True
                self.result_timer = 2.0

    def update(self, dt):
        if not self.entrance_complete:
            self.fade_alpha = min(255, self.fade_alpha + dt * 500)
            self.box_scale = min(1.0, self.box_scale + dt * 3)

            for i in range(4):
                target = 0
                self.option_offsets[i] += (target - self.option_offsets[i]) * dt * 8

            if self.box_scale >= 1.0:
                self.entrance_complete = True
                self.option_offsets = [-200, -250, -300, -350]
        else:
            for i in range(4):
                self.option_offsets[i] += (0 - self.option_offsets[i]) * dt * 10

        if self.show_result:
            self.result_scale = min(1.0, self.result_scale + dt * 5)
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.current_question += 1
                self.selected_option = None
                self.show_result = False
                self.result_scale = 0.0
                self.option_offsets = [-200, -250, -300, -350]

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

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (30, 30, 35), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)

        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pack Your Belongings", True, (255, 220, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

        progress_text = f"Packed: {len(self.packed_items)}/{len(self.items)}"
        prog_font = pygame.font.Font(None, 32)
        prog_surface = prog_font.render(progress_text, True, (200, 200, 200))
        screen.blit(prog_surface, (box_x + 40, box_y + 100))

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
        self.stage = 0
        self.tips_learned = []

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        box_width = 800
        box_height = 600
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 150, 200), (box_x, box_y, box_width, box_height), 3)

        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 28)

        title = title_font.render("Life Skills Workshop", True, (150, 200, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

        if self.stage == 0:
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

            header_font = pygame.font.Font(None, 40)
            header = header_font.render(current_tip["title"], True, (255, 220, 100))
            screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, box_y + 100))

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

            nav_text = f"Tip {self.stage} of 3"
            nav = small_font.render(nav_text, True, (150, 150, 150))
            screen.blit(nav, (SCREEN_WIDTH // 2 - nav.get_width() // 2, box_y + 450))

            cont_text = text_font.render("Click or press SPACE to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 500))

        else:
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
        self.stage = 0

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        box_width = 700
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        if self.stage == 0:
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

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (30, 30, 35), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 200, 100), (box_x, box_y, box_width, box_height), 3)

        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Required Documents", True, (100, 200, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

        doc_font = pygame.font.Font(None, 32)
        y_offset = box_y + 120

        for i, (doc_name, is_checked) in enumerate(self.documents.items()):
            checkbox_x = box_x + 60
            checkbox_y = y_offset - 5
            checkbox_size = 30

            pygame.draw.rect(screen, (255, 255, 255),
                             (checkbox_x, checkbox_y, checkbox_size, checkbox_size), 2)

            if is_checked:
                pygame.draw.line(screen, (100, 255, 100),
                                 (checkbox_x + 5, checkbox_y + 15),
                                 (checkbox_x + 12, checkbox_y + 22), 3)
                pygame.draw.line(screen, (100, 255, 100),
                                 (checkbox_x + 12, checkbox_y + 22),
                                 (checkbox_x + 25, checkbox_y + 8), 3)

            color = (100, 255, 100) if is_checked else (255, 255, 255)
            text = doc_font.render(f"{i + 1}. {doc_name}", True, color)
            screen.blit(text, (checkbox_x + 50, y_offset))
            y_offset += 60

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
                "options": ["Leave immediately", "Ask for the reason in writing", "Argue with your boss",
                            "Call the police"],
                "correct": 1
            },
            {
                "question": "Are you entitled to your final paycheck?",
                "options": ["No, you were fired", "Yes, for all hours worked", "Only if you quit",
                            "Depends on the boss"],
                "correct": 1
            },
            {
                "question": "What benefits might you qualify for after being fired?",
                "options": ["Nothing", "Unemployment insurance", "Free housing", "Company car"],
                "correct": 1
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

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, self.fade_alpha))
        screen.blit(overlay, (0, 0))

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
            title_font = pygame.font.Font(None, 48)
            title = title_font.render("Employment Rights Quiz", True, (200, 100, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

            if self.current_question < len(self.questions):
                question = self.questions[self.current_question]

                q_font = pygame.font.Font(None, 32)
                q_text = q_font.render(question["question"], True, (255, 255, 255))
                screen.blit(q_text, (SCREEN_WIDTH // 2 - q_text.get_width() // 2, box_y + 120))

                opt_font = pygame.font.Font(None, 28)
                y_offset = box_y + 200

                self.option_rects = []

                for i, option in enumerate(question["options"]):
                    option_rect = pygame.Rect(box_x + 80, y_offset - 10, box_width - 160, 45)
                    self.option_rects.append(option_rect)

                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering = option_rect.collidepoint(mouse_pos) and not self.show_result

                    if is_hovering:
                        pygame.draw.rect(screen, (40, 40, 50), option_rect, border_radius=5)
                        pygame.draw.rect(screen, (100, 100, 120), option_rect, 2, border_radius=5)

                    color = (255, 255, 255)
                    if self.selected_option == i:
                        color = (255, 220, 100)
                    if self.show_result:
                        if i == question["correct"]:
                            color = (100, 255, 100)
                        elif i == self.selected_option:
                            color = (255, 100, 100)

                    opt_text = opt_font.render(f"{i + 1}. {option}", True, color)
                    screen.blit(opt_text, (box_x + 100, y_offset))
                    y_offset += 50

                if not self.show_result:
                    submit_width = 150
                    submit_height = 40
                    submit_x = SCREEN_WIDTH // 2 - submit_width // 2
                    submit_y = box_y + box_height - 80
                    self.submit_rect = pygame.Rect(submit_x, submit_y, submit_width, submit_height)

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

                    inst_font = pygame.font.Font(None, 20)
                    inst_text = inst_font.render("Click an option or press 1-4 to select", True, (180, 180, 180))
                    screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 25))
            else:
                score_font = pygame.font.Font(None, 48)
                score_text = score_font.render(f"Score: {self.score}/{len(self.questions)}", True, (100, 255, 100))
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, box_y + 180))

                continue_width = 200
                continue_height = 50
                continue_x = SCREEN_WIDTH // 2 - continue_width // 2
                continue_y = box_y + 280
                self.continue_rect = pygame.Rect(continue_x, continue_y, continue_width, continue_height)

                mouse_pos = pygame.mouse.get_pos()
                is_hovering = self.continue_rect.collidepoint(mouse_pos)

                button_color = (120, 170, 255) if is_hovering else (100, 150, 255)
                pygame.draw.rect(screen, button_color, self.continue_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 255, 255), self.continue_rect, 2, border_radius=5)

                button_font = pygame.font.Font(None, 32)
                button_text = button_font.render("Continue", True, (255, 255, 255))
                text_rect = button_text.get_rect(center=self.continue_rect.center)
                screen.blit(button_text, text_rect)

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
                if self.selected_option == self.questions[self.current_question]["correct"]:
                    self.score += 1
                self.show_result = True
                self.result_timer = 2.0

        elif self.current_question >= len(self.questions) and key == pygame.K_RETURN:
            self.complete()

    def handle_mouse_click(self, pos, button):
        if not self.active or not self.entrance_complete or button != 1:
            return

        if self.current_question < len(self.questions) and not self.show_result:
            for i, rect in enumerate(getattr(self, 'option_rects', [])):
                if rect.collidepoint(pos):
                    self.selected_option = i
                    return

            if hasattr(self, 'submit_rect') and self.submit_rect.collidepoint(pos):
                if self.selected_option is not None:
                    if self.selected_option == self.questions[self.current_question]["correct"]:
                        self.score += 1
                    self.show_result = True
                    self.result_timer = 2.0

        elif self.current_question >= len(self.questions):
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
            inst_text = inst_font.render("Type to fill fields, TAB to next field, ENTER to submit", True,
                                         (150, 150, 150))
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
            req_text = req_font.render("Order: " + ", ".join(self.current_pizza["required_toppings"]), True,
                                       (255, 255, 255))
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
                        pygame.draw.rect(screen, (50, 200, 50), (x - 5, y - 5, 10, 10))

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

                    button_text = req_font.render(f"{i + 1}. {topping}", True, (255, 255, 255))
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
                inst_text = req_font.render("Click toppings or press 1-4, click Bake or press SPACE", True,
                                            (200, 200, 200))
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
            num_text = item_font.render(f"Press {i + 1}", True, (150, 150, 150))
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

            question_text = context_font.render("How do you want to handle this with your manager?", True,
                                                (255, 255, 255))
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




        # Add all other activity classes here following the same pattern...
        # Including: TransitionScene, SchoolEmergencyScene, FiringScene, PizzaMakingGame,
        # BurgerMakingGame, DocumentChecklistWork, BurgerTrainingActivity, JobListingsActivity,
        # ManagerNoticeActivity, PanicSceneActivity, ILPOfficerCallActivity, ManagerChoiceActivity
        # (Due to length, I'm showing the pattern - you would copy all these from the original file)