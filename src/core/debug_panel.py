"""
Debug Panel - Overlay debug information for troubleshooting game issues
"""
import pygame
from src.core.debug_logger import debug_logger

class DebugPanel:
    """Debug overlay panel for game diagnostics"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        self.font_small = pygame.font.Font(None, 16)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 24)

        # Panel dimensions
        self.panel_width = 400
        self.panel_height = 600
        self.panel_x = screen_width - self.panel_width - 10
        self.panel_y = 10

        # Colors
        self.bg_color = (0, 0, 0, 200)
        self.border_color = (100, 150, 200)
        self.text_color = (255, 255, 255)
        self.error_color = (255, 100, 100)
        self.warning_color = (255, 200, 100)
        self.success_color = (100, 255, 100)

    def toggle(self):
        """Toggle debug panel visibility"""
        self.visible = not self.visible

    def draw(self, screen, game):
        """Draw the debug panel overlay"""
        if not self.visible:
            return

        # Create semi-transparent surface
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)

        # Draw border
        pygame.draw.rect(panel_surface, self.border_color,
                        (0, 0, self.panel_width, self.panel_height), 2)

        # Draw content
        y_offset = 10
        y_offset = self.draw_header(panel_surface, y_offset)
        y_offset = self.draw_game_state(panel_surface, y_offset, game)
        y_offset = self.draw_input_debug(panel_surface, y_offset, game)
        y_offset = self.draw_performance_stats(panel_surface, y_offset)
        y_offset = self.draw_recent_errors(panel_surface, y_offset)
        y_offset = self.draw_room_history(panel_surface, y_offset)
        self.draw_controls(panel_surface, self.panel_height - 60)

        # Blit to main screen
        screen.blit(panel_surface, (self.panel_x, self.panel_y))

    def draw_header(self, surface, y):
        """Draw panel header"""
        title = self.font_large.render("DEBUG PANEL", True, self.text_color)
        surface.blit(title, (10, y))
        y += 30

        # Draw separator line
        pygame.draw.line(surface, self.border_color, (10, y), (self.panel_width - 10, y), 1)
        return y + 10

    def draw_game_state(self, surface, y, game):
        """Draw current game state information"""
        # Section title
        title = self.font_normal.render("GAME STATE", True, self.success_color)
        surface.blit(title, (10, y))
        y += 25

        # Current room
        if hasattr(game, 'current_interior') and game.current_interior:
            room_name = game.current_interior.__class__.__name__
            building_pos = getattr(game.current_interior, 'building_pos', 'Unknown')
        else:
            room_name = "Exterior"
            building_pos = "N/A"

        room_text = self.font_small.render(f"Room: {room_name}", True, self.text_color)
        surface.blit(room_text, (15, y))
        y += 18

        pos_text = self.font_small.render(f"Position: {building_pos}", True, self.text_color)
        surface.blit(pos_text, (15, y))
        y += 18

        # Current objective
        if hasattr(game, 'objective_manager') and game.objective_manager:
            current_obj = game.objective_manager.get_current_objective()
            obj_id = current_obj.id if current_obj else "None"
        else:
            obj_id = "No Manager"

        obj_text = self.font_small.render(f"Objective: {obj_id}", True, self.text_color)
        surface.blit(obj_text, (15, y))
        y += 18

        # Player position
        if hasattr(game, 'current_interior') and game.current_interior:
            if hasattr(game.current_interior, 'player_pixel_x'):
                px = int(game.current_interior.player_pixel_x)
                py = int(game.current_interior.player_pixel_y)
                player_text = self.font_small.render(f"Player: ({px}, {py})", True, self.text_color)
                surface.blit(player_text, (15, y))
        elif hasattr(game, 'player'):
            px = int(game.player.x)
            py = int(game.player.y)
            player_text = self.font_small.render(f"Player: ({px}, {py})", True, self.text_color)
            surface.blit(player_text, (15, y))

        return y + 25

    def draw_performance_stats(self, surface, y):
        """Draw performance statistics"""
        title = self.font_normal.render("PERFORMANCE", True, self.success_color)
        surface.blit(title, (10, y))
        y += 25

        stats = debug_logger.get_performance_summary()

        # Room loads
        loads_text = f"Room Loads: {stats['total_room_loads']}"
        text = self.font_small.render(loads_text, True, self.text_color)
        surface.blit(text, (15, y))
        y += 18

        # Success rate
        success_rate = f"Success Rate: {stats['success_rate']:.1f}%"
        color = self.success_color if stats['success_rate'] > 90 else self.warning_color
        text = self.font_small.render(success_rate, True, color)
        surface.blit(text, (15, y))
        y += 18

        # Load time
        if stats['average_load_time'] > 0:
            load_time = f"Avg Load: {stats['average_load_time']:.3f}s"
            color = self.success_color if stats['average_load_time'] < 0.1 else self.warning_color
            text = self.font_small.render(load_time, True, color)
            surface.blit(text, (15, y))
            y += 18

        # Uptime
        uptime = f"Uptime: {stats['uptime']:.1f}s"
        text = self.font_small.render(uptime, True, self.text_color)
        surface.blit(text, (15, y))

        return y + 25

    def draw_recent_errors(self, surface, y):
        """Draw recent errors"""
        title = self.font_normal.render("RECENT ERRORS", True, self.error_color)
        surface.blit(title, (10, y))
        y += 25

        recent_errors = debug_logger.get_recent_entries(3, 'ERROR')

        if not recent_errors:
            no_errors = self.font_small.render("No recent errors", True, self.success_color)
            surface.blit(no_errors, (15, y))
            y += 18
        else:
            for error in recent_errors:
                time_text = error['timestamp']
                msg_text = error['message'][:35] + "..." if len(error['message']) > 35 else error['message']

                error_line = f"{time_text}: {msg_text}"
                text = self.font_small.render(error_line, True, self.error_color)
                surface.blit(text, (15, y))
                y += 18

        return y + 15

    def draw_room_history(self, surface, y):
        """Draw recent room history"""
        title = self.font_normal.render("ROOM HISTORY", True, self.success_color)
        surface.blit(title, (10, y))
        y += 25

        room_history = debug_logger.get_room_history()

        if not room_history:
            no_history = self.font_small.render("No room history", True, self.text_color)
            surface.blit(no_history, (15, y))
            y += 18
        else:
            # Show last 4 rooms
            for room in room_history[-4:]:
                room_line = f"{room['time']}: {room['room']}"
                text = self.font_small.render(room_line, True, self.text_color)
                surface.blit(text, (15, y))
                y += 18

        return y + 15

    def draw_input_debug(self, surface, y, game):
        """Draw input system debug information"""
        try:
            from src.core.input_manager import get_input_debug_info
            input_info = get_input_debug_info()

            # Input system header
            title = self.font_normal.render("INPUT SYSTEM", True, self.success_color)
            surface.blit(title, (10, y))
            y += 25

            # Input events this frame
            events_text = f"Events This Frame: {input_info.get('events_this_frame', 0)}"
            text = self.font_small.render(events_text, True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

            # Buffered events
            buffered_text = f"Buffered Events: {input_info.get('buffered_events', 0)}"
            text = self.font_small.render(buffered_text, True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

            # Processing time
            process_time = input_info.get('avg_process_time_ms', 0)
            color = self.error_color if process_time > 5 else self.text_color
            time_text = f"Avg Process Time: {process_time:.2f}ms"
            text = self.font_small.render(time_text, True, color)
            surface.blit(text, (15, y))
            y += 18

            # Lag warnings
            warnings = input_info.get('input_lag_warnings', 0)
            if warnings > 0:
                warning_text = f"Lag Warnings: {warnings}"
                text = self.font_small.render(warning_text, True, self.warning_color)
                surface.blit(text, (15, y))
                y += 18

            # Buffer sizes
            key_buffer = input_info.get('key_buffer_size', 0)
            mouse_buffer = input_info.get('mouse_buffer_size', 0)
            buffer_text = f"Buffers: Key={key_buffer}, Mouse={mouse_buffer}"
            text = self.font_small.render(buffer_text, True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

        except ImportError:
            # Input manager not available yet
            text = self.font_small.render("Input Manager Not Available", True, self.warning_color)
            surface.blit(text, (15, y))
            y += 18
        except Exception as e:
            error_text = f"Input debug error: {str(e)[:30]}"
            text = self.font_small.render(error_text, True, self.error_color)
            surface.blit(text, (15, y))
            y += 18

        return y + 15

    def draw_controls(self, surface, y):
        """Draw control instructions"""
        title = self.font_normal.render("CONTROLS", True, self.warning_color)
        surface.blit(title, (10, y))
        y += 25

        controls = [
            "F3: Toggle this panel",
            "CTRL+ESC: Emergency exit room"
        ]

        for control in controls:
            text = self.font_small.render(control, True, self.text_color)
            surface.blit(text, (15, y))
            y += 18