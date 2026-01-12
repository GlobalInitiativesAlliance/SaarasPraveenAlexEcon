"""
ER Waiting Room Activity
Interactive visual experience of waiting 6 hours in emergency room
"""

import pygame
import random
import math
import os
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from src.core.transform_cache import get_scaled

class ERWaitingRoom:
    """Mini-game simulating the ER waiting experience"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.narrative_ref = None

        # Time tracking (6 hours = 360 game minutes)
        self.wait_time = 0
        self.total_wait_time = 360  # 6 hours in minutes
        self.time_speed = 2.0  # Minutes per second
        self.current_hour = 0

        # Player state
        self.player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.player_comfort = 50  # 0-100
        self.pain_level = 80  # 0-100 (starts high)
        self.morale = 60  # 0-100
        self.energy = 70  # 0-100
        self.player_facing = 'down'  # Track facing direction
        self.player_walking = False
        self.walk_frame = 0
        self.walk_timer = 0

        # Load character sprites
        self.load_sprites()

        # Room layout
        self.setup_room_layout()

        # Other patients (NPCs)
        self.setup_patients()

        # Visual effects
        self.pain_pulse_timer = 0
        self.clock_tick_timer = 0
        self.ambient_timer = 0

        # Interaction state
        self.current_interaction = None
        self.interaction_cooldown = 0

        # Messages and events
        self.current_message = None
        self.message_timer = 0
        self.hour_events = self.setup_hour_events()

        # Pre-render pain vignette for performance
        self._prerender_pain_vignettes()

    def _prerender_pain_vignettes(self):
        """Pre-render vignette at multiple intensities to eliminate 200 draw calls per frame"""
        self._vignette_cache = {}

        # Pre-render 11 intensity levels (0, 10, 20...100)
        for intensity in range(0, 101, 10):
            surf = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.SRCALPHA
            )

            # Render all 200 rectangles ONCE
            for i in range(50):
                color = (200, 0, 0)
                # Top edge
                pygame.draw.rect(surf, color, (0, i, SCREEN_WIDTH, 1))
                # Bottom edge
                pygame.draw.rect(surf, color,
                               (0, SCREEN_HEIGHT - i, SCREEN_WIDTH, 1))
                # Left edge
                pygame.draw.rect(surf, color, (i, 0, 1, SCREEN_HEIGHT))
                # Right edge
                pygame.draw.rect(surf, color,
                               (SCREEN_WIDTH - i, 0, 1, SCREEN_HEIGHT))

            self._vignette_cache[intensity] = surf

    def load_sprites(self):
        """Load character sprites from game assets"""
        self.sprites = {}
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
            '0_Premade_Characters', '16x16'
        )

        # Load player sprite (Character 01)
        self.player_sprites = self.load_character_sprite(base_path, 'Premade_Character_01.png')

        # Load NPC sprites for patients
        self.npc_sprites = {
            'child': self.load_character_sprite(base_path, 'Premade_Character_02.png'),
            'elderly': self.load_character_sprite(base_path, 'Premade_Character_03.png'),
            'woman': self.load_character_sprite(base_path, 'Premade_Character_04.png'),
            'worker': self.load_character_sprite(base_path, 'Premade_Character_05.png'),
            'teen': self.load_character_sprite(base_path, 'Premade_Character_06.png'),
            'receptionist': self.load_character_sprite(base_path, 'Premade_Character_07.png')
        }

    def load_character_sprite(self, base_path, filename):
        """Load a character spritesheet and extract animation frames"""
        sprite_path = os.path.join(base_path, filename)

        try:
            spritesheet = pygame.image.load(sprite_path)

            # Characters are 16x32 (width x height) in the sheet
            sprite_width = 16
            sprite_height = 32

            # Extract animation frames for each direction
            # The sheet has rows for: down, left, right, up
            # Each row has 4 frames of animation
            sprites = {
                'down': [],
                'left': [],
                'right': [],
                'up': []
            }

            directions = ['down', 'left', 'right', 'up']
            for row, direction in enumerate(directions):
                for col in range(4):  # 4 frames per direction
                    rect = pygame.Rect(
                        col * sprite_width,
                        row * sprite_height,
                        sprite_width,
                        sprite_height
                    )
                    sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                    sprite.blit(spritesheet, (0, 0), rect)

                    # Scale to display size (2x) - NOT CACHED (animation frames loaded once)
                    sprite = pygame.transform.scale(sprite, (32, 64))
                    sprites[direction].append(sprite)

            return sprites

        except Exception as e:
            print(f"Could not load sprite {filename}: {e}")
            # Return placeholder sprites if loading fails
            return self.create_placeholder_sprites()

    def create_placeholder_sprites(self):
        """Create placeholder sprites if real ones can't load"""
        placeholder = pygame.Surface((32, 64), pygame.SRCALPHA)
        placeholder.fill((100, 150, 200))
        return {
            'down': [placeholder],
            'left': [placeholder],
            'right': [placeholder],
            'up': [placeholder]
        }

    def setup_room_layout(self):
        """Define the waiting room layout"""
        self.room_objects = {
            'chairs': [
                {'pos': (150, 200), 'comfort': 30, 'occupied': False},
                {'pos': (250, 200), 'comfort': 40, 'occupied': True},
                {'pos': (350, 200), 'comfort': 35, 'occupied': False},
                {'pos': (450, 200), 'comfort': 20, 'occupied': True},
                {'pos': (550, 200), 'comfort': 45, 'occupied': False},
                {'pos': (150, 350), 'comfort': 25, 'occupied': True},
                {'pos': (250, 350), 'comfort': 50, 'occupied': False},
                {'pos': (350, 350), 'comfort': 30, 'occupied': True},
                {'pos': (450, 350), 'comfort': 35, 'occupied': False},
                {'pos': (550, 350), 'comfort': 40, 'occupied': True},
            ],
            'vending_machine': {'pos': (100, 450), 'cost': 3},
            'water_fountain': {'pos': (650, 450), 'free': True},
            'tv': {'pos': (SCREEN_WIDTH // 2, 80), 'channel': 'news'},
            'reception_desk': {'pos': (SCREEN_WIDTH // 2, 500)},
            'restroom_door': {'pos': (50, 300)},
            'clock': {'pos': (SCREEN_WIDTH // 2, 30)}
        }

        # Track which chair player is in
        self.player_chair = None

    def setup_patients(self):
        """Create other patients in waiting room"""
        self.patients = [
            {
                'name': 'Crying Child',
                'pos': [250, 200],
                'condition': 'broken_arm',
                'animation': 'crying',
                'sprite_key': 'child',
                'facing': 'down',
                'anim_frame': 0,
                'timer': 0,
                'dialogue': ["*sniffles* My arm hurts so bad...", "Mommy, when can we go home?"]
            },
            {
                'name': 'Elderly Man',
                'pos': [450, 200],
                'condition': 'chest_pain',
                'animation': 'worried',
                'sprite_key': 'elderly',
                'facing': 'down',
                'anim_frame': 0,
                'timer': 0,
                'dialogue': ["Been here since 6am...", "Chest pains, but they say it's not priority."]
            },
            {
                'name': 'Young Woman',
                'pos': [150, 350],
                'condition': 'cut_hand',
                'animation': 'holding_wound',
                'sprite_key': 'woman',
                'facing': 'right',
                'anim_frame': 0,
                'timer': 0,
                'dialogue': ["Kitchen accident. Bleeding through the towel.", "Insurance doesn't cover much..."]
            },
            {
                'name': 'Construction Worker',
                'pos': [350, 350],
                'condition': 'back_injury',
                'animation': 'pain_standing',
                'sprite_key': 'worker',
                'facing': 'down',
                'anim_frame': 0,
                'timer': 0,
                'dialogue': ["Can't sit, can't stand. Back's shot.", "No worker's comp at my job."]
            },
            {
                'name': 'Anxious Teen',
                'pos': [550, 350],
                'condition': 'panic_attack',
                'animation': 'pacing',
                'sprite_key': 'teen',
                'facing': 'left',
                'anim_frame': 0,
                'timer': 0,
                'dialogue': ["Can't breathe right...", "They think I'm faking it."]
            }
        ]

    def setup_hour_events(self):
        """Define events that happen each hour"""
        return {
            0: "You arrive and check in. The wait begins.",
            1: "An hour passes. Your ankle throbs with each heartbeat.",
            2: "Two hours. Someone who came after you gets called first.",
            3: "Three hours. Finally called for triage. Back to waiting.",
            4: "Four hours. The ice pack has melted. Pain increasing.",
            5: "Five hours. Exhaustion sets in. You can barely stay awake.",
            6: "Six hours. Finally! Your name is called."
        }

    def start(self):
        """Start the ER waiting activity"""
        self.active = True
        self.completed = False
        self.wait_time = 0
        self.current_hour = 0
        self.show_message(self.hour_events[0], 3)

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update timers
        self.wait_time += dt * self.time_speed
        self.pain_pulse_timer += dt
        self.clock_tick_timer += dt
        self.ambient_timer += dt

        # Update walking animation
        if self.player_walking:
            self.walk_timer += dt
            if self.walk_timer > 0.15:  # Change frame every 0.15 seconds
                self.walk_timer = 0
                self.walk_frame = (self.walk_frame + 1) % 4

        # Check hour progression
        new_hour = int(self.wait_time // 60)
        if new_hour > self.current_hour and new_hour <= 6:
            self.current_hour = new_hour
            self.show_message(self.hour_events.get(new_hour, ""), 4)

            # Hour-specific effects
            self.apply_hour_effects(new_hour)

        # Update patient animations
        for patient in self.patients:
            patient['timer'] += dt
            self.update_patient_animation(patient, dt)

            # Update sprite animation frames
            if patient['animation'] in ['crying', 'worried', 'pacing']:
                patient['anim_frame'] = int(patient['timer'] * 2) % 2  # Idle animation between frames 0-1

        # Update player stats over time
        self.update_player_stats(dt)

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.current_message = None

        # Update interaction cooldown
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= dt

        # Check completion (6 hours elapsed)
        if self.wait_time >= self.total_wait_time:
            self.complete()

    def apply_hour_effects(self, hour):
        """Apply effects based on the hour"""
        if hour == 1:
            self.pain_level = min(100, self.pain_level + 10)
            self.energy -= 10
        elif hour == 2:
            self.morale -= 15
            self.show_message("Someone who arrived after you is called first...", 3)
        elif hour == 3:
            self.pain_level = max(60, self.pain_level - 10)  # Ice pack helps briefly
        elif hour == 4:
            self.pain_level = min(100, self.pain_level + 20)  # Ice melted
            self.energy -= 15
        elif hour == 5:
            self.energy = max(10, self.energy - 20)
            self.morale = max(10, self.morale - 10)

    def update_patient_animation(self, patient, dt):
        """Animate other patients"""
        if patient['animation'] == 'crying':
            # Crying animation
            patient['pos'][1] += math.sin(patient['timer'] * 3) * 0.5
        elif patient['animation'] == 'pacing':
            # Pacing back and forth
            patient['pos'][0] += math.sin(patient['timer'] * 2) * 30 * dt
        elif patient['animation'] == 'pain_standing':
            # Shifting weight due to pain
            patient['pos'][0] += math.sin(patient['timer'] * 1.5) * 0.3
        elif patient['animation'] == 'worried':
            # Slight trembling
            patient['pos'][0] += random.random() * 0.5 - 0.25
            patient['pos'][1] += random.random() * 0.5 - 0.25

    def update_player_stats(self, dt):
        """Update player stats over time"""
        # Pain increases over time if standing
        if self.player_chair is None:
            self.pain_level = min(100, self.pain_level + dt * 2)
            self.energy = max(0, self.energy - dt * 3)
        else:
            # Sitting helps a bit
            self.pain_level = max(50, self.pain_level - dt * 0.5)
            self.energy = max(0, self.energy - dt * 1)

        # Comfort affects morale
        if self.player_comfort < 30:
            self.morale = max(0, self.morale - dt * 2)

        # Low energy affects everything
        if self.energy < 20:
            self.pain_level = min(100, self.pain_level + dt)

    def handle_event(self, event):
        """Handle player input"""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Skip to end (for testing)
                self.wait_time = self.total_wait_time
                return True

            # Movement
            move_speed = 5
            old_pos = self.player_pos.copy()
            moved = False

            if event.key == pygame.K_LEFT:
                self.player_pos[0] = max(50, self.player_pos[0] - move_speed)
                self.player_facing = 'left'
                self.player_walking = True
                moved = True
                self.leave_chair()
            elif event.key == pygame.K_RIGHT:
                self.player_pos[0] = min(SCREEN_WIDTH - 50, self.player_pos[0] + move_speed)
                self.player_facing = 'right'
                self.player_walking = True
                moved = True
                self.leave_chair()
            elif event.key == pygame.K_UP:
                self.player_pos[1] = max(100, self.player_pos[1] - move_speed)
                self.player_facing = 'up'
                self.player_walking = True
                moved = True
                self.leave_chair()
            elif event.key == pygame.K_DOWN:
                self.player_pos[1] = min(SCREEN_HEIGHT - 100, self.player_pos[1] + move_speed)
                self.player_facing = 'down'
                self.player_walking = True
                moved = True
                self.leave_chair()

            # Interaction
            elif event.key == pygame.K_SPACE:
                self.interact()

        elif event.type == pygame.KEYUP:
            # Stop walking animation when key is released
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                self.player_walking = False
                self.walk_frame = 0

        return True

    def leave_chair(self):
        """Player leaves their chair"""
        if self.player_chair is not None:
            self.player_chair['occupied'] = False
            self.player_chair = None
            self.player_comfort = 0

    def interact(self):
        """Handle interactions with objects"""
        if self.interaction_cooldown > 0:
            return

        # Check chairs
        for chair in self.room_objects['chairs']:
            if not chair['occupied'] and self.get_distance(self.player_pos, chair['pos']) < 40:
                self.sit_in_chair(chair)
                return

        # Check vending machine
        vm = self.room_objects['vending_machine']
        if self.get_distance(self.player_pos, vm['pos']) < 50:
            self.use_vending_machine()
            return

        # Check water fountain
        wf = self.room_objects['water_fountain']
        if self.get_distance(self.player_pos, wf['pos']) < 50:
            self.use_water_fountain()
            return

        # Check other patients
        for patient in self.patients:
            if self.get_distance(self.player_pos, patient['pos']) < 50:
                self.talk_to_patient(patient)
                return

        # Check reception
        desk = self.room_objects['reception_desk']
        if self.get_distance(self.player_pos, desk['pos']) < 60:
            self.check_with_reception()
            return

    def sit_in_chair(self, chair):
        """Sit in a chair"""
        if self.player_chair:
            self.player_chair['occupied'] = False

        chair['occupied'] = True
        self.player_chair = chair
        self.player_pos = list(chair['pos'])
        self.player_comfort = chair['comfort']

        comfort_msg = "Uncomfortable chair..." if chair['comfort'] < 30 else "This chair is okay."
        self.show_message(comfort_msg, 2)

        # Sitting helps a bit with pain
        self.pain_level = max(50, self.pain_level - 5)

    def use_vending_machine(self):
        """Use vending machine"""
        self.show_message("$3 for chips. You need to save money for rent...", 3)
        self.morale = max(0, self.morale - 5)
        self.interaction_cooldown = 1

    def use_water_fountain(self):
        """Use water fountain"""
        self.show_message("At least water is free. It helps a little.", 2)
        self.energy = min(100, self.energy + 5)
        self.interaction_cooldown = 1

    def talk_to_patient(self, patient):
        """Talk to another patient"""
        dialogue = random.choice(patient['dialogue'])
        self.show_message(f"{patient['name']}: {dialogue}", 3)
        self.morale = min(100, self.morale + 3)  # Solidarity helps
        self.interaction_cooldown = 2

    def check_with_reception(self):
        """Check status with reception"""
        responses = [
            "Receptionist: 'We're very busy today. Shouldn't be much longer.'",
            "Receptionist: 'You're still on the list. Please be patient.'",
            "Receptionist: 'The doctor will see you as soon as possible.'",
            "Receptionist: *barely looks up* 'Take a seat.'"
        ]
        self.show_message(random.choice(responses), 3)
        self.morale = max(0, self.morale - 3)
        self.interaction_cooldown = 3

    def get_distance(self, pos1, pos2):
        """Calculate distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def show_message(self, message, duration):
        """Show a temporary message"""
        self.current_message = message
        self.message_timer = duration

    def render(self, screen):
        """Render the waiting room"""
        if not self.active:
            return

        # Background - dingy waiting room
        hour_darkness = min(40, self.current_hour * 7)  # Gets darker over time
        bg_color = (140 - hour_darkness, 135 - hour_darkness, 130 - hour_darkness)
        screen.fill(bg_color)

        # Draw floor pattern
        self.draw_floor_pattern(screen)

        # Draw room objects
        self.draw_room_objects(screen)

        # Draw other patients
        self.draw_patients(screen)

        # Draw player
        self.draw_player(screen)

        # Draw UI elements
        self.draw_ui(screen)

        # Draw message if active
        if self.current_message:
            self.draw_message(screen)

        # Pain effect overlay
        if self.pain_level > 70:
            self.draw_pain_effect(screen)

    def draw_floor_pattern(self, screen):
        """Draw checkered floor pattern"""
        tile_size = 40
        for x in range(0, SCREEN_WIDTH, tile_size):
            for y in range(100, SCREEN_HEIGHT - 80, tile_size):
                if (x // tile_size + y // tile_size) % 2 == 0:
                    color = (120, 115, 110)
                else:
                    color = (110, 105, 100)
                pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))

    def draw_room_objects(self, screen):
        """Draw all room objects"""
        # Draw chairs
        for chair in self.room_objects['chairs']:
            color = (60, 60, 80) if chair['occupied'] else (80, 80, 100)
            # Chair back
            pygame.draw.rect(screen, color,
                           (chair['pos'][0] - 20, chair['pos'][1] - 25, 40, 35))
            # Chair seat
            pygame.draw.rect(screen, color,
                           (chair['pos'][0] - 20, chair['pos'][1], 40, 20))
            # Comfort indicator
            if not chair['occupied']:
                comfort_color = (100, 150, 100) if chair['comfort'] > 35 else (150, 100, 100)
                pygame.draw.circle(screen, comfort_color,
                                 (chair['pos'][0], chair['pos'][1]), 3)

        # Draw vending machine
        vm = self.room_objects['vending_machine']
        pygame.draw.rect(screen, (50, 50, 60),
                        (vm['pos'][0] - 30, vm['pos'][1] - 50, 60, 100))
        pygame.draw.rect(screen, (30, 30, 40),
                        (vm['pos'][0] - 25, vm['pos'][1] - 45, 50, 40))
        font = pygame.font.Font(None, 16)
        text = font.render("SNACKS", True, (150, 150, 150))
        screen.blit(text, (vm['pos'][0] - 20, vm['pos'][1] - 40))

        # Draw water fountain
        wf = self.room_objects['water_fountain']
        pygame.draw.rect(screen, (100, 100, 120),
                        (wf['pos'][0] - 20, wf['pos'][1] - 30, 40, 60))
        pygame.draw.arc(screen, (150, 150, 170),
                       (wf['pos'][0] - 15, wf['pos'][1] - 25, 30, 30),
                       0, math.pi, 3)

        # Draw TV
        tv = self.room_objects['tv']
        pygame.draw.rect(screen, (20, 20, 30),
                        (tv['pos'][0] - 80, tv['pos'][1] - 30, 160, 90))
        pygame.draw.rect(screen, (40, 40, 50),
                        (tv['pos'][0] - 75, tv['pos'][1] - 25, 150, 80))
        # TV screen with static
        for i in range(20):
            x = random.randint(tv['pos'][0] - 70, tv['pos'][0] + 70)
            y = random.randint(tv['pos'][1] - 20, tv['pos'][1] + 50)
            gray = random.randint(100, 200)
            pygame.draw.circle(screen, (gray, gray, gray), (x, y), 1)

        # Draw reception desk
        desk = self.room_objects['reception_desk']
        pygame.draw.rect(screen, (90, 70, 50),
                        (desk['pos'][0] - 100, desk['pos'][1] - 30, 200, 60))
        pygame.draw.rect(screen, (255, 255, 200),
                        (desk['pos'][0] - 90, desk['pos'][1] - 20, 180, 40))

        # Draw receptionist using sprite
        if 'receptionist' in self.npc_sprites:
            recep_sprite = self.npc_sprites['receptionist']['down'][0]  # Use idle down frame
            recep_rect = recep_sprite.get_rect(center=(desk['pos'][0], desk['pos'][1] - 30))
            screen.blit(recep_sprite, recep_rect)
        else:
            # Fallback to circle if sprite not available
            pygame.draw.circle(screen, (200, 180, 160),
                             (desk['pos'][0], desk['pos'][1] - 40), 15)

        # Draw clock
        self.draw_clock(screen)

    def draw_clock(self, screen):
        """Draw wall clock showing time"""
        clock = self.room_objects['clock']
        # Clock face
        pygame.draw.circle(screen, (200, 200, 200), clock['pos'], 25)
        pygame.draw.circle(screen, (50, 50, 50), clock['pos'], 25, 2)

        # Hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            start_x = clock['pos'][0] + math.cos(angle) * 20
            start_y = clock['pos'][1] + math.sin(angle) * 20
            end_x = clock['pos'][0] + math.cos(angle) * 23
            end_y = clock['pos'][1] + math.sin(angle) * 23
            pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)

        # Clock hands based on wait time
        hour_angle = math.radians((self.wait_time / 60) * 30 - 90)
        minute_angle = math.radians((self.wait_time % 60) * 6 - 90)

        # Hour hand
        hour_end_x = clock['pos'][0] + math.cos(hour_angle) * 12
        hour_end_y = clock['pos'][1] + math.sin(hour_angle) * 12
        pygame.draw.line(screen, (0, 0, 0), clock['pos'], (hour_end_x, hour_end_y), 3)

        # Minute hand
        min_end_x = clock['pos'][0] + math.cos(minute_angle) * 18
        min_end_y = clock['pos'][1] + math.sin(minute_angle) * 18
        pygame.draw.line(screen, (0, 0, 0), clock['pos'], (min_end_x, min_end_y), 2)

    def draw_patients(self, screen):
        """Draw other patients using actual sprites"""
        for patient in self.patients:
            # Try to use sprite if available
            sprite_key = patient.get('sprite_key')
            if sprite_key and sprite_key in self.npc_sprites:
                sprites = self.npc_sprites[sprite_key]
                facing = patient.get('facing', 'down')
                anim_frame = patient.get('anim_frame', 0)

                # Get the sprite for this patient
                sprite = sprites[facing][anim_frame]

                # Apply condition-specific visual effects
                if patient['condition'] == 'chest_pain':
                    # Elderly man - add slight gray tint for worried look
                    worried_sprite = sprite.copy()
                    gray_overlay = pygame.Surface(worried_sprite.get_size())
                    gray_overlay.fill((50, 50, 50))
                    worried_sprite.blit(gray_overlay, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
                    sprite = worried_sprite
                elif patient['condition'] == 'panic_attack':
                    # Teen - slight transparency for anxiety effect
                    sprite.set_alpha(220)

                # Draw the sprite
                sprite_rect = sprite.get_rect(center=[int(patient['pos'][0]), int(patient['pos'][1])])
                screen.blit(sprite, sprite_rect)

                # Add condition-specific overlays
                if patient['condition'] == 'broken_arm':
                    # Draw arm sling
                    sling_color = (240, 240, 240)
                    pygame.draw.line(screen, sling_color,
                                   (patient['pos'][0] - 8, patient['pos'][1] - 5),
                                   (patient['pos'][0] + 8, patient['pos'][1]), 3)
                    pygame.draw.rect(screen, sling_color,
                                   (patient['pos'][0] - 10, patient['pos'][1] - 10, 8, 15), 2)
                elif patient['condition'] == 'cut_hand':
                    # Draw bandage on hand
                    bandage_pos = (patient['pos'][0] + 12, patient['pos'][1] - 5)
                    pygame.draw.rect(screen, (255, 230, 230),
                                   (bandage_pos[0] - 4, bandage_pos[1] - 4, 8, 8))
                    pygame.draw.rect(screen, (200, 100, 100),
                                   (bandage_pos[0] - 4, bandage_pos[1] - 4, 8, 8), 1)
                    # Blood spots
                    pygame.draw.circle(screen, (180, 50, 50), bandage_pos, 2)
                elif patient['condition'] == 'back_injury':
                    # Show pain posture indicator
                    if int(patient['timer'] * 2) % 3 == 0:  # Periodic pain
                        for i in range(2):
                            angle = patient['timer'] + i * math.pi
                            x = patient['pos'][0] + math.cos(angle) * 15
                            y = patient['pos'][1] - 10 + math.sin(angle) * 5
                            pygame.draw.line(screen, (255, 150, 150),
                                           (patient['pos'][0], patient['pos'][1] - 10),
                                           (x, y), 1)

            else:
                # Fallback to simple shapes if sprites not available
                color = (150, 140, 130)
                pygame.draw.circle(screen, color,
                                 [int(patient['pos'][0]), int(patient['pos'][1]) - 20], 15)
                pygame.draw.rect(screen, color,
                               (patient['pos'][0] - 10, patient['pos'][1] - 10, 20, 30))

    def draw_player(self, screen):
        """Draw the player character using actual sprites"""
        # Get the current sprite based on direction and animation frame
        if self.player_sprites:
            sprite = self.player_sprites[self.player_facing][self.walk_frame if self.player_walking else 0]

            # Apply pain effect (red tint) if pain is high
            if self.pain_level > 70:
                # Create a copy and apply red tint
                pain_sprite = sprite.copy()
                pain_overlay = pygame.Surface(pain_sprite.get_size())
                pain_intensity = int((self.pain_level - 70) * 2.5)  # 0-75 based on pain level
                pain_overlay.fill((pain_intensity, 0, 0))
                pain_sprite.blit(pain_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                sprite = pain_sprite

            # Draw the sprite centered on player position
            sprite_rect = sprite.get_rect(center=(self.player_pos[0], self.player_pos[1]))
            screen.blit(sprite, sprite_rect)

            # Draw injured ankle indicator
            if self.pain_level > 50:
                # Draw bandage/swelling on foot
                ankle_pos = (self.player_pos[0] + 5, self.player_pos[1] + 25)
                pygame.draw.circle(screen, (255, 200, 200), ankle_pos, 6)
                pygame.draw.circle(screen, (200, 100, 100), ankle_pos, 6, 2)

                # Pain effect lines around ankle
                if self.pain_level > 70:
                    for i in range(3):
                        angle = self.pain_pulse_timer * 2 + i * 2
                        x = ankle_pos[0] + math.cos(angle) * 10
                        y = ankle_pos[1] + math.sin(angle) * 10
                        pygame.draw.line(screen, (255, 100, 100), ankle_pos, (x, y), 1)
        else:
            # Fallback to simple drawing if sprites didn't load
            player_color = (100, 150, 200)
            pygame.draw.circle(screen, player_color,
                             (self.player_pos[0], self.player_pos[1] - 20), 12)
            pygame.draw.rect(screen, player_color,
                           (self.player_pos[0] - 8, self.player_pos[1] - 10, 16, 25))

    def draw_ui(self, screen):
        """Draw UI elements"""
        # UI Panel background
        panel_height = 100
        pygame.draw.rect(screen, (30, 30, 40),
                        (0, SCREEN_HEIGHT - panel_height, SCREEN_WIDTH, panel_height))

        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)

        # Time waited
        hours = int(self.wait_time // 60)
        minutes = int(self.wait_time % 60)
        time_text = f"Time Waiting: {hours}h {minutes}m / 6 hours"
        time_surf = font.render(time_text, True, (255, 200, 200))
        screen.blit(time_surf, (20, SCREEN_HEIGHT - 90))

        # Stats bars
        bar_y = SCREEN_HEIGHT - 60
        bar_height = 15
        bar_spacing = 150

        # Pain level bar
        self.draw_stat_bar(screen, "Pain", self.pain_level, 100,
                          20, bar_y, (200, 50, 50))

        # Comfort bar
        self.draw_stat_bar(screen, "Comfort", self.player_comfort, 100,
                          20 + bar_spacing, bar_y, (100, 150, 100))

        # Energy bar
        self.draw_stat_bar(screen, "Energy", self.energy, 100,
                          20 + bar_spacing * 2, bar_y, (200, 200, 100))

        # Morale bar
        self.draw_stat_bar(screen, "Morale", self.morale, 100,
                          20 + bar_spacing * 3, bar_y, (100, 100, 200))

        # Instructions
        inst_text = "Arrow Keys: Move | SPACE: Interact | ESC: Skip"
        inst_surf = small_font.render(inst_text, True, (180, 180, 180))
        screen.blit(inst_surf, (20, SCREEN_HEIGHT - 25))

    def draw_stat_bar(self, screen, label, value, max_value, x, y, color):
        """Draw a stat bar"""
        bar_width = 120
        bar_height = 15

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))

        # Fill
        fill_width = int((value / max_value) * bar_width)
        pygame.draw.rect(screen, color, (x, y, fill_width, bar_height))

        # Border
        pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height), 2)

        # Label
        font = pygame.font.Font(None, 18)
        label_surf = font.render(f"{label}: {int(value)}", True, (200, 200, 200))
        screen.blit(label_surf, (x, y - 15))

    def draw_message(self, screen):
        """Draw current message"""
        if not self.current_message:
            return

        # Message box
        box_width = 600
        box_height = 60
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = SCREEN_HEIGHT // 2 - 100

        # Background with alpha
        alpha = min(255, self.message_timer * 255)
        msg_surface = pygame.Surface((box_width, box_height))
        msg_surface.set_alpha(alpha)
        msg_surface.fill((20, 20, 30))
        screen.blit(msg_surface, (box_x, box_y))

        # Border
        pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_width, box_height), 2)

        # Text
        font = pygame.font.Font(None, 24)
        lines = self.current_message.split('\n') if '\n' in self.current_message else [self.current_message]

        y_offset = box_y + 20
        for line in lines:
            text_surf = font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 25

    def draw_pain_effect(self, screen):
        """Draw pain visual effect (pre-rendered: 200 rects → 1 blit)"""
        # Quantize pain level to nearest 10 for cache lookup
        intensity_key = int((self.pain_level / 100) * 10) * 10

        # Get cached vignette and apply alpha
        vignette = self._vignette_cache[intensity_key].copy()
        vignette.set_alpha(int(20 + abs(math.sin(self.pain_pulse_timer * 3)) * 30))

        screen.blit(vignette, (0, 0))

    def complete(self):
        """Complete the ER waiting activity"""
        if not self.active:
            return

        self.active = False
        self.completed = True

        # Final message
        self.show_message("Finally! After 6 hours, your name is called.", 5)

        # Update narrative if reference exists
        if self.narrative_ref:
            self.narrative_ref.triaged = True
            self.narrative_ref.current_wait_phase = 6