"""
Document search mini-game for the foster home narrative
"""
import pygame
import math
import random
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class DocumentSearch(Activity):
    """Mini-game where player searches through desk drawers for important documents"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)  # Call parent Activity init
        self.foster_home_ref = None

        # Desk drawers with different items
        self.drawers = [
            {
                "id": "top_left",
                "name": "Top Left Drawer",
                "pos": (0, 0),
                "open": False,
                "searched": False,
                "items": [
                    {"name": "Birth Certificate", "type": "document", "important": True, "found": False},
                    {"name": "Old receipts", "type": "junk", "important": False, "found": False},
                    {"name": "Paperclips", "type": "junk", "important": False, "found": False}
                ]
            },
            {
                "id": "top_right",
                "name": "Top Right Drawer",
                "pos": (1, 0),
                "open": False,
                "searched": False,
                "items": [
                    {"name": "Social Security Card", "type": "document", "important": True, "found": False},
                    {"name": "Old homework", "type": "junk", "important": False, "found": False},
                    {"name": "Broken calculator", "type": "junk", "important": False, "found": False}
                ]
            },
            {
                "id": "middle",
                "name": "Middle Drawer",
                "pos": (0.5, 1),
                "open": False,
                "searched": False,
                "items": [
                    {"name": "Medical Records (incomplete)", "type": "document", "important": True, "found": False},
                    {"name": "Foster care placement letters", "type": "document", "important": True, "found": False},
                    {"name": "Rubber bands", "type": "junk", "important": False, "found": False}
                ]
            },
            {
                "id": "bottom_left",
                "name": "Bottom Left Drawer",
                "pos": (0, 2),
                "open": False,
                "searched": False,
                "items": [
                    {"name": "School transcripts (partial)", "type": "document", "important": True, "found": False},
                    {"name": "Old magazines", "type": "junk", "important": False, "found": False}
                ]
            },
            {
                "id": "bottom_right",
                "name": "Bottom Right Drawer",
                "pos": (1, 2),
                "open": False,
                "searched": False,
                "items": [
                    {"name": "Immunization records", "type": "document", "important": True, "found": False},
                    {"name": "Emergency contact list (outdated)", "type": "document", "important": True, "found": False},
                    {"name": "Dried up pens", "type": "junk", "important": False, "found": False}
                ]
            }
        ]

        # Documents found
        self.documents_found = []
        self.total_documents = sum(1 for drawer in self.drawers
                                  for item in drawer["items"]
                                  if item["important"])

        # State
        self.current_drawer = None
        self.viewing_item = None
        self.hover_drawer = None
        self.search_progress = {}

        # Animation
        self.animation_timer = 0
        self.drawer_slide = {}
        self.item_float = {}
        self.sparkle_positions = []

        # Messages
        self.current_message = None
        self.message_timer = 0

        # UI
        self.continue_button_rect = None

    def start(self):
        """Start the document search activity"""
        super().start()  # Call parent start method
        self.documents_found = []
        self.current_drawer = None
        self.viewing_item = None
        self.animation_timer = 0
        self.current_message = "Search the desk drawers for your important documents"
        self.message_timer = 3.0

        # Reset drawers
        for drawer in self.drawers:
            drawer["open"] = False
            drawer["searched"] = False
            self.drawer_slide[drawer["id"]] = 0
            for item in drawer["items"]:
                item["found"] = False
                self.item_float[item["name"]] = random.random() * math.pi * 2

        # No sparkles - they're distracting
        self.sparkle_positions = []

    def get_desk_rect(self):
        """Get the main desk area rectangle"""
        return pygame.Rect(SCREEN_WIDTH // 2 - 250, 200, 500, 350)

    def get_drawer_rect(self, drawer):
        """Get rectangle for a specific drawer"""
        desk = self.get_desk_rect()
        drawer_width = 160
        drawer_height = 80

        # Better drawer positioning - properly aligned
        if drawer["id"] == "middle":
            x = desk.x + desk.width // 2 - drawer_width // 2
            y = desk.y + 140
        elif drawer["id"] == "top_left":
            x = desk.x + 40
            y = desk.y + 50
        elif drawer["id"] == "top_right":
            x = desk.x + desk.width - drawer_width - 40
            y = desk.y + 50
        elif drawer["id"] == "bottom_left":
            x = desk.x + 40
            y = desk.y + 230
        elif drawer["id"] == "bottom_right":
            x = desk.x + desk.width - drawer_width - 40
            y = desk.y + 230
        else:
            # Fallback
            x = desk.x + 60 + drawer["pos"][0] * 220
            y = desk.y + 50 + drawer["pos"][1] * 100

        # Add subtle slide animation when open
        if drawer["id"] in self.drawer_slide and drawer["open"]:
            x += min(self.drawer_slide[drawer["id"]], 15)  # Small slide

        return pygame.Rect(x, y, drawer_width, drawer_height)

    def draw_desk(self, screen):
        """Draw the desk with drawers"""
        desk_rect = self.get_desk_rect()

        # Desk shadow
        shadow = pygame.Surface((desk_rect.width + 20, desk_rect.height + 20), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 50))
        screen.blit(shadow, (desk_rect.x - 10, desk_rect.y - 5))

        # Desk body
        pygame.draw.rect(screen, (101, 67, 33), desk_rect)
        pygame.draw.rect(screen, (139, 90, 43), desk_rect, 3)

        # Desk top
        top_rect = pygame.Rect(desk_rect.x - 20, desk_rect.y - 20, desk_rect.width + 40, 30)
        pygame.draw.rect(screen, (139, 90, 43), top_rect)
        pygame.draw.rect(screen, (101, 67, 33), top_rect, 2)

        # Draw drawers
        for drawer in self.drawers:
            self.draw_drawer(screen, drawer)

    def draw_drawer(self, screen, drawer):
        """Draw an individual drawer"""
        rect = self.get_drawer_rect(drawer)

        # Drawer face
        if drawer["open"]:
            # Open drawer (darker interior)
            pygame.draw.rect(screen, (50, 30, 15), rect)
            pygame.draw.rect(screen, (70, 50, 30), rect, 2)

            # Draw items inside if open
            if drawer == self.current_drawer:
                self.draw_drawer_contents(screen, rect, drawer)
        else:
            # Closed drawer
            color = (120, 80, 40) if drawer != self.hover_drawer else (140, 100, 60)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (80, 60, 30), rect, 2)

            # Drawer handle
            handle_rect = pygame.Rect(rect.centerx - 20, rect.centery - 5, 40, 10)
            pygame.draw.rect(screen, (180, 150, 100), handle_rect)
            pygame.draw.rect(screen, (150, 120, 80), handle_rect, 1)

            # Label if not searched
            if not drawer["searched"]:
                font = pygame.font.Font(None, 18)
                label = font.render(drawer["name"], True, (200, 180, 150))
                screen.blit(label, (rect.x + 10, rect.y + 10))

    def draw_drawer_contents(self, screen, drawer_rect, drawer):
        """Draw items inside an open drawer"""
        # Keep items properly inside drawer
        padding = 8
        item_width = 65
        item_height = 20

        # Max items that fit in drawer
        items_per_row = 2
        max_rows = (drawer_rect.height - 2 * padding) // (item_height + 5)

        for i, item in enumerate(drawer["items"]):
            if not item["found"]:
                row = i // items_per_row
                col = i % items_per_row

                # Skip items that won't fit in drawer
                if row >= max_rows:
                    continue

                item_x = drawer_rect.x + padding + col * (item_width + 10)
                item_y = drawer_rect.y + padding + row * (item_height + 5)

                item_rect = pygame.Rect(item_x, item_y, item_width, item_height)

                # No float animation - keeps items stable
                float_offset = 0

                # Item representation
                if item["type"] == "document":
                    # Important document - paper icon
                    paper_color = (255, 255, 230) if item == self.viewing_item else (230, 230, 200)
                    doc_rect = item_rect  # No float offset
                    pygame.draw.rect(screen, paper_color, doc_rect)
                    pygame.draw.rect(screen, (100, 100, 100), doc_rect, 1)

                    # Document lines (fewer, smaller)
                    for j in range(2):
                        y = doc_rect.y + 5 + j * 7
                        pygame.draw.line(screen, (150, 150, 150), (doc_rect.x + 3, y), (doc_rect.x + doc_rect.width - 3, y), 1)

                    # Important marker
                    if item["important"]:
                        pygame.draw.circle(screen, (255, 100, 100), (doc_rect.x + doc_rect.width - 10, doc_rect.y + 5), 3)

                else:
                    # Junk item - simple colored box
                    junk_color = (150, 150, 150)
                    junk_rect = item_rect  # No float offset
                    pygame.draw.rect(screen, junk_color, junk_rect)
                    pygame.draw.rect(screen, (100, 100, 100), junk_rect, 1)

                # Hover effect
                mouse_pos = pygame.mouse.get_pos()
                if item_rect.collidepoint(mouse_pos):
                    # Show item name
                    font = pygame.font.Font(None, 16)
                    name_surf = font.render(item["name"], True, (255, 255, 255))
                    name_bg = pygame.Surface((name_surf.get_width() + 10, name_surf.get_height() + 4))
                    name_bg.fill((50, 50, 50))
                    screen.blit(name_bg, (mouse_pos[0] + 10, mouse_pos[1] - 20))
                    screen.blit(name_surf, (mouse_pos[0] + 15, mouse_pos[1] - 18))

    def draw(self, screen):
        """Draw the document search interface"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Update animations
        self.animation_timer += 0.016

        # Background panel
        panel_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (40, 35, 30), panel_rect)
        pygame.draw.rect(screen, (100, 90, 80), panel_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Gather Your Documents", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Progress bar
        self.draw_progress_bar(screen)

        # Draw desk with drawers
        self.draw_desk(screen)

        # No sparkles - keep it clean

        # Documents found list
        self.draw_found_documents(screen)

        # Message
        if self.current_message and self.message_timer > 0:
            self.draw_message(screen)

        # Continue button
        if len(self.documents_found) >= self.total_documents - 1:  # Allow continuing with most documents
            self.draw_continue_button(screen)

    def draw_progress_bar(self, screen):
        """Draw progress bar for documents found"""
        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 120

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Fill
        progress = len(self.documents_found) / max(1, self.total_documents)
        fill_width = int(bar_width * progress)
        fill_color = (100, 255, 100) if progress >= 1.0 else (255, 200, 100)
        if fill_width > 0:
            pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 2)

        # Text
        font = pygame.font.Font(None, 20)
        text = f"Documents: {len(self.documents_found)}/{self.total_documents}"
        text_surf = font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (bar_x + bar_width // 2 - text_surf.get_width() // 2, bar_y + 5))

    def draw_found_documents(self, screen):
        """Draw list of found documents"""
        if not self.documents_found:
            return

        list_x = 100
        list_y = 300
        font = pygame.font.Font(None, 20)

        # Title
        title = font.render("Documents Found:", True, (200, 180, 150))
        screen.blit(title, (list_x, list_y - 30))

        # Documents
        for i, doc_name in enumerate(self.documents_found):
            y = list_y + i * 25
            # Checkmark
            pygame.draw.lines(screen, (100, 255, 100), False,
                            [(list_x, y + 10), (list_x + 8, y + 18), (list_x + 20, y + 5)], 2)
            # Document name
            doc_surf = font.render(doc_name, True, (200, 200, 200))
            screen.blit(doc_surf, (list_x + 30, y))

    def draw_message(self, screen):
        """Draw temporary message"""
        if self.message_timer <= 0:
            return

        font = pygame.font.Font(None, 28)
        msg_surf = font.render(self.current_message, True, (255, 255, 200))

        # Background
        bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - msg_surf.get_width() // 2 - 20,
                             SCREEN_HEIGHT - 150,
                             msg_surf.get_width() + 40, 40)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(screen, (150, 150, 150), bg_rect, 2)

        screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, SCREEN_HEIGHT - 140))

    def draw_continue_button(self, screen):
        """Draw continue button"""
        font = pygame.font.Font(None, 32)
        if len(self.documents_found) >= self.total_documents:
            text = "Pack All Documents"
            color = (100, 200, 100)
        else:
            text = f"Continue ({len(self.documents_found)}/{self.total_documents} found)"
            color = (200, 150, 100)

        button_surf = font.render(text, True, (255, 255, 255))
        self.continue_button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 50
        )

        pygame.draw.rect(screen, color, self.continue_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.continue_button_rect, 2)

        button_x = self.continue_button_rect.centerx - button_surf.get_width() // 2
        button_y = self.continue_button_rect.centery - button_surf.get_height() // 2
        screen.blit(button_surf, (button_x, button_y))

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        # Check continue button
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.complete_search()
            return

        # Check drawer clicks
        for drawer in self.drawers:
            drawer_rect = self.get_drawer_rect(drawer)
            if drawer_rect.collidepoint(pos):
                if drawer["open"]:
                    # Check for item clicks inside drawer
                    item_y = drawer_rect.y + 20
                    for i, item in enumerate(drawer["items"]):
                        if not item["found"]:
                            item_rect = pygame.Rect(
                                drawer_rect.x + 10 + (i % 2) * 85,
                                item_y + (i // 2) * 30,
                                80, 25
                            )
                            if item_rect.collidepoint(pos):
                                self.collect_item(drawer, item)
                                return
                    # Close drawer if clicking on it but not on items
                    drawer["open"] = False
                    self.current_drawer = None
                    self.drawer_slide[drawer["id"]] = 0
                else:
                    # Open drawer
                    # Close other drawers first
                    for d in self.drawers:
                        d["open"] = False
                        self.drawer_slide[d["id"]] = 0

                    drawer["open"] = True
                    drawer["searched"] = True
                    self.current_drawer = drawer
                    self.drawer_slide[drawer["id"]] = 10  # Smaller slide amount
                break

    def handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        if not self.active:
            return

        self.hover_drawer = None
        for drawer in self.drawers:
            if not drawer["open"]:
                drawer_rect = self.get_drawer_rect(drawer)
                if drawer_rect.collidepoint(pos):
                    self.hover_drawer = drawer
                    break

    def collect_item(self, drawer, item):
        """Collect an item from a drawer"""
        item["found"] = True

        if item["important"]:
            self.documents_found.append(item["name"])
            self.current_message = f"Found: {item['name']}"
            self.message_timer = 2.0

            # Check for special messages
            if "incomplete" in item["name"].lower() or "partial" in item["name"].lower():
                self.current_message += " (incomplete records)"
            elif "outdated" in item["name"].lower():
                self.current_message += " (needs updating)"
        else:
            self.current_message = f"{item['name']} - not important"
            self.message_timer = 1.0

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if key == pygame.K_ESCAPE:
            # Close current drawer
            if self.current_drawer:
                self.current_drawer["open"] = False
                self.drawer_slide[self.current_drawer["id"]] = 0
                self.current_drawer = None

    def complete_search(self):
        """Complete the document search"""
        # Update foster home state
        if self.foster_home_ref:
            self.foster_home_ref.items_packed.add('documents')
            self.foster_home_ref.update_objective_display()

            # Show completion message
            if hasattr(self.foster_home_ref, 'dialogue_box'):
                if len(self.documents_found) >= self.total_documents:
                    msg = "You gather all your important documents. Birth certificate, social security card, medical records..."
                    msg += " Most are incomplete or outdated, but they're all you have to prove who you are."
                else:
                    missing = self.total_documents - len(self.documents_found)
                    msg = f"You found most of your documents, but {missing} are still missing. "
                    msg += "You'll have to make do with what you have."

                self.foster_home_ref.dialogue_box.show(None, msg)

        self.complete()  # Use parent's complete method

    def update(self, dt):
        """Update animations and timers"""
        if not self.active:
            return

        self.animation_timer += dt

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt

        # Update drawer slide animations
        for drawer_id in self.drawer_slide:
            if self.drawer_slide[drawer_id] > 0:
                self.drawer_slide[drawer_id] *= 0.9
                if self.drawer_slide[drawer_id] < 0.1:
                    self.drawer_slide[drawer_id] = 0