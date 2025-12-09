# Debug System - Economics Adventure Game

This debug system allows you to quickly test specific game objectives, scenes, and scenarios without having to play through the entire game. Perfect for development, testing, and debugging.

## 🚀 Quick Start

### Launch with Debug Presets
```bash
# Test mailbox sorting mini-game
python debug_launcher.py --preset test_mailbox

# Test clinic checklist and forms
python debug_launcher.py --preset test_clinic

# Test breathing exercise at work
python debug_launcher.py --preset test_breathing

# Test pharmacy medication selection
python debug_launcher.py --preset test_pharmacy
```

### Launch at Specific Objectives
```bash
# Jump to specific objective by ID
python debug_launcher.py --objective check_mailbox

# Jump to specific game part
python debug_launcher.py --part 2

# Combine part and objective
python debug_launcher.py --part 2 --objective clinic_checklist
```

### Set Custom Parameters
```bash
# Set player position
python debug_launcher.py --player-pos 54 33

# Set starting money
python debug_launcher.py --money 500

# Combine multiple settings
python debug_launcher.py --preset test_clinic --money 25
```

## 🎮 Runtime Debug Controls

### Keyboard Shortcuts
- **F1** - Toggle Debug Menu (main interface)
- **F3** - Toggle Debug Panel (technical info)
- **N** - Skip to next objective
- **P** - Skip to next part
- **Ctrl+ESC** - Emergency exit from rooms
- **Ctrl+F5** - Force complete stuck activities

### Debug Menu (F1)
The debug menu provides a full interface for:
- **📋 Jump to Objective** - List and select any objective
- **📊 Modify Stats** - Change money, health, stress, energy
- **🎮 Load Preset** - Apply predefined test scenarios
- **⏭️ Skip Current Objective** - Move to next objective
- **🔄 Restart Current Objective** - Reset current objective
- **📍 Set Player Position** - Move player to specific coordinates
- **🏠 Part Navigation** - Jump between game parts
- **💾 Save/Load Debug State** - Save current game state for later

## 📋 Available Presets

### Part 1 - Housing Stability
- `part1_start` - Beginning of Part 1
- `part1_workplace` - Workplace application scenario
- `part1_pizza_work` - Pizza place work scenario

### Part 2 - Healthcare Access
- `part2_start` - Beginning of Part 2
- `test_mailbox` - Mailbox sorting mini-game
- `test_clinic` - Clinic forms and checklist
- `test_breathing` - Workplace breathing exercise
- `test_pharmacy` - Pharmacy medication selection
- `test_bus_route` - Bus route selection game
- `test_medicaid_notice` - Medicaid termination notice
- `test_therapy_decision` - Therapy payment decision
- `test_foster_application` - Foster youth application

### Special Test Scenarios
- `low_money_crisis` - Test low money scenarios ($15)
- `high_stress_test` - Test high stress scenarios (100% stress)
- `endgame_test` - Test near end-game scenarios

## 🔧 Configuration

### Debug Config File (`debug_config.json`)
The configuration file contains:

```json
{
  "debug_mode": true,
  "show_all_objectives": true,
  "instant_transitions": false,
  "presets": {
    "preset_name": {
      "description": "What this preset tests",
      "part": 2,
      "objective": "objective_id",
      "player_pos": [x, y],
      "stats": {
        "money": 100.0,
        "health": 80,
        "stress": 50,
        "energy": 70
      }
    }
  }
}
```

### Creating Custom Presets
1. Edit `debug_config.json`
2. Add your preset under the `"presets"` section
3. Use `python debug_launcher.py --list-presets` to verify

## 📖 Usage Examples

### Testing Specific Game Flows

#### Test Mailbox Interaction
```bash
python debug_launcher.py --preset test_mailbox
```
- Starts at apartment with mailbox nearby
- Player has moderate stats
- Ready to test mailbox sorting mini-game

