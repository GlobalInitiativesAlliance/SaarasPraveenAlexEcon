"""Roommate Selection Game - Choose compatible roommates"""

import pygame
import random
from shared.constants import *

class RoommateSelectionGame:
    """Review profiles and select a compatible roommate"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.current_profile = 0
        self.candidates = []
        self.selected_roommate = None
        self.interview_phase = False
        self.interview_questions = []
        self.current_question = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Generate roommate profiles
        self.generate_candidates()
        
    def generate_candidates(self):
        """Generate random roommate candidates"""
        first_names = ['Alex', 'Jordan', 'Sam', 'Casey', 'Morgan', 'Taylor']
        last_initials = ['B.', 'C.', 'D.', 'G.', 'K.', 'L.', 'M.', 'P.', 'R.', 'S.']
        
        jobs = [
            ('Part-time barista', 1200, 'Variable schedule'),
            ('Gig driver', 1500, 'Flexible hours'),
            ('Retail worker', 1100, 'Evenings/weekends'),
            ('Student', 800, 'Part-time income'),
            ('Restaurant server', 1400, 'Night shifts'),
            ('Warehouse worker', 1800, 'Early mornings')
        ]
        
        traits = [
            {'trait': 'Clean freak', 'compatibility': 'mixed', 'details': 'Expects spotless common areas'},
            {'trait': 'Night owl', 'compatibility': 'negative', 'details': 'Active until 3 AM'},
            {'trait': 'Quiet introvert', 'compatibility': 'positive', 'details': 'Respects personal space'},
            {'trait': 'Party person', 'compatibility': 'negative', 'details': 'Frequent guests over'},
            {'trait': 'Responsible', 'compatibility': 'positive', 'details': 'Always pays on time'},
            {'trait': 'Disorganized', 'compatibility': 'negative', 'details': 'Forgets chores often'},
            {'trait': 'Good communicator', 'compatibility': 'positive', 'details': 'Addresses issues directly'},
            {'trait': 'Passive-aggressive', 'compatibility': 'negative', 'details': 'Leaves angry notes'}
        ]
        
        red_flags = [
            'Has been evicted before',
            'Owes previous roommate money',
            'No references available',
            'Vague about income source',
            'Wants to pay cash only',
            'Mentions frequent "friends staying over"'
        ]
        
        self.candidates = []
        for i in range(4):
            name = f"{random.choice(first_names)} {random.choice(last_initials)}"
            age = random.randint(18, 28)
            job_title, income, schedule = random.choice(jobs)
            
            # Generate traits (2-3 per person)
            person_traits = random.sample(traits, random.randint(2, 3))
            
            # Add red flags to some candidates
            person_red_flags = []
            if random.random() < 0.6:  # 60% chance of red flags
                person_red_flags = random.sample(red_flags, random.randint(1, 2))
                
            # Calculate compatibility score
            positive_traits = sum(1 for t in person_traits if t['compatibility'] == 'positive')
            negative_traits = sum(1 for t in person_traits if t['compatibility'] == 'negative')
            compatibility = 50 + (positive_traits * 20) - (negative_traits * 15) - (len(person_red_flags) * 25)
            
            candidate = {
                'name': name,
                'age': age,
                'job': job_title,
                'income': income,
                'schedule': schedule,
                'traits': person_traits,
                'red_flags': person_red_flags,
                'compatibility': max(0, min(100, compatibility)),
                'references': random.choice(['Strong', 'Weak', 'None']),
                'social_media': random.choice(['Clean', 'Party photos', 'Private', 'Red flags'])
            }
            
            self.candidates.append(candidate)
            
    def start(self):
        """Start the selection process"""
        self.active = True
        self.completed = False
        self.current_profile = 0
        self.selected_roommate = None
        self.interview_phase = False
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if not self.interview_phase:
            # Profile browsing phase
            if key == pygame.K_LEFT:
                self.current_profile = (self.current_profile - 1) % len(self.candidates)
            elif key == pygame.K_RIGHT:
                self.current_profile = (self.current_profile + 1) % len(self.candidates)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                # Select this candidate for interview
                self.start_interview()
            elif key == pygame.K_ESCAPE:
                # Skip to random selection
                self.make_desperate_choice()
        else:
            # Interview phase
            if key == pygame.K_y:
                self.answer_interview(True)
            elif key == pygame.K_n:
                self.answer_interview(False)
                
    def start_interview(self):
        """Start interviewing selected candidate"""
        self.interview_phase = True
        self.current_question = 0
        self.interview_questions = [
            {
                'question': 'Do you have the full deposit ready?',
                'good_answer': True,
                'responses': {
                    True: "Yes, I have it in my bank account.",
                    False: "I'll have it by move-in... probably."
                }
            },
            {
                'question': 'Are you okay with quiet hours after 10 PM?',
                'good_answer': True,
                'responses': {
                    True: "Absolutely, I need my sleep too.",
                    False: "That seems pretty early..."
                }
            },
            {
                'question': 'How do you feel about overnight guests?',
                'good_answer': True,
                'responses': {
                    True: "I'd always ask first and keep it minimal.",
                    False: "My partner basically lives here too, hope that's cool."
                }
            }
        ]
        
    def answer_interview(self, answer):
        """Process interview answer"""
        if self.current_question < len(self.interview_questions):
            question = self.interview_questions[self.current_question]
            if answer == question['good_answer']:
                self.candidates[self.current_profile]['compatibility'] += 10
            else:
                self.candidates[self.current_profile]['compatibility'] -= 10
                
            self.current_question += 1
            
            if self.current_question >= len(self.interview_questions):
                # Interview complete
                self.finalize_selection()
                
    def make_desperate_choice(self):
        """Make a quick choice without proper vetting"""
        self.selected_roommate = random.choice(self.candidates)
        self.selected_roommate['rushed'] = True
        self.end_game()
        
    def finalize_selection(self):
        """Finalize the roommate selection"""
        self.selected_roommate = self.candidates[self.current_profile]
        self.end_game()
        
    def end_game(self):
        """End the selection process"""
        self.active = False
        self.completed = True
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
    def draw(self, screen):
        """Draw the selection interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((245, 245, 250))
        
        # Title
        title = "ROOMMATE SELECTION"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        if not self.interview_phase:
            # Profile viewing phase
            candidate = self.candidates[self.current_profile]
            
            # Profile card
            card_rect = pygame.Rect(100, 80, SCREEN_WIDTH - 200, 400)
            pygame.draw.rect(screen, (255, 255, 255), card_rect)
            pygame.draw.rect(screen, (200, 200, 210), card_rect, 3)
            
            # Basic info
            y_offset = card_rect.y + 20
            
            # Name and age
            name_text = f"{candidate['name']}, {candidate['age']}"
            name_surf = self.font.render(name_text, True, (50, 50, 60))
            screen.blit(name_surf, (card_rect.x + 20, y_offset))
            y_offset += 40
            
            # Job and income
            job_text = f"Job: {candidate['job']} (${candidate['income']}/month)"
            job_surf = self.font.render(job_text, True, (80, 80, 90))
            screen.blit(job_surf, (card_rect.x + 20, y_offset))
            y_offset += 30
            
            schedule_surf = self.small_font.render(f"Schedule: {candidate['schedule']}", True, (100, 100, 110))
            screen.blit(schedule_surf, (card_rect.x + 20, y_offset))
            y_offset += 40
            
            # Traits
            trait_label = self.font.render("Personality:", True, (50, 50, 60))
            screen.blit(trait_label, (card_rect.x + 20, y_offset))
            y_offset += 30
            
            for trait_info in candidate['traits']:
                trait_color = (60, 140, 60) if trait_info['compatibility'] == 'positive' else \
                             (180, 180, 60) if trait_info['compatibility'] == 'mixed' else \
                             (180, 60, 60)
                trait_text = f"• {trait_info['trait']}: {trait_info['details']}"
                trait_surf = self.small_font.render(trait_text, True, trait_color)
                screen.blit(trait_surf, (card_rect.x + 40, y_offset))
                y_offset += 25
                
            y_offset += 20
            
            # References and social media
            ref_text = f"References: {candidate['references']}"
            ref_color = (60, 140, 60) if candidate['references'] == 'Strong' else \
                       (180, 180, 60) if candidate['references'] == 'Weak' else (180, 60, 60)
            ref_surf = self.font.render(ref_text, True, ref_color)
            screen.blit(ref_surf, (card_rect.x + 20, y_offset))
            y_offset += 30
            
            social_text = f"Social Media Check: {candidate['social_media']}"
            social_color = (60, 140, 60) if candidate['social_media'] == 'Clean' else \
                          (180, 180, 60) if candidate['social_media'] == 'Private' else (180, 60, 60)
            social_surf = self.font.render(social_text, True, social_color)
            screen.blit(social_surf, (card_rect.x + 20, y_offset))
            y_offset += 40
            
            # Red flags
            if candidate['red_flags']:
                flag_label = self.font.render("Concerns:", True, (180, 60, 60))
                screen.blit(flag_label, (card_rect.x + 20, y_offset))
                y_offset += 25
                
                for flag in candidate['red_flags']:
                    flag_text = f"⚠ {flag}"
                    flag_surf = self.small_font.render(flag_text, True, (180, 60, 60))
                    screen.blit(flag_surf, (card_rect.x + 40, y_offset))
                    y_offset += 20
                    
            # Compatibility meter
            compat_rect = pygame.Rect(card_rect.x + card_rect.width - 150, card_rect.y + 20, 120, 80)
            pygame.draw.rect(screen, (240, 240, 245), compat_rect)
            pygame.draw.rect(screen, (180, 180, 190), compat_rect, 2)
            
            compat_label = self.small_font.render("Compatibility", True, (80, 80, 90))
            label_rect = compat_label.get_rect(center=(compat_rect.centerx, compat_rect.y + 15))
            screen.blit(compat_label, label_rect)
            
            # Compatibility percentage
            compat_color = (60, 180, 60) if candidate['compatibility'] >= 70 else \
                          (220, 180, 60) if candidate['compatibility'] >= 40 else (220, 60, 60)
            compat_text = f"{candidate['compatibility']}%"
            compat_surf = self.title_font.render(compat_text, True, compat_color)
            compat_text_rect = compat_surf.get_rect(center=(compat_rect.centerx, compat_rect.y + 50))
            screen.blit(compat_surf, compat_text_rect)
            
            # Navigation
            nav_y = 510
            nav_surf = self.font.render(f"Profile {self.current_profile + 1} of {len(self.candidates)}", 
                                       True, (100, 100, 110))
            nav_rect = nav_surf.get_rect(center=(SCREEN_WIDTH // 2, nav_y))
            screen.blit(nav_surf, nav_rect)
            
            # Instructions
            inst_lines = [
                "← → Browse profiles | ENTER Select for interview | ESC Make quick choice"
            ]
            inst_y = 550
            for line in inst_lines:
                inst_surf = self.small_font.render(line, True, (120, 120, 140))
                inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
                screen.blit(inst_surf, inst_rect)
                inst_y += 25
        else:
            # Interview phase
            candidate = self.candidates[self.current_profile]
            
            # Interview box
            interview_rect = pygame.Rect(50, 100, SCREEN_WIDTH - 100, 400)
            pygame.draw.rect(screen, (250, 250, 255), interview_rect)
            pygame.draw.rect(screen, (180, 180, 200), interview_rect, 3)
            
            # Candidate name
            interview_title = f"Interviewing {candidate['name']}"
            interview_surf = self.font.render(interview_title, True, (50, 50, 80))
            interview_rect_text = interview_surf.get_rect(center=(SCREEN_WIDTH // 2, 130))
            screen.blit(interview_surf, interview_rect_text)
            
            if self.current_question < len(self.interview_questions):
                # Current question
                question = self.interview_questions[self.current_question]
                
                q_text = f"Question {self.current_question + 1}: {question['question']}"
                q_surf = self.font.render(q_text, True, (40, 40, 60))
                q_rect = q_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
                screen.blit(q_surf, q_rect)
                
                # Response options
                y_resp = self.font.render("Y - Yes", True, (60, 140, 60))
                n_resp = self.font.render("N - No", True, (180, 60, 60))
                
                screen.blit(y_resp, (interview_rect.x + 100, 280))
                screen.blit(n_resp, (interview_rect.x + 100, 320))
            else:
                # Interview complete
                complete_text = "Interview Complete! Making final decision..."
                complete_surf = self.font.render(complete_text, True, (60, 140, 60))
                complete_rect = complete_surf.get_rect(center=(SCREEN_WIDTH // 2, 250))
                screen.blit(complete_surf, complete_rect)