import math
import os
import pygame

from src.interiors.generic_interior import GenericInterior
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE


class InitialRoomInterior(GenericInterior):
    """Warm introductory bedroom scene with parents and task prompts."""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Start player near the foot of the bed facing parents
        self.player_x = 9
        self.player_y = max(0, self.room_height - 3)
        self.target_x = self.player_x
        self.target_y = self.player_y
        self.is_moving = False
        self.player_direction = "up"

        # Conversation script
        self.dialogue = [
            ("Tia Renee", "Happy birthday, baby. Eighteen comes fast, huh?"),
            ("Mr. Ellis", "We wish we could keep you here, but the program says tonight is it."),
            ("Tia Renee", "We stuffed the good duffel with toiletries and your transit card. Promise you’ll eat."),
            ("Mr. Ellis", "Head to Housing Services first thing. Officer Diaz said they'd be ready for you."),
            ("Player", "Okay... I'll check in and text once I'm there. I love you both.")
        ]
        self.dialogue_index = 0
        self.conversation_active = True

        # Parents positioned near the head of the bed
        self.parents = [
            {
                "name": "Tia Renee",
                "pos": (8, 5),
                "surface": self._load_character_sprite(4, 6)
            },
            {
                "name": "Mr. Ellis",
                "pos": (10, 5),
                "surface": self._load_character_sprite(12, 2)
            }
        ]
        self.npc_font = pygame.font.Font(None, 20)

        # Interaction markers and timers
        self.highlight_timer = 0.0
        self.duffel_pos = (9, 7)
        self.wallet_pos = (11, 6)
        self.phone_pos = (12, 6)
        self.pack_started = False

        # Event system state
        self.events_started = set()
        self.events_completed = set()
        self.active_event = None
        self.last_objective_id = self.current_objective_id()

        self.event_definitions = {
            "packed_belongings": {
                "type": "interactive",
                "pos": self.duffel_pos,
                "label": "Pack your life (E)",
                "action": "packing",
                "advance_objective": False
            },
            "cash_reality": {
                "type": "interactive",
                "pos": self.wallet_pos,
                "label": "Count what's left (E)",
                "title": "What Remains",
                "slides": [
                    "$73 in crumpled bills—bus fare, meals, everything.",
                    "A transit card with $18 left. That and the duffel are the safety net.",
                    "No co-signer, no savings, no backup—just today."
                ]
            },
            "first_night": {
                "type": "interactive",
                "pos": self.phone_pos,
                "label": "Text Sarah (E)",
                "title": "Nowhere Tonight",
                "slides": [
                    "Sarah: \"You can crash for three nights. Parents can't know.\"",
                    "You promise to be invisible. The countdown toward the street starts now."
                ]
            },
            "sarah_couch_rules": {
                "type": "auto",
                "title": "House Rules",
                "slides": [
                    "Out by 8 AM. No kitchen. No guests. Pretend you were never here.",
                    "Gratitude knots with panic—couch-surfing has a timer."
                ]
            },
            "mike_couch_unsafe": {
                "type": "auto",
                "title": "Unsafe Offer",
                "slides": [
                    "Mike: \"You can stay, but my roommates party until sunrise.\"",
                    "You weigh exhaustion against safety and keep moving."
                ]
            },
            "couch_exhausted": {
                "type": "auto",
                "title": "Couch to Couch",
                "slides": [
                    "Fourth couch in ten days. Every goodbye sounds like \"don't come back.\"",
                    "Kindness is finite. You learn to sleep lightly and pack faster."
                ]
            },
            "apartment_search": {
                "type": "auto",
                "title": "Apartment Listings",
                "slides": [
                    "Every listing demands 3× rent, 650 credit, proof of income.",
                    "You refresh the feed anyway. Hope feels like work."
                ]
            },
            "viewing_scheduled": {
                "type": "auto",
                "title": "Scheduling Conflict",
                "slides": [
                    "Only viewing: 2 PM. Your shift starts at 3.",
                    "Lose the shift, lose the job. Skip the viewing, stay homeless."
                ]
            },
            "application_fee": {
                "type": "auto",
                "title": "Application Fee",
                "slides": [
                    "Non-refundable $45 fee. More than half of what you have left.",
                    "You pay anyway. Optimism costs money."
                ]
            },
            "cosigner_needed": {
                "type": "auto",
                "title": "Need a Co-Signer",
                "slides": [
                    "\"Do you have a parent or guardian who can co-sign?\"",
                    "Silence answers for you. The agent moves to the next applicant."
                ]
            },
            "application_denied": {
                "type": "auto",
                "title": "Denied",
                "slides": [
                    "Email: \"Insufficient income history.\"",
                    "Two weeks of paychecks don't count enough to unlock a door."
                ]
            },
            "facebook_roommates": {
                "type": "auto",
                "title": "Roommate Post",
                "slides": [
                    "You flood every roommate group: \"18, working, clean, need room ASAP.\"",
                    "Each refresh is a prayer with Wi-Fi."
                ]
            },
            "alex_response": {
                "type": "auto",
                "title": "Sketchy Offer",
                "slides": [
                    "Alex replies: $600, cash only, no lease, move tonight.",
                    "Red flags everywhere, but the street is worse."
                ]
            },
            "move_in_alex": {
                "type": "auto",
                "title": "Cash for Keys",
                "slides": [
                    "You hand over the last $200 for a room with no paper trail.",
                    "Sleep with your shoes by the bed—just in case."
                ]
            },
            "work_schedule_conflict": {
                "type": "auto",
                "title": "Shift Collides",
                "slides": [
                    "Housing offices open 9–3. Your manager schedules you 8–4.",
                    "You choose between keeping the job and chasing paperwork."
                ]
            },
            "fired_for_absence": {
                "type": "auto",
                "title": "Fired",
                "slides": [
                    "You miss one shift for the TLP interview.",
                    "Manager: \"We need reliable people.\" The job disappears."
                ]
            },
            "no_address_job": {
                "type": "auto",
                "title": "Address Required",
                "slides": [
                    "Applications demand a current address. The shelter won't share theirs.",
                    "You stare at the blank field, wondering whether honesty is worth hunger."
                ]
            },
            "deposit_math": {
                "type": "auto",
                "title": "The Math",
                "slides": [
                    "First month plus deposit: $1,450. You make $12 an hour, twenty hours a week.",
                    "The math says no. The landlord says next."
                ]
            },
            "id_expired": {
                "type": "auto",
                "title": "Expired ID",
                "slides": [
                    "Your ID lapses. DMV wants proof of address. Housing wants valid ID.",
                    "Loops inside loops. You photocopy what you can and keep receipts."
                ]
            },
            "phone_shutoff": {
                "type": "auto",
                "title": "Disconnected",
                "slides": [
                    "Phone shuts off—no callbacks, no interview confirmations, no emergency number.",
                    "You pace outside cafes for free Wi-Fi and pray employers read email."
                ]
            },
            "alex_eviction": {
                "type": "auto",
                "title": "Risk of Eviction",
                "slides": [
                    "Roommate vanishes. Three-day pay-or-quit taped to the door.",
                    "No lease means no rights. You're back to bags and favors."
                ]
            },
            "shelter_search": {
                "type": "auto",
                "title": "No Vacancies",
                "slides": [
                    "Hotlines loop: 'Full.' 'Try tomorrow.' 'Need 90 days sober.'",
                    "You call the next number, and the next, until batteries blink red."
                ]
            },
            "youth_shelter": {
                "type": "auto",
                "title": "Youth Shelter",
                "slides": [
                    "One youth bed opens. Curfew 8 PM, out by 6 AM, three-night max.",
                    "You sign in with a Sharpie and guard the locker key while you sleep."
                ]
            },
            "shelter_rules": {
                "type": "auto",
                "title": "Shelter Reality",
                "slides": [
                    "Your bag is rummaged while you sleep; your jacket disappears.",
                    "Miss curfew once and you're banned. Safety isn't part of the rules."
                ]
            },
            "storage_unit": {
                "type": "auto",
                "title": "Storage Locker",
                "slides": [
                    "You rent a five-by-five. Everything you own fits behind a metal door.",
                    "Every payment is a tax on not having housing."
                ]
            },
            "tlp_discovery": {
                "type": "auto",
                "title": "Transitional Hope",
                "slides": [
                    "Your caseworker whispers about the Transitional Living Program.",
                    "18-24 months if you qualify. If there’s space. If the paperwork lands."
                ]
            },
            "tlp_application": {
                "type": "auto",
                "title": "Paperwork Mountain",
                "slides": [
                    "Twenty-page application: proof of homelessness, references, background checks.",
                    "You gather every document you own and hope it’s enough."
                ]
            },
            "tlp_interview": {
                "type": "auto",
                "title": "Interview Collision",
                "slides": [
                    "Interview Tuesday at 10 AM—same time as your shift.",
                    "Miss the interview, lose housing. Miss the shift, risk the job."
                ]
            },
            "tlp_waitlist": {
                "type": "auto",
                "title": "Waitlisted",
                "slides": [
                    "Waitlist: three to six months. Transitional bed ends in weeks.",
                    "No next step on paper. You plan for worst weather and worst news."
                ]
            },
            "winter_prep": {
                "type": "auto",
                "title": "No Next Step",
                "slides": [
                    "Shelter warns: once weather warms, bed isn't guaranteed.",
                    "You start hoarding bus fare and clean socks, just in case."
                ]
            },
            "shower_access": {
                "type": "auto",
                "title": "Shower",
                "slides": [
                    "A seven-day gym trial means a hot shower and clean clothes.",
                    "You feel human long enough to send more applications."
                ]
            },
            "food_bank": {
                "type": "auto",
                "title": "Food Bank",
                "slides": [
                    "Three-hour wait for groceries you can't refrigerate.",
                    "You trade cans for ready-to-eat and promise to stretch every bite."
                ]
            },
            "library_refuge": {
                "type": "auto",
                "title": "Library Refuge",
                "slides": [
                    "Heat, outlets, free Wi-Fi—but no naps allowed.",
                    "You apply for ten jobs while fighting to stay awake."
                ]
            },
            "three_months_later": {
                "type": "auto",
                "title": "Day 90",
                "slides": [
                    "Ninety days unhoused. Twenty pounds gone. Friends stop calling.",
                    "You whisper it's temporary, even when doubt is louder."
                ]
            },
            "health_declining": {
                "type": "auto",
                "title": "Health Slipping",
                "slides": [
                    "Two-week chest cold. No rest, no clinic, no co-pay money.",
                    "You cough through interviews and hope nobody notices."
                ]
            },
            "giving_up": {
                "type": "auto",
                "title": "Rock Bottom",
                "slides": [
                    "Every system said no. The bench feels safer than asking again.",
                    "You count to ten and decide to see sunrise anyway."
                ]
            },
            "outreach_worker": {
                "type": "auto",
                "title": "Street Outreach",
                "slides": [
                    "James from Youth Services hands you food and a phone number.",
                    "You let yourself believe someone might stick around."
                ]
            },
            "rapid_rehousing": {
                "type": "auto",
                "title": "Rapid Rehousing",
                "slides": [
                    "Program covers deposit and three months rent if you can maintain it after.",
                    "You sign, cry, and budget on the back of the brochure."
                ]
            },
            "studio_apartment": {
                "type": "auto",
                "title": "Keys",
                "slides": [
                    "Studio apartment. Your name on the lease. A key that turns for you.",
                    "You stand in the doorway until relief feels real."
                ]
            },
            "first_night_housed": {
                "type": "auto",
                "title": "Temporary Room",
                "slides": [
                    "You finally get a door to close. No lease, no guarantees.",
                    "Gratitude and fear share the pillow."
                ]
            },
            "six_months_stable": {
                "type": "auto",
                "title": "Still Counting",
                "slides": [
                    "Six months later you still count days and dollars.",
                    "Stability feels like a guest pass, never a lease."
                ]
            },
            "part1_complete": {
                "type": "auto",
                "title": "Chapter One",
                "slides": [
                    "Chapter One ends. The systems that pushed you out are still intact.",
                    "Breathe. Save. Keep fighting for the next door."
                ]
            }
        }

        self.interior_event_ids = {
            "packed_belongings",
            "cash_reality",
            "first_night",
            "sarah_couch_rules"
        }

    def _load_character_sprite(self, col, row):
        """Extract and scale character frame from the Modern Interiors sheet."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        sheet_path = os.path.join(
            base_dir,
            "assets",
            "moderninteriors-win",
            "2_Characters",
            "Character_Generator",
            "0_Premade_Characters",
            "16x16",
            "Premade_Character_01.png"
        )
        try:
            sheet = pygame.image.load(sheet_path).convert_alpha()
            sprite = pygame.Surface((16, 32), pygame.SRCALPHA)
            sprite.blit(sheet, (0, 0), pygame.Rect(col * 16, row * 32, 16, 32))
            return pygame.transform.scale(sprite, (TILE_SIZE, TILE_SIZE * 2))
        except Exception as exc:
            print(f"Failed to load parent sprite: {exc}")
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (200, 160, 140), fallback.get_rect(), border_radius=6)
            return fallback

    # --------------------------------------------------------------------- #
    # Scene state helpers
    # --------------------------------------------------------------------- #
    def current_objective_id(self):
        current = self.game.objective_manager.get_current_objective()
        return current.id if current else None

    def _packing_activity_active(self):
        pack_activity = getattr(self.game.objective_manager, "packing", None)
        return bool(pack_activity and getattr(pack_activity, "active", False))

    # --------------------------------------------------------------------- #
    # Overrides
    # --------------------------------------------------------------------- #
    def enter(self):
        super().enter()
        self.conversation_active = True
        self.dialogue_index = 0
        self.pack_started = False
        self.active_event = None
        self.last_objective_id = self.current_objective_id()

    def handle_input(self, keys):
        if self.conversation_active or self.active_event or self._packing_activity_active():
            return
        super().handle_input(keys)

    def handle_event(self, event):
        if self.active_event:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                if self.active_event['index'] + 1 >= len(self.active_event['slides']):
                    self._complete_active_event()
                else:
                    self.active_event['index'] += 1
            return

        # Check if UniversalActivityManager has active activity - MUST be checked first
        if (hasattr(self.game, 'objective_manager') and
            hasattr(self.game.objective_manager, 'activity_manager')):
            activity_manager = self.game.objective_manager.activity_manager
            if activity_manager and activity_manager.is_handling_events():
                # Route ALL events to activity first
                activity_manager.handle_event(event)
                return  # Don't process interior events when activity is active

        # Legacy activity handling (for backward compatibility)
        activity = self.game.objective_manager.current_activity if hasattr(self.game, "objective_manager") else None
        packing_active = self._packing_activity_active()

        if event.type == pygame.KEYDOWN:
            if self.conversation_active:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue):
                        self.conversation_active = False
                        if self.current_objective_id() == "housing_intro":
                            self.game.objective_manager.advance_to_next_objective()
                    return
            elif packing_active and activity and hasattr(activity, "handle_key"):
                activity.handle_key(event.key)
                return
            elif event.key == pygame.K_e and self._try_trigger_interaction():
                return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if packing_active and activity and hasattr(activity, "handle_mouse_click"):
                activity.handle_mouse_click(event.pos, event.button)
                return

        elif event.type == pygame.MOUSEBUTTONUP:
            if packing_active and activity and hasattr(activity, "handle_mouse_release"):
                activity.handle_mouse_release(event.pos, event.button)
                return

        elif event.type == pygame.MOUSEMOTION:
            if packing_active and activity and hasattr(activity, "handle_mouse_motion"):
                activity.handle_mouse_motion(event.pos)
                return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if hasattr(self, 'doors') and isinstance(self.doors, list):
                px, py = round(self.player_x), round(self.player_y)
                for door in self.doors:
                    if isinstance(door, list) and len(door) >= 2:
                        dx, dy = door[0], door[1]
                        if abs(px - dx) <= 1 and abs(py - dy) <= 1:
                            if "sarah_couch_rules" not in self.events_completed:
                                if hasattr(self.game.objective_manager, 'show_notification'):
                                    self.game.objective_manager.show_notification(
                                        "Finish the conversation with your parents first."
                                    )
                                return

        super().handle_event(event)

    def update(self, dt):
        self.highlight_timer += dt

        current_id = self.current_objective_id()
        if current_id != self.last_objective_id:
            self.last_objective_id = current_id

        if current_id in self.interior_event_ids and not self.conversation_active and not self.active_event \
                and not self._packing_activity_active():
            event = self.event_definitions.get(current_id)
            if event and event.get("type") == "auto" and current_id not in self.events_started:
                self.start_event(current_id)

        if self.pack_started and not self._packing_activity_active() and current_id != "packed_belongings":
            self.pack_started = False

        super().update(dt)

    # --------------------------------------------------------------------- #
    # Interactions
    # --------------------------------------------------------------------- #
    def _try_trigger_interaction(self):
        objective_id = self.current_objective_id()
        if objective_id not in self.interior_event_ids:
            return False
        event = self.event_definitions.get(objective_id)
        if not event or event.get("type") != "interactive":
            return False
        if event.get("action") != "packing" and objective_id in self.events_started:
            return False
        pos = event.get("pos")
        if not pos:
            return False
        px, py = round(self.player_x), round(self.player_y)
        if abs(px - pos[0]) <= 1 and abs(py - pos[1]) <= 1:
            self.start_event(objective_id)
            return True
        return False

    def _start_packing_activity(self):
        pack_activity = getattr(self.game.objective_manager, "packing", None)
        if not pack_activity:
            return
        self.pack_started = True
        if hasattr(pack_activity, "apartment_ref"):
            pack_activity.apartment_ref = self
        pack_activity.start()
        self.game.objective_manager.current_activity = pack_activity

    def start_event(self, event_id):
        if event_id not in self.interior_event_ids:
            return

        event = self.event_definitions.get(event_id)
        if not event:
            return

        if event_id in self.events_started and event.get("action") != "packing":
            return

        self.events_started.add(event_id)

        if event.get("action") == "packing":
            self._start_packing_activity()
            return

        slides = event.get("slides", [])
        if not slides:
            self.events_completed.add(event_id)
            if event.get("advance_objective", True):
                self.game.objective_manager.advance_to_next_objective()
            return

        self.active_event = {
            "id": event_id,
            "slides": slides,
            "index": 0,
            "title": event.get("title"),
            "advance": event.get("advance_objective", True)
        }

    def _complete_active_event(self):
        if not self.active_event:
            return
        event_id = self.active_event["id"]
        if self.active_event.get("advance", True):
            self.game.objective_manager.advance_to_next_objective()
        self.events_completed.add(event_id)
        self.active_event = None
        if event_id == "sarah_couch_rules":
            self.exit()
        elif event_id == "cash_reality":
            if self.current_objective_id() == "first_night":
                self.start_event("first_night")
        elif event_id == "first_night":
            if self.current_objective_id() == "sarah_couch_rules":
                self.start_event("sarah_couch_rules")

    def mark_event_completed(self, event_id):
        self.events_started.add(event_id)
        self.events_completed.add(event_id)
        if event_id == "packed_belongings":
            self.pack_started = False
            if self.current_objective_id() == "cash_reality":
                self.start_event("cash_reality")

    # --------------------------------------------------------------------- #
    # Drawing helpers
    # --------------------------------------------------------------------- #
    def _draw_parents(self, screen, offset_x, offset_y):
        for parent in self.parents:
            tile_x, tile_y = parent["pos"]
            screen_x = int(tile_x * self.TILE_SIZE - self.camera_x + offset_x)
            screen_y = int((tile_y - 1) * self.TILE_SIZE - self.camera_y + offset_y)
            screen.blit(parent["surface"], (screen_x, screen_y))

            name_label = self.npc_font.render(parent["name"], True, (234, 242, 255))
            label_rect = name_label.get_rect(midbottom=(screen_x + TILE_SIZE // 2, screen_y - 6))
            pygame.draw.rect(screen, (24, 28, 40, 200), label_rect.inflate(18, 8), border_radius=6)
            screen.blit(name_label, label_rect)

    def _draw_dialogue_box(self, screen):
        if not self.conversation_active or self.dialogue_index >= len(self.dialogue):
            return

        speaker, line = self.dialogue[self.dialogue_index]
        box_width = SCREEN_WIDTH - 120
        box_height = 150

        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (16, 20, 31, 232), (0, 0, box_width, box_height), border_radius=18)
        pygame.draw.rect(box_surf, (120, 170, 255, 180), (0, 0, box_width, box_height), 2, border_radius=18)

        title_font = pygame.font.Font(None, 32)
        body_font = pygame.font.Font(None, 26)
        title = title_font.render(speaker, True, (212, 224, 255))
        box_surf.blit(title, (28, 20))

        words = line.split()
        lines = []
        current = []
        for word in words:
            test_line = " ".join(current + [word])
            if body_font.size(test_line)[0] <= box_width - 56:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))

        for idx, text in enumerate(lines[:3]):
            text_surface = body_font.render(text, True, (240, 244, 255))
            box_surf.blit(text_surface, (28, 64 + idx * 30))

        prompt_font = pygame.font.Font(None, 22)
        prompt = prompt_font.render("Press SPACE to continue", True, (180, 200, 255))
        box_surf.blit(prompt, (box_width - prompt.get_width() - 28, box_height - 42))

        screen.blit(box_surf, (60, SCREEN_HEIGHT - box_height - 60))

    def _draw_story_overlay(self, screen):
        if not self.active_event:
            return

        slides = self.active_event["slides"]
        index = min(self.active_event["index"], len(slides) - 1)
        title = self.active_event.get("title")

        box_width = SCREEN_WIDTH - 160
        box_height = 240
        overlay = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (18, 22, 35, 235), (0, 0, box_width, box_height), border_radius=18)
        pygame.draw.rect(overlay, (126, 174, 255, 180), (0, 0, box_width, box_height), 2, border_radius=18)

        y_offset = 32
        if title:
            title_font = pygame.font.Font(None, 32)
            title_surface = title_font.render(title, True, (210, 224, 255))
            overlay.blit(title_surface, (32, y_offset))
            y_offset += 40

        body_font = pygame.font.Font(None, 26)
        for line in slides[index].split("\n"):
            text_surface = body_font.render(line, True, (232, 238, 252))
            overlay.blit(text_surface, (32, y_offset))
            y_offset += 36

        prompt_font = pygame.font.Font(None, 22)
        prompt = prompt_font.render("Press SPACE to continue", True, (190, 205, 235))
        overlay.blit(prompt, (box_width - prompt.get_width() - 32, box_height - 44))

        screen.blit(overlay, (80, SCREEN_HEIGHT - box_height - 80))

    def _draw_highlights(self, screen, offset_x, offset_y):
        if self.conversation_active or self.active_event or self._packing_activity_active():
            return

        objective_id = self.current_objective_id()
        event = self.event_definitions.get(objective_id)
        if not event or event.get("type") != "interactive":
            return
        if event.get("action") != "packing" and objective_id in self.events_started:
            return
        if event.get("action") == "packing" and self.pack_started:
            return

        pos = event.get("pos")
        if not pos:
            return

        pulse = (math.sin(self.highlight_timer * 3) + 1) * 0.5
        glow_alpha = int(110 + 90 * pulse)
        glow_color = (126, 174, 255, glow_alpha)

        tile_x, tile_y = pos
        center_x = tile_x * self.TILE_SIZE - self.camera_x + offset_x + self.TILE_SIZE // 2
        center_y = tile_y * self.TILE_SIZE - self.camera_y + offset_y + self.TILE_SIZE // 2

        radius = int(self.TILE_SIZE * (1.2 + 0.1 * pulse))
        halo = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, glow_color, (radius, radius), radius)
        screen.blit(halo, (center_x - radius, center_y - radius), special_flags=pygame.BLEND_PREMULTIPLIED)

        badge_font = pygame.font.Font(None, 20)
        label = event.get("label", "Interact (E)")
        badge_text = badge_font.render(label, True, (18, 22, 33))
        badge_rect = badge_text.get_rect()
        badge_rect.x = center_x - badge_rect.width // 2 - 10
        badge_rect.y = center_y + radius - 4
        pygame.draw.rect(screen, (237, 244, 255), badge_rect.inflate(20, 10), border_radius=12)
        screen.blit(badge_text, (badge_rect.x + 10, badge_rect.y + 5))

    # --------------------------------------------------------------------- #
    # Rendering
    # --------------------------------------------------------------------- #
    def draw(self, screen):
        room_pixel_width = self.room_width * self.TILE_SIZE
        room_pixel_height = self.room_height * self.TILE_SIZE
        offset_x = (SCREEN_WIDTH - room_pixel_width) // 2
        offset_y = (SCREEN_HEIGHT - room_pixel_height) // 2

        screen.fill((40, 40, 40))

        for layer_name in ["floor", "walls", "furniture", "decor"]:
            if layer_name in self.layers:
                layer = self.layers[layer_name]
                for y, row in enumerate(layer):
                    for x, tile_info in enumerate(row):
                        if tile_info:
                            tile_surf = self.get_tile_surface(tile_info)
                            if tile_surf:
                                screen_x = x * self.TILE_SIZE - self.camera_x + offset_x
                                screen_y = y * self.TILE_SIZE - self.camera_y + offset_y
                                if -self.TILE_SIZE <= screen_x <= SCREEN_WIDTH and -self.TILE_SIZE <= screen_y <= SCREEN_HEIGHT:
                                    screen.blit(tile_surf, (screen_x, screen_y))

        self._draw_parents(screen, offset_x, offset_y)
        self._draw_highlights(screen, offset_x, offset_y)

        player_screen_x = int(self.player_x * self.TILE_SIZE - self.camera_x + offset_x)
        player_screen_y = int(self.player_y * self.TILE_SIZE - self.camera_y + offset_y - TILE_SIZE)
        if self.player_sprite and hasattr(self.player_sprite, "animations"):
            anim_name = "idle_up" if (self.conversation_active or self.active_event or self._packing_activity_active()) else (
                f"walk_{self.player_direction}" if self.player_walking else f"idle_{self.player_direction}"
            )
            frames = self.player_sprite.animations.get(anim_name)
            if frames:
                frame = frames[self.animation_frame % len(frames)]
                screen.blit(frame, (player_screen_x, player_screen_y))
        else:
            pygame.draw.circle(screen, (255, 255, 0),
                               (player_screen_x + TILE_SIZE // 2, player_screen_y + TILE_SIZE // 2), 12)

        for door in self.doors:
            if isinstance(door, list) and len(door) >= 2:
                door_x, door_y = door[:2]
                center_x = door_x * self.TILE_SIZE - self.camera_x + offset_x + self.TILE_SIZE // 2
                center_y = door_y * self.TILE_SIZE - self.camera_y + offset_y + self.TILE_SIZE
                radius = int(self.TILE_SIZE * 0.85)
                points = []
                for angle in range(0, 181, 3):
                    rad = math.radians(angle)
                    x = center_x + radius * math.cos(rad)
                    y = center_y - radius * math.sin(rad)
                    points.append((x, y))
                if len(points) > 1:
                    pygame.draw.lines(screen, (255, 220, 100, 100), False, points, 2)

        if not self.conversation_active and not self.active_event and not self._packing_activity_active():
            ui_font = pygame.font.Font(None, 24)
            text = ui_font.render("Press E at the door when you're ready to step out.", True, (235, 240, 250))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 42))

        self._draw_dialogue_box(screen)
        self._draw_story_overlay(screen)

    def exit(self):
        """Exit back to the map near the 8,11 doorway."""
        self.active = False
        if self.building_pos:
            self.game.player.x = self.building_pos[0]
            self.game.player.y = self.building_pos[1] + 1
            self.game.player.pixel_x = self.game.player.x * TILE_SIZE
            self.game.player.pixel_y = self.game.player.y * TILE_SIZE
            self.game.player.target_x = self.game.player.pixel_x
            self.game.player.target_y = self.game.player.pixel_y
            self.game.player.moving = False
            if hasattr(self.game, "update_camera"):
                self.game.update_camera()
        self.game.current_interior = None
