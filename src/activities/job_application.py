"""
Job Application Mini-Game
Following pattern from shelter_checkin and apartment_search
"""
import pygame
import math
import random
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class JobApplication(Activity):
    """Job application process showing desperation of finding work"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None  # Set by parent interior

        # Phase management (1=form, 2=availability, 3=rejection loop)
        self.current_phase = 1
        self.phase_complete = {1: False, 2: False, 3: False}

        # Application tracking
        self.applications_submitted = 0
        self.rejections_received = 0
        self.finally_hired = False

        # Phase 1: Application form
        self.form_fields = {
            "name": {"value": "", "rect": None, "placeholder": "Enter your name"},
            "experience": {"value": "", "rect": None, "placeholder": "Describe your work experience"},
            "education": {"value": "", "rect": None, "placeholder": "Your education level"},
            "references": {"value": "", "rect": None, "placeholder": "List references"},
            "transportation": {"value": "", "rect": None, "placeholder": "How will you get to work?"}
        }
        self.active_field = None  # Track which field is currently being edited
        self.field_order = ["name", "experience", "education", "references", "transportation"]

        # Phase 2: Availability grid
        self.availability_grid = {}  # day/time slots
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.times = ["6-10am", "10-2pm", "2-6pm", "6-10pm", "10pm-2am"]
        self.selected_slots = set()
        self.school_conflicts = {("Mon", "10-2pm"), ("Wed", "10-2pm"), ("Fri", "10-2pm")}

        # Phase 3: Rejection messages
        self.rejection_messages = [
            "Thank you for your interest. We've decided to go with another candidate.",
            "Your application has been reviewed. We're not moving forward at this time.",
            "We require 2+ years experience for this entry-level position.",
            "We need someone with more flexible availability.",
            "Position has been filled.",
            "We'll keep your application on file.",
            "Not a good fit for our team culture.",
            "Overqualified for this position.",  # The irony
            "We need someone who can start immediately. Oh, you can? Still no.",
            "Background check didn't pass. (You have no criminal record)",
            "We've decided not to fill this position after all.",
            "Your lack of references is concerning."
        ]
        self.current_rejection_index = 0

        # Visual elements
        self.animation_timer = 0
        self.hover_element = None
        self.shake_timer = 0
        self.desperation_level = 0
        self.continue_button_rect = None

        # Load textures
        self.load_textures()

    def load_textures(self):
        """Create visual elements for the application process"""
        # Application form background
        self.form_bg = pygame.Surface((600, 400))
        self.form_bg.fill((245, 245, 240))

        # Rejection stamp texture
        self.rejection_stamp = pygame.Surface((150, 60), pygame.SRCALPHA)
        font = pygame.font.Font(None, 36)
        stamp_text = font.render("REJECTED", True, (255, 0, 0))
        self.rejection_stamp.blit(stamp_text, (10, 15))

        # Hired stamp texture
        self.hired_stamp = pygame.Surface((150, 60), pygame.SRCALPHA)
        hired_text = font.render("HIRED!", True, (0, 200, 0))
        self.hired_stamp.blit(hired_text, (30, 15))

    def start(self):
        """Start the job application activity"""
        super().start()
        self.current_phase = 1
        self.animation_timer = 0
        self.applications_submitted = 0
        self.desperation_level = 0
        self.active_field = None

        # Enable text input
        pygame.key.start_text_input()

    def draw(self, screen):
        """Main draw function"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Update animation
        self.animation_timer += 0.016

        # Main container
        container_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (40, 35, 30), container_rect)
        pygame.draw.rect(screen, (200, 180, 160), container_rect, 3)

        # Draw current phase
        if self.current_phase == 1:
            self.draw_phase1_form(screen)
        elif self.current_phase == 2:
            self.draw_phase2_availability(screen)
        elif self.current_phase == 3:
            self.draw_phase3_rejection_loop(screen)

        # Continue button when phase complete
        if self.phase_complete[self.current_phase]:
            self.draw_continue_button(screen)

        # Desperation indicator
        self.draw_desperation_meter(screen)

    def draw_phase1_form(self, screen):
        """Draw application form with harsh reality"""
        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render(f"Job Application #{self.applications_submitted + 1}", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        # Subtitle with instructions
        sub_font = pygame.font.Font(None, 24)
        subtitle = sub_font.render("Click on a field to start typing", True, (200, 180, 160))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 120))

        # Form background
        form_x = SCREEN_WIDTH // 2 - 300
        form_y = 160
        pygame.draw.rect(screen, (245, 245, 240), (form_x, form_y, 600, 400))
        pygame.draw.rect(screen, (100, 100, 100), (form_x, form_y, 600, 400), 2)

        # Form fields
        field_font = pygame.font.Font(None, 22)
        field_y = form_y + 30

        for field_name, field_data in self.form_fields.items():
            # Field label
            label = field_name.replace("_", " ").title() + ":"
            label_surf = field_font.render(label, True, (50, 50, 50))
            screen.blit(label_surf, (form_x + 20, field_y))

            # Field box
            field_rect = pygame.Rect(form_x + 200, field_y - 2, 350, 30)
            field_data["rect"] = field_rect

            # Draw field background
            is_active = (self.active_field == field_name)
            has_content = len(field_data["value"]) > 0

            if is_active:
                # Active field - white background
                pygame.draw.rect(screen, (255, 255, 255), field_rect)
            elif has_content:
                # Filled field - light green
                pygame.draw.rect(screen, (240, 255, 240), field_rect)
            else:
                # Empty field - light gray
                pygame.draw.rect(screen, (245, 245, 240), field_rect)

            # Border - highlight active field
            if is_active:
                pygame.draw.rect(screen, (100, 150, 255), field_rect, 3)  # Blue border
            elif self.hover_element == field_name:
                pygame.draw.rect(screen, (255, 220, 100), field_rect, 2)  # Yellow on hover
            else:
                pygame.draw.rect(screen, (100, 100, 100), field_rect, 1)  # Gray border

            # Draw value or placeholder
            if field_data["value"]:
                # Show actual value
                value_surf = field_font.render(field_data["value"], True, (0, 0, 0))
                screen.blit(value_surf, (field_rect.x + 5, field_rect.y + 5))

                # Draw cursor if active
                if is_active and int(self.animation_timer * 2) % 2 == 0:
                    cursor_x = field_rect.x + 5 + value_surf.get_width() + 2
                    pygame.draw.line(screen, (0, 0, 0),
                                   (cursor_x, field_rect.y + 5),
                                   (cursor_x, field_rect.y + 23), 2)
            else:
                # Show placeholder
                placeholder_surf = field_font.render(field_data["placeholder"], True, (150, 150, 150))
                screen.blit(placeholder_surf, (field_rect.x + 5, field_rect.y + 5))

                # Draw cursor if active
                if is_active and int(self.animation_timer * 2) % 2 == 0:
                    cursor_x = field_rect.x + 5
                    pygame.draw.line(screen, (0, 0, 0),
                                   (cursor_x, field_rect.y + 5),
                                   (cursor_x, field_rect.y + 23), 2)

            field_y += 70

        # Instruction text
        instruction_font = pygame.font.Font(None, 20)
        instruction_text = "* Click a field to edit. Press TAB/ENTER for next field. Max 50 characters per field."
        instruction_surf = instruction_font.render(instruction_text, True, (100, 100, 100))
        screen.blit(instruction_surf, (form_x + 20, form_y + 350))

        # Check if all fields have content (any content, including spaces)
        all_filled = all(len(field["value"]) > 0 for field in self.form_fields.values())
        self.phase_complete[1] = all_filled

    def draw_phase2_availability(self, screen):
        """Draw availability grid showing school/work conflict"""
        # Title
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("When Can You Work?", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        # Warning about school
        warning_font = pygame.font.Font(None, 22)
        warning = warning_font.render("⚠ Red slots conflict with school. Choose work or education.", True, (255, 100, 100))
        screen.blit(warning, (SCREEN_WIDTH // 2 - warning.get_width() // 2, 115))

        # Grid setup
        grid_x = 150
        grid_y = 160
        cell_width = 90
        cell_height = 50

        # Draw day headers
        day_font = pygame.font.Font(None, 24)
        for i, day in enumerate(self.days):
            day_surf = day_font.render(day, True, (255, 255, 255))
            day_x = grid_x + (i + 1) * cell_width + cell_width // 2 - day_surf.get_width() // 2
            screen.blit(day_surf, (day_x, grid_y - 25))

        # Draw time headers
        time_font = pygame.font.Font(None, 20)
        for i, time in enumerate(self.times):
            time_surf = time_font.render(time, True, (255, 255, 255))
            screen.blit(time_surf, (grid_x - 60, grid_y + i * cell_height + 15))

        # Draw grid cells
        for i, day in enumerate(self.days):
            for j, time in enumerate(self.times):
                cell_x = grid_x + (i + 1) * cell_width
                cell_y = grid_y + j * cell_height
                cell_rect = pygame.Rect(cell_x, cell_y, cell_width - 5, cell_height - 5)

                # Store rect for click detection
                self.availability_grid[(day, time)] = cell_rect

                # Check if selected
                is_selected = (day, time) in self.selected_slots
                is_school_conflict = (day, time) in self.school_conflicts

                # Draw cell
                if is_selected:
                    if is_school_conflict:
                        # Selected but conflicts with school - dark red
                        pygame.draw.rect(screen, (150, 50, 50), cell_rect)
                    else:
                        # Selected and available - green
                        pygame.draw.rect(screen, (50, 150, 50), cell_rect)
                elif is_school_conflict:
                    # School time - light red
                    pygame.draw.rect(screen, (100, 50, 50), cell_rect)
                else:
                    # Available slot - gray
                    pygame.draw.rect(screen, (70, 70, 70), cell_rect)

                pygame.draw.rect(screen, (200, 200, 200), cell_rect, 1)

                # Add checkmark if selected
                if is_selected:
                    check_font = pygame.font.Font(None, 30)
                    check = check_font.render("✓", True, (255, 255, 255))
                    screen.blit(check, (cell_x + cell_width // 2 - 15, cell_y + cell_height // 2 - 20))

        # Requirement text
        req_font = pygame.font.Font(None, 24)
        req_text = f"Manager requires FULL availability. Selected: {len(self.selected_slots)}/35 slots"
        req_color = (100, 255, 100) if len(self.selected_slots) >= 30 else (255, 100, 100)
        req_surf = req_font.render(req_text, True, req_color)
        screen.blit(req_surf, (SCREEN_WIDTH // 2 - req_surf.get_width() // 2, 480))

        # Education sacrifice counter
        school_sacrificed = len(self.selected_slots & self.school_conflicts)
        if school_sacrificed > 0:
            sacrifice_text = f"School hours sacrificed: {school_sacrificed}/3"
            sacrifice_surf = req_font.render(sacrifice_text, True, (255, 150, 50))
            screen.blit(sacrifice_surf, (SCREEN_WIDTH // 2 - sacrifice_surf.get_width() // 2, 510))

        # Check if enough availability
        self.phase_complete[2] = len(self.selected_slots) >= 25

    def draw_phase3_rejection_loop(self, screen):
        """Draw rejection messages with increasing desperation"""
        # Title
        title_font = pygame.font.Font(None, 36)
        title = title_font.render(f"Application #{self.applications_submitted}", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        # Show current status
        if not self.finally_hired and self.rejections_received < 47:
            # Another rejection
            self.draw_rejection(screen)
        else:
            # Finally hired!
            self.draw_hired(screen)

    def draw_rejection(self, screen):
        """Draw rejection message"""
        # Rejection envelope
        envelope_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 180, 400, 250)
        pygame.draw.rect(screen, (245, 245, 240), envelope_rect)
        pygame.draw.rect(screen, (100, 100, 100), envelope_rect, 2)

        # Company header
        header_font = pygame.font.Font(None, 28)
        company_names = ["QuickMart", "BurgerPlace", "MegaStore", "FoodChain", "RetailCo"]
        company = company_names[self.rejections_received % len(company_names)]
        header_text = header_font.render(company, True, (0, 0, 0))
        screen.blit(header_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2, 200))

        # Rejection message
        msg_font = pygame.font.Font(None, 22)
        rejection_msg = self.rejection_messages[self.current_rejection_index % len(self.rejection_messages)]

        # Word wrap the message
        words = rejection_msg.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if msg_font.size(test_line)[0] < 360:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        y_offset = 250
        for line in lines:
            line_surf = msg_font.render(line, True, (50, 50, 50))
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y_offset))
            y_offset += 30

        # Rejection stamp
        stamp_x = envelope_rect.x + envelope_rect.width - 180
        stamp_y = envelope_rect.y + envelope_rect.height - 80

        # Rotate stamp for effect
        rotated_stamp = pygame.transform.rotate(self.rejection_stamp, -15)
        screen.blit(rotated_stamp, (stamp_x, stamp_y))

        # Counter
        counter_font = pygame.font.Font(None, 24)
        counter_text = f"Rejections: {self.rejections_received}/47"
        counter_surf = counter_font.render(counter_text, True, (255, 100, 100))
        screen.blit(counter_surf, (SCREEN_WIDTH // 2 - counter_surf.get_width() // 2, 460))

        # Next button
        self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 40)
        pygame.draw.rect(screen, (150, 150, 150), self.continue_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.continue_button_rect, 2)

        button_font = pygame.font.Font(None, 24)
        button_text = "Try Again" if self.rejections_received < 46 else "One More Try..."
        button_surf = button_font.render(button_text, True, (255, 255, 255))
        button_x = self.continue_button_rect.centerx - button_surf.get_width() // 2
        button_y = self.continue_button_rect.centery - button_surf.get_height() // 2
        screen.blit(button_surf, (button_x, button_y))

    def draw_hired(self, screen):
        """Draw hiring confirmation"""
        # Success envelope
        envelope_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 180, 400, 300)
        pygame.draw.rect(screen, (240, 255, 240), envelope_rect)
        pygame.draw.rect(screen, (100, 200, 100), envelope_rect, 3)

        # Company header
        header_font = pygame.font.Font(None, 32)
        header_text = header_font.render("ValueMart Groceries", True, (0, 100, 0))
        screen.blit(header_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2, 200))

        # Hiring message
        msg_font = pygame.font.Font(None, 24)
        messages = [
            "Congratulations!",
            "We'd like to offer you a position:",
            "",
            "Part-Time Retail Associate",
            "$15/hour",
            "20 hours/week maximum",
            "No benefits",
            "Mandatory availability for all shifts",
            "",
            "Start: Tomorrow 6 AM"
        ]

        y_offset = 240
        for msg in messages:
            if msg == "":
                y_offset += 15
                continue
            msg_surf = msg_font.render(msg, True, (0, 80, 0) if "Congratulations" in msg else (50, 50, 50))
            screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, y_offset))
            y_offset += 25

        # Hired stamp
        stamp_x = envelope_rect.x + envelope_rect.width - 180
        stamp_y = envelope_rect.y + 20
        screen.blit(self.hired_stamp, (stamp_x, stamp_y))

        # Relief text
        relief_font = pygame.font.Font(None, 20)
        relief_text = "Finally... After 48 applications..."
        relief_surf = relief_font.render(relief_text, True, (100, 100, 100))
        screen.blit(relief_surf, (SCREEN_WIDTH // 2 - relief_surf.get_width() // 2, 510))

        self.phase_complete[3] = True

    def draw_desperation_meter(self, screen):
        """Draw desperation level indicator"""
        if self.current_phase < 3:
            return

        # Meter background
        meter_x = SCREEN_WIDTH - 150
        meter_y = 100
        meter_height = 300
        meter_width = 30

        pygame.draw.rect(screen, (50, 50, 50), (meter_x, meter_y, meter_width, meter_height))

        # Fill based on desperation
        fill_height = int((self.desperation_level / 100) * meter_height)
        fill_y = meter_y + meter_height - fill_height

        # Color gradient from yellow to red
        red = min(255, int(self.desperation_level * 2.55))
        green = max(0, 255 - int(self.desperation_level * 2.55))
        fill_color = (red, green, 0)

        pygame.draw.rect(screen, fill_color, (meter_x, fill_y, meter_width, fill_height))
        pygame.draw.rect(screen, (200, 200, 200), (meter_x, meter_y, meter_width, meter_height), 2)

        # Label
        label_font = pygame.font.Font(None, 20)
        label = label_font.render("Desperation", True, (200, 200, 200))
        screen.blit(label, (meter_x - 20, meter_y - 25))

    def draw_continue_button(self, screen):
        """Draw continue button when phase is complete"""
        button_font = pygame.font.Font(None, 32)

        if self.current_phase == 1:
            button_text = "Submit Application"
        elif self.current_phase == 2:
            button_text = "Send Availability"
        else:
            button_text = "Accept Position"

        button_surf = button_font.render(button_text, True, (255, 255, 255))

        self.continue_button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 120, 240, 50
        )

        button_color = (100, 150, 100)
        pygame.draw.rect(screen, button_color, self.continue_button_rect)

        if self.hover_element == "continue":
            pygame.draw.rect(screen, (255, 255, 255), self.continue_button_rect, 3)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self.continue_button_rect, 2)

        button_x = self.continue_button_rect.centerx - button_surf.get_width() // 2
        button_y = self.continue_button_rect.centery - button_surf.get_height() // 2
        screen.blit(button_surf, (button_x, button_y))

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        # Check continue button FIRST (before phase-specific handling)
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            if self.phase_complete[self.current_phase]:
                if self.current_phase < 3:
                    self.current_phase += 1
                    self.hover_element = None
                    self.applications_submitted += 1
                    if self.current_phase == 3:
                        # Start rejection loop
                        self.rejections_received = 0
                        self.current_rejection_index = 0
                    # Deactivate any active field when advancing phase
                    if self.active_field:
                        self.active_field = None
                        pygame.key.stop_text_input()
                return

        if self.current_phase == 1:
            # Check if clicked on a field
            clicked_field = None
            for field_name, field_data in self.form_fields.items():
                if field_data["rect"] and field_data["rect"].collidepoint(pos):
                    clicked_field = field_name
                    break

            if clicked_field:
                # Activate this field for text input
                self.active_field = clicked_field
                pygame.key.start_text_input()
            else:
                # Clicked outside all fields - deactivate current field
                if self.active_field:
                    self.active_field = None
                    pygame.key.stop_text_input()
            return

        elif self.current_phase == 2:
            # Handle availability grid clicks
            for (day, time), rect in self.availability_grid.items():
                if rect.collidepoint(pos):
                    slot = (day, time)
                    if slot in self.selected_slots:
                        self.selected_slots.remove(slot)
                    else:
                        self.selected_slots.add(slot)
                        # Increase desperation when sacrificing school
                        if slot in self.school_conflicts:
                            self.desperation_level = min(100, self.desperation_level + 10)

        elif self.current_phase == 3:
            # Handle rejection progression
            if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
                if not self.finally_hired:
                    self.rejections_received += 1
                    self.applications_submitted += 1
                    self.current_rejection_index += 1
                    self.desperation_level = min(100, self.desperation_level + 2)

                    # After 47 rejections, finally get hired
                    if self.rejections_received >= 47:
                        self.finally_hired = True
                else:
                    # Complete the activity
                    self.complete_application()
                return

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return

        self.hover_element = None

        if self.current_phase == 1:
            # Check form field hovers
            for field_name, field_data in self.form_fields.items():
                if field_data["rect"] and field_data["rect"].collidepoint(pos):
                    self.hover_element = field_name
                    break

        # Check continue button hover
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.hover_element = "continue"

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        # ESC to go back a phase (except in rejection loop)
        if key == pygame.K_ESCAPE:
            if self.current_phase > 1 and self.current_phase < 3:
                self.current_phase -= 1

    def complete_application(self):
        """Complete the job application process"""
        # Stop text input
        pygame.key.stop_text_input()
        self.active_field = None

        # Update parent interior state
        if self.narrative_ref:
            self.narrative_ref.got_hired = True
            self.narrative_ref.applied_count = 48

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            # Show completion message through parent's dialogue box
            if hasattr(self.narrative_ref, 'dialogue_box'):
                msg = "After 48 applications and 47 rejections, you finally got a job. "
                msg += "Part-time. Minimum wage. No benefits. But it's something."
                self.narrative_ref.dialogue_box.show(None, msg)

        # Mark activity complete
        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt

        # Update shake timer
        if self.shake_timer > 0:
            self.shake_timer -= dt

    def handle_event(self, event):
        """Handle pygame events including text input"""
        if not self.active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event.pos, event.button)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_key(event.key)

            # Handle text editing keys
            if self.active_field and self.current_phase == 1:
                if event.key == pygame.K_BACKSPACE:
                    # Remove last character
                    field_data = self.form_fields[self.active_field]
                    field_data["value"] = field_data["value"][:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                    # Move to next field
                    self.move_to_next_field()
        elif event.type == pygame.TEXTINPUT and self.active_field and self.current_phase == 1:
            # Add typed character
            self.handle_text_input(event.text)

    def handle_text_input(self, unicode_char):
        """Handle text input for active field"""
        if not self.active_field:
            return

        field_data = self.form_fields[self.active_field]

        # Limit field length to 50 characters
        if len(field_data["value"]) < 50:
            field_data["value"] += unicode_char

    def move_to_next_field(self):
        """Move focus to the next field"""
        if not self.active_field:
            return

        current_idx = self.field_order.index(self.active_field)
        if current_idx < len(self.field_order) - 1:
            self.active_field = self.field_order[current_idx + 1]
        else:
            # Last field - deactivate
            self.active_field = None
            pygame.key.stop_text_input()