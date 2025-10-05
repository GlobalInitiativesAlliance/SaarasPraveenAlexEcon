"""Form Filling Mini-Game - Navigate bureaucratic paperwork"""

import pygame
import random
from shared.constants import *

class FormFillingGame:
    """Fill out complex forms with impossible requirements"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.current_page = 0
        self.total_pages = 5
        self.fields_completed = 0
        self.total_fields = 20
        self.errors_made = 0
        self.time_remaining = 300  # 5 minutes
        
        # Current field
        self.current_field = 0
        self.current_input = ""
        self.field_focused = False
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Form fields with requirements
        self.create_form_fields()
        
    def create_form_fields(self):
        """Create realistic form fields"""
        self.form_fields = [
            # Page 1 - Basic Info
            {'page': 0, 'label': 'Legal Name', 'type': 'text', 'required': True},
            {'page': 0, 'label': 'Date of Birth', 'type': 'date', 'required': True},
            {'page': 0, 'label': 'Social Security #', 'type': 'ssn', 'required': True, 
             'issue': "Don't have SSN card"},
            {'page': 0, 'label': 'Current Address', 'type': 'address', 'required': True,
             'issue': "Homeless - no address"},
             
            # Page 2 - Income
            {'page': 1, 'label': 'Monthly Income', 'type': 'money', 'required': True},
            {'page': 1, 'label': 'Employer Name', 'type': 'text', 'required': True},
            {'page': 1, 'label': 'Employer Phone', 'type': 'phone', 'required': True},
            {'page': 1, 'label': 'Pay Stub Attached?', 'type': 'checkbox', 'required': True,
             'issue': "Paid cash - no stubs"},
             
            # Page 3 - References
            {'page': 2, 'label': 'Reference 1 Name', 'type': 'text', 'required': True},
            {'page': 2, 'label': 'Reference 1 Phone', 'type': 'phone', 'required': True},
            {'page': 2, 'label': 'Relationship', 'type': 'text', 'required': True,
             'issue': "No family to list"},
            {'page': 2, 'label': 'Years Known', 'type': 'number', 'required': True},
            
            # Page 4 - Background
            {'page': 3, 'label': 'Criminal History?', 'type': 'checkbox', 'required': True},
            {'page': 3, 'label': 'Eviction History?', 'type': 'checkbox', 'required': True},
            {'page': 3, 'label': 'Credit Score', 'type': 'number', 'required': True,
             'issue': "Never had credit"},
            {'page': 3, 'label': 'Bank Account?', 'type': 'checkbox', 'required': True},
            
            # Page 5 - Impossible Requirements
            {'page': 4, 'label': "Parent's Tax Return", 'type': 'file', 'required': True,
             'issue': "No contact with parents"},
            {'page': 4, 'label': 'Proof of Residence', 'type': 'file', 'required': True,
             'issue': "Couch surfing"},
            {'page': 4, 'label': 'Co-signer Name', 'type': 'text', 'required': True,
             'issue': "Nobody will co-sign"},
            {'page': 4, 'label': 'Application Fee', 'type': 'payment', 'required': True,
             'issue': "$45 non-refundable"}
        ]
        
        # Get fields for current page
        self.update_current_fields()
        
    def update_current_fields(self):
        """Get fields for current page"""
        self.current_page_fields = [f for f in self.form_fields if f['page'] == self.current_page]
        self.current_field = 0
        
    def start(self):
        """Start the form filling game"""
        self.active = True
        self.completed = False
        self.current_page = 0
        self.update_current_fields()
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.end_game("Time's up! Office is closing.")
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        # Navigation
        if key == pygame.K_TAB:
            # Next field
            self.current_field = (self.current_field + 1) % len(self.current_page_fields)
        elif key == pygame.K_RETURN:
            # Try to submit field
            self.submit_field()
        elif key == pygame.K_PAGEDOWN and self.current_page < self.total_pages - 1:
            # Next page
            self.current_page += 1
            self.update_current_fields()
        elif key == pygame.K_PAGEUP and self.current_page > 0:
            # Previous page
            self.current_page -= 1
            self.update_current_fields()
        elif key == pygame.K_ESCAPE:
            self.end_game("Application incomplete")
            
        # Text input for current field
        if self.current_field < len(self.current_page_fields):
            field = self.current_page_fields[self.current_field]
            if field['type'] in ['text', 'number', 'phone', 'ssn']:
                if key == pygame.K_BACKSPACE:
                    self.current_input = self.current_input[:-1]
                elif key >= pygame.K_SPACE and key <= pygame.K_z:
                    self.current_input += chr(key)
                    
    def submit_field(self):
        """Submit current field"""
        if self.current_field >= len(self.current_page_fields):
            return
            
        field = self.current_page_fields[self.current_field]
        
        # Check for issues
        if 'issue' in field:
            self.errors_made += 1
            # Field has an issue but we have to fill it anyway
            
        if field.get('completed'):
            return
            
        field['completed'] = True
        self.fields_completed += 1
        self.current_input = ""
        
        # Check if form is complete
        if self.fields_completed >= self.total_fields:
            self.end_game("Form submitted! Wait 6-8 weeks for response.", success=True)
            
    def end_game(self, message, success=False):
        """End the form filling game"""
        self.active = False
        self.completed = True
        self.completion_message = message
        self.success = success
        
    def draw(self, screen):
        """Draw the form interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((245, 245, 240))  # Paper color
        
        # Title
        title = f"TRANSITIONAL HOUSING APPLICATION - Page {self.current_page + 1}/{self.total_pages}"
        title_surf = self.title_font.render(title, True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(title_surf, title_rect)
        
        # Timer
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        timer_color = (255, 0, 0) if self.time_remaining < 60 else (0, 0, 0)
        timer_text = f"Time: {minutes}:{seconds:02d}"
        timer_surf = self.font.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (SCREEN_WIDTH - 150, 40))
        
        # Progress
        progress_text = f"Fields: {self.fields_completed}/{self.total_fields}"
        progress_surf = self.font.render(progress_text, True, (0, 0, 0))
        screen.blit(progress_surf, (50, 40))
        
        # Draw form fields
        y_offset = 100
        for i, field in enumerate(self.current_page_fields):
            # Field background
            if i == self.current_field:
                pygame.draw.rect(screen, (220, 220, 255), (100, y_offset - 5, 600, 40))
                
            # Label
            label_text = field['label']
            if field.get('required'):
                label_text += " *"
            label_surf = self.font.render(label_text, True, (0, 0, 0))
            screen.blit(label_surf, (120, y_offset))
            
            # Field value or input
            if field.get('completed'):
                value_text = "[COMPLETED]"
                value_color = (0, 150, 0)
            elif i == self.current_field and self.current_input:
                value_text = self.current_input
                value_color = (0, 0, 200)
            else:
                value_text = "________________"
                value_color = (150, 150, 150)
                
            value_surf = self.font.render(value_text, True, value_color)
            screen.blit(value_surf, (350, y_offset))
            
            # Issue warning
            if 'issue' in field:
                issue_surf = self.small_font.render(f"Issue: {field['issue']}", True, (255, 0, 0))
                screen.blit(issue_surf, (350, y_offset + 25))
                
            y_offset += 60
            
        # Instructions
        inst_lines = [
            "TAB: Next field | ENTER: Submit field",
            "PAGE UP/DOWN: Change pages | ESC: Give up"
        ]
        inst_y = SCREEN_HEIGHT - 80
        for line in inst_lines:
            inst_surf = self.small_font.render(line, True, (100, 100, 100))
            inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            screen.blit(inst_surf, inst_rect)
            inst_y += 25
            
        # Errors
        if self.errors_made > 0:
            error_text = f"Issues found: {self.errors_made} (form will likely be rejected)"
            error_surf = self.font.render(error_text, True, (255, 0, 0))
            error_rect = error_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
            screen.blit(error_surf, error_rect)