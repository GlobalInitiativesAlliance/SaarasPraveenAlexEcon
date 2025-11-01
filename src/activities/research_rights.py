"""
Tenant Rights Research Activity
Library legal research mini-game for learning tenant rights
"""

import pygame
import random
import math
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class TenantRightsResearch:
    """Mini-game where player researches tenant law at library computer"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Research state
        self.evidence_found = []
        self.evidence_required = 3
        self.evidence_total = 5
        self.search_history = []
        self.current_search = ""
        self.search_results = []
        self.selected_result = 0
        self.viewing_document = None
        self.highlighted_passages = []

        # Time and energy
        self.time_remaining = 120  # 2 hours in minutes
        self.energy = 100
        self.coffee_breaks = 3

        # Visual state
        self.typing_timer = 0
        self.cursor_blink = 0
        self.screen_glow = 0
        self.success_flash = 0
        self.crt_scanline_y = 0

        # Evidence definitions
        self.evidence_database = {
            'habitability': {
                'title': 'CA Civil Code §1941.1 - Habitability Standards',
                'key_text': 'Landlord must maintain heating facilities capable of producing 70°F',
                'search_terms': ['heat', 'habitability', 'temperature', 'broken heater'],
                'importance': 'critical',
                'found_message': 'Proof landlord must fix the heater!'
            },
            'repair_timeline': {
                'title': 'CA Civil Code §1942 - Repair Timeline',
                'key_text': 'Landlord has 30 days after notice to make repairs',
                'search_terms': ['repair time', 'notice', '30 days', 'timeline'],
                'importance': 'critical',
                'found_message': 'They had 30 days - it\'s been 3 months!'
            },
            'rent_withholding': {
                'title': 'CA Civil Code §1942.5 - Rent Withholding Rights',
                'key_text': 'Tenant may withhold rent if conditions substantially breach warranty',
                'search_terms': ['withhold rent', 'rent reduction', 'repair and deduct'],
                'importance': 'critical',
                'found_message': 'You can legally withhold rent!'
            },
            'retaliation': {
                'title': 'CA Civil Code §1942.5 - Retaliation Protection',
                'key_text': 'Landlord cannot evict in retaliation for complaints',
                'search_terms': ['retaliation', 'eviction protection', 'complaint'],
                'importance': 'important',
                'found_message': 'They can\'t evict you for complaining!'
            },
            'code_violations': {
                'title': 'Housing Code §17920.3 - Substandard Conditions',
                'key_text': 'Lack of heating, mold, and pests make dwelling substandard',
                'search_terms': ['code violation', 'substandard', 'mold', 'roaches'],
                'importance': 'important',
                'found_message': 'Multiple code violations documented!'
            }
        }

        # Irrelevant searches for realism
        self.distraction_results = [
            'Commercial Property Management Guide',
            'Landlord Rights and Remedies',
            'Eviction Procedures Manual',
            'Property Investment Strategies',
            'Real Estate Tax Guidelines'
        ]

        # UI Layout
        self.monitor_rect = pygame.Rect(100, 50, 600, 400)
        self.notes_rect = pygame.Rect(720, 50, 200, 400)
        self.search_bar_rect = pygame.Rect(120, 70, 400, 30)
        self.results_rect = pygame.Rect(120, 120, 560, 200)
        self.document_rect = pygame.Rect(120, 340, 560, 100)

    def start(self):
        """Start the research activity"""
        self.active = True
        self.completed = False
        self.time_remaining = 120
        self.energy = 100
        self.evidence_found = []
        self.search_history = []
        self.current_search = ""
        self.viewing_document = None

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update timers
        self.typing_timer += dt
        self.cursor_blink += dt
        self.screen_glow += dt
        self.crt_scanline_y = (self.crt_scanline_y + dt * 50) % self.monitor_rect.height

        # Decrease time
        self.time_remaining -= dt * 2  # 2 seconds = 1 minute game time

        # Decrease energy slowly
        self.energy = max(0, self.energy - dt * 2)

        # Update success flash
        if self.success_flash > 0:
            self.success_flash -= dt

        # Check fail conditions
        if self.time_remaining <= 0:
            self.fail_timeout()
        elif self.energy <= 0:
            self.fail_exhaustion()

        # Check win condition
        if len(self.evidence_found) >= self.evidence_required:
            self.complete()

    def handle_event(self, event):
        """Handle player input"""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.complete()
                return True

            # Typing in search bar
            if not self.viewing_document:
                if event.key == pygame.K_RETURN:
                    self.perform_search()
                elif event.key == pygame.K_BACKSPACE:
                    self.current_search = self.current_search[:-1]
                elif event.key == pygame.K_UP:
                    self.selected_result = max(0, self.selected_result - 1)
                elif event.key == pygame.K_DOWN:
                    if self.search_results:
                        self.selected_result = min(len(self.search_results) - 1, self.selected_result + 1)
                elif event.key == pygame.K_SPACE:
                    if self.search_results:
                        self.view_document(self.search_results[self.selected_result])
                    else:
                        self.current_search += ' '
                elif event.unicode and len(self.current_search) < 40:
                    self.current_search += event.unicode

            # Viewing document
            else:
                if event.key == pygame.K_SPACE:
                    self.highlight_passage()
                elif event.key == pygame.K_BACKSPACE:
                    self.viewing_document = None

            # Coffee break
            if event.key == pygame.K_c and self.coffee_breaks > 0:
                self.take_coffee_break()

        return True

    def perform_search(self):
        """Execute search and show results"""
        if not self.current_search.strip():
            return

        self.search_history.append(self.current_search)
        search_lower = self.current_search.lower()

        # Clear previous results
        self.search_results = []
        self.selected_result = 0

        # Check for relevant evidence
        relevant_found = False
        for key, evidence in self.evidence_database.items():
            if key not in self.evidence_found:
                for term in evidence['search_terms']:
                    if term in search_lower or search_lower in term:
                        self.search_results.append({
                            'type': 'relevant',
                            'key': key,
                            'title': evidence['title'],
                            'preview': evidence['key_text'][:50] + '...'
                        })
                        relevant_found = True
                        break

        # Add some distraction results
        if not relevant_found or random.random() < 0.3:
            for i in range(random.randint(1, 3)):
                if i < len(self.distraction_results):
                    self.search_results.append({
                        'type': 'irrelevant',
                        'title': self.distraction_results[i],
                        'preview': 'Not relevant to tenant rights...'
                    })

        # Waste time on bad searches
        if not relevant_found:
            self.time_remaining -= 5
            self.energy -= 5

        self.current_search = ""

    def view_document(self, result):
        """Open and view a search result"""
        self.viewing_document = result

        if result['type'] == 'irrelevant':
            # Waste time on irrelevant docs
            self.time_remaining -= 3
            self.energy -= 3

    def highlight_passage(self):
        """Highlight important text in document"""
        if not self.viewing_document:
            return

        if self.viewing_document['type'] == 'relevant':
            doc_key = self.viewing_document['key']
            if doc_key not in self.evidence_found:
                self.evidence_found.append(doc_key)
                self.success_flash = 1.0
                self.energy = min(100, self.energy + 10)  # Finding evidence energizes you

                # Show success message
                evidence = self.evidence_database[doc_key]
                self.highlighted_passages.append(evidence['found_message'])

        self.viewing_document = None

    def take_coffee_break(self):
        """Restore energy with coffee"""
        if self.coffee_breaks > 0:
            self.coffee_breaks -= 1
            self.energy = min(100, self.energy + 30)
            self.time_remaining -= 5  # Takes 5 minutes

    def draw(self, screen):
        """Render the research activity"""
        if not self.active:
            return

        # Dark library background
        screen.fill((30, 25, 20))

        # Draw bookshelves in background
        self.draw_library_background(screen)

        # Draw monitor with CRT effect
        self.draw_crt_monitor(screen)

        # Draw research notes
        self.draw_research_notes(screen)

        # Draw UI elements
        self.draw_status_bars(screen)

        # Draw success flash
        if self.success_flash > 0:
            self.draw_success_effect(screen)

    def draw_library_background(self, screen):
        """Draw library environment"""
        # Bookshelves
        shelf_color = (60, 40, 30)
        book_colors = [(120, 80, 60), (80, 100, 80), (100, 60, 60), (70, 70, 100)]

        # Left bookshelf
        pygame.draw.rect(screen, shelf_color, (0, 0, 80, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 80):
            for x in range(5, 75, 15):
                color = random.choice(book_colors)
                pygame.draw.rect(screen, color, (x, y + 10, 12, 60))

        # Right bookshelf
        pygame.draw.rect(screen, shelf_color, (SCREEN_WIDTH - 80, 0, 80, SCREEN_HEIGHT))

        # Desk surface
        pygame.draw.rect(screen, (80, 60, 40), (90, 450, 640, 150))

    def draw_crt_monitor(self, screen):
        """Draw the computer monitor with CRT effects"""
        # Monitor bezel
        pygame.draw.rect(screen, (180, 175, 160), self.monitor_rect.inflate(20, 20), 0, 5)
        pygame.draw.rect(screen, (100, 95, 80), self.monitor_rect.inflate(20, 20), 3, 5)

        # Screen (dark green phosphor)
        screen_color = (20, 40, 20)
        pygame.draw.rect(screen, screen_color, self.monitor_rect)

        # Scanline effect
        scanline_alpha = 30
        for y in range(0, self.monitor_rect.height, 2):
            pygame.draw.line(screen, (0, 20, 0),
                           (self.monitor_rect.x, self.monitor_rect.y + y),
                           (self.monitor_rect.right, self.monitor_rect.y + y))

        # Moving scanline for authenticity
        scan_y = self.monitor_rect.y + int(self.crt_scanline_y)
        pygame.draw.line(screen, (40, 80, 40),
                       (self.monitor_rect.x, scan_y),
                       (self.monitor_rect.right, scan_y), 2)

        # Screen content
        if not self.viewing_document:
            self.draw_search_interface(screen)
        else:
            self.draw_document_view(screen)

    def draw_search_interface(self, screen):
        """Draw the search interface"""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)

        # Terminal header
        header_text = "LEGAL RESEARCH DATABASE v2.3"
        header = font.render(header_text, True, (0, 255, 0))
        screen.blit(header, (self.monitor_rect.x + 20, self.monitor_rect.y + 10))

        # Search bar
        pygame.draw.rect(screen, (0, 60, 0), self.search_bar_rect, 2)
        search_text = self.current_search
        if int(self.cursor_blink * 2) % 2 == 0:
            search_text += "_"
        search_surf = font.render(f"SEARCH> {search_text}", True, (0, 200, 0))
        screen.blit(search_surf, (self.search_bar_rect.x + 5, self.search_bar_rect.y + 5))

        # Search results
        if self.search_results:
            y_offset = 0
            for i, result in enumerate(self.search_results):
                if i == self.selected_result:
                    # Highlight selected
                    highlight_rect = pygame.Rect(self.results_rect.x,
                                               self.results_rect.y + y_offset,
                                               self.results_rect.width, 40)
                    pygame.draw.rect(screen, (0, 80, 0), highlight_rect)

                # Result type indicator
                if result['type'] == 'relevant':
                    color = (0, 255, 0)
                    prefix = "[RELEVANT]"
                else:
                    color = (100, 100, 0)
                    prefix = "[MAYBE]"

                # Title
                title_text = f"{prefix} {result['title']}"
                title_surf = small_font.render(title_text, True, color)
                screen.blit(title_surf, (self.results_rect.x + 10,
                                       self.results_rect.y + y_offset + 5))

                # Preview
                preview_surf = small_font.render(result['preview'], True, (0, 150, 0))
                screen.blit(preview_surf, (self.results_rect.x + 10,
                                         self.results_rect.y + y_offset + 25))

                y_offset += 45

        # Instructions
        inst_text = "ENTER: Search | UP/DOWN: Select | SPACE: Open | C: Coffee | ESC: Exit"
        inst_surf = small_font.render(inst_text, True, (0, 150, 0))
        screen.blit(inst_surf, (self.monitor_rect.x + 20, self.monitor_rect.bottom - 30))

    def draw_document_view(self, screen):
        """Draw document viewing interface"""
        font = pygame.font.Font(None, 22)
        small_font = pygame.font.Font(None, 18)

        # Document title
        title = self.viewing_document['title']
        title_surf = font.render(title, True, (0, 255, 0))
        screen.blit(title_surf, (self.document_rect.x, self.document_rect.y - 30))

        # Document content
        if self.viewing_document['type'] == 'relevant':
            doc_key = self.viewing_document['key']
            evidence = self.evidence_database[doc_key]

            # Split text for display
            words = evidence['key_text'].split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) < 60:
                    current_line += word + " "
                else:
                    lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)

            # Display lines
            for i, line in enumerate(lines[:5]):  # Max 5 lines
                color = (0, 255, 0) if doc_key not in self.evidence_found else (100, 255, 100)
                line_surf = small_font.render(line, True, color)
                screen.blit(line_surf, (self.document_rect.x, self.document_rect.y + i * 20))

            # Highlight prompt
            if doc_key not in self.evidence_found:
                prompt = "SPACE: Highlight this passage as evidence"
                prompt_surf = font.render(prompt, True, (255, 255, 0))
                screen.blit(prompt_surf, (self.document_rect.x, self.document_rect.bottom + 10))
        else:
            # Irrelevant document
            text = "This document does not appear relevant to tenant rights."
            text_surf = small_font.render(text, True, (100, 100, 0))
            screen.blit(text_surf, (self.document_rect.x, self.document_rect.y))

        # Back instruction
        back_text = "BACKSPACE: Return to search"
        back_surf = small_font.render(back_text, True, (0, 150, 0))
        screen.blit(back_surf, (self.monitor_rect.x + 20, self.monitor_rect.bottom - 30))

    def draw_research_notes(self, screen):
        """Draw the notepad with collected evidence"""
        # Notepad background
        pygame.draw.rect(screen, (255, 250, 205), self.notes_rect, 0, 3)
        pygame.draw.rect(screen, (100, 80, 60), self.notes_rect, 2, 3)

        # Spiral binding
        for y in range(self.notes_rect.y + 10, self.notes_rect.bottom, 15):
            pygame.draw.circle(screen, (80, 80, 80), (self.notes_rect.x + 10, y), 3)

        # Title
        font = pygame.font.Font(None, 24)
        title = font.render("EVIDENCE NOTES", True, (0, 0, 100))
        screen.blit(title, (self.notes_rect.x + 30, self.notes_rect.y + 10))

        # Progress
        progress_text = f"Found: {len(self.evidence_found)}/{self.evidence_required} (need {self.evidence_required})"
        progress = font.render(progress_text, True, (0, 100, 0))
        screen.blit(progress, (self.notes_rect.x + 30, self.notes_rect.y + 35))

        # Evidence list
        small_font = pygame.font.Font(None, 18)
        y_offset = 70
        for i, key in enumerate(self.evidence_found):
            evidence = self.evidence_database[key]
            # Checkbox
            pygame.draw.rect(screen, (0, 150, 0),
                           (self.notes_rect.x + 20, self.notes_rect.y + y_offset, 10, 10))
            pygame.draw.lines(screen, (0, 100, 0), False,
                            [(self.notes_rect.x + 22, self.notes_rect.y + y_offset + 5),
                             (self.notes_rect.x + 24, self.notes_rect.y + y_offset + 8),
                             (self.notes_rect.x + 28, self.notes_rect.y + y_offset + 2)], 2)

            # Evidence title (shortened)
            title_short = evidence['title'][:20] + "..."
            text = small_font.render(title_short, True, (0, 0, 0))
            screen.blit(text, (self.notes_rect.x + 35, self.notes_rect.y + y_offset))
            y_offset += 25

        # Messages
        if self.highlighted_passages:
            last_message = self.highlighted_passages[-1]
            msg_surf = small_font.render(last_message, True, (0, 100, 0))
            msg_rect = msg_surf.get_rect(center=(self.notes_rect.centerx, self.notes_rect.bottom - 30))
            screen.blit(msg_surf, msg_rect)

    def draw_status_bars(self, screen):
        """Draw time and energy status"""
        font = pygame.font.Font(None, 24)

        # Time remaining
        time_color = (255, 255, 0) if self.time_remaining > 30 else (255, 100, 100)
        time_text = f"Library closes in: {int(self.time_remaining // 60)}h {int(self.time_remaining % 60)}m"
        time_surf = font.render(time_text, True, time_color)
        screen.blit(time_surf, (100, 20))

        # Energy bar
        bar_width = 200
        bar_height = 20
        bar_x = 350
        bar_y = 20

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Fill
        fill_width = int((self.energy / 100) * bar_width)
        energy_color = (0, 200, 0) if self.energy > 30 else (200, 200, 0) if self.energy > 10 else (200, 0, 0)
        pygame.draw.rect(screen, energy_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)

        # Label
        energy_text = f"Energy: {int(self.energy)}%"
        energy_surf = font.render(energy_text, True, (200, 200, 200))
        screen.blit(energy_surf, (bar_x + bar_width + 10, bar_y))

        # Coffee breaks
        coffee_text = f"Coffee breaks: {self.coffee_breaks}"
        coffee_surf = font.render(coffee_text, True, (150, 100, 50))
        screen.blit(coffee_surf, (600, 20))

    def draw_success_effect(self, screen):
        """Draw success flash effect"""
        if self.success_flash > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.set_alpha(int(self.success_flash * 100))
            flash_surf.fill((100, 255, 100))
            screen.blit(flash_surf, (0, 0))

            # Success text
            font = pygame.font.Font(None, 48)
            text = font.render("EVIDENCE FOUND!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

    def fail_timeout(self):
        """Handle timeout failure"""
        self.active = False
        self.completed = False
        # Could trigger a failure narrative here

    def fail_exhaustion(self):
        """Handle exhaustion failure"""
        self.active = False
        self.completed = False
        # Could trigger a failure narrative here

    def complete(self):
        """Complete the activity"""
        if not self.active:
            return

        self.active = False
        self.completed = True

        # Update objective based on evidence found
        current = self.objective_manager.get_current_objective()
        if current and current.id == 'research_rights':
            if len(self.evidence_found) >= self.evidence_required:
                self.objective_manager.complete_objective('research_rights')
            # Could add different outcomes based on how much evidence was found