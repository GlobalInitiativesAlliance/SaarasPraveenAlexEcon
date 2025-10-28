# Foster Home Narrative Integration

## How It Works

### 1. Player Approaches Foster Home
- Player walks to coordinates (29, 39) on the map
- The building is already mapped in `data/maps/building_interiors.json`
- Game shows "Press E to enter" prompt

### 2. Player Enters Building (Press E)
```python
# Main.py detects E key near building
if self.near_building_with_interior:
    building_manager.enter_building(building_pos, building_name, room_name)
    # This loads FosterHomeNarrative instead of generic interior
```

### 3. Interior Loads with Narrative
```python
# FosterHomeNarrative checks current objective
def enter(self):
    current = self.game.objective_manager.get_current_objective()
    if current.id == "housing_intro":
        # Start aging out narrative!
```

### 4. Narrative Sequence Plays
1. **Foster Parent NPC appears** with dialogue
2. **Text box appears** at bottom of screen (RPG-style)
3. **Player reads dialogue** (SPACE to continue)
4. **Interactive objects highlighted** when nearby
5. **Player packs items** (E to interact):
   - Dresser → Pack clothes
   - Desk → Grab documents
   - Nightstand → Take photo
6. **Door becomes available** after packing
7. **Final interaction** at door completes objective

### 5. Visual Experience
```
┌────────────────────────────────────┐
│ [Room with furniture and NPC]      │
│                                    │
│      Foster Parent                 │
│         👤                         │
│                                    │
│     📦 Dresser    📄 Desk         │
│                                    │
│         🚶 You                    │
├────────────────────────────────────┤
│ Foster Parent:                     │
│ "Happy 18th birthday. You know    │
│ the rules - time to pack."        │
│                    [SPACE] Continue│
└────────────────────────────────────┘
```

## Testing Instructions

### Run Standalone Test:
```bash
python3 test_foster_home.py
```

### Test in Main Game:
1. Start the game normally
2. Walk to foster home at (29, 39)
3. Press E to enter
4. Experience the narrative!

## Adding More Narrative Interiors

### Step 1: Create Narrative Class
```python
# src/interiors/narratives/grocery_store_narrative.py
class GroceryStoreNarrative(NarrativeInterior):
    def load_narrative_content(self):
        return {
            'grocery_shopping': {
                'dialogue_sequence': [...],
                'interactions': {...}
            }
        }
```

### Step 2: Update BuildingManager
```python
# src/core/building_manager.py
if room_name == "grocery_store":
    from src.interiors.narratives.grocery_store_narrative import GroceryStoreNarrative
    interior = GroceryStoreNarrative(self.game, room_data, building_pos)
```

### Step 3: Map Building Location
```json
// data/maps/building_interiors.json
{
    "39,51": "grocery_store"
}
```

## Key Components

### DialogueBox (`src/ui/dialogue_box.py`)
- Displays text at bottom of screen
- Typewriter effect
- Speaker names with color coding

### NarrativeInterior (`src/interiors/narrative_interior.py`)
- Base class for all narrative rooms
- Handles objective checking
- Manages NPCs and interactions
- Controls dialogue flow

### FosterHomeNarrative (`src/interiors/narratives/foster_home_narrative.py`)
- Specific implementation for foster home
- Tracks packing progress
- Multiple interactive objects
- Sequential narrative flow

## Benefits of This System

1. **Reusable** - One system works for all interiors
2. **Narrative-Driven** - Story guides gameplay
3. **Contextual** - Rooms change based on objectives
4. **Visual** - Professional RPG-style presentation
5. **Easy to Extend** - Just add narrative content

## Next Steps

1. ✅ Foster Home aging out sequence
2. ⬜ Housing Office application forms
3. ⬜ Grocery Store budget shopping
4. ⬜ TLP Apartment roommate interactions
5. ⬜ Classroom focus challenges
6. ⬜ Emergency Shelter intake process

Each interior becomes a meaningful part of the story!