import pygame
import math
import json
from src.constants import *
from src.activities.work.burger_activity import BurgerFlippingActivity

class BurgerPlaceInterior:
    """Burger place interior with burger flipping tutorial"""
    def __init__(self, game, room_name="burger_room"):
        self.game = game
        self.active = False
        self.room_name = room_name
        self.room_data = None
        
        # Room dimensions (in tiles)
        self.room_width = 16
        self.room_height = 12
        
        # Calculate room position to center on screen
        self.room_x = (SCREEN_WIDTH - self.room_width * TILE_SIZE) // 2
        self.room_y = (SCREEN_HEIGHT - self.room_height * TILE_SIZE) // 2
        
        # Player position in burger place (tile coordinates)
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
        
        # Burger station state
        self.burger_station_pos = (8, 2)  # Default position
        self.near_station = False
        self.tutorial_state = "enter"  # enter, guide, work, complete
        
        # Create burger activity - pass the objective manager
        objective_manager = None
        if hasattr(game, 'objective_manager'):
            objective_manager = game.objective_manager
        elif hasattr(game, 'game') and hasattr(game.game, 'objective_manager'):
            objective_manager = game.game.objective_manager
        self.burger_activity = BurgerFlippingActivity(objective_manager)
        
        # Manager NPC
        self.manager = {
            'x': 6,
            'y': 5,
            'facing': 'down',
            'name': 'Manager Mike',
            'target_x': 6,
            'target_y': 5,
            'moving': False,
            'move_progress': 0.0
        }
        
        # Animation timers
        self.animation_timer = 0
        self.floating_text = []
        
        # Transition effects
        self.transition_alpha = 255
        self.transition_state = "fade_in"
        
        # Dialogue
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
        
        # Create collision map
        self.create_collision_map()
        
    def load_room_data(self):
        """Load room data from interior_rooms.json"""
        try:
            with open("interior_rooms.json", "r") as f:
                data = json.load(f)
                if self.room_name in data["rooms"]:
                    self.room_data = data["rooms"][self.room_name]
                    self.room_width = self.room_data.get('width', 16)
                    self.room_height = self.room_data.get('height', 12)
                    print(f"Loaded burger place: {self.room_name} ({self.room_width}x{self.room_height})")
                else:
                    print(f"Room '{self.room_name}' not found, using default layout")
                    self.room_data = None
        except Exception as e:
            print(f"Could not load room data: {e}")
            self.room_data = None
    
    def load_interior_tiles(self):
        """Load interior tileset images"""
        try:
            self.floor_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_FloorsAndWalls.png").convert_alpha()
            self.furniture_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_FurnitureState1.png").convert_alpha()
            self.small_items_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_SmallItems.png").convert_alpha()
            self.doors_windows_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_DoorsAndWindows.png").convert_alpha()
            
            # Scale factor for tiles
            self.tile_scale = TILE_SIZE / 16
        except:
            print("Warning: Could not load interior tilesets")
            self.floor_tileset = None
            self.furniture_tileset = None
            
    def get_tile_from_sheet(self, sheet, x, y, width=16, height=16):
        """Extract a tile from a tileset"""
        if sheet is None:
            return None
        try:
            tile = sheet.subsurface(pygame.Rect(x * width, y * height, width, height))
            scaled_tile = pygame.transform.scale(tile, (int(width * self.tile_scale), int(height * self.tile_scale)))
            return scaled_tile
        except:
            return None
            
    def create_collision_map(self):
        """Create collision map for the burger place"""
        self.collision_map = set()
        
        # Walls (except door)
        for x in range(self.room_width):
            self.collision_map.add((x, 0))
            if x != 8:  # Door position
                self.collision_map.add((x, self.room_height - 1))
        for y in range(1, self.room_height - 1):
            self.collision_map.add((0, y))
            self.collision_map.add((self.room_width - 1, y))
            
        # Burger station/counter area
        for x in range(5, 12):
            for y in range(0, 3):
                self.collision_map.add((x, y))
                
    def enter(self):
        """Enter the burger place"""
        self.active = True
        self.transition_state = "fade_in"
        self.transition_alpha = 255
        self.tutorial_state = "enter"
        
        # Start with greeting
        self.start_dialogue([
            "Welcome to Burger Palace!",
            "I'm Manager Mike. Ready to learn burger flipping?",
            "Follow me to the grill station!"
        ], self.manager['name'])
        
        # Clear the player near objective flag
        if hasattr(self.game, 'player_near_objective'):
            self.game.player_near_objective = False
            
    def exit(self):
        """Exit the burger place"""
        self.transition_state = "fade_out"
        
    def start_dialogue(self, dialogue_list, speaker=None):
        """Start a dialogue sequence"""
        self.dialogue_active = True
        self.current_dialogue = dialogue_list
        self.dialogue_index = 0
        self.dialogue_speaker = speaker
        
    def handle_input(self, keys):
        """Handle keyboard input"""
        if self.dialogue_active:
            return
            
        if self.tutorial_state == "work" and self.burger_activity.active:
            return
            
        # Movement
        if not self.player_moving:
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
                
            if self.tutorial_state == "work" and self.burger_activity.active:
                self.burger_activity.handle_key(event.key)
                return
                
            if event.key == pygame.K_e:
                self.handle_interaction()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.tutorial_state == "work" and self.burger_activity.active:
                self.burger_activity.handle_mouse_click(event.pos, event.button)
                    
        elif event.type == pygame.MOUSEMOTION:
            if self.tutorial_state == "work" and self.burger_activity.active:
                self.burger_activity.handle_mouse_motion(event.pos)
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.tutorial_state == "work" and self.burger_activity.active:
                self.burger_activity.handle_mouse_release(event.pos, event.button)
                    
    def handle_interaction(self):
        """Handle E key interactions"""
        # Check for door (more lenient positioning)
        if self.player_y >= self.room_height - 3 and (self.player_x >= 7 and self.player_x <= 9):
            if self.tutorial_state == "complete":
                self.exit()
            else:
                self.start_dialogue(["Please complete the training first!"], self.manager['name'])
            return
            
        # Check for burger station
        if self.near_station and self.tutorial_state == "guide":
            self.start_dialogue([
                "Great! You're at the grill station.",
                "Press E again to start your burger training.",
                "You'll need to complete 3 burger orders!"
            ], self.manager['name'])
            self.tutorial_state = "ready"
        elif self.near_station and self.tutorial_state == "ready":
            # Start burger making
            self.tutorial_state = "work"
            self.burger_activity.start()
            
    def on_dialogue_complete(self):
        """Called when dialogue ends"""
        if self.tutorial_state == "enter":
            self.tutorial_state = "guide"
            # Start manager movement
            self.manager['target_x'] = self.burger_station_pos[0] - 1
            self.manager['target_y'] = self.burger_station_pos[1] + 1
            self.manager['moving'] = True
            
    def update_manager(self, dt):
        """Update manager NPC movement"""
        if self.manager['moving']:
            # Simple movement towards target
            dx = self.manager['target_x'] - self.manager['x']
            dy = self.manager['target_y'] - self.manager['y']
            
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                # Move towards target
                move_speed = 3.0 * dt
                if abs(dx) > abs(dy):
                    if dx > 0:
                        self.manager['x'] = min(self.manager['x'] + move_speed, self.manager['target_x'])
                        self.manager['facing'] = 'right'
                    else:
                        self.manager['x'] = max(self.manager['x'] - move_speed, self.manager['target_x'])
                        self.manager['facing'] = 'left'
                else:
                    if dy > 0:
                        self.manager['y'] = min(self.manager['y'] + move_speed, self.manager['target_y'])
                        self.manager['facing'] = 'down'
                    else:
                        self.manager['y'] = max(self.manager['y'] - move_speed, self.manager['target_y'])
                        self.manager['facing'] = 'up'
            else:
                # Reached target
                self.manager['x'] = self.manager['target_x']
                self.manager['y'] = self.manager['target_y']
                self.manager['moving'] = False
                self.manager['facing'] = 'right'  # Face the station
                
                if self.tutorial_state == "guide":
                    self.start_dialogue([
                        "This is the grill station!",
                        "Stand next to it and press E to start training."
                    ], self.manager['name'])
                    
    def update(self, dt):
        """Update burger place state"""
        self.animation_timer += dt
        
        # Update floating text
        for text_item in self.floating_text[:]:
            text_item['timer'] -= dt
            text_item['y'] -= 20 * dt
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
                t = self.player_move_progress
                t = t * t * (3.0 - 2.0 * t)
                
        # Update manager
        self.update_manager(dt)
        
        # Check if player is near burger station
        dist = abs(self.player_x - self.burger_station_pos[0]) + abs(self.player_y - self.burger_station_pos[1])
        self.near_station = dist <= 2
        
        # Update burger activity if active
        if self.tutorial_state == "work" and self.burger_activity.active:
            self.burger_activity.update(dt)
            if self.burger_activity.completed:
                self.tutorial_state = "complete"
                self.start_dialogue([
                    "Excellent work!",
                    "You've mastered burger flipping!",
                    "You can exit through the door now.",
                    "Come back to work anytime!"
                ], self.manager['name'])
                # Complete the objective here - check both possible locations
                print(f"Burger training complete, advancing objective...")
                if hasattr(self.game, 'objective_manager'):
                    obj_mgr = self.game.objective_manager
                    current_obj = obj_mgr.get_current_objective()
                    print(f"Current objective before advance: {current_obj.id if current_obj else 'None'}")
                    print(f"Current index: {obj_mgr.current_objective_index}")
                    print(f"Total objectives: {len(obj_mgr.objectives)}")
                    if obj_mgr.current_objective_index + 1 < len(obj_mgr.objectives):
                        next_obj = obj_mgr.objectives[obj_mgr.current_objective_index + 1]
                        print(f"Next objective will be: {next_obj.id}")
                    self.game.objective_manager.advance_to_next_objective()
                elif hasattr(self.game, 'game') and hasattr(self.game.game, 'objective_manager'):
                    obj_mgr = self.game.game.objective_manager
                    current_obj = obj_mgr.get_current_objective()
                    print(f"Current objective before advance: {current_obj.id if current_obj else 'None'}")
                    print(f"Current index: {obj_mgr.current_objective_index}")
                    print(f"Total objectives: {len(obj_mgr.objectives)}")
                    if obj_mgr.current_objective_index + 1 < len(obj_mgr.objectives):
                        next_obj = obj_mgr.objectives[obj_mgr.current_objective_index + 1]
                        print(f"Next objective will be: {next_obj.id}")
                    self.game.game.objective_manager.advance_to_next_objective()
                
    def get_player_pixel_pos(self):
        """Get interpolated player position in pixels"""
        if self.player_moving:
            t = self.player_move_progress
            t = t * t * (3.0 - 2.0 * t)
            
            current_x = self.player_start_x + (self.player_target_x - self.player_start_x) * t
            current_y = self.player_start_y + (self.player_target_y - self.player_start_y) * t
            
            pixel_x = self.room_x + current_x * TILE_SIZE
            pixel_y = self.room_y + current_y * TILE_SIZE
        else:
            pixel_x = self.room_x + self.player_x * TILE_SIZE
            pixel_y = self.room_y + self.player_y * TILE_SIZE
            
        return pixel_x, pixel_y
        
    def draw(self, screen):
        """Draw the burger place"""
        if not self.active:
            return
            
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Draw room from saved layout
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
            # Fallback drawing
            # Draw floor
            for y in range(self.room_height):
                for x in range(self.room_width):
                    screen_x = self.room_x + x * TILE_SIZE
                    screen_y = self.room_y + y * TILE_SIZE
                    color = (100, 80, 60) if (x + y) % 2 == 0 else (90, 70, 50)
                    pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    
            # Draw grill station
            grill_x = self.room_x + self.burger_station_pos[0] * TILE_SIZE
            grill_y = self.room_y + self.burger_station_pos[1] * TILE_SIZE
            pygame.draw.rect(screen, (60, 60, 60), (grill_x - TILE_SIZE, grill_y, TILE_SIZE * 3, TILE_SIZE * 2))
            pygame.draw.rect(screen, (40, 40, 40), (grill_x - TILE_SIZE, grill_y, TILE_SIZE * 3, TILE_SIZE * 2), 3)
                                        
        # Draw door
        door_x = self.room_x + 8 * TILE_SIZE
        door_y = self.room_y + (self.room_height - 1) * TILE_SIZE
        
        if self.doors_windows_tileset:
            door_tile = self.get_tile_from_sheet(self.doors_windows_tileset, 1, 0)
            if door_tile:
                screen.blit(door_tile, (door_x, door_y))
        else:
            pygame.draw.rect(screen, (80, 60, 40), (door_x, door_y, TILE_SIZE, TILE_SIZE))
            
        # Draw manager NPC
        manager_x = self.room_x + int(self.manager['x'] * TILE_SIZE)
        manager_y = self.room_y + int(self.manager['y'] * TILE_SIZE)
        
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            self.game.player.draw_at_position(screen, manager_x, manager_y, self.manager['facing'])
        else:
            pygame.draw.circle(screen, (100, 150, 200),
                             (manager_x + TILE_SIZE // 2, manager_y + TILE_SIZE // 2),
                             TILE_SIZE // 3)
            
        # Draw player
        player_x, player_y = self.get_player_pixel_pos()
        
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            self.game.player.draw_at_position(screen, player_x, player_y, self.player_facing)
        else:
            pygame.draw.circle(screen, (255, 100, 100),
                             (player_x + TILE_SIZE // 2, player_y + TILE_SIZE // 2),
                             TILE_SIZE // 3)
                             
        # Draw interaction prompts
        font = pygame.font.Font(None, 20)
        
        # Burger station prompt
        if self.near_station and (self.tutorial_state == "guide" or self.tutorial_state == "ready"):
            prompt = font.render("Press E to interact", True, (255, 255, 200))
            prompt_x = player_x - prompt.get_width() // 2 + TILE_SIZE // 2
            prompt_y = player_y - 25
            screen.blit(prompt, (prompt_x, prompt_y))
            
        # Door prompt
        if self.player_y >= self.room_height - 3 and (self.player_x >= 7 and self.player_x <= 9):
            if self.tutorial_state == "complete":
                prompt = font.render("Press E to exit", True, (255, 255, 200))
            else:
                prompt = font.render("Complete training first!", True, (255, 100, 100))
            prompt_x = player_x - prompt.get_width() // 2 + TILE_SIZE // 2
            prompt_y = player_y - 25
            screen.blit(prompt, (prompt_x, prompt_y))
            
        # Draw floating text
        for text_item in self.floating_text:
            text_surf = self.small_font.render(text_item['text'], True, text_item['color'])
            text_rect = text_surf.get_rect(center=(int(text_item['x']), int(text_item['y'])))
            shadow_surf = self.small_font.render(text_item['text'], True, (0, 0, 0))
            screen.blit(shadow_surf, (text_rect.x + 1, text_rect.y + 1))
            screen.blit(text_surf, text_rect)
            
        # Draw dialogue
        if self.dialogue_active:
            self.draw_dialogue(screen)
            
        # Draw transition overlay
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.transition_alpha)
            screen.blit(fade_surface, (0, 0))
            
        # Draw burger activity LAST to ensure it's on top
        if self.tutorial_state == "work" and self.burger_activity.active:
            self.burger_activity.draw(screen)
            
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
        
        # Draw speaker name
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