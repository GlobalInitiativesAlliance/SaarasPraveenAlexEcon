# Economics Adventure - File Organization Plan

## Proposed Directory Structure

```
SaarasPraveenAlexEcon/
│
├── README.md                      # Project overview and setup instructions
├── requirements.txt               # Python dependencies
├── .gitignore                    # Git ignore file
│
├── src/                          # Main source code directory
│   ├── __init__.py
│   ├── main.py                   # Game entry point
│   ├── constants.py              # Game constants and configuration
│   │
│   ├── core/                     # Core game systems
│   │   ├── __init__.py
│   │   ├── game_world.py         # World management, objectives
│   │   ├── main_menu.py          # Main menu system
│   │   └── player.py             # Player class and animation (from playerAnimate.py)
│   │
│   ├── interiors/                # All interior building implementations
│   │   ├── __init__.py
│   │   ├── base_interior.py      # Base interior class
│   │   ├── building_manager.py   # Interior building management (from building_interiors.py)
│   │   │
│   │   ├── residential/          # Residential buildings
│   │   │   ├── __init__.py
│   │   │   ├── home_interior.py
│   │   │   ├── foster_home_interior.py
│   │   │   ├── japanese_home_interior.py  # (from japanese_home_auto.py)
│   │   │   └── tlp_apartment_interior.py
│   │   │
│   │   ├── commercial/           # Commercial buildings
│   │   │   ├── __init__.py
│   │   │   ├── pizzaplace_interior.py
│   │   │   ├── burgerplace_interior.py
│   │   │   └── grocery_store_interior.py
│   │   │
│   │   └── public/               # Public buildings
│   │       ├── __init__.py
│   │       ├── classroom_interior.py
│   │       ├── community_center_interior.py
│   │       └── housing_office_interior.py
│   │
│   ├── activities/               # Activities and minigames
│   │   ├── __init__.py
│   │   ├── base_activity.py      # Base activity class (extract from activities.py)
│   │   ├── activities.py         # All activity implementations
│   │   ├── minigames.py          # All minigame implementations
│   │   │
│   │   └── work/                 # Work-related activities
│   │       ├── __init__.py
│   │       ├── pizza_activity.py
│   │       └── burger_activity.py
│   │
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       └── building_definitions.py
│
├── data/                         # Game data files
│   ├── maps/                     # Map data
│   │   ├── city_map_data.json
│   │   ├── city_map_data.cmap
│   │   ├── city_map_data.cmap.gz
│   │   └── city_map_mini.txt
│   │
│   ├── interiors/                # Interior configuration
│   │   ├── interior_rooms.json
│   │   ├── interior_themes.json
│   │   └── japenese_home_blocks.json
│   │
│   └── tiles/                    # Tile configuration
│       └── tile_selections_unique.json
│
├── assets/                       # Game assets (textures already organized)
│   ├── images/
│   ├── Top-Down_Retro_Interior/
│   ├── moderninteriors-win/
│   └── city_map.png
│
├── tools/                        # Development tools
│   ├── __init__.py
│   ├── editors/                  # Editor tools
│   │   ├── __init__.py
│   │   ├── interior_room_builder.py
│   │   ├── tilemap_block_editor.py
│   │   ├── interior_theme_editor.py
│   │   └── mapcreator_visual.py
│   │
│   └── analysis/                 # Analysis tools
│       ├── __init__.py
│       ├── analyze_rooms.py
│       ├── findTiles_unique.py
│       └── detected_tiles_old.py  # (from detected_tiles(OLD).py)
│
├── docs/                         # Documentation
│   ├── BLOCKS_SYSTEM_GUIDE.md
│   ├── OBJECTIVES_BUILDING_CONNECTION.md
│   ├── PYGBAG_INSTRUCTIONS.md
│   ├── QUICK_BLENDING_GUIDE.md
│   ├── UNIQUE_ITEMS_QUICKSTART.md
│   └── UNIQUE_ITEMS_STATUS.md
│
├── web/                          # Web deployment files
│   └── index.html
│
├── tests/                        # Test files (to be created)
│   ├── __init__.py
│   └── test_activities.py
│
├── backups/                      # Backup files
│   └── interior_rooms_backup.json
│
└── logs/                         # Log files
    └── pygbag.log
```

