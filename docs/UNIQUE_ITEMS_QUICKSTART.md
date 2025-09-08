# Unique Items System - Quick Start Guide

## Why Unique Items?
The old category system had a critical flaw: buildings with the same category but different sizes (like 4×3 store vs 4×4 store) would conflict. The unique items system solves this by giving every tile and building its own unique name.

## Step 1: Create Unique Items
```bash
python findTiles_unique.py
```

### Controls:
- **Click** on a single tile → Name it (e.g., "Grass Tile", "Road Tile")
- **Drag** to select a building area → Name it (e.g., "Pizza Shop", "Player House")
- **Tab** - Switch between sprite sheets
- **S** - Save your selections
- **H** - Toggle help
- **Mouse wheel** - Scroll view

### Naming Tips:
- Use descriptive names: "Pizza Shop Building" not just "store1"
- Include purpose: "Player Starting House" not just "house"
- Be specific: "Main Street Road Tile" not just "road"

## Step 2: Create Your Map
```bash
python mapcreator_visual.py
```

The editor automatically loads your unique items from `tile_selections_unique.json`.

### Tools:
- **T** - Place single tiles
- **B** - Place buildings
- **E** - Eraser
- **S** - Save map

### Navigation:
- **WASD/Arrows** - Move camera
- **Mouse wheel** - Zoom in/out
- **Space + drag** - Pan view
- **G** - Toggle grid

## Step 3: Load in Game
Your game (`detected_tiles.py`) automatically loads maps created with unique items.

## Example Workflow

1. **Select a pizza shop building:**
   ```
   python findTiles_unique.py
   # Drag a 4×3 area on the sprite sheet
   # Name it: "Pizza Shop Building"
   # Press S to save
   ```

2. **Place it on your map:**
   ```
   python mapcreator_visual.py
   # Press B for building tool
   # Select "Pizza Shop Building" from sidebar
   # Click to place it
   # Press S to save
   ```

3. **Run your game:**
   ```
   python detected_tiles.py
   # Your pizza shop loads correctly!
   ```

## Troubleshooting

### "No items found"
- Run `findTiles_unique.py` first to create items

### "Building doesn't appear"
- Make sure you saved (S) in both tools
- Check that `tile_selections_unique.json` exists

### "Wrong building loads"
- This shouldn't happen with unique items!
- Each building has its own unique name

## Files Created

- `tile_selections_unique.json` - Your unique item definitions
- `city_map_data.json` - Your map layout
- `city_map.png` - Visual preview (auto-generated)

## Next Steps

1. Create all the tiles and buildings you need
2. Build your city map
3. The game will load everything correctly!

Remember: The key advantage is that "Pizza Shop 4×3" and "Grocery Store 4×3" are now completely separate items that won't conflict!