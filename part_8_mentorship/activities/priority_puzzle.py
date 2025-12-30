"""
Priority Ordering Mini-Game
Drag life options (college, job, trade school, gap year) into priority order
No feedback given - always shows "Incomplete Plan"
"""
import pygame


class PriorityPuzzle:
    """Drag-and-drop priority ordering game"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Life options to prioritize
        self.options = [
            {"name": "College", "icon": "graduation", "color": (100, 150, 200)},
            {"name": "Job", "icon": "briefcase", "color": (150, 200, 100)},
            {"name": "Trade School", "icon": "wrench", "color": (200, 150, 100)},
            {"name": "Gap Year", "icon": "compass", "color": (180, 130, 180)},
        ]

        # Slot positions for priority order
        self.slots = []
        self.slot_width = 160
        self.slot_height = 60
        self.slot_spacing = 20

        # Draggable items
        self.items = []
        self.dragging = None
        self.drag_offset = (0, 0)

        # Placed items (index in slots)
        self.placed = [None, None, None, None]

        # UI state
        self.show_result = False
        self.result_timer = 0

    def start(self):
        """Start the puzzle"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.result_timer = 0
        self.dragging = None
        self.placed = [None, None, None, None]

        # Initialize slots (right side)
        slot_x = self.SCREEN_WIDTH - 200
        slot_start_y = 150
        self.slots = []
        for i in range(4):
            self.slots.append(pygame.Rect(
                slot_x, slot_start_y + i * (self.slot_height + self.slot_spacing),
                self.slot_width, self.slot_height
            ))

        # Initialize draggable items (left side)
        item_x = 100
        item_start_y = 150
        self.items = []
        for i, opt in enumerate(self.options):
            rect = pygame.Rect(
                item_x, item_start_y + i * (self.slot_height + self.slot_spacing),
                self.slot_width, self.slot_height
            )
            self.items.append({
                "option": opt,
                "rect": rect,
                "original_pos": (rect.x, rect.y),
                "in_slot": None
            })

    def stop(self):
        """Stop the puzzle"""
        self.active = False

    def update(self, dt):
        """Update puzzle state"""
        if not self.active:
            return

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 3.0:
                self.completed = True
                self.active = False

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_result:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Check if clicking on an item
            for item in self.items:
                if item["rect"].collidepoint(pos):
                    self.dragging = item
                    self.drag_offset = (
                        pos[0] - item["rect"].x,
                        pos[1] - item["rect"].y
                    )
                    # Remove from slot if placed
                    if item["in_slot"] is not None:
                        self.placed[item["in_slot"]] = None
                        item["in_slot"] = None
                    break

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                pos = event.pos
                self.dragging["rect"].x = pos[0] - self.drag_offset[0]
                self.dragging["rect"].y = pos[1] - self.drag_offset[1]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped in a slot
                dropped_in_slot = False
                for i, slot in enumerate(self.slots):
                    if slot.colliderect(self.dragging["rect"]):
                        if self.placed[i] is None:
                            # Place in slot
                            self.dragging["rect"].x = slot.x
                            self.dragging["rect"].y = slot.y
                            self.dragging["in_slot"] = i
                            self.placed[i] = self.dragging
                            dropped_in_slot = True
                            break

                if not dropped_in_slot:
                    # Return to original position
                    self.dragging["rect"].x = self.dragging["original_pos"][0]
                    self.dragging["rect"].y = self.dragging["original_pos"][1]

                self.dragging = None

                # Check if all slots filled
                if all(p is not None for p in self.placed):
                    self.show_result = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Allow early completion
                self.show_result = True

    def render(self, screen):
        """Render the puzzle"""
        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill((30, 30, 40))
        overlay.set_alpha(240)
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Future Planning Worksheet", True, (200, 200, 210))
        screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst = inst_font.render("Drag options to set your priorities (1 = highest)", True, (150, 150, 160))
        screen.blit(inst, (self.SCREEN_WIDTH // 2 - inst.get_width() // 2, 90))

        # Draw slots with priority labels
        slot_font = pygame.font.Font(None, 28)
        for i, slot in enumerate(self.slots):
            # Slot background
            pygame.draw.rect(screen, (50, 55, 65), slot)
            pygame.draw.rect(screen, (80, 85, 95), slot, 2)

            # Priority number
            label = slot_font.render(f"#{i + 1}", True, (120, 120, 130))
            screen.blit(label, (slot.x - 40, slot.y + 18))

        # Draw items
        item_font = pygame.font.Font(None, 26)
        for item in self.items:
            opt = item["option"]
            rect = item["rect"]

            # Item background
            pygame.draw.rect(screen, opt["color"], rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

            # Item name
            name = item_font.render(opt["name"], True, (255, 255, 255))
            screen.blit(name, (rect.x + 10, rect.y + 20))

        # Left side label
        left_label = slot_font.render("Options:", True, (180, 180, 190))
        screen.blit(left_label, (100, 120))

        # Right side label
        right_label = slot_font.render("Priority:", True, (180, 180, 190))
        screen.blit(right_label, (self.SCREEN_WIDTH - 200, 120))

        # Show result overlay
        if self.show_result:
            result_overlay = pygame.Surface((400, 200))
            result_overlay.fill((40, 35, 50))
            result_rect = result_overlay.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
            screen.blit(result_overlay, result_rect)
            pygame.draw.rect(screen, (100, 80, 80), result_rect, 3)

            # Result text - always "Incomplete Plan"
            result_font = pygame.font.Font(None, 36)
            result_text = result_font.render("Incomplete Plan", True, (200, 150, 150))
            screen.blit(result_text, (result_rect.centerx - result_text.get_width() // 2, result_rect.y + 50))

            # No feedback message
            feedback_font = pygame.font.Font(None, 24)
            feedback = feedback_font.render("No feedback provided.", True, (150, 150, 160))
            screen.blit(feedback, (result_rect.centerx - feedback.get_width() // 2, result_rect.y + 100))

            sub = feedback_font.render("Please contact your ILP case manager.", True, (150, 150, 160))
            screen.blit(sub, (result_rect.centerx - sub.get_width() // 2, result_rect.y + 130))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)
