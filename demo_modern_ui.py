#!/usr/bin/env python3
"""Demo script to showcase the modern UI improvements"""

import pygame
import sys
import time
import math

# Add project to path
sys.path.insert(0, '.')

from src.ui.modern_objective_ui import ModernObjectiveUI, UITheme
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Modern UI Demo - Economics Adventure")
    clock = pygame.time.Clock()

    # Create modern UI
    modern_ui = ModernObjectiveUI(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Animate UI in
    modern_ui.animate_in()

    # Sample objective data
    objectives = [
        {
            'part': 1,
            'time': '8:00 AM',
            'title': 'Find Employment',
            'description': 'Head to the Jobs Center to look for work opportunities',
            'progress': 0.2
        },
        {
            'part': 1,
            'time': '10:30 AM',
            'title': 'Complete Job Application',
            'description': 'Fill out the application form at Tony\'s Pizza',
            'progress': 0.4
        },
        {
            'part': 1,
            'time': '2:00 PM',
            'title': 'Start First Shift',
            'description': 'Begin your training shift - time to make some pizzas!',
            'progress': 0.6
        }
    ]

    current_objective = 0
    theme_switch_time = 0
    notification_time = time.time() + 2  # Show notification after 2 seconds

    # Background gradient colors for demo
    bg_color1 = (15, 23, 42)
    bg_color2 = (30, 41, 59)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Switch objectives
                    current_objective = (current_objective + 1) % len(objectives)
                    modern_ui.show_notification(
                        "Objective Complete!",
                        f"Moving to: {objectives[current_objective]['title']}",
                        'success'
                    )
                elif event.key == pygame.K_t:
                    # Switch theme
                    themes = [UITheme.DARK_GLASS, UITheme.CYBERPUNK]
                    theme_index = 0 if modern_ui.theme == UITheme.CYBERPUNK.value else 1
                    modern_ui.theme = themes[theme_index].value
                    modern_ui.show_notification(
                        "Theme Changed",
                        f"Switched to {themes[theme_index].name} theme",
                        'info'
                    )
                elif event.key == pygame.K_n:
                    # Show notification
                    types = ['info', 'success', 'warning', 'error']
                    messages = [
                        ("New Message", "You have received a new task", 'info'),
                        ("Level Up!", "Your skills have improved", 'success'),
                        ("Low Energy", "You need to rest soon", 'warning'),
                        ("Failed Task", "You missed the deadline", 'error')
                    ]
                    import random
                    msg = random.choice(messages)
                    modern_ui.show_notification(*msg)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check skip button manually for demo
                skip_x = 30 + 380 - 100  # panel_x + panel_width - 100
                skip_y = modern_ui.panel_y + 20
                skip_width = 80
                skip_height = 32

                if (skip_x <= event.pos[0] <= skip_x + skip_width and
                    skip_y <= event.pos[1] <= skip_y + skip_height):
                    current_objective = (current_objective + 1) % len(objectives)

        # Draw gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = [
                int(bg_color1[i] + (bg_color2[i] - bg_color1[i]) * ratio)
                for i in range(3)
            ]
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        # Add subtle animated background elements
        for i in range(5):
            x = SCREEN_WIDTH // 2 + math.sin(time.time() * 0.5 + i) * 300
            y = SCREEN_HEIGHT // 2 + math.cos(time.time() * 0.3 + i) * 200
            radius = 50 + math.sin(time.time() + i) * 20
            alpha = int(20 + math.sin(time.time() * 0.7 + i) * 10)

            circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (147, 51, 234, alpha), (radius, radius), radius)
            screen.blit(circle_surf, (int(x - radius), int(y - radius)))

        # Draw the modern UI
        modern_ui.draw_objective_panel(screen, objectives[current_objective])

        # Draw interaction prompt demo
        if math.sin(time.time() * 2) > 0:
            modern_ui.draw_interaction_prompt(
                screen,
                "Press E to enter building",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT - 150
            )

        # Draw notifications
        modern_ui.draw_notifications(screen)

        # Show first-time notification
        if notification_time and time.time() > notification_time:
            modern_ui.show_notification(
                "Welcome!",
                "Press SPACE to switch objectives, T for theme",
                'info'
            )
            notification_time = None

        # Draw instructions
        font = pygame.font.Font(None, 20)
        instructions = [
            "SPACE - Next Objective",
            "T - Switch Theme",
            "N - Show Notification",
            "ESC - Exit Demo"
        ]

        y = SCREEN_HEIGHT - 120
        for instruction in instructions:
            text = font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (20, y))
            y += 25

        # Draw title
        title_font = pygame.font.Font(None, 28)
        title = title_font.render("Modern UI Demo - Economics Adventure", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()