"""
Balance Scale Puzzle
Place "income," "education," and "housing" blocks to balance the scale
If puzzle fails, blocks fall and "future plan collapsed" message appears
"""
import pygame
import math


class BalancePuzzle:
    """Balance scale puzzle with life priority blocks"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Blocks to balance
        self.blocks = [
            {"name": "Income", "weight": 3, "color": (100, 180, 100), "placed": False, "side": None},
            {"name": "Education", "weight": 4, "color": (100, 150, 200), "placed": False, "side": None},
            {"name": "Housing", "weight": 5, "color": (200, 150, 100), "placed": False, "side": None},
        ]

        # Block positions and rects
        self.block_rects = []
        self.block_width = 100
        self.block_height = 50

        # Scale state
        self.left_weight = 0
        self.right_weight = 0
        self.scale_angle = 0  # radians, 0 = balanced
        self.max_angle = 0.4  # max tilt before collapse

        # Dragging
        self.dragging = None
        self.drag_offset = (0, 0)

        # Drop zones
        self.left_zone = None
        self.right_zone = None

        # Game state
        self.collapsed = False
        self.balanced = False
        self.show_result = False
        self.result_timer = 0

    def start(self):
        """Start the puzzle"""
        self.active = True
        self.completed = False
        self.collapsed = False
        self.balanced = False
        self.show_result = False
        self.result_timer = 0
        self.left_weight = 0
        self.right_weight = 0
        self.scale_angle = 0
        self.dragging = None

        # Reset blocks
        for block in self.blocks:
            block["placed"] = False
            block["side"] = None

        # Initialize block positions (top of screen)
        start_x = 250
        start_y = 80
        self.block_rects = []
        for i, block in enumerate(self.blocks):
            rect = pygame.Rect(
                start_x + i * (self.block_width + 20),
                start_y,
                self.block_width,
                self.block_height
            )
            self.block_rects.append({
                "block": block,
                "rect": rect,
                "original_pos": (rect.x, rect.y)
            })

        # Drop zones (scale pans)
        self.left_zone = pygame.Rect(150, 350, 150, 100)
        self.right_zone = pygame.Rect(500, 350, 150, 100)

    def stop(self):
        """Stop the puzzle"""
        self.active = False

    def update(self, dt):
        """Update puzzle state"""
        if not self.active:
            return

        # Calculate balance
        weight_diff = self.left_weight - self.right_weight
        target_angle = weight_diff * 0.1

        # Smoothly move toward target angle
        self.scale_angle += (target_angle - self.scale_angle) * dt * 3

        # Check for collapse
        if abs(self.scale_angle) > self.max_angle and not self.collapsed:
            self.collapsed = True
            self.show_result = True

        # Check for balance (all placed and balanced)
        all_placed = all(b["placed"] for b in self.blocks)
        if all_placed and abs(self.scale_angle) < 0.05 and not self.collapsed:
            self.balanced = True
            self.show_result = True

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

            # Check if clicking on a block
            for item in self.block_rects:
                if item["rect"].collidepoint(pos) and not item["block"]["placed"]:
                    self.dragging = item
                    self.drag_offset = (
                        pos[0] - item["rect"].x,
                        pos[1] - item["rect"].y
                    )
                    break

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                pos = event.pos
                self.dragging["rect"].x = pos[0] - self.drag_offset[0]
                self.dragging["rect"].y = pos[1] - self.drag_offset[1]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                block = self.dragging["block"]
                rect = self.dragging["rect"]

                # Check if dropped in left zone
                if self.left_zone.colliderect(rect):
                    block["placed"] = True
                    block["side"] = "left"
                    self.left_weight += block["weight"]
                    rect.x = self.left_zone.x + 25
                    rect.y = self.left_zone.y + 25

                # Check if dropped in right zone
                elif self.right_zone.colliderect(rect):
                    block["placed"] = True
                    block["side"] = "right"
                    self.right_weight += block["weight"]
                    rect.x = self.right_zone.x + 25
                    rect.y = self.right_zone.y + 25

                else:
                    # Return to original position
                    rect.x = self.dragging["original_pos"][0]
                    rect.y = self.dragging["original_pos"][1]

                self.dragging = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.collapsed = True
                self.show_result = True

    def render(self, screen):
        """Render the puzzle"""
        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill((35, 35, 45))
        overlay.set_alpha(240)
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Balance Your Future", True, (200, 200, 210))
        screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst = inst_font.render("Place blocks on the scale to balance income, education, and housing", True, (150, 150, 160))
        screen.blit(inst, (self.SCREEN_WIDTH // 2 - inst.get_width() // 2, 55))

        # Draw scale base
        base_x = self.SCREEN_WIDTH // 2
        base_y = 480

        # Base triangle
        pygame.draw.polygon(screen, (100, 100, 110), [
            (base_x, base_y),
            (base_x - 40, base_y + 60),
            (base_x + 40, base_y + 60)
        ])

        # Scale beam (rotated)
        beam_length = 300
        beam_height = 10

        # Calculate beam endpoints based on angle
        left_x = base_x - beam_length // 2 * math.cos(self.scale_angle)
        left_y = base_y - 20 + beam_length // 2 * math.sin(self.scale_angle)
        right_x = base_x + beam_length // 2 * math.cos(self.scale_angle)
        right_y = base_y - 20 - beam_length // 2 * math.sin(self.scale_angle)

        # Draw beam
        pygame.draw.line(screen, (150, 150, 160), (left_x, left_y), (right_x, right_y), 8)

        # Draw pans
        pan_width = 120
        pan_height = 60

        # Left pan
        left_pan = pygame.Rect(left_x - pan_width // 2, left_y + 20, pan_width, pan_height)
        pygame.draw.rect(screen, (80, 80, 90), left_pan)
        pygame.draw.rect(screen, (120, 120, 130), left_pan, 2)

        # Right pan
        right_pan = pygame.Rect(right_x - pan_width // 2, right_y + 20, pan_width, pan_height)
        pygame.draw.rect(screen, (80, 80, 90), right_pan)
        pygame.draw.rect(screen, (120, 120, 130), right_pan, 2)

        # Update drop zones to match pan positions
        self.left_zone = left_pan
        self.right_zone = right_pan

        # Draw blocks
        block_font = pygame.font.Font(None, 22)
        for item in self.block_rects:
            block = item["block"]
            rect = item["rect"]

            # Update position if placed on moving pan
            if block["placed"]:
                if block["side"] == "left":
                    rect.x = left_pan.x + 10
                    rect.y = left_pan.y + 5
                elif block["side"] == "right":
                    rect.x = right_pan.x + 10
                    rect.y = right_pan.y + 5

            pygame.draw.rect(screen, block["color"], rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

            # Block name and weight
            name = block_font.render(f"{block['name']}", True, (255, 255, 255))
            screen.blit(name, (rect.x + 5, rect.y + 5))
            weight = block_font.render(f"Weight: {block['weight']}", True, (220, 220, 220))
            screen.blit(weight, (rect.x + 5, rect.y + 28))

        # Weight indicators
        weight_font = pygame.font.Font(None, 24)
        left_text = weight_font.render(f"Left: {self.left_weight}", True, (180, 180, 190))
        screen.blit(left_text, (150, 550))
        right_text = weight_font.render(f"Right: {self.right_weight}", True, (180, 180, 190))
        screen.blit(right_text, (550, 550))

        # Show result overlay
        if self.show_result:
            result_overlay = pygame.Surface((450, 180))
            result_overlay.fill((50, 40, 45) if self.collapsed else (40, 50, 45))
            result_rect = result_overlay.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
            screen.blit(result_overlay, result_rect)

            border_color = (180, 100, 100) if self.collapsed else (100, 180, 100)
            pygame.draw.rect(screen, border_color, result_rect, 3)

            result_font = pygame.font.Font(None, 36)

            if self.collapsed:
                # Collapse message
                text1 = result_font.render("Future Plan Collapsed", True, (200, 120, 120))
                screen.blit(text1, (result_rect.centerx - text1.get_width() // 2, result_rect.y + 40))

                sub_font = pygame.font.Font(None, 26)
                text2 = sub_font.render("Without balance, the weight became too much.", True, (180, 150, 150))
                screen.blit(text2, (result_rect.centerx - text2.get_width() // 2, result_rect.y + 90))

                text3 = sub_font.render("You needed guidance to find stability.", True, (180, 150, 150))
                screen.blit(text3, (result_rect.centerx - text3.get_width() // 2, result_rect.y + 120))
            else:
                # Balance achieved (rare)
                text1 = result_font.render("Temporary Balance", True, (120, 200, 120))
                screen.blit(text1, (result_rect.centerx - text1.get_width() // 2, result_rect.y + 40))

                sub_font = pygame.font.Font(None, 26)
                text2 = sub_font.render("You found balance... for now.", True, (150, 180, 150))
                screen.blit(text2, (result_rect.centerx - text2.get_width() // 2, result_rect.y + 90))

                text3 = sub_font.render("But without guidance, how long can it last?", True, (150, 180, 150))
                screen.blit(text3, (result_rect.centerx - text3.get_width() // 2, result_rect.y + 120))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)
