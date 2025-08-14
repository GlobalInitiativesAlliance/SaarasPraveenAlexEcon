# Japanese Home Blocks System Guide

## ✅ Everything is Fixed!

### What's Working:
1. **No more errors** when pressing F3 or interacting
2. **Editor and game use the SAME file**: `japenese_home_blocks.json`
3. **Blocks start hidden** for immersive gameplay
4. **Collision always active** (can't walk through walls/furniture)

## 🎮 How to Use

### Step 1: Edit Blocks Visually
```bash
python tilemap_block_editor.py
```
- See the actual tilemap textures
- Click to add/remove blocks:
  - **RED** = Walls (can't walk through)
  - **ORANGE** = Furniture (can't walk through)  
  - **GREEN** = Interaction zones (press E here)
- **Press S to save** → Updates `japenese_home_blocks.json`

### Step 2: Play the Game
```bash
python main.py
```
- Game **automatically loads** from `japenese_home_blocks.json`
- Blocks are **hidden by default**
- **F3** toggles block visibility (prints to console)
- **Ctrl+R** reloads blocks if you edit while playing

## 📁 The Shared File

Both editor and game use: **`japenese_home_blocks.json`**

This file contains:
```json
{
  "room_name": "japenese_home",
  "walls": [[x,y], [x,y], ...],      // Red blocks
  "furniture": [[x,y], [x,y], ...],  // Orange blocks
  "interactions": [[x,y], [x,y], ...] // Green blocks
}
```

## 🔧 Key Features

1. **Visual Feedback**
   - F3 shows/hides blocks
   - Console prints: "Debug blocks: ON/OFF"

2. **Collision System**
   - Always active (visible or not)
   - Can't walk through walls/furniture
   - Can walk through interaction zones

3. **Auto-Loading**
   - No manual steps needed
   - Edit → Save → Play

## 🎯 Workflow

1. Run editor: `python tilemap_block_editor.py`
2. Make changes visually
3. Press S to save
4. Changes immediately available in game!

## 📝 Console Messages

When playing, you'll see:
- "Debug blocks: ON/OFF" when pressing F3
- "Interaction: [message]" when pressing E in green zones
- "Reloaded blocks from file" when pressing Ctrl+R

That's it! The system is fully automatic and error-free.