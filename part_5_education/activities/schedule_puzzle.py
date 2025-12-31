"""
Schedule Puzzle Mini-Game
Rearrange schedule to fit work and orientation
Visual calendar puzzle
"""
import pygame

class SchedulePuzzleGame:
    """Drag and rearrange schedule blocks to fit both commitments"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.failed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Time blocks
        self.schedule_blocks = [
            {'name': 'Work Shift', 'duration': 4, 'color': (255, 150, 100), 'moveable': True, 'required': True},
            {'name': 'Orientation', 'duration': 2, 'color': (100, 150, 255), 'moveable': False, 'required': True, 'fixed_time': 11},
            {'name': 'Class', 'duration': 2, 'color': (150, 255, 150), 'moveable': True, 'required': False},
            {'name': 'Study Time', 'duration': 2, 'color': (255, 255, 150), 'moveable': True, 'required': False},
        ]

        # Calendar grid (8am to 8pm = 12 hours)
        self.calendar_hours = list(range(8, 20))  # 8am to 7pm
        self.grid_start_x = 200
        self.grid_start_y = 200
        self.hour_width = 70
        self.block_height = 60

        # Placed blocks
        self.placed_blocks = {}  # {hour: block}

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Create block rectangles
        self.create_block_rects()

        # Solution check
        self.solution_valid = False
        self.check_button = pygame.Rect(540, 520, 200, 50)

    def create_block_rects(self):
        """Create visual rectangles for schedule blocks"""
        start_x = 200
        start_y = 100

        for i, block in enumerate(self.schedule_blocks):
            width = block['duration'] * self.hour_width
            rect = pygame.Rect(start_x + (i * 180), start_y, width, self.block_height)
            block['rect'] = rect
            block['original_rect'] = rect.copy()
            block['placed'] = False

            # Pre-place orientation at 11am
            if block.get('fixed_time'):
                hour_index = block['fixed_time'] - 8  # Convert to grid index
                block['rect'].x = self.grid_start_x + (hour_index * self.hour_width)
                block['rect'].y = self.grid_start_y
                block['placed'] = True
                # Mark hours as occupied
                for h in range(block['fixed_time'], block['fixed_time'] + block['duration']):
                    self.placed_blocks[h] = block

    def handle_event(self, event):
        """Handle schedule block dragging"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check button click
            if self.check_button.collidepoint(mouse_pos):
                self.check_solution()
                return True

            # Check block dragging
            for block in self.schedule_blocks:
                if block['moveable'] and block['rect'].collidepoint(mouse_pos):
                    self.dragging = block
                    self.drag_offset = (
                        block['rect'].x - mouse_pos[0],
                        block['rect'].y - mouse_pos[1]
                    )

                    # Remove from placed blocks if already placed
                    if block['placed']:
                        hours_to_remove = []
                        for hour, placed_block in self.placed_blocks.items():
                            if placed_block == block:
                                hours_to_remove.append(hour)
                        for hour in hours_to_remove:
                            del self.placed_blocks[hour]
                        block['placed'] = False
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Snap to grid if close enough
                grid_y = self.grid_start_y
                if abs(self.dragging['rect'].y - grid_y) < 50:
                    # Find closest hour slot
                    closest_hour = None
                    min_dist = float('inf')

                    for i, hour in enumerate(self.calendar_hours):
                        slot_x = self.grid_start_x + (i * self.hour_width)
                        dist = abs(self.dragging['rect'].x - slot_x)
                        if dist < min_dist:
                            min_dist = dist
                            closest_hour = hour

                    if closest_hour and min_dist < self.hour_width:
                        # Check if space is available
                        can_place = True
                        for h in range(closest_hour, min(closest_hour + self.dragging['duration'], 20)):
                            if h in self.placed_blocks and self.placed_blocks[h] != self.dragging:
                                can_place = False
                                break

                        if can_place and closest_hour + self.dragging['duration'] <= 20:
                            # Place block
                            hour_index = closest_hour - 8
                            self.dragging['rect'].x = self.grid_start_x + (hour_index * self.hour_width)
                            self.dragging['rect'].y = grid_y
                            self.dragging['placed'] = True

                            # Mark hours as occupied
                            for h in range(closest_hour, closest_hour + self.dragging['duration']):
                                self.placed_blocks[h] = self.dragging
                        else:
                            # Return to original position
                            self.dragging['rect'] = self.dragging['original_rect'].copy()
                            self.dragging['placed'] = False
                    else:
                        # Return to original position
                        self.dragging['rect'] = self.dragging['original_rect'].copy()
                        self.dragging['placed'] = False
                else:
                    # Not close to grid
                    if self.dragging['placed']:
                        # Keep in grid
                        pass
                    else:
                        # Return to original
                        self.dragging['rect'] = self.dragging['original_rect'].copy()

                self.dragging = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

        return True

    def check_solution(self):
        """Check if all required blocks are placed without conflicts"""
        # Check if required blocks are placed
        work_placed = False
        orientation_placed = False

        for block in self.schedule_blocks:
            if block['required'] and block['placed']:
                if block['name'] == 'Work Shift':
                    work_placed = True
                elif block['name'] == 'Orientation':
                    orientation_placed = True

        self.solution_valid = work_placed and orientation_placed

        if self.solution_valid:
            self.completed = True
            # Activity completion handled by interior callback
        else:
            self.failed = True
            self.completed = True

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

    def render(self, screen):
        """Render the schedule puzzle interface"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(245)
        overlay.fill((245, 245, 250))
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Schedule Puzzle - Fit Work and Orientation", True, (30, 30, 40))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst_text = "Drag blocks to the timeline. Orientation is MANDATORY at 11am!"
        inst_surface = inst_font.render(inst_text, True, (200, 50, 50))
        screen.blit(inst_surface, (self.SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, 70))

        # Calendar grid
        grid_font = pygame.font.Font(None, 20)

        # Draw time slots
        for i, hour in enumerate(self.calendar_hours):
            x = self.grid_start_x + (i * self.hour_width)
            y = self.grid_start_y

            # Grid cell
            pygame.draw.rect(screen, (240, 240, 245), (x, y, self.hour_width, self.block_height))
            pygame.draw.rect(screen, (180, 180, 190), (x, y, self.hour_width, self.block_height), 1)

            # Hour label
            time_str = f"{hour}:00" if hour <= 12 else f"{hour-12}:00"
            if hour == 12:
                time_str = "12:00"
            label = grid_font.render(time_str, True, (100, 100, 110))
            screen.blit(label, (x + 5, y - 20))

        # Schedule blocks
        block_font = pygame.font.Font(None, 22)
        for block in self.schedule_blocks:
            # Block rectangle
            pygame.draw.rect(screen, block['color'], block['rect'])
            pygame.draw.rect(screen, (80, 80, 90), block['rect'], 2)

            # Block label
            label = block_font.render(block['name'], True, (30, 30, 40))
            label_x = block['rect'].centerx - label.get_width() // 2
            label_y = block['rect'].centery - label.get_height() // 2
            screen.blit(label, (label_x, label_y))

            # Duration indicator
            dur_text = grid_font.render(f"{block['duration']}h", True, (60, 60, 70))
            screen.blit(dur_text, (block['rect'].right - 30, block['rect'].bottom - 20))

            # Fixed indicator
            if not block['moveable']:
                fixed_text = grid_font.render("FIXED", True, (200, 50, 50))
                screen.blit(fixed_text, (block['rect'].x + 5, block['rect'].y + 5))

        # Check solution button
        mouse_pos = pygame.mouse.get_pos()
        btn_color = (100, 150, 200) if self.check_button.collidepoint(mouse_pos) else (80, 130, 180)
        pygame.draw.rect(screen, btn_color, self.check_button)
        pygame.draw.rect(screen, (60, 90, 120), self.check_button, 2)

        btn_font = pygame.font.Font(None, 28)
        btn_text = btn_font.render("Check Schedule", True, (255, 255, 255))
        btn_x = self.check_button.centerx - btn_text.get_width() // 2
        btn_y = self.check_button.centery - btn_text.get_height() // 2
        screen.blit(btn_text, (btn_x, btn_y))

        # Result message
        if self.completed:
            result_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 250, self.SCREEN_HEIGHT // 2 - 50, 500, 150)

            if self.solution_valid:
                pygame.draw.rect(screen, (200, 255, 200), result_rect)
                pygame.draw.rect(screen, (50, 150, 50), result_rect, 3)

                result_font = pygame.font.Font(None, 36)
                result_text = result_font.render("Schedule Complete!", True, (50, 100, 50))
                screen.blit(result_text, (result_rect.centerx - result_text.get_width() // 2, result_rect.y + 30))

                msg = "You can attend both work and orientation!"
                msg_surface = btn_font.render(msg, True, (50, 100, 50))
                screen.blit(msg_surface, (result_rect.centerx - msg_surface.get_width() // 2, result_rect.y + 80))
            else:
                pygame.draw.rect(screen, (255, 200, 200), result_rect)
                pygame.draw.rect(screen, (200, 50, 50), result_rect, 3)

                result_font = pygame.font.Font(None, 36)
                result_text = result_font.render("Schedule Failed!", True, (150, 50, 50))
                screen.blit(result_text, (result_rect.centerx - result_text.get_width() // 2, result_rect.y + 30))

                msg = "Course enrollment will be delayed!"
                msg_surface = btn_font.render(msg, True, (150, 50, 50))
                screen.blit(msg_surface, (result_rect.centerx - msg_surface.get_width() // 2, result_rect.y + 80))

    def start(self):
        """Start the schedule puzzle game"""
        self.active = True
        self.completed = False
        self.failed = False
        self.solution_valid = False
        self.placed_blocks = {}
        self.create_block_rects()  # Reset positions

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False