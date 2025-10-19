# Objectives Connected to Map Buildings

## What Was Fixed

The timeline and objectives in detected_tiles.py now properly connect to actual buildings on your custom map!

## Key Improvements

### 1. **Building Detection Enhanced**
- Now detects both regular buildings AND buildings with backgrounds (`building_with_bg`)
- Searches for specific building types: school, pizza, apartment, office, grocery
- Falls back to generic building types if specific ones aren't found

### 2. **Smart Building Assignment**

#### Part 1 (Employment Story):
- **School**: Looks for buildings with "school" in name, then any "building"
- **Workplace**: Prefers "pizza" buildings, then "store" buildings
- **Home**: Looks for "house" or "apartment" buildings
- **Jobs Center**: Prefers "office" buildings, then other buildings

#### Part 2 (Housing Crisis):
- **Foster Home**: Uses "house" buildings
- **TLP Apartment**: Prefers "apartment" buildings, then houses
- **Community Center**: Looks for "office" or "bank" buildings
- **Housing Office**: Uses different building from community center
- **Grocery Store**: Prefers "grocery" buildings, then stores

### 3. **Fallback System**
- If specific building types aren't found, uses generic buildings
- Ensures every objective has a position, even on sparse maps
- Prints debug info showing which buildings were found and assigned

### 4. **Debug Output**
When the game starts, you'll see:
```
Found buildings on map:
  house: 5 buildings
  store: 3 buildings
  building: 8 buildings
  ...
  School at: (10, 15)
  Workplace at: (25, 30)
  Home at: (5, 8)
  ...
```

## How to Name Buildings for Best Results

When creating your map in mapcreator_visual.py, name buildings like:
- `school_main`, `highschool_1` → Will be used for school objectives
- `pizza_shop`, `pizza_place` → Will be workplace in Part 1
- `apartment_complex`, `apartment_1` → Will be TLP apartment
- `grocery_store`, `grocery_mart` → Will be grocery shopping location
- `office_building`, `office_1` → Will be jobs center/offices
- `house_blue`, `house_residential` → Will be homes

## Testing

1. Create your map with appropriately named buildings
2. Run `python detected_tiles.py`
3. Watch the console for building assignment messages
4. Follow the yellow markers to each objective location!

The game now intelligently assigns objectives to appropriate buildings based on their names!