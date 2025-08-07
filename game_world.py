import pygame
import json
import random
import os
import math
from constants import *
from activities import *
from minigames import *


class ObjectiveManager:
    """Manages game objectives and progression"""

    def __init__(self, game):
        self.game = game
        self.objectives = []
        self.current_objective_index = 0
        self.active = True
        self.game_time = "8:00 AM"
        self.current_day = 1
        self.game_part = 1
        self.player_money = 0.0

        # Building locations (will be set after map loads)
        self.foster_home = None
        self.community_center = None
        self.tlp_apartment = None
        self.workplace = None
        self.school = None
        self.jobs_center = None

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

        # Mini-games
        self.grocery_game = GroceryShoppingGame(self)
        self.application_game = DocumentApplicationGame(self)
        self.roommate_game = RoommateAgreementGame(self)

        # Initialize Part 1 activities
        self.init_part1_activities()

        # Initialize objectives
        self.setup_objectives()

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

    def setup_objectives(self):
        """Create complete game objectives for the housing storyline"""
        if self.game_part == 1:
            self.setup_part1_objectives()
        else:
            self.setup_part2_objectives()

    def setup_part1_objectives(self):
        """Create Part 1 objectives - Employment storyline"""
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
                "Congratulations! You got the job!",
                None,
                "Press E to continue"
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
                "Your manager says: 'Be here tomorrow morning at 9 AM sharp!'",
                None,
                "Press E to acknowledge"
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
                "Check that you have: ID, SSN, Resume",
                None,
                "Press E to verify documents"
            ),
            # Burger Training Offer
            GameObjective(
                "burger_training",
                "Training Opportunity",
                "Would you like burger-making training? (You have pizza experience)",
                None,
                "Press E to accept"
            ),
            # Receive Training
            GameObjective(
                "receive_training",
                "Burger Training",
                "Learn the basics of making burgers",
                None,
                "Press E to complete training"
            ),
            # Told to come back tomorrow
            GameObjective(
                "come_back_tomorrow",
                "Return Tomorrow",
                "Come back tomorrow for job listings",
                None,
                "Press E to continue"
            ),
            # Go home and sleep
            GameObjective(
                "go_home_sleep_day2",
                "End of Day",
                "Go home and rest",
                None,
                "Press E to go home"
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
                "You don't need to work tomorrow",
                None,
                "Press E to continue"
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
                "Important Notice",
                "School: You have a mandatory meeting tomorrow!",
                None,
                "Press E to read notice"
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
                "Foster Youth Resources",
                "Research: ILP officers can help foster youth with work conflicts",
                None,
                "Press E to learn more"
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
                "Good News!",
                "ILP officer: 'I spoke to your manager - you're approved for tomorrow off!'",
                None,
                "Press E to continue"
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
        """Create Part 2 objectives - Original housing storyline"""
        self.objectives = [
            # Day 1 - Morning
            GameObjective(
                "foster_home_class",
                "Attend Tenant Rights Class",
                "Go to the Foster Home and attend the tenant rights class (8:00 AM - 3:00 PM)",
                None,
                "Press E to enter class"
            ),
            GameObjective(
                "community_center_workshop",
                "Life Skills Workshop",
                "Head to the Community Center for the Life Skills Workshop",
                None,
                "Press E to enter workshop"
            ),
            GameObjective(
                "submit_application",
                "Submit TLP Application",
                "Apply for Transitional Living Program housing",
                None,
                "Press E to submit application"
            ),
            # Day 1 - Evening
            GameObjective(
                "pack_belongings",
                "Move to TLP Apartment",
                "Pack and move into your new TLP apartment (5:00 PM - 9:00 PM)",
                None,
                "Press E to start packing"
            ),
            GameObjective(
                "meet_roommate",
                "Meet Your Roommate",
                "Return to apartment and meet your new roommate",
                None,
                "Press E to greet roommate"
            ),
            GameObjective(
                "sleep_day1",
                "Rest for Tomorrow",
                "Go to sleep in your new apartment",
                None,
                "Press E to sleep"
            ),
            # Day 2 - Crisis
            GameObjective(
                "discover_emergency",
                "Emergency: Roommate Gone!",
                "Check your apartment - something's wrong",
                None,
                "Press E to investigate"
            ),
            GameObjective(
                "receive_notices",
                "Urgent Notices",
                "You've received a 3-day pay or quit notice and utility shutoff warning",
                None,
                "Press E to read notices"
            ),
            GameObjective(
                "housing_services",
                "Visit Housing Services",
                "Go to Housing Services Office with your documents",
                None,
                "Press E to enter office"
            ),
            GameObjective(
                "emergency_assistance",
                "Emergency Housing Help",
                "Accept emergency housing assistance",
                None,
                "Press E to proceed"
            ),
            GameObjective(
                "pack_essentials",
                "Pack Essential Items",
                "Return to apartment and pack essentials for temporary housing",
                None,
                "Press E to pack"
            ),
            # Day 3 - Recovery
            GameObjective(
                "return_housing_services",
                "Return to Housing Services",
                "Come back at 3:00 PM as instructed",
                None,
                "Press E to enter"
            ),
            GameObjective(
                "select_roommate",
                "Choose New Roommate",
                "Review roommate profiles and select a compatible match",
                None,
                "Press E to view profiles"
            ),
            GameObjective(
                "roommate_agreement",
                "Set Up Living Agreement",
                "Go to apartment and establish roommate agreement",
                None,
                "Press E to start agreement"
            ),
            GameObjective(
                "grocery_shopping",
                "Shop for Groceries",
                "Visit grocery store and learn to split costs with roommate",
                None,
                "Press E to shop"
            ),
            # Day 4 - New Crisis
            GameObjective(
                "heater_broken",
                "Emergency: No Heat!",
                "Your heater is broken and you have a test tomorrow",
                None,
                "Press E to assess situation"
            ),
            GameObjective(
                "contact_help",
                "Get Help for Heater",
                "Contact TLP case manager or landlord for emergency repair",
                None,
                "Press E to make calls"
            ),
            GameObjective(
                "resolution",
                "Crisis Resolved",
                "Maintenance is on the way - you've learned to advocate for yourself",
                None,
                "Press E to continue"
            )
        ]

    def find_building_locations(self):
        """Find appropriate buildings for the storyline"""
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

        # Assign key locations based on game part
        if self.game_part == 1:
            # Part 1 locations - prioritize specific building types

            # School - prefer actual school buildings
            if building_types['school']:
                self.school = random.choice(building_types['school'])
            elif building_types['building']:
                self.school = random.choice(building_types['building'])
            else:
                # Fallback to any building
                all_buildings = building_types['bank'] + building_types['office']
                if all_buildings:
                    self.school = random.choice(all_buildings)

            if hasattr(self, 'school') and self.school:
                self.objectives[0].target_position = self.school  # school_quiz
                self.objectives[9].target_position = self.school  # school_emergency
                print(f"  School at: {self.school}")

            # Workplace (Pizza Shop) - prefer pizza buildings
            if building_types['pizza']:
                self.workplace = random.choice(building_types['pizza'])
            elif building_types['store']:
                self.workplace = random.choice(building_types['store'])
            else:
                # Fallback
                all_commercial = building_types['building'] + building_types['bank']
                if all_commercial:
                    self.workplace = random.choice(all_commercial)

            if hasattr(self, 'workplace') and self.workplace:
                self.objectives[1].target_position = self.workplace  # go_to_workplace
                self.objectives[2].target_position = self.workplace  # workplace_apply
                self.objectives[4].target_position = self.workplace  # start_work
                self.objectives[10].target_position = self.workplace  # late_to_work
                self.objectives[11].target_position = self.workplace  # get_fired
                self.objectives[12].target_position = self.workplace  # collect_pay
                print(f"  Workplace at: {self.workplace}")

            # Player's home
            if building_types['house']:
                home = random.choice(building_types['house'])
            elif building_types['apartment']:
                home = random.choice(building_types['apartment'])
            else:
                # Fallback to any building
                all_buildings = building_types['building'] + building_types['store']
                if all_buildings:
                    home = random.choice(all_buildings)

            if home:
                self.objectives[5].target_position = home  # go_home_day1
                self.objectives[7].target_position = home  # sleep_work
                print(f"  Home at: {home}")

            # Jobs Center - prefer office buildings
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
                self.objectives[13].target_position = self.jobs_center  # jobs_center
                print(f"  Jobs Center at: {self.jobs_center}")

        else:
            # Part 2 locations - housing crisis storyline

            # Foster home
            if building_types['house']:
                self.foster_home = random.choice(building_types['house'])
                self.objectives[0].target_position = self.foster_home
                print(f"  Foster home at: {self.foster_home}")

            # TLP Apartment - prefer apartment buildings
            if building_types['apartment']:
                self.tlp_apartment = random.choice(building_types['apartment'])
            elif building_types['house']:
                available_houses = [h for h in building_types['house']
                                    if h != getattr(self, 'foster_home', None)]
                if available_houses:
                    self.tlp_apartment = random.choice(available_houses)
            else:
                # Fallback
                all_residential = building_types['building'] + building_types['store']
                if all_residential:
                    self.tlp_apartment = random.choice(all_residential)

            if hasattr(self, 'tlp_apartment') and self.tlp_apartment:
                # All apartment-related objectives
                apartment_indices = [3, 4, 5, 6, 7, 10, 13, 15, 16, 17]
                for idx in apartment_indices:
                    if idx < len(self.objectives):
                        self.objectives[idx].target_position = self.tlp_apartment
                print(f"  TLP Apartment at: {self.tlp_apartment}")

            # Community Center
            self.community_center = None
            if building_types['office']:
                self.community_center = random.choice(building_types['office'])
            elif building_types['bank']:
                self.community_center = random.choice(building_types['bank'])
            elif building_types['building']:
                self.community_center = random.choice(building_types['building'])
            else:
                # Ultimate fallback - use ANY building
                all_buildings = []
                for btype in building_types.values():
                    all_buildings.extend(btype)
                if all_buildings:
                    self.community_center = random.choice(all_buildings)
                    print("  WARNING: Using ANY building as community center fallback")

            if self.community_center:
                # Community center objectives
                cc_indices = [1, 2]
                for idx in cc_indices:
                    if idx < len(self.objectives):
                        self.objectives[idx].target_position = self.community_center
                print(f"  Community Center at: {self.community_center}")
            else:
                print("  ERROR: No Community Center found even with fallback!")

            # Housing Services Office (use a different building)
            housing_office = None
            if building_types['office']:
                available_offices = [o for o in building_types['office']
                                     if o != getattr(self, 'community_center', None)]
                if available_offices:
                    housing_office = random.choice(available_offices)
            elif building_types['building']:
                available_buildings = [b for b in building_types['building']
                                       if b != getattr(self, 'community_center', None)]
                if available_buildings:
                    housing_office = random.choice(available_buildings)
            elif building_types['bank']:
                available_banks = [b for b in building_types['bank']
                                   if b != getattr(self, 'community_center', None)]
                if available_banks:
                    housing_office = random.choice(available_banks)

            if housing_office:
                # Housing office objectives
                ho_indices = [8, 9, 11, 12]
                for idx in ho_indices:
                    if idx < len(self.objectives):
                        self.objectives[idx].target_position = housing_office
                print(f"  Housing Office at: {housing_office}")

            # Grocery Store - prefer actual grocery stores
            grocery_store = None
            if building_types['grocery']:
                grocery_store = random.choice(building_types['grocery'])
            elif building_types['store']:
                grocery_store = random.choice(building_types['store'])
            else:
                # Fallback
                all_commercial = building_types['building'] + building_types['bank']
                if all_commercial:
                    grocery_store = random.choice(all_commercial)

            if grocery_store and 14 < len(self.objectives):
                self.objectives[14].target_position = grocery_store
                print(f"  Grocery Store at: {grocery_store}")

    def start(self):
        """Start the objective system"""
        self.find_building_locations()
        self.ensure_all_objectives_have_positions()
        self.activate_current_objective()

    def ensure_all_objectives_have_positions(self):
        """Make sure every objective has a target position"""
        # Find any building as fallback
        fallback_position = None
        for y in range(self.game.city_map.height):
            for x in range(self.game.city_map.width):
                tile_data = self.game.city_map.map_data[y][x]
                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, _, offset_x, offset_y, _ = tile_data
                    else:
                        _, _, offset_x, offset_y = tile_data
                    if offset_x == 0 and offset_y == 0:
                        fallback_position = (x, y)
                        break
            if fallback_position:
                break

        # If no buildings found, use center of map
        if not fallback_position:
            fallback_position = (self.game.city_map.width // 2, self.game.city_map.height // 2)
            print(f"Warning: No buildings found on map! Using center: {fallback_position}")

        # Assign fallback position to any objective without one
        for i, obj in enumerate(self.objectives):
            if not obj.target_position:
                obj.target_position = fallback_position
                print(
                    f"Warning: Objective '{obj.id}' ({obj.title}) had no position, using fallback: {fallback_position}")

        # Double-check that all objectives now have positions
        for i, obj in enumerate(self.objectives):
            if not obj.target_position:
                print(f"ERROR: Objective '{obj.id}' STILL has no position after fallback!")
            else:
                print(f"Objective '{obj.id}' position confirmed: {obj.target_position}")

    def activate_current_objective(self):
        """Activate the current objective"""
        if self.current_objective_index < len(self.objectives):
            self.objectives[self.current_objective_index].activate()

    def get_current_objective(self):
        """Get the current active objective"""
        if self.current_objective_index < len(self.objectives):
            return self.objectives[self.current_objective_index]
        return None

    def check_player_at_objective(self, player_x, player_y):
        """Check if player is at the current objective location"""
        current = self.get_current_objective()
        if not current or not current.target_position:
            return False

        target_x, target_y = current.target_position
        # Check if player is near the building entrance (within 1 tile)
        distance = abs(player_x - target_x) + abs(player_y - target_y)
        return distance <= 3  # Within 3 tiles

    def complete_current_objective(self):
        """Start activity or complete objective"""
        current = self.get_current_objective()
        if not current:
            return

        # Handle Part 1 objectives
        if self.game_part == 1:
            if current.id == "school_quiz":
                self.current_activity = self.workplace_quiz
                self.current_activity.start()
            elif current.id == "go_to_workplace":
                self.advance_to_next_objective()
            elif current.id == "workplace_apply":
                self.current_activity = self.job_application
                self.current_activity.start()
            elif current.id == "get_hired":
                self.advance_to_next_objective()
            elif current.id == "start_work":
                self.current_activity = self.pizza_game
                self.current_activity.start()
            elif current.id == "go_home_day1":
                self.advance_to_next_objective()
            elif current.id == "manager_notice":
                self.current_activity = self.manager_notice
                self.current_activity.start()
            elif current.id == "sleep_work":
                self.current_day = 2
                self.game_time = "8:00 AM"
                self.advance_to_next_objective()
            elif current.id == "wake_go_school":
                self.game_time = "9:00 AM"
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
                self.advance_to_next_objective()
            elif current.id == "document_checklist":
                self.current_activity = self.document_checklist_work
                self.current_activity.start()
            elif current.id == "burger_training":
                self.advance_to_next_objective()
            elif current.id == "receive_training":
                self.current_activity = self.burger_training
                self.current_activity.start()
            elif current.id == "come_back_tomorrow":
                self.advance_to_next_objective()
            elif current.id == "go_home_sleep_day2":
                self.current_day = 3
                self.game_time = "8:00 AM"
                self.advance_to_next_objective()
            elif current.id == "day3_school":
                self.game_time = "3:00 PM"
                self.advance_to_next_objective()
            elif current.id == "view_job_listings":
                self.current_activity = self.job_listings
                self.current_activity.start()
            elif current.id == "apply_for_jobs":
                self.advance_to_next_objective()
            elif current.id == "hired_burger_place":
                self.advance_to_next_objective()
            elif current.id == "work_burger_place":
                self.current_activity = self.burger_game
                self.current_activity.start()
            elif current.id == "day_off_notice":
                self.advance_to_next_objective()
            elif current.id == "grocery_shopping_work":
                self.current_activity = self.grocery_game
                self.current_activity.start()
            elif current.id == "return_home_shopping":
                self.advance_to_next_objective()
            elif current.id == "school_mandatory_meeting":
                self.current_day = 4
                self.game_time = "9:00 AM"
                self.advance_to_next_objective()
            elif current.id == "panic_scene":
                self.current_activity = self.panic_scene
                self.current_activity.start()
            elif current.id == "learn_ilp_officer":
                self.advance_to_next_objective()
            elif current.id == "call_ilp_officer":
                self.current_activity = self.ilp_officer_call
                self.current_activity.start()
            elif current.id == "ilp_callback":
                self.advance_to_next_objective()
            elif current.id == "manager_choice":
                self.current_activity = self.manager_choice
                self.current_activity.start()
            elif current.id == "part1_complete":
                # Transition to Part 2
                self.game_part = 2
                self.current_objective_index = 0
                self.setup_part2_objectives()
                self.find_building_locations()
                self.current_activity = None
                self.activate_current_objective()

        # Handle Part 2 objectives (original code)
        elif current.id == "foster_home_class":
            self.current_activity = self.quiz
            self.current_activity.start()
        elif current.id == "tenant_orientation":
            # Advance after tenant orientation
            self.advance_to_next_objective()
        elif current.id == "community_center_workshop":
            # Launch life skills workshop activity
            self.current_activity = self.life_skills_workshop
            self.current_activity.start()
        elif current.id == "submit_application":
            # Launch document application mini-game
            self.current_activity = self.application_game
            self.current_activity.start()
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
            # Quick pack
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
            # Launch roommate agreement mini-game
            self.current_activity = self.roommate_game
            self.current_activity.start()
        elif current.id == "grocery_shopping":
            # Launch grocery shopping mini-game
            self.current_activity = self.grocery_game
            self.current_activity.start()
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

    def advance_to_next_objective(self):
        """Move to the next objective"""
        current = self.get_current_objective()
        if current:
            current.complete()
            self.current_objective_index += 1

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

    def update(self, dt):
        """Update objectives and activities"""
        # Update current activity if any
        if self.current_activity and self.current_activity.active:
            self.current_activity.update(dt)
            # Check if activity completed
            if self.current_activity.completed:
                # Special handling for transition scene
                if isinstance(self.current_activity, TransitionScene):
                    # Complete the transition to Part 2
                    self.game_part = 2
                    self.current_day = 1
                    self.game_time = "8:00 AM"
                    self.current_objective_index = 0
                    self.setup_objectives()  # Reset objectives for Part 2
                    self.find_building_locations()  # Find new buildings for Part 2
                    self.current_activity = None
                    self.activate_current_objective()
                    return

                self.current_activity = None
                self.advance_to_next_objective()
                return  # Important: return here to avoid re-checking the same objective
        elif self.current_activity and self.current_activity.completed:
            # Clean up completed activity
            self.current_activity = None
            self.advance_to_next_objective()
            return
        else:
            # Update current objective notification timer
            current = self.get_current_objective()
            if current:
                current.update(dt)

    def draw_ui(self, screen):
        """Draw professional, well-aligned HUD"""
        # Draw current activity if active
        if self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return  # Don't draw other UI when activity is active

        current = self.get_current_objective()
        if not current:
            return

        # Professional HUD design
        margin = 25
        panel_width = 320
        panel_height = 160
        corner_radius = 10

        # Create main panel with gradient effect
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.fill((25, 25, 30))

        # Draw gradient overlay
        for i in range(panel_height):
            alpha = int(255 - (i / panel_height) * 50)
            color = (30, 30, 35)
            line_surface = pygame.Surface((panel_width, 1))
            line_surface.fill(color)
            line_surface.set_alpha(alpha)
            panel_surface.blit(line_surface, (0, i))

        panel_surface.set_alpha(220)
        screen.blit(panel_surface, (margin, margin))

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
        part_bg = pygame.Surface((60, 24))
        part_bg.fill(part_color)
        part_bg.set_alpha(40)
        screen.blit(part_bg, (content_x, row1_y - 2))
        pygame.draw.rect(screen, part_color, (content_x, row1_y - 2, 60, 24), 1)

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

        # Objective text with proper wrapping
        obj_text_y = obj_y + 20
        max_width = panel_width - 40
        words = current.title.split(' ')
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

            # Create notification panel with gradient
            notif_panel = pygame.Surface((box_width, box_height))
            notif_panel.fill((25, 25, 30))

            # Add subtle gradient
            for i in range(box_height):
                alpha = int(255 - (i / box_height) * 30)
                line = pygame.Surface((box_width, 1))
                line.fill((30, 30, 35))
                line.set_alpha(alpha)
                notif_panel.blit(line, (0, i))

            notif_panel.set_alpha(min(220, notification_alpha))
            screen.blit(notif_panel, (box_x, box_y))

            # Elegant border with glow effect
            border_color = (255, 220, 100)
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2, border_radius=8)

            # Left accent bar
            accent_width = 4
            accent_surface = pygame.Surface((accent_width, box_height - 20))
            accent_surface.fill(border_color)
            accent_surface.set_alpha(notification_alpha)
            screen.blit(accent_surface, (box_x + 10, box_y + 10))

            # Draw text
            notif_surface = notif_font.render(notif_text, True, border_color)
            notif_surface.set_alpha(notification_alpha)
            desc_surface.set_alpha(notification_alpha)

            # Align text properly
            text_x = box_x + 25
            screen.blit(notif_surface, (text_x, box_y + 12))
            screen.blit(desc_surface, (text_x, box_y + 35))

        # Draw interaction prompt if player is near objective
        if self.game.player_near_objective:
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

            # Create prompt panel
            prompt_panel = pygame.Surface((prompt_width, prompt_height))
            prompt_panel.fill((25, 25, 30))
            prompt_panel.set_alpha(int(220 * pulse))
            screen.blit(prompt_panel, (prompt_x, prompt_y))

            # Green accent border
            border_color = (120, 255, 120)
            pygame.draw.rect(screen, border_color,
                             (prompt_x, prompt_y, prompt_width, prompt_height),
                             2, border_radius=6)

            # E key indicator
            key_bg = pygame.Surface((24, 24))
            key_bg.fill((40, 40, 45))
            key_bg.set_alpha(int(255 * pulse))
            key_x = prompt_x + 8
            key_y = prompt_y + 6
            screen.blit(key_bg, (key_x, key_y))
            pygame.draw.rect(screen, border_color, (key_x, key_y, 24, 24), 1, border_radius=4)

            key_font = pygame.font.Font(None, 20)
            key_text = key_font.render("E", True, border_color)
            screen.blit(key_text, (key_x + 8, key_y + 4))

            # Interaction text
            text_x = prompt_x + 40
            text_y = prompt_y + prompt_height // 2 - prompt_surface.get_height() // 2
            screen.blit(prompt_surface, (text_x, text_y))

    def draw_objective_markers(self, screen, camera_x, camera_y):
        """Draw markers and path for objective locations on the map"""
        current = self.get_current_objective()
        if not current:
            return

        # Additional safety check and debug info
        if not current.target_position:
            print(f"WARNING: Current objective '{current.id}' has no target position!")
            # Try to ensure positions again
            self.ensure_all_objectives_have_positions()
            if not current.target_position:
                print(f"ERROR: Still no position for '{current.id}' after re-ensuring!")
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
                            glow_surf = pygame.Surface((16, 16))
                            glow_surf.set_colorkey((0, 0, 0))
                            pygame.draw.circle(glow_surf, (255, 220, 100), (8, 8), 8)
                            glow_surf.set_alpha(int(50 * pulse))
                            screen.blit(glow_surf, (int(dot_x) - 8, int(dot_y) - 8))

                        # Draw main dot
                        pygame.draw.circle(screen, color, (int(dot_x), int(dot_y)), size)
                        pygame.draw.circle(screen, (255, 255, 200), (int(dot_x), int(dot_y)), size - 1)

                    # Draw larger, more visible arrow
                    arrow_length = 20
                    arrow_width = 12

                    # Pulsing arrow
                    arrow_pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.4 + 0.6

                    # Create arrow with glow
                    arrow_surface = pygame.Surface((60, 60))
                    arrow_surface.set_colorkey((0, 0, 0))

                    # Draw glow
                    for i in range(3):
                        glow_size = 30 - i * 8
                        glow_alpha = int(30 * arrow_pulse)
                        pygame.draw.circle(arrow_surface, (255, 220, 100), (30, 30), glow_size)

                    # Arrow points (centered in surface)
                    center_x, center_y = 30, 30
                    tip_x = center_x + dx * arrow_length
                    tip_y = center_y + dy * arrow_length

                    # Calculate perpendicular for arrow wings
                    perp_x = -dy
                    perp_y = dx

                    wing1_x = center_x + perp_x * arrow_width
                    wing1_y = center_y + perp_y * arrow_width
                    wing2_x = center_x - perp_x * arrow_width
                    wing2_y = center_y - perp_y * arrow_width

                    # Draw arrow with outline
                    arrow_points = [(tip_x, tip_y), (wing1_x, wing1_y), (wing2_x, wing2_y)]
                    pygame.draw.polygon(arrow_surface, (255, 255, 150), arrow_points)
                    pygame.draw.polygon(arrow_surface, (255, 220, 100), arrow_points, 2)

                    # Apply alpha and blit
                    arrow_surface.set_alpha(int(200 * arrow_pulse))
                    screen.blit(arrow_surface, (int(line_end_x) - 30, int(line_end_y) - 30))

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

                ring_surface = pygame.Surface((ring_size * 2, ring_size * 2))
                ring_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(ring_surface, (255, 220, 100),
                                   (ring_size, ring_size), ring_size, 3)
                ring_surface.set_alpha(ring_alpha)
                screen.blit(ring_surface,
                            (int(target_screen_x) - ring_size,
                             int(target_screen_y) - ring_size))

            # Central glowing marker
            marker_size = int(25 + pulse * 5)

            # Glow effect
            glow_surf = pygame.Surface((80, 80))
            glow_surf.set_colorkey((0, 0, 0))
            for i in range(4):
                size = 40 - i * 8
                alpha = int(60 * pulse / (i + 1))
                pygame.draw.circle(glow_surf, (255, 220, 100), (40, 40), size)
            glow_surf.set_alpha(100)
            screen.blit(glow_surf, (int(target_screen_x) - 40, int(target_screen_y) - 40))

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

        # Player display size (larger than tile)
        self.display_size = int(tile_size * 1.8)  # 80% larger

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

        # Load sprites
        self.load_animations()

    def load_animations(self):
        """Load all character animations with optimization"""
        sprite_dir = os.path.join(os.path.dirname(__file__), 'sprites', 'player')

        # Define which files belong to which animations
        animation_files = {
            'idle_down': ['idle_front.png'],
            'idle_up': ['idle_back.png'],
            'idle_left': ['idle_left.png'],
            'idle_right': ['idle_right.png'],
            'walk_down': ['walk_front_1.png', 'walk_front_2.png'],
            'walk_up': ['walk_back_1.png', 'walk_back_2.png'],
            'walk_left': ['walk_left_1.png', 'walk_left_2.png'],
            'walk_right': ['walk_right_1.png', 'walk_right_2.png']
        }

        # Load each animation
        for anim_name, files in animation_files.items():
            self.animations[anim_name] = []
            for file in files:
                path = os.path.join(sprite_dir, file)
                try:
                    # Load and scale the image
                    img = pygame.image.load(path)
                    # Scale to display size
                    img = pygame.transform.scale(img, (self.display_size, self.display_size))
                    # Convert for better performance
                    img = img.convert_alpha()
                    self.animations[anim_name].append(img)
                except Exception as e:
                    print(f"Warning: Could not load {path}: {e}")
                    # Create placeholder if file missing
                    placeholder = pygame.Surface((self.display_size, self.display_size))
                    placeholder.fill((255, 0, 255))  # Magenta for missing sprites
                    self.animations[anim_name].append(placeholder)

                # Verify all animations loaded
            for anim_name in animation_files:
                if anim_name not in self.animations or not self.animations[anim_name]:
                    print(f"Animation {anim_name} failed to load!")
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
                self.animation_timer -= self.animation_speed
                current_anim = self.animations[self.current_animation]
                if len(current_anim) > 0:
                    self.animation_frame = (self.animation_frame + 1) % len(current_anim)

    def draw(self, screen, camera_x, camera_y):
        """Draw the player with proper positioning"""
        # Calculate screen position (center the larger sprite on the tile)
        offset = (self.display_size - self.tile_size) // 2
        screen_x = int(self.pixel_x - camera_x - offset)
        screen_y = int(self.pixel_y - camera_y - offset)

        # Get current frame
        current_anim = self.animations.get(self.current_animation)
        if current_anim and 0 <= self.animation_frame < len(current_anim):
            screen.blit(current_anim[self.animation_frame], (screen_x, screen_y))
        else:
            # Fallback circle if no sprite
            pygame.draw.circle(screen, (255, 0, 0),
                               (int(self.pixel_x - camera_x + self.tile_size // 2),
                                int(self.pixel_y - camera_y + self.tile_size // 2)),
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
            with open("tile_selections_unique.json", "r") as f:
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
            with open("tile_selections.json", "r") as f:
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
        base_dir = os.path.dirname(__file__)

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

class CityMap:
    def __init__(self):
        # First load a dummy map to get dimensions
        self.load_map_dimensions()
        self.map_data = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.tile_manager = None  # Will be set by Game class
        self.building_tiles = set()
        self.load_from_image()

    def load_map_dimensions(self):
        """Load map dimensions from the PNG file"""
        try:
            city_map_path = os.path.join(os.path.dirname(__file__), "city_map.png")
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
            with open("city_map_data.json", "r") as f:
                map_data = json.load(f)

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
            city_map_path = os.path.join(os.path.dirname(__file__), "city_map.png")
            map_image = pygame.image.load(city_map_path)

            # Get image dimensions
            img_width, img_height = map_image.get_size()

            print(f"Loading map from city_map.png: {img_width}x{img_height} pixels")

            # Define color mappings
            COLOR_TO_TILE = {
                # Natural terrain
                (34, 139, 34): 'grass',  # Forest green
                (0, 100, 0): 'tree',  # Dark green
                (128, 128, 128): 'rock',  # Gray
                (0, 119, 190): 'water',  # Blue
                (238, 203, 173): 'sand',  # Sandy beige
                (139, 69, 19): 'dirt',  # Brown
                (0, 80, 150): 'deep_water',  # Deep blue

                # Buildings - these will be handled separately
                (139, 90, 43): 'house',  # Brown house
                (192, 192, 192): 'bank',  # Silver/light gray
                (105, 105, 105): 'building',  # Dark gray office
                (70, 130, 180): 'skyscraper',  # Steel blue
                (255, 140, 0): 'store',  # Dark orange

                # Roads and urban
                (32, 32, 32): 'road',  # Asphalt black
                (190, 190, 190): 'sidewalk',  # Light gray concrete
            }

            # Building colors for easy lookup
            BUILDING_COLORS = {
                (139, 90, 43): 'house',
                (192, 192, 192): 'bank',
                (105, 105, 105): 'building',
                (70, 130, 180): 'skyscraper',
                (255, 140, 0): 'store',
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
                        if self.try_place_building_by_type(x, y, building_type, map_image, BUILDING_COLORS):
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