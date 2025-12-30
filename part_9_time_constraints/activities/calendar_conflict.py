"""
Calendar Conflict Mini-Game
Drag notifications into calendar slots - all three overlap at 3pm
Shows the impossibility of managing conflicting responsibilities
"""
import pygame


class CalendarConflict:
    """Calendar scheduling game where all events overlap"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Notifications to schedule
        self.notifications = [
            {
                "name": "Work Shift",
                "time": "3:00 PM",
                "color": (100, 180, 100),
                "description": "Mandatory shift - need the money",
                "placed": False,
                "slot": None
            },
            {
                "name": "Program Meeting",
                "time": "3:00 PM",
                "color": (100, 150, 200),
                "description": "Mandatory - benefits depend on it",
                "placed": False,
                "slot": None
            },
            {
                "name": "Therapy Session",
                "time": "3:30 PM",
                "color": (180, 130, 180),
                "description": "Mental health appointment",
                "placed": False,
                "slot": None
            }
        ]

        # Notification card positions and rects
        self.notification_rects = []
        self.card_width = 180
        self.card_height = 80

        # Calendar time slots
        self.time_slots = [
            {"time": "2:00 PM", "y": 180},
            {"time": "3:00 PM", "y": 260},
            {"time": "4:00 PM", "y": 340},
            {"time": "5:00 PM", "y": 420},
        ]
        self.slot_rects = []

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Game state
        self.show_conflict = False
        self.conflict_timer = 0
        self.all_placed = False

        # Result
        self.show_result = False
        self.result_timer = 0

    def start(self):
        """Start the calendar game"""
        self.active = True
        self.completed = False
        self.show_conflict = False
        self.conflict_timer = 0
        self.show_result = False
        self.result_timer = 0
        self.dragging = None
        self.all_placed = False

        # Reset notifications
        for notif in self.notifications:
            notif["placed"] = False
            notif["slot"] = None

        # Initialize notification positions (left side)
        start_x = 50
        start_y = 180
        self.notification_rects = []
        for i, notif in enumerate(self.notifications):
            rect = pygame.Rect(
                start_x,
                start_y + i * (self.card_height + 20),
                self.card_width,
                self.card_height
            )
            self.notification_rects.append({
                "notif": notif,
                "rect": rect,
                "original_pos": (rect.x, rect.y)
            })

        # Initialize calendar slot positions (right side)
        calendar_x = 450
        self.slot_rects = []
        for slot in self.time_slots:
            rect = pygame.Rect(
                calendar_x,
                slot["y"],
                280,
                70
            )
            self.slot_rects.append({
                "slot": slot,
                "rect": rect,
                "items": []
            })

    def stop(self):
        """Stop the game"""
        self.active = False

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Check if all placed
        if all(n["placed"] for n in self.notifications) and not self.all_placed:
            self.all_placed = True
            self.show_conflict = True

        # Conflict animation
        if self.show_conflict:
            self.conflict_timer += dt
            if self.conflict_timer > 3.0:
                self.show_result = True

        # Result timer
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

            # Check if clicking on a notification card
            for item in self.notification_rects:
                if item["rect"].collidepoint(pos) and not item["notif"]["placed"]:
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
                notif = self.dragging["notif"]
                rect = self.dragging["rect"]

                # Check if dropped in a slot
                dropped = False
                for slot_item in self.slot_rects:
                    if slot_item["rect"].colliderect(rect):
                        # Place in slot
                        notif["placed"] = True
                        notif["slot"] = slot_item["slot"]["time"]
                        slot_item["items"].append(notif)

                        # Position in slot
                        rect.x = slot_item["rect"].x + 10
                        rect.y = slot_item["rect"].y + 5
                        dropped = True
                        break

                if not dropped:
                    # Return to original position
                    rect.x = self.dragging["original_pos"][0]
                    rect.y = self.dragging["original_pos"][1]

                self.dragging = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.show_conflict:
                    self.show_result = True

    def render(self, screen):
        """Render the calendar game"""
        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill((35, 35, 45))
        overlay.set_alpha(245)
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Schedule Your Day", True, (200, 200, 210))
        screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst = inst_font.render("Drag each notification to a time slot on the calendar", True, (150, 150, 160))
        screen.blit(inst, (self.SCREEN_WIDTH // 2 - inst.get_width() // 2, 70))

        # Left side label
        label_font = pygame.font.Font(None, 28)
        left_label = label_font.render("Notifications:", True, (180, 180, 190))
        screen.blit(left_label, (50, 140))

        # Right side label
        right_label = label_font.render("Calendar:", True, (180, 180, 190))
        screen.blit(right_label, (450, 140))

        # Draw calendar slots
        slot_font = pygame.font.Font(None, 24)
        for slot_item in self.slot_rects:
            slot = slot_item["slot"]
            rect = slot_item["rect"]

            # Slot background
            bg_color = (50, 55, 65)
            if self.show_conflict and slot["time"] == "3:00 PM":
                # Flash red for conflict
                flash = int((self.conflict_timer * 4) % 2)
                if flash:
                    bg_color = (120, 50, 50)
                else:
                    bg_color = (80, 40, 40)

            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, (80, 85, 95), rect, 2)

            # Time label
            time_text = slot_font.render(slot["time"], True, (160, 160, 170))
            screen.blit(time_text, (rect.x - 70, rect.y + 25))

        # Draw notification cards
        card_font = pygame.font.Font(None, 22)
        for item in self.notification_rects:
            notif = item["notif"]
            rect = item["rect"]

            # Card background
            pygame.draw.rect(screen, notif["color"], rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

            # Card text
            name = card_font.render(notif["name"], True, (255, 255, 255))
            screen.blit(name, (rect.x + 10, rect.y + 10))

            time = card_font.render(notif["time"], True, (220, 220, 220))
            screen.blit(time, (rect.x + 10, rect.y + 32))

            desc = card_font.render(notif["description"][:25], True, (200, 200, 200))
            screen.blit(desc, (rect.x + 10, rect.y + 54))

        # Show conflict warning
        if self.show_conflict and not self.show_result:
            # Flashing warning box
            warning_rect = pygame.Rect(200, 500, 400, 60)
            flash = int((self.conflict_timer * 3) % 2)
            if flash:
                pygame.draw.rect(screen, (150, 50, 50), warning_rect)
            else:
                pygame.draw.rect(screen, (100, 30, 30), warning_rect)
            pygame.draw.rect(screen, (200, 80, 80), warning_rect, 3)

            warn_font = pygame.font.Font(None, 32)
            warn_text = warn_font.render("CONFLICT DETECTED!", True, (255, 200, 200))
            screen.blit(warn_text, (warning_rect.centerx - warn_text.get_width() // 2, warning_rect.y + 8))

            sub_font = pygame.font.Font(None, 24)
            sub_text = sub_font.render("All events overlap at 3:00 PM", True, (220, 180, 180))
            screen.blit(sub_text, (warning_rect.centerx - sub_text.get_width() // 2, warning_rect.y + 35))

        # Show result
        if self.show_result:
            result_rect = pygame.Rect(150, 200, 500, 200)
            pygame.draw.rect(screen, (50, 40, 45), result_rect)
            pygame.draw.rect(screen, (180, 100, 100), result_rect, 3)

            result_font = pygame.font.Font(None, 36)
            text1 = result_font.render("You Cannot Attend Everything", True, (200, 150, 150))
            screen.blit(text1, (result_rect.centerx - text1.get_width() // 2, result_rect.y + 40))

            sub_font = pygame.font.Font(None, 26)
            text2 = sub_font.render("Work shift: 3:00 PM", True, (180, 180, 180))
            screen.blit(text2, (result_rect.centerx - text2.get_width() // 2, result_rect.y + 90))

            text3 = sub_font.render("Program meeting: 3:00 PM", True, (180, 180, 180))
            screen.blit(text3, (result_rect.centerx - text3.get_width() // 2, result_rect.y + 115))

            text4 = sub_font.render("Therapy: 3:30 PM", True, (180, 180, 180))
            screen.blit(text4, (result_rect.centerx - text4.get_width() // 2, result_rect.y + 140))

            text5 = result_font.render("Choose ONE.", True, (220, 120, 120))
            screen.blit(text5, (result_rect.centerx - text5.get_width() // 2, result_rect.y + 170))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)
