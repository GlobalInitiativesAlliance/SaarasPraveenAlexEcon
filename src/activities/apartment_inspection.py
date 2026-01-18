"""
Apartment Inspection Mini-Game for Part 2
Document all the problems in your crappy studio apartment
"""

import pygame
import math
import random
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class ApartmentInspection(Activity):
    """Visual apartment inspection to document problems"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None

        # Initialize fonts
        self.small_font = pygame.font.Font(None, 20)
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)

        # Tutorial state
        self.show_tutorial = True
        self.tutorial_step = 0
        self.tutorial_dismissed = False

        # Apartment layout
        self.apartment_layout = {
            'bedroom': pygame.Rect(50, 100, 400, 300),
            'kitchen': pygame.Rect(450, 100, 300, 300),
            'bathroom': pygame.Rect(750, 100, 224, 300),
            'living': pygame.Rect(50, 400, 924, 268)
        }

        # Inspection state
        self.problems_found = {
            'roaches': False,
            'mold': False,
            'heater': False,
            'windows': False,
            'walls': False,
            'plumbing': False
        }

        # Animation timers for problems
        self.animation_timers = {
            'roaches': 0,
            'mold': 0,
            'leak_drops': 0,
            'sound_waves': 0
        }

        # Roach positions for animation
        self.roach_positions = [
            [150, 400],
            [180, 420],
            [200, 410]
        ]

        self.evidence_photos = []
        self.inspection_complete = False

        # Camera state
        self.camera_active = False
        self.camera_flash_timer = 0
        self.photo_count = 0

        # Polaroid photos taken
        self.polaroid_photos = []
        self.photo_develop_timer = {}

        # Visual elements
        self.hover_problem = None
        self.info_text = ""
        self.completion_timer = 0

        # Problem locations and descriptions
        self.problem_spots = {
            'roaches': {
                'rect': pygame.Rect(150, 420, 120, 80),
                'name': 'Roach Infestation',
                'desc': 'Cockroaches scatter when you approach',
                'severity': 'SEVERE',
                'color': (139, 69, 19),
                'room': 'kitchen',
                'legal_note': 'Violates habitability standards'
            },
            'mold': {
                'rect': pygame.Rect(780, 150, 150, 100),
                'name': 'Black Mold',
                'desc': 'Toxic mold spreading on bathroom wall',
                'severity': 'HEALTH HAZARD',
                'color': (20, 20, 20),
                'room': 'bathroom',
                'legal_note': 'Health code violation - uninhabitable'
            },
            'heater': {
                'rect': pygame.Rect(100, 500, 100, 120),
                'name': 'Broken Heater',
                'desc': 'Hasn\'t worked in months, ice cold',
                'severity': 'CRITICAL',
                'color': (100, 100, 150),
                'room': 'living',
                'legal_note': 'Violates heating requirements'
            },
            'windows': {
                'rect': pygame.Rect(350, 120, 80, 150),
                'name': 'Broken Lock',
                'desc': 'Window lock broken - security risk',
                'severity': 'DANGEROUS',
                'color': (150, 150, 180),
                'room': 'bedroom',
                'legal_note': 'Security violation - unsafe premises'
            },
            'walls': {
                'rect': pygame.Rect(250, 200, 150, 150),
                'name': 'Paper Thin Walls',
                'desc': 'Can hear everything from neighbors',
                'severity': 'NO PRIVACY',
                'color': (200, 180, 160),
                'room': 'bedroom',
                'legal_note': 'Inadequate sound insulation'
            },
            'plumbing': {
                'rect': pygame.Rect(550, 250, 80, 80),
                'name': 'Leaking Pipes',
                'desc': 'Constant drip under sink',
                'severity': 'WATER DAMAGE',
                'color': (80, 100, 120),
                'room': 'kitchen',
                'legal_note': 'Plumbing code violation'
            }
        }

        # Load textures
        self.load_all_textures()

    def load_all_textures(self):
        """Load visual assets for apartment inspection"""

        # Room background (dirty apartment)
        self.room_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.room_bg.fill((180, 170, 160))  # Dingy beige

        # Draw room boundaries
        for room_name, room_rect in self.apartment_layout.items():
            # Different floor colors for each room
            if room_name == 'bedroom':
                color = (160, 150, 140)
            elif room_name == 'kitchen':
                color = (150, 145, 135)
            elif room_name == 'bathroom':
                color = (145, 150, 155)
            else:  # living
                color = (165, 155, 145)

            pygame.draw.rect(self.room_bg, color, room_rect)
            pygame.draw.rect(self.room_bg, (100, 90, 80), room_rect, 3)

        # Add floor pattern
        for y in range(0, SCREEN_HEIGHT, 32):
            for x in range(0, SCREEN_WIDTH, 32):
                if (x // 32 + y // 32) % 2 == 0:
                    tile_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                    pygame.draw.rect(tile_surf, (0, 0, 0, 20), (0, 0, 32, 32))
                    self.room_bg.blit(tile_surf, (x, y))

        # Add wall stains
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            radius = random.randint(10, 30)
            stain_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(stain_surf, (140, 130, 120, 50), (radius, radius), radius)
            self.room_bg.blit(stain_surf, (x - radius, y - radius))

        # Camera UI
        self.camera_frame = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Draw camera viewfinder corners
        corner_length = 50
        corner_color = (255, 255, 255)
        # Top-left
        pygame.draw.lines(self.camera_frame, corner_color, False,
                         [(100, 150), (100, 100), (150, 100)], 3)
        # Top-right
        pygame.draw.lines(self.camera_frame, corner_color, False,
                         [(SCREEN_WIDTH - 150, 100), (SCREEN_WIDTH - 100, 100),
                          (SCREEN_WIDTH - 100, 150)], 3)
        # Bottom-left
        pygame.draw.lines(self.camera_frame, corner_color, False,
                         [(100, SCREEN_HEIGHT - 150), (100, SCREEN_HEIGHT - 100),
                          (150, SCREEN_HEIGHT - 100)], 3)
        # Bottom-right
        pygame.draw.lines(self.camera_frame, corner_color, False,
                         [(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100),
                          (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
                          (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150)], 3)

        # Problem indicators (use actual sprites if available)
        try:
            # Try loading actual pest/damage sprites
            pest_path = "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter_Shadowless_Singles/16_Grocery_Store_Singles_Shadowless/"
            self.roach_sprite = self.load_sprite(pest_path + "Grocery_Store_Singles_Shadowless_1.png", (32, 32))
        except:
            # Fallback to colored circles
            self.roach_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.ellipse(self.roach_sprite, (80, 40, 20), (8, 8, 16, 24))

    def load_sprite(self, path, size):
        """Load and scale a sprite"""
        try:
            sprite = pygame.image.load(path)
            return pygame.transform.scale(sprite, size)
        except:
            # Return placeholder
            placeholder = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (200, 100, 100), placeholder.get_rect(), 2)
            return placeholder

    def start(self):
        """Start the inspection"""
        super().start()
        self.show_tutorial = True
        self.tutorial_step = 0
        self.info_text = "Welcome to apartment inspection - Press ENTER to begin"

    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            # Handle tutorial
            if self.show_tutorial and not self.tutorial_dismissed:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.tutorial_step += 1
                    if self.tutorial_step >= 3:
                        self.show_tutorial = False
                        self.tutorial_dismissed = True
                        self.info_text = "Look around and find problems to document"
                elif event.key == pygame.K_ESCAPE:
                    self.show_tutorial = False
                    self.tutorial_dismissed = True
                return

            if event.key == pygame.K_ESCAPE:
                if self.photo_count >= 4:  # Require minimum documentation
                    self.complete_inspection()
                else:
                    self.info_text = f"Document at least {4 - self.photo_count} more problems"

            elif event.key == pygame.K_SPACE:
                # Toggle camera mode
                self.camera_active = not self.camera_active
                if self.camera_active:
                    self.info_text = "Camera ready - Click on problems to photograph"
                else:
                    self.info_text = "Move around to inspect - SPACE for camera"

        elif event.type == pygame.MOUSEBUTTONDOWN and self.camera_active:
            # Take photo if clicking on a problem
            mouse_pos = pygame.mouse.get_pos()
            for problem_id, problem in self.problem_spots.items():
                if problem['rect'].collidepoint(mouse_pos) and not self.problems_found[problem_id]:
                    self.take_photo(problem_id)

    def take_photo(self, problem_id):
        """Photograph a problem"""
        self.problems_found[problem_id] = True
        self.photo_count += 1
        self.camera_flash_timer = 0.5

        problem = self.problem_spots[problem_id]

        # Create polaroid photo
        polaroid = {
            'id': problem_id,
            'rect': problem['rect'].copy(),
            'name': problem['name'],
            'severity': problem['severity'],
            'timestamp': pygame.time.get_ticks()
        }
        self.polaroid_photos.append(polaroid)
        self.photo_develop_timer[problem_id] = 2.0  # 2 seconds to develop

        self.evidence_photos.append({
            'id': problem_id,
            'name': problem['name'],
            'severity': problem['severity'],
            'legal_note': problem.get('legal_note', '')
        })

        self.info_text = f"📸 Documented: {problem['name']} - {problem['severity']}"

        # Check if we've found everything
        if self.photo_count >= len(self.problem_spots):
            self.info_text = "All problems documented! Press ESC to finish"

    def complete_inspection(self):
        """Complete the inspection"""
        self.inspection_complete = True
        self.completion_timer = 2.0

        # Calculate severity score
        severity_score = self.photo_count * 10

        # Pass results back to narrative
        if self.narrative_ref:
            self.narrative_ref.inspection_results = {
                'problems_found': self.photo_count,
                'evidence_photos': self.evidence_photos,
                'severity_score': severity_score
            }

    def update(self, dt):
        """Update inspection state"""
        # Update animation timers
        for key in self.animation_timers:
            self.animation_timers[key] += dt

        # Animate roaches
        if self.animation_timers['roaches'] > 0.1:
            self.animation_timers['roaches'] = 0
            for roach in self.roach_positions:
                roach[0] += random.randint(-5, 5)
                roach[1] += random.randint(-5, 5)
                # Keep within bounds
                roach[0] = max(150, min(270, roach[0]))
                roach[1] = max(400, min(480, roach[1]))

        # Update camera flash
        if self.camera_flash_timer > 0:
            self.camera_flash_timer -= dt

        # Update photo development timers
        for photo_id in list(self.photo_develop_timer.keys()):
            self.photo_develop_timer[photo_id] -= dt
            if self.photo_develop_timer[photo_id] <= 0:
                del self.photo_develop_timer[photo_id]

        # Update hover detection
        mouse_pos = pygame.mouse.get_pos()
        self.hover_problem = None
        for problem_id, problem in self.problem_spots.items():
            if problem['rect'].collidepoint(mouse_pos):
                self.hover_problem = problem_id
                break

        # Handle completion
        if self.completion_timer > 0:
            self.completion_timer -= dt
            if self.completion_timer <= 0:
                self.completed = True
                self.active = False

    def draw(self, screen):
        """Draw the inspection interface"""
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Draw apartment background
        screen.blit(self.room_bg, (0, 0))

        # Draw room labels
        self.draw_room_labels(screen)

        # Draw problem areas
        for problem_id, problem in self.problem_spots.items():
            # Draw problem indicator
            if self.problems_found[problem_id]:
                # Already photographed - show checkmark
                pygame.draw.rect(screen, (50, 200, 50), problem['rect'], 3)
                # Draw checkmark
                check_points = [
                    (problem['rect'].x + 20, problem['rect'].centery),
                    (problem['rect'].x + 40, problem['rect'].bottom - 20),
                    (problem['rect'].right - 20, problem['rect'].y + 20)
                ]
                pygame.draw.lines(screen, (50, 200, 50), False, check_points, 4)
            else:
                # Not yet documented
                color = problem['color']

                # Draw animated problems
                if problem_id == 'roaches':
                    # Draw animated roaches
                    for roach_pos in self.roach_positions:
                        pygame.draw.ellipse(screen, (60, 30, 10),
                                          pygame.Rect(roach_pos[0], roach_pos[1], 8, 5))
                        pygame.draw.ellipse(screen, (40, 20, 5),
                                          pygame.Rect(roach_pos[0]-2, roach_pos[1], 4, 3))
                elif problem_id == 'mold':
                    # Draw spreading mold
                    mold_alpha = int(100 + 50 * math.sin(self.animation_timers['mold']))
                    mold_surf = pygame.Surface((problem['rect'].width, problem['rect'].height), pygame.SRCALPHA)
                    for i in range(5):
                        x = random.randint(0, problem['rect'].width-20)
                        y = random.randint(0, problem['rect'].height-20)
                        pygame.draw.circle(mold_surf, (20, 30, 20, mold_alpha), (x, y), 15)
                    screen.blit(mold_surf, problem['rect'])
                elif problem_id == 'plumbing':
                    # Draw water drops
                    drop_y = int(problem['rect'].y + 20 * math.sin(self.animation_timers['leak_drops'] * 3))
                    pygame.draw.circle(screen, (100, 150, 200),
                                     (problem['rect'].centerx, drop_y), 3)
                elif problem_id == 'walls':
                    # Draw sound waves
                    if int(self.animation_timers['sound_waves']) % 2 == 0:
                        wave_surf = pygame.Surface((problem['rect'].width, problem['rect'].height), pygame.SRCALPHA)
                        for i in range(3):
                            radius = 10 + i * 15
                            alpha = max(0, 100 - i * 30)
                            pygame.draw.circle(wave_surf, (200, 180, 160, alpha),
                                             (problem['rect'].width//2, problem['rect'].height//2),
                                             radius, 2)
                        screen.blit(wave_surf, problem['rect'])
                else:
                    # Default problem indicator
                    problem_surf = pygame.Surface((problem['rect'].width, problem['rect'].height), pygame.SRCALPHA)
                    pygame.draw.rect(problem_surf, (*color, 100), problem_surf.get_rect())
                    screen.blit(problem_surf, problem['rect'])

                if problem_id == self.hover_problem:
                    # Highlight on hover
                    pygame.draw.rect(screen, (255, 200, 100), problem['rect'], 3)
                    # Show problem details
                    self.draw_problem_tooltip(screen, problem, mouse_pos)

        # Draw camera UI if active
        if self.camera_active:
            screen.blit(self.camera_frame, (0, 0))

            # Draw camera info
            cam_text = self.font.render(f"CAMERA MODE - {self.photo_count} photos taken", True, (255, 255, 255))
            pygame.draw.rect(screen, (0, 0, 0), (SCREEN_WIDTH//2 - 150, 50, 300, 40))
            screen.blit(cam_text, (SCREEN_WIDTH//2 - cam_text.get_width()//2, 60))

        # Draw camera flash
        if self.camera_flash_timer > 0:
            flash_alpha = int(255 * (self.camera_flash_timer / 0.5))
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(flash_alpha)
            screen.blit(flash_surf, (0, 0))

        # Draw evidence counter
        evidence_bg = pygame.Rect(20, 20, 250, 100)
        pygame.draw.rect(screen, (40, 40, 50), evidence_bg)
        pygame.draw.rect(screen, (200, 200, 200), evidence_bg, 2)

        title = self.font.render("EVIDENCE COLLECTED", True, (255, 255, 255))
        screen.blit(title, (30, 30))

        count_text = self.large_font.render(f"{self.photo_count}/{len(self.problem_spots)}", True, (255, 200, 100))
        screen.blit(count_text, (30, 60))

        # Draw instructions
        instruction_bg = pygame.Rect(20, SCREEN_HEIGHT - 80, 400, 60)
        pygame.draw.rect(screen, (40, 40, 50), instruction_bg)
        pygame.draw.rect(screen, (200, 200, 200), instruction_bg, 2)

        instructions = [
            "SPACE - Toggle camera",
            "CLICK - Take photo (in camera mode)",
            "ESC - Finish inspection (need 4+ photos)"
        ]
        y_offset = SCREEN_HEIGHT - 70
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (200, 200, 200))
            screen.blit(inst_text, (30, y_offset))
            y_offset += 18

        # Draw info text
        if self.info_text:
            info_surf = self.font.render(self.info_text, True, (255, 255, 200))
            info_bg = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400, 30)
            pygame.draw.rect(screen, (40, 40, 50), info_bg)
            screen.blit(info_surf, (SCREEN_WIDTH//2 - info_surf.get_width()//2, SCREEN_HEIGHT - 35))

        # Draw polaroid photos on the side (evidence board)
        self.draw_evidence_board(screen)

        # Draw completion message
        if self.inspection_complete:
            self.draw_completion_summary(screen)

        # Draw tutorial overlay if active
        if self.show_tutorial and not self.tutorial_dismissed:
            self.draw_tutorial(screen)

    def draw_problem_tooltip(self, screen, problem, mouse_pos):
        """Draw tooltip for problem on hover"""
        tooltip_width = 300
        tooltip_height = 80

        # Position tooltip near mouse but keep on screen
        tooltip_x = min(mouse_pos[0] + 20, SCREEN_WIDTH - tooltip_width - 20)
        tooltip_y = min(mouse_pos[1] - tooltip_height - 10, SCREEN_HEIGHT - tooltip_height - 20)

        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(screen, (20, 20, 30), tooltip_rect)
        pygame.draw.rect(screen, (255, 200, 100), tooltip_rect, 2)

        # Draw problem info
        name_text = self.font.render(problem['name'], True, (255, 255, 255))
        screen.blit(name_text, (tooltip_x + 10, tooltip_y + 10))

        desc_text = self.small_font.render(problem['desc'], True, (200, 200, 200))
        screen.blit(desc_text, (tooltip_x + 10, tooltip_y + 35))

        severity_text = self.font.render(problem['severity'], True, (255, 100, 100))
        screen.blit(severity_text, (tooltip_x + 10, tooltip_y + 55))

    def draw_completion_summary(self, screen):
        """Draw inspection summary"""
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Draw summary box
        summary_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 200, 600, 400)
        pygame.draw.rect(screen, (30, 30, 40), summary_rect)
        pygame.draw.rect(screen, (255, 200, 100), summary_rect, 3)

        # Title
        title = self.large_font.render("INSPECTION COMPLETE", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 180))

        # Problems documented
        y_offset = SCREEN_HEIGHT//2 - 120
        for photo in self.evidence_photos:
            problem_text = self.font.render(f"✓ {photo['name']}: {photo['severity']}", True, (200, 255, 200))
            screen.blit(problem_text, (SCREEN_WIDTH//2 - 250, y_offset))
            y_offset += 30

        # Summary
        summary_text = self.font.render(f"Total violations documented: {self.photo_count}", True, (255, 255, 200))
        screen.blit(summary_text, (SCREEN_WIDTH//2 - summary_text.get_width()//2, y_offset + 20))

        advice = self.small_font.render("This evidence will be crucial for your tenant rights case", True, (200, 200, 200))
        screen.blit(advice, (SCREEN_WIDTH//2 - advice.get_width()//2, y_offset + 50))

    def draw_room_labels(self, screen):
        """Draw room labels on the apartment layout"""
        room_labels = {
            'bedroom': 'BEDROOM',
            'kitchen': 'KITCHEN',
            'bathroom': 'BATHROOM',
            'living': 'LIVING ROOM'
        }

        for room_name, label in room_labels.items():
            room_rect = self.apartment_layout[room_name]
            label_surf = self.small_font.render(label, True, (80, 80, 80))
            label_x = room_rect.centerx - label_surf.get_width() // 2
            label_y = room_rect.y + 10
            screen.blit(label_surf, (label_x, label_y))

    def draw_tutorial(self, screen):
        """Draw tutorial overlay"""
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Tutorial box
        tutorial_rect = pygame.Rect(SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT//2 - 200, 800, 400)
        pygame.draw.rect(screen, (30, 30, 40), tutorial_rect)
        pygame.draw.rect(screen, (100, 200, 255), tutorial_rect, 3)

        # Title
        title = self.title_font.render("APARTMENT INSPECTION TUTORIAL", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 180))

        # Tutorial steps
        steps = [
            [
                "Step 1: EXPLORE THE APARTMENT",
                "Move your mouse around to find problems.",
                "Look for: Roaches 🪳, Mold 🦴, Broken items 🔨"
            ],
            [
                "Step 2: ACTIVATE CAMERA MODE",
                "Press SPACE to enter camera mode.",
                "The viewfinder will appear on screen."
            ],
            [
                "Step 3: DOCUMENT PROBLEMS",
                "Click on problems to photograph them.",
                "Collect at least 4 pieces of evidence!",
                "Each photo proves a violation of tenant rights."
            ]
        ]

        if self.tutorial_step < len(steps):
            step_info = steps[self.tutorial_step]
            y_offset = SCREEN_HEIGHT//2 - 80

            # Step title
            step_title = self.large_font.render(step_info[0], True, (100, 200, 255))
            screen.blit(step_title, (SCREEN_WIDTH//2 - step_title.get_width()//2, y_offset))

            # Step details
            y_offset += 60
            for line in step_info[1:]:
                line_surf = self.font.render(line, True, (200, 200, 200))
                screen.blit(line_surf, (SCREEN_WIDTH//2 - line_surf.get_width()//2, y_offset))
                y_offset += 35

        # Continue prompt
        if self.tutorial_step < 3:
            prompt = "Press ENTER to continue" if self.tutorial_step < 2 else "Press ENTER to start inspecting"
        else:
            prompt = "Starting inspection..."

        prompt_surf = self.font.render(prompt, True, (255, 200, 100))
        screen.blit(prompt_surf, (SCREEN_WIDTH//2 - prompt_surf.get_width()//2, SCREEN_HEIGHT//2 + 150))

        # Skip option
        skip_surf = self.small_font.render("Press ESC to skip tutorial", True, (150, 150, 150))
        screen.blit(skip_surf, (SCREEN_WIDTH//2 - skip_surf.get_width()//2, SCREEN_HEIGHT//2 + 180))

    def draw_evidence_board(self, screen):
        """Draw collected polaroid photos as an evidence board"""
        if not self.polaroid_photos:
            return

        # Evidence board background
        board_rect = pygame.Rect(SCREEN_WIDTH - 200, 100, 180, 400)
        pygame.draw.rect(screen, (60, 50, 40), board_rect)
        pygame.draw.rect(screen, (40, 30, 20), board_rect, 3)

        # Title
        title = self.small_font.render("EVIDENCE", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH - 190 + (160 - title.get_width())//2, 110))

        # Draw polaroid photos
        y_offset = 140
        for i, photo in enumerate(self.polaroid_photos[:5]):  # Show max 5 photos
            # Polaroid frame
            polaroid_rect = pygame.Rect(SCREEN_WIDTH - 180, y_offset, 140, 60)
            pygame.draw.rect(screen, (240, 240, 230), polaroid_rect)
            pygame.draw.rect(screen, (200, 200, 190), polaroid_rect, 2)

            # Photo content (simplified representation of the problem)
            content_rect = pygame.Rect(polaroid_rect.x + 10, polaroid_rect.y + 5, 120, 35)

            # Check if photo is still developing
            if photo['id'] in self.photo_develop_timer:
                alpha = int(255 * (1 - self.photo_develop_timer[photo['id']] / 2.0))
                photo_surf = pygame.Surface((120, 35))
                photo_surf.fill(self.problem_spots[photo['id']]['color'])
                photo_surf.set_alpha(alpha)
                screen.blit(photo_surf, content_rect)
            else:
                pygame.draw.rect(screen, self.problem_spots[photo['id']]['color'], content_rect)

            # Problem name on polaroid
            name = self.problem_spots[photo['id']]['name'][:12]  # Truncate if too long
            name_surf = self.small_font.render(name, True, (50, 50, 50))
            screen.blit(name_surf, (polaroid_rect.x + 10, polaroid_rect.y + 42))

            y_offset += 70