#### Test Low Money Scenarios
```bash
python debug_launcher.py --preset low_money_crisis
```
- Sets money to $15
- Places player in therapy decision scenario
- Tests how player handles expensive options

#### Test Clinic Navigation
```bash
python debug_launcher.py --preset test_clinic
```
- Starts at clinic entrance
- Player has required documents
- Ready to test clinic checklist and forms

#### Custom Testing Setup
```bash
# Test breathing exercise with high stress
python debug_launcher.py --objective breathing_exercise --money 50
# Then modify stress in debug menu (F1)
```

### Quick Part Navigation

#### Jump to Part 2 Healthcare
```bash
python debug_launcher.py --part 2
```

#### Start Part 2 at Specific Objective
```bash
python debug_launcher.py --part 2 --objective clinic_checklist
```

### Development Workflow

#### Save Your Progress
1. Press F1 to open debug menu
2. Select "💾 Save Debug State"
3. State saved to `debug_save_state.json`

#### Load Saved State
1. Press F1 to open debug menu
2. Select "📂 Load Debug State"
3. Or use: `python debug_launcher.py` + F1 + Load State

#### Quick Objective Testing
1. Launch with preset: `python debug_launcher.py --preset test_clinic`
2. Test the scenario
3. Press N to skip to next objective if needed
4. Press F1 → "🔄 Restart Current Objective" to test again

## 🐛 Debugging Common Issues

### Player Gets Stuck
```bash
# Emergency exit
Ctrl+ESC

# Or force complete stuck activities
Ctrl+F5

# Or restart objective via debug menu
F1 → "🔄 Restart Current Objective"
```

### Wrong Game State
```bash
# Check current state
F3 (Debug Panel)

# Jump to correct part
F1 → "🏠 Part X"

# Or restart with preset
python debug_launcher.py --preset part2_start
```

### Activity Not Triggering
```bash
# Check debug info
F3 (Debug Panel)

# Force skip problematic objective
N (Skip Objective)

# Or restart objective
F1 → "🔄 Restart Current Objective"
```

## 📝 Command Line Reference

### List Commands
```bash
python debug_launcher.py --list-objectives  # Show all objectives
python debug_launcher.py --list-presets    # Show all presets
```

### Launching Options
```bash
python debug_launcher.py [OPTIONS]

Options:
  --objective, -o ID    Start at specific objective
  --part, -p PART      Start at specific game part (1-6)
  --preset NAME        Use debug preset
  --player-pos X Y     Set player position
  --money AMOUNT       Set starting money
  --debug-menu         Show debug menu at startup
  --list-objectives    List all objectives and exit
  --list-presets       List all presets and exit
```

### Examples
```bash
# Basic preset
python debug_launcher.py --preset test_clinic

# Custom objective with money
python debug_launcher.py --objective breathing_exercise --money 25

# Specific position and part
python debug_launcher.py --part 2 --player-pos 34 31

# Show debug menu immediately
python debug_launcher.py --debug-menu
```

## 🎯 Testing Workflows

### New Feature Testing
1. Create preset for your feature's starting state
2. Launch with preset: `python debug_launcher.py --preset my_feature`
3. Test the feature
4. Use debug menu to modify variables and retest
5. Save successful states for regression testing

### Bug Reproduction
1. Use preset closest to bug scenario
2. Modify stats/position as needed via debug menu
3. Reproduce the bug
4. Save the problematic state for later analysis
5. Test fixes with same saved state

### Regression Testing
1. Create presets for critical game paths
2. Test each preset after changes
3. Use saved states to verify fixes don't break other features

## 🚨 Important Notes

- **Always test in debug mode first** - Don't modify production saves
- **Save debug states** - Before testing major changes
- **Use emergency exits** - Ctrl+ESC if you get completely stuck
- **Check debug panel** - F3 shows technical game state info
- **Presets override individual settings** - Use presets for consistent testing

## 🔄 Normal Game Launch

To launch the game normally (without debug features):
```bash
python run_game.py
# or
python src/main.py
```

---

Happy debugging! 🎮✨