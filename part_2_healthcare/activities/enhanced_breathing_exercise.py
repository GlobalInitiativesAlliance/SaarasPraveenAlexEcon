"""
Enhanced Breathing Exercise Mini-Game with High-Quality Graphics
Beautiful animated breathing visualization with calming colors and sound-reactive elements
"""
import pygame
import math
import random

class EnhancedBreathingExercise:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Breathing timing (in seconds)
        self.inhale_duration = 4.0
        self.exhale_duration = 6.0
        self.total_cycle_duration = self.inhale_duration + self.exhale_duration

        # Game state
        self.breathing_cycle_time = 0
        self.is_inhaling = True
        self.cycles_completed = 0
        self.required_cycles = 5
        self.player_input_timing = []
        self.timing_accuracy = 1.0
        self.current_phase = "prepare"  # prepare, breathing, complete

        # Animation state
        self.time = 0
        self.circle_radius = 80
        self.target_radius = 80
        self.pulse_intensity = 0

        # Visual elements
        self.center_x = self.SCREEN_WIDTH // 2
        self.center_y = self.SCREEN_HEIGHT // 2

        # Particle system for ambient effects
        self.particles = []
        self.energy_particles = []

        # Color schemes for different phases
        self.colors = {
            'inhale': {
                'primary': (100, 180, 255),      # Light blue
                'secondary': (150, 220, 255),    # Lighter blue
                'accent': (200, 240, 255),       # Very light blue
                'glow': (80, 150, 255)           # Glow blue
            },
            'exhale': {
                'primary': (255, 150, 100),      # Warm orange
                'secondary': (255, 200, 150),    # Light orange
                'accent': (255, 230, 200),       # Very light orange
                'glow': (255, 120, 80)           # Glow orange
            },
            'neutral': {
                'primary': (150, 255, 150),      # Soft green
                'secondary': (200, 255, 200),    # Light green
                'accent': (230, 255, 230),       # Very light green
                'glow': (120, 255, 120)          # Glow green
            }
        }

        # Fonts with elegant typography
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'large': pygame.font.Font(None, 48),
            'medium': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 28)
        }

        # Sound wave visualization
        self.sound_waves = []

        # Performance tracking
        self.breath_quality_scores = []
        self.current_breath_score = 100

        # Guided text animations
        self.text_fade = 0
        self.current_instruction = ""

        # Background elements
        self.floating_elements = []
        self.initialize_floating_elements()

    def initialize_floating_elements(self):
        """Initialize floating background elements"""
        for _ in range(20):
            element = {
                'x': random.uniform(0, self.SCREEN_WIDTH),
                'y': random.uniform(0, self.SCREEN_HEIGHT),
                'size': random.uniform(2, 8),
                'speed': random.uniform(0.5, 2),
                'phase': random.uniform(0, math.pi * 2),
                'opacity': random.uniform(30, 80)
            }
            self.floating_elements.append(element)

    def create_particle(self, x, y, color, velocity=(0, 0), life=2.0):
        """Create an ambient particle"""
        return {
            'x': x,
            'y': y,
            'vx': velocity[0],
            'vy': velocity[1],
            'color': color,
            'life': life,
            'max_life': life,
            'size': random.uniform(1, 4)
        }

    def update_particles(self, dt):
        """Update particle animations"""
        # Update ambient particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            particle['life'] -= dt

            if particle['life'] <= 0:
                self.particles.remove(particle)

        # Update energy particles
        for particle in self.energy_particles[:]:
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            particle['life'] -= dt

            # Fade based on life
            particle['opacity'] = int(255 * (particle['life'] / particle['max_life']))

            if particle['life'] <= 0:
                self.energy_particles.remove(particle)

    def get_current_colors(self):
        """Get colors based on breathing phase"""
        if self.current_phase == "prepare":
            return self.colors['neutral']
        elif self.is_inhaling:
            return self.colors['inhale']
        else:
            return self.colors['exhale']

    def draw_breathing_circle(self, surface):
        """Draw the main breathing visualization circle"""
        colors = self.get_current_colors()

        # Calculate breathing progress
        progress = self.breathing_cycle_time / (self.inhale_duration if self.is_inhaling else self.exhale_duration)
        progress = max(0, min(1, progress))

        # Smooth easing for natural breathing feel
        if self.is_inhaling:
            eased_progress = 1 - math.cos(progress * math.pi / 2)  # Ease in
            self.target_radius = 80 + (120 * eased_progress)
        else:
            eased_progress = math.sin(progress * math.pi / 2)  # Ease out
            self.target_radius = 200 - (120 * eased_progress)

        # Smooth radius transition
        self.circle_radius += (self.target_radius - self.circle_radius) * 0.1

        # Draw multiple concentric circles for depth
        for i in range(5):
            radius = self.circle_radius - (i * 15)
            if radius <= 0:
                continue

            # Calculate opacity based on layer
            opacity = max(50, 255 - (i * 40))

            # Create color with opacity
            color = (*colors['primary'], opacity)

            # Draw glow effect
            glow_radius = radius + 20
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)

            # Create gradient glow
            for r in range(int(glow_radius), int(radius), -2):
                alpha = int(30 * (glow_radius - r) / (glow_radius - radius))
                glow_color = (*colors['glow'], alpha)
                pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), r)

            # Blit glow
            glow_rect = glow_surface.get_rect(center=(self.center_x, self.center_y))
            surface.blit(glow_surface, glow_rect)

            # Main circle
            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, color, (radius, radius), radius)

            circle_rect = circle_surface.get_rect(center=(self.center_x, self.center_y))
            surface.blit(circle_surface, circle_rect)

    def draw_breathing_guide(self, surface):
        """Draw breathing guide with animated text"""
        colors = self.get_current_colors()

        # Determine current instruction
        if self.current_phase == "prepare":
            self.current_instruction = "Get comfortable and prepare to breathe"
        elif self.is_inhaling:
            self.current_instruction = "Breathe In Slowly..."
        else:
            self.current_instruction = "Breathe Out Gently..."

        # Animated text fade
        self.text_fade = math.sin(self.time * 2) * 0.3 + 0.7

        # Main instruction text
        text_color = (*colors['primary'], int(255 * self.text_fade))
        instruction_surface = self.fonts['large'].render(self.current_instruction, True, colors['primary'])

        # Text shadow
        shadow_surface = self.fonts['large'].render(self.current_instruction, True, (50, 50, 50))

        text_x = self.center_x - instruction_surface.get_width() // 2
        text_y = self.center_y + 180

        surface.blit(shadow_surface, (text_x + 2, text_y + 2))
        surface.blit(instruction_surface, (text_x, text_y))

        # Progress indicator
        if self.current_phase == "breathing":
            progress_text = f"Cycle {self.cycles_completed + 1} of {self.required_cycles}"
            progress_surface = self.fonts['medium'].render(progress_text, True, colors['secondary'])
            progress_x = self.center_x - progress_surface.get_width() // 2
            surface.blit(progress_surface, (progress_x, text_y + 50))

            # Timing bar
            bar_width = 300
            bar_height = 8
            bar_x = self.center_x - bar_width // 2
            bar_y = text_y + 90

            # Background bar
            pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

            # Progress bar
            total_progress = (self.breathing_cycle_time /
                            (self.inhale_duration if self.is_inhaling else self.exhale_duration))
            progress_width = int(bar_width * min(1, total_progress))

            progress_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height)
            pygame.draw.rect(surface, colors['primary'], progress_rect, border_radius=4)

    def draw_floating_particles(self, surface):
        """Draw ambient floating particles"""
        colors = self.get_current_colors()

        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 2.0))
            color = (*colors['accent'], alpha)

            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color,
                             (particle['size'], particle['size']), particle['size'])

            surface.blit(particle_surface, (int(particle['x'] - particle['size']),
                                          int(particle['y'] - particle['size'])))

    def draw_energy_waves(self, surface):
        """Draw energy waves emanating from the center"""
        colors = self.get_current_colors()

        # Create expanding rings
        for i in range(3):
            ring_time = (self.time + i * 2) % 6  # Stagger rings
            ring_progress = ring_time / 6

            ring_radius = ring_progress * 300
            ring_opacity = int(100 * (1 - ring_progress))

            if ring_opacity > 10:
                ring_color = (*colors['glow'], ring_opacity)

                # Create ring surface
                ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(ring_surface, ring_color,
                                 (ring_radius, ring_radius), ring_radius, width=3)

                ring_rect = ring_surface.get_rect(center=(self.center_x, self.center_y))
                surface.blit(ring_surface, ring_rect)

    def draw_background_elements(self, surface):
        """Draw subtle background elements"""
        colors = self.get_current_colors()

        for element in self.floating_elements:
            # Update position
            element['y'] -= element['speed'] * 0.5
            element['x'] += math.sin(self.time + element['phase']) * 0.5

            # Reset if off screen
            if element['y'] < -10:
                element['y'] = self.SCREEN_HEIGHT + 10
                element['x'] = random.uniform(0, self.SCREEN_WIDTH)

            # Draw element
            alpha = int(element['opacity'] * self.text_fade)
            color = (*colors['accent'], alpha)

            element_surface = pygame.Surface((element['size'] * 2, element['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(element_surface, color,
                             (element['size'], element['size']), element['size'])

            surface.blit(element_surface, (int(element['x'] - element['size']),
                                         int(element['y'] - element['size'])))

    def handle_event(self, event):
        """Handle input for breathing exercise"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.current_phase == "prepare":
                    self.start_breathing()
                elif self.current_phase == "breathing":
                    # Record timing accuracy
                    expected_time = self.inhale_duration if self.is_inhaling else self.exhale_duration
                    timing_error = abs(self.breathing_cycle_time - expected_time) / expected_time
                    accuracy = max(0, 1 - timing_error)
                    self.player_input_timing.append(accuracy)

                    # Force phase transition
                    self.switch_breathing_phase()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def start_breathing(self):
        """Start the breathing exercise"""
        self.current_phase = "breathing"
        self.breathing_cycle_time = 0
        self.is_inhaling = True

    def switch_breathing_phase(self):
        """Switch between inhale and exhale"""
        self.breathing_cycle_time = 0
        self.is_inhaling = not self.is_inhaling

        if not self.is_inhaling and self.cycles_completed < self.required_cycles:
            # Completed an inhale, about to exhale
            pass
        elif self.is_inhaling:
            # Completed an exhale, about to inhale (new cycle)
            self.cycles_completed += 1

            # Calculate breath quality
            if self.player_input_timing:
                cycle_score = sum(self.player_input_timing[-2:]) / min(2, len(self.player_input_timing))
                self.breath_quality_scores.append(cycle_score)

            if self.cycles_completed >= self.required_cycles:
                self.complete_exercise()

    def complete_exercise(self):
        """Complete the breathing exercise"""
        self.current_phase = "complete"

        # Calculate overall performance
        if self.breath_quality_scores:
            average_accuracy = sum(self.breath_quality_scores) / len(self.breath_quality_scores)
        else:
            average_accuracy = 0.5

        # Create celebration particles
        for _ in range(50):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            particle = self.create_particle(
                self.center_x + random.uniform(-50, 50),
                self.center_y + random.uniform(-50, 50),
                self.colors['neutral']['primary'],
                (vx, vy),
                3.0
            )
            self.energy_particles.append(particle)

        # Complete objective based on performance
        if self.objective_manager:
            if average_accuracy > 0.7:  # Good breathing performance
                self.objective_manager.complete_objective("breathing_exercise")
            else:
                # Poor performance affects work - advance with consequence
                self.objective_manager.advance_to_next_objective()

        self.completed = True

    def update(self, dt):
        """Update breathing exercise animation"""
        if not self.active:
            return

        self.time += dt

        # Update particles
        self.update_particles(dt)

        # Create new ambient particles occasionally
        if random.random() < 0.05:
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(200, 400)
            x = self.center_x + math.cos(angle) * distance
            y = self.center_y + math.sin(angle) * distance

            # Drift toward center
            vx = (self.center_x - x) * 0.01
            vy = (self.center_y - y) * 0.01

            particle = self.create_particle(x, y, (200, 220, 255), (vx, vy))
            self.particles.append(particle)

        if self.current_phase == "breathing":
            # Update breathing timing
            self.breathing_cycle_time += dt

            # Auto-advance breathing phases
            current_duration = self.inhale_duration if self.is_inhaling else self.exhale_duration
            if self.breathing_cycle_time >= current_duration:
                self.switch_breathing_phase()

    def render(self, screen):
        """Render the enhanced breathing exercise"""
        if not self.active:
            return

        # Gradient background
        colors = self.get_current_colors()

        # Create vertical gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            r = int(20 + (colors['accent'][0] - 20) * progress * 0.1)
            g = int(20 + (colors['accent'][1] - 20) * progress * 0.1)
            b = int(40 + (colors['accent'][2] - 40) * progress * 0.1)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))

        # Draw background elements
        self.draw_background_elements(screen)

        # Draw energy waves
        self.draw_energy_waves(screen)

        # Draw floating particles
        self.draw_floating_particles(screen)

        # Draw main breathing circle
        self.draw_breathing_circle(screen)

        # Draw breathing guide
        self.draw_breathing_guide(screen)

        # Title
        title_color = colors['primary']
        title_shadow = self.fonts['title'].render("Mindful Breathing", True, (30, 30, 30))
        title_text = self.fonts['title'].render("Mindful Breathing", True, title_color)

        title_x = self.center_x - title_text.get_width() // 2
        screen.blit(title_shadow, (title_x + 3, 30 + 3))
        screen.blit(title_text, (title_x, 30))

        # Instructions
        if self.current_phase == "prepare":
            instruction = "Press SPACE when ready to begin"
        elif self.current_phase == "breathing":
            instruction = "Follow the circle rhythm, press SPACE to sync"
        else:
            # Show completion message
            if self.breath_quality_scores:
                accuracy = sum(self.breath_quality_scores) / len(self.breath_quality_scores)
                if accuracy > 0.8:
                    message = "Excellent breathing control! You feel calm and focused."
                elif accuracy > 0.6:
                    message = "Good breathing exercise. You feel more relaxed."
                else:
                    message = "Breathing exercise complete. Some stress remains."
            else:
                message = "Breathing exercise complete."

            instruction = message

        instruction_surface = self.fonts['small'].render(instruction, True, colors['secondary'])
        instruction_x = self.center_x - instruction_surface.get_width() // 2
        screen.blit(instruction_surface, (instruction_x, self.SCREEN_HEIGHT - 60))

    def start(self):
        """Start the enhanced breathing exercise"""
        self.active = True
        self.completed = False
        self.current_phase = "prepare"
        self.breathing_cycle_time = 0
        self.is_inhaling = True
        self.cycles_completed = 0
        self.player_input_timing.clear()
        self.breath_quality_scores.clear()
        self.particles.clear()
        self.energy_particles.clear()
        self.time = 0

    def stop(self):
        """Stop the breathing exercise"""
        self.active = False