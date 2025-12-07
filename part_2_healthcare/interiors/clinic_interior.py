"""
Community Health Clinic Interior
Handles Medi-Cal reapplication process and document checklist
"""
import pygame
from ..activities.clinic_mini_game_manager import ClinicMiniGameManager

class CommunityHealthClinicInterior:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.active = False

        # Initialize mini-game manager
        self.mini_game_manager = ClinicMiniGameManager(game.objective_manager if hasattr(game, 'objective_manager') else None)

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.LIGHT_BLUE = (173, 216, 230)
        self.GRAY = (128, 128, 128)
        self.RED = (220, 20, 60)

        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)

        # Clinic state
        self.current_step = "welcome"  # welcome, checklist, application, approval, waiting
        self.documents_checked = {"id": False, "medicaid_card": False, "income_proof": False}
        self.application_answers = {}
        self.current_question = 0

        # Application questions
        self.questions = [
            {
                "text": "What is your current age?",
                "options": ["17", "18-20", "21-24", "25+"],
                "correct": 1  # 18-20
            },
            {
                "text": "How long have you lived in California?",
                "options": ["Less than 6 months", "6 months - 1 year", "1-2 years", "More than 2 years"],
                "correct": 3  # More than 2 years
            },
            {
                "text": "When did you age out of foster care?",
                "options": ["Never in foster care", "More than 2 years ago", "Within the last 2 years", "Still in care"],
                "correct": 2  # Within the last 2 years
            },
            {
                "text": "Do you have current income documentation?",
                "options": ["No income", "Part-time job", "Full-time job", "Benefits only"],
                "correct": 1  # Part-time job
            }
        ]

        # UI elements
        self.checklist_boxes = [
            pygame.Rect(300, 200, 30, 30),  # ID
            pygame.Rect(300, 250, 30, 30),  # Medi-Cal card
            pygame.Rect(300, 300, 30, 30)   # Income proof
        ]

        # Interactive objects
        self.interactive_objects = {}

    def enter(self):
        """Enter the clinic"""
        self.active = True
        self.current_step = "welcome"

        # Initialize interactive objects for current objective
        self.interactive_objects = {}

        if self.game.objective_manager:
            current_obj = self.game.objective_manager.get_current_objective()
            print(f"[CLINIC] Current objective: {current_obj.id if current_obj else 'None'}")

            if current_obj and current_obj.id == "clinic_checklist":
                # Add E key interaction for document checklist
                self.add_interactive_object('check_documents', {
                    'position': (8, 6),  # Center of clinic
                    'prompt': 'Show required documents',
                    'trigger_activity': 'clinic_checklist'
                })
                print(f"[CLINIC] Added clinic_checklist interaction")

            elif current_obj and current_obj.id in ["travel_to_clinic", "foster_youth_application", "application_approved"]:
                # For other objectives, auto-start mini-games
                self.mini_game_manager.start_mini_game(current_obj.id)

    def exit(self):
        """Exit the clinic"""
        self.active = False
        if self.game.objective_manager:
            current_obj = self.game.objective_manager.get_current_objective()
            if current_obj and current_obj.id in ["travel_to_clinic", "clinic_checklist",
                                                 "foster_youth_application", "application_approved"]:
                # Let the game world handle objective completion
                pass

    def handle_event(self, event):
        """Handle player input in the clinic"""
        if not self.active:
            return False

        # Let mini-game manager handle events first
        if self.mini_game_manager.active:
            self.mini_game_manager.handle_event(event)
            return True

        if event.type == pygame.KEYDOWN:
            print(f"[CLINIC] Key pressed: {event.key}")

            if event.key == pygame.K_e:
                print("[CLINIC] E key detected in clinic!")
                # Check for nearby interactive objects
                obj_name, obj = self.check_interactions()
                print(f"[CLINIC] Interaction check result: obj_name={obj_name}, obj={obj}")

                if obj:
                    print(f"[CLINIC] Triggering interaction: {obj_name}")
                    self.interact_with_object(obj_name)
                    return True
                else:
                    print("[CLINIC] No interactions found")

            elif event.key == pygame.K_ESCAPE:
                self.exit()
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            if self.current_step == "welcome":
                # Click to start checklist
                self.current_step = "checklist"

            elif self.current_step == "checklist":
                # Check document boxes
                for i, box in enumerate(self.checklist_boxes):
                    if box.collidepoint(mouse_pos):
                        doc_keys = ["id", "medicaid_card", "income_proof"]
                        self.documents_checked[doc_keys[i]] = True

                # Check if all documents are checked
                if all(self.documents_checked.values()):
                    self.current_step = "application"

            elif self.current_step == "application":
                # Handle question answers
                if self.current_question < len(self.questions):
                    question = self.questions[self.current_question]

                    # Check answer clicks
                    for i, option in enumerate(question["options"]):
                        option_rect = pygame.Rect(350, 300 + (i * 50), 400, 40)
                        if option_rect.collidepoint(mouse_pos):
                            self.application_answers[self.current_question] = i
                            self.current_question += 1
                            break

                    # Check if application is complete
                    if self.current_question >= len(self.questions):
                        self.current_step = "approval"

            elif self.current_step == "approval":
                # Click to acknowledge approval
                self.current_step = "waiting"
                if self.game.objective_manager:
                    self.game.objective_manager.advance_to_next_objective()

        return True

    def update(self, dt):
        """Update clinic state"""
        if not self.active:
            return

        # Update mini-game manager
        self.mini_game_manager.update(dt)

    def render(self, screen):
        """Render the clinic interior"""
        if not self.active:
            return

        # If mini-game is active, let it draw instead
        if self.mini_game_manager.active:
            self.mini_game_manager.draw(screen)
            return

        # Background
        screen.fill(self.LIGHT_BLUE)

        # Clinic sign
        title = self.font_large.render("Community Health Clinic", True, self.BLUE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)

        if self.current_step == "welcome":
            self.render_welcome(screen)
        elif self.current_step == "checklist":
            self.render_checklist(screen)
        elif self.current_step == "application":
            self.render_application(screen)
        elif self.current_step == "approval":
            self.render_approval(screen)
        elif self.current_step == "waiting":
            self.render_waiting(screen)

        # Exit instruction
        exit_text = self.font_small.render("Press ESC to exit", True, self.GRAY)
        screen.blit(exit_text, (20, self.SCREEN_HEIGHT - 40))

    def render_welcome(self, screen):
        """Render welcome screen"""
        welcome_text = [
            "Welcome to the Community Health Clinic",
            "",
            "We help young adults navigate health insurance",
            "and access affordable healthcare services.",
            "",
            "Click anywhere to begin your application."
        ]

        y = 200
        for line in welcome_text:
            if line:
                text = self.font_medium.render(line, True, self.BLACK)
                text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y))
                screen.blit(text, text_rect)
            y += 40

    def render_checklist(self, screen):
        """Render document checklist"""
        checklist_title = self.font_large.render("Required Documents", True, self.BLACK)
        title_rect = checklist_title.get_rect(center=(self.SCREEN_WIDTH // 2, 120))
        screen.blit(checklist_title, title_rect)

        instruction = self.font_medium.render("Click to check off documents you brought:", True, self.GRAY)
        inst_rect = instruction.get_rect(center=(self.SCREEN_WIDTH // 2, 160))
        screen.blit(instruction, inst_rect)

        documents = [
            "Photo ID (Driver's License or State ID)",
            "Previous Medi-Cal card",
            "Proof of income (Pay stubs, work letter)"
        ]

        for i, (doc, box) in enumerate(zip(documents, self.checklist_boxes)):
            # Checkbox
            color = self.GREEN if self.documents_checked[list(self.documents_checked.keys())[i]] else self.WHITE
            pygame.draw.rect(screen, color, box)
            pygame.draw.rect(screen, self.BLACK, box, 2)

            # Checkmark
            if self.documents_checked[list(self.documents_checked.keys())[i]]:
                pygame.draw.line(screen, self.BLACK,
                               (box.x + 5, box.y + 15), (box.x + 12, box.y + 22), 3)
                pygame.draw.line(screen, self.BLACK,
                               (box.x + 12, box.y + 22), (box.x + 25, box.y + 8), 3)

            # Document text
            doc_text = self.font_medium.render(doc, True, self.BLACK)
            screen.blit(doc_text, (box.x + 50, box.y + 5))

        # Progress message
        if all(self.documents_checked.values()):
            ready_text = self.font_large.render("Great! You have all required documents.", True, self.GREEN)
            ready_rect = ready_text.get_rect(center=(self.SCREEN_WIDTH // 2, 400))
            screen.blit(ready_text, ready_rect)

            continue_text = self.font_medium.render("Click anywhere to continue to application.", True, self.BLUE)
            cont_rect = continue_text.get_rect(center=(self.SCREEN_WIDTH // 2, 440))
            screen.blit(continue_text, cont_rect)

    def render_application(self, screen):
        """Render application form"""
        app_title = self.font_large.render("Former Foster Youth Medi-Cal Application", True, self.BLACK)
        title_rect = app_title.get_rect(center=(self.SCREEN_WIDTH // 2, 120))
        screen.blit(app_title, title_rect)

        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]

            # Question number
            q_num = self.font_medium.render(f"Question {self.current_question + 1} of {len(self.questions)}",
                                          True, self.GRAY)
            screen.blit(q_num, (350, 180))

            # Question text
            q_text = self.font_large.render(question["text"], True, self.BLACK)
            screen.blit(q_text, (350, 220))

            # Answer options
            for i, option in enumerate(question["options"]):
                option_rect = pygame.Rect(350, 300 + (i * 50), 400, 40)

                # Option background
                pygame.draw.rect(screen, self.WHITE, option_rect)
                pygame.draw.rect(screen, self.BLUE, option_rect, 2)

                # Option text
                opt_text = self.font_medium.render(f"{chr(65 + i)}. {option}", True, self.BLACK)
                screen.blit(opt_text, (option_rect.x + 10, option_rect.y + 10))

    def render_approval(self, screen):
        """Render approval message"""
        approval_text = [
            "Application Approved!",
            "",
            "Your Former Foster Youth Medi-Cal coverage",
            "has been approved instantly.",
            "",
            "However, coverage reinstatement will take",
            "approximately 2 weeks to process.",
            "",
            "Click anywhere to continue."
        ]

        y = 200
        for i, line in enumerate(approval_text):
            if line:
                color = self.GREEN if i == 0 else self.BLACK
                font = self.font_large if i == 0 else self.font_medium
                text = font.render(line, True, color)
                text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y))
                screen.blit(text, text_rect)
            y += 40

    def render_waiting(self, screen):
        """Render waiting period message"""
        waiting_text = [
            "Coverage Gap Period",
            "",
            "You now have a 2-week gap where you're approved",
            "but not yet covered for services.",
            "",
            "This is a common challenge for young adults",
            "transitioning between coverage types.",
            "",
            "You can now leave the clinic."
        ]

        y = 200
        for i, line in enumerate(waiting_text):
            if line:
                color = self.RED if i == 0 else self.BLACK
                font = self.font_large if i == 0 else self.font_medium
                text = font.render(line, True, color)
                text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y))
                screen.blit(text, text_rect)
            y += 35

    def add_interactive_object(self, name, obj_data):
        """Add an interactive object"""
        self.interactive_objects[name] = obj_data
        print(f"[CLINIC] Added interactive object: {name} at {obj_data.get('position')}")

    def check_interactions(self):
        """Check if player is near any interactive objects"""
        if not hasattr(self.game, 'player'):
            return None, None

        player_pos = (self.game.player.x, self.game.player.y)
        print(f"[CLINIC] Player position: {player_pos}")

        for name, obj in self.interactive_objects.items():
            if 'position' in obj:
                obj_pos = obj['position']
                distance = abs(player_pos[0] - obj_pos[0]) + abs(player_pos[1] - obj_pos[1])
                print(f"[CLINIC] Distance to {name}: {distance}")

                if distance <= 2:  # Within 2 tiles
                    return name, obj

        return None, None

    def interact_with_object(self, name):
        """Interact with an object"""
        print(f"[CLINIC] interact_with_object called with: {name}")

        if name in self.interactive_objects:
            obj = self.interactive_objects[name]
            print(f"[CLINIC] Object data: {obj}")
            trigger = obj.get('trigger_activity')
            print(f"[CLINIC] Trigger activity: {trigger}")

            if trigger == 'clinic_checklist':
                print("[CLINIC] Launching clinic document checklist")
                self.mini_game_manager.start_mini_game('clinic_checklist')
                return

        print(f"[CLINIC] No trigger found for: {name}")

    def draw(self, screen):
        """Draw the clinic interior with interaction indicators"""
        # Draw the base clinic interface
        self.render(screen)

        # DEBUG: Draw interaction hotspots with labels
        if hasattr(self, 'interactive_objects'):
            for name, obj in self.interactive_objects.items():
                if 'position' in obj:
                    pos = obj['position']
                    # Convert grid position to screen coordinates (assuming 32x32 tiles)
                    screen_x = pos[0] * 32
                    screen_y = pos[1] * 32

                    # Draw debug circle at interaction position
                    pygame.draw.circle(screen, (255, 0, 0), (screen_x + 16, screen_y + 16), 20, 3)

                    # Draw label
                    font = pygame.font.Font(None, 24)
                    text = font.render(f"E: {name}", True, (255, 255, 0))
                    screen.blit(text, (screen_x - 20, screen_y - 30))

                    print(f"[DEBUG] Interaction '{name}' at grid {pos} -> screen ({screen_x}, {screen_y})")