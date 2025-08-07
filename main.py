import pygame
import math
from constants import *
from game_world import ObjectiveManager, AnimatedPlayer, TileManager, CityMap


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Builder - Tile Based")
        self.clock = pygame.time.Clock()

        self.tile_manager = TileManager()
        self.city_map = CityMap()
        self.city_map.tile_manager = self.tile_manager
        self.city_map.load_from_image()

        self.player = AnimatedPlayer(
            self.city_map.width // 2,
            self.city_map.height // 2,
            TILE_SIZE
        )

        self.objective_manager = ObjectiveManager(self)
        self.player_near_objective = False

        self.camera_x = 0
        self.camera_y = 0
        self.update_camera()

        self.font = pygame.font.Font(None, 20)
        self.show_grid = True

        self.render_map_cache()
        self.objective_manager.start()

    def update_camera(self):
        self.camera_x = self.player.pixel_x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.camera_y = self.player.pixel_y - (SCREEN_HEIGHT - UI_HEIGHT) // 2 + TILE_SIZE // 2

        max_camera_x = self.city_map.width * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = self.city_map.height * TILE_SIZE - (SCREEN_HEIGHT - UI_HEIGHT)

        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def render_map_cache(self):
        self.map_cache = {}
        tile_count = 0
        building_count = 0

        for y in range(self.city_map.height):
            for x in range(self.city_map.width):
                tile_data = self.city_map.map_data[y][x]

                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, building_key, offset_x, offset_y, bg_info = tile_data
                        bg_tile = self.tile_manager.get_tile(bg_info[0], bg_info[1], bg_info[2])
                        if bg_tile:
                            self.map_cache[(x, y)] = ('background', bg_tile)
                    else:
                        _, building_key, offset_x, offset_y = tile_data

                    building = self.tile_manager.building_data.get(building_key)

                    if building and offset_y < len(building['tiles']) and offset_x < len(building['tiles'][offset_y]):
                        tile_info = building['tiles'][offset_y][offset_x]
                        tile = self.tile_manager.get_tile(tile_info[0], tile_info[1], tile_info[2])
                        if tile:
                            if tile_data[0] == 'building_with_bg':
                                self.map_cache[(x, y)] = ('building_with_bg', bg_tile, tile)
                            else:
                                self.map_cache[(x, y)] = ('building', tile)
                            building_count += 1

                elif isinstance(tile_data, tuple) and tile_data[0] == 'tile':
                    _, tile_info = tile_data
                    tile = self.tile_manager.get_tile(tile_info[0], tile_info[1], tile_info[2])
                    if tile:
                        self.map_cache[(x, y)] = ('tile', tile)
                        tile_count += 1
                elif tile_data == 'grass':
                    tile = self.tile_manager.get_grass_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('grass', tile)
                elif tile_data == 'sidewalk':
                    tile = self.tile_manager.get_sidewalk_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('sidewalk', tile)
                elif tile_data == 'road':
                    tile = self.tile_manager.get_random_tile('road')
                    if tile:
                        self.map_cache[(x, y)] = ('road', tile)
                else:
                    self.map_cache[(x, y)] = ('dirt', None)

        print(f"Map cache rendered: {tile_count} tiles, {building_count} building parts")

    def handle_input(self):
        if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
            return

        keys = pygame.key.get_pressed()

        if not self.player.moving:
            new_x, new_y = self.player.x, self.player.y

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if new_x > 0:
                    new_x -= 1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if new_x < self.city_map.width - 1:
                    new_x += 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                if new_y > 0:
                    new_y -= 1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if new_y < self.city_map.height - 1:
                    new_y += 1

            if new_x != self.player.x or new_y != self.player.y:
                self.player.move_to(new_x, new_y)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        start_x = max(0, int(self.camera_x // TILE_SIZE))
        end_x = min(int((self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 2), self.city_map.width)
        start_y = max(0, int(self.camera_y // TILE_SIZE))
        end_y = min(int((self.camera_y + (SCREEN_HEIGHT - UI_HEIGHT)) // TILE_SIZE + 2), self.city_map.height)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - int(self.camera_x)
                screen_y = y * TILE_SIZE - int(self.camera_y)

                if (x, y) in self.map_cache:
                    cache_data = self.map_cache[(x, y)]

                    if cache_data[0] == 'dirt':
                        pygame.draw.rect(self.screen, (139, 90, 43),
                                         (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif cache_data[0] == 'building_with_bg':
                        _, bg_tile, building_tile = cache_data
                        if bg_tile:
                            self.screen.blit(bg_tile, (screen_x, screen_y))
                        if building_tile:
                            self.screen.blit(building_tile, (screen_x, screen_y))
                    else:
                        tile_type, tile_surface = cache_data
                        if tile_surface:
                            self.screen.blit(tile_surface, (screen_x, screen_y))

                if self.show_grid:
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        self.player.draw(self.screen, self.camera_x, self.camera_y)
        self.objective_manager.draw_objective_markers(self.screen, self.camera_x, self.camera_y)
        self.draw_ui()
        self.objective_manager.draw_ui(self.screen)

    def draw_ui(self):
        controls_font = pygame.font.Font(None, 18)

        controls_texts = [
            "WASD - Move",
            "E - Interact",
            "G - Toggle Grid",
            "N - Skip Objective"
        ]

        controls_height = len(controls_texts) * 20 + 15
        controls_width = 120
        controls_x = SCREEN_WIDTH - controls_width - 20
        controls_y = SCREEN_HEIGHT - controls_height - 20

        controls_bg = pygame.Surface((controls_width, controls_height))
        controls_bg.fill((20, 20, 25))
        controls_bg.set_alpha(120)
        self.screen.blit(controls_bg, (controls_x - 5, controls_y - 5))

        for i, text in enumerate(controls_texts):
            text_surface = controls_font.render(text, True, (180, 180, 180))
            self.screen.blit(text_surface, (controls_x, controls_y + i * 20))

        self.objective_manager.draw_ui(self.screen)

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_r:
                        self.city_map.load_from_image()
                        self.render_map_cache()
                    elif event.key == pygame.K_e:
                        if self.player_near_objective:
                            self.objective_manager.complete_current_objective()
                    elif event.key == pygame.K_n:
                        # Admin skip - press N to skip to next objective
                        self.objective_manager.skip_to_next_objective()
                    else:
                        if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                            self.objective_manager.current_activity.handle_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        self.objective_manager.current_activity.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check for skip button click first
                    if event.button == 1:  # Left click
                        mx, my = event.pos
                        # Skip button position (matching draw_ui in ObjectiveManager)
                        margin = 25
                        panel_width = 320
                        skip_width = 80
                        skip_height = 28
                        skip_x = margin + panel_width - skip_width - 15
                        skip_y = margin + 15
                        
                        if skip_x <= mx <= skip_x + skip_width and skip_y <= my <= skip_y + skip_height:
                            self.objective_manager.skip_to_next_objective()
                            continue
                    
                    if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        self.objective_manager.current_activity.handle_mouse_click(event.pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        if hasattr(self.objective_manager.current_activity, 'handle_mouse_release'):
                            self.objective_manager.current_activity.handle_mouse_release(event.pos, event.button)

            self.handle_input()
            self.player.update(dt)

            self.player_near_objective = self.objective_manager.check_player_at_objective(
                self.player.x, self.player.y
            )

            self.objective_manager.update(dt)
            self.update_camera()
            self.draw()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()