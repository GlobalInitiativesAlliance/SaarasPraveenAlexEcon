import pygame
import math
import json
import random
from constants import *

class ClassroomInterior:
    """Complete classroom interior with NPCs and interactions"""
    def __init__(self, game, quiz_activity, room_name="classroom_default"):
        self.game = game
        self.quiz_activity = quiz_activity
        self.active = False
        self.room_name = room_name
        self.room_data = None
        
        # Room dimensions (in tiles)
        self.room_width = 16
        self.room_height = 12
        
        # Calculate room position to center on screen
        self.room_x = (SCREEN_WIDTH - self.room_width * TILE_SIZE) // 2
        self.room_y = (SCREEN_HEIGHT - self.room_height * TILE_SIZE) // 2
        
        # Player position in classroom (tile coordinates)
        self.player_x = 8
        self.player_y = 10
        self.player_facing = "up"
        self.player_moving = False
        self.player_move_progress = 0.0
        self.player_start_x = self.player_x
        self.player_start_y = self.player_y
        self.player_target_x = self.player_x
        self.player_target_y = self.player_y
        self.move_speed = 5.0  # tiles per second
        
        # Player states
        self.player_seated = False
        self.player_seat_pos = (10, 7)  # Desk index 7 position
        
        # Animation timers
        self.animation_timer = 0
        self.npc_blink_timers = {}
        self.floating_text = []  # For showing temporary messages
        
        # Transition effects
        self.transition_alpha = 255
        self.transition_state = "fade_in"
        
        # Classroom state
        self.lesson_state = "enter"  # enter, find_seat, lesson, quiz
        self.dialogue_active = False
        self.current_dialogue = None
        self.dialogue_index = 0
        self.dialogue_speaker = None
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Load room layout and tilesets
        self.load_room_data()
        self.load_interior_tiles()
        
        # Initialize desks list before setup
        self.desks = []
        
        # Scan room for furniture first if room data exists
        if self.room_data:
            self.scan_room_furniture()
        
        # Initialize classroom elements (will use scanned desks or create defaults)
        self.setup_classroom()
        
    def load_room_data(self):
        """Load room data from interior_rooms.json"""
        try:
            with open("interior_rooms.json", "r") as f:
                data = json.load(f)
                if self.room_name in data["rooms"]:
                    self.room_data = data["rooms"][self.room_name]
                    # Update room dimensions from saved data
                    self.room_width = self.room_data.get('width', 16)
                    self.room_height = self.room_data.get('height', 12)
                    print(f"Loaded room: {self.room_name} ({self.room_width}x{self.room_height})")
                else:
                    print(f"Room '{self.room_name}' not found, using default layout")
                    self.room_data = None
        except Exception as e:
            print(f"Could not load room data: {e}")
            self.room_data = None
    
    def load_interior_tiles(self):
        """Load interior tileset images"""
        try:
            # Load all interior tilesets
            self.floor_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_FloorsAndWalls.png").convert_alpha()
            self.furniture_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_FurnitureState1.png").convert_alpha()
            self.small_items_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_SmallItems.png").convert_alpha()
            self.doors_windows_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_DoorsAndWindows.png").convert_alpha()
            
            # Scale factor for tiles (assuming 16x16 original tiles)
            self.tile_scale = TILE_SIZE / 16
        except:
            print("Warning: Could not load interior tilesets, using placeholder graphics")
            self.floor_tileset = None
            self.furniture_tileset = None
            
    def get_tile_from_sheet(self, sheet, x, y, width=16, height=16):
        """Extract a tile from a tileset"""
        if sheet is None:
            return None
        try:
            tile = sheet.subsurface(pygame.Rect(x * width, y * height, width, height))
            # Scale to match game tile size
            scaled_tile = pygame.transform.scale(tile, (int(width * self.tile_scale), int(height * self.tile_scale)))
            return scaled_tile
        except:
            return None
        
    def scan_room_furniture(self):
        """Scan the room layout to find furniture positions"""
        if not self.room_data or 'layers' not in self.room_data:
            return
            
        furniture_layer = self.room_data['layers'].get('furniture', [])
        self.detected_desks = []
        self.detected_seats = []
        self.detected_blackboard = None
        
        # Scan for furniture
        for y in range(len(furniture_layer)):
            for x in range(len(furniture_layer[y])):
                tile = furniture_layer[y][x]
                if tile and len(tile) == 3:
                    sheet_name, tile_x, tile_y = tile
                    
                    # Detect seats/desks based on your furniture tiles
                    # Looking at your data, seats seem to be at positions like (5,2), (5,3), (6,2), (6,3)
                    if 'Furniture' in sheet_name:
                        # Check for desk/seat combinations
                        if (tile_x == 5 or tile_x == 6) and (tile_y == 2 or tile_y == 3):
                            self.detected_seats.append({
                                'x': x, 
                                'y': y, 
                                'tile': (sheet_name, tile_x, tile_y),
                                'occupied': False
                            })
                        # Detect blackboard (appears to be at 2-4, 4-6 based on your data)
                        elif tile_x >= 2 and tile_x <= 4 and tile_y >= 4 and tile_y <= 6:
                            if not self.detected_blackboard:
                                self.detected_blackboard = {'x': x, 'y': y, 'width': 3, 'height': 3}
                    
                    # Also check for standalone desks at (10, 0) and (10, 1)
                    if 'Furniture' in sheet_name and tile_x == 10 and (tile_y == 0 or tile_y == 1):
                        # These appear to be desks on the right side
                        self.detected_seats.append({
                            'x': x,
                            'y': y,
                            'tile': (sheet_name, tile_x, tile_y),
                            'occupied': False
                        })
                        
        # Use detected seats as desks
        if self.detected_seats:
            # Sort seats by position for consistent ordering
            self.detected_seats.sort(key=lambda s: (s['y'], s['x']))
            
            # Mark some seats as occupied by students
            for i, seat in enumerate(self.detected_seats):
                if i < 6 and i != 3:  # Leave one seat empty for player (index 3)
                    seat['occupied'] = True
                    
            self.desks = self.detected_seats
            print(f"Found {len(self.detected_seats)} seats in room layout")
            
            # Update player seat position to an empty desk
            if len(self.desks) > 3:
                self.player_seat_pos = (self.desks[3]['x'], self.desks[3]['y'])
        else:
            # Fall back to default positions if no seats found
            self.desks = []
            for i in range(12):
                self.desks.append({
                    'x': 4 + (i % 4) * 2,
                    'y': 5 + (i // 4) * 2,
                    'occupied': False,
                    'tile': None
                })
        
        if self.detected_blackboard:
            self.blackboard = self.detected_blackboard
        else:
            # Default blackboard
            self.blackboard = {'x': 8, 'y': 2, 'width': 3, 'height': 1}
            
        print(f"Detected {len(self.desks)} desks in room layout")
    
    def setup_classroom(self):
        """Setup all classroom elements"""
        # Default tile indices
        self.floor_tile_index = (7, 0)  # Wood floor
        self.wall_tile_index = (0, 2)   # Wall tile
        
        # Create students list
        self.students = []
        
        # Only create default desks if none were detected from room
        if not self.desks:
            # Default desk layout
            desk_positions = [
                (4, 5), (6, 5), (8, 5), (10, 5),    # Front row
                (4, 7), (6, 7), (8, 7), (10, 7),    # Middle row
                (4, 9), (6, 9), (8, 9), (10, 9),    # Back row
            ]
            
            for i, (x, y) in enumerate(desk_positions):
                self.desks.append({
                    'x': x,
                    'y': y,
                    'occupied': i != 7,  # Leave desk 7 empty for player
                    'tile': None
                })
                
            # Set player seat position
            self.player_seat_pos = (self.desks[7]['x'], self.desks[7]['y'])
        
        # Teacher setup
        self.teacher = {
            'x': 8,
            'y': 2,
            'facing': 'down',
            'name': 'Ms. Johnson',
            'dialogues': {
                'enter': [
                    "Welcome to Employment Rights class!",
                    "Please find your seat - it's the empty desk in the front row.",
                    "We'll begin once everyone is seated."
                ],
                'lesson': [
                    "Today we'll learn about your rights as an employee.",
                    "It's important to know what protections you have at work.",
                    "Let's start with some key concepts...",
                    "First: You have the right to a safe workplace.",
                    "Your employer must provide proper safety equipment and training.",
                    "Second: You cannot be discriminated against.",
                    "This includes race, gender, age, or disability.",
                    "Third: You're entitled to fair wages for your work.",
                    "This includes minimum wage and overtime pay.",
                    "Now, let's test your understanding with a quiz."
                ]
            }
        }
        
        # Create student NPCs for occupied desks after room scan
        student_names = ["Alex", "Sam", "Jordan", "Casey", "Morgan", "Riley"]
        student_colors = [
            (150, 100, 200),  # Purple
            (200, 150, 100),  # Orange
            (100, 150, 200),  # Blue
            (200, 100, 150),  # Pink
            (150, 200, 100),  # Green
            (200, 200, 100),  # Yellow
        ]
        student_dialogues = [
            ["Hey! Ready for class?", "I heard this quiz is important."],
            ["Ms. Johnson is a great teacher.", "Pay attention, this stuff matters!"],
            ["I'm nervous about the quiz...", "Good luck!"],
            ["Did you do the reading?", "Workers' rights are so important."],
            ["This class is really useful.", "Especially if you're getting a job soon."],
            ["I'm taking notes.", "Want to study together later?"]
        ]
        
        # Create students for occupied desks
        student_idx = 0
        for i, desk in enumerate(self.desks):
            if desk.get('occupied', False) and student_idx < len(student_names):
                self.students.append({
                    'x': desk['x'],
                    'y': desk['y'],
                    'name': student_names[student_idx],
                    'color': student_colors[student_idx] if student_idx < len(student_colors) else (150, 150, 150),
                    'desk_index': i,
                    'dialogue': student_dialogues[student_idx] if student_idx < len(student_dialogues) else ["Hello!", "Good to see you."],
                    'facing': 'up'
                })
                student_idx += 1
        
        # Blackboard
        self.blackboard = {
            'x': 6,
            'y': 1,
            'width': 4,
            'height': 2,
            'content': "EMPLOYMENT RIGHTS"
        }
        
        # Create collision map
        self.create_collision_map()
        
    def create_collision_map(self):
        """Create collision map for the classroom"""
        self.collision_map = set()
        
        # Walls (except door)
        for x in range(self.room_width):
            self.collision_map.add((x, 0))
            if x != 8:  # Door position
                self.collision_map.add((x, self.room_height - 1))
        for y in range(1, self.room_height - 1):
            self.collision_map.add((0, y))
            self.collision_map.add((self.room_width - 1, y))
            
        # Desks
        for desk in self.desks:
            self.collision_map.add((desk['x'], desk['y']))
            
        # Teacher's position and desk area
        self.collision_map.add((self.teacher['x'], self.teacher['y']))
        for x in range(7, 10):
            self.collision_map.add((x, 2))
            
        # Blackboard area
        for x in range(6, 10):
            self.collision_map.add((x, 1))
            
    def enter(self):
        """Enter the classroom"""
        self.active = True
        self.transition_state = "fade_in"
        self.transition_alpha = 255
        self.lesson_state = "enter"
        self.start_dialogue(self.teacher['dialogues']['enter'], self.teacher['name'])
        
        # Clear the player near objective flag to hide E prompt
        if hasattr(self.game, 'player_near_objective'):
            self.game.player_near_objective = False
        
    def add_floating_text(self, text, x, y, color=(255, 255, 100)):
        """Add floating text effect"""
        self.floating_text.append({
            'text': text,
            'x': x,
            'y': y,
            'color': color,
            'timer': 2.0  # 2 seconds
        })
        
    def exit(self):
        """Exit the classroom"""
        self.transition_state = "fade_out"
        
    def start_dialogue(self, dialogue_list, speaker=None):
        """Start a dialogue sequence"""
        self.dialogue_active = True
        self.current_dialogue = dialogue_list
        self.dialogue_index = 0
        self.dialogue_speaker = speaker
        
    def handle_input(self, keys):
        """Handle keyboard input (receives keys state)"""
        if self.dialogue_active:
            return
            
        if self.lesson_state == "quiz" and self.quiz_activity.active:
            return
            
        # Movement (only if not seated and not moving)
        if not self.player_seated and not self.player_moving:
            new_x, new_y = self.player_x, self.player_y
            new_facing = self.player_facing
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_x -= 1
                new_facing = "left"
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_x += 1
                new_facing = "right"
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                new_y -= 1
                new_facing = "up"
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                new_y += 1
                new_facing = "down"
                
            self.player_facing = new_facing
                
            # Check collision
            if new_x != self.player_x or new_y != self.player_y:
                if (new_x, new_y) not in self.collision_map and \
                   0 <= new_x < self.room_width and 0 <= new_y < self.room_height:
                    self.player_start_x = self.player_x
                    self.player_start_y = self.player_y
                    self.player_target_x = new_x
                    self.player_target_y = new_y
                    self.player_moving = True
                    self.player_move_progress = 0.0
                    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if self.dialogue_active:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.current_dialogue):
                        self.dialogue_active = False
                        self.on_dialogue_complete()
                return
                
            if self.lesson_state == "quiz" and self.quiz_activity.active:
                self.quiz_activity.handle_key(event.key)
                return
                
            if event.key == pygame.K_e:
                self.handle_interaction()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.lesson_state == "quiz" and self.quiz_activity.active:
                # Pass mouse events to quiz
                if hasattr(self.quiz_activity, 'handle_mouse_click'):
                    self.quiz_activity.handle_mouse_click(event.pos, event.button)
                    
    def handle_interaction(self):
        """Handle E key interactions"""
        # Check for door
        if self.player_y == self.room_height - 2 and self.player_x == 8:
            if self.lesson_state != "enter":
                self.exit()
            return
            
        # Check for seat
        if self.lesson_state == "find_seat":
            # Check if player is next to their seat
            seat_x, seat_y = self.player_seat_pos
            if abs(self.player_x - seat_x) <= 1 and abs(self.player_y - seat_y) <= 1:
                # Sit down
                self.player_x = seat_x
                self.player_y = seat_y
                self.player_seated = True
                self.player_facing = "up"
                
                # Add visual feedback
                screen_x, screen_y = self.get_screen_pos(seat_x, seat_y)
                self.add_floating_text("Seated!", screen_x + TILE_SIZE // 2, screen_y, (100, 255, 100))
                
                self.start_lesson()
                return
                
        # Check for teacher interaction
        if abs(self.player_x - self.teacher['x']) <= 1 and \
           abs(self.player_y - self.teacher['y']) <= 1:
            if not self.dialogue_active and self.lesson_state == "find_seat":
                self.start_dialogue(["Please find your seat so we can begin."], self.teacher['name'])
            return
            
        # Check for student interactions
        for student in self.students:
            if abs(self.player_x - student['x']) <= 1 and \
               abs(self.player_y - student['y']) <= 1:
                if not self.dialogue_active:
                    self.start_dialogue(student['dialogue'], student['name'])
                return
                
    def on_dialogue_complete(self):
        """Called when dialogue sequence ends"""
        if self.lesson_state == "enter":
            self.lesson_state = "find_seat"
        elif self.lesson_state == "lesson":
            # Start quiz after lesson
            self.lesson_state = "quiz"
            self.quiz_activity.start()
            self.quiz_activity.entrance_complete = True
            # Ensure quiz is properly initialized
            print(f"Starting quiz: {self.quiz_activity.__class__.__name__}")
            print(f"Quiz active: {self.quiz_activity.active}, entrance_complete: {self.quiz_activity.entrance_complete}")
            
    def start_lesson(self):
        """Start the lesson sequence"""
        self.lesson_state = "lesson"
        self.start_dialogue(self.teacher['dialogues']['lesson'], self.teacher['name'])
        
    def update(self, dt):
        """Update classroom state"""
        # Update animation timer
        self.animation_timer += dt
        
        # Update floating text
        for text_item in self.floating_text[:]:
            text_item['timer'] -= dt
            text_item['y'] -= 20 * dt  # Float upward
            if text_item['timer'] <= 0:
                self.floating_text.remove(text_item)
        
        # Handle transitions
        if self.transition_state == "fade_in":
            self.transition_alpha = max(0, self.transition_alpha - 400 * dt)
            if self.transition_alpha <= 0:
                self.transition_state = "active"
        elif self.transition_state == "fade_out":
            self.transition_alpha = min(255, self.transition_alpha + 400 * dt)
            if self.transition_alpha >= 255:
                self.active = False
                
        # Update player movement
        if self.player_moving:
            self.player_move_progress += self.move_speed * dt
            if self.player_move_progress >= 1.0:
                self.player_x = self.player_target_x
                self.player_y = self.player_target_y
                self.player_moving = False
                self.player_move_progress = 0.0
            else:
                # Smooth interpolation
                t = self.player_move_progress
                # Use smoothstep for more natural movement
                t = t * t * (3.0 - 2.0 * t)
                
        # Update quiz if active
        if self.lesson_state == "quiz" and self.quiz_activity.active:
            self.quiz_activity.update(dt)
            if self.quiz_activity.completed:
                self.lesson_state = "complete"
                self.game.objective_manager.advance_to_next_objective()
                self.exit()
                
    def get_player_pixel_pos(self):
        """Get interpolated player position in pixels"""
        if self.player_moving:
            t = self.player_move_progress
            t = t * t * (3.0 - 2.0 * t)  # smoothstep
            
            current_x = self.player_start_x + (self.player_target_x - self.player_start_x) * t
            current_y = self.player_start_y + (self.player_target_y - self.player_start_y) * t
            
            pixel_x = self.room_x + current_x * TILE_SIZE
            pixel_y = self.room_y + current_y * TILE_SIZE
        else:
            pixel_x = self.room_x + self.player_x * TILE_SIZE
            pixel_y = self.room_y + self.player_y * TILE_SIZE
            
        return pixel_x, pixel_y
        
    def get_screen_pos(self, grid_x, grid_y):
        """Convert grid position to screen position"""
        screen_x = self.room_x + grid_x * TILE_SIZE
        screen_y = self.room_y + grid_y * TILE_SIZE
        return screen_x, screen_y
        
    def draw_desks_and_students(self, screen):
        """Draw all desks with seats and students"""
        # Draw all desks first
        for i, desk in enumerate(self.desks):
            desk_x = self.room_x + desk['x'] * TILE_SIZE
            desk_y = self.room_y + desk['y'] * TILE_SIZE
            
            # Use seat texture from room data if available
            if 'tile' in desk and desk['tile']:
                sheet_name, tile_x, tile_y = desk['tile']
                if self.furniture_tileset and 'Furniture' in sheet_name:
                    seat_tile = self.get_tile_from_sheet(self.furniture_tileset, tile_x, tile_y)
                    if seat_tile:
                        screen.blit(seat_tile, (desk_x, desk_y))
                        # Skip fallback drawing
                        continue
            
            # Fallback if no tile data or failed to load
            if self.furniture_tileset:
                # Try to get chair sprite
                chair_tile = self.get_tile_from_sheet(self.furniture_tileset, 0, 7)  # Chair position
                if chair_tile:
                    screen.blit(chair_tile, (desk_x, desk_y))
                    
                # Draw desk on top
                desk_tile = self.get_tile_from_sheet(self.furniture_tileset, 0, 6)  # Desk position
                if desk_tile:
                    screen.blit(desk_tile, (desk_x, desk_y - TILE_SIZE // 2))
            else:
                # Fallback - draw simple rectangles
                # Chair
                chair_rect = pygame.Rect(desk_x + 4, desk_y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
                pygame.draw.rect(screen, (100, 80, 60), chair_rect)
                pygame.draw.rect(screen, (60, 40, 30), chair_rect, 2)
                
                # Desk
                desk_rect = pygame.Rect(desk_x, desk_y - 10, TILE_SIZE, 20)
                pygame.draw.rect(screen, (120, 100, 80), desk_rect)
                pygame.draw.rect(screen, (80, 60, 40), desk_rect, 2)
                
            # Highlight player's seat
            if i == 7 and self.lesson_state == "find_seat" and not self.player_seated:  # Middle row, 4th desk
                # Draw pulsing highlight
                pulse = abs(math.sin(self.animation_timer * 3)) * 50 + 50
                highlight_color = (100, 255, 100, int(pulse))
                highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(highlight_surf, highlight_color, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
                screen.blit(highlight_surf, (desk_x, desk_y))
                
                # Arrow pointing down
                arrow_y = desk_y - 30 + math.sin(self.animation_timer * 4) * 5
                arrow_points = [
                    (desk_x + TILE_SIZE // 2, arrow_y + 10),
                    (desk_x + TILE_SIZE // 2 - 8, arrow_y),
                    (desk_x + TILE_SIZE // 2 + 8, arrow_y)
                ]
                pygame.draw.polygon(screen, (255, 255, 100), arrow_points)
                
        # Draw students
        for student in self.students:
            student_x = self.room_x + student['x'] * TILE_SIZE
            student_y = self.room_y + student['y'] * TILE_SIZE
            
            # Get color, use default if not present
            color = student.get('color', (150, 150, 150))
            
            # Draw simple student representation
            # Body circle
            pygame.draw.circle(screen, color, 
                             (student_x + TILE_SIZE // 2, student_y + TILE_SIZE // 2), 
                             12)
            # Head circle
            pygame.draw.circle(screen, color, 
                             (student_x + TILE_SIZE // 2, student_y + TILE_SIZE // 2 - 8), 
                             8)
            # Outline
            pygame.draw.circle(screen, (0, 0, 0), 
                             (student_x + TILE_SIZE // 2, student_y + TILE_SIZE // 2), 
                             12, 2)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (student_x + TILE_SIZE // 2, student_y + TILE_SIZE // 2 - 8), 
                             8, 2)
                
    def draw(self, screen):
        """Draw the classroom"""
        if not self.active:
            return
            
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Draw room from saved layout if available
        if self.room_data and 'layers' in self.room_data:
            layers = self.room_data['layers']
            
            # Draw each layer in order
            for layer_name in ['floor', 'walls', 'furniture', 'decor']:
                if layer_name in layers:
                    layer = layers[layer_name]
                    
                    for y in range(min(len(layer), self.room_height)):
                        for x in range(min(len(layer[y]), self.room_width)):
                            tile_info = layer[y][x]
                            if tile_info and len(tile_info) == 3:
                                sheet_name, tile_x, tile_y = tile_info
                                
                                # Determine which tileset to use
                                tileset = None
                                if 'FloorsAndWalls' in sheet_name:
                                    tileset = self.floor_tileset
                                elif 'FurnitureState1' in sheet_name:
                                    tileset = self.furniture_tileset
                                elif 'SmallItems' in sheet_name:
                                    tileset = self.small_items_tileset
                                elif 'DoorsAndWindows' in sheet_name:
                                    tileset = self.doors_windows_tileset
                                    
                                if tileset:
                                    tile = self.get_tile_from_sheet(tileset, tile_x, tile_y)
                                    if tile:
                                        screen_x = self.room_x + x * TILE_SIZE
                                        screen_y = self.room_y + y * TILE_SIZE
                                        screen.blit(tile, (screen_x, screen_y))
        else:
            # Fallback to default tiles if no room data
            if self.floor_tileset:
                floor_tile = self.get_tile_from_sheet(self.floor_tileset, self.floor_tile_index[0], self.floor_tile_index[1])
                wall_tile = self.get_tile_from_sheet(self.floor_tileset, self.wall_tile_index[0], self.wall_tile_index[1])
                
                for y in range(self.room_height):
                    for x in range(self.room_width):
                        tile_x = self.room_x + x * TILE_SIZE
                        tile_y = self.room_y + y * TILE_SIZE
                        
                        if y == 0 or (y == self.room_height - 1 and x != 8) or x == 0 or x == self.room_width - 1:
                            if wall_tile:
                                screen.blit(wall_tile, (tile_x, tile_y))
                        else:
                            if floor_tile:
                                screen.blit(floor_tile, (tile_x, tile_y))
                                
        # Fallback to colored tiles if no tileset loaded
        if not self.floor_tileset:
            floor_rect = pygame.Rect(self.room_x, self.room_y, 
                                    self.room_width * TILE_SIZE, 
                                    self.room_height * TILE_SIZE)
            pygame.draw.rect(screen, (180, 140, 100), floor_rect)
            pygame.draw.rect(screen, (100, 80, 60), floor_rect, TILE_SIZE)
            
        # Draw blackboard
        board_x = self.room_x + self.blackboard['x'] * TILE_SIZE
        board_y = self.room_y + self.blackboard['y'] * TILE_SIZE
        board_rect = pygame.Rect(board_x, board_y,
                               self.blackboard['width'] * TILE_SIZE,
                               self.blackboard['height'] * TILE_SIZE)
        pygame.draw.rect(screen, (20, 40, 20), board_rect)
        pygame.draw.rect(screen, (80, 60, 40), board_rect, 3)
        
        # Blackboard content
        if self.lesson_state != "quiz":
            font = pygame.font.Font(None, 28)
            text = font.render(self.blackboard['content'], True, (255, 255, 255))
            text_rect = text.get_rect(center=board_rect.center)
            screen.blit(text, text_rect)
        else:
            # Draw quiz on blackboard
            self.draw_quiz_on_board(screen, board_rect)
            
        # Draw desks and chairs
        self.draw_desks_and_students(screen)
                           
        # Draw teacher (using player sprite for now)
        teacher_x = self.room_x + self.teacher['x'] * TILE_SIZE
        teacher_y = self.room_y + self.teacher['y'] * TILE_SIZE
        
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            self.game.player.draw_at_position(screen, teacher_x, teacher_y, 'down')
        else:
            pygame.draw.circle(screen, (100, 100, 200),
                             (teacher_x + TILE_SIZE // 2, teacher_y + TILE_SIZE // 2),
                             TILE_SIZE // 3)
                         
        # Draw students (using player sprite)
        for student in self.students:
            student_x = self.room_x + student['x'] * TILE_SIZE
            student_y = self.room_y + student['y'] * TILE_SIZE
            
            if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
                self.game.player.draw_at_position(screen, student_x, student_y, student['facing'])
            else:
                pygame.draw.circle(screen, (100, 200, 100),
                                 (student_x + TILE_SIZE // 2, student_y + TILE_SIZE // 2),
                                 TILE_SIZE // 3)
                                 
        # Draw player
        player_x, player_y = self.get_player_pixel_pos()
        
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            self.game.player.draw_at_position(screen, player_x, player_y, self.player_facing)
        else:
            pygame.draw.circle(screen, (255, 100, 100),
                             (player_x + TILE_SIZE // 2, player_y + TILE_SIZE // 2),
                             TILE_SIZE // 3)
                         
        # Draw door
        door_x = self.room_x + 8 * TILE_SIZE
        door_y = self.room_y + (self.room_height - 1) * TILE_SIZE
        
        if self.doors_windows_tileset:
            door_tile = self.get_tile_from_sheet(self.doors_windows_tileset, 1, 0)  # Door sprite
            if door_tile:
                screen.blit(door_tile, (door_x, door_y))
        else:
            pygame.draw.rect(screen, (80, 60, 40),
                           (door_x, door_y, TILE_SIZE, TILE_SIZE))
                           
        # Draw interaction prompts
        self.draw_interaction_prompts(screen)
        
        # Draw dialogue
        if self.dialogue_active:
            self.draw_dialogue(screen)
            
        # Draw objective reminder
        if self.lesson_state == "find_seat" and not self.player_seated:
            self.draw_objective_reminder(screen)
            
        # Draw floating text
        for text_item in self.floating_text:
            text_surf = self.small_font.render(text_item['text'], True, text_item['color'])
            text_rect = text_surf.get_rect(center=(int(text_item['x']), int(text_item['y'])))
            # Add shadow
            shadow_surf = self.small_font.render(text_item['text'], True, (0, 0, 0))
            screen.blit(shadow_surf, (text_rect.x + 1, text_rect.y + 1))
            screen.blit(text_surf, text_rect)
            
        # Don't draw quiz overlay - it's already drawn on the blackboard
            
        # Draw transition overlay
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.transition_alpha)
            screen.blit(fade_surface, (0, 0))
            
    def draw_interaction_prompts(self, screen):
        """Draw E prompts for interactions"""
        font = pygame.font.Font(None, 20)
        
        # Get player grid position
        player_grid_x = self.player_x
        player_grid_y = self.player_y
        
        # Door prompt
        if player_grid_y == self.room_height - 2 and player_grid_x == 8:
            if self.lesson_state != "enter":
                prompt = font.render("Press E to exit", True, (255, 255, 200))
                prompt_x = self.room_x + 8 * TILE_SIZE - prompt.get_width() // 2 + TILE_SIZE // 2
                prompt_y = self.room_y + (self.room_height - 2) * TILE_SIZE - 25
                screen.blit(prompt, (prompt_x, prompt_y))
                
        # Seat prompt
        if self.lesson_state == "find_seat" and not self.player_seated:
            seat_x, seat_y = self.player_seat_pos
            if abs(player_grid_x - seat_x) <= 1 and abs(player_grid_y - seat_y) <= 1:
                prompt = font.render("Press E to sit", True, (255, 255, 200))
                pixel_x, pixel_y = self.get_player_pixel_pos()
                prompt_x = pixel_x - prompt.get_width() // 2 + TILE_SIZE // 2
                prompt_y = pixel_y - 25
                screen.blit(prompt, (prompt_x, prompt_y))
                
    def draw_dialogue(self, screen):
        """Draw dialogue box"""
        if not self.dialogue_active or not self.current_dialogue:
            return
            
        # Dialogue box dimensions
        box_width = 700
        box_height = 140
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = SCREEN_HEIGHT - box_height - 60
        
        # Draw box background
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (40, 40, 40), box_rect)
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 3)
        
        # Draw speaker name if available
        y_offset = 15
        if self.dialogue_speaker:
            name_font = pygame.font.Font(None, 22)
            name_text = name_font.render(self.dialogue_speaker + ":", True, (255, 220, 100))
            screen.blit(name_text, (box_x + 20, box_y + y_offset))
            y_offset += 30
                       
        # Draw text
        font = pygame.font.Font(None, 24)
        text = self.current_dialogue[self.dialogue_index]
        
        # Word wrap
        words = text.split(' ')
        lines = []
        current_line = []
        max_width = box_width - 40
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
            
        # Draw lines
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (box_x + 20, box_y + y_offset))
            y_offset += 28
            
        # Continue prompt
        cont_font = pygame.font.Font(None, 20)
        cont_text = "Press SPACE to continue" if self.dialogue_index < len(self.current_dialogue) - 1 else "Press SPACE"
        cont_surface = cont_font.render(cont_text, True, (200, 200, 200))
        screen.blit(cont_surface, (box_x + box_width - cont_surface.get_width() - 20, 
                                 box_y + box_height - 30))
                                 
    def draw_objective_reminder(self, screen):
        """Draw objective reminder at top of screen"""
        font = pygame.font.Font(None, 28)
        text = "🎯 Find your seat (empty desk in front row)"
        text_surface = font.render(text, True, (255, 255, 100))
        
        # Background for text
        bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - text_surface.get_width() // 2 - 20,
                            20, text_surface.get_width() + 40, 40)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        pygame.draw.rect(screen, (255, 255, 100), bg_rect, 2)
        
        # Draw text
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, 30))
        
    def draw_quiz_on_board(self, screen, board_rect):
        """Draw quiz content on the blackboard"""
        if not self.quiz_activity.active:
            return
            
        # Clear board
        pygame.draw.rect(screen, (20, 40, 20), board_rect)
        pygame.draw.rect(screen, (80, 60, 40), board_rect, 3)
        
        # Let quiz draw itself
        if hasattr(self.quiz_activity, 'draw_on_board'):
            self.quiz_activity.draw_on_board(screen, board_rect)