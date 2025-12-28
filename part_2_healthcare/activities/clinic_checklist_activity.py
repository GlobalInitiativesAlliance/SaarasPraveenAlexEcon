"""
Clinic Documents Checklist Activity
Interactive experience checking off required documents at the clinic
"""
import pygame
import math

class ClinicChecklistActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game state
        self.checklist_progress = 0
        self.documents_checked = []
        self.current_document = 0
        self.all_checked = False
        self.completion_timer = 0

        # Required documents with status and emotional impact
        self.required_documents = [
            {
                "name": "Photo ID (Driver's License or State ID)",
                "description": "Required to verify your identity and eligibility",
                "checked": False,
                "concern": "Without ID, you can't prove who you are",
                "relief": "✓ Identity verified - you're in the system"
            },
            {
                "name": "Previous Medi-Cal Card",
                "description": "Shows your previous coverage and case number",
                "checked": False,
                "concern": "They need proof of your previous coverage",
                "relief": "✓ Coverage history confirmed"
            },
            {
                "name": "Proof of Income",
                "description": "Pay stubs, bank statements, or benefits letter",
                "checked": False,
                "concern": "Income verification determines your eligibility",
                "relief": "✓ Financial eligibility confirmed"
            }
        ]

        # Visual elements
        self.clipboard_rect = pygame.Rect(340, 80, 600, 560)
        self.paper_rect = pygame.Rect(370, 110, 540, 500)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (220, 220, 220)
        self.PAPER_WHITE = (248, 248, 248)
        self.CLINIC_BLUE = (41, 84, 144)
        self.CHECK_GREEN = (0, 150, 0)
        self.CHECKBOX_GRAY = (200, 200, 200)

        # Fonts
        self.font_header = pygame.font.Font(None, 32)
        self.font_doc_name = pygame.font.Font(None, 24)
        self.font_description = pygame.font.Font(None, 20)
        self.font_status = pygame.font.Font(None, 22)
        self.font_title = pygame.font.Font(None, 36)

        # Animation state
        self.pulse_timer = 0
        self.check_animations = {}

    def start(self):
        """Start the clinic checklist activity"""
        print("[CLINIC_CHECKLIST] Activity starting...")
        self.active = True
        self.completed = False
        self.checklist_progress = 0
        self.documents_checked = []
        self.current_document = 0
        self.all_checked = False
        self.completion_timer = 0
        self.pulse_timer = 0
        self.check_animations = {}

        # Reset all document checks
        for doc in self.required_documents:
            doc["checked"] = False

        print("[CLINIC_CHECKLIST] Activity started successfully!")

    def stop(self):
        """Stop the clinic checklist activity"""
        print("[CLINIC_CHECKLIST] Activity stopping...")
        self.active = False

    def handle_event(self, event):
        """Handle player input"""
        print(f"[CLINIC_CHECKLIST] handle_event called: active={self.active}, completed={self.completed}, event_type={event.type}")

        if not self.active or self.completed:
            print(f"[CLINIC_CHECKLIST] Ignoring event - not active or completed")
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print("[CLINIC_CHECKLIST] Mouse click detected")
            mouse_pos = event.pos
            self.handle_checkbox_click(mouse_pos)

        elif event.type == pygame.KEYDOWN:
            print(f"[CLINIC_CHECKLIST] Key pressed: {event.key}")
            if event.key == pygame.K_SPACE:
                print("[CLINIC_CHECKLIST] SPACE key pressed")
                if self.all_checked and self.completion_timer <= 0:
                    self.complete_activity()
                else:
                    self.check_next_document()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events from main game engine"""
        print(f"[CLINIC_CHECKLIST] handle_mouse_click called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release events from main game engine"""
        print(f"[CLINIC_CHECKLIST] handle_mouse_release called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONUP, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_checkbox_click(self, mouse_pos):
        """Handle clicking on checkboxes"""
        for i, doc in enumerate(self.required_documents):
            if doc["checked"]:
                continue

            # Calculate checkbox position
            checkbox_x = self.paper_rect.x + 30
            checkbox_y = self.paper_rect.y + 120 + (i * 120)
            checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, 25, 25)

            if checkbox_rect.collidepoint(mouse_pos):
                print(f"[CLINIC_CHECKLIST] Checking document: {doc['name']}")
                doc["checked"] = True
                self.documents_checked.append(i)
                self.check_animations[i] = 1.0  # Start check animation

                # Check if all documents are now checked
                if all(doc["checked"] for doc in self.required_documents):
                    self.all_checked = True
                    self.completion_timer = 3.0  # 3 seconds to show completion
                    print("[CLINIC_CHECKLIST] All documents checked!")

                break

    def check_next_document(self):
        """Check the next document in sequence"""
        for i, doc in enumerate(self.required_documents):
            if not doc["checked"]:
                print(f"[CLINIC_CHECKLIST] Auto-checking document: {doc['name']}")
                doc["checked"] = True
                self.documents_checked.append(i)
                self.check_animations[i] = 1.0
                break

        # Check if all documents are now checked
        if all(doc["checked"] for doc in self.required_documents):
            self.all_checked = True
            self.completion_timer = 3.0

    def complete_activity(self):
        """Complete the clinic checklist activity"""
        print("[CLINIC_CHECKLIST] Completing activity...")
        self.completed = True

        if self.objective_manager:
            print("[CLINIC_CHECKLIST] Completed document checklist...")
            self.objective_manager.complete_current_objective()

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update timers
        self.pulse_timer += dt

        # Update check animations
        for doc_id in list(self.check_animations.keys()):
            self.check_animations[doc_id] = max(0, self.check_animations[doc_id] - dt * 2)
            if self.check_animations[doc_id] <= 0:
                del self.check_animations[doc_id]

        # Update completion timer
        if self.all_checked and self.completion_timer > 0:
            self.completion_timer -= dt
            if self.completion_timer <= 0:
                # Auto-complete after showing completion state
                self.complete_activity()

    def draw_clipboard(self, screen):
        """Draw the clinic clipboard"""
        # Clipboard shadow
        shadow_rect = self.clipboard_rect.copy()
        shadow_rect.x += 8
        shadow_rect.y += 8
        pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=10)

        # Clipboard body
        pygame.draw.rect(screen, (139, 69, 19), self.clipboard_rect, border_radius=10)

        # Metal clip at top
        clip_rect = pygame.Rect(self.clipboard_rect.centerx - 40, self.clipboard_rect.y - 10, 80, 20)
        pygame.draw.rect(screen, (192, 192, 192), clip_rect, border_radius=5)

        # Paper
        pygame.draw.rect(screen, self.PAPER_WHITE, self.paper_rect)
        pygame.draw.rect(screen, self.BLACK, self.paper_rect, 2)

    def draw_header(self, screen):
        """Draw the checklist header"""
        # Clinic logo area
        logo_rect = pygame.Rect(self.paper_rect.x + 20, self.paper_rect.y + 20, self.paper_rect.width - 40, 60)
        pygame.draw.rect(screen, self.CLINIC_BLUE, logo_rect)

        # Header text
        header_text = self.font_title.render("COMMUNITY HEALTH CLINIC", True, self.WHITE)
        header_rect = header_text.get_rect(center=(logo_rect.centerx, logo_rect.centery - 10))
        screen.blit(header_text, header_rect)

        # Subtitle
        subtitle_text = self.font_description.render("Required Documents Checklist", True, self.WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(logo_rect.centerx, logo_rect.centery + 15))
        screen.blit(subtitle_text, subtitle_rect)

    def draw_document_checklist(self, screen):
        """Draw the document checklist"""
        start_y = self.paper_rect.y + 100

        for i, doc in enumerate(self.required_documents):
            doc_y = start_y + (i * 120)

            # Document section background
            doc_rect = pygame.Rect(self.paper_rect.x + 20, doc_y, self.paper_rect.width - 40, 100)

            # Highlight if being checked
            if i in self.check_animations:
                intensity = self.check_animations[i]
                highlight_color = (int(200 + 55 * intensity), int(255 * intensity), int(200 + 55 * intensity))
                pygame.draw.rect(screen, highlight_color, doc_rect, border_radius=5)

            pygame.draw.rect(screen, self.LIGHT_GRAY, doc_rect, 2, border_radius=5)

            # Checkbox
            checkbox_x = doc_rect.x + 10
            checkbox_y = doc_rect.y + 10
            checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, 25, 25)

            if doc["checked"]:
                # Checked box
                pygame.draw.rect(screen, self.CHECK_GREEN, checkbox_rect)
                pygame.draw.rect(screen, self.BLACK, checkbox_rect, 2)

                # Checkmark
                check_points = [
                    (checkbox_x + 6, checkbox_y + 13),
                    (checkbox_x + 11, checkbox_y + 18),
                    (checkbox_x + 19, checkbox_y + 8)
                ]
                pygame.draw.lines(screen, self.WHITE, False, check_points, 3)
            else:
                # Empty checkbox
                pygame.draw.rect(screen, self.WHITE, checkbox_rect)
                pygame.draw.rect(screen, self.BLACK, checkbox_rect, 2)

            # Document name
            name_text = self.font_doc_name.render(doc["name"], True, self.BLACK)
            screen.blit(name_text, (checkbox_x + 35, checkbox_y))

            # Document description
            desc_text = self.font_description.render(doc["description"], True, self.GRAY)
            screen.blit(desc_text, (checkbox_x + 35, checkbox_y + 25))

            # Status message
            if doc["checked"]:
                status_text = self.font_status.render(doc["relief"], True, self.CHECK_GREEN)
                screen.blit(status_text, (checkbox_x + 35, checkbox_y + 50))
            else:
                concern_text = self.font_status.render(doc["concern"], True, self.RED)
                screen.blit(concern_text, (checkbox_x + 35, checkbox_y + 50))

    def draw_progress_indicator(self, screen):
        """Draw checklist completion progress"""
        checked_count = len(self.documents_checked)
        total_count = len(self.required_documents)

        # Progress bar
        progress_rect = pygame.Rect(self.paper_rect.x + 30, self.paper_rect.bottom - 80, self.paper_rect.width - 60, 20)
        pygame.draw.rect(screen, self.LIGHT_GRAY, progress_rect)

        if checked_count > 0:
            progress_width = int((checked_count / total_count) * progress_rect.width)
            filled_rect = pygame.Rect(progress_rect.x, progress_rect.y, progress_width, progress_rect.height)
            pygame.draw.rect(screen, self.CHECK_GREEN, filled_rect)

        # Progress text
        progress_text = f"Documents: {checked_count}/{total_count} Complete"
        text_surface = self.font_status.render(progress_text, True, self.BLACK)
        text_rect = text_surface.get_rect(center=(progress_rect.centerx, progress_rect.y - 15))
        screen.blit(text_surface, text_rect)

    def draw_completion_message(self, screen):
        """Draw completion message when all documents are checked"""
        if not self.all_checked:
            return

        # Pulsing completion message
        pulse = math.sin(self.pulse_timer * 4) * 0.2 + 0.8

        completion_messages = [
            "✓ All documents verified!",
            "You're ready to proceed with your application",
            "The clinic staff will review your paperwork"
        ]

        message_y = self.paper_rect.bottom - 50
        for i, message in enumerate(completion_messages):
            alpha = int(pulse * 255)
            color = (int(34 * pulse), int(139 * pulse), int(34 * pulse))

            message_surface = self.font_status.render(message, True, color)
            message_rect = message_surface.get_rect(center=(self.paper_rect.centerx, message_y + i * 25))
            screen.blit(message_surface, message_rect)

    def draw(self, screen):
        """Render the clinic checklist interface"""
        if not self.active:
            return

        # Dark background for focus
        screen.fill((30, 40, 50))

        # Draw clipboard
        self.draw_clipboard(screen)
        self.draw_header(screen)
        self.draw_document_checklist(screen)
        self.draw_progress_indicator(screen)
        self.draw_completion_message(screen)

        # Instructions
        if not self.all_checked:
            instruction = "Click checkboxes or press SPACE to check documents..."
            instruction_surface = self.font_description.render(instruction, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)
        elif self.completion_timer > 0:
            instruction = "Documents verified! Preparing to continue..."
            instruction_surface = self.font_description.render(instruction, True, self.CHECK_GREEN)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)