# Economics Adventure

An educational game teaching economics through interactive city exploration and mini-games.

## Overview

Economics Adventure is a Python-based educational game where players navigate through economic challenges as a young person in the city. The game combines exploration, decision-making, and mini-games to teach concepts like budgeting, work, financial literacy, and life skills.

## Features

- **Interactive City Exploration**: Navigate through a detailed city map with various buildings and locations
- **Multiple Interior Environments**: Enter buildings like homes, workplaces, schools, and community centers
- **Educational Mini-Games**: Learn through interactive activities like pizza making, burger cooking, shopping, and more
- **Progressive Storyline**: Follow a two-part narrative that teaches real-world economic concepts
- **Life Skills Workshops**: Participate in workshops covering topics like tenant rights and financial planning

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd SaarasPraveenAlexEcon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python run_game.py
```

## How to Play

### Controls

- **WASD/Arrow Keys**: Move your character
- **E**: Interact with buildings and objects
- **G**: Toggle grid view
- **ESC**: Exit buildings / Return to menu
- **F12**: Take screenshot
- **N**: Skip current objective (debug)
- **P**: Skip to Part 2 (debug)

### Gameplay

1. Start from the main menu
2. Follow the objectives displayed at the top of the screen
3. Navigate to highlighted locations on the map
4. Enter buildings and complete activities
5. Make economic decisions that affect your progress
6. Learn about work, budgeting, and financial independence

## Project Structure

```
SaarasPraveenAlexEcon/
├── src/                    # Main source code
│   ├── main.py            # Game entry point
│   ├── constants.py       # Game constants
│   ├── core/              # Core game systems
│   ├── interiors/         # Building interiors
│   ├── activities/        # Mini-games and activities
│   └── utils/             # Utility modules
├── data/                  # Game data files
│   ├── maps/              # Map data
│   ├── interiors/         # Interior configurations
│   └── tiles/             # Tile definitions
├── assets/                # Game assets
│   ├── images/            # Image files
│   └── Top-Down_Retro_Interior/  # Tileset assets
├── tools/                 # Development tools
├── docs/                  # Documentation
└── run_game.py           # Main entry point
```

## Development

### Adding New Features

1. **New Interiors**: Create a class inheriting from `BaseInterior` in `src/interiors/`
2. **New Activities**: Add to `src/activities/` following the activity pattern
3. **New Objectives**: Modify the objective system in `src/core/game_world.py`

### Tools

The project includes several development tools in the `tools/` directory:

- **Interior Room Builder**: Visual editor for creating room layouts
- **Tilemap Block Editor**: Tool for editing tilemap blocks
- **Map Creator**: Visual map creation tool

Run tools from the project root:
```bash
python tools/editors/interior_room_builder.py
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- `FILE_ORGANIZATION_PLAN.md`: Project structure details
- `OBJECTIVES_BUILDING_CONNECTION.md`: Objective system documentation
- `PYGBAG_INSTRUCTIONS.md`: Web deployment guide
- `UNIQUE_ITEMS_QUICKSTART.md`: Item system guide

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This is an educational project created for teaching economics concepts through interactive gameplay.

## Credits

Created for economics education, combining game development with financial literacy.
