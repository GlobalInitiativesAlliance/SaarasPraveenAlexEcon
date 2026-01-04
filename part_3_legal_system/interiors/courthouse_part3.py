"""
Courthouse Interior for Part 3 - Legal System
Handles scenes 10-15 and 17: queue, forms, wrong room, judge, fine, appeal, reflection
Enhanced with portrait system for dialogue
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior
from part_3_legal_system.dialogue_portraits import portrait_renderer, Emotion


class CourthousePart3(NarrativeInterior):
    """Courthouse with Part 3 legal system narrative - bureaucratic nightmare"""

    # Speaker name to character ID mapping for portraits
    SPEAKER_TO_CHARACTER = {
        'You': 'player',
        'Judge': 'judge',
        'Clerk': 'clerk',
        'Security Guard': 'officer',
        'Bailiff': 'officer',
        'Person Ahead': 'coworker',
        'Prosecutor': 'officer',
    }

    # Emotion mapping for specific dialogue contexts
    CONTEXT_EMOTIONS = {
        'courthouse_queue': {
            'player': Emotion.WORRIED,
            'officer': Emotion.DISMISSIVE,
        },
        'court_forms': {
            'player': Emotion.WORRIED,
            'clerk': Emotion.DISMISSIVE,
        },
        'wrong_courtroom': {
            'player': Emotion.SCARED,
            'officer': Emotion.DISMISSIVE,
        },
        'face_judge': {
            'player': Emotion.SCARED,
            'judge': Emotion.STERN,
        },
        'court_fine': {
            'player': Emotion.SCARED,
            'judge': Emotion.STERN,
        },
        'dispute_denied': {
            'player': Emotion.DETERMINED,
            'judge': Emotion.DISAPPOINTED,
        },
        'courthouse_reflection': {
            'player': Emotion.WORRIED,
        },
    }

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.forms_completed = False
        self.fine_amount = 300  # $150 original + $150 failure to appear

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Track debt added to player
        self.debt_applied = False

        # Portrait system
        self.portrait_renderer = portrait_renderer

    def enter(self):
        """Override enter to set up courthouse scene based on objective"""
        super().enter()

        print(f"[COURT_P3] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[COURT_P3]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[COURT_P3]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[COURT_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        # All courthouse scenes are dialogue-driven
        pass

    def load_narrative_content(self):
        """Load the courthouse narrative content for Part 3"""
        return {
            'courthouse_queue': {
                'npcs': [
                    {'name': 'Security Guard', 'x': 8, 'y': 10},
                    {'name': 'Person Ahead', 'x': 6, 'y': 6},
                ],
                'dialogue_sequence': [
                    (None, "The courthouse looms before you."),
                    (None, "Imposing stone columns. Heavy doors."),
                    (None, "A building designed to make you feel small."),
                    ("Security Guard", "ID and any electronics in the bin."),
                    (None, "You empty your pockets. Your phone. Your keys."),
                    (None, "Everything that connects you to the outside world."),
                    (None, "The metal detector beeps."),
                    ("Security Guard", "Belt. Take off your belt."),
                    ("You", "Sorry, sorry..."),
                    (None, "Humiliation before you've even started."),
                    (None, "Inside, lines snake through the marble hallway."),
                    (None, "Dozens of people. All waiting. All anxious."),
                    ("Person Ahead", "You here for traffic court?"),
                    ("You", "Yeah... failure to appear."),
                    ("Person Ahead", "Been here since 7am. Still waiting."),
                    ("You", "But my hearing is at 9..."),
                    ("Person Ahead", "Good luck with that. They're running two hours behind."),
                    (None, "Two hours. You have work later. School tomorrow."),
                    (None, "But what choice do you have?"),
                    (None, "You take your place in line."),
                    (None, "And wait."),
                ],
                'interactions': {}
            },

            'court_forms': {
                'npcs': [
                    {'name': 'Clerk', 'x': 8, 'y': 4},
                ],
                'dialogue_sequence': [
                    (None, "Finally. The front of the line."),
                    ("Clerk", "Next. Name and case number."),
                    ("You", "I... I don't know my case number."),
                    ("Clerk", "(sighs) ID."),
                    (None, "She types rapidly, not making eye contact."),
                    ("Clerk", "Fill out forms 27-B and 42-A. In triplicate."),
                    ("You", "I don't understand half of these questions."),
                    ("Clerk", "Figure it out. Next!"),
                    (None, "She's already looking past you."),
                    (None, "You step aside, papers in hand."),
                    (None, "Legal jargon fills every line."),
                    (None, "'Petitioner hereby acknowledges...'"),
                    (None, "'Waiver of rights pursuant to...'"),
                    ("You", "(struggling) 'Waiver of rights'? What rights?"),
                    (None, "No one explains. No one helps."),
                    (None, "You do your best. Check boxes. Sign lines."),
                    (None, "Hoping you're not signing away something important."),
                ],
                'interactions': {}
            },

            'wrong_courtroom': {
                'npcs': [
                    {'name': 'Bailiff', 'x': 8, 'y': 8},
                ],
                'dialogue_sequence': [
                    (None, "You find what you think is the right room."),
                    (None, "Room 301. Criminal Court."),
                    (None, "You wait. And wait."),
                    (None, "Your name is never called."),
                    ("You", "(to bailiff) Excuse me, I'm here for traffic court..."),
                    ("Bailiff", "Traffic court? Wrong room."),
                    ("You", "But I was told—"),
                    ("Bailiff", "Room 204. Down the hall, down the stairs."),
                    ("You", "But it's almost my time!"),
                    ("Bailiff", "Then you better hurry."),
                    (None, "You run through the halls, lost in the bureaucratic maze."),
                    (None, "Signs point in contradicting directions."),
                    ("You", "201... 202... 203... 204!"),
                    (None, "You burst through the doors, out of breath."),
                    (None, "Everyone turns to look at you."),
                    (None, "The judge's gaze is cold."),
                ],
                'interactions': {}
            },

            'face_judge': {
                'npcs': [
                    {'name': 'Judge', 'x': 8, 'y': 2},
                    {'name': 'Prosecutor', 'x': 10, 'y': 5},
                ],
                'dialogue_sequence': [
                    ("Judge", "Case number 47821."),
                    (None, "The court clerk reads your name."),
                    ("Judge", "Step forward."),
                    (None, "Your legs feel like lead."),
                    ("Judge", "You are... late."),
                    ("You", "Your Honor, I got sent to the wrong room—"),
                    ("Judge", "I don't want to hear excuses."),
                    ("Judge", "According to records, you also missed your original court date."),
                    ("You", "I had to work. I would have lost my job—"),
                    ("Judge", "The law doesn't make exceptions for scheduling conflicts."),
                    ("You", "But I'm trying to support myself—"),
                    ("Judge", "Order."),
                    (None, "The word cuts through the room."),
                    ("Judge", "You will address the court properly."),
                    ("You", "Yes, Your Honor. I apologize."),
                    ("Judge", "Your original violation was for running a red light."),
                    ("Judge", "The fine was $150."),
                    (None, "You remember that day. Late for work. Trying not to lose your job."),
                    ("Judge", "Which you failed to pay. And then failed to appear."),
                ],
                'interactions': {}
            },

            'court_fine': {
                'npcs': [
                    {'name': 'Judge', 'x': 8, 'y': 2},
                ],
                'dialogue_sequence': [
                    ("Judge", "For failure to appear, I'm adding a $150 fine."),
                    ("You", "$150?! Your Honor, I barely make rent!"),
                    ("Judge", "That's in addition to your original citation."),
                    ("Judge", "Total due: $300."),
                    (None, "Three hundred dollars."),
                    (None, "That's almost your entire paycheck."),
                    ("Judge", "You have 30 days to pay in full."),
                    ("You", "(whispering) I don't have $300..."),
                    ("Judge", "Failure to pay will result in additional penalties."),
                    ("Judge", "Including possible jail time."),
                    (None, "Jail. For a traffic ticket. For being poor."),
                    (None, "Another impossible debt. Another hole to climb out of."),
                    (None, "The weight of it presses down on your chest."),
                ],
                'interactions': {}
            },

            'dispute_denied': {
                'npcs': [
                    {'name': 'Judge', 'x': 8, 'y': 2},
                ],
                'dialogue_sequence': [
                    ("You", "Your Honor, please. Can I explain?"),
                    ("Judge", "The court has already ruled."),
                    ("You", "But I'm a foster youth! I aged out with nothing!"),
                    (None, "The judge's expression doesn't change."),
                    ("You", "I don't have parents to help me. No safety net."),
                    ("You", "I was just trying to keep my job—"),
                    ("Judge", "Your circumstances are not the court's concern."),
                    (None, "Those words hit like a physical blow."),
                    ("Judge", "The law applies equally to everyone."),
                    (None, "Equally. As if everyone starts from the same place."),
                    ("Judge", "Pay the fine or face additional penalties."),
                    ("Judge", "Next case."),
                    (None, "Dismissed. Invisible. Just another case number."),
                    (None, "You walk out of the courtroom in a daze."),
                ],
                'interactions': {}
            },

            'courthouse_reflection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stand outside the courthouse."),
                    (None, "The sun is setting. Hours have passed."),
                    (None, "In one hand: court papers. $300 debt."),
                    (None, "In the other: your study guide. Exam next week."),
                    ("You", "Work. School. Court. Survival."),
                    ("You", "Pick two. You can't have all four."),
                    (None, "A group of lawyers walk past, laughing."),
                    (None, "For them, this is just a job. A game."),
                    (None, "For you, it's your life."),
                    (None, "The system wasn't built for people like you."),
                    (None, "It was built to process you. File you. Fine you."),
                    (None, "And move on to the next case."),
                    (None, "But you're not just a case number."),
                    (None, "You're not just a statistic."),
                    (None, "You're trying to build a life."),
                    (None, "Against a system that keeps knocking it down."),
                    (None, "You pocket the papers and start walking."),
                    (None, "Tomorrow, you'll figure something out."),
                    (None, "You always do."),
                    (None, "Because you have no other choice."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update objective text based on courthouse progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        objective_displays = {
            'courthouse_queue': ("Wait in the courthouse line", "Join the others waiting"),
            'court_forms': ("Fill out the required forms", "Navigate the paperwork"),
            'wrong_courtroom': ("Find the right courtroom", "Room 204"),
            'face_judge': ("Face the judge", "Answer for your absence"),
            'court_fine': ("Receive your sentence", "$300 in fines"),
            'dispute_denied': ("Try to explain", "Make your case"),
            'courthouse_reflection': ("Leave the courthouse", "Process what happened"),
        }

        if current.id in objective_displays:
            current.dynamic_description = objective_displays[current.id][0]
            current.progress_text = objective_displays[current.id][1]

    def end_narrative_sequence(self):
        """Override to properly handle courthouse transitions - Part 1 pattern"""
        print(f"[COURT_P3] *** end_narrative_sequence() CALLED ***")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()

        if not current:
            return

        if not self.check_objective_complete():
            return

        # Apply debt when reaching court_fine scene
        if current.id == 'court_fine' and not self.debt_applied:
            self.apply_court_debt()
            self.debt_applied = True

        print(f"[COURT_P3] Completing objective: {current.id}")

        # Part 1 Pattern: Just set should_exit flag
        # Main game's complete_current_objective() handles advancement and re-entry
        print(f"[COURT_P3] Objective complete - setting should_exit = True")
        print(f"[COURT_P3]   Main game will handle advancement via complete_current_objective()")
        self.should_exit = True

        # Call complete_current_objective() to let main game handle transition
        self.game.objective_manager.complete_current_objective()

    def apply_court_debt(self):
        """Apply the $300 fine to player's debt"""
        if hasattr(self.game, 'objective_manager'):
            # Add debt to player stats if tracking exists
            if hasattr(self.game.objective_manager, 'player_debt'):
                self.game.objective_manager.player_debt += self.fine_amount
                print(f"[COURT_P3] Added ${self.fine_amount} to player debt")
            # Also reduce money if player has any
            if hasattr(self.game.objective_manager, 'player_money'):
                # Don't actually reduce - just track debt
                pass

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        # All courthouse scenes are dialogue-only
        return True

    def _get_dialogue_characters(self):
        """Determine which characters should be shown for current dialogue"""
        if not self.dialogue_box.active:
            return None, None, None

        speaker = self.dialogue_box.current_speaker
        phase = self.current_objective_phase

        # Map speaker to character
        speaking_char = self.SPEAKER_TO_CHARACTER.get(speaker) if speaker else None

        # Determine character positions based on scene
        left_char = 'player'  # Player always on left
        right_char = None

        # Determine right character based on phase
        if phase in ['courthouse_queue']:
            right_char = 'officer' if speaker in ['Security Guard'] else 'coworker'
        elif phase in ['court_forms']:
            right_char = 'clerk'
        elif phase in ['wrong_courtroom']:
            right_char = 'officer'
        elif phase in ['face_judge', 'court_fine', 'dispute_denied']:
            right_char = 'judge'
        elif phase == 'courthouse_reflection':
            right_char = None  # Solo reflection

        return left_char, right_char, speaking_char

    def _get_character_emotion(self, char_id):
        """Get emotion for a character in current context"""
        phase = self.current_objective_phase
        if phase in self.CONTEXT_EMOTIONS:
            return self.CONTEXT_EMOTIONS[phase].get(char_id, Emotion.NEUTRAL)
        return Emotion.NEUTRAL

    def draw(self, screen):
        """Draw courthouse interior with portrait system"""
        super().draw(screen)

        # Add visual atmosphere based on scene
        if self.current_objective_phase in ['face_judge', 'court_fine', 'dispute_denied']:
            # Oppressive atmosphere in courtroom
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.set_alpha(30)
            overlay.fill((20, 20, 40))  # Dark blue-gray
            screen.blit(overlay, (0, 0))

        elif self.current_objective_phase == 'courthouse_reflection':
            # Sunset/contemplative atmosphere
            gradient = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            for y in range(self.SCREEN_HEIGHT):
                # Orange to purple gradient
                r = int(80 - (y / self.SCREEN_HEIGHT) * 40)
                g = int(40 - (y / self.SCREEN_HEIGHT) * 20)
                b = int(60 + (y / self.SCREEN_HEIGHT) * 20)
                pygame.draw.line(gradient, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))
            gradient.set_alpha(40)
            screen.blit(gradient, (0, 0))

        # Draw portraits during dialogue
        if self.dialogue_box.active:
            left_char, right_char, speaking = self._get_dialogue_characters()

            if left_char:
                left_emotion = self._get_character_emotion(left_char)
                self.portrait_renderer.draw_portrait(
                    screen, left_char, 'left',
                    emotion=left_emotion,
                    is_speaking=(speaking == left_char)
                )

            if right_char:
                right_emotion = self._get_character_emotion(right_char)
                self.portrait_renderer.draw_portrait(
                    screen, right_char, 'right',
                    emotion=right_emotion,
                    is_speaking=(speaking == right_char)
                )

        # Show debt counter during/after fine scene
        if self.current_objective_phase in ['court_fine', 'dispute_denied', 'courthouse_reflection']:
            self.draw_debt_counter(screen)

    def draw_debt_counter(self, screen):
        """Draw the running debt total"""
        font = pygame.font.Font(None, 36)
        debt_text = font.render(f"DEBT: ${self.fine_amount}", True, (255, 80, 80))
        debt_rect = debt_text.get_rect(topright=(self.SCREEN_WIDTH - 30, 30))

        # Background
        bg_rect = debt_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(screen, (255, 80, 80), bg_rect, 2)

        screen.blit(debt_text, debt_rect)
