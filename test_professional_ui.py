#!/usr/bin/env python3
"""
Test the Professional UI System
Shows how the new UI looks in action
"""

import pygame
import sys
import time

sys.path.insert(0, '.')

from src.ui.professional_ui import (
    ProfessionalObjectiveUI,
    InteractionPrompt,
    NotificationToast
)
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Professional UI Test - Economics Adventure")
    clock = pygame.time.Clock()

    # Initialize UI components
    objective_ui = ProfessionalObjectiveUI(SCREEN_WIDTH, SCREEN_HEIGHT)
    interaction_prompt = InteractionPrompt()
    notifications = NotificationToast(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Show initial UI
    objective_ui.show()

    # Sample objectives to cycle through
    objectives = [
        {
            'part': 1,
            'day': 1,
            'time': '8:00 AM',
            'title': 'Aging Out',
            'description': "You're turning 18 tomorrow. Time to face reality.",
            'progress': 0.14
        },
        {
            'part': 1,
            'day': 1,
            'time': '10:30 AM',
            'title': 'Find Housing',
            'description': 'Visit the Housing Office to explore your options',
            'progress': 0.28
        },
        {
            'part': 1,
            'day': 2,
            'time': '2:00 PM',
            'title': 'Job Application',
            'description': 'Apply for work at local businesses to earn money',
            'progress': 0.42
        },
        {
            'part': 2,
            'day': 5,
            'time': '9:00 AM',
            'title': 'Budget Management',
            'description': 'Learn to manage your limited resources wisely',
            'progress': 0.56
        }
    ]

    current_objective_index = 0
    last_switch = time.time()
    notification_shown = False

    # Game loop
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
                    # Next objective
                    current_objective_index = (current_objective_index + 1) % len(objectives)
                    notifications.show(
                        "Objective Complete",
                        f"Moving to: {objectives[current_objective_index]['title']}",
                        'success'
                    )
                elif event.key == pygame.K_n:
                    # Show notification
                    notifications.show(
                        "System Message",
                        "Your progress has been saved",
                        'info'
                    )
                elif event.key == pygame.K_w:
                    notifications.show(
                        "Low Energy",
                        "You need to rest soon",
                        'warning'
                    )
                elif event.key == pygame.K_e:
                    notifications.show(
                        "No Money",
                        "You cannot afford this item",
                        'error'
                    )
                elif event.key == pygame.K_i:
                    # Toggle interaction prompt
                    if interaction_prompt.visible:
                        interaction_prompt.hide()
                    else:
                        interaction_prompt.show("Press E to enter building")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check for skip button click
                skip_rect = objective_ui.draw(screen, objectives[current_objective_index])
                if skip_rect and skip_rect.collidepoint(event.pos):
                    current_objective_index = (current_objective_index + 1) % len(objectives)
                    notifications.show(
                        "Skipped",
                        "Objective skipped",
                        'info'
                    )

        # Update components
        objective_ui.update(dt)
        interaction_prompt.update(dt)
        notifications.update(dt)

        # Auto-progress animation
        current_obj = objectives[current_objective_index]
        if current_obj['progress'] < 0.95:
            current_obj['progress'] += dt * 0.05  # Slowly increase

        # Draw background (match game style)
        screen.fill((15, 23, 42))  # Dark blue-gray background

        # Add subtle grid pattern for game feel
        grid_color = (20, 28, 46)
        for x in range(0, SCREEN_WIDTH, 32):
            pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 32):
            pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

        # Draw UI components
        objective_ui.draw(screen, objectives[current_objective_index])

        # Draw interaction prompt if visible
        if interaction_prompt.visible:
            interaction_prompt.draw(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)

        # Draw notifications
        notifications.draw(screen)

        # Show welcome notification once
        if not notification_shown and time.time() > 1:
            notifications.show(
                "Welcome",
                "Professional UI System Active",
                'success'
            )
            notification_shown = True

        # Instructions
        font = pygame.font.Font(None, 16)
        instructions = [
            "Controls:",
            "SPACE - Next Objective",
            "N - Info Notification",
            "W - Warning Notification",
            "E - Error Notification",
            "I - Toggle Interaction Prompt",
            "Click SKIP - Skip Objective",
            "ESC - Exit"
        ]

        y = SCREEN_HEIGHT - 140
        for i, line in enumerate(instructions):
            color = (120, 130, 145) if i > 0 else (185, 195, 210)
            text = font.render(line, True, color)
            screen.blit(text, (20, y))
            y += 18

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()