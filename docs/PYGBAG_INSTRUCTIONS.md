# Running the Game on Web with Pygbag

## Installation

First, install Pygbag:
```bash
pip install pygbag
```

## Running the Game

1. Navigate to your project directory:
```bash
cd /Users/praveenvadlamani/SaarasPraveenAlexEcon
```

2. Run Pygbag:
```bash
pygbag main.py
```

3. Open your browser and go to:
```
http://localhost:8000
```

## Important Notes

- The game will take a moment to load in the browser
- Make sure all your game assets (images, JSON files) are in the same directory
- The web version uses WebAssembly, so performance may vary
- Browser console (F12) can help debug any issues

## Building for Distribution

To create a distributable web build:
```bash
pygbag --build main.py
```

This will create a `build` directory with all files needed for web hosting.

## Troubleshooting

- If you see file loading errors, ensure all paths are relative
- For better performance, consider reducing screen resolution in constants.py
- Clear browser cache if you make changes and they don't appear