# Professional UI components for the game
try:
    from .professional_ui import ProfessionalObjectiveUI, InteractionPrompt, NotificationToast
    from .ui_manager import GameUIManager
    __all__ = ['ProfessionalObjectiveUI', 'InteractionPrompt', 'NotificationToast', 'GameUIManager']
except ImportError:
    # Fallback to previous UI systems
    from .modern_objective_ui import ModernObjectiveUI, UITheme
    from .objective_ui_integration import ObjectiveUIManager
    __all__ = ['ModernObjectiveUI', 'UITheme', 'ObjectiveUIManager']

# Activity UI Framework - dynamic sizing for mini-games
from .activity_ui_base import (
    ActivityUIBase,
    UIColors,
    UIMetrics,
    UIFonts,
    UIHelpers,
    Align,
    get_ui
)
__all__.extend([
    'ActivityUIBase', 'UIColors', 'UIMetrics', 'UIFonts',
    'UIHelpers', 'Align', 'get_ui'
])