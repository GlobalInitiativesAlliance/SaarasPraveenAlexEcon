"""
Document Search Mini-Game for Foster Home Aging Out
Clean implementation using Part 1 visual base
"""
import pygame
from src.activities.activities import Activity
from .part1_visual_base import (
    Part1UIColors, Part1UIMetrics, Part1VisualHelpers,
    Part1VisualComponents, part1_visuals
)
from .particle_effects import part1_particles
from .feedback_popups import part1_feedback

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


class DocumentSearch(Activity):
    """Search desk drawers for important documents"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.foster_home_ref = None
        self.visuals = part1_visuals

        # Drawers with documents
        self.drawers = [
            {
                "id": "top_left", "name": "Top Left",
                "items": [
                    {"name": "Birth Certificate", "important": True, "found": False},
                    {"name": "Old receipts", "important": False, "found": False},
                ],
                "open": False, "searched": False, "hover_anim": 0.0
            },
            {
                "id": "top_right", "name": "Top Right",
                "items": [
                    {"name": "Social Security Card", "important": True, "found": False},
                    {"name": "Old homework", "important": False, "found": False},
                ],
                "open": False, "searched": False, "hover_anim": 0.0
            },
            {
                "id": "middle", "name": "Middle",
                "items": [
                    {"name": "Medical Records", "important": True, "found": False},
                    {"name": "Foster Care Letters", "important": True, "found": False},
                ],
                "open": False, "searched": False, "hover_anim": 0.0
            },
            {
                "id": "bottom_left", "name": "Bottom Left",
                "items": [
                    {"name": "School Transcripts", "important": True, "found": False},
                    {"name": "Old magazines", "important": False, "found": False},
                ],
                "open": False, "searched": False, "hover_anim": 0.0
            },
            {
                "id": "bottom_right", "name": "Bottom Right",
                "items": [
                    {"name": "Immunization Records", "important": True, "found": False},
                    {"name": "Emergency Contacts", "important": True, "found": False},
                ],
                "open": False, "searched": False, "hover_anim": 0.0
            },
        ]

        # Count total important documents
        self.total_documents = sum(
            1 for d in self.drawers for item in d["items"] if item["important"]
        )
        self.documents_found = []

        # State
        self.current_drawer = None
        self.hover_drawer = None
        self.hover_item = None

        # Layout
        self.desk_rect = pygame.Rect(180, 200, 450, 320)

        # Button
        self.button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        self.button_hover = False

    def start(self):
        """Start the document search"""
        super().start()
        self.visuals.init_fonts()

        # Reset state
        for drawer in self.drawers:
            drawer["open"] = False
            drawer["searched"] = False
            drawer["hover_anim"] = 0.0
            for item in drawer["items"]:
                item["found"] = False

        self.documents_found = []
        self.current_drawer = None
        self.hover_drawer = None

    def get_drawer_rect(self, drawer):
        """Get rectangle for a drawer"""
        desk = self.desk_rect
        w, h = 140, 70
        gap = 15

        positions = {
            "top_left": (desk.x + 30, desk.y + 40),
            "top_right": (desk.x + desk.width - w - 30, desk.y + 40),
            "middle": (desk.x + desk.width // 2 - w // 2, desk.y + 130),
            "bottom_left": (desk.x + 30, desk.y + 220),
            "bottom_right": (desk.x + desk.width - w - 30, desk.y + 220),
        }

        x, y = positions.get(drawer["id"], (desk.x, desk.y))
        return pygame.Rect(x, y, w, h)

    def draw_desk(self, screen):
        """Draw the desk"""
        rect = self.desk_rect

        # Shadow
        Part1VisualHelpers.draw_shadow(screen, rect, offset=8, alpha=60, border_radius=10)

        # Main desk body
        WOOD = (101, 67, 33)
        WOOD_LIGHT = (139, 90, 50)
        WOOD_DARK = (70, 45, 20)

        pygame.draw.rect(screen, WOOD, rect, border_radius=8)

        # Desk top edge
        top_rect = pygame.Rect(rect.x - 15, rect.y - 15, rect.width + 30, 25)
        pygame.draw.rect(screen, WOOD_LIGHT, top_rect, border_radius=5)
        pygame.draw.rect(screen, WOOD_DARK, top_rect, 2, border_radius=5)

        # Border
        pygame.draw.rect(screen, WOOD_DARK, rect, 3, border_radius=8)

    def draw_drawer(self, screen, drawer):
        """Draw a single drawer"""
        rect = self.get_drawer_rect(drawer)
        is_hover = (drawer == self.hover_drawer)
        is_open = drawer["open"]
        is_searched = drawer["searched"]

        # Animate hover
        target = 1.0 if is_hover else 0.0
        drawer["hover_anim"] += (target - drawer["hover_anim"]) * 0.2

        # Drawer colors
        if is_open:
            DRAWER = (50, 35, 20)  # Dark interior
            DRAWER_BORDER = (70, 50, 30)
        elif is_searched:
            DRAWER = (90, 110, 90)  # Greenish tint for searched
            DRAWER_BORDER = (70, 90, 70)
        else:
            base = (120, 80, 45)
            if is_hover:
                DRAWER = Part1VisualHelpers.lighten_color(base, 1.2)
            else:
                DRAWER = base
            DRAWER_BORDER = Part1VisualHelpers.darken_color(DRAWER)

        # Lift on hover
        draw_rect = rect.copy()
        if is_hover and not is_open:
            draw_rect.y -= int(drawer["hover_anim"] * 3)

        # Shadow
        if is_hover or is_open:
            Part1VisualHelpers.draw_shadow(screen, draw_rect, offset=4, alpha=50, border_radius=6)

        # Draw drawer
        pygame.draw.rect(screen, DRAWER, draw_rect, border_radius=6)
        pygame.draw.rect(screen, DRAWER_BORDER, draw_rect, 2, border_radius=6)

        if is_open:
            # Draw items inside
            self.draw_drawer_contents(screen, draw_rect, drawer)
        else:
            # Handle
            handle_rect = pygame.Rect(draw_rect.centerx - 25, draw_rect.centery - 5, 50, 10)
            handle_color = (200, 170, 120) if is_hover else (160, 130, 90)
            pygame.draw.rect(screen, handle_color, handle_rect, border_radius=3)

            # Label
            if not is_searched:
                label = self.visuals.fonts['tiny'].render(drawer["name"], True, (200, 180, 160))
                screen.blit(label, (draw_rect.x + 8, draw_rect.y + 8))

        # Checkmark for searched
        if is_searched and not is_open:
            self.visuals.draw_checkmark(screen, (draw_rect.right - 12, draw_rect.y + 12), size=8)

    def draw_drawer_contents(self, screen, drawer_rect, drawer):
        """Draw items inside an open drawer"""
        items = drawer["items"]
        item_height = 22
        start_y = drawer_rect.y + 8

        for i, item in enumerate(items):
            if item["found"]:
                continue

            item_rect = pygame.Rect(
                drawer_rect.x + 8,
                start_y + i * (item_height + 4),
                drawer_rect.width - 16,
                item_height
            )

            is_hover = (item == self.hover_item)

            # Background
            if item["important"]:
                bg = (255, 250, 230) if not is_hover else (255, 255, 240)
            else:
                bg = (180, 175, 170) if not is_hover else (200, 195, 190)

            pygame.draw.rect(screen, bg, item_rect, border_radius=4)

            # Border
            border = Part1UIColors.PRIMARY if is_hover else (
                Part1UIColors.DOCUMENT if item["important"] else Part1UIColors.INACTIVE
            )
            pygame.draw.rect(screen, border, item_rect, 1, border_radius=4)

            # Important indicator
            if item["important"]:
                pygame.draw.circle(screen, (255, 100, 100),
                                 (item_rect.right - 10, item_rect.centery), 4)

            # Name
            name_color = Part1UIColors.TEXT_DARK if item["important"] else Part1UIColors.TEXT_MUTED
            name = self.visuals.fonts['tiny'].render(item["name"], True, name_color)
            screen.blit(name, (item_rect.x + 6, item_rect.centery - name.get_height() // 2))

    def draw_found_list(self, screen):
        """Draw list of found documents"""
        list_x = self.desk_rect.right + 40
        list_y = 200

        header = self.visuals.fonts['subheading'].render("Found Documents", True, Part1UIColors.TEXT_WARM)
        screen.blit(header, (list_x, list_y))

        if self.documents_found:
            for i, doc in enumerate(self.documents_found):
                y = list_y + 35 + i * 24
                # Checkmark
                self.visuals.draw_checkmark(screen, (list_x + 10, y + 8), size=8)
                # Name
                doc_surf = self.visuals.fonts['small'].render(doc, True, Part1UIColors.SUCCESS)
                screen.blit(doc_surf, (list_x + 28, y))
        else:
            hint = self.visuals.fonts['small'].render("Click drawers to search", True, Part1UIColors.TEXT_MUTED)
            screen.blit(hint, (list_x, list_y + 35))

    def draw(self, screen):
        """Draw the document search interface"""
        if not self.active:
            return

        # Overlay
        self.visuals.draw_modal_overlay(screen)

        # Title
        self.visuals.draw_title(screen, "Gather Your Documents", y=30)

        # Progress bar
        progress_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 85, 300, 30)
        self.visuals.draw_progress_bar(screen, progress_rect,
                                       len(self.documents_found), self.total_documents,
                                       label="Documents")

        # Draw desk and drawers
        self.draw_desk(screen)
        for drawer in self.drawers:
            self.draw_drawer(screen, drawer)

        # Found documents list
        self.draw_found_list(screen)

        # Instructions
        if self.current_drawer:
            hint = "Click documents to collect them, or click elsewhere to close"
        else:
            hint = "Click a drawer to search inside"
        inst_surf = self.visuals.fonts['small'].render(hint, True, Part1UIColors.TEXT_MUTED)
        screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, 140))

        # Complete button (show when most documents found)
        if len(self.documents_found) >= self.total_documents - 1:
            self.visuals.draw_button(screen, self.button_rect,
                                    "Done Searching",
                                    is_hover=self.button_hover,
                                    is_enabled=True)

        # Hint
        self.visuals.draw_hint(screen, "Press ESC or SPACE to continue when done")

        # Draw particles and feedback popups on top
        part1_particles.render(screen)
        part1_feedback.render(screen)

    def handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        if not self.active:
            return

        self.button_hover = self.button_rect.collidepoint(pos)
        self.hover_drawer = None
        self.hover_item = None

        # Check drawer hover
        for drawer in self.drawers:
            rect = self.get_drawer_rect(drawer)
            if rect.collidepoint(pos):
                self.hover_drawer = drawer

                # Check item hover if drawer is open
                if drawer["open"]:
                    self.check_item_hover(pos, drawer, rect)
                break

    def check_item_hover(self, pos, drawer, drawer_rect):
        """Check if hovering over an item in open drawer"""
        items = drawer["items"]
        item_height = 22
        start_y = drawer_rect.y + 8

        for i, item in enumerate(items):
            if item["found"]:
                continue

            item_rect = pygame.Rect(
                drawer_rect.x + 8,
                start_y + i * (item_height + 4),
                drawer_rect.width - 16,
                item_height
            )

            if item_rect.collidepoint(pos):
                self.hover_item = item
                break

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        # Check button
        if len(self.documents_found) >= self.total_documents - 1:
            if self.button_rect.collidepoint(pos):
                self.finish_search()
                return

        # Check drawer click
        for drawer in self.drawers:
            rect = self.get_drawer_rect(drawer)
            if rect.collidepoint(pos):
                if drawer["open"]:
                    # Check item click
                    if self.hover_item:
                        self.collect_item(drawer, self.hover_item)
                    else:
                        # Close drawer
                        drawer["open"] = False
                        self.current_drawer = None
                else:
                    # Open this drawer, close others
                    for d in self.drawers:
                        d["open"] = False
                    drawer["open"] = True
                    self.current_drawer = drawer
                return

        # Click outside - close any open drawer
        if self.current_drawer:
            self.current_drawer["open"] = False
            self.current_drawer = None

    def collect_item(self, drawer, item):
        """Collect a document"""
        drawer_rect = self.get_drawer_rect(drawer)
        doc_x = drawer_rect.centerx
        doc_y = drawer_rect.centery

        if item["important"]:
            item["found"] = True
            self.documents_found.append(item["name"])

            # Particle effects and feedback
            part1_particles.emit_document_found(doc_x, doc_y)
            part1_feedback.add_document_found(doc_x, doc_y - 30, item["name"])

            # Check if drawer is fully searched
            remaining = [i for i in drawer["items"] if i["important"] and not i["found"]]
            if not remaining:
                drawer["searched"] = True
                drawer["open"] = False
                self.current_drawer = None
        else:
            # Junk item - just mark as found
            item["found"] = True

    def handle_key(self, key):
        """Handle keyboard"""
        if not self.active:
            return

        if key == pygame.K_ESCAPE or key == pygame.K_SPACE:
            if self.current_drawer:
                self.current_drawer["open"] = False
                self.current_drawer = None
            elif len(self.documents_found) >= self.total_documents - 1:
                self.finish_search()

    def finish_search(self):
        """Complete document search"""
        found = len(self.documents_found)
        total = self.total_documents

        # Achievement and celebration
        part1_feedback.add_documents_complete_achievement(found, total)
        if found > 0:
            part1_particles.emit_achievement(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        if self.foster_home_ref:
            self.foster_home_ref.items_packed.add('documents')
            self.foster_home_ref.update_objective_display()

            if found == total:
                msg = f"You found all {total} documents. These are crucial for your future."
            elif found > 0:
                msg = f"You found {found} of {total} documents. Some might be missing, but you have the essentials."
            else:
                msg = "You couldn't find any documents. This will make things harder."

            if hasattr(self.foster_home_ref, 'dialogue_box'):
                self.foster_home_ref.dialogue_box.show(None, msg)

        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        # Update particles and feedback popups
        part1_particles.update(dt)
        part1_feedback.update(dt)
