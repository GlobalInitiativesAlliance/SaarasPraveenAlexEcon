"""
Legal Document Sorting Mini-Game for Part 3 - Legal System
Production-ready version with error handling, animations, and visual feedback
"""
import pygame
import random
import math


class LegalDocumentSortingGame:
    """Sort legal documents into correct categories with time pressure"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer with visual urgency
        self.time_limit = 60.0
        self.time_remaining = self.time_limit

        # Document definitions with clear categories
        self.documents = [
            # Legal documents (left bin) - blue tint
            {'name': 'Court Summons', 'type': 'legal', 'color': (200, 200, 255), 'is_critical': True},
            {'name': 'Traffic Citation', 'type': 'legal', 'color': (200, 200, 255), 'is_critical': False},
            {'name': 'Warrant Notice', 'type': 'legal', 'color': (200, 200, 255), 'is_critical': False},
            {'name': 'Bail Conditions', 'type': 'legal', 'color': (200, 200, 255), 'is_critical': False},
            {'name': 'Appeal Form', 'type': 'legal', 'color': (200, 200, 255), 'is_critical': False},

            # Personal records (right bin) - orange tint
            {'name': 'Birth Certificate', 'type': 'personal', 'color': (255, 220, 200), 'is_critical': False},
            {'name': 'Social Security', 'type': 'personal', 'color': (255, 220, 200), 'is_critical': False},
            {'name': 'Foster Care ID', 'type': 'personal', 'color': (255, 220, 200), 'is_critical': False},
            {'name': 'School Records', 'type': 'personal', 'color': (255, 220, 200), 'is_critical': False},
            {'name': 'Medical History', 'type': 'personal', 'color': (255, 220, 200), 'is_critical': False},
        ]

        # Sorting zones
        self.legal_zone = pygame.Rect(100, 480, 250, 180)
        self.personal_zone = pygame.Rect(930, 480, 250, 180)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)
        self.hover_zone = None

        # Scoring
        self.correctly_sorted = 0
        self.incorrectly_sorted = 0
        self.total_documents = len(self.documents)

        # Animation state
        self.animation_timer = 0
        self.shake_timer = 0
        self.pulse_timer = 0
        self.success_particles = []

        # Instructions display
        self.show_instructions = True
        self.instruction_timer = 0

        # Results tracking
        self.found_critical_document = False

        # Error handling
        self._initialized = False

        # Narrative reference (set by interior)
        self.narrative_ref = None

        # Initialize documents
        self._initialize_documents()

    def _initialize_documents(self):
        """Initialize document positions and state"""
        try:
            random.shuffle(self.documents)

            for i, doc in enumerate(self.documents):
                col = i % 5
                row = i // 5

                base_x = 280 + col * 150
                base_y = 120 + row * 140
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-10, 10)

                doc['rect'] = pygame.Rect(base_x + offset_x, base_y + offset_y, 130, 90)
                doc['original_pos'] = (doc['rect'].x, doc['rect'].y)
                doc['placed'] = False
                doc['placed_in'] = None

            self._initialized = True

        except Exception as e:
            print(f"[DOC_SORT] Error initializing documents: {e}")
            self._initialized = False

    def start(self):
        """Start the activity"""
        if not self._initialized:
            self._initialize_documents()

        self.active = True
        self.completed = False
        self.show_instructions = True
        self.instruction_timer = pygame.time.get_ticks()
        self.time_remaining = self.time_limit
        self.correctly_sorted = 0
        self.incorrectly_sorted = 0
        self.found_critical_document = False
        self.success_particles = []

        # Reset documents
        for doc in self.documents:
            doc['placed'] = False
            doc['placed_in'] = None
            if 'original_pos' in doc:
                doc['rect'].x = doc['original_pos'][0]
                doc['rect'].y = doc['original_pos'][1]

        print("[DOC_SORT] Activity started")

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        # Hide instructions after 4 seconds
        if self.show_instructions:
            if pygame.time.get_ticks() - self.instruction_timer > 4000:
                self.show_instructions = False

        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self._complete_activity()
            return

        # Update animations
        self.animation_timer += dt
        self.pulse_timer += dt

        if self.shake_timer > 0:
            self.shake_timer -= dt

        # Update particles
        self._update_particles(dt)

        # Check completion
        unsorted = sum(1 for d in self.documents if not d['placed'])
        if unsorted == 0:
            self._complete_activity()

    def _complete_activity(self):
        """Complete the activity"""
        self.completed = True
        self.active = False
        print(f"[DOC_SORT] Activity completed - Correct: {self.correctly_sorted}, Errors: {self.incorrectly_sorted}")

    def _update_particles(self, dt):
        """Update success particles"""
        for particle in self.success_particles[:]:
            particle['life'] -= dt
            particle['y'] -= particle['speed'] * dt
            particle['x'] += particle['drift'] * dt
            if particle['life'] <= 0:
                self.success_particles.remove(particle)

    def _spawn_success_particles(self, x, y):
        """Spawn success particles at position"""
        for _ in range(5):
            self.success_particles.append({
                'x': x + random.randint(-20, 20),
                'y': y,
                'speed': random.randint(50, 100),
                'drift': random.randint(-30, 30),
                'life': 1.0,
                'color': (100, 200, 100)
            })

    def handle_event(self, event):
        """Handle pygame events"""
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_release(event.pos, event.button)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)

    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False

    def handle_mouse_click(self, pos, button=1):
        """Start dragging a document"""
        if button != 1 or not self.active:
            return

        # Check documents in reverse order (top first)
        for doc in reversed(self.documents):
            if not doc['placed'] and doc['rect'].collidepoint(pos):
                self.dragging = doc
                self.drag_offset = (
                    doc['rect'].x - pos[0],
                    doc['rect'].y - pos[1]
                )
                # Bring to front
                self.documents.remove(doc)
                self.documents.append(doc)
                break

    def handle_mouse_release(self, pos, button=1):
        """Drop document and check placement"""
        if not self.dragging or not self.active:
            return

        dropped_correctly = False

        # Check legal zone
        if self.legal_zone.collidepoint(pos):
            if self.dragging['type'] == 'legal':
                self.dragging['placed'] = True
                self.dragging['placed_in'] = 'legal'
                self.correctly_sorted += 1
                dropped_correctly = True
                self._place_in_zone(self.dragging, self.legal_zone, 'legal')
                self._spawn_success_particles(pos[0], pos[1])

                # Check for critical document
                if self.dragging.get('is_critical'):
                    self.found_critical_document = True
                    print("[DOC_SORT] Critical document (Court Summons) found!")
            else:
                self.incorrectly_sorted += 1
                self.shake_timer = 0.3
                self._bounce_back(self.dragging)

        # Check personal zone
        elif self.personal_zone.collidepoint(pos):
            if self.dragging['type'] == 'personal':
                self.dragging['placed'] = True
                self.dragging['placed_in'] = 'personal'
                self.correctly_sorted += 1
                dropped_correctly = True
                self._place_in_zone(self.dragging, self.personal_zone, 'personal')
                self._spawn_success_particles(pos[0], pos[1])
            else:
                self.incorrectly_sorted += 1
                self.shake_timer = 0.3
                self._bounce_back(self.dragging)

        else:
            # Dropped outside zones
            self._bounce_back(self.dragging)

        self.dragging = None
        self.hover_zone = None

    def handle_mouse_motion(self, pos):
        """Move dragged document"""
        if self.dragging:
            self.dragging['rect'].x = pos[0] + self.drag_offset[0]
            self.dragging['rect'].y = pos[1] + self.drag_offset[1]

            # Track hover zone
            if self.legal_zone.collidepoint(pos):
                self.hover_zone = 'legal'
            elif self.personal_zone.collidepoint(pos):
                self.hover_zone = 'personal'
            else:
                self.hover_zone = None

    def _place_in_zone(self, doc, zone, zone_name):
        """Place document in zone"""
        placed_count = sum(1 for d in self.documents
                         if d['placed'] and d.get('placed_in') == zone_name)
        doc['rect'].x = zone.x + 20 + (placed_count % 3) * 40
        doc['rect'].y = zone.y + 30 + (placed_count // 3) * 30

    def _bounce_back(self, doc):
        """Bounce document back to original position"""
        if 'original_pos' in doc:
            doc['rect'].x = doc['original_pos'][0]
            doc['rect'].y = doc['original_pos'][1]

    def draw(self, screen):
        """Draw the document sorting interface"""
        if not self.active and not self.completed:
            return

        # Background
        screen.fill((220, 220, 215))

        # Draw desk surface
        desk_rect = pygame.Rect(50, 400, self.SCREEN_WIDTH - 100, 280)
        pygame.draw.rect(screen, (139, 90, 43), desk_rect)
        pygame.draw.rect(screen, (100, 60, 30), desk_rect, 3)

        # Draw zones
        self._draw_zone(screen, self.legal_zone, "LEGAL", (180, 180, 240),
                       self.hover_zone == 'legal')
        self._draw_zone(screen, self.personal_zone, "PERSONAL", (240, 200, 180),
                       self.hover_zone == 'personal')

        # Draw unsorted documents
        for doc in self.documents:
            if not doc['placed']:
                self._draw_document(screen, doc)

        # Draw particles
        self._draw_particles(screen)

        # Draw instructions overlay
        if self.show_instructions:
            self._draw_instructions(screen)

        # Draw timer
        self._draw_timer(screen)

        # Draw progress
        self._draw_progress(screen)

        # Draw error feedback
        if self.shake_timer > 0:
            self._draw_error_feedback(screen)

        # Draw ESC hint
        font = pygame.font.Font(None, 24)
        hint = font.render("Press ESC to exit", True, (120, 120, 120))
        screen.blit(hint, (20, self.SCREEN_HEIGHT - 30))

    def _draw_zone(self, screen, zone, label, color, is_hovered):
        """Draw a sorting zone"""
        # Pulse effect when hovered
        if is_hovered:
            pulse = abs(math.sin(self.pulse_timer * 4)) * 20
            expanded = zone.inflate(pulse, pulse)
            s = pygame.Surface((expanded.width, expanded.height), pygame.SRCALPHA)
            s.fill((255, 255, 200, 100))
            screen.blit(s, expanded.topleft)

        # Zone background
        zone_color = tuple(min(255, c + 30) for c in color) if is_hovered else color
        pygame.draw.rect(screen, zone_color, zone)
        pygame.draw.rect(screen, (80, 80, 80), zone, 3)

        # Label
        font = pygame.font.Font(None, 36)
        text = font.render(label, True, (60, 60, 60))
        text_rect = text.get_rect(center=(zone.centerx, zone.y + 25))
        screen.blit(text, text_rect)

        # Count
        zone_key = 'legal' if label == 'LEGAL' else 'personal'
        placed = sum(1 for d in self.documents if d['placed'] and d.get('placed_in') == zone_key)
        count_font = pygame.font.Font(None, 28)
        count_text = count_font.render(f"{placed}/5", True, (100, 100, 100))
        count_rect = count_text.get_rect(center=(zone.centerx, zone.bottom - 25))
        screen.blit(count_text, count_rect)

    def _draw_document(self, screen, doc):
        """Draw a document card"""
        rect = doc['rect']

        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (80, 80, 80), shadow_rect)

        # Document card
        color = doc['color']
        if self.dragging == doc:
            color = tuple(min(255, c + 40) for c in color)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 2)

        # Type indicator stripe
        indicator_color = (100, 100, 200) if doc['type'] == 'legal' else (200, 150, 100)
        pygame.draw.rect(screen, indicator_color, (rect.x, rect.y, rect.width, 5))

        # Critical document highlight
        if doc.get('is_critical'):
            pygame.draw.rect(screen, (255, 200, 0), rect, 3)

        # Document name
        font = pygame.font.Font(None, 22)
        name = doc['name']
        words = name.split()

        if len(words) > 1:
            line1 = words[0]
            line2 = ' '.join(words[1:])
            text1 = font.render(line1, True, (40, 40, 40))
            text2 = font.render(line2, True, (40, 40, 40))
            screen.blit(text1, (rect.x + 10, rect.y + 25))
            screen.blit(text2, (rect.x + 10, rect.y + 50))
        else:
            text = font.render(name, True, (40, 40, 40))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def _draw_particles(self, screen):
        """Draw success particles"""
        for particle in self.success_particles:
            alpha = int(255 * particle['life'])
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*particle['color'], alpha), (3, 3), 3)
            screen.blit(s, (int(particle['x']), int(particle['y'])))

    def _draw_timer(self, screen):
        """Draw timer"""
        if self.time_remaining > 30:
            color = (80, 150, 80)
        elif self.time_remaining > 15:
            color = (200, 150, 50)
        else:
            color = (200, 80, 80)
            if int(self.time_remaining * 2) % 2 == 0:
                color = (255, 100, 100)

        font = pygame.font.Font(None, 48)
        timer_text = font.render(f"Time: {int(self.time_remaining)}s", True, color)
        timer_rect = timer_text.get_rect(topright=(self.SCREEN_WIDTH - 30, 20))

        bg_rect = timer_rect.inflate(20, 10)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        pygame.draw.rect(screen, color, bg_rect, 2)
        screen.blit(timer_text, timer_rect)

    def _draw_progress(self, screen):
        """Draw sorting progress"""
        font = pygame.font.Font(None, 32)
        text = font.render(f"Sorted: {self.correctly_sorted}/{self.total_documents}", True, (60, 60, 60))
        screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, 20))

        if self.incorrectly_sorted > 0:
            error_text = font.render(f"Errors: {self.incorrectly_sorted}", True, (180, 80, 80))
            screen.blit(error_text, (self.SCREEN_WIDTH // 2 - error_text.get_width() // 2, 55))

    def _draw_instructions(self, screen):
        """Draw instruction overlay"""
        overlay = pygame.Surface((800, 120), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        overlay_rect = overlay.get_rect(center=(self.SCREEN_WIDTH // 2, 90))
        screen.blit(overlay, overlay_rect)

        font = pygame.font.Font(None, 36)
        text1 = font.render("Sort documents by dragging them to the correct zone", True, (255, 255, 255))
        text2 = font.render("LEGAL (blue) = Court documents  |  PERSONAL (orange) = ID/Records", True, (200, 200, 200))

        screen.blit(text1, (self.SCREEN_WIDTH // 2 - text1.get_width() // 2, 60))
        screen.blit(text2, (self.SCREEN_WIDTH // 2 - text2.get_width() // 2, 100))

    def _draw_error_feedback(self, screen):
        """Draw error shake effect"""
        flash_alpha = int(255 * (self.shake_timer / 0.3))
        flash_surf = pygame.Surface((self.SCREEN_WIDTH, 10), pygame.SRCALPHA)
        flash_surf.fill((255, 0, 0, flash_alpha))
        screen.blit(flash_surf, (0, 0))
        screen.blit(flash_surf, (0, self.SCREEN_HEIGHT - 10))

    def get_results(self):
        """Return results of the activity"""
        return {
            'completed': self.completed,
            'correctly_sorted': self.correctly_sorted,
            'incorrectly_sorted': self.incorrectly_sorted,
            'time_remaining': self.time_remaining,
            'found_critical_document': self.found_critical_document,
            'message': f"Sorted {self.correctly_sorted}/{self.total_documents} documents correctly",
            'stress': 5 if self.incorrectly_sorted > 2 else -5
        }
