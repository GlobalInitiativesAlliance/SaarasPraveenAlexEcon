"""
Task Prioritization Mini-Game
Floating tasks overwhelm the screen - prioritize them before the timer runs out
Demonstrates decision paralysis and task overwhelm
"""
import pygame
import random
import math

class TaskPrioritizationGame:
    """Prioritize floating tasks under time pressure"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 30.0  # seconds
        self.time_remaining = self.time_limit

        # Tasks that float around
        self.tasks = [
            {'name': 'College Application', 'urgency': 'HIGH', 'prioritized': False},
            {'name': 'Work Shift Tomorrow', 'urgency': 'HIGH', 'prioritized': False},
            {'name': 'Pay Electric Bill', 'urgency': 'MEDIUM', 'prioritized': False},
            {'name': 'Grocery Shopping', 'urgency': 'MEDIUM', 'prioritized': False},
            {'name': 'Call Case Worker', 'urgency': 'MEDIUM', 'prioritized': False},
            {'name': 'Laundry', 'urgency': 'LOW', 'prioritized': False},
            {'name': 'Clean Apartment', 'urgency': 'LOW', 'prioritized': False},
            {'name': 'Text Friend Back', 'urgency': 'LOW', 'prioritized': False},
        ]

        # Priority slots
        self.priority_slots = [
            {'label': '#1 Priority', 'rect': None, 'task': None},
            {'label': '#2 Priority', 'rect': None, 'task': None},
            {'label': '#3 Priority', 'rect': None, 'task': None},
        ]

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Animation
        self.float_offsets = []
        self.float_speeds = []

        # Result state
        self.show_result = False
        self.result_timer = 0
        self.success = False

        # Initialize positions
        self.initialize_tasks()

    def initialize_tasks(self):
        """Create floating task positions"""
        self.float_offsets = []
        self.float_speeds = []

        for i, task in enumerate(self.tasks):
            # Random starting position in left area
            x = random.randint(100, 500)
            y = random.randint(150, 500)
            task['rect'] = pygame.Rect(x, y, 180, 50)
            task['original_pos'] = (x, y)

            # Random float pattern
            self.float_offsets.append(random.uniform(0, math.pi * 2))
            self.float_speeds.append(random.uniform(0.02, 0.05))

        # Priority slot positions
        slot_x = 900
        slot_y = 200
        for i, slot in enumerate(self.priority_slots):
            slot['rect'] = pygame.Rect(slot_x, slot_y + i * 120, 250, 80)

    def handle_event(self, event):
        """Handle task dragging"""
        if not self.active or self.completed:
            return False

        if self.show_result:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.completed = True
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            for task in self.tasks:
                if not task['prioritized'] and task['rect'].collidepoint(mouse_pos):
                    self.dragging = task
                    self.drag_offset = (
                        task['rect'].x - mouse_pos[0],
                        task['rect'].y - mouse_pos[1]
                    )
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped in a priority slot
                placed = False
                for slot in self.priority_slots:
                    if slot['task'] is None and slot['rect'].colliderect(self.dragging['rect']):
                        slot['task'] = self.dragging
                        self.dragging['prioritized'] = True
                        # Center in slot
                        self.dragging['rect'].center = slot['rect'].center
                        placed = True
                        break

                if not placed:
                    # Return to floating
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

                # Check if all slots filled
                if all(slot['task'] is not None for slot in self.priority_slots):
                    self.trigger_result()

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

        return True

    def trigger_result(self):
        """Show the result"""
        self.show_result = True
        self.result_timer = 180

        # Check if high urgency tasks were prioritized
        high_urgency_prioritized = 0
        for slot in self.priority_slots:
            if slot['task'] and slot['task']['urgency'] == 'HIGH':
                high_urgency_prioritized += 1

        self.success = high_urgency_prioritized >= 1

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        if self.show_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.completed = True
            return

        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.show_result = True
            self.success = False
            self.result_timer = 180
            return

        # Update floating animation for unprioritized tasks
        for i, task in enumerate(self.tasks):
            if not task['prioritized'] and task != self.dragging:
                self.float_offsets[i] += self.float_speeds[i]
                offset_x = math.sin(self.float_offsets[i]) * 15
                offset_y = math.cos(self.float_offsets[i] * 0.7) * 10
                task['rect'].x = task['original_pos'][0] + offset_x
                task['rect'].y = task['original_pos'][1] + offset_y

    def render(self, screen):
        """Render the task prioritization interface"""
        if not self.active:
            return

        # Background with slight chaos effect
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(250)

        # Background gets more red as time runs out
        red_factor = max(0, 1 - (self.time_remaining / self.time_limit))
        bg_color = (240 + int(15 * red_factor), 238 - int(20 * red_factor), 235 - int(20 * red_factor))
        overlay.fill(bg_color)
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Prioritize Your Tasks!", True, (40, 40, 50))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

        # Timer with urgency coloring
        timer_font = pygame.font.Font(None, 36)
        timer_color = (50, 150, 50)
        if self.time_remaining < 15:
            timer_color = (200, 150, 50)
        if self.time_remaining < 8:
            timer_color = (200, 50, 50)
        timer_text = timer_font.render(f"Time: {int(self.time_remaining)}s", True, timer_color)
        screen.blit(timer_text, (self.SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 80))

        if not self.show_result:
            # Instruction
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Drag the 3 most important tasks to priority slots", True, (100, 100, 110))
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 115))

            # Priority slots
            self.render_priority_slots(screen)

            # Floating tasks
            self.render_tasks(screen)

            # Overwhelm indicator
            unprioritized = sum(1 for t in self.tasks if not t['prioritized'])
            if unprioritized > 5:
                overwhelm_font = pygame.font.Font(None, 20)
                overwhelm_text = overwhelm_font.render(f"{unprioritized} tasks competing for attention...", True, (150, 100, 100))
                screen.blit(overwhelm_text, (200, 580))

        else:
            self.render_result(screen)

    def render_priority_slots(self, screen):
        """Render the priority slots"""
        slot_font = pygame.font.Font(None, 28)

        for slot in self.priority_slots:
            # Slot background
            if slot['task']:
                color = (200, 255, 200)
                border_color = (100, 200, 100)
            else:
                color = (250, 250, 255)
                border_color = (150, 150, 200)

            pygame.draw.rect(screen, color, slot['rect'])
            pygame.draw.rect(screen, border_color, slot['rect'], 3)

            # Slot label
            label = slot_font.render(slot['label'], True, (80, 80, 100))
            screen.blit(label, (slot['rect'].x + 10, slot['rect'].y - 25))

            # Show task if placed
            if slot['task']:
                task_font = pygame.font.Font(None, 24)
                task_text = task_font.render(slot['task']['name'], True, (40, 40, 50))
                text_x = slot['rect'].centerx - task_text.get_width() // 2
                screen.blit(task_text, (text_x, slot['rect'].centery - 10))

    def render_tasks(self, screen):
        """Render floating task cards"""
        task_font = pygame.font.Font(None, 20)
        urgency_font = pygame.font.Font(None, 16)

        for task in self.tasks:
            if task['prioritized']:
                continue

            # Task card with urgency coloring
            if task['urgency'] == 'HIGH':
                color = (255, 220, 220)
                border_color = (200, 100, 100)
            elif task['urgency'] == 'MEDIUM':
                color = (255, 245, 220)
                border_color = (200, 180, 100)
            else:
                color = (220, 240, 255)
                border_color = (100, 150, 200)

            if self.dragging == task:
                color = (255, 255, 200)
                border_color = (200, 200, 100)

            pygame.draw.rect(screen, color, task['rect'])
            pygame.draw.rect(screen, border_color, task['rect'], 2)

            # Task name
            name_text = task_font.render(task['name'], True, (40, 40, 50))
            name_x = task['rect'].centerx - name_text.get_width() // 2
            screen.blit(name_text, (name_x, task['rect'].y + 10))

            # Urgency label
            urgency_color = (200, 50, 50) if task['urgency'] == 'HIGH' else (150, 120, 50) if task['urgency'] == 'MEDIUM' else (80, 120, 150)
            urgency_text = urgency_font.render(task['urgency'], True, urgency_color)
            urgency_x = task['rect'].centerx - urgency_text.get_width() // 2
            screen.blit(urgency_text, (urgency_x, task['rect'].y + 32))

    def render_result(self, screen):
        """Render the result screen"""
        panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 350, 200, 700, 300)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect)

        if self.success:
            pygame.draw.rect(screen, (100, 200, 100), panel_rect, 4)

            result_font = pygame.font.Font(None, 36)
            result_text = result_font.render("You managed to prioritize!", True, (50, 150, 50))
        else:
            pygame.draw.rect(screen, (200, 100, 100), panel_rect, 4)

            result_font = pygame.font.Font(None, 36)
            if self.time_remaining <= 0:
                result_text = result_font.render("Time ran out - too many tasks!", True, (200, 50, 50))
            else:
                result_text = result_font.render("Important tasks were missed", True, (200, 100, 50))

        result_x = panel_rect.centerx - result_text.get_width() // 2
        screen.blit(result_text, (result_x, panel_rect.y + 40))

        # Show what was prioritized
        priority_font = pygame.font.Font(None, 24)
        y = panel_rect.y + 100

        screen.blit(priority_font.render("Your priorities:", True, (80, 80, 90)), (panel_rect.x + 50, y))
        y += 30

        for i, slot in enumerate(self.priority_slots):
            if slot['task']:
                text = f"#{i+1}: {slot['task']['name']} ({slot['task']['urgency']})"
            else:
                text = f"#{i+1}: (empty)"
            slot_text = priority_font.render(text, True, (60, 60, 70))
            screen.blit(slot_text, (panel_rect.x + 70, y))
            y += 25

        # Commentary
        comment_font = pygame.font.Font(None, 22)
        comments = [
            "When everything feels urgent, nothing gets done.",
            "Decision paralysis is real for foster youth managing alone."
        ]

        y = panel_rect.y + 230
        for comment in comments:
            comment_surface = comment_font.render(comment, True, (100, 100, 110))
            comment_x = panel_rect.centerx - comment_surface.get_width() // 2
            screen.blit(comment_surface, (comment_x, y))
            y += 22

        # Continue prompt
        if self.result_timer < 120:
            prompt_font = pygame.font.Font(None, 22)
            prompt = "Press any key to continue..."
            prompt_surface = prompt_font.render(prompt, True, (120, 120, 130))
            prompt_x = panel_rect.centerx - prompt_surface.get_width() // 2
            screen.blit(prompt_surface, (prompt_x, panel_rect.bottom - 25))

    def start(self):
        """Start the task prioritization game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.success = False
        self.time_remaining = self.time_limit
        self.result_timer = 0

        # Reset tasks
        for task in self.tasks:
            task['prioritized'] = False
            task['rect'].x = task['original_pos'][0]
            task['rect'].y = task['original_pos'][1]

        # Reset slots
        for slot in self.priority_slots:
            slot['task'] = None

        # Randomize positions
        self.initialize_tasks()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)
