# Quick Building Blending Guide

## You Already Have Transition Tiles! 

Your current tiles are perfect for blending:
- `grass` - Full grass (center)
- `left_grass`, `right_grass`, `top_grass` - Edge transitions
- `side_left_grass`, `side_right_grass`, `side_down_grass` - More edges
- `left_down_grass`, `bottom_right_grass` - Corner transitions

## How to Use Them

### Around a 3×3 Building:
```
Before (harsh edges):
G G G G G
G B B B G    G = grass (full green)
G B B B G    B = building
G B B B G
G G G G G

After (with transitions):
G T T T G
L B B B R    T = top_grass (grass with dirt on top)
L B B B R    L = left_grass (grass with dirt on left)
L B B B R    R = right_grass (grass with dirt on right)
G D D D G    D = side_down_grass (grass with dirt below)
```

### Step-by-Step in mapcreator_visual.py:

1. **Place your building**
2. **Use transition tiles around it**:
   - Above building: Use `side_down_grass` (dirt bottom, grass top)
   - Below building: Use `top_grass` (dirt top, grass bottom)
   - Left of building: Use `right_grass` (dirt right, grass left)
   - Right of building: Use `left_grass` (dirt left, grass right)
   - Corners: Use corner tiles like `left_down_grass`

## Quick Tips:
- The transition tiles create a "worn path" effect around buildings
- This makes it look like people walk around the building
- Much more natural than sharp grass-to-building edges

## Even Better:
Add some dirt or path tiles (if you have them) directly adjacent to the building, THEN use the transition tiles to blend back to grass:

```
G G G T T T G G
G L D D D D R G
G L D B B B D R
G L D B B B D R
G L D B B B D R
G G G D D D G G

G = full grass
T/L/R/D = transition tiles
D = dirt/path
B = building
```

This creates a natural progression: Grass → Transition → Dirt → Building