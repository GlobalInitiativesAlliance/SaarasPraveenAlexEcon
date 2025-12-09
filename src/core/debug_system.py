"""
Debug System - Core functionality for game state jumping and testing
Provides utilities to jump between objectives, parts, and game states for fast testing.
"""

import pygame
import json
import os
from typing import Dict, Any, Optional, List, Tuple

# Global debug settings storage
_debug_settings = {}

def set_debug_settings(settings: Dict[str, Any]) -> None:
    """Set debug settings from launcher or config file"""
    global _debug_settings
    _debug_settings = settings.copy()

def get_debug_settings() -> Dict[str, Any]:
    """Get current debug settings"""
    return _debug_settings.copy()

def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return _debug_settings.get('debug_mode', False)

class DebugMenu:
    """In-game debug menu for runtime objective and state management"""

    def __init__(self, game):
        self.game = game
        self.visible = False
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 32)

        self.menu_width = 600
        self.menu_height = 500
        self.menu_x = 50
        self.menu_y = 50

        self.scroll_offset = 0
        self.selected_index = 0
        self.menu_items = []
        self.current_page = 'main'  # 'main', 'objectives', 'stats', 'presets'

        # Colors
        self.bg_color = (40, 40, 50, 230)
        self.header_color = (70, 70, 90)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 150, 255)
        self.button_color = (60, 60, 80)
        self.button_hover_color = (80, 80, 100)

        self.update_menu_items()

    def toggle(self) -> None:
        """Toggle debug menu visibility"""
        self.visible = not self.visible
        if self.visible:
            self.update_menu_items()
            print("🔧 Debug menu opened (F1 to close)")
        else:
            print("🔧 Debug menu closed")

    def update_menu_items(self) -> None:
        """Update menu items based on current page"""
        self.menu_items = []

        if self.current_page == 'main':
            self.menu_items = [
                ('📋 Jump to Objective', 'objectives'),
                ('📊 Modify Stats', 'stats'),
                ('🎮 Load Preset', 'presets'),
                ('⏭️  Skip Current Objective', 'skip_objective'),
                ('🔄 Restart Current Objective', 'restart_objective'),
                ('📍 Set Player Position', 'set_position'),
                ('🏠 Part 1 (Housing)', 'jump_part_1'),
                ('🏥 Part 2 (Healthcare)', 'jump_part_2'),
                ('💾 Save Debug State', 'save_state'),
                ('📂 Load Debug State', 'load_state'),
                ('❌ Close Menu', 'close')
            ]
        elif self.current_page == 'objectives':
            self.menu_items = [('← Back to Main', 'main')]

            # Add current part objectives
            obj_mgr = self.game.objective_manager
            current_part = obj_mgr.game_part
            self.menu_items.append((f'📝 Part {current_part} Objectives:', 'header'))

            for i, obj in enumerate(obj_mgr.objectives):
                marker = "👉" if i == obj_mgr.current_objective_index else "  "
                status = "✅" if obj.completed else "⭕"
                self.menu_items.append((f'{marker} {status} {i:2d}. {obj.title}', f'jump_obj_{i}'))

        elif self.current_page == 'stats':
            self.menu_items = [
                ('← Back to Main', 'main'),
                ('💰 Money Settings', 'header'),
                ('Set Money: $20 (Low)', 'money_low'),
                ('Set Money: $100 (Medium)', 'money_medium'),
                ('Set Money: $500 (High)', 'money_high'),
                ('❤️  Health/Stress Settings', 'header'),
                ('Low Health (30), High Stress (90)', 'health_low_stress_high'),
                ('Medium Health (70), Medium Stress (50)', 'health_medium_stress_medium'),
                ('High Health (100), Low Stress (20)', 'health_high_stress_low'),
                ('⚡ Energy Settings', 'header'),
                ('Low Energy (25)', 'energy_low'),
                ('Medium Energy (60)', 'energy_medium'),
                ('High Energy (100)', 'energy_high')
            ]

        elif self.current_page == 'presets':
            self.menu_items = [('← Back to Main', 'main')]

            # Load presets from config
            try:
                config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'debug_config.json')
                with open(config_path, 'r') as f:
                    config = json.load(f)

                presets = config.get('presets', {})
                self.menu_items.append(('🎮 Available Presets:', 'header'))

                for preset_name, preset_data in presets.items():
                    desc = preset_data.get('description', 'No description')
                    part = preset_data.get('part', '?')
                    obj = preset_data.get('objective', 'unknown')
                    display_text = f'{preset_name} - Part {part} ({obj[:20]}{"..." if len(obj) > 20 else ""})'
                    self.menu_items.append((display_text, f'preset_{preset_name}'))

            except Exception as e:
                self.menu_items.append((f'Error loading presets: {e}', 'header'))

    def handle_key(self, key: int) -> None:
        """Handle keyboard input for debug menu"""
        if not self.visible:
            return

        if key == pygame.K_ESCAPE or key == pygame.K_F1:
            self.toggle()
        elif key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == pygame.K_DOWN:
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
        elif key == pygame.K_RETURN:
            self.execute_selected()

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse clicks on menu items"""
        if not self.visible:
            return False

        mx, my = pos

        # Check if click is within menu bounds
        if not (self.menu_x <= mx <= self.menu_x + self.menu_width and
                self.menu_y <= my <= self.menu_y + self.menu_height):
            return False

        # Calculate clicked item
        item_y = my - (self.menu_y + 60)  # Account for header
        if item_y >= 0:
            item_height = 30
            clicked_index = int(item_y // item_height) + self.scroll_offset

            if 0 <= clicked_index < len(self.menu_items):
                self.selected_index = clicked_index
                self.execute_selected()

        return True

    def execute_selected(self) -> None:
        """Execute the selected menu action"""
        if not self.menu_items or self.selected_index >= len(self.menu_items):
            return

        _, action = self.menu_items[self.selected_index]

        # Page navigation
        if action in ['main', 'objectives', 'stats', 'presets']:
            self.current_page = action
            self.selected_index = 0
            self.update_menu_items()
            return

        # Main actions
        if action == 'close':
            self.toggle()
        elif action == 'skip_objective':
            self.game.objective_manager.skip_to_next_objective()
            self.game.objective_manager.show_notification("Objective skipped", (255, 255, 100))
            self.update_menu_items()
        elif action == 'restart_objective':
            self.restart_current_objective()
        elif action.startswith('jump_obj_'):
            obj_index = int(action.split('_')[-1])
            self.jump_to_objective(obj_index)
        elif action.startswith('jump_part_'):
            part = int(action.split('_')[-1])
            self.jump_to_part(part)
        elif action.startswith('money_'):
            self.set_money_preset(action.split('_')[-1])
        elif action.startswith('health_') or action.startswith('energy_'):
            self.set_health_preset(action)
        elif action.startswith('preset_'):
            preset_name = action[7:]  # Remove 'preset_' prefix
            self.load_preset(preset_name)
        elif action == 'set_position':
            self.show_position_input()
        elif action == 'save_state':
            self.save_debug_state()
        elif action == 'load_state':
            self.load_debug_state()

    def jump_to_objective(self, obj_index: int) -> None:
        """Jump to a specific objective index"""
        obj_mgr = self.game.objective_manager
        if 0 <= obj_index < len(obj_mgr.objectives):
            obj_mgr.current_objective_index = obj_index
            obj = obj_mgr.get_current_objective()
            if obj:
                obj_mgr.show_notification(f"Jumped to: {obj.title}", (100, 255, 100))
                print(f"🎯 Jumped to objective {obj_index}: {obj.title}")
            self.update_menu_items()

    def jump_to_part(self, part: int) -> None:
        """Jump to a specific game part"""
        obj_mgr = self.game.objective_manager

        if part == 1:
            obj_mgr.skip_to_part1()
        elif part == 2:
            obj_mgr.skip_to_part2()
        elif part == 3:
            obj_mgr.skip_to_part3()

        obj_mgr.show_notification(f"Jumped to Part {part}", (100, 255, 100))
        print(f"🏆 Jumped to Part {part}")
        self.update_menu_items()

    def restart_current_objective(self) -> None:
        """Restart the current objective"""
        obj_mgr = self.game.objective_manager
        current_obj = obj_mgr.get_current_objective()

        if current_obj:
            # Reset objective state
            current_obj.completed = False

            # Clear any active activities
            if obj_mgr.current_activity:
                if hasattr(obj_mgr.current_activity, 'cleanup'):
                    obj_mgr.current_activity.cleanup()
                obj_mgr.current_activity = None

            # Exit any current interior
            if self.game.current_interior:
                self.game.current_interior = None

            obj_mgr.show_notification(f"Restarted: {current_obj.title}", (255, 255, 100))
            print(f"🔄 Restarted objective: {current_obj.title}")

    def set_money_preset(self, preset: str) -> None:
        """Set money to predefined amounts"""
        amounts = {'low': 20.0, 'medium': 100.0, 'high': 500.0}
        if preset in amounts:
            self.game.player_money = amounts[preset]
            self.game.objective_manager.show_notification(f"Money set to ${amounts[preset]}", (255, 255, 100))
            print(f"💰 Money set to ${amounts[preset]}")

    def set_health_preset(self, preset: str) -> None:
        """Set health/stress/energy presets"""
        if preset == 'health_low_stress_high':
            self.game.player_health = 30
            self.game.player_stress = 90
        elif preset == 'health_medium_stress_medium':
            self.game.player_health = 70
            self.game.player_stress = 50
        elif preset == 'health_high_stress_low':
            self.game.player_health = 100
            self.game.player_stress = 20
        elif preset == 'energy_low':
            self.game.player_energy = 25
        elif preset == 'energy_medium':
            self.game.player_energy = 60
        elif preset == 'energy_high':
            self.game.player_energy = 100

        self.game.objective_manager.show_notification("Stats updated", (255, 255, 100))
        print(f"📊 Stats updated: Health={self.game.player_health}, Stress={self.game.player_stress}, Energy={self.game.player_energy}")

    def load_preset(self, preset_name: str) -> None:
        """Load a debug preset"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'debug_config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)

            presets = config.get('presets', {})
            if preset_name in presets:
                preset = presets[preset_name]

                # Set stats if provided
                if 'stats' in preset:
                    stats = preset['stats']
                    self.game.player_money = stats.get('money', self.game.player_money)
                    self.game.player_health = stats.get('health', self.game.player_health)
                    self.game.player_stress = stats.get('stress', self.game.player_stress)
                    self.game.player_energy = stats.get('energy', self.game.player_energy)

                # Set player position if provided
                if 'player_pos' in preset:
                    x, y = preset['player_pos']
                    self.game.player.x = x
                    self.game.player.y = y
                    self.game.player.pixel_x = x * 32  # TILE_SIZE
                    self.game.player.pixel_y = y * 32
                    self.game.player.target_x = self.game.player.pixel_x
                    self.game.player.target_y = self.game.player.pixel_y
                    self.game.update_camera()

                # Jump to part/objective if provided
                if 'part' in preset:
                    obj_mgr = self.game.objective_manager
                    if preset['part'] != obj_mgr.game_part:
                        self.jump_to_part(preset['part'])

                if 'objective' in preset:
                    self.jump_to_objective_by_id(preset['objective'])

                self.game.objective_manager.show_notification(f"Preset '{preset_name}' loaded", (100, 255, 100))
                print(f"🎮 Loaded preset: {preset_name}")
                self.update_menu_items()

        except Exception as e:
            print(f"❌ Error loading preset {preset_name}: {e}")

    def jump_to_objective_by_id(self, obj_id: str) -> None:
        """Jump to objective by its ID string"""
        obj_mgr = self.game.objective_manager
        for i, obj in enumerate(obj_mgr.objectives):
            if obj.id == obj_id:
                self.jump_to_objective(i)
                return
        print(f"❌ Objective '{obj_id}' not found in current part")

    def save_debug_state(self) -> None:
        """Save current game state for debugging"""
        try:
            state = {
                'part': self.game.objective_manager.game_part,
                'objective_index': self.game.objective_manager.current_objective_index,
                'player_pos': [self.game.player.x, self.game.player.y],
                'stats': {
                    'money': self.game.player_money,
                    'health': self.game.player_health,
                    'stress': self.game.player_stress,
                    'energy': self.game.player_energy
                },
                'timestamp': pygame.time.get_ticks()
            }

            with open('debug_save_state.json', 'w') as f:
                json.dump(state, f, indent=2)

            self.game.objective_manager.show_notification("Debug state saved", (100, 255, 100))
            print("💾 Debug state saved to debug_save_state.json")

        except Exception as e:
            print(f"❌ Error saving debug state: {e}")

    def load_debug_state(self) -> None:
        """Load saved debug state"""
        try:
            with open('debug_save_state.json', 'r') as f:
                state = json.load(f)

            # Apply saved state
            if 'stats' in state:
                stats = state['stats']
                self.game.player_money = stats.get('money', self.game.player_money)
                self.game.player_health = stats.get('health', self.game.player_health)
                self.game.player_stress = stats.get('stress', self.game.player_stress)
                self.game.player_energy = stats.get('energy', self.game.player_energy)

            if 'player_pos' in state:
                x, y = state['player_pos']
                self.game.player.x = x
                self.game.player.y = y
                self.game.player.pixel_x = x * 32
                self.game.player.pixel_y = y * 32
                self.game.player.target_x = self.game.player.pixel_x
                self.game.player.target_y = self.game.player.pixel_y
                self.game.update_camera()

            if 'part' in state:
                self.jump_to_part(state['part'])

            if 'objective_index' in state:
                self.jump_to_objective(state['objective_index'])

            self.game.objective_manager.show_notification("Debug state loaded", (100, 255, 100))
            print("📂 Debug state loaded from debug_save_state.json")

        except FileNotFoundError:
            print("❌ No saved debug state found (debug_save_state.json)")
        except Exception as e:
            print(f"❌ Error loading debug state: {e}")

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the debug menu"""
        if not self.visible:
            return

        # Draw semi-transparent background overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Draw main menu background
        menu_surface = pygame.Surface((self.menu_width, self.menu_height))
        menu_surface.fill(self.bg_color[:-1])
        menu_surface.set_alpha(self.bg_color[-1])
        screen.blit(menu_surface, (self.menu_x, self.menu_y))

        # Draw border
        pygame.draw.rect(screen, self.highlight_color,
                        (self.menu_x, self.menu_y, self.menu_width, self.menu_height), 2)

        # Draw title
        title_text = self.title_font.render("🔧 DEBUG MENU", True, self.text_color)
        screen.blit(title_text, (self.menu_x + 20, self.menu_y + 10))

        # Draw current game state
        obj_mgr = self.game.objective_manager
        current_obj = obj_mgr.get_current_objective()
        state_text = f"Part {obj_mgr.game_part} | Obj {obj_mgr.current_objective_index}"
        if current_obj:
            state_text += f" | {current_obj.id}"

        state_surface = self.small_font.render(state_text, True, (200, 200, 200))
        screen.blit(state_surface, (self.menu_x + 20, self.menu_y + 40))

        # Draw menu items
        item_y = self.menu_y + 70
        max_visible_items = 12

        for i in range(min(len(self.menu_items), max_visible_items)):
            actual_index = i + self.scroll_offset
            if actual_index >= len(self.menu_items):
                break

            text, action = self.menu_items[actual_index]

            # Highlight selected item
            if actual_index == self.selected_index:
                highlight_rect = pygame.Rect(self.menu_x + 10, item_y - 5,
                                           self.menu_width - 20, 25)
                pygame.draw.rect(screen, self.highlight_color, highlight_rect)

            # Different colors for different item types
            if action == 'header':
                color = (255, 200, 100)
                font = self.font
            else:
                color = self.text_color
                font = self.small_font if len(text) > 50 else self.font

            text_surface = font.render(text[:70], True, color)
            screen.blit(text_surface, (self.menu_x + 20, item_y))
            item_y += 30

        # Draw controls help
        help_y = self.menu_y + self.menu_height - 60
        help_texts = [
            "Controls: ↑↓ Navigate | Enter: Select | F1/ESC: Close",
            "F3: Debug Panel | N: Skip Obj | P: Skip Part"
        ]

        for i, help_text in enumerate(help_texts):
            help_surface = self.small_font.render(help_text, True, (150, 150, 150))
            screen.blit(help_surface, (self.menu_x + 20, help_y + i * 20))


def apply_debug_settings(game) -> None:
    """Apply debug settings to game instance"""
    settings = get_debug_settings()

    if not settings:
        return

    print("🔧 Applying debug settings...")

    # Set player stats
    if 'stats' in settings:
        stats = settings['stats']
        if 'money' in stats:
            game.player_money = stats['money']
            print(f"💰 Money set to ${stats['money']}")
        if 'health' in stats:
            game.player_health = stats['health']
        if 'stress' in stats:
            game.player_stress = stats['stress']
        if 'energy' in stats:
            game.player_energy = stats['energy']
        print(f"📊 Stats: Health={game.player_health}, Stress={game.player_stress}, Energy={game.player_energy}")

    # Set player position
    if 'player_pos' in settings:
        x, y = settings['player_pos']
        game.player.x = x
        game.player.y = y
        game.player.pixel_x = x * 32  # TILE_SIZE from constants
        game.player.pixel_y = y * 32
        game.player.target_x = game.player.pixel_x
        game.player.target_y = game.player.pixel_y
        game.update_camera()
        print(f"📍 Player position set to ({x}, {y})")

    # Jump to specific part
    if 'part' in settings:
        part = settings['part']
        obj_mgr = game.objective_manager
        obj_mgr.game_part = part
        obj_mgr.setup_objectives()
        print(f"🏆 Jumped to Part {part}")

    # Jump to specific objective
    if 'objective' in settings:
        obj_id = settings['objective']
        obj_mgr = game.objective_manager

        # Find objective by ID
        for i, obj in enumerate(obj_mgr.objectives):
            if obj.id == obj_id:
                obj_mgr.current_objective_index = i
                print(f"🎯 Jumped to objective {i}: {obj.title}")
                break
        else:
            print(f"❌ Objective '{obj_id}' not found in Part {obj_mgr.game_part}")

    print("✅ Debug settings applied!")


# Debug utility functions

def create_debug_save(game, filename: str = "debug_quicksave.json") -> bool:
    """Create a debug save file with current game state"""
    try:
        state = {
            'part': game.objective_manager.game_part,
            'objective_index': game.objective_manager.current_objective_index,
            'current_objective_id': game.objective_manager.get_current_objective().id if game.objective_manager.get_current_objective() else None,
            'player_pos': [game.player.x, game.player.y],
            'stats': {
                'money': game.player_money,
                'health': game.player_health,
                'stress': game.player_stress,
                'energy': game.player_energy,
                'debt': game.player_debt,
                'work_ready': game.player_work_ready
            },
            'game_time': {
                'hour': game.game_hour,
                'day': getattr(game, 'current_day', 1)
            },
            'timestamp': pygame.time.get_ticks()
        }

        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"💾 Debug save created: {filename}")
        return True

    except Exception as e:
        print(f"❌ Failed to create debug save: {e}")
        return False

def load_debug_save(game, filename: str = "debug_quicksave.json") -> bool:
    """Load a debug save file"""
    try:
        with open(filename, 'r') as f:
            state = json.load(f)

        # Apply loaded state using debug settings format
        debug_settings = {
            'part': state.get('part', 1),
            'player_pos': state.get('player_pos', [25, 25]),
            'stats': state.get('stats', {})
        }

        if 'objective_index' in state:
            # Find objective by index
            obj_mgr = game.objective_manager
            if obj_mgr.game_part != state['part']:
                obj_mgr.game_part = state['part']
                obj_mgr.setup_objectives()

            if 0 <= state['objective_index'] < len(obj_mgr.objectives):
                obj_mgr.current_objective_index = state['objective_index']

        # Apply settings
        set_debug_settings(debug_settings)
        apply_debug_settings(game)

        print(f"📂 Debug save loaded: {filename}")
        return True

    except FileNotFoundError:
        print(f"❌ Debug save not found: {filename}")
        return False
    except Exception as e:
        print(f"❌ Failed to load debug save: {e}")
        return False

def print_debug_info(game) -> None:
    """Print current debug information"""
    obj_mgr = game.objective_manager
    current_obj = obj_mgr.get_current_objective()

    print("\n" + "="*60)
    print("🔍 DEBUG INFO")
    print("="*60)
    print(f"🏆 Part: {obj_mgr.game_part}")
    print(f"🎯 Objective: {obj_mgr.current_objective_index} / {len(obj_mgr.objectives) - 1}")

    if current_obj:
        print(f"📝 Current: {current_obj.id} - {current_obj.title}")
        print(f"📍 Target: {current_obj.target_position}")
        print(f"✅ Completed: {current_obj.completed}")

    print(f"👤 Player: ({game.player.x}, {game.player.y})")
    print(f"💰 Money: ${game.player_money}")
    print(f"📊 Health: {game.player_health} | Stress: {game.player_stress} | Energy: {game.player_energy}")

    if obj_mgr.current_activity:
        activity = obj_mgr.current_activity
        print(f"⚡ Activity: {activity.__class__.__name__}")
        if hasattr(activity, 'active'):
            print(f"   Active: {activity.active}")
        if hasattr(activity, 'completed'):
            print(f"   Completed: {activity.completed}")

    if game.current_interior:
        print(f"🏠 Interior: {game.current_interior.__class__.__name__}")

    print("="*60)

# Export main functions
__all__ = [
    'set_debug_settings',
    'get_debug_settings',
    'is_debug_mode',
    'DebugMenu',
    'apply_debug_settings',
    'create_debug_save',
    'load_debug_save',
    'print_debug_info'
]