## Migration Steps

### Phase 1: Create Directory Structure
```bash
# Create main directories
mkdir -p src/{core,interiors/{residential,commercial,public},activities/work,utils}
mkdir -p data/{maps,interiors,tiles}
mkdir -p tools/{editors,analysis}
mkdir -p {docs,web,tests,backups,logs}
```

### Phase 2: Move Files (Suggested Commands)
```bash
# Core files
mv main.py constants.py src/
mv main_menu.py game_world.py src/core/
mv playerAnimate.py src/core/player.py

# Interior files
mv base_interior.py src/interiors/
mv building_interiors.py src/interiors/building_manager.py

# Residential interiors
mv home_interior.py foster_home_interior.py tlp_apartment_interior.py src/interiors/residential/
mv japanese_home_auto.py src/interiors/residential/japanese_home_interior.py

# Commercial interiors
mv pizzaplace_interior.py burgerplace_interior.py grocery_store_interior.py src/interiors/commercial/

# Public interiors
mv classroom_interior.py community_center_interior.py housing_office_interior.py src/interiors/public/

# Activities
mv activities.py minigames.py src/activities/
mv pizza_activity.py burger_activity.py src/activities/work/

# Utils
mv building_definitions.py src/utils/

# Data files
mv city_map_data.* data/maps/
mv city_map_mini.txt data/maps/
mv interior_*.json data/interiors/
mv japenese_home_blocks.json data/interiors/
mv tile_selections_unique.json data/tiles/

# Tools
mv interior_room_builder.py tilemap_block_editor.py interior_theme_editor.py mapcreator_visual.py tools/editors/
mv analyze_rooms.py findTiles_unique.py tools/analysis/
mv "detected_tiles(OLD).py" tools/analysis/detected_tiles_old.py

# Documentation
mv *.md docs/

# Web files
mv index.html web/

# Logs and backups
mv pygbag.log logs/
mv interior_rooms_backup.json backups/
```

### Phase 3: Update Import Statements

After moving files, you'll need to update all import statements. For example:

**Old:**
```python
from constants import *
from home_interior import HomeInterior
```

**New:**
```python
from src.constants import *
from src.interiors.residential.home_interior import HomeInterior
```

### Phase 4: Create __init__.py Files

Each directory needs an `__init__.py` file to be recognized as a Python package:

```python
# src/__init__.py
"""Economics Adventure Game - Main Package"""

# src/interiors/__init__.py
"""Interior building implementations"""

# src/activities/__init__.py
"""Game activities and minigames"""
```

### Phase 5: Create Setup Files

**requirements.txt:**
```
pygame==2.6.1
# Add other dependencies
```

**README.md:**
```markdown
# Economics Adventure

An educational game teaching economics through city life simulation.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the game: `python src/main.py`

## Project Structure
See FILE_ORGANIZATION_PLAN.md for detailed structure.
```

**.gitignore:**
```
__pycache__/
*.pyc
*.pyo
.DS_Store
logs/
backups/
*.log
build/
dist/
```

## Benefits of This Organization

1. **Clear Separation of Concerns**: Each module type has its own directory
2. **Scalability**: Easy to add new interiors, activities, or tools
3. **Maintainability**: Related files are grouped together
4. **Import Clarity**: Clear import paths show relationships
5. **Tool Isolation**: Development tools separated from game code
6. **Data Management**: All game data in one place
7. **Version Control**: Better git history with organized structure

## Additional Recommendations

1. **Use relative imports** within packages for better portability
2. **Create a main entry point** at project root:
   ```python
   # run_game.py (at root)
   from src.main import main
   if __name__ == "__main__":
       main()
   ```

3. **Consider using a build system** like setuptools for distribution
4. **Add type hints** to improve code clarity
5. **Create unit tests** in the tests directory

This organization will make your project much more professional and easier to maintain!