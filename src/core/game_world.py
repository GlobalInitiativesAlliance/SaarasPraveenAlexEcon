import pygame
import json
import random
import os
import math
from src.constants import *
from src.activities import *
from src.core.debug_logger import dprint
from src.core.progress_manager import get_progress_manager


class ObjectiveManager:
    """Manages game objectives and progression"""
    
    # Define notification objectives that don't need position markers
    NOTIFICATION_OBJECTIVES = [
        # Part 1 - ALL REMOVED so navigation arrows show for entire part
        # Now every Part 1 objective will have navigation arrows!
        # Original Part 1 objectives
        'housing_gameplay',
        'get_hired', 'manager_notice', 'wake_go_school',
        'document_checklist', 'burger_training',
        'come_back_tomorrow', 'apply_for_jobs', 'hired_burger_place',
        'day_off_notice', 'school_mandatory_meeting',
        'panic_scene', 'learn_ilp_officer',
        'ilp_callback', 'manager_choice',
        'part1_complete',  # Part 1 transition should be automatic
        # Part 2 - Housing Services narrative objectives
        'part2_intro', 'case_worker_meeting', 'tlp_requirements', 'mandatory_classes',
        'life_skills_workshop', 'application_submitted', 'tlp_approval', 'pack_belongings',
        'meet_roommate', 'first_night_tlp', 'three_weeks_later', 'rent_increase',
        'impossible_budget', 'emergency_meeting', 'payment_plan', 'second_job_search',
        'new_roommate_arrives', 'roommate_conflict', 'mike_evicted', 'six_months_in',
        'housing_search_again', 'savings_depleted', 'year_in_tlp', 'final_warning',
        'program_ending', 'emergency_extension', 'couch_surfing_return', 'part2_reflection',
        'part2_complete',

    ]

    def __init__(self, game):
        self.game = game
        self.objectives = []
        self.current_objective_index = 0
        self.active = True
        self.game_time = "8:00 AM"
        self.current_day = 1
        self.game_part = 1
        self.player_money = 0.0

        # Initialize professional UI system
        try:
            from src.ui.ui_manager import GameUIManager
            self.ui_manager = GameUIManager(game)
            self.use_modern_ui = True
        except ImportError:
            # Fallback to previous UI if available
            try:
                from src.ui.objective_ui_integration import ObjectiveUIManager
                self.ui_manager = ObjectiveUIManager(game)
                self.use_modern_ui = True
            except ImportError:
                self.ui_manager = None
                self.use_modern_ui = False

        # Building locations (will be set after map loads)
        self.foster_home = None
        self.community_center = None
        self.tlp_apartment = None
        self.workplace = None
        self.school = None
        self.jobs_center = None
        self.burger_place = None
        
        # Universal activity manager
        from shared.universal_activity_manager import UniversalActivityManager
        self.activity_manager = UniversalActivityManager(game)

        # Part transition manager for clean state management
        from src.core.part_transition_manager import PartTransitionManager
        self.part_transition_manager = PartTransitionManager(game)
        # Ensure the part transition manager has the correct reference to this objective manager
        self.part_transition_manager.objective_manager = self

        # Part 1 Activities
        self.workplace_quiz = None
        self.job_application = None
        self.pizza_game = None

        # Part 2 Activities (original)
        self.current_activity = None
        self.quiz = TenantRightsQuiz(self)
        self.packing = PackingActivity(self)
        self.life_skills_workshop = LifeSkillsWorkshop(self)
        self.emergency_notice = EmergencyNoticeActivity(self)
        self.document_checklist = DocumentChecklistActivity(self)

        # Mini-games removed - will be integrated into interior rooms

        # PERFORMANCE: Pre-cached surfaces for marker rendering
        # Avoids creating new surfaces every frame
        self._marker_glow_surf = None
        self._init_marker_cache()

        # Initialize Part 1 activities
        self.init_part1_activities()

        # Initialize objectives
        self.setup_objectives()
        
        # Notification display state
        self.showing_notification = False
        self.notification_text = ""
        self.notification_timer = 0
        self.notification_alpha = 255

    def init_part1_activities(self):
        """Initialize Part 1 specific activities"""
        self.workplace_quiz = WorkplaceQuiz(self)
        self.job_application = JobApplicationActivity(self)
        self.pizza_game = PizzaMakingGame(self)
        self.firing_scene = FiringScene(self)
        self.emergency_scene = SchoolEmergencyScene(self)
        self.transition_scene = TransitionScene(self)

        # New activities for complete employment timeline
        self.burger_game = BurgerMakingGame(self)
        self.document_checklist_work = DocumentChecklistWork(self)
        self.burger_training = BurgerTrainingActivity(self)
        self.job_listings = JobListingsActivity(self)
        self.manager_notice = ManagerNoticeActivity(self)
        self.panic_scene = PanicSceneActivity(self)
        self.ilp_officer_call = ILPOfficerCallActivity(self)
        self.manager_choice = ManagerChoiceActivity(self)

    def load_part2_objectives(self):
        """Load Part 2 legal system objectives and reset to start (was Part 3)"""
        self.setup_part2_objectives()
        self.current_objective_index = 0
        print("Part 2 Legal System objectives loaded and ready to start")

    def load_part3_objectives(self):
        """Load Part 3 healthcare objectives and reset to start (was Part 4)"""
        self.setup_part3_objectives()
        self.current_objective_index = 0
        print("Part 3 Healthcare Crisis objectives loaded and ready to start")

    def load_part4_objectives(self):
        """Load Part 4 education objectives and reset to start (was Part 5)"""
        self.setup_part4_objectives()
        self.current_objective_index = 0
        print("Part 4 Education Journey objectives loaded and ready to start")

    def load_part5_objectives(self):
        """Load Part 5 systemic barriers objectives and reset to start (was Part 6)"""
        self.setup_part5_objectives()
        self.current_objective_index = 0
        print("Part 5 Systemic Barriers objectives loaded and ready to start")

    def setup_objectives(self):
        """Create complete game objectives for the housing storyline"""
        if self.game_part == 1:
            # Try to use narrative objectives if available
            if hasattr(self.game, 'use_housing_objectives') and self.game.use_housing_objectives:
                try:
                    from part_1_housing_stability.objectives_narrative import get_part1_narrative_objectives
                    self.objectives = get_part1_narrative_objectives()
                    print("Loaded Part 1 Housing Narrative objectives")
                    return
                except ImportError:
                    print("Could not load narrative objectives, using default")

            self.setup_part1_objectives()
        elif self.game_part == 2:
            self.setup_part2_objectives()  # Legal System (was Part 3)
        elif self.game_part == 3:
            self.setup_part3_objectives()  # Healthcare Crisis (was Part 4)
        elif self.game_part == 4:
            self.setup_part4_objectives()  # Education (was Part 5)
        elif self.game_part == 5:
            self.setup_part5_objectives()  # Systemic Barriers (was Part 6)

    def setup_part1_objectives(self):
        """Create Part 1 objectives - Employment storyline"""
        # Check if we should use the new housing objectives

            
        # Otherwise use the original objectives
        self.objectives = [
            # Part 1 - School and Quiz
            GameObjective(
                "school_quiz",
                "Employment Rights Class",
                "Go to School for an employment rights quiz",
                None,
                "Press E to enter school"
            ),
            # Go to workplace after school
            GameObjective(
                "go_to_workplace",
                "Visit the Workplace",
                "Head to the workplace after attending school",
                None,
                "Press E to continue"
            ),
            # Job Application
            GameObjective(
                "workplace_apply",
                "Apply for Job",
                "Apply for a job at Tony's Pizza",
                None,
                "Press E to apply"
            ),
            # Get Hired
            GameObjective(
                "get_hired",
                "You're Hired!",
                "Congratulations! You got the job! Time to start your first shift",
                None,
                "Head to the pizza place to begin work"
            ),
            # Start Working
            GameObjective(
                "start_work",
                "First Day at Work",
                "Start your shift - time to make pizzas!",
                None,
                "Press E to start working"
            ),
            # Go Home after work
            GameObjective(
                "go_home_day1",
                "Return Home",
                "Head back home after your shift",
                None,
                "Press E when at home"
            ),
            # Manager tells you to be in office tomorrow
            GameObjective(
                "manager_notice",
                "Important Notice",
                "Your manager says: 'Be here tomorrow at 7 AM sharp!'",
                None,
                "Time to go home and rest"
            ),
            # Sleep
            GameObjective(
                "sleep_work",
                "Rest for Tomorrow",
                "Get some sleep for tomorrow's work",
                None,
                "Press E to sleep"
            ),
            # Day 2 - Wake up and go to school (time skip)
            GameObjective(
                "wake_go_school",
                "Morning Routine",
                "Wake up and go to school (time skip)",
                None,
                "Press E to continue"
            ),
            # School Emergency
            GameObjective(
                "school_emergency",
                "School Emergency!",
                "There's an emergency at school!",
                None,
                "Press E to handle emergency"
            ),
            # Late to Work
            GameObjective(
                "late_to_work",
                "Rush to Work",
                "You're late! Get to the workplace immediately",
                None,
                "Press E to enter"
            ),
            # Get Fired
            GameObjective(
                "get_fired",
                "Meeting with Manager",
                "Your manager fires you for missing the shift...",
                None,
                "Press E to continue"
            ),
            # Collect Pay
            GameObjective(
                "collect_pay",
                "Collect Final Paycheck",
                "You earned $71.24 for yesterday's work (minimum wage * 4 hours)",
                None,
                "Press E to collect"
            ),
            # Jobs Center
            GameObjective(
                "jobs_center",
                "Visit Jobs Center",
                "Go to the Jobs Center for help finding work",
                None,
                "Press E to enter"
            ),
            # Document Checklist
            GameObjective(
                "document_checklist",
                "Required Documents",
                "Check that you have: ID, SSN, Resume (Stay at Jobs Center)",
                None,
                "Press E to verify documents"
            ),
            # Burger Training Offer
            GameObjective(
                "burger_training",
                "Training Opportunity",
                "Burger Palace offers training! Head there now for training",
                None,
                "Go to Burger Palace"
            ),
            # Receive Training
            GameObjective(
                "receive_training",
                "Burger Training",
                "Enter Burger Palace to start your training",
                None,
                "Press E to enter Burger Palace"
            ),
            # Told to come back tomorrow
            GameObjective(
                "come_back_tomorrow",
                "Training Complete!",
                "Great work! Come back tomorrow at 4 PM for your first shift",
                None,
                "Head home to rest"
            ),
            # Go home and sleep
            GameObjective(
                "go_home_sleep_day2",
                "End of Day",
                "Go home and get some sleep for tomorrow's work",
                None,
                "Press E at home to sleep"
            ),
            # Day 3 - Go to school
            GameObjective(
                "day3_school",
                "Back to School",
                "Another day at school",
                None,
                "Press E to attend"
            ),
            # View job listings
            GameObjective(
                "view_job_listings",
                "Job Listings",
                "Check available job opportunities",
                None,
                "Press E to view listings"
            ),
            # Apply for jobs
            GameObjective(
                "apply_for_jobs",
                "Send Applications",
                "Apply to the burger restaurant job",
                None,
                "Press E to apply"
            ),
            # Get hired at burger place
            GameObjective(
                "hired_burger_place",
                "New Job!",
                "You got the burger restaurant job!",
                None,
                "Press E to continue"
            ),
            # Work at burger place
            GameObjective(
                "work_burger_place",
                "First Shift",
                "Start flipping burgers at your new job",
                None,
                "Press E to work"
            ),
            # Day off notice
            GameObjective(
                "day_off_notice",
                "Schedule Update",
                "You have tomorrow off - perfect for grocery shopping!",
                None,
                "Go grocery shopping next"
            ),
            # Grocery shopping
            GameObjective(
                "grocery_shopping_work",
                "Buy Groceries",
                "Use your earnings to buy food (meet calorie/health requirements)",
                None,
                "Press E to shop"
            ),
            # Return home from shopping
            GameObjective(
                "return_home_shopping",
                "Head Home",
                "Go back home with your groceries",
                None,
                "Press E when home"
            ),
            # Day 4 - School with mandatory meeting notice
            GameObjective(
                "school_mandatory_meeting",
                "Schedule Conflict!",
                "School has mandatory meeting tomorrow - but you have work!",
                None,
                "This is a problem..."
            ),
            # Panic about missing work
            GameObjective(
                "panic_scene",
                "Work Conflict!",
                "Oh no! You might get fired again for missing work!",
                None,
                "Press E to think of solution"
            ),
            # Learn about ILP officer
            GameObjective(
                "learn_ilp_officer",
                "Found a Solution!",
                "ILP officers can help foster youth with school-work conflicts",
                None,
                "Go home to call the ILP officer"
            ),
            # Call ILP officer
            GameObjective(
                "call_ilp_officer",
                "Contact ILP Officer",
                "Call your ILP officer for help",
                None,
                "Press E to make call"
            ),
            # ILP officer calls back
            GameObjective(
                "ilp_callback",
                "Problem Solved!",
                "ILP officer got you approved for tomorrow off!",
                None,
                "Go to work to talk with manager"
            ),
            # Choice: How to handle manager
            GameObjective(
                "manager_choice",
                "Decision Time",
                "Choose: Thank manager directly, do nothing, or let ILP handle it",
                None,
                "Press E to decide"
            ),
            # End of Part 1
            GameObjective(
                "part1_complete",
                "Part 1 Complete!",
                "You've learned about employment rights and advocacy!",
                None,
                "Press E to continue to Part 2"
            )
        ]

    def setup_part2_objectives(self):
        """Create Part 2 objectives - Legal System storyline (was Part 3)"""
        from part_3_legal_system.objectives import get_part3_objectives
        self.objectives = get_part3_objectives()
        print("Loaded Part 2 Legal System objectives")

    def setup_part3_objectives(self):
        """Create Part 3 objectives - Healthcare Crisis storyline (was Part 4)"""
        from part_4_healthcare.objectives import get_part4_objectives
        self.objectives = get_part4_objectives()
        print("Loaded Part 3 Healthcare Crisis objectives")

    def setup_part4_objectives(self):
        """Create Part 4 objectives - Education Access storyline (was Part 5)"""
        from part_5_education.objectives import get_part5_objectives
        self.objectives = get_part5_objectives()
        print("Loaded Part 4 Education Access objectives")

    def setup_part5_objectives(self):
        """Create Part 5 objectives - Systemic Barriers storyline (was Part 6)"""
        from part_6_systemic_barriers.objectives import get_part6_objectives
        self.objectives = get_part6_objectives()
        print("Loaded Part 5 Systemic Barriers objectives")

    def find_building_locations(self):
        """Find appropriate buildings for the storyline"""
        # Load building interior mappings
        import json
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        mappings_file = os.path.join(base_dir, "data", "maps", "building_interiors.json")

        building_interiors = {}
        if os.path.exists(mappings_file):
            try:
                with open(mappings_file, 'r') as f:
                    building_interiors = json.load(f)
                print(f"\nLoaded building interior mappings: {building_interiors}")
            except Exception as e:
                print(f"Error loading building interiors: {e}")

        # Define specific location mappings from building_interiors.json
        # Map room types to their coordinates
        room_locations = {
            'alex_apartment': (1, 5),  # Alex's apartment
            'library': (8, 11),
            'hospital': [(38, 23), (34, 31)],  # Two hospital locations
            'bad_studio': (3, 31),
            'bank': (12, 34),
            'classroom': [(54, 51), (27, 56)],  # Two classroom locations
            'emergency_shelter': (30, 11),
            'foster_home': (29, 39),
            'grocery_store': (39, 51),  # Fixed typo from JSON
            'mike': (54, 33),  # Mike's place
            'rental': (27, 52)
        }

        building_types = {
            'house': [],
            'bank': [],
            'building': [],
            'store': [],
            'school': [],
            'pizza': [],
            'apartment': [],
            'office': [],
            'grocery': []
        }

        # Scan the map for buildings
        for y in range(self.game.city_map.height):
            for x in range(self.game.city_map.width):
                tile_data = self.game.city_map.map_data[y][x]
                # Check for both regular buildings and buildings with backgrounds
                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, building_key, offset_x, offset_y, _ = tile_data
                    else:
                        _, building_key, offset_x, offset_y = tile_data

                    # Only store the top-left corner of buildings
                    if offset_x == 0 and offset_y == 0:
                        # Store in specific categories first
                        building_name_lower = building_key.lower()
                        found_specific = False

                        # Check for specific building types
                        for specific_type in ['school', 'pizza', 'apartment', 'office', 'grocery']:
                            if specific_type in building_name_lower:
                                building_types[specific_type].append((x, y))
                                found_specific = True
                                break

                        # Then check general categories
                        if not found_specific:
                            for btype in ['house', 'bank', 'building', 'store']:
                                if btype in building_name_lower:
                                    building_types[btype].append((x, y))
                                    break

        # Print found buildings for debugging
        print("\nFound buildings on map:")
        for btype, locations in building_types.items():
            if locations:
                print(f"  {btype}: {len(locations)} buildings")

        # DO NOT OVERRIDE COORDINATES FROM objectives_narrative.py
        # The narrative objectives already have their coordinates set
        if self.game_part == 1:
            # Part 1 - Using coordinates from objectives_narrative.py
            # Just set some location variables for reference, but don't override objective positions

            # School - for reference only
            self.school = (54, 51)  # First classroom location from JSON
            print(f"  School reference at: {self.school}")

            # Workplace - for reference only
            self.workplace = (39, 51)  # Grocery store from JSON
            print(f"  Workplace reference at: {self.workplace}")

            # Player's home - for reference only
            home = (1, 5)  # Alex's apartment from JSON
            print(f"  Home reference at: {home}")

            # Bank location - for reference only
            self.bank = (12, 34)  # Bank from JSON
            print(f"  Bank reference at: {self.bank}")

            # Emergency shelter - for reference only
            self.emergency_shelter = (30, 11)  # Emergency shelter from JSON
            print(f"  Emergency shelter reference at: {self.emergency_shelter}")

            # Jobs Center - for reference only, DO NOT override objectives
            if building_types['office']:
                self.jobs_center = random.choice(building_types['office'])
            elif building_types['building']:
                available_buildings = [b for b in building_types['building']
                                       if b != getattr(self, 'school', None)]
                if available_buildings:
                    self.jobs_center = random.choice(available_buildings)
            else:
                # Fallback
                all_buildings = building_types['bank'] + building_types['store']
                if all_buildings:
                    self.jobs_center = random.choice(all_buildings)

            if hasattr(self, 'jobs_center') and self.jobs_center:
                # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
                print(f"  Jobs Center reference at: {self.jobs_center}")
                
            # Burger place - for reference only, DO NOT override objectives
            self.burger_place = None
            # First try stores
            if building_types['store']:
                available_stores = [s for s in building_types['store']
                                  if s not in [getattr(self, 'workplace', None),
                                             getattr(self, 'jobs_center', None)]]
                if available_stores:
                    self.burger_place = random.choice(available_stores)

            # If no stores available, try regular buildings
            if not self.burger_place and building_types['building']:
                available_buildings = [b for b in building_types['building']
                                     if b not in [getattr(self, 'workplace', None),
                                                getattr(self, 'jobs_center', None),
                                                getattr(self, 'school', None)]]
                if available_buildings:
                    self.burger_place = random.choice(available_buildings)

            # Try banks
            if not self.burger_place and building_types['bank']:
                self.burger_place = random.choice(building_types['bank'])

            # If still nothing, use any house
            if not self.burger_place and building_types['house']:
                available_houses = building_types['house'][:5]  # Use first 5 houses
                if available_houses:
                    self.burger_place = random.choice(available_houses)

            if self.burger_place:
                # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
                print(f"  Burger Place reference at: {self.burger_place}")
                
            # Grocery store - for reference only
            grocery_store = None
            if building_types['grocery']:
                grocery_store = random.choice(building_types['grocery'])
            elif building_types['store']:
                available_stores = [s for s in building_types['store']
                                  if s not in [getattr(self, 'workplace', None), self.burger_place]]
                if available_stores:
                    grocery_store = random.choice(available_stores)
            else:
                # Fallback
                all_commercial = building_types['building'] + building_types['bank']
                if all_commercial:
                    grocery_store = random.choice(all_commercial)

            if grocery_store:
                # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
                print(f"  Grocery Store reference at: {grocery_store}")

            # DO NOT OVERRIDE any remaining objectives - they have their coordinates from objectives_narrative.py

        else:
            # Part 2 - DO NOT OVERRIDE COORDINATES
            # The narrative objectives already have their coordinates (or None) set

            # Foster home - for reference only
            self.foster_home = (29, 39)  # Foster home from JSON
            # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
            print(f"  Foster home reference at: {self.foster_home}")

            # TLP Apartment - for reference only
            self.tlp_apartment = (54, 33)  # Mike's place from JSON
            # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
            if hasattr(self, 'tlp_apartment') and self.tlp_apartment:
                print(f"  TLP Apartment reference at: {self.tlp_apartment}")

            # Community Center - for reference only
            self.community_center = (3, 31)  # Bad studio from JSON
            # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
            if self.community_center:
                print(f"  Community Center reference at: {self.community_center}")
            else:
                print("  ERROR: No Community Center found even with fallback!")

            # Housing Services Office - for reference only
            housing_office = (27, 52)  # Rental from JSON
            # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
            if housing_office:
                print(f"  Housing Office reference at: {housing_office}")

            # Grocery Store - for reference only
            grocery_store = (39, 51)  # Grocery store from JSON
            # DO NOT OVERRIDE - objectives already have their coordinates from objectives_narrative.py
            if grocery_store:
                print(f"  Grocery Store reference at: {grocery_store}")

        # Print summary of all DIRECTLY MAPPED locations
        print("\n=== USING EXACT COORDINATES FROM building_interiors.json ===")
        print(f"ALL LOCATIONS MAPPED TO EXACT GRID POSITIONS:")
        print(f"  Alex's Apartment: (15, 20)")
        print(f"  School/Classroom: (54, 51)")
        print(f"  Library: (8, 11)")
        print(f"  Bank: (12, 34)")
        print(f"  Emergency Shelter: (30, 11)")
        print(f"  Foster Home: (29, 39)")
        print(f"  Grocery Store: (39, 51)")
        print(f"  Mike's Place/TLP: (54, 33)")
        print(f"  Bad Studio/Community: (3, 31)")
        print(f"  Rental/Housing Office: (27, 52)")
        print(f"  Hospital: (38, 23)")
        print("ALL ROOMS NOW PROPERLY TIED TO EXACT BUILDING COORDINATES!")
        print("=" * 50)

    def set_new_part_locations(self):
        """Set building locations for Parts 3-8"""
        # Load building interior mappings
        import json
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        mappings_file = os.path.join(base_dir, "data", "maps", "building_interiors.json")

        building_interiors = {}
        if os.path.exists(mappings_file):
            try:
                with open(mappings_file, 'r') as f:
                    building_interiors = json.load(f)
                print(f"\nLoaded building interior mappings for Parts 3-8: {building_interiors}")
            except Exception as e:
                print(f"Error loading building interiors: {e}")

        # Define specific location mappings from building_interiors.json
        room_locations = {
            'alex_apartment': (1, 5),
            'library': (8, 11),
            'hospital': [(38, 23), (34, 31)],
            'bad_studio': (3, 31),
            'bank': (12, 34),
            'classroom': [(54, 51), (27, 56)],
            'emergency_shelter': (30, 11),
            'foster_home': (29, 39),
            'grocery_store': (39, 51),
            'mike': (54, 33),
            'rental': (27, 52)
        }

        # Build building types dictionary (same logic as find_building_locations)
        building_types = {
            'house': [],
            'bank': [],
            'building': [],
            'store': [],
            'school': [],
            'pizza': [],
            'apartment': [],
            'office': [],
            'burger': [],
            'grocery': []
        }
        
        # Scan the map for buildings
        for y in range(self.game.city_map.height):
            for x in range(self.game.city_map.width):
                tile_data = self.game.city_map.map_data[y][x]
                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, building_key, offset_x, offset_y, _ = tile_data
                    else:
                        _, building_key, offset_x, offset_y = tile_data

                    # Only store the top-left corner of buildings
                    if offset_x == 0 and offset_y == 0:
                        building_name_lower = building_key.lower()
                        found_specific = False

                        # Check for specific building types
                        for specific_type in ['school', 'pizza', 'apartment', 'office', 'grocery', 'burger']:
                            if specific_type in building_name_lower:
                                building_types[specific_type].append((x, y))
                                found_specific = True
                                break

                        # Check for houses
                        if not found_specific:
                            for house_indicator in ['house', 'home', 'residence']:
                                if house_indicator in building_name_lower:
                                    building_types['house'].append((x, y))
                                    found_specific = True
                                    break

                        # Check for banks
                        if not found_specific and 'bank' in building_name_lower:
                            building_types['bank'].append((x, y))
                            found_specific = True

                        # Check for stores
                        if not found_specific:
                            for store_indicator in ['store', 'shop', 'mart']:
                                if store_indicator in building_name_lower:
                                    building_types['store'].append((x, y))
                                    found_specific = True
                                    break

                        # If not categorized, add to generic buildings
                        if not found_specific:
                            building_types['building'].append((x, y))
        
        # Ensure community center is found (needed for many objectives)
        if not self.community_center:
            if building_types['office']:
                self.community_center = random.choice(building_types['office'])
            elif building_types['store']:
                self.community_center = random.choice(building_types['store'])
            elif building_types['building']:
                self.community_center = random.choice(building_types['building'])

    def set_part1_housing_locations(self):
        """Set locations for Part 1 Housing objectives"""
        # Scan the map for buildings - same logic as find_building_locations
        building_types = {
            'house': [], 'building': [], 'office': [], 'store': [],
            'bank': [], 'burger': [], 'pizza': [], 'school': [],
            'apartment': [], 'grocery': []
        }
        
        # Scan map for buildings
        for y in range(self.game.city_map.height):
            for x in range(self.game.city_map.width):
                tile_data = self.game.city_map.map_data[y][x]
                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, building_key, offset_x, offset_y, _ = tile_data
                    else:
                        _, building_key, offset_x, offset_y = tile_data
                    
                    # Only store the top-left corner of buildings
                    if offset_x == 0 and offset_y == 0:
                        building_name_lower = building_key.lower()
                        found_specific = False
                        
                        # Check for specific building types
                        for specific_type in ['school', 'pizza', 'apartment', 'office', 'grocery']:
                            if specific_type in building_name_lower:
                                building_types[specific_type].append((x, y))
                                found_specific = True
                                break
                        
                        # Then check general categories
                        if not found_specific:
                            for btype in ['house', 'bank', 'building', 'store']:
                                if btype in building_name_lower:
                                    building_types[btype].append((x, y))
                                    break
        
        # Housing Office - use bank or office buildings
        housing_office = None
        if building_types['bank']:
            housing_office = random.choice(building_types['bank'])
        elif building_types['office']:
            housing_office = random.choice(building_types['office'])
        elif building_types['store']:
            housing_office = random.choice(building_types['store'])
        else:
            # Fallback to any building
            all_buildings = building_types['building'] + building_types['house']
            if all_buildings:
                housing_office = random.choice(all_buildings)
        
        # Assign housing office to relevant objectives  
        housing_office_objectives = ['apartment_search', 'rental_application', 'viewing_scheduled',
                                   'application_fee', 'cosigner_needed', 'application_denied',
                                   'tlp_discovery', 'tlp_application', 'tlp_interview', 
                                   'deposit_math', 'id_expired', 'outreach_worker',
                                   'rapid_rehousing', 'studio_apartment']
        for obj in self.objectives:
            if obj.id in housing_office_objectives:
                pass  # DO NOT OVERRIDE - obj.target_position = housing_office
        
        # Community locations - use stores or schools
        community_loc = None
        if building_types['store']:
            community_loc = random.choice(building_types['store'])
        elif building_types['school']:
            community_loc = random.choice(building_types['school'])
        else:
            community_loc = housing_office
            
        community_objectives = ['first_night', 'sarah_couch_rules', 'mike_couch_unsafe', 
                              'couch_exhausted', 'shelter_search', 'youth_shelter',
                              'shelter_rules', 'food_bank', 'library_refuge', 
                              'shower_access', 'outreach_worker']
        for obj in self.objectives:
            if obj.id in community_objectives:
                pass  # DO NOT OVERRIDE - obj.target_position = community_loc
                
        # Home/apartment objectives - use houses
        if building_types['house']:
            home_loc = random.choice(building_types['house'])
            home_objectives = ['packed_belongings', 'cash_reality', 'facebook_roommates',
                             'alex_response', 'move_in_alex', 'alex_eviction', 
                             'storage_unit', 'first_night_housed', 'six_months_stable']
            for obj in self.objectives:
                if obj.id in home_objectives:
                    pass  # DO NOT OVERRIDE - obj.target_position = home_loc
                    
        # Work locations - use burger/pizza places
        work_loc = None
        if building_types['burger'] or building_types['pizza']:
            work_loc = random.choice(building_types['burger'] + building_types['pizza'])
        elif building_types['store']:
            work_loc = random.choice(building_types['store'])
        else:
            work_loc = housing_office
            
        work_objectives = ['work_schedule_conflict', 'fired_for_absence', 'no_address_job',
                          'phone_shutoff', 'health_declining']
        for obj in self.objectives:
            if obj.id in work_objectives:
                pass  # DO NOT OVERRIDE - obj.target_position = work_loc
                
        # Shelter/TLP - use different building from housing office
        shelter_loc = None
        if building_types['office']:
            available = [b for b in building_types['office'] if b != housing_office]
            if available:
                shelter_loc = random.choice(available)
        if not shelter_loc and building_types['bank']:
            available = [b for b in building_types['bank'] if b != housing_office]
            if available:
                shelter_loc = random.choice(available)
        if not shelter_loc:
            shelter_loc = community_loc
            
        shelter_objectives = ['tlp_waitlist', 'winter_prep', 'three_months_later',
                            'giving_up', 'part1_complete']
        for obj in self.objectives:
            if obj.id in shelter_objectives:
                pass  # DO NOT OVERRIDE - obj.target_position = shelter_loc
                
        print(f"Part 1 Housing locations set - Housing Office: {housing_office}")

    def start(self):
        """Start the objective system"""
        self.find_building_locations()
        if self.game_part >= 2:
            self.set_new_part_locations()
        # Check if this is Part 1 housing objectives
        if len(self.objectives) > 0 and self.objectives[0].id == "housing_intro":
            self.set_part1_housing_locations()
        self.ensure_all_objectives_have_positions()
        self.activate_current_objective()

    def ensure_all_objectives_have_positions(self):
        """Make sure every objective has a target position"""
        # Find a good fallback position - prioritize known buildings over random ones
        fallback_position = None
        
        # First try to use one of the known buildings as fallback
        if self.workplace:
            fallback_position = self.workplace
        elif self.school:
            fallback_position = self.school
        elif self.foster_home:
            fallback_position = self.foster_home
        elif self.community_center:
            fallback_position = self.community_center
        elif self.tlp_apartment:
            fallback_position = self.tlp_apartment
        elif self.jobs_center:
            fallback_position = self.jobs_center
        
        # If still no fallback, find a non-tree building
        if not fallback_position:
            for y in range(self.game.city_map.height):
                for x in range(self.game.city_map.width):
                    tile_data = self.game.city_map.map_data[y][x]
                    if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                        if tile_data[0] == 'building_with_bg':
                            _, building_key, offset_x, offset_y, _ = tile_data
                        else:
                            _, building_key, offset_x, offset_y = tile_data
                        
                        # Skip trees and only use building origins
                        if offset_x == 0 and offset_y == 0 and building_key not in ['tree1', 'tree2', 'tree3']:
                            fallback_position = (x, y)
                            break
                if fallback_position:
                    break
        
        # If still no buildings found, use center of map
        if not fallback_position:
            fallback_position = (self.game.city_map.width // 2, self.game.city_map.height // 2)
            print(f"Warning: No suitable buildings found on map! Using center: {fallback_position}")

        # Assign fallback position to any objective without one
        # But skip notification-style objectives
        skip_objectives = self.NOTIFICATION_OBJECTIVES
        
        for i, obj in enumerate(self.objectives):
            if not obj.target_position and obj.id not in skip_objectives:
                pass  # DO NOT OVERRIDE - obj.target_position = fallback_position
                print(
                    f"Warning: Objective '{obj.id}' ({obj.title}) had no position, using fallback: {fallback_position}")

        # Double-check that all objectives now have positions
        for i, obj in enumerate(self.objectives):
            if not obj.target_position:
                # Only show error for objectives that should have positions
                if obj.id not in self.NOTIFICATION_OBJECTIVES:
                    print(f"ERROR: Objective '{obj.id}' STILL has no position after fallback!")
            else:
                print(f"Objective '{obj.id}' position confirmed: {obj.target_position}")

    def activate_current_objective(self):
        """Activate the current objective"""
        if self.current_objective_index < len(self.objectives):
            current = self.objectives[self.current_objective_index]
            print(f"Activating objective: {current.id} (index: {self.current_objective_index}, part: {self.game_part})")
            current.activate()
            
            # Auto-trigger notification objectives that have no position
            if current.id in self.NOTIFICATION_OBJECTIVES and not current.target_position:
                # These are pure notification objectives that should trigger immediately
                if current.id in ['housing_intro',  # Auto-start intro dialogue
                                  'document_checklist', 'burger_training', 'apply_for_jobs',
                                  'hired_burger_place', 'manager_notice', 'wake_go_school',
                                  'get_hired', 'come_back_tomorrow', 'day_off_notice',
                                  'school_mandatory_meeting', 'panic_scene', 'learn_ilp_officer',
                                  'ilp_callback']:
                    # Give a small delay so the UI can update
                    print(f"🎬 [AUTO_TRIGGER] Auto-triggering objective: {current.id}")
                    pygame.time.wait(100)
                    self.complete_current_objective()

            # Special handling for part1_complete - always auto-trigger regardless of position
            if current.id == 'part1_complete':
                print(f"🎬 [AUTO_TRIGGER] Part 1 complete reached - starting transition automatically")
                # Show completion message to user
                self.show_notification("Part 1 Complete! Transitioning to Part 2...", 2.0)
                pygame.time.wait(1000)  # Give user time to read the message
                self.complete_current_objective()

    def get_current_objective(self):
        """Get the current active objective"""
        if self.current_objective_index < len(self.objectives):
            return self.objectives[self.current_objective_index]
        return None

    def get_next_objective(self):
        """Get the next objective (if any)"""
        next_index = self.current_objective_index + 1
        if next_index < len(self.objectives):
            return self.objectives[next_index]
        return None

    def check_player_at_objective(self, player_x, player_y):
        """Check if player is at the current objective location"""
        current = self.get_current_objective()
        if not current:
            return False
            
        # Skip proximity check for notification objectives
        if current.id in self.NOTIFICATION_OBJECTIVES:
            return False
        
        # Don't auto-advance notification objectives - let player enter building first
        # The complete_current_objective will handle showing the notification
            
        if not current.target_position:
            return False

        target_x, target_y = current.target_position
        # Check if player is near the building entrance (within 5 tiles)
        distance = abs(player_x - target_x) + abs(player_y - target_y)
        return distance <= 5  # Within 5 tiles for easier interaction

    def complete_current_objective(self):
        """Start activity or complete objective"""
        current = self.get_current_objective()
        dprint(f"[COMPLETE] Attempting to complete objective: {current.id if current else 'None'}")
        if not current:
            return

        # Store the current objective index to detect if it changes
        old_index = self.current_objective_index
        self._complete_objective_old_index = old_index

        # PRIORITY CHECK: If we're in an interior with should_exit=True, handle transition first
        # This must run BEFORE the UAM check to prevent activity restart loops
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            interior = self.game.current_interior
            if hasattr(interior, 'should_exit') and interior.should_exit:
                dprint(f"[COMPLETE] Interior has should_exit=True, handling transition")
                self.advance_to_next_objective()

                # Check if next objective is at same location
                next_obj = self.get_current_objective()
                if next_obj and hasattr(interior, 'building_pos'):
                    if next_obj.target_position == interior.building_pos:
                        # Re-enter for next phase (same location)
                        dprint(f"[COMPLETE] Next objective at same location - re-entering interior")
                        interior.should_exit = False  # Reset for next phase
                        interior.enter()
                    else:
                        # Different location - exit interior
                        dprint(f"[COMPLETE] Next objective at different location - exiting interior")
                        interior.active = False
                else:
                    # No next objective or no building_pos - exit
                    interior.active = False
                return  # Transition handled

        # Check if universal activity manager can handle this (only if not transitioning)
        # BUT: Only start activities if player is INSIDE the target building
        # This prevents activities from blocking building entry
        should_start_activity = True
        if current.target_position:
            # Objective targets a building location
            if hasattr(self.game, 'current_interior') and self.game.current_interior:
                # Player is inside a building - check if it's the right one
                if hasattr(self.game.current_interior, 'building_pos'):
                    if self.game.current_interior.building_pos != current.target_position:
                        # Wrong building - don't start activity
                        should_start_activity = False
                        dprint(f"[COMPLETE] Player in wrong building - skipping UAM")
                # If no building_pos, allow activity (interior might handle it)
            else:
                # Player is OUTSIDE - don't start activity, let them enter building first
                should_start_activity = False
                dprint(f"[COMPLETE] Player outside target building - skipping UAM to allow entry")

        if should_start_activity and self.activity_manager.start_activity_for_objective(current.id):
            # Activity started successfully
            dprint(f"[COMPLETE] Activity manager handled: {current.id}")
            return

        # Handle Part 1 objectives
        dprint(f"[COMPLETE] Game part: {self.game_part}")
        if self.game_part == 1:
            # Check for housing objectives first
            if current.id == "housing_intro":
                # Check if we're being called from the foster home interior completion
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.foster_home_aging_out import FosterHomeAgingOut
                    if isinstance(self.game.current_interior, FosterHomeAgingOut):
                        # If the foster home is calling this because it's complete, advance
                        if self.game.current_interior.should_exit:
                            self.advance_to_next_objective()
                            return
                        # NOTE: Removed force completion fallback - was causing premature progression
                        # The interior should properly set should_exit=True when ALL tasks are done
                        dprint(f"[COMPLETE] housing_intro called but should_exit={self.game.current_interior.should_exit} - waiting for all tasks")
                    # The foster home narrative is still active
                    return
                # Otherwise use the intro dialogue screen (old system)
                if not hasattr(self, 'intro_dialogue'):
                    from part_1_housing_stability.intro_dialogue_screen import IntroDialogueScreen
                    self.intro_dialogue = IntroDialogueScreen(self)
                self.current_activity = self.intro_dialogue
                self.current_activity.start()
                return
            elif current.id == "reality_check":
                # Handle emergency shelter completion
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.emergency_shelter_narrative import EmergencyShelterNarrative
                    if isinstance(self.game.current_interior, EmergencyShelterNarrative):
                        # If the shelter is calling this because it's complete, advance
                        if self.game.current_interior.should_exit:
                            self.advance_to_next_objective()
                            return
                    # The emergency shelter narrative is still active
                    return
                # If called directly (not from interior), just advance
                self.advance_to_next_objective()
                return
            elif current.id == "apartment_search":
                # Handle library apartment search completion
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.library_narrative import LibraryNarrative
                    if isinstance(self.game.current_interior, LibraryNarrative):
                        # If the library is calling this because it's complete, advance
                        if self.game.current_interior.should_exit:
                            self.advance_to_next_objective()
                            return
                    # The library narrative is still active
                    return
                # If called directly (not from interior), just advance
                self.advance_to_next_objective()
                return
            elif current.id in ["learn_about_tlp", "tlp_paperwork", "waitlist_47", "found_listing", "application_barriers", "your_reality", "call_foster_parents", "first_rejection"]:
                # These are handled by the rental/housing office interior
                dprint(f"[COMPLETE] Rental/housing office objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.rental_office_narrative import RentalOfficeNarrative
                    from src.interiors.narratives.housing_office_narrative import HousingOfficeNarrative
                    if isinstance(self.game.current_interior, (RentalOfficeNarrative, HousingOfficeNarrative)):
                        dprint(f"[COMPLETE]   In rental/housing office, should_exit={self.game.current_interior.should_exit}")
                        # If the rental office is calling this because it's complete, advance
                        if self.game.current_interior.should_exit:
                            dprint(f"[COMPLETE]   Advancing to next objective!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   should_exit is False, not advancing")
                    # The rental office narrative is still active
                    dprint(f"[COMPLETE]   Rental/housing office narrative still active, returning")
                    return
                # If not in rental office, player needs to go there
                dprint(f"[COMPLETE] Objective {current.id} requires rental office visit")
                return
            elif current.id in ["alex_room", "meet_alex", "move_in_alex", "three_months_later", "landlord_eviction", "pack_again"]:
                # These are handled by Alex's apartment interior
                dprint(f"[COMPLETE] Alex apartment objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.alex_apartment_narrative import AlexApartmentNarrative
                    if isinstance(self.game.current_interior, AlexApartmentNarrative):
                        dprint(f"[COMPLETE]   In Alex apartment, should_exit={self.game.current_interior.should_exit}")
                        # If the apartment is calling this because it's complete, advance
                        if self.game.current_interior.should_exit:
                            dprint(f"[COMPLETE]   Advancing to next objective!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   should_exit is False, not advancing")
                    # The apartment narrative is still active
                    dprint(f"[COMPLETE]   Alex apartment narrative still active, returning")
                    return
                # If not in apartment, player needs to go there
                dprint(f"[COMPLETE] Objective {current.id} requires Alex apartment visit")
                return
            elif current.id == "housing_gameplay":
                # Launch the Part 1 housing game
                if not hasattr(self, 'housing_game'):
                    from part_1_housing_stability.housing_game_integration import Part1HousingGame
                    self.housing_game = Part1HousingGame(self)
                self.current_activity = self.housing_game
                self.current_activity.start()
                return
            elif current.id == "school_quiz":
                # This is handled by the classroom interior in main.py
                return
            elif current.id == "go_to_workplace":
                self.advance_to_next_objective()
            elif current.id == "workplace_apply":
                self.current_activity = self.job_application
                self.current_activity.start()
            elif current.id == "get_hired":
                # Show notification and advance
                self.show_notification("Congratulations! You've been hired at the pizza place! Report to work for your first shift.")
                # Don't advance - let notification system handle it
            elif current.id == "start_work":
                # Don't start the old pizza game - it's handled by the pizza place interior
                pass
            elif current.id == "go_home_day1":
                # Player needs to enter home - handled by interior
                pass
            elif current.id == "manager_notice":
                # Show notification and let it auto-advance
                self.show_notification("Manager Notice: You must come in tomorrow at 7 AM sharp! Go home and get some rest.")
                # Don't advance - let notification system handle it
            elif current.id == "sleep_work":
                # Sleep is handled by home interior
                pass
            elif current.id == "wake_go_school":
                self.game_time = "9:00 AM"
                self.show_notification("Good morning! Time to go to school for mandatory attendance.")
                self.advance_to_next_objective()
            elif current.id == "school_emergency":
                self.current_activity = self.emergency_scene
                self.current_activity.start()
            elif current.id == "late_to_work":
                self.advance_to_next_objective()
            elif current.id == "get_fired":
                self.current_activity = self.firing_scene
                self.current_activity.start()
            elif current.id == "collect_pay":
                self.player_money += 71.24
                self.advance_to_next_objective()
            elif current.id == "jobs_center":
                self.show_notification("Jobs Center: We have openings at local restaurants. Let me check your documents first.")
                # Don't advance - let notification system handle it
            elif current.id == "document_checklist":
                # Start the document checklist activity
                if hasattr(self, 'document_checklist_work'):
                    self.current_activity = self.document_checklist_work
                    self.current_activity.start()
                else:
                    # Fallback to notification
                    self.show_notification("Good news! Your documents are in order. Burger Palace is hiring and offers training!")
                    # Don't advance - let notification system handle it
            elif current.id == "burger_training":
                self.show_notification("Head to Burger Palace (marked on map) for your training opportunity!")
                # Don't advance - let notification system handle it
            elif current.id == "receive_training":
                # This is handled by entering the burger place interior
                pass
            elif current.id == "come_back_tomorrow":
                self.show_notification("Great first day! Come back tomorrow at 4 PM for your first real shift. Now go home and rest.")
                self.advance_to_next_objective()
            elif current.id == "go_home_sleep_day2":
                # Sleep is handled by home interior
                pass
            elif current.id == "day3_school":
                self.game_time = "3:00 PM"
                self.advance_to_next_objective()
            elif current.id == "view_job_listings":
                self.current_activity = self.job_listings
                self.current_activity.start()
            elif current.id == "apply_for_jobs":
                self.show_notification("You've applied to several positions. Good luck!")
                self.advance_to_next_objective()
            elif current.id == "hired_burger_place":
                self.show_notification("Great news! Burger Palace wants to hire you! Go there to start work.")
                self.advance_to_next_objective()
            elif current.id == "work_burger_place":
                # Don't start the burger game - it's handled by the burger place interior
                pass
            elif current.id == "day_off_notice":
                self.show_notification("Manager: You have tomorrow off. Time to do some shopping!")
                # Don't advance - let notification system handle it
            elif current.id == "grocery_shopping_work":
                # Mini-game removed - will be integrated into grocery store interior
                self.advance_to_next_objective()
            elif current.id == "return_home_shopping":
                self.advance_to_next_objective()
            elif current.id == "school_mandatory_meeting":
                self.current_day = 4
                self.game_time = "9:00 AM"
                self.show_notification("School Notice: Mandatory ILP meeting tomorrow! This conflicts with work...")
                # Don't advance - let notification system handle it
            elif current.id == "panic_scene":
                self.current_activity = self.panic_scene
                self.current_activity.start()
            elif current.id == "learn_ilp_officer":
                self.show_notification("You learned about the ILP officer who can help with school-work conflicts. Call them from home!")
                # Don't advance - let notification system handle it
            elif current.id == "call_ilp_officer":
                self.current_activity = self.ilp_officer_call
                self.current_activity.start()
            elif current.id == "ilp_callback":
                self.show_notification("ILP Officer: I've spoken to your manager. You're approved for tomorrow off! Go talk to your manager.")
                # Don't advance - let notification system handle it
            elif current.id == "manager_choice":
                self.current_activity = self.manager_choice
                self.current_activity.start()
            elif current.id in ["ending_stable_housing", "ending_temporary_housing",
                               "ending_couch_surfing", "ending_homeless"]:
                # Handle housing endings
                self.show_notification(current.description)
                self.advance_to_next_objective()
            elif current.id == "final_month":
                # Handle TLP ending notification - requires interior visit
                dprint(f"[COMPLETE] Final month objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.tlp_housing_final_narrative import TLPHousingFinalNarrative
                    if isinstance(self.game.current_interior, TLPHousingFinalNarrative):
                        dprint(f"[COMPLETE]   In TLP housing final, should_exit={getattr(self.game.current_interior, 'should_exit', False)}")
                        if not self.game.current_interior.active:
                            dprint(f"[COMPLETE]   TLP final narrative complete, advancing!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   TLP final narrative still active, returning")
                    return
                dprint(f"[COMPLETE] Objective {current.id} requires TLP housing visit")
                return
            elif current.id == "desperate_measures":
                # Handle selling items in classroom
                dprint(f"[COMPLETE] Desperate measures objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.classroom_narrative import ClassroomNarrative
                    if isinstance(self.game.current_interior, ClassroomNarrative):
                        dprint(f"[COMPLETE]   In classroom, checking completion...")
                        # Check if all required items are sold
                        required_items = ['sell_laptop', 'sell_textbooks', 'sell_coat']
                        if all(item in self.game.current_interior.completed_interactions for item in required_items):
                            dprint(f"[COMPLETE]   All items sold, advancing!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   Not all items sold yet, returning")
                    return
                dprint(f"[COMPLETE] Objective {current.id} requires classroom visit")
                return
            elif current.id == "six_months_surviving":
                # Handle TLP acceptance phone call in classroom
                dprint(f"[COMPLETE] Six months surviving objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.classroom_narrative import ClassroomNarrative
                    if isinstance(self.game.current_interior, ClassroomNarrative):
                        dprint(f"[COMPLETE]   In classroom, checking completion...")
                        if 'celebration' in self.game.current_interior.completed_interactions:
                            dprint(f"[COMPLETE]   Celebration interaction complete, advancing!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   Celebration not complete yet, returning")
                    return
                dprint(f"[COMPLETE] Objective {current.id} requires classroom visit")
                return
            elif current.id == "the_system":
                # Handle system analysis in classroom
                dprint(f"[COMPLETE] System analysis objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.classroom_narrative import ClassroomNarrative
                    if isinstance(self.game.current_interior, ClassroomNarrative):
                        dprint(f"[COMPLETE]   In classroom, checking completion...")
                        if 'whiteboard' in self.game.current_interior.completed_interactions:
                            dprint(f"[COMPLETE]   Whiteboard interaction complete, advancing!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   Whiteboard not interacted with yet, returning")
                    return
                dprint(f"[COMPLETE] Objective {current.id} requires classroom visit")
                return
            elif current.id in ["found_studio", "moving_day", "reflection"]:
                # Handle apartment-related objectives
                dprint(f"[COMPLETE] Apartment objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.crappy_apartment_narrative import CrappyApartmentNarrative
                    from src.interiors.narratives.studio_apartment_part1 import StudioApartmentPart1
                    if isinstance(self.game.current_interior, (CrappyApartmentNarrative, StudioApartmentPart1)):
                        dprint(f"[COMPLETE]   In apartment interior, checking completion...")
                        if not self.game.current_interior.active:
                            dprint(f"[COMPLETE]   Apartment narrative complete, advancing!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   Apartment narrative still active, returning")
                    return
                dprint(f"[COMPLETE] Objective {current.id} requires apartment visit")
                return
            elif current.id == "not_alone":
                # Handle community support group
                dprint(f"[COMPLETE] Not alone objective: {current.id}")
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    from src.interiors.narratives.community_center_narrative import CommunityCenterNarrative
                    if isinstance(self.game.current_interior, CommunityCenterNarrative):
                        dprint(f"[COMPLETE]   In community center, checking completion...")
                        if 'support_circle' in self.game.current_interior.completed_interactions:
                            dprint(f"[COMPLETE]   Support circle complete, advancing!")
                            self.advance_to_next_objective()
                            return
                        else:
                            dprint(f"[COMPLETE]   Support circle not complete yet, returning")
                    return
                dprint(f"[COMPLETE] Objective {current.id} requires community center visit")
                return
            elif current.id == "part1_complete":
                print("🎬 [TRANSITION_DEBUG] Starting Part 1 Complete transition scene!")
                print(f"🎬 [TRANSITION_DEBUG] Current activity before: {self.current_activity}")
                print(f"🎬 [TRANSITION_DEBUG] Transition scene object: {self.transition_scene}")

                # Force exit any current interior first
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    print(f"🎬 [TRANSITION_DEBUG] Exiting current interior: {type(self.game.current_interior).__name__}")
                    self.game.current_interior.active = False
                    self.game.current_interior = None

                # Show transition scene
                self.current_activity = self.transition_scene
                self.current_activity.start()
                print(f"🎬 [TRANSITION_DEBUG] Transition scene started, active: {self.current_activity.active}")
                print(f"🎬 [TRANSITION_DEBUG] Current activity after: {self.current_activity}")
                return  # Important: return here to prevent further processing
            else:
                # Fallback for notification objectives not explicitly handled
                if current.id in self.NOTIFICATION_OBJECTIVES:
                    dprint(f"[COMPLETE] Handling notification objective: {current.id}")
                    self.show_notification(current.description)
                    # Don't auto-advance, let the notification system handle it

        # Handle Part 2 objectives (original code)
        elif current.id == "foster_home_class":
            # Let the foster home interior handle this
            pass
        elif current.id == "tenant_orientation":
            # Advance after tenant orientation
            self.advance_to_next_objective()
        elif current.id == "community_center_workshop":
            # Launch life skills workshop activity
            self.current_activity = self.life_skills_workshop
            self.current_activity.start()
        elif current.id == "submit_application":
            # Mini-game removed - will be integrated into housing office interior
            self.advance_to_next_objective()
        elif current.id == "pack_belongings":
            self.current_activity = self.packing
            self.current_activity.start()
        elif current.id == "meet_roommate":
            # Show roommate meeting
            self.advance_to_next_objective()
        elif current.id == "sleep_day1":
            # Sleep and advance to next day
            self.current_day = 2
            self.game_time = "8:00 AM"
            self.advance_to_next_objective()
        elif current.id == "discover_emergency":
            # Show emergency notices
            self.current_activity = self.emergency_notice
            self.current_activity.start()
        elif current.id == "receive_notices":
            self.advance_to_next_objective()
        elif current.id == "housing_services":
            # Document checklist
            self.current_activity = self.document_checklist
            self.current_activity.start()
        elif current.id == "emergency_assistance":
            # Force yes option (will implement later)
            self.advance_to_next_objective()
        elif current.id == "pack_essentials":
            # Launch packing activity for essential items
            if hasattr(self, 'packing'):
                self.current_activity = self.packing
                self.current_activity.start()
            else:
                # Fallback
                self.advance_to_next_objective()
        elif current.id == "return_housing_services":
            # Skip to next
            self.current_day = 3
            self.game_time = "3:00 PM"
            self.advance_to_next_objective()
        elif current.id == "select_roommate":
            # Roommate selection (will implement)
            self.advance_to_next_objective()
        elif current.id == "roommate_agreement":
            # Mini-game removed - will be integrated into TLP apartment interior
            self.advance_to_next_objective()
        elif current.id == "grocery_shopping":
            # Mini-game removed - will be integrated into grocery store interior
            self.advance_to_next_objective()
        elif current.id == "heater_broken":
            # Start heater crisis
            self.current_day = 4
            self.advance_to_next_objective()
        elif current.id == "contact_help":
            # Contact help (will implement)
            self.advance_to_next_objective()
        elif current.id == "resolution":
            # End of simulation
            self.advance_to_next_objective()

        # Handle Part 2 objectives - Legal System (was Part 3)
        elif self.game_part == 2:
            dprint(f"[COMPLETE] Part 3 objective: {current.id}")
            # Check if we're in a Part 3 interior
            if hasattr(self.game, 'current_interior') and self.game.current_interior:
                interior = self.game.current_interior
                dprint(f"[COMPLETE] Part 3 interior: {type(interior).__name__}, should_exit={getattr(interior, 'should_exit', False)}")

                # Check if interior has completed its narrative
                if hasattr(interior, 'should_exit') and interior.should_exit:
                    dprint(f"[COMPLETE] Part 3 interior signaled should_exit - advancing objective")
                    self.advance_to_next_objective()

                    # Check if next objective is at same location
                    next_obj = self.get_current_objective()
                    if next_obj and hasattr(interior, 'building_pos'):
                        if next_obj.target_position == interior.building_pos:
                            # Re-enter for next phase (same location)
                            dprint(f"[COMPLETE] Next objective at same location - re-entering interior")
                            interior.should_exit = False  # Reset for next phase
                            interior.enter()
                        else:
                            # Different location - exit interior
                            dprint(f"[COMPLETE] Next objective at different location - exiting interior")
                            interior.active = False
                    else:
                        # No next objective or no building_pos - exit
                        interior.active = False
                else:
                    # Interior not ready to exit - let it control the flow
                    dprint(f"[COMPLETE] Part 3 interior not ready to exit - waiting")
                return  # Let interior control the flow
            else:
                # Not in interior, just advance
                dprint(f"[COMPLETE] Part 3 not in interior - advancing")
                self.advance_to_next_objective()

        # Handle Part 3 objectives - Healthcare Crisis (was Part 4)
        elif self.game_part == 3:
            dprint(f"[COMPLETE] Part 4 objective: {current.id}")

            # Check if we're in a Part 4 interior
            if hasattr(self.game, 'current_interior') and self.game.current_interior:
                interior = self.game.current_interior
                dprint(f"[COMPLETE] Part 4 interior: {type(interior).__name__}, should_exit={getattr(interior, 'should_exit', False)}")

                # Check if interior has completed its narrative
                if hasattr(interior, 'should_exit') and interior.should_exit:
                    dprint(f"[COMPLETE] Part 4 interior signaled should_exit - advancing objective")
                    self.advance_to_next_objective()

                    # Check if next objective is at same location
                    next_obj = self.get_current_objective()
                    if next_obj and hasattr(interior, 'building_pos'):
                        if next_obj.target_position == interior.building_pos:
                            # Re-enter for next phase (same location)
                            dprint(f"[COMPLETE] Next objective at same location - re-entering interior")
                            interior.should_exit = False  # Reset for next phase
                            interior.enter()
                        else:
                            # Different location - exit interior
                            dprint(f"[COMPLETE] Next objective at different location - exiting interior")
                            interior.active = False
                    else:
                        # No next objective or no building_pos - exit
                        interior.active = False
                else:
                    # Interior not ready to exit - let it control the flow
                    dprint(f"[COMPLETE] Part 4 interior not ready to exit - waiting")
                return  # Let interior control the flow
            else:
                # Not in interior, just advance
                dprint(f"[COMPLETE] Part 4 not in interior - advancing")
                self.advance_to_next_objective()

    def show_notification(self, text, duration=3.0):
        """Show a notification message - disabled for professional gameplay flow"""
        # Professional games don't use intrusive modal notifications
        # Activities and objectives flow smoothly without blocking overlays
        dprint(f"[SMOOTH_FLOW] Silent progression: {text}")
        return
        
    def draw_notification(self, screen):
        """Professional smooth flow - no intrusive notification overlays"""
        # Modern games use subtle UI transitions, not blocking modals
        return
        
        # Draw notification box
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(self.notification_alpha)
        pygame.draw.rect(box_surface, (40, 40, 45), (0, 0, box_width, box_height), 0, border_radius=15)
        pygame.draw.rect(box_surface, (100, 100, 110), (0, 0, box_width, box_height), 3, border_radius=15)
        screen.blit(box_surface, (box_x, box_y))
        
        # Draw notification text with word wrap
        font = pygame.font.Font(None, 28)
        padding = 40
        max_width = box_width - (padding * 2)
        
        # Word wrap the text
        words = self.notification_text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Handle manual line breaks
            if '\n' in word:
                parts = word.split('\n')
                for i, part in enumerate(parts):
                    if i > 0:
                        # Add current line and start new one
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = []
                    if part:
                        test_line = ' '.join(current_line + [part])
                        if font.size(test_line)[0] <= max_width:
                            current_line.append(part)
                        else:
                            if current_line:
                                lines.append(' '.join(current_line))
                            current_line = [part]
            else:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Center the text vertically
        total_height = len(lines) * 35
        y_offset = box_y + (box_height - total_height) // 2 - 20
        
        # Draw each line
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            text_surface.set_alpha(self.notification_alpha)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 35
            
        # Draw "Press E to continue" prompt
        if self.notification_timer > 0.5:  # Only show after half a second
            prompt_font = pygame.font.Font(None, 24)
            prompt_text = prompt_font.render("Press E to continue", True, (200, 200, 200))
            prompt_text.set_alpha(self.notification_alpha)
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + box_height - 40))
            screen.blit(prompt_text, prompt_rect)

    def advance_to_next_objective(self):
        """Move to the next objective"""
        current = self.get_current_objective()
        if current:
            print(f"Completing objective: {current.id} (index: {self.current_objective_index})")
            print(f"Game part: {self.game_part}, Total objectives: {len(self.objectives)}")
            
            # Safety check - ensure we're not jumping between parts accidentally
            if self.game_part == 1 and current.id == "receive_training":
                print(f"DEBUG: Burger training complete, checking next objective...")
                if self.current_objective_index + 1 < len(self.objectives):
                    next_obj_preview = self.objectives[self.current_objective_index + 1]
                    print(f"DEBUG: Next objective should be: {next_obj_preview.id}")
                    if next_obj_preview.id in ["pack_belongings", "pack_essentials"]:
                        print(f"ERROR: About to jump to Part 2 objective! Preventing this.")
                        # Force correct objective
                        for i, obj in enumerate(self.objectives):
                            if obj.id == "come_back_tomorrow":
                                self.current_objective_index = i - 1
                                print(f"DEBUG: Reset to index {i-1} to properly advance to come_back_tomorrow")
                                break
            
            current.complete()
            self.current_objective_index += 1
            next_obj = self.get_current_objective()
            if next_obj:
                print(f"Advanced to objective: {next_obj.id} (index: {self.current_objective_index})")

            # Notify UI manager about objective change
            self.notify_ui_objective_changed()

            # Save progress to persistent storage
            self._save_progress()

            # Update game time based on objective
            time_updates = {
                # Part 1 time updates
                "school_quiz": "10:00 AM",
                "workplace_apply": "2:00 PM",
                "start_work": "7:00 PM",
                "go_home_day1": "8:00 PM",
                # Part 2 time updates
                "foster_home_class": "3:00 PM",
                "submit_application": "5:00 PM",
                "pack_belongings": "9:00 PM",
                "meet_roommate": "10:00 PM",
                "housing_services": "10:00 AM",
                "emergency_assistance": "11:00 AM",
                "pack_essentials": "12:00 PM",
                "grocery_shopping": "6:00 PM",
                "heater_broken": "7:00 PM"
            }

            if current.id in time_updates:
                self.game_time = time_updates[current.id]

            # Activate next objective
            self.activate_current_objective()

    def go_to_previous_objective(self):
        """Go back to the previous objective in the list"""
        if self.current_objective_index <= 0:
            print("[OBJECTIVE] Already at first objective, cannot go back")
            return

        # Get current objective before changing index
        current = self.get_current_objective()
        if current:
            # Mark current as incomplete (we're going back)
            current.completed = False
            print(f"[OBJECTIVE] Unmarking '{current.title}' as incomplete")

        # Decrement index
        self.current_objective_index -= 1

        # Get previous objective
        previous = self.get_current_objective()
        if previous:
            print(f"[OBJECTIVE] Going back to: {previous.title} (index: {self.current_objective_index})")
            # Activate the previous objective
            self.activate_current_objective()

            # Notify UI of change
            self.notify_ui_objective_changed()

    def notify_ui_objective_changed(self):
        """Notify UI manager that the objective has changed"""
        dprint(f"[UI_NOTIFY] Objective changed to index {self.current_objective_index}")
        if self.use_modern_ui and self.ui_manager:
            # Force UI to update objective counter and data
            if hasattr(self.ui_manager.objective_panel, 'force_update'):
                self.ui_manager.objective_panel.force_update()
            elif hasattr(self.ui_manager.objective_panel, 'last_objective_index'):
                # Reset the cached index to force a redraw
                self.ui_manager.objective_panel.last_objective_index = -1

    def _save_progress(self):
        """Save current progress to persistent storage"""
        try:
            progress_manager = get_progress_manager()
            current_obj = self.get_current_objective()
            obj_id = current_obj.id if current_obj else None

            progress_manager.update_scenario_progress(
                self.game_part,
                self.current_objective_index,
                len(self.objectives),
                objective_id=obj_id
            )
            dprint(f"[PROGRESS] Saved progress: Part {self.game_part}, Objective {self.current_objective_index}/{len(self.objectives)} ({obj_id})")
        except Exception as e:
            dprint(f"[PROGRESS] Failed to save progress: {e}")

    def load_from_saved_progress(self, scenario_id):
        """Load objective index from saved progress"""
        try:
            progress_manager = get_progress_manager()
            resume_info = progress_manager.get_resume_info(scenario_id)

            if resume_info and resume_info["objective_index"] > 0:
                saved_index = resume_info["objective_index"]
                # Make sure we don't go beyond available objectives
                if saved_index < len(self.objectives):
                    self.current_objective_index = saved_index
                    dprint(f"[PROGRESS] Loaded saved progress: Part {scenario_id}, Objective {saved_index}/{len(self.objectives)}")
                    return True
        except Exception as e:
            dprint(f"[PROGRESS] Failed to load progress: {e}")
        return False

    def skip_to_part1(self):
        """Skip to Part 1 - Housing Stability"""
        print("Skipping to Part 1...")
        # Clean up any active activities
        if self.current_activity and self.current_activity.active:
            self.current_activity.cleanup() if hasattr(self.current_activity, 'cleanup') else None
            self.current_activity = None

        # Set to Part 1
        self.game_part = 1
        self.setup_objectives()
        self.current_objective_index = 0

        # Reset player position to a good starting location
        if hasattr(self.game, 'player'):
            self.game.player.x = 25
            self.game.player.y = 25
            self.game.player.pixel_x = 25 * 32
            self.game.player.pixel_y = 25 * 32
            self.game.player.target_x = self.game.player.pixel_x
            self.game.player.target_y = self.game.player.pixel_y
            self.game.update_camera()

        self.show_notification("Part 1: Housing Stability", (100, 255, 100))
        print(f"Jumped to Part 1 with {len(self.objectives)} objectives")

    def skip_to_part2(self):
        """Skip directly to Part 2 using clean transition"""
        print("Skipping to Part 2...")

        # Use Part Transition Manager for clean skip
        try:
            self.part_transition_manager.transition_to_part2()

            # Validate clean transition
            if self.part_transition_manager.validate_clean_transition():
                print("[SKIP] Clean Part 1→2 skip successful")
            else:
                print("[WARNING] Part skip validation failed")

        except Exception as e:
            dprint(f"[ERROR] Part skip failed: {e}")
            self.part_transition_manager.handle_transition_error(e)

        print("Part 2 started!")

    def skip_to_part3(self):
        """Skip directly to Part 3"""
        print("Skipping to Part 3...")

        # Clean up any active activities
        if self.current_activity and self.current_activity.active:
            self.current_activity.completed = True
            self.current_activity.active = False
            self.current_activity = None

        # Set up Part 2 state (Legal System - was Part 3)
        self.game_part = 2
        self.current_day = 1
        self.game_time = "6:00 PM"
        self.current_objective_index = 0

        # Add debt tracking for Part 2
        if not hasattr(self.game, 'player_debt'):
            self.game.player_debt = 0

        # Clear current objectives and set up Part 2 objectives
        self.objectives = []
        self.setup_part2_objectives()

        # Find building locations for Part 2
        self.find_building_locations()

        # Activate the first objective
        self.activate_current_objective()

        print("Part 2 (Legal System) started!")

    def skip_to_part3(self):
        """Skip directly to Part 3 (Healthcare Crisis - was Part 4)"""
        print("Skipping to Part 3...")

        # Clean up any active activities
        if self.current_activity and self.current_activity.active:
            self.current_activity.completed = True
            self.current_activity.active = False
            self.current_activity = None

        # Set up Part 3 state
        self.game_part = 3
        self.current_day = 1
        self.game_time = "9:00 AM"
        self.current_objective_index = 0

        # Clear current objectives and set up Part 3 objectives
        self.objectives = []
        self.setup_part3_objectives()

        # Find building locations for Part 3
        self.find_building_locations()

        # Activate the first objective
        self.activate_current_objective()

        print("Part 3 (Healthcare Crisis) started!")

    def skip_to_part4(self):
        """Skip directly to Part 4 (Education - was Part 5)"""
        print("Skipping to Part 4...")

        # Clean up any active activities
        if self.current_activity and self.current_activity.active:
            self.current_activity.completed = True
            self.current_activity.active = False
            self.current_activity = None

        # Set up Part 4 state
        self.game_part = 4
        self.current_day = 1
        self.game_time = "10:00 AM"
        self.current_objective_index = 0

        # Clear current objectives and set up Part 4 objectives
        self.objectives = []
        self.setup_part4_objectives()

        # Find building locations for Part 4
        self.find_building_locations()

        # Activate the first objective
        self.activate_current_objective()

        print("Part 4 (Education) started!")

    def skip_to_part5(self):
        """Skip directly to Part 5 (Systemic Barriers - was Part 6)"""
        print("Skipping to Part 5...")

        # Clean up any active activities
        if self.current_activity and self.current_activity.active:
            self.current_activity.completed = True
            self.current_activity.active = False
            self.current_activity = None

        # Set up Part 5 state
        self.game_part = 5
        self.current_day = 1
        self.game_time = "9:00 AM"
        self.current_objective_index = 0

        # Clear current objectives and set up Part 5 objectives
        self.objectives = []
        self.setup_part5_objectives()

        # Find building locations for Part 5
        self.find_building_locations()

        # Activate the first objective
        self.activate_current_objective()

        print("Part 5 (Systemic Barriers) started!")

    def skip_to_next_objective(self):
        """Admin command to skip to the next objective - mirrors complete_current_objective flow"""
        print("[SKIP] Skipping to next objective...")

        # If there's an active activity, complete it first
        if self.current_activity and self.current_activity.active:
            self.current_activity.completed = True
            self.current_activity.active = False
            self.current_activity = None

        # Also clean up UAM activity if active
        if self.activity_manager.current_activity:
            self.activity_manager.current_activity.completed = True
            self.activity_manager.current_activity.active = False
            self.activity_manager.current_activity = None

        # Special handling for certain objectives that need to trigger activities
        current = self.get_current_objective()
        dprint(f"[SKIP] Current objective: {current.id if current else 'None'}")
        if current and current.id == "part1_complete":
            print("[SKIP] Triggering part1_complete transition...")
            self.complete_current_objective()
            return

        # Get interior reference BEFORE advancing
        interior = None
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            interior = self.game.current_interior

        # Advance to next objective
        self.advance_to_next_objective()

        # After advancing, check if we landed on part1_complete
        new_current = self.get_current_objective()
        if new_current and new_current.id == "part1_complete":
            print("[SKIP] Advanced to part1_complete, triggering transition...")
            self.complete_current_objective()
            return

        # Handle interior re-entry (same logic as complete_current_objective)
        if interior and new_current:
            if hasattr(interior, 'building_pos') and new_current.target_position == interior.building_pos:
                # Same location - re-enter interior for next phase
                print(f"[SKIP] Next objective at same location - re-entering interior")
                if hasattr(interior, 'should_exit'):
                    interior.should_exit = False
                interior.enter()
            else:
                # Different location - exit interior
                print(f"[SKIP] Next objective at different location - exiting interior")
                interior.active = False

    def update(self, dt):
        """Update objectives and activities"""
        # Validate activity state to prevent conflicts
        self.validate_activity_state()

        # Check if objective changed since last update and notify UI
        if not hasattr(self, '_last_objective_index'):
            self._last_objective_index = self.current_objective_index
        elif self._last_objective_index != self.current_objective_index:
            dprint(f"[UPDATE] Objective index changed from {self._last_objective_index} to {self.current_objective_index}")
            self._last_objective_index = self.current_objective_index
            self.notify_ui_objective_changed()

        # Update modern UI if available
        if self.use_modern_ui and self.ui_manager:
            self.ui_manager.update(dt)

        # Professional smooth flow - no notification interruptions
        # Objectives advance naturally without blocking overlays
        
        # Update universal activity manager first
        if self.activity_manager.current_activity:
            if self.activity_manager.update(dt):
                # Activity completed
                self.advance_to_next_objective()
            return

        # Update current activity if any
        if self.current_activity:
            # Check if activity is valid and active (use getattr for performance)
            is_active = getattr(self.current_activity, 'active', None)
            if is_active is None:
                dprint(f"[OBJ_UPDATE] Warning: Activity {type(self.current_activity).__name__} missing 'active' attribute")
                self.current_activity = None
                return

            if is_active:
                self.current_activity.update(dt)
                # Check if activity completed (not all activities have a completed attribute)
                if getattr(self.current_activity, 'completed', False):
                    dprint(f"[OBJ_UPDATE] Activity completed: {self.current_activity.__class__.__name__}")

                    # Special handling for transition scene
                    if isinstance(self.current_activity, TransitionScene):
                        dprint("🎬 [TRANSITION] TransitionScene completed - switching to Part 2")
                        # Use Part Transition Manager for clean transition
                        try:
                            self.part_transition_manager.transition_to_part2()
                            self.current_activity = None

                            # Validate clean transition
                            if self.part_transition_manager.validate_clean_transition():
                                print("[TRANSITION] Clean Part 1→2 transition successful")
                            else:
                                print("[WARNING] Part transition validation failed")

                        except Exception as e:
                            dprint(f"[ERROR] Part transition failed: {e}")
                            self.part_transition_manager.handle_transition_error(e)

                        return

                    # Clean up activity and advance objective
                    completed_activity = type(self.current_activity).__name__
                    self.current_activity = None
                    dprint(f"[OBJ_UPDATE] Cleared completed activity: {completed_activity}")
                    self.advance_to_next_objective()
                    return  # Important: return here to avoid re-checking the same objective

            elif getattr(self.current_activity, 'completed', False):
                # Activity is completed but not active - clean up
                completed_activity = type(self.current_activity).__name__
                dprint(f"[OBJ_UPDATE] Cleaning up inactive completed activity: {completed_activity}")
                self.current_activity = None
                self.advance_to_next_objective()
                return
        else:
            # Check for Part 2 police encounter trigger (Legal System - was Part 3)
            if self.game_part == 2:
                current = self.get_current_objective()
                if current and current.id in ['police_stop', 'stay_calm', 'court_citation']:
                    # Check if player is at the police encounter location
                    player_tile_x = int(self.game.player.x)
                    player_tile_y = int(self.game.player.y)
                    target_x, target_y = 46, 42  # Police encounter location

                    # Check proximity (within 2 tiles)
                    if abs(player_tile_x - target_x) <= 2 and abs(player_tile_y - target_y) <= 2:
                        print(f"[PART3] Triggering police encounter at ({player_tile_x}, {player_tile_y})")
                        from part_3_legal_system.activities.police_encounter import PoliceEncounterActivity
                        self.current_activity = PoliceEncounterActivity(self)
                        self.current_activity.start()
                        return

            # Update current objective notification timer
            current = self.get_current_objective()
            if current:
                current.update(dt)

    def validate_activity_state(self):
        """Validate that only one activity is running at a time.

        OPTIMIZED: Fast path when no activities exist.
        Uses getattr() instead of hasattr() + access for better performance.
        """
        # Fast path: if neither activity source has anything, skip validation
        if not self.current_activity and not self.activity_manager.current_activity:
            return

        active_activities = []

        # Check main current_activity (use getattr for single access instead of hasattr + access)
        if self.current_activity and getattr(self.current_activity, 'active', False):
            active_activities.append(f"current_activity:{type(self.current_activity).__name__}")

        # Check universal activity manager
        am_activity = self.activity_manager.current_activity
        if am_activity and getattr(am_activity, 'active', False):
            active_activities.append(f"activity_manager:{type(am_activity).__name__}")

        if len(active_activities) > 1:
            dprint(f"[STATE_WARNING] Multiple activities active simultaneously: {', '.join(active_activities)}")
            # Clear all except the most recently set one (current_activity takes priority)
            if self.current_activity:
                dprint(f"[STATE_FIX] Keeping current_activity, clearing activity_manager")
                self.activity_manager.current_activity = None
            else:
                dprint(f"[STATE_FIX] Keeping activity_manager, no current_activity conflict")

        return len(active_activities) <= 1

    def force_complete_current_activity(self):
        """Force complete current activity (for debugging stuck states)"""
        if self.current_activity:
            activity_name = type(self.current_activity).__name__
            dprint(f"[FORCE_COMPLETE] Force completing activity: {activity_name}")

            # Try to complete gracefully first
            if hasattr(self.current_activity, 'completed'):
                self.current_activity.completed = True

            if hasattr(self.current_activity, 'active'):
                self.current_activity.active = False

            # Clear the activity
            self.current_activity = None

            # Advance objective
            self.advance_to_next_objective()
            dprint(f"[FORCE_COMPLETE] Activity {activity_name} force completed")
            return True

        dprint(f"[FORCE_COMPLETE] No current activity to complete")
        return False
                
    def draw_debug_info(self, screen):
        """Draw debug information in top left"""
        debug_font = pygame.font.Font(None, 16)
        current = self.get_current_objective()
        
        debug_info = [
            "=== GAME DEBUG ===",
            f"Part: {self.game_part}",
            f"Day: {self.current_day} - {self.game_time}",
            f"Objective: {current.id if current else 'None'}",
            "",
            "NEXT STEP:",
        ]
        
        # Add specific next step based on current objective
        if current:
            if current.id == "school_quiz":
                debug_info.append("Find and enter the SCHOOL building")
                debug_info.append("Look for a building with classrooms")
            elif current.id == "go_to_workplace":
                debug_info.append("Go to workplace after school")
            elif current.id == "apply_for_jobs":
                debug_info.append("Look for burger or pizza place")
            elif current.id == "housing_intro":
                debug_info.append("Watch the intro dialogue")
            elif current.id == "housing_menu":
                debug_info.append("Go to the Housing Office")
            else:
                debug_info.append(f"Complete: {current.title}")
                
        # Add location-specific hints
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            debug_info.append("")
            debug_info.append("In Interior - see interior debug")
        else:
            debug_info.append("")
            debug_info.append("Use arrow keys to move")
            debug_info.append("Press E near buildings")
            
        # Draw background - position on the RIGHT side to avoid overlap
        debug_width = 280
        debug_height = len(debug_info) * 18 + 10
        debug_x = SCREEN_WIDTH - debug_width - 10  # Right side with margin
        debug_y = 10
        
        debug_bg = pygame.Surface((debug_width, debug_height))
        debug_bg.set_alpha(200)
        debug_bg.fill((0, 0, 0))
        screen.blit(debug_bg, (debug_x, debug_y))
        
        # Draw border
        pygame.draw.rect(screen, (0, 255, 0), (debug_x, debug_y, debug_width, debug_height), 1)
        
        # Draw text
        y = debug_y + 5
        for line in debug_info:
            if line.startswith("===") or line == "NEXT STEP:":
                color = (0, 255, 0)
            else:
                color = (200, 255, 200)
                
            text = debug_font.render(line, True, color)
            screen.blit(text, (debug_x + 5, y))
            y += 18

    def draw_ui(self, screen):
        """Draw professional, well-aligned HUD"""
        # Draw activity manager UI first if active
        if self.activity_manager.current_activity:
            self.activity_manager.draw(screen)
            return  # Don't draw other UI when activity is active

        # Draw current activity if active (including TransitionScene)
        if self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return  # Don't draw other UI when activity is active

        # Draw notification if showing
        if self.showing_notification:
            self.draw_notification(screen)
            return  # Don't draw other UI when notification is showing

        # Use modern UI if available - this is the only UI we need
        if self.use_modern_ui and self.ui_manager:
            self.ui_manager.draw(screen)
            return  # Exit immediately after drawing modern UI

        # If no modern UI, just return (don't draw fallback UI)
        return

        current = self.get_current_objective()
        if not current:
            return

        # Professional HUD design
        margin = 25
        panel_width = 320
        panel_height = 160
        corner_radius = 10

        # Draw panel background directly on screen with rounded corners
        pygame.draw.rect(screen, (25, 25, 30), 
                        (margin, margin, panel_width, panel_height), 
                        0, border_radius=corner_radius)
        
        # Draw elegant border
        pygame.draw.rect(screen, (70, 70, 80),
                         (margin, margin, panel_width, panel_height), 2,
                         border_radius=corner_radius)

        # Inner content positioning
        content_x = margin + 20
        content_y = margin + 20

        # Fonts
        header_font = pygame.font.Font(None, 26)
        value_font = pygame.font.Font(None, 24)
        label_font = pygame.font.Font(None, 20)

        # Row 1: Game Part and Day/Time (aligned)
        row1_y = content_y

        # Part indicator with better styling
        part_color = (120, 170, 255) if self.game_part == 1 else (255, 170, 120)
        # Draw semi-transparent background
        part_bg_color = (part_color[0] // 5, part_color[1] // 5, part_color[2] // 5)
        pygame.draw.rect(screen, part_bg_color, (content_x, row1_y - 2, 60, 24), 0, border_radius=2)
        pygame.draw.rect(screen, part_color, (content_x, row1_y - 2, 60, 24), 1, border_radius=2)

        part_text = label_font.render(f"PART {self.game_part}", True, part_color)
        screen.blit(part_text, (content_x + 8, row1_y + 2))

        # Day/Time aligned to the right
        day_time_text = f"Day {self.current_day} • {self.game_time}"
        day_time_surface = value_font.render(day_time_text, True, (220, 220, 220))
        day_time_x = margin + panel_width - day_time_surface.get_width() - 20
        screen.blit(day_time_surface, (day_time_x, row1_y))

        # Row 2: Money (if applicable)
        row2_y = row1_y + 35
        if self.game_part == 1 or self.player_money > 0:
            # Money label
            money_label = label_font.render("Balance", True, (150, 150, 150))
            screen.blit(money_label, (content_x, row2_y))

            # Money value aligned
            money_color = (120, 255, 120) if self.player_money > 0 else (255, 120, 120)
            money_text = f"${self.player_money:,.2f}"
            money_surface = header_font.render(money_text, True, money_color)
            screen.blit(money_surface, (content_x + 70, row2_y - 2))

            row3_y = row2_y + 35
        else:
            row3_y = row2_y

        # Divider line
        pygame.draw.line(screen, (50, 50, 55),
                         (content_x, row3_y),
                         (margin + panel_width - 20, row3_y), 1)

        # Row 3: Current Objective
        obj_y = row3_y + 10
        obj_label = label_font.render("OBJECTIVE", True, (150, 150, 150))
        screen.blit(obj_label, (content_x, obj_y))

        # Get dynamic or static description
        display_text = current.get_display_text() if hasattr(current, 'get_display_text') else current.description

        # Add progress text if available
        if hasattr(current, 'progress_text') and current.progress_text:
            display_text = f"{display_text} - {current.progress_text}"

        # Objective text with proper wrapping (now using display_text instead of title)
        obj_text_y = obj_y + 20
        max_width = panel_width - 40
        words = display_text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if value_font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Draw objective lines
        for i, line in enumerate(lines[:2]):  # Max 2 lines
            obj_surface = value_font.render(line, True, (255, 255, 200))
            screen.blit(obj_surface, (content_x, obj_text_y + i * 22))

        # Progress bar instead of dots
        if len(self.objectives) > 1:
            progress_y = margin + panel_height - 15
            progress_width = panel_width - 40
            progress_x = content_x

            # Background bar
            pygame.draw.rect(screen, (40, 40, 45),
                             (progress_x, progress_y, progress_width, 6),
                             border_radius=3)

            # Progress fill
            progress_percent = (self.current_objective_index + 1) / len(self.objectives)
            fill_width = int(progress_width * progress_percent)
            if fill_width > 0:
                pygame.draw.rect(screen, (100, 200, 100),
                                 (progress_x, progress_y, fill_width, 6),
                                 border_radius=3)

        # Admin Skip Button - positioned in top right of panel
        skip_width = 80
        skip_height = 28
        skip_x = margin + panel_width - skip_width - 15
        skip_y = margin + 15
        
        # Check hover on skip button
        skip_hover = False
        if hasattr(self.game, 'mouse_pos'):
            mx, my = pygame.mouse.get_pos()
            skip_hover = skip_x <= mx <= skip_x + skip_width and skip_y <= my <= skip_y + skip_height
        
        # Draw skip button
        skip_color = (150, 100, 100) if skip_hover else (100, 60, 60)
        pygame.draw.rect(screen, skip_color, (skip_x, skip_y, skip_width, skip_height), 0, border_radius=4)
        pygame.draw.rect(screen, (200, 150, 150), (skip_x, skip_y, skip_width, skip_height), 2, border_radius=4)
        
        skip_font = pygame.font.Font(None, 20)
        skip_text = skip_font.render("SKIP →", True, (255, 200, 200))
        skip_text_x = skip_x + skip_width // 2 - skip_text.get_width() // 2
        skip_text_y = skip_y + skip_height // 2 - skip_text.get_height() // 2
        screen.blit(skip_text, (skip_text_x, skip_text_y))
        
        if skip_hover:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        # Draw objective notification if recently activated
        if current.show_notification and current.notification_timer > 0:
            notification_alpha = int(min(255, current.notification_timer * 255))

            # Professional notification design
            notif_font = pygame.font.Font(None, 24)
            desc_font = pygame.font.Font(None, 20)

            # Create notification text
            notif_text = "NEW OBJECTIVE"
            desc_text = current.title

            # Calculate dimensions
            desc_surface = desc_font.render(desc_text, True, (255, 255, 255))
            box_width = desc_surface.get_width() + 80
            box_height = 60
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            box_y = 120

            # Draw notification panel directly with rounded corners
            pygame.draw.rect(screen, (25, 25, 30), (box_x, box_y, box_width, box_height), 0, border_radius=8)
            
            # Elegant border with glow effect
            border_color = (255, 220, 100)
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2, border_radius=8)

            # Left accent bar
            accent_width = 4
            pygame.draw.rect(screen, border_color, (box_x + 10, box_y + 10, accent_width, box_height - 20))

            # Draw text
            notif_surface = notif_font.render(notif_text, True, border_color)
            desc_surface = desc_font.render(desc_text, True, (255, 255, 255))

            # Align text properly
            text_x = box_x + 25
            screen.blit(notif_surface, (text_x, box_y + 12))
            screen.blit(desc_surface, (text_x, box_y + 35))

        # Draw interaction prompt if player is near objective (but not in interior)
        if self.game.player_near_objective and not (hasattr(self.game, 'current_interior') and self.game.current_interior):
            prompt_font = pygame.font.Font(None, 22)
            prompt_text = current.interaction_text
            prompt_surface = prompt_font.render(prompt_text, True, (255, 255, 255))

            # Professional prompt design
            prompt_width = prompt_surface.get_width() + 40
            prompt_height = 36
            prompt_x = SCREEN_WIDTH // 2 - prompt_width // 2
            prompt_y = SCREEN_HEIGHT // 2 - 100

            # Pulsing effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.2 + 0.8

            # Draw prompt panel directly with rounded corners
            pygame.draw.rect(screen, (25, 25, 30), 
                           (prompt_x, prompt_y, prompt_width, prompt_height),
                           0, border_radius=6)

            # Green accent border
            border_color = (120, 255, 120)
            pygame.draw.rect(screen, border_color,
                             (prompt_x, prompt_y, prompt_width, prompt_height),
                             2, border_radius=6)

            # E key indicator background
            key_x = prompt_x + 8
            key_y = prompt_y + 6
            pygame.draw.rect(screen, (40, 40, 45), (key_x, key_y, 24, 24), 0, border_radius=4)
            pygame.draw.rect(screen, border_color, (key_x, key_y, 24, 24), 1, border_radius=4)

            key_font = pygame.font.Font(None, 20)
            key_text = key_font.render("E", True, border_color)
            screen.blit(key_text, (key_x + 8, key_y + 4))

            # Interaction text
            text_x = prompt_x + 40
            text_y = prompt_y + prompt_height // 2 - prompt_surface.get_height() // 2
            screen.blit(prompt_surface, (text_x, text_y))

    def _init_marker_cache(self):
        """Pre-create cached surfaces for marker rendering (performance optimization)."""
        # Create glow surface once - reused every frame
        self._marker_glow_surf = pygame.Surface((80, 80))
        self._marker_glow_surf.set_colorkey((0, 0, 0))
        # Draw the glow circles (static, alpha applied at render time)
        for i in range(4):
            size = 40 - i * 8
            pygame.draw.circle(self._marker_glow_surf, (255, 220, 100), (40, 40), size)

    def draw_objective_markers(self, screen, camera_x, camera_y):
        """Draw markers and path for objective locations on the map"""
        # Don't draw markers if we're in an interior
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            return
            
        current = self.get_current_objective()
        if not current:
            return

        # Check if this is a notification-style objective that doesn't need a position
        if current.id in self.NOTIFICATION_OBJECTIVES:
            # Skip drawing markers for notification objectives
            return

        # Additional safety check and debug info
        if not current.target_position:
            print(f"WARNING: Current objective '{current.id}' has no target position!")
            return

        # Get positions
        player_x = self.game.player.x
        player_y = self.game.player.y
        target_x, target_y = current.target_position

        # Calculate distance in tiles
        tile_distance = math.sqrt((target_x - player_x) ** 2 + (target_y - player_y) ** 2)

        # Draw navigation line
        if not self.game.player_near_objective and tile_distance > 2:
            # Get screen positions
            player_screen_x = self.game.player.pixel_x - camera_x + TILE_SIZE // 2
            player_screen_y = self.game.player.pixel_y - camera_y + TILE_SIZE // 2
            target_screen_x = target_x * TILE_SIZE - camera_x + TILE_SIZE // 2
            target_screen_y = target_y * TILE_SIZE - camera_y + TILE_SIZE // 2

            # Calculate line direction
            dx = target_screen_x - player_screen_x
            dy = target_screen_y - player_screen_y
            line_length = math.sqrt(dx * dx + dy * dy)

            if line_length > 0:
                # Normalize direction
                dx /= line_length
                dy /= line_length

                # Line starts near player
                start_offset = 50
                line_start_x = player_screen_x + dx * start_offset
                line_start_y = player_screen_y + dy * start_offset

                # Line ends near target (but not quite at it)
                end_offset = 40
                line_end_x = target_screen_x - dx * end_offset
                line_end_y = target_screen_y - dy * end_offset

                # Only draw if line would be visible
                actual_line_length = math.sqrt((line_end_x - line_start_x) ** 2 + (line_end_y - line_start_y) ** 2)

                if actual_line_length > 20:
                    # Draw more visible animated dotted line
                    num_dots = int(actual_line_length / 20)  # More dots
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 0.3 + 0.7

                    for i in range(num_dots):
                        t = i / float(num_dots - 1) if num_dots > 1 else 0
                        dot_x = line_start_x + (line_end_x - line_start_x) * t
                        dot_y = line_start_y + (line_end_y - line_start_y) * t

                        # Animated dots that "flow" toward objective
                        flow_offset = (pygame.time.get_ticks() * 0.001) % 1.0
                        if abs((i / float(max(num_dots, 1))) - flow_offset) < 0.1:
                            size = 6
                            color = (255, 255, 150)
                            glow = True
                        else:
                            size = 4
                            color = (255, 220, 100)
                            glow = False

                        # Draw glow effect for active dots
                        if glow:
                            # Draw glow directly on screen
                            glow_color = (255, 220, 100)
                            for i in range(3):
                                alpha_mult = 0.1 * (3 - i) * pulse
                                color = (int(glow_color[0] * alpha_mult), 
                                       int(glow_color[1] * alpha_mult), 
                                       int(glow_color[2] * alpha_mult))
                                pygame.draw.circle(screen, color, (int(dot_x), int(dot_y)), 8 - i * 2)

                        # Draw main dot
                        pygame.draw.circle(screen, color, (int(dot_x), int(dot_y)), size)
                        pygame.draw.circle(screen, (255, 255, 200), (int(dot_x), int(dot_y)), size - 1)

                    # Draw larger, more visible arrow
                    arrow_length = 20
                    arrow_width = 12

                    # Pulsing arrow
                    arrow_pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.4 + 0.6

                    # Draw arrow directly on screen
                    arrow_x = int(line_end_x)
                    arrow_y = int(line_end_y)
                    
                    # Arrow points
                    tip_x = arrow_x + dx * arrow_length
                    tip_y = arrow_y + dy * arrow_length

                    # Calculate perpendicular for arrow wings
                    perp_x = -dy
                    perp_y = dx

                    wing1_x = arrow_x + perp_x * arrow_width
                    wing1_y = arrow_y + perp_y * arrow_width
                    wing2_x = arrow_x - perp_x * arrow_width
                    wing2_y = arrow_y - perp_y * arrow_width

                    # Draw arrow with outline
                    arrow_points = [(tip_x, tip_y), (wing1_x, wing1_y), (wing2_x, wing2_y)]
                    pygame.draw.polygon(screen, (255, 255, 150), arrow_points)
                    pygame.draw.polygon(screen, (255, 220, 100), arrow_points, 2)

        # Draw objective marker
        target_screen_x = target_x * TILE_SIZE - camera_x + TILE_SIZE // 2
        target_screen_y = target_y * TILE_SIZE - camera_y + TILE_SIZE // 2

        if 0 <= target_screen_x <= SCREEN_WIDTH and 0 <= target_screen_y <= SCREEN_HEIGHT - UI_HEIGHT:
            # Large, animated beacon marker
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.5 + 0.5

            # Draw expanding rings
            for i in range(3):
                ring_time = (pygame.time.get_ticks() * 0.001 + i * 0.3) % 1.0
                ring_size = int(20 + ring_time * 30)
                ring_alpha = int((1.0 - ring_time) * 150)

                # Draw ring directly on screen with alpha color
                ring_color = (int(255 * ring_alpha / 255), 
                            int(220 * ring_alpha / 255), 
                            int(100 * ring_alpha / 255))
                pygame.draw.circle(screen, ring_color,
                                 (int(target_screen_x), int(target_screen_y)), 
                                 ring_size, 3)

            # Central glowing marker
            marker_size = int(25 + pulse * 5)

            # Glow effect - use cached surface (PERFORMANCE: avoids Surface creation per frame)
            if self._marker_glow_surf:
                # Apply pulsing alpha to cached surface
                self._marker_glow_surf.set_alpha(int(60 + pulse * 40))
                screen.blit(self._marker_glow_surf, (int(target_screen_x) - 40, int(target_screen_y) - 40))

            # Main marker
            pygame.draw.circle(screen, (255, 255, 150),
                               (int(target_screen_x), int(target_screen_y)),
                               marker_size, 3)
            pygame.draw.circle(screen, (255, 220, 100),
                               (int(target_screen_x), int(target_screen_y)),
                               marker_size - 3, 2)

            # Floating indicator above
            if not self.game.player_near_objective:
                # Draw floating arrow pointing down
                arrow_y = int(target_screen_y - 40 - abs(math.sin(pygame.time.get_ticks() * 0.002)) * 10)
                arrow_points = [
                    (int(target_screen_x), arrow_y + 15),
                    (int(target_screen_x) - 10, arrow_y),
                    (int(target_screen_x) + 10, arrow_y)
                ]
                pygame.draw.polygon(screen, (255, 255, 150), arrow_points)
                pygame.draw.polygon(screen, (255, 220, 100), arrow_points, 2)


class AnimatedPlayer:
    def __init__(self, x, y, tile_size):
        self.x = x  # Tile position
        self.y = y
        self.tile_size = tile_size

        # Player display size - characters are 2 tiles tall
        self.display_width = tile_size
        self.display_height = tile_size * 2  # Characters are 2 tiles tall

        # Pixel position for smooth movement
        self.pixel_x = float(x * tile_size)
        self.pixel_y = float(y * tile_size)
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        # Movement
        self.moving = False
        self.move_speed = tile_size / 8.0  # Faster movement (doubled speed)
        self.direction = 'down'  # 'up', 'down', 'left', 'right'
        self.movement_x = 0  # Track current movement direction
        self.movement_y = 0
        self.animation_lock_time = 0  # Prevent rapid animation changes

        # Animation
        self.animations = {}
        self.sprite_cache = {}  # Cache for converted sprites
        self.current_animation = 'idle_down'
        self.animation_frame = 0
        self.animation_speed = 0.08  # Even faster animation for smoother walk
        self.animation_timer = 0

        # Character selection
        self.selected_character_index = 1  # Default character

        # Load sprites
        self.load_animations()

    def load_animations(self):
        """Load character animations from ModernInteriors premade character spritesheet"""
        # Path to the selected character spritesheet (16x16 version)
        sprite_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
            '0_Premade_Characters', '16x16', f'Premade_Character_{self.selected_character_index:02d}.png'
        )

        try:
            # Load the entire spritesheet
            spritesheet = pygame.image.load(sprite_path)
            print(f"Loaded character {self.selected_character_index} spritesheet (896x656, 56x41 sprites)")

            # ModernInteriors characters are 16x32 (width x height) - 2 tiles tall!
            sprite_width = 16
            sprite_height = 32  # Characters are 2 tiles tall

            # Function to extract and scale a sprite from the sheet
            def get_sprite(col, row):
                # Characters span 2 vertical tiles, so adjust row position
                rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
                sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                sprite.blit(spritesheet, (0, 0), rect)
                # Scale to proper display size (width = tile size, height = 2x tile size)
                sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size * 2))
                # Convert for better performance
                sprite = sprite.convert_alpha()
                return sprite

            # MANUAL SPRITE CONFIGURATION
            # You can easily change these coordinates based on what you see in the spritesheet
            # Format: [(column, row), (column, row), ...] for each animation

            # IDLE SPRITES (single frame each)
            # Fixed mapping based on actual spritesheet layout:
            idle_config = {
                'idle_down': (3, 0),   # Column 0, Row 0 = facing down
                'idle_left': (2, 0),   # Column 1, Row 0 = facing left
                'idle_right': (0, 0),  # Column 2, Row 0 = facing right
                'idle_up': (1, 0),     # Column 3, Row 0 = facing up
            }

            # WALKING SPRITES - Alternating pattern
            # Every 4 sprites is one animation frame for all 4 directions
            # Pattern in each group of 4: down, left, right, up
            # Row 1: First 3 frames (columns 0-11)
            # Row 2: Next 3 frames (columns 0-11)
            walk_config = {
                'walk_down': [
                    (18, 2), (19, 2), (20, 2),  # Row 1: frames 1-3
                    (21, 2), (22, 2), (23, 2)
                ],
                'walk_left': [
                    (12, 2), (13, 2), (14, 2),    # Row 1: frames 1-3
                    (15, 2), (16, 2), (17, 2)     # Row 2: frames 4-6
                ],
                'walk_right': [
                    (0, 2), (1, 2), (2, 2),  # Row 1: frames 1-3
                    (3, 2), (4, 2), (5, 2)  # Row 2: frames 4-6
                ],
                'walk_up': [
                    (6, 2), (7, 2), (8, 2),   # First 3 frames
                    (9, 2), (10, 2), (11, 2)  # Next 3 frames
                ],
            }

            # Load idle animations
            for name, (col, row) in idle_config.items():
                self.animations[name] = [get_sprite(col, row)]

            # Load walking animations
            for name, positions in walk_config.items():
                self.animations[name] = []
                for col, row in positions:
                    self.animations[name].append(get_sprite(col, row))

            print(f"Loaded animations: idle (4 dirs), walk (6 frames x 4 dirs)")

        except Exception as e:
            print(f"Error loading spritesheet: {e}")
            # Fallback - create simple colored rectangles (2 tiles tall)
            placeholder = pygame.Surface((self.tile_size, self.tile_size * 2))
            placeholder.fill((255, 0, 255))  # Magenta
            for anim in ['idle_down', 'idle_up', 'idle_left', 'idle_right']:
                self.animations[anim] = [placeholder]
            for anim in ['walk_down', 'walk_up', 'walk_left', 'walk_right']:
                self.animations[anim] = [placeholder, placeholder]

    def move_to(self, new_x, new_y):
        """Start moving to a new tile position"""
        if self.moving:
            return False  # Already moving

        # Set new target position
        self.x = new_x
        self.y = new_y
        self.target_x = float(new_x * self.tile_size)
        self.target_y = float(new_y * self.tile_size)

        # Determine direction based on movement
        dx = self.target_x - self.pixel_x
        dy = self.target_y - self.pixel_y

        # Store movement direction
        self.movement_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
        self.movement_y = 1 if dy > 0 else (-1 if dy < 0 else 0)

        # Determine animation direction with priority system
        # For diagonal movement, prioritize the last different direction
        new_direction = self.direction

        if abs(dx) > abs(dy):
            # Horizontal movement is dominant
            new_direction = 'right' if dx > 0 else 'left'
        elif abs(dy) > abs(dx):
            # Vertical movement is dominant
            new_direction = 'down' if dy > 0 else 'up'
        else:
            # Equal movement - keep current direction to avoid flickering
            new_direction = self.direction

        # Only change animation if direction actually changed
        if new_direction != self.direction:
            self.direction = new_direction
            self.set_animation(f'walk_{self.direction}')
            self.animation_lock_time = 0.1  # Lock animation for 100ms
        elif not self.moving:
            # Starting to move in same direction
            self.set_animation(f'walk_{self.direction}')

        self.moving = True
        return True

    def set_animation(self, anim_name):
        """Change current animation"""
        if anim_name != self.current_animation and anim_name in self.animations:
            self.current_animation = anim_name
            self.animation_frame = 0
            self.animation_timer = 0

    def update(self, dt):
        """Update player position and animation"""
        # Update animation lock timer
        if self.animation_lock_time > 0:
            self.animation_lock_time -= dt

        # Update movement with proper interpolation
        if self.moving:
            # Calculate movement step based on dt
            step = self.move_speed * dt * 60  # Normalize to 60 FPS

            # Move towards target
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y

            # Calculate distance
            distance = (dx * dx + dy * dy) ** 0.5

            if distance <= step:
                # Arrived at target
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.movement_x = 0
                self.movement_y = 0
                self.set_animation(f'idle_{self.direction}')
            else:
                # Move towards target
                ratio = step / distance
                self.pixel_x += dx * ratio
                self.pixel_y += dy * ratio

                # Update direction only if animation isn't locked
                if self.animation_lock_time <= 0:
                    # Check if we need to update direction based on movement
                    if abs(dx) > 0.1 or abs(dy) > 0.1:
                        if abs(dx) > abs(dy) * 1.5:  # Strong horizontal movement
                            new_dir = 'right' if dx > 0 else 'left'
                        elif abs(dy) > abs(dx) * 1.5:  # Strong vertical movement
                            new_dir = 'down' if dy > 0 else 'up'
                        else:
                            new_dir = self.direction  # Keep current for diagonal

                        if new_dir != self.direction:
                            self.direction = new_dir
                            self.set_animation(f'walk_{self.direction}')
                            self.animation_lock_time = 0.15  # Lock for 150ms

        # Update animation
        if self.current_animation in self.animations:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0  # Full reset instead of subtract
                current_anim = self.animations[self.current_animation]
                if len(current_anim) > 0:
                    self.animation_frame = (self.animation_frame + 1) % len(current_anim)
                    # Ensure frame is valid
                    if self.animation_frame >= len(current_anim):
                        self.animation_frame = 0

    def draw(self, screen, camera_x, camera_y):
        """Draw the player with proper positioning"""
        # Calculate screen position
        # X: center on tile
        # Y: offset up by one tile since character is 2 tiles tall
        screen_x = int(self.pixel_x - camera_x)
        screen_y = int(self.pixel_y - camera_y - self.tile_size)  # Offset up by 1 tile

        # Get current frame
        current_anim = self.animations.get(self.current_animation)
        if current_anim and 0 <= self.animation_frame < len(current_anim):
            current_frame = current_anim[self.animation_frame]
            if current_frame:
                screen.blit(current_frame, (screen_x, screen_y))
        else:
            # Fallback circle if no sprite
            pygame.draw.circle(screen, (255, 0, 0),
                               (int(self.pixel_x - camera_x + self.tile_size // 2),
                                int(self.pixel_y - camera_y + self.tile_size // 2)),
                               self.display_size // 3)
    
    def draw_at_position(self, screen, x, y, direction='down'):
        """Draw the player at a specific position without camera offset"""
        # Calculate screen position (center the larger sprite on the tile)
        offset = (self.display_size - self.tile_size) // 2
        screen_x = int(x - offset)
        screen_y = int(y - offset)
        
        # Select animation based on direction
        anim_name = f'idle_{direction}'
        if anim_name not in self.animations:
            anim_name = 'idle_down'  # Fallback
            
        # Get current frame
        current_anim = self.animations.get(anim_name)
        if current_anim and len(current_anim) > 0:
            # Use first frame of idle animation
            screen.blit(current_anim[0], (screen_x, screen_y))
        else:
            # Fallback circle if no sprite
            colors = {
                'teacher': (100, 100, 200),
                'student': (100, 200, 100),
                'default': (255, 100, 100)
            }
            color = colors.get('default')
            pygame.draw.circle(screen, color,
                               (int(x + self.tile_size // 2),
                                int(y + self.tile_size // 2)),
                               self.display_size // 3)

class TileManager:
    def __init__(self):
        self.sheets = {}
        self.tile_cache = {}
        self.tile_data = None
        self.building_data = None
        self.load_tile_selections()
        self.load_sheets()
        # Initialize empty tile type dicts (not used with unique items)
        self.grass_tile_types = {'center': None, 'edges': {}, 'corners': {}, 'inner_corners': {}}
        self.sidewalk_tile_types = {'center': None, 'edges': {}, 'corners': {}, 'inner_corners': {}}

    def load_tile_selections(self):
        """Load tile selections from JSON file (supports both formats)"""
        # Try loading unique items format first
        try:
            tile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "tiles", "tile_selections_unique.json")
            with open(tile_path, "r") as f:
                data = json.load(f)
                unique_items = data.get('unique_items', {})

                # Convert unique format to old format for compatibility
                self.tile_data = {}
                self.building_data = {}

                for name, item in unique_items.items():
                    if item['type'] == 'tile':
                        # Group tiles by a generic category
                        if 'tiles' not in self.tile_data:
                            self.tile_data['tiles'] = []
                        self.tile_data['tiles'].append(item['tile'])
                    else:  # building
                        self.building_data[name] = {
                            'size': item['size'],
                            'tiles': item['tiles'],
                            'category': 'building'
                        }

                print(f"Loaded unique items format:")
                print(f"  - {sum(1 for item in unique_items.values() if item['type'] == 'tile')} tiles")
                print(f"  - {sum(1 for item in unique_items.values() if item['type'] == 'building')} buildings")
                return
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print("Error: tile_selections_unique.json is corrupted")

        # Try old format
        try:
            tile_path_old = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "tiles", "tile_selections.json")
            with open(tile_path_old, "r") as f:
                content = f.read()
                if content.strip():  # Only parse if file has content
                    data = json.loads(content)
                    self.tile_data = data.get('tiles', {})
                    self.building_data = data.get('buildings', {})
                    print(f"Loaded old format: {sum(len(tiles) for tiles in self.tile_data.values())} tiles")
                    print(f"Loaded {len(self.building_data)} building definitions")
                else:
                    raise ValueError("Empty file")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            print(f"No valid tile selections found, using defaults")
            # Set default tile data
            self.tile_data = {
                'grass': [('CP_V1.0.4.png', 31, 33)],  # Default grass tile
                'road': [('CP_V1.0.4.png', 32, 44)],  # Default road tile
                'sidewalk': [('CP_V1.0.4.png', 32, 48)]  # Default sidewalk tile
            }
            self.building_data = {}

    def load_sheets(self):
        """Load sprite sheets"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Define sheet paths
        sheet_paths = {
            'CP_V1.0.4.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "CP_V1.0.4_nyknck", "CP_V1.0.4.png"),
            'BL001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "BL001.png"),
            'BD001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "BD001.png"),
            'SL001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "SL001.png")
        }

        for sheet_name, path in sheet_paths.items():
            try:
                self.sheets[sheet_name] = pygame.image.load(path)
                print(f"Loaded {sheet_name}")
            except Exception as e:
                print(f"Failed to load {sheet_name}: {e}")
                # Create placeholder surface
                self.sheets[sheet_name] = pygame.Surface((256, 256))
                self.sheets[sheet_name].fill((255, 0, 255))

    def get_tile(self, sheet_name, x, y):
        """Get a tile from cache or create it"""
        cache_key = (sheet_name, x, y)

        if cache_key in self.tile_cache:
            return self.tile_cache[cache_key]

        if sheet_name not in self.sheets:
            return None

        sheet = self.sheets[sheet_name]
        src_rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                               ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)

        try:
            tile_surface = sheet.subsurface(src_rect)
            scaled_tile = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
            self.tile_cache[cache_key] = scaled_tile
            return scaled_tile
        except ValueError:
            return None

    def get_random_tile(self, category):
        """Get a random tile from a category"""
        if category not in self.tile_data or not self.tile_data[category]:
            return None

        tile_info = random.choice(self.tile_data[category])
        return self.get_tile(tile_info[0], tile_info[1], tile_info[2])
    
    def get_grass_tile_for_position(self, map_data, x, y):
        """Get a grass tile appropriate for the given position"""
        # For now, just return a random grass tile
        # In the future, this could check neighboring tiles for better variety
        return self.get_random_tile('grass')
    
    def get_sidewalk_tile_for_position(self, map_data, x, y):
        """Get a sidewalk tile appropriate for the given position"""
        # For now, just return a random sidewalk tile
        # In the future, this could check neighboring tiles for edge/corner tiles
        return self.get_random_tile('sidewalk')

class CityMap:
    def __init__(self):
        # First load a dummy map to get dimensions
        self.load_map_dimensions()
        self.map_data = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.tile_manager = None  # Will be set by Game class
        self.building_tiles = set()
        # Don't load from image here - wait until tile_manager is set

    def load_map_dimensions(self):
        """Load map dimensions from the PNG file"""
        try:
            city_map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "images", "city_map.png")
            map_image = pygame.image.load(city_map_path)
            img_width, img_height = map_image.get_size()

            # Set map dimensions based on image
            # Each pixel in the image represents one tile
            self.width = img_width
            self.height = img_height

            print(f"Map dimensions set to {self.width}x{self.height} from image")
        except Exception as e:
            print(f"Failed to load city_map.png for dimensions: {e}")
            # Fallback dimensions
            self.width = 64
            self.height = 64

    def load_from_visual_map(self):
        """Load city layout from visual map data"""
        try:
            # Try to load the visual map data first
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            map_file = os.path.join(base_dir, "data", "maps", "city_map_data.json")

            # Try multiple locations
            paths_to_try = [map_file, "city_map_data.json"]

            map_data = None
            for path in paths_to_try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        map_data = json.load(f)
                        print(f"Loading visual map from: {path}")
                        break

            if not map_data:
                return False

            self.width = map_data['width']
            self.height = map_data['height']
            saved_map = map_data['map_data']

            print(f"Loading visual map: {self.width}x{self.height}")

            # Initialize map data
            self.map_data = [['dirt' for _ in range(self.width)] for _ in range(self.height)]
            self.building_tiles = set()

            # Process each cell
            for y in range(self.height):
                for x in range(self.width):
                    if y < len(saved_map) and x < len(saved_map[y]):
                        cell = saved_map[y][x]
                        if cell:
                            if cell['type'] == 'tile':
                                # With unique items, store the tile data directly
                                tile_info = cell['data']
                                # For now, just store the tile info directly
                                # The renderer will handle displaying it
                                self.map_data[y][x] = ('tile', tile_info)

                            elif cell['type'] in ['building_part', 'building_part_with_bg']:
                                # Part of a building
                                self.building_tiles.add((x, y))

                                # If this building part has a background, store it
                                if cell['type'] == 'building_part_with_bg' and 'background' in cell:
                                    # Store the background tile info along with building info
                                    bg_info = cell['background']
                                    self.map_data[y][x] = ('building_with_bg',
                                                           cell['building_name'],
                                                           cell['offset_x'],
                                                           cell['offset_y'],
                                                           bg_info)
                                else:
                                    # Regular building without background
                                    self.map_data[y][x] = ('building',
                                                           cell['building_name'],
                                                           cell['offset_x'],
                                                           cell['offset_y'])

            print(f"Visual map loaded successfully")
            return True

        except FileNotFoundError:
            print("No visual map data found, falling back to image loading")
            return False
        except Exception as e:
            print(f"Error loading visual map: {e}")
            return False

    def load_from_image(self):
        """Load city layout from city_map.png"""
        # First try to load visual map
        if self.load_from_visual_map():
            return

        try:
            # Load the city map image
            city_map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "images", "city_map.png")
            map_image = pygame.image.load(city_map_path)

            # Get image dimensions
            img_width, img_height = map_image.get_size()

            print(f"Loading map from city_map.png: {img_width}x{img_height} pixels")

            # Define color mappings based on actual map colors
            COLOR_TO_TILE = {
                # Natural terrain
                (56, 183, 100): 'grass',  # Green
                (139, 69, 19): 'dirt',  # Brown
                (51, 60, 87): 'road',  # Dark gray/blue
                (255, 205, 117): 'sand',  # Sandy yellow
                (245, 247, 250): 'water',  # Light blue/white
                
                # Buildings - these will be handled separately
                (86, 108, 134): 'building',  # Blue-gray buildings
            }

            # Building colors for easy lookup
            BUILDING_COLORS = {
                (86, 108, 134): 'building',  # The actual building color in the map
            }

            # Initialize all tiles as dirt first
            for y in range(self.height):
                for x in range(self.width):
                    if y < len(self.map_data) and x < len(self.map_data[y]):
                        self.map_data[y][x] = 'dirt'

            # Read pixels directly - 1 pixel = 1 tile
            grass_count = 0
            building_count = 0

            # Track which tiles are part of buildings (to avoid overlaps)
            self.building_tiles = set()

            # First pass: identify all tiles
            for y in range(min(self.height, img_height)):
                for x in range(min(self.width, img_width)):
                    # Skip if this tile is already part of a building
                    if (x, y) in self.building_tiles:
                        continue

                    # Get pixel color
                    color = map_image.get_at((x, y))
                    color_tuple = (color.r, color.g, color.b)

                    # Check if it's a building color
                    if color_tuple in BUILDING_COLORS:
                        # Try to place a building starting from this position
                        building_type = BUILDING_COLORS[color_tuple]
                        placed = self.try_place_building_by_type(x, y, building_type, map_image, BUILDING_COLORS)
                        if placed:
                            building_count += 1
                    else:
                        # Find closest matching color
                        tile_type = 'dirt'  # default
                        min_distance = float('inf')

                        for ref_color, ref_type in COLOR_TO_TILE.items():
                            # Calculate color distance
                            dist = sum((c1 - c2) ** 2 for c1, c2 in zip(color_tuple, ref_color))
                            if dist < min_distance:
                                min_distance = dist
                                tile_type = ref_type

                        # Apply the tile type
                        self.map_data[y][x] = tile_type

                        if tile_type == 'grass':
                            grass_count += 1

            print(f"Map loaded with {grass_count} grass tiles and {building_count} buildings")

        except Exception as e:
            print(f"Failed to load city_map.png: {e}")
            print("Please ensure city_map.png is in the same directory as this script")

    def try_place_building_by_type(self, start_x, start_y, building_type, map_image, building_colors):
        """
        Try to place a building of category `building_type` at (start_x, start_y).
        """
        # No tile data? bail out
        if not hasattr(self, 'tile_manager') or not self.tile_manager:
            return False
        bdata_map = self.tile_manager.building_data
        if not bdata_map:
            return False

        # Gather all candidates of this category
        candidates = [
            (key, data) for key, data in bdata_map.items()
            if data.get('category') == building_type
        ]
        
        # If no exact match, try to find any building
        if not candidates:
            candidates = [
                (key, data) for key, data in bdata_map.items()
                if data.get('category') == 'building'
            ]
        
        if not candidates:
            return False

        # Sort by descending area so larger footprints match first
        candidates.sort(key=lambda item: item[1]['size'][0] * item[1]['size'][1],
                        reverse=True)

        # Grab the pixel color at the top‐left of the candidate
        px0 = map_image.get_at((start_x, start_y))
        expected_color = (px0.r, px0.g, px0.b)

        # Try each building definition
        for building_key, bdef in candidates:
            w, h = bdef['size']

            # 1) does it even fit on the map?
            if start_x + w > self.width or start_y + h > self.height:
                continue

            # 2) are all pixels in that w×h block the same color, and not already placed?
            ok = True
            for dy in range(h):
                for dx in range(w):
                    x, y = start_x + dx, start_y + dy
                    if (x, y) in self.building_tiles:
                        ok = False
                        break
                    c = map_image.get_at((x, y))
                    if (c.r, c.g, c.b) != expected_color:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue

            # 3) stamp it into your map_data and building_tiles
            for dy in range(h):
                for dx in range(w):
                    x, y = start_x + dx, start_y + dy
                    self.building_tiles.add((x, y))
                    self.map_data[y][x] = ('building', building_key, dx, dy)

            print(f"Placed {building_key} at ({start_x}, {start_y})")
            return True

        # nothing matched
        return False