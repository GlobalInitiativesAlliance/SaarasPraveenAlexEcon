# GameObjective Implementation Guide

This comprehensive guide provides a systematic approach for implementing new GameObjectives with high-quality visuals and proper integration.

## 📋 Claude Prompting Checklist

### Phase 1: Analysis and Setup
Use this exact prompt structure with Claude:

```
I need to implement this GameObjective:

GameObjective(
    "work_performance",
    "Work Performance",
    "If breathing failed: Burn a burger and get manager warning",
    (39, 51),  # Workplace
    "Press E to continue"
)

Please analyze:
1. What type of scene this needs (interior narrative, activity mini-game, or both)
2. Which existing interior files I should examine for patterns
3. What visual elements would enhance the narrative
4. If this location coordinate matches building_interiors.json correctly
```

### Phase 2: Scene Implementation
```
Based on the analysis, please implement:
1. Create/modify the narrative interior file for this objective
2. Add appropriate NPCs with positions and sprite IDs
3. Design interactive objects with clear visual feedback
4. Implement dialogue sequences that match the objective's theme
5. Add atmospheric elements (lighting, colors, UI indicators)
```

### Phase 3: Integration and Polish
```
Please ensure:
1. The objective completion logic works correctly
2. Visual transitions are smooth
3. The scene connects properly to the next objective
4. Debug logging shows the correct flow
5. Error handling prevents crashes
```

## 🏗️ Technical Implementation Structure

### 1. File Organization
- **Narrative Interior**: `/src/interiors/narratives/{location}_narrative.py`
- **Activity Mini-games**: `/src/activities/{activity_name}.py`
- **Room Data**: `/data/interiors/rooms/{location}.json`
- **Building Mapping**: `/data/maps/building_interiors.json`

### 2. Interior Class Template
```python
class WorkplaceNarrative(NarrativeInterior):
    """Workplace interior for work performance objectives"""

    def __init__(self, game, room_data, building_pos):
        # Initialize attributes BEFORE super().__init__()
        self.work_stress = 0
        self.manager_warnings = 0
        self.breathing_activity_complete = False

        super().__init__(game, room_data, building_pos)

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'work_performance': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5},
                    {'name': 'Coworker', 'x': 6, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Manager", "Your anxiety is affecting your work quality."),
                    ("You", "I'm trying my best..."),
                    (None, "The smell of burnt food fills the air.")
                ],
                'interactions': {
                    'cash_register': {
                        'position': (8, 6),
                        'prompt': 'Try to work normally',
                        'trigger_activity': 'anxiety_work_simulation',
                        'dialogue': None,
                        'required': True
                    }
                }
            }
        }

    def enter(self):
        """Set up the workplace based on current objective"""
        super().enter()

        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'work_performance':
            # Add interactions for this specific objective
            interactions = self.narrative_content['work_performance']['interactions']
            for obj_name, obj_data in interactions.items():
                self.add_interactive_object(obj_name, obj_data)
            # Start narrative sequence
            self.start_narrative_sequence('work_performance')
```

### 3. Visual Enhancement Patterns

#### Atmospheric Effects
```python
def draw(self, screen):
    """Draw with atmospheric enhancements"""
    super().draw(screen)

    # Stress-based color overlay
    if self.work_stress > 50:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(30)
        overlay.fill((255, 100, 100))  # Red tint for stress
        screen.blit(overlay, (0, 0))

    # Interactive object highlights
    self.draw_interaction_highlights(screen)

    # Status display
    self.draw_stress_meter(screen)
```

#### Interactive Object Highlights
```python
def draw_interaction_highlights(self, screen):
    """Draw glowing highlights on interaction points"""
    for interaction_key, interaction in self.current_interactions.items():
        if interaction.get('required', False):
            pos = interaction.get('position')
            if pos:
                # Pulsing glow effect
                pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.3 + 0.7
                glow_alpha = int(100 * pulse)

                # Draw highlight
                x = offset_x + pos[0] * TILE_SIZE
                y = offset_y + pos[1] * TILE_SIZE
                pygame.draw.circle(screen, (100, 255, 100, glow_alpha),
                                 (x + TILE_SIZE//2, y + TILE_SIZE//2),
                                 TILE_SIZE//2 + 10)
```

### 4. Activity Integration
```python
def launch_anxiety_work_simulation(self):
    """Launch workplace anxiety mini-game"""
    from src.activities.anxiety_work_simulation import AnxietyWorkSimulation

    # Clear dialogue
    if hasattr(self, 'dialogue_box'):
        self.dialogue_box.hide()

    # Create activity
    activity = AnxietyWorkSimulation(self.game)
    activity.narrative_ref = self
    activity.start()

    # Set in objective manager (single source of truth)
    if hasattr(self.game, 'objective_manager'):
        self.game.objective_manager.current_activity = activity
```

## 🎨 Visual Quality Guidelines

### 1. Color Schemes by Scene Type
- **Stress/Anxiety**: Red tints (255, 100, 100)
- **Hope/Relief**: Green tints (100, 255, 100)
- **Neutral/Calm**: Blue tints (100, 150, 255)
- **Depression/Despair**: Gray overlays (100, 100, 100)

### 2. NPC Placement Rules
- **Authority figures**: Center back (x: 8-12, y: 3-5)
- **Peers/Friends**: Side positions (x: 4-6, y: 6-8)
- **Background characters**: Corners (x: 2-3, y: 8-10)

### 3. Interactive Object Design
```python
interaction_template = {
    'position': (x, y),          # Tile coordinates
    'prompt': 'Action text',     # Clear, concise action
    'dialogue': [list],          # Optional immediate dialogue
    'trigger_activity': str,     # Optional mini-game trigger
    'required': bool,            # For objective progression
    'visual_feedback': dict      # Custom visual indicators
}
```

## 🔄 Testing and Validation

### Quick Test Script Template
```python
# Test new objective implementation
PYTHONPATH=/path/to/project python3 -c "
# Test objective loading
from part_1_housing_stability.objectives_narrative import OBJECTIVES
target_obj = next((obj for obj in OBJECTIVES if obj.id == 'work_performance'), None)
if target_obj:
    print(f'✅ Objective found: {target_obj.title}')
    print(f'    Location: {target_obj.location}')
    print(f'    Description: {target_obj.description}')
else:
    print('❌ Objective not found')

# Test building mapping
import json
with open('data/maps/building_interiors.json', 'r') as f:
    mappings = json.load(f)
pos_key = f'{target_obj.location[0]},{target_obj.location[1]}'
if pos_key in mappings:
    print(f'✅ Building mapping found: {mappings[pos_key]}')
else:
    print(f'❌ No building mapping for {pos_key}')
"
```

## 📝 Common Bug Patterns and Fixes

### 1. Coordinate Mismatch
**Problem**: Objective uses (30,11) but building_interiors.json maps (31,11)
**Fix**: Update coordinates to match between objective and building mapping

### 2. Missing Room Data
**Problem**: Interior loads but has no tiles/furniture
**Fix**: Ensure room JSON file exists and has proper structure

### 3. Activity Not Triggering
**Problem**: Interactive object doesn't launch mini-game
**Fix**: Check `trigger_activity` matches activity import name

### 4. Wrong Interior Type
**Problem**: Wrong scene loads for objective (classroom vs emergency shelter)
**Fix**: Verify building_manager.py routing logic

## 🚀 Advanced Features

### 1. Dynamic NPCs
```python
# NPCs that react to player state
def update_npc_behavior(self, dt):
    if self.work_stress > 70:
        self.animated_npcs['Manager']['dialogue'] = "You need to calm down!"
    elif self.work_stress < 30:
        self.animated_npcs['Manager']['dialogue'] = "Good job today."
```

### 2. Progressive Difficulty
```python
# Objectives that get harder over time
def adjust_difficulty(self):
    attempts = getattr(self, 'attempts', 0)
    if attempts > 3:
        self.time_pressure += 10  # Make it harder
        self.success_threshold += 5
```

### 3. Narrative Branching
```python
# Different outcomes based on player choices
def check_objective_complete(self):
    if self.breathing_activity_complete:
        return 'breathing_success'
    else:
        return 'breathing_failure'  # Leads to manager warning
```

## 🎯 Success Metrics
- ✅ Objective loads without errors
- ✅ Visual scene renders correctly
- ✅ Interactive objects respond properly
- ✅ Activity mini-games trigger and complete
- ✅ Transitions to next objective work smoothly
- ✅ No console errors or warnings
- ✅ Performance remains smooth (60 FPS)

## 📚 Reference Examples
- **Complex Interior**: `/src/interiors/narratives/emergency_shelter_narrative.py`
- **Activity Integration**: `/src/interiors/narratives/grocery_store_narrative.py`
- **Visual Effects**: `/src/interiors/narratives/sarahs_place_narrative.py`
- **State Management**: `/src/interiors/narrative_interior.py`

## 🎮 Final Testing Protocol
1. Run objective in isolation
2. Test full scenario flow from previous objective
3. Verify visual quality and performance
4. Check edge cases and error handling
5. Validate completion triggers next objective
6. Document any special behavior or requirements

This guide ensures consistent, high-quality implementation of GameObjectives with robust visual presentation and reliable functionality.