# Testing Foster Home Narrative

## Quick Test
Run the standalone test to see the narrative system in action:
```bash
python3 test_foster_home.py
```

## Full Game Test

### 1. Start the Game
```bash
python3 main.py
```

### 2. Navigate to Foster Home
- The foster home is at coordinates (29, 39)
- Walk there using arrow keys or WASD
- You'll see "Press E to enter" when nearby

### 3. Experience the Narrative
- **Press E** to enter the foster home
- **Watch** the foster parent NPC appear
- **Read** the dialogue (SPACE to continue)
- **Move around** the room
- **Interact** with objects when prompted:
  - Dresser (Pack clothes)
  - Desk (Grab documents)
  - Nightstand (Take photo)
- **Complete** packing to unlock the door
- **Exit** to complete the objective

### 4. Controls
- **Arrow Keys/WASD**: Move
- **E**: Interact with objects/enter buildings
- **SPACE**: Continue dialogue
- **ESC**: Exit interior/return to menu

## What You Should See

1. **Dialogue Box**: Professional RPG-style text at bottom
2. **NPCs**: Foster parent appears in room
3. **Interactive Prompts**: "[E] Pack clothes" when near objects
4. **Progress Tracking**: Checklist of packed items
5. **Emotional Narrative**: Story unfolds through interactions

## Troubleshooting

### If the narrative doesn't start:
- Make sure you're at the right objective ("housing_intro")
- Check that you entered at coordinates (29, 39)

### If you get stuck:
- Press ESC to exit the interior
- The game auto-saves your progress

## Success Indicators
✅ Dialogue box appears with foster parent text
✅ Can interact with dresser, desk, nightstand
✅ Packing progress shows in corner
✅ Door becomes available after packing all items
✅ Objective completes when leaving

## Next Steps
Once this works, the same system can be applied to:
- Housing Office (application forms)
- Grocery Store (budget shopping)
- TLP Apartment (roommate interactions)
- Any other interior that needs narrative!