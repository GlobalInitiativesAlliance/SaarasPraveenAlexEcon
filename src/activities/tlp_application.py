"""
TLP Application Activity
A soul-crushing 50-page application highlighting bureaucratic barriers
"""
import pygame
import math
from src.activities.activities import Activity
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class TLPApplication(Activity):
    """Interactive TLP application form showing the overwhelming bureaucracy"""

    def __init__(self, game):
        super().__init__(game)
        self.narrative_ref = None  # Set by parent interior

        # Application state
        self.current_page = 1
        self.total_pages = 12  # Simplified from actual 50 for gameplay
        self.completed_fields = 0
        self.required_fields = 156  # Realistic number
        self.missing_documents = []
        self.errors = []
        self.time_spent = 0

        # Form sections
        self.sections = [
            {"name": "Personal Information", "fields": 18, "completed": False},
            {"name": "Housing History", "fields": 24, "completed": False},
            {"name": "Homelessness Verification", "fields": 15, "completed": False},
            {"name": "Income & Employment", "fields": 20, "completed": False},
            {"name": "Education Background", "fields": 12, "completed": False},
            {"name": "Medical History", "fields": 22, "completed": False},
            {"name": "Mental Health", "fields": 18, "completed": False},
            {"name": "Substance Use", "fields": 10, "completed": False},
            {"name": "Criminal Background", "fields": 8, "completed": False},
            {"name": "References", "fields": 6, "completed": False},
            {"name": "Emergency Contacts", "fields": 3, "completed": False}
        ]

        # Current section being filled
        self.current_section = 0
        self.section_progress = 0

        # Required documents (most you don't have)
        self.required_docs = [
            {"name": "Birth Certificate", "have": False, "note": "Lost in move"},
            {"name": "Social Security Card", "have": True, "note": "Worn but readable"},
            {"name": "Photo ID", "have": False, "note": "Expired last month"},
            {"name": "Proof of Homelessness", "have": False, "note": "How do you prove this?"},
            {"name": "Income Verification", "have": False, "note": "Just got job, no stubs yet"},
            {"name": "Medical Records", "have": False, "note": "Which doctor? When?"},
            {"name": "School Transcripts", "have": False, "note": "School wants $25 fee"},
            {"name": "Reference Letters (3)", "have": False, "note": "Who would write these?"}
        ]

        # Visual state
        self.scroll_offset = 0
        self.frustration_level = 0
        self.hope_remaining = 100
        self.hand_cramp_timer = 0
        self.blink_timer = 0

        # UI elements
        self.submit_button_rect = None
        self.next_button_rect = None
        self.scroll_bar_rect = None

        # Colors
        self.form_bg = (250, 248, 245)
        self.field_color = (255, 255, 255)
        self.error_color = (255, 100, 100)
        self.complete_color = (100, 255, 100)

    def start(self):
        """Start the application activity"""
        super().start()
        self.current_page = 1
        self.time_spent = 0
        self.frustration_level = 0

    def draw(self, screen):
        """Main draw function"""
        if not self.active:
            return

        # White background (harsh office lighting)
        screen.fill(self.form_bg)

        # Update timers
        self.time_spent += 0.016
        self.blink_timer += 0.016
        self.hand_cramp_timer += 0.016

        # Draw form header
        self.draw_header(screen)

        # Draw current section
        self.draw_current_section(screen)

        # Draw document checklist
        self.draw_document_checklist(screen)

        # Draw progress and frustration
        self.draw_progress_meters(screen)

        # Draw navigation buttons
        self.draw_navigation(screen)

        # Draw errors and warnings
        self.draw_errors(screen)

    def draw_header(self, screen):
        """Draw the form header with official seals and warnings"""
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 120)
        pygame.draw.rect(screen, (230, 225, 220), header_rect)
        pygame.draw.line(screen, (180, 175, 170), (0, 120), (SCREEN_WIDTH, 120), 2)

        # Title
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("TRANSITIONAL LIVING PROGRAM APPLICATION", True, (50, 45, 40))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title, title_rect)

        # Form number and version (bureaucratic detail)
        form_font = pygame.font.Font(None, 18)
        form_text = form_font.render("Form TLP-2024-A Rev. 3.2.1", True, (120, 115, 110))
        screen.blit(form_text, (50, 60))

        # Warning text
        warning_font = pygame.font.Font(None, 16)
        warning = warning_font.render("INCOMPLETE APPLICATIONS WILL BE REJECTED WITHOUT REVIEW", True, self.error_color)
        warning_rect = warning.get_rect(center=(SCREEN_WIDTH // 2, 85))

        # Blinking effect for warning
        if int(self.blink_timer * 2) % 2 == 0:
            screen.blit(warning, warning_rect)

        # Page indicator
        page_text = form_font.render(f"Page {self.current_page} of {self.total_pages}", True, (100, 95, 90))
        screen.blit(page_text, (SCREEN_WIDTH - 150, 60))

    def draw_current_section(self, screen):
        """Draw the current form section"""
        section = self.sections[self.current_section]
        y_pos = 140

        # Section title
        section_font = pygame.font.Font(None, 28)
        section_title = section_font.render(f"Section {self.current_section + 1}: {section['name']}", True, (70, 65, 60))
        screen.blit(section_title, (50, y_pos))
        y_pos += 40

        # Required fields asterisk
        asterisk_font = pygame.font.Font(None, 20)
        asterisk_text = asterisk_font.render("* Required Field", True, self.error_color)
        screen.blit(asterisk_text, (50, y_pos))
        y_pos += 35

        # Draw form fields (simplified representation)
        field_font = pygame.font.Font(None, 22)
        field_height = 30
        fields_to_show = min(8, section['fields'] - self.section_progress)

        for i in range(fields_to_show):
            field_num = self.section_progress + i + 1

            # Field label
            field_labels = self.get_field_labels(section['name'], field_num)
            label = field_labels if isinstance(field_labels, str) else field_labels[0]

            # Draw field background
            field_rect = pygame.Rect(50, y_pos, SCREEN_WIDTH - 100, field_height)
            field_color = self.field_color if field_num > self.section_progress else (230, 255, 230)
            pygame.draw.rect(screen, field_color, field_rect)
            pygame.draw.rect(screen, (200, 195, 190), field_rect, 1)

            # Draw asterisk for required
            asterisk = field_font.render("*", True, self.error_color)
            screen.blit(asterisk, (55, y_pos + 5))

            # Draw field label
            label_text = field_font.render(label, True, (80, 75, 70))
            screen.blit(label_text, (70, y_pos + 5))

            # Show "COMPLETED" for filled fields
            if field_num <= self.section_progress:
                complete_font = pygame.font.Font(None, 18)
                complete = complete_font.render("✓ FILLED", True, self.complete_color)
                screen.blit(complete, (SCREEN_WIDTH - 150, y_pos + 6))

            y_pos += field_height + 10

        # Show section completion
        if section['completed']:
            complete_font = pygame.font.Font(None, 24)
            complete_text = complete_font.render(f"✓ Section Complete ({section['fields']}/{section['fields']} fields)",
                                                True, self.complete_color)
            screen.blit(complete_text, (50, y_pos + 20))

    def get_field_labels(self, section_name, field_num):
        """Get realistic field labels based on section"""
        field_labels = {
            "Personal Information": [
                "Legal First Name", "Legal Middle Name", "Legal Last Name",
                "Preferred Name", "Date of Birth (MM/DD/YYYY)", "Social Security Number",
                "Current Phone", "Alternative Phone", "Email Address",
                "Mailing Address (if any)", "Last Permanent Address", "County of Origin"
            ],
            "Housing History": [
                "Current living situation", "How long at current location?",
                "Previous address #1", "Dates at previous address #1", "Reason for leaving #1",
                "Landlord name #1", "Landlord phone #1", "Eviction from #1? (Y/N)"
            ],
            "Homelessness Verification": [
                "Date homelessness began", "Number of times homeless in past 3 years",
                "Total months homeless", "Causes of homelessness (check all that apply)",
                "Shelter name (if applicable)", "Case worker name", "Case worker phone"
            ]
        }

        section_fields = field_labels.get(section_name, [f"Field {field_num}"])
        if field_num <= len(section_fields):
            return section_fields[field_num - 1]
        return f"{section_name} Field {field_num}"

    def draw_document_checklist(self, screen):
        """Draw the required documents checklist"""
        # Document panel on the right
        panel_rect = pygame.Rect(SCREEN_WIDTH - 300, 140, 280, 400)
        pygame.draw.rect(screen, (240, 235, 230), panel_rect)
        pygame.draw.rect(screen, (180, 175, 170), panel_rect, 2)

        # Title
        doc_font = pygame.font.Font(None, 22)
        title = doc_font.render("Required Documents", True, (60, 55, 50))
        screen.blit(title, (SCREEN_WIDTH - 280, 150))

        # Document list
        y_pos = 180
        item_font = pygame.font.Font(None, 18)
        missing_count = 0

        for doc in self.required_docs:
            # Checkbox
            box_rect = pygame.Rect(SCREEN_WIDTH - 280, y_pos, 15, 15)
            pygame.draw.rect(screen, (255, 255, 255), box_rect)
            pygame.draw.rect(screen, (150, 145, 140), box_rect, 1)

            if doc['have']:
                # Draw checkmark
                check_font = pygame.font.Font(None, 20)
                check = check_font.render("✓", True, self.complete_color)
                screen.blit(check, (SCREEN_WIDTH - 280, y_pos - 2))
            else:
                missing_count += 1
                # Draw X
                x_font = pygame.font.Font(None, 20)
                x_mark = x_font.render("✗", True, self.error_color)
                screen.blit(x_mark, (SCREEN_WIDTH - 280, y_pos - 2))

            # Document name
            color = (100, 95, 90) if doc['have'] else (180, 50, 50)
            doc_text = item_font.render(doc['name'], True, color)
            screen.blit(doc_text, (SCREEN_WIDTH - 260, y_pos))

            # Note for missing docs
            if not doc['have'] and doc['note']:
                note_font = pygame.font.Font(None, 14)
                note = note_font.render(f"  {doc['note']}", True, (150, 130, 110))
                screen.blit(note, (SCREEN_WIDTH - 260, y_pos + 18))
                y_pos += 18

            y_pos += 25

        # Missing documents warning
        if missing_count > 0:
            warning_font = pygame.font.Font(None, 16)
            warning = warning_font.render(f"⚠ Missing {missing_count} documents", True, self.error_color)
            screen.blit(warning, (SCREEN_WIDTH - 280, y_pos + 10))

    def draw_progress_meters(self, screen):
        """Draw progress bars and frustration indicators"""
        y_pos = 560

        # Overall progress
        progress_font = pygame.font.Font(None, 20)
        progress_text = progress_font.render(f"Overall Progress: {self.completed_fields}/{self.required_fields} fields",
                                           True, (80, 75, 70))
        screen.blit(progress_text, (50, y_pos))

        # Progress bar
        progress_rect = pygame.Rect(50, y_pos + 25, 400, 20)
        pygame.draw.rect(screen, (220, 215, 210), progress_rect)
        pygame.draw.rect(screen, (150, 145, 140), progress_rect, 2)

        # Fill progress
        progress_width = int((self.completed_fields / self.required_fields) * 400)
        if progress_width > 0:
            fill_rect = pygame.Rect(50, y_pos + 25, progress_width, 20)
            pygame.draw.rect(screen, (100, 200, 100), fill_rect)

        # Percentage
        percentage = int((self.completed_fields / self.required_fields) * 100)
        percent_text = progress_font.render(f"{percentage}%", True, (60, 55, 50))
        screen.blit(percent_text, (460, y_pos + 25))

        # Time spent
        y_pos += 55
        hours = int(self.time_spent // 3600)
        minutes = int((self.time_spent % 3600) // 60)
        time_text = progress_font.render(f"Time Spent: {hours}h {minutes}m", True, (100, 95, 90))
        screen.blit(time_text, (50, y_pos))

        # Hope remaining (decreases over time)
        self.hope_remaining = max(10, self.hope_remaining - 0.01)
        hope_text = progress_font.render(f"Hope Remaining: {int(self.hope_remaining)}%", True, (150, 130, 110))
        screen.blit(hope_text, (250, y_pos))

        # Hand cramp indicator (humor in the horror)
        if self.hand_cramp_timer > 30:
            cramp_font = pygame.font.Font(None, 18)
            cramp = cramp_font.render("✋ Hand cramping...", True, (200, 100, 100))
            screen.blit(cramp, (450, y_pos))

    def draw_navigation(self, screen):
        """Draw navigation buttons"""
        button_y = 650

        # Skip ahead button (simulating filling out form)
        if self.current_section < len(self.sections) - 1 or self.section_progress < self.sections[self.current_section]['fields']:
            next_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y, 140, 40)
            self.next_button_rect = next_rect

            mouse_pos = pygame.mouse.get_pos()
            if next_rect.collidepoint(mouse_pos):
                button_color = (100, 150, 100)
                text_color = (255, 255, 255)
            else:
                button_color = (80, 130, 80)
                text_color = (240, 240, 240)

            pygame.draw.rect(screen, button_color, next_rect)
            pygame.draw.rect(screen, (60, 100, 60), next_rect, 2)

            button_font = pygame.font.Font(None, 24)
            button_text = button_font.render("Fill Fields →", True, text_color)
            text_rect = button_text.get_rect(center=next_rect.center)
            screen.blit(button_text, text_rect)

        # Submit button (always visible after 70% complete)
        if self.completed_fields >= self.required_fields * 0.7:  # 70% complete for gameplay
            submit_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, button_y, 140, 40)
            self.submit_button_rect = submit_rect

            mouse_pos = pygame.mouse.get_pos()

            # Check if we have missing documents
            missing_docs = []
            for doc_info in self.required_docs:
                if not doc_info['have']:
                    missing_docs.append(doc_info['name'])

            has_missing = len(missing_docs) > 0

            if submit_rect.collidepoint(mouse_pos):
                if has_missing:
                    button_color = (180, 120, 60)  # Orange when missing docs
                    text_color = (255, 255, 255)
                else:
                    button_color = (100, 150, 100)  # Green when complete
                    text_color = (255, 255, 255)
            else:
                if has_missing:
                    button_color = (160, 100, 40)  # Darker orange
                    text_color = (240, 240, 240)
                else:
                    button_color = (80, 130, 80)   # Darker green
                    text_color = (240, 240, 240)

            pygame.draw.rect(screen, button_color, submit_rect)

            # Border color also indicates status
            border_color = (120, 80, 20) if has_missing else (60, 100, 60)
            pygame.draw.rect(screen, border_color, submit_rect, 2)

            button_font = pygame.font.Font(None, 20)
            button_text_str = "Submit Anyway" if has_missing else "SUBMIT"
            button_text = button_font.render(button_text_str, True, text_color)
            text_rect = button_text.get_rect(center=submit_rect.center)
            screen.blit(button_text, text_rect)

            # Show missing document count near button
            if has_missing:
                missing_font = pygame.font.Font(None, 16)
                missing_text = missing_font.render(f"Missing {len(missing_docs)} docs", True, (200, 150, 100))
                screen.blit(missing_text, (submit_rect.x, submit_rect.y - 20))

        # Give up button (the temptation)
        give_up_rect = pygame.Rect(50, button_y, 100, 40)
        mouse_pos = pygame.mouse.get_pos()
        if give_up_rect.collidepoint(mouse_pos):
            button_color = (150, 100, 100)
            text_color = (255, 255, 255)
        else:
            button_color = (130, 80, 80)
            text_color = (240, 240, 240)

        pygame.draw.rect(screen, button_color, give_up_rect)
        pygame.draw.rect(screen, (100, 60, 60), give_up_rect, 2)

        button_font = pygame.font.Font(None, 20)
        button_text = button_font.render("Give Up", True, text_color)
        text_rect = button_text.get_rect(center=give_up_rect.center)
        screen.blit(button_text, text_rect)

    def draw_errors(self, screen):
        """Draw error messages and warnings"""
        if self.errors:
            error_y = 500
            error_font = pygame.font.Font(None, 18)
            for error in self.errors[-3:]:  # Show last 3 errors
                error_text = error_font.render(f"❌ {error}", True, self.error_color)
                screen.blit(error_text, (50, error_y))
                error_y += 22

        # Call parent draw for completion feedback system
        super().draw(screen)

    def update(self, dt):
        """Update TLP application activity"""
        # Call parent update for completion feedback system
        super().update(dt)

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active:
            return

        if button == 1:  # Left click
            # Next/Fill button
            if self.next_button_rect and self.next_button_rect.collidepoint(pos):
                self.fill_next_fields()

            # Submit button
            elif self.submit_button_rect and self.submit_button_rect.collidepoint(pos):
                self.submit_application()

    def fill_next_fields(self):
        """Simulate filling out the next set of fields"""
        section = self.sections[self.current_section]

        # Fill 5 fields at a time
        fields_to_fill = min(5, section['fields'] - self.section_progress)
        self.section_progress += fields_to_fill
        self.completed_fields += fields_to_fill
        self.frustration_level += 10

        # Check if section complete
        if self.section_progress >= section['fields']:
            section['completed'] = True
            self.section_progress = 0

            # Move to next section if available
            if self.current_section < len(self.sections) - 1:
                self.current_section += 1
                self.current_page += 1

        # Random errors
        import random
        if random.random() < 0.2:
            self.errors.append("Session timeout. Please re-enter previous page.")
            self.completed_fields = max(0, self.completed_fields - 3)

    def submit_application(self):
        """Submit the application"""
        missing = [doc['name'] for doc in self.required_docs if not doc['have']]

        # Update housing office state
        if self.narrative_ref:
            self.narrative_ref.application_submitted = True
            self.narrative_ref.waitlist_position = 47

        # Show completion message through narrative dialogue
        if self.narrative_ref and hasattr(self.narrative_ref, 'dialogue_box'):
            if missing:
                msg = f"Application submitted with {len(missing)} missing documents. "
                msg += "You're added to waitlist #47. Estimated wait: 6-8 months."
            else:
                msg = "Application submitted with all documents! "
                msg += "You're on waitlist #47. Estimated wait: 6-8 months."
            self.narrative_ref.dialogue_box.show(None, msg)

        # Complete the activity
        self.complete()

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if key == pygame.K_ESCAPE:
            self.complete()
        elif key == pygame.K_SPACE:
            # Quick fill for testing
            self.fill_next_fields()

    def handle_mouse_motion(self, pos):
        """Track mouse movement for hover effects"""
        pass

    def update(self, dt):
        """Update animation timers"""
        if self.active:
            self.time_spent += dt
            self.blink_timer += dt
            self.hand_cramp_timer += dt