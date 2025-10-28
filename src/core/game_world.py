import pygame
import json
import random
import os
import math
from src.constants import *
from src.activities import *


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
        # Part 2 - Housing Services narrative objectives
        'part2_intro', 'case_worker_meeting', 'tlp_requirements', 'mandatory_classes',
        'life_skills_workshop', 'application_submitted', 'tlp_approval', 'pack_belongings',
        'meet_roommate', 'first_night_tlp', 'three_weeks_later', 'rent_increase',
        'impossible_budget', 'emergency_meeting', 'payment_plan', 'second_job_search',
        'new_roommate_arrives', 'roommate_conflict', 'mike_evicted', 'six_months_in',
        'housing_search_again', 'savings_depleted', 'year_in_tlp', 'final_warning',
        'program_ending', 'emergency_extension', 'couch_surfing_return', 'part2_reflection',
        'part2_complete',
        # Part 3 - Financial Stress notifications
        'wake_up_broke', 'check_notifications', 'overdraft_explained', 'plead_with_teller',
        'one_fee_reversed', 'empty_fridge', 'count_change', 'food_decision', 'choose_food',
        'food_math', 'phone_shutoff_warning', 'last_calls', 'no_answer_family', 'phone_dies',
        'job_email', 'try_calling', 'email_response', 'auto_rejection', 'hunger_pains',
        'print_directions', 'income_verification', 'turned_away', 'dumpster_consideration',
        'eviction_posted', 'rent_calculation', 'call_landlord_attempt', 'knock_neighbors',
        'inventory_items', 'lowball_offer', 'final_offer', 'not_enough', 'fever_starts',
        'no_thermometer', 'work_sick_choice', 'hiding_symptoms', 'customer_complaint',
        'dizzy_spell', 'collapse_work', 'ambulance_called', 'forced_hospital', 'emergency_room',
        'treatment_received', 'discharge_papers', 'billing_preview', 'work_termination',
        'eviction_court', 'homeless_research', 'shelter_waitlist', 'car_living', 'final_night',
        'cycle_complete', 'system_analysis', 'chapter_end',
        # Part 4 - Credit/Debt notifications
        'need_new_apartment', 'apartment_search', 'application_fee', 'credit_check_wait',
        'credit_denial_call', 'credit_report_request', 'credit_report_shock', 'second_apartment',
        'slumlord_meeting', 'impossible_deposit', 'couch_surfing', 'one_week_max', 'storage_unit',
        'new_job_start', 'first_paycheck_two_weeks', 'payday_loan_search', 'loan_salesperson',
        'loan_amount_needed', 'loan_terms_explained', 'apr_hidden', 'payday_arrives', 'loan_due',
        'fifteen_left', 'rollover_option', 'rollover_accepted', 'second_lender', 'third_lender',
        'debt_calendar', 'total_owed', 'work_overtime_request', 'hours_denied', 'first_default',
        'collection_calls_start', 'voicemail_full', 'work_calls', 'manager_complaint',
        'know_your_rights', 'cease_desist_letter', 'bank_letter', 'direct_deposit_lost',
        'check_cashing_fee', 'money_orders', 'cash_budgeting', 'court_summons',
        'court_date_work_conflict', 'default_judgment', 'garnishment_notice', 'new_paycheck',
        'cant_afford_food', 'car_payment_behind', 'repo_warning', 'hide_car', 'repo_truck_arrives',
        'plead_with_driver', 'car_gone', 'bus_research', 'four_hour_commute', 'wake_up_4am',
        'first_late', 'final_warning', 'second_late', 'fired_attendance', 'unemployment_application',
        'benefits_denied', 'sell_plasma', 'feel_weak', 'bankruptcy_consultation', 'bankruptcy_fee',
        'no_escape', 'debt_total', 'system_rigged', 'poverty_expensive', 'chapter_4_end',
        # Part 5 - Healthcare notifications (all notification-style)
        'tooth_pain_starts', 'inspect_tooth', 'weekend_clinic_search', 'no_weekend_dentists',
        'otc_painkillers', 'temporary_relief', 'monday_calls', 'no_insurance_quotes',
        'payment_plans_denied', 'dental_school_option', 'pain_increasing', 'cant_sleep_pain',
        'er_wait_7hours', 'er_doctor_exam', 'er_prescriptions', 'er_bill_preview',
        'pain_pills_work', 'pills_running_out', 'breakthrough_pain', 'pills_gone',
        'withdrawal_begins', 'cant_eat_properly', 'weight_loss', 'work_mistakes',
        'supervisor_meeting', 'isolation_begins', 'depression_sets_in', 'abscess_forms',
        'fever_starts', 'call_in_sick', 'final_warning_work', 'emergency_extraction',
        'post_surgery', 'gap_tooth_shame', 'panic_attack_work', 'psych_evaluation',
        'mental_health_referral', 'six_month_wait', 'self_medicating', 'morning_drinks',
        'caught_drinking', 'fired_immediately', 'unemployment_denied_2', 'medical_bills_arrive',
        'collections_medical', 'eviction_again', 'medicaid_application', 'medicaid_denied',
        'preventable_suffering', 'system_broken', 'permanent_damage', 'healthcare_poor_tax',
        'chapter_5_complete',
        # Part 6 - Education notifications (all notification-style)
        'dropout_regret', 'job_listings', 'ged_research', 'intake_appointment',
        'placement_test', 'test_results', 'reality_hits', 'class_times',
        'work_schedule_conflict', 'talk_to_manager', 'manager_response', 'hours_cut_punishment',
        'choose_priority', 'free_classes_but', 'book_list', 'total_cost',
        'books_unavailable', 'old_edition_find', 'share_books', 'online_component',
        'no_computer_home', 'library_hours_issue', 'twenty_minutes', 'assignments_incomplete',
        'teacher_concern', 'miss_monday_class', 'miss_wednesday', 'attendance_warning',
        'sick_child_roommate', 'dropped_from_program', 'appeal_process', 'appeal_denied',
        'wait_period', 'second_try', 'same_problems', 'study_alone', 'practice_test_fail',
        'tutoring_cost', 'youtube_university', 'ready_to_test', 'test_fee_shock',
        'save_for_test', 'test_center_far', 'mixed_results', 'retake_fee',
        'test_anxiety', 'third_math_attempt', 'fail_again', 'give_up_temporary',
        'years_pass', 'still_no_diploma', 'systemic_barriers', 'not_about_intelligence',
        'education_privilege', 'cycle_continues', 'chapter_6_end',
        # Part 7 - Isolation notifications (all notification-style)
        'roommate_news', 'why_leaving', 'no_parents_option', 'rent_panic', 'beg_roommate',
        'final_no', 'weekend_move', 'empty_apartment', 'find_new_roommate', 'sketchy_responses',
        'call_mom', 'mom_cold', 'dad_disconnected', 'siblings_distant', 'extended_family',
        'lunch_alone', 'try_joining', 'ignored_completely', 'friday_drinks', 'not_invited',
        'ask_why', 'eat_in_car', 'social_media_scroll', 'happy_posts', 'no_posts',
        'birthday_forgotten', 'delete_facebook', 'more_isolated', 'thin_walls', 'tv_company',
        'walking_loud', 'afraid_to_live', 'complete_silence', 'support_group_search',
        'depression_group', 'bus_routes', 'first_meeting', 'arrive_late', 'cant_speak',
        'flee_meeting', 'online_forums', 'pour_heart_out', 'no_responses', 'internet_bill',
        'last_connection', 'talk_to_self', 'security_suspicious', 'park_bench',
        'someone_talks', 'overshare', 'backs_away', 'dark_thoughts', 'making_plans',
        'moment_clarity', 'crisis_hotline', 'find_phone', 'borrow_phone', 'make_call',
        'counselor_voice', 'thirty_minutes', 'resources_given', 'long_waitlists',
        'still_alone', 'but_alive', 'chapter_7_end',
        # Part 8 - Legal notifications (all notification-style)  
        'morning_routine', 'check_wallet', 'no_more_money', 'walk_or_jump', 'approach_turnstile',
        'look_around', 'jump_quick', 'almost_clear', 'officer_shouts', 'explain_situation',
        'no_sympathy', 'handcuffed_subway', 'citation_written', 'late_to_work', 'final_warning_job',
        'read_court_date', 'request_day_off', 'denied_time_off', 'no_one_covers', 'skip_court',
        'mail_notice', 'panic_mode', 'avoid_police', 'cant_sleep', 'friend_car', 'tail_light',
        'passenger_id', 'warrant_found', 'arrested_roadside', 'booking_process', 'phone_call',
        'no_bail_money', 'overnight_hold', 'miss_work_call', 'court_transport', 'meet_defender',
        'rushed_meeting', 'no_real_choice', 'guilty_plea', 'probation_terms', 'released_afternoon',
        'phone_dead', 'work_voicemail', 'no_explanation', 'first_meeting_po', 'probation_rules',
        'job_search_requirement', 'application_question', 'auto_rejections', 'cant_pay_fees',
        'first_violation', 'community_service', 'miss_service', 'violation_warrant',
        'arrested_again', 'thirty_days', 'released_homeless', 'permanent_record',
        'poverty_crime', 'total_cost', 'system_design', 'modern_slavery',
        'no_rehabilitation', 'chapter_8_end'
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
            # Verify no Part 2 objectives snuck in
            part2_objectives = ["pack_belongings", "pack_essentials", "foster_home_class",
                              "tenant_orientation", "meet_roommate", "discover_emergency"]
            for obj in self.objectives:
                if obj.id in part2_objectives:
                    print(f"ERROR: Part 2 objective '{obj.id}' found in Part 1 objectives list!")
        elif self.game_part == 2:
            self.setup_part2_objectives()
        elif self.game_part == 3:
            self.setup_part3_objectives()
        elif self.game_part == 4:
            self.setup_part4_objectives()
        elif self.game_part == 5:
            self.setup_part5_objectives()
        elif self.game_part == 6:
            self.setup_part6_objectives()
        elif self.game_part == 7:
            self.setup_part7_objectives()
        elif self.game_part == 8:
            self.setup_part8_objectives()

    def setup_part1_objectives(self):
        """Create Part 1 objectives - Employment storyline"""
        # Check if we should use the new housing objectives
        if hasattr(self.game, 'use_housing_objectives') and self.game.use_housing_objectives:
            from part_1_housing_stability.objectives_new import get_part1_objectives_new
            self.objectives = get_part1_objectives_new()
            return
            
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
        """Create Part 2 objectives - Housing services storyline"""
        # Try to use narrative objectives if available
        try:
            from part_2_housing.objectives_narrative import get_part2_narrative_objectives
            self.objectives = get_part2_narrative_objectives()
            print("Loaded Part 2 Housing Narrative objectives")
            return
        except ImportError:
            print("Could not load Part 2 narrative objectives, using default")

        # Fallback to old objectives if narrative not available
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
            'groccery': (39, 51),  # Note the typo in the JSON
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
            'groccery': (39, 51),
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
        
        # Part 3 - Financial Stress locations
        if self.game_part == 3:
            # Bank for banking objectives
            bank_location = None
            if building_types['bank']:
                bank_location = random.choice(building_types['bank'])
            elif building_types['office']:
                bank_location = random.choice(building_types['office'])
            
            if bank_location:
                # Assign bank-related objectives
                bank_objectives = ['check_bank', 'plead_with_teller']
                for obj in self.objectives:
                    if obj.id in bank_objectives:
                        # DO NOT OVERRIDE - use coordinates from objectives files
                        pass  # pass  # DO NOT OVERRIDE - obj.target_position = bank_location
            
            # Home for many objectives
            home_location = None
            if building_types['house']:
                home_location = random.choice(building_types['house'])
            elif building_types['apartment']:
                home_location = random.choice(building_types['apartment'])
            
            if home_location:
                home_objectives = ['empty_fridge', 'count_change', 'last_calls', 'fever_starts', 'final_night']
                for obj in self.objectives:
                    if obj.id in home_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = home_location
            
            # Store locations
            store_location = None
            if building_types['store']:
                store_location = random.choice(building_types['store'])
            elif building_types['grocery']:
                store_location = random.choice(building_types['grocery'])
                
            if store_location:
                store_objectives = ['dollar_menu', 'food_math', 'pawn_shop_walk', 'lowball_offer', 'final_offer']
                for obj in self.objectives:
                    if obj.id in store_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = store_location
            
            # Library - EXACT COORDINATES
            library_location = (8, 11)  # Library from JSON
            library_objectives = ['walk_to_library', 'library_computer', 'food_bank_search', 'homeless_research']
            for obj in self.objectives:
                if obj.id in library_objectives:
                    pass  # DO NOT OVERRIDE - obj.target_position = library_location
                        
            # Hospital - EXACT COORDINATES
            hospital_location = (38, 23)  # First hospital from JSON
            hospital_objectives = ['forced_hospital', 'emergency_room', 'treatment_received']
            for obj in self.objectives:
                if obj.id in hospital_objectives:
                    pass  # DO NOT OVERRIDE - obj.target_position = hospital_location

            # Community center for food bank
            if self.community_center:
                cc_objectives = ['walk_foodbank', 'food_bank_line']
                for obj in self.objectives:
                    if obj.id in cc_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = self.community_center
                        
            # Workplace
            workplace_location = None
            if building_types['pizza']:
                workplace_location = random.choice(building_types['pizza'])
            elif building_types['burger']:
                workplace_location = random.choice(building_types['burger'])
            elif building_types['store']:
                workplace_location = random.choice(building_types['store'])
                
            if workplace_location:
                work_objectives = ['work_sick', 'hiding_symptoms', 'dizzy_spell']
                for obj in self.objectives:
                    if obj.id in work_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = workplace_location
        
        # Part 4 - Credit & Debt locations
        elif self.game_part == 4:
            # Apartments for viewing
            apt_locations = building_types['apartment'] + building_types['house']
            if apt_locations and len(apt_locations) >= 2:
                # First apartment viewing
                if any(obj.id == 'first_viewing' for obj in self.objectives):
                    for obj in self.objectives:
                        if obj.id == 'first_viewing':
                            pass  # DO NOT OVERRIDE - obj.target_position = apt_locations[0]
                        elif obj.id == 'slumlord_meeting':
                            pass  # DO NOT OVERRIDE - obj.target_position = apt_locations[1] if len(apt_locations) > 1 else apt_locations[0]
            
            # Payday loan office (use office building)
            payday_location = None
            if building_types['office']:
                payday_location = random.choice(building_types['office'])
            elif building_types['bank']:
                payday_location = random.choice(building_types['bank'])
                
            if payday_location:
                payday_objectives = ['payday_storefront', 'loan_salesperson', 'payday_arrives', 'rollover_accepted']
                for obj in self.objectives:
                    if obj.id in payday_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = payday_location
                        
            # Check cashing (use store)
            if building_types['store'] or building_types['grocery']:
                check_location = random.choice(building_types['store'] + building_types['grocery'])
                check_objectives = ['check_cashing_search', 'check_cashing_fee', 'money_orders']
                for obj in self.objectives:
                    if obj.id in check_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = check_location
                        
            # Work location
            work_location = None
            if building_types['burger']:
                work_location = random.choice(building_types['burger'])
            elif building_types['pizza']:
                work_location = random.choice(building_types['pizza'])
                
            if work_location:
                work_objectives = ['new_job_start', 'work_overtime_request', 'work_calls', 'manager_complaint']
                for obj in self.objectives:
                    if obj.id in work_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = work_location
                        
            # Library for computer access
            if building_types['school']:
                lib_location = random.choice(building_types['school'])
                lib_objectives = ['credit_report_request', 'payday_loan_search', 'know_your_rights', 'unemployment_application']
                for obj in self.objectives:
                    if obj.id in lib_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = lib_location
                        
            # Community center for plasma/bankruptcy
            if self.community_center:
                cc_objectives = ['sell_plasma', 'bankruptcy_consultation']
                for obj in self.objectives:
                    if obj.id in cc_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = self.community_center
                        
            # Home objectives
            if building_types['house'] or building_types['apartment']:
                home_loc = random.choice(building_types['house'] + building_types['apartment'])
                home_objectives = ['hide_car', 'wake_up_4am', 'cash_budgeting', 'feel_weak']
                for obj in self.objectives:
                    if obj.id in home_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = home_loc
        
        # Part 5 - Healthcare locations
        elif self.game_part == 5:
            # Hospital/ER (use community center)
            if self.community_center:
                er_objectives = ['first_er_visit', 'er_visit_2', 'er_mental_health']
                for obj in self.objectives:
                    if obj.id in er_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = self.community_center
                        
            # Pharmacy (use grocery/store)
            pharmacy_location = None
            if building_types['grocery']:
                pharmacy_location = random.choice(building_types['grocery'])
            elif building_types['store']:
                pharmacy_location = random.choice(building_types['store'])
                
            if pharmacy_location:
                pharmacy_objectives = ['otc_painkillers', 'dental_school_option']
                for obj in self.objectives:
                    if obj.id in pharmacy_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = pharmacy_location
                        
            # Work location
            if building_types['burger'] or building_types['pizza']:
                work_loc = random.choice((building_types['burger'] + building_types['pizza']))
                work_objectives = ['work_mistakes', 'call_in_sick', 'panic_attack_work', 'caught_drinking']
                for obj in self.objectives:
                    if obj.id in work_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = work_loc
                        
            # Home for personal objectives
            if building_types['house'] or building_types['apartment']:
                home_location = random.choice(building_types['house'] + building_types['apartment'])
                home_objectives = ['cant_eat_properly', 'morning_drinks', 'medicaid_application']
                for obj in self.objectives:
                    if obj.id in home_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = home_location
        
        # Part 6 - Education locations
        elif self.game_part == 6:
            # Adult education center (use school)
            if building_types['school']:
                school_loc = random.choice(building_types['school'])
                school_objectives = ['adult_education_center', 'intake_appointment', 'placement_test', 
                                   'library_option', 'library_computers', 'test_day_1', 'third_math_attempt']
                for obj in self.objectives:
                    if obj.id in school_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = school_loc
                        
            # Work for schedule conflicts
            if building_types['burger'] or building_types['pizza']:
                work_location = random.choice(building_types['burger'] + building_types['pizza'])
                work_objectives = ['talk_to_manager', 'miss_monday_class']
                for obj in self.objectives:
                    if obj.id in work_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = work_location
                        
            # Home for studying
            if building_types['house'] or building_types['apartment']:
                home_loc = random.choice(building_types['house'] + building_types['apartment'])
                home_objectives = ['share_books', 'study_alone', 'youtube_university']
                for obj in self.objectives:
                    if obj.id in home_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = home_loc
        
        # Part 7 - Isolation locations
        elif self.game_part == 7:
            # Home is primary location for isolation
            if building_types['house'] or building_types['apartment']:
                home_location = random.choice(building_types['house'] + building_types['apartment'])
                home_objectives = ['weekend_move', 'empty_apartment', 'call_mom', 'thin_walls', 
                                 'tv_company', 'complete_silence', 'talk_to_self', 'still_alone']
                for obj in self.objectives:
                    if obj.id in home_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = home_location
                        
            # Work for lunch isolation
            if building_types['burger'] or building_types['pizza']:
                work_loc = random.choice(building_types['burger'] + building_types['pizza'])
                work_objectives = ['lunch_alone', 'eat_in_car']
                for obj in self.objectives:
                    if obj.id in work_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = work_loc
                        
            # Library for internet/support groups
            if building_types['school']:
                lib_loc = random.choice(building_types['school'])
                lib_objectives = ['support_group_search', 'depression_group', 'first_meeting', 
                                'online_forums', 'library_internet']
                for obj in self.objectives:
                    if obj.id in lib_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = lib_loc
                        
            # Public spaces (community center)
            if self.community_center:
                public_objectives = ['public_spaces', 'park_bench']
                for obj in self.objectives:
                    if obj.id in public_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = self.community_center
                        
            # Crisis calls (housing office)
            if building_types['office']:
                office_loc = random.choice(building_types['office'])
                call_objectives = ['crisis_hotline', 'make_call']
                for obj in self.objectives:
                    if obj.id in call_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = office_loc
        
        # Part 8 - Legal System locations
        elif self.game_part == 8:
            # Transit station (use community center)
            if self.community_center:
                transit_objectives = ['approach_turnstile', 'jump_quick']
                for obj in self.objectives:
                    if obj.id in transit_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = self.community_center
                        
            # Workplace
            if building_types['burger'] or building_types['pizza']:
                work_location = random.choice(building_types['burger'] + building_types['pizza'])
                work_objectives = ['late_to_work', 'final_warning_job', 'request_day_off']
                for obj in self.objectives:
                    if obj.id in work_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = work_location
                        
            # Courthouse/jail (use office building)
            if building_types['office']:
                court_location = random.choice(building_types['office'])
                court_objectives = ['booking_process', 'overnight_hold', 'court_transport', 
                                  'meet_defender', 'first_meeting_po']
                for obj in self.objectives:
                    if obj.id in court_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = court_location
                        
            # Home objectives
            if building_types['house'] or building_types['apartment']:
                home_loc = random.choice(building_types['house'] + building_types['apartment'])
                home_objectives = ['phone_dead', 'work_voicemail']
                for obj in self.objectives:
                    if obj.id in home_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = home_loc
                        
            # Job center (use school as library)
            if building_types['school']:
                job_center = random.choice(building_types['school'])
                job_objectives = ['application_question', 'auto_rejections']
                for obj in self.objectives:
                    if obj.id in job_objectives:
                        pass  # DO NOT OVERRIDE - obj.target_position = job_center
                        
            # Community service location
            if self.community_center:
                service_objectives = ['community_service']
                for obj in self.objectives:
                    if obj.id == 'community_service':
                        pass  # DO NOT OVERRIDE - obj.target_position = self.community_center

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
        if self.game_part >= 3:
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
                                  'ilp_callback', 'part1_complete']:  # Auto-trigger transition!
                    # Give a small delay so the UI can update
                    pygame.time.wait(100)
                    self.complete_current_objective()

    def get_current_objective(self):
        """Get the current active objective"""
        if self.current_objective_index < len(self.objectives):
            return self.objectives[self.current_objective_index]
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
        print(f"[COMPLETE] Attempting to complete objective: {current.id if current else 'None'}")
        if not current:
            return

        # First check if universal activity manager can handle this
        if self.activity_manager.start_activity_for_objective(current.id):
            # Activity started successfully
            print(f"[COMPLETE] Activity manager handled: {current.id}")
            return

        # Handle Part 1 objectives
        print(f"[COMPLETE] Game part: {self.game_part}")
        if self.game_part == 1:
            # Check for housing objectives first
            if current.id == "housing_intro":
                # Start the intro dialogue screen
                if not hasattr(self, 'intro_dialogue'):
                    from part_1_housing_stability.intro_dialogue_screen import IntroDialogueScreen
                    self.intro_dialogue = IntroDialogueScreen(self)
                self.current_activity = self.intro_dialogue
                self.current_activity.start()
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
            elif current.id == "part1_complete":
                print("Starting Part 1 Complete transition scene!")
                # Show transition scene
                self.current_activity = self.transition_scene
                self.current_activity.start()
            else:
                # Fallback for notification objectives not explicitly handled
                if current.id in self.NOTIFICATION_OBJECTIVES:
                    print(f"[COMPLETE] Handling notification objective: {current.id}")
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

    def show_notification(self, text, duration=3.0):
        """Show a notification message"""
        self.showing_notification = True
        self.notification_text = text
        self.notification_timer = duration
        self.notification_alpha = 255
        
    def draw_notification(self, screen):
        """Draw notification message"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(int(self.notification_alpha * 0.7))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Notification box dimensions
        box_width = 700
        box_height = 250
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
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

    def skip_to_part2(self):
        """Skip directly to Part 2"""
        print("Skipping to Part 2...")
        
        # Clean up any active activities
        if self.current_activity and self.current_activity.active:
            self.current_activity.completed = True
            self.current_activity.active = False
            self.current_activity = None
            
        # Set up Part 2 state
        self.game_part = 2
        self.current_day = 1
        self.game_time = "8:00 AM"
        self.current_objective_index = 0
        
        # Clear current objectives and set up Part 2 objectives
        self.objectives = []
        self.setup_part2_objectives()
        
        # Find building locations for Part 2
        self.find_building_locations()
        
        # Activate the first objective
        self.activate_current_objective()
        
        print("Part 2 started!")
        
    def skip_to_next_objective(self):
        """Admin command to skip to the next objective"""
        # If there's an active activity, complete it first
        if self.current_activity and self.current_activity.active:
            self.current_activity.completed = True
            self.current_activity.active = False
            self.current_activity = None
        
        # Special handling for certain objectives that need to trigger activities
        current = self.get_current_objective()
        print(f"[SKIP] Current objective: {current.id if current else 'None'}")
        if current and current.id == "part1_complete":
            print("[SKIP] Triggering part1_complete transition...")
            # Don't skip part1_complete - trigger it properly
            self.complete_current_objective()
        else:
            # Advance to next objective
            self.advance_to_next_objective()

            # After advancing, check if we landed on part1_complete
            new_current = self.get_current_objective()
            if new_current and new_current.id == "part1_complete":
                print("[SKIP] Advanced to part1_complete, triggering transition...")
                self.complete_current_objective()

    def update(self, dt):
        """Update objectives and activities"""
        # Update modern UI if available
        if self.use_modern_ui and self.ui_manager:
            self.ui_manager.update(dt)

        # Update notification display
        if self.showing_notification:
            self.notification_timer -= dt
            if self.notification_timer <= 0:
                # Start fading out
                self.notification_alpha = max(0, self.notification_alpha - 300 * dt)
                if self.notification_alpha <= 0:
                    self.showing_notification = False
                    # Advance to next objective after notification is shown
                    self.advance_to_next_objective()
        
        # Update universal activity manager first
        if self.activity_manager.current_activity:
            if self.activity_manager.update(dt):
                # Activity completed
                self.advance_to_next_objective()
            return

        # Update current activity if any
        if self.current_activity and self.current_activity.active:
            self.current_activity.update(dt)
            # Check if activity completed
            if self.current_activity.completed:
                print(f"Activity completed: {self.current_activity.__class__.__name__}")
                # Special handling for transition scene
                if isinstance(self.current_activity, TransitionScene):
                    print("TransitionScene completed - switching to Part 2")
                    # Complete the transition to Part 2
                    self.game_part = 2
                    self.current_day = 1
                    self.game_time = "8:00 AM"
                    self.current_objective_index = 0
                    self.setup_objectives()  # Reset objectives for Part 2
                    self.find_building_locations()  # Find new buildings for Part 2
                    self.current_activity = None
                    self.activate_current_objective()
                    # Debug: Verify Part 2 setup
                    print(f"[TRANSITION] Part 2 setup complete:")
                    print(f"  - Game part: {self.game_part}")
                    print(f"  - Total objectives: {len(self.objectives)}")
                    print(f"  - First objective: {self.objectives[0].id if self.objectives else 'NONE'}")
                    print(f"  - Current index: {self.current_objective_index}")
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

        # Use modern UI if available - this is the only UI we need
        if self.use_modern_ui and self.ui_manager:
            self.ui_manager.draw(screen)
            return  # Exit immediately after drawing modern UI

        # If no modern UI, just return (don't draw fallback UI)
        return

        # Draw notification if showing
        if self.showing_notification:
            self.draw_notification(screen)
            return  # Don't draw other UI when notification is showing
            
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

    def setup_part3_objectives(self):
        """Part 3 - Financial Stress & Survival Decisions"""
        self.objectives = [
            # Day 1 - The Crisis Begins
            GameObjective("wake_up_broke", "Monday Morning Crisis", "You wake up with only $5.47 in your bank account", None, "Press E to check phone"),
            GameObjective("check_notifications", "27 Notifications", "Overdraft alerts, bill reminders, and missed calls flood your screen", None, "Press E to read"),
            GameObjective("check_bank", "Visit Bank", "Go to the bank to understand what happened", None, "Press E to enter bank"),
            GameObjective("overdraft_explained", "The Cascade", "One autopay triggered 5 overdraft fees totaling $175", None, "Press E to continue"),
            GameObjective("plead_with_teller", "Beg for Help", "Plead with bank teller to reverse the fees", None, "Press E to plead"),
            GameObjective("one_fee_reversed", "Small Victory", "Bank reverses one $35 fee, you still owe $140", None, "Press E to leave"),
            
            # Food vs Bills Dilemma
            GameObjective("empty_fridge", "Check Food Supply", "Return home to find only condiments and expired milk", None, "Press E to search cabinets"),
            GameObjective("count_change", "Count Your Money", "Find $2.13 in couch cushions, total: $7.60", None, "Press E to continue"),
            GameObjective("food_decision", "Impossible Choice", "Phone bill ($45) due today. Choose: Keep phone service or eat?", None, "Press E to decide"),
            GameObjective("choose_food", "Choose Survival", "You choose food. Phone will be disconnected at midnight", None, "Press E to continue"),
            GameObjective("dollar_menu", "Dollar Store", "Walk to dollar store with your $7.60", None, "Press E to shop"),
            GameObjective("food_math", "Survival Math", "Calculate: Rice $1, beans $1, bread $1, peanut butter $2.50, leaves $2.10", None, "Press E to checkout"),
            
            # Day 2 - Disconnection
            GameObjective("phone_shutoff_warning", "Final Warning", "11:47 PM - Final warning text before disconnection", None, "Press E to read"),
            GameObjective("last_calls", "Desperate Calls", "Try calling family for help before midnight", None, "Press E to call"),
            GameObjective("no_answer_family", "No Response", "Mom doesn't answer, dad's number disconnected, sister in another state", None, "Press E to continue"),
            GameObjective("phone_dies", "Service Terminated", "12:00 AM - 'No Service' appears on phone", None, "Press E to accept"),
            
            # Day 3 - Missed Opportunities
            GameObjective("walk_to_library", "Find Connection", "Walk 3 miles to library for wifi", None, "Press E to walk"),
            GameObjective("library_computer", "Check Email", "47 new emails. Wait 25 minutes for computer", None, "Press E to use computer"),
            GameObjective("job_email", "Missed Interview!", "Email from yesterday: 'Please call to schedule interview'", None, "Press E to read"),
            GameObjective("try_calling", "No Phone", "Can't call back without phone service", None, "Press E to continue"),
            GameObjective("email_response", "Desperate Email", "Send email explaining situation, hoping they understand", None, "Press E to send"),
            GameObjective("auto_rejection", "Too Late", "Auto-reply: 'Position has been filled'", None, "Press E to close"),
            
            # Day 4 - Food Bank
            GameObjective("hunger_pains", "Day 4 Hunger", "Sharp stomach pains from rationing food", None, "Press E to continue"),
            GameObjective("food_bank_search", "Find Food Bank", "Search for local food bank at library", None, "Press E to search"),
            GameObjective("print_directions", "Get Directions", "Print directions, costs $0.10 you don't have", None, "Press E to memorize"),
            GameObjective("walk_foodbank", "Long Walk", "Walk 2.5 miles to community center", None, "Press E to walk"),
            GameObjective("food_bank_line", "The Line", "137 people already in line, 2 hour wait", None, "Press E to wait"),
            GameObjective("income_verification", "Prove Your Poverty", "Must show proof of income/address you don't have", None, "Press E to explain"),
            GameObjective("turned_away", "Denied", "Turned away for lack of documentation", None, "Press E to leave"),
            GameObjective("dumpster_consideration", "Rock Bottom", "Pass restaurant dumpster, seriously consider it", None, "Press E to keep walking"),
            
            # Day 5 - Eviction Notice
            GameObjective("eviction_posted", "Red Notice", "5-DAY PAY OR QUIT notice taped to door", None, "Press E to read"),
            GameObjective("rent_calculation", "The Math", "Owe: $750 rent + $150 late fee + $50 posting fee = $950", None, "Press E to panic"),
            GameObjective("call_landlord_attempt", "No Phone", "Need to call landlord but have no phone", None, "Press E to continue"),
            GameObjective("knock_neighbors", "Ask Neighbors", "Knock on 6 doors asking to use phone, all say no", None, "Press E to continue"),
            
            # Day 6 - Selling Everything
            GameObjective("inventory_items", "Take Inventory", "List everything you own that has value", None, "Press E to list"),
            GameObjective("pawn_shop_walk", "Pawn Shop", "Carry TV, laptop, and guitar 1.5 miles to pawn shop", None, "Press E to walk"),
            GameObjective("lowball_offer", "Insulting Offer", "Items worth $800+, offered $120 total", None, "Press E to negotiate"),
            GameObjective("final_offer", "Take It or Leave It", "Final offer: $140 for everything", None, "Press E to accept"),
            GameObjective("not_enough", "Still Short", "Have $147.60 total, need $950 for rent", None, "Press E to despair"),
            
            # Day 7 - Getting Sick
            GameObjective("fever_starts", "Feeling Sick", "Wake up sweating with 101° fever", None, "Press E to continue"),
            GameObjective("no_thermometer", "Can't Verify", "Sold thermometer yesterday, can't check temperature", None, "Press E to continue"),
            GameObjective("work_sick_choice", "Impossible Choice", "Call in sick and get fired, or work with fever?", None, "Press E to choose"),
            GameObjective("work_sick", "Work Anyway", "Take 4 expired ibuprofen and go to work", None, "Press E to work"),
            GameObjective("hiding_symptoms", "Hide Illness", "Splash cold water on face every 30 minutes", None, "Press E to continue"),
            GameObjective("customer_complaint", "Making Mistakes", "Fever causes mistakes, customers complaining", None, "Press E to continue"),
            
            # Day 8 - Collapse
            GameObjective("dizzy_spell", "Room Spinning", "Sudden dizziness while carrying order", None, "Press E to steady yourself"),
            GameObjective("collapse_work", "Collapse", "Collapse in front of customers, hitting head on counter", None, "Press E to continue"),
            GameObjective("ambulance_called", "911 Called", "Manager calls ambulance despite your protests", None, "Press E to refuse"),
            GameObjective("forced_hospital", "No Choice", "EMTs insist on hospital for head injury", None, "Press E to go"),
            GameObjective("emergency_room", "ER Wait", "Wait 6 hours in ER with concussion", None, "Press E to wait"),
            GameObjective("treatment_received", "Basic Treatment", "CT scan, IV fluids, diagnosis: exhaustion and dehydration", None, "Press E to continue"),
            
            # Day 9 - Medical Debt
            GameObjective("discharge_papers", "Discharge", "Handed discharge papers and told to rest for 48 hours", None, "Press E to read"),
            GameObjective("billing_preview", "The Bill Preview", "Estimated charges: $4,500-6,000", None, "Press E to panic"),
            GameObjective("work_termination", "Job Lost", "Text from manager: 'We had to let you go, sorry'", None, "Press E to read"),
            GameObjective("eviction_court", "Court Date", "Eviction court date in 2 days, still no money", None, "Press E to accept fate"),
            
            # Day 10 - The Cycle
            GameObjective("homeless_research", "Research Shelters", "At library, research homeless shelters", None, "Press E to search"),
            GameObjective("shelter_waitlist", "All Full", "Every shelter has a waitlist, 2-4 weeks minimum", None, "Press E to continue"),
            GameObjective("car_living", "Plan B", "Research living in car, but car was repossessed last month", None, "Press E to continue"),
            GameObjective("final_night", "Last Night", "Spend possibly last night in apartment", None, "Press E to reflect"),
            GameObjective("cycle_complete", "The Poverty Trap", "Started with $5 overdraft, now homeless and $5000+ in debt", None, "Press E to understand"),
            GameObjective("system_analysis", "The System", "Realize how one small financial shock destroys everything", None, "Press E to continue"),
            GameObjective("chapter_end", "Chapter Complete", "Financial stress leads to homelessness in just 10 days", None, "Press E to finish"),
        ]
    
    def setup_part4_objectives(self):
        """Part 4 - Credit, Debt, and Financial Systems"""
        self.objectives = [
            # Week 1 - The Credit Check
            GameObjective("need_new_apartment", "Eviction Complete", "You've been evicted, need new apartment immediately", None, "Press E to continue"),
            GameObjective("apartment_search", "Apartment Hunt", "Find 3 apartments within budget on Craigslist", None, "Press E to search"),
            GameObjective("first_viewing", "First Viewing", "Nice studio apartment, $650/month, seems perfect", None, "Press E to view"),
            GameObjective("application_fee", "Application Process", "Fill out application, pay $35 non-refundable fee", None, "Press E to apply"),
            GameObjective("credit_check_wait", "Anxious Wait", "Landlord says they'll call after credit check", None, "Press E to wait"),
            GameObjective("credit_denial_call", "Rejection Call", "'Sorry, your credit score of 487 is too low'", None, "Press E to listen"),
            GameObjective("credit_report_request", "Check Credit Report", "Request free annual credit report online", None, "Press E to request"),
            GameObjective("credit_report_shock", "The Damage", "Medical debt, old utility bills, student loans in default", None, "Press E to review"),
            
            # Week 2 - Desperate Measures
            GameObjective("second_apartment", "Try Again", "Another apartment, seedier area, $500/month", None, "Press E to view"),
            GameObjective("slumlord_meeting", "Sketchy Landlord", "No credit check but wants 3 months upfront", None, "Press E to negotiate"),
            GameObjective("impossible_deposit", "Can't Afford", "Need $1,500 upfront, you have $147", None, "Press E to leave"),
            GameObjective("couch_surfing", "Friend's Couch", "Text everyone you know asking for temporary shelter", None, "Press E to text"),
            GameObjective("one_week_max", "Temporary Relief", "Friend says you can stay one week maximum", None, "Press E to accept"),
            GameObjective("storage_unit", "Store Belongings", "Put remaining possessions in storage, $50/month", None, "Press E to store"),
            
            # Week 3 - Payday Loan Trap
            GameObjective("new_job_start", "Minimum Wage Job", "Start at fast food place, $9/hour, 25 hours/week", None, "Press E to work"),
            GameObjective("first_paycheck_two_weeks", "Two Week Wait", "Won't get paid for two weeks, need money now", None, "Press E to calculate"),
            GameObjective("payday_loan_search", "Quick Cash", "Google 'need money today', find payday lenders", None, "Press E to search"),
            GameObjective("payday_storefront", "EZ Money", "Visit 'EZ Money Payday Loans' storefront", None, "Press E to enter"),
            GameObjective("loan_salesperson", "Friendly Staff", "'We're here to help! How much do you need?'", None, "Press E to talk"),
            GameObjective("loan_amount_needed", "Calculate Needs", "Need $300 for food, transport, phone reconnection", None, "Press E to request"),
            GameObjective("loan_terms_explained", "The Fine Print", "'$300 loan, $45 fee, due in 2 weeks. That's just 15%!'", None, "Press E to listen"),
            GameObjective("apr_hidden", "Hidden Truth", "391% APR mentioned quickly in tiny print", None, "Press E to sign anyway"),
            
            # Week 4 - First Payment Due
            GameObjective("payday_arrives", "First Paycheck", "Receive $360 after taxes for 2 weeks work", None, "Press E to calculate"),
            GameObjective("loan_due", "Payment Day", "Owe $345 to payday lender", None, "Press E to pay"),
            GameObjective("fifteen_left", "$15 Remaining", "Have $15 left for next 2 weeks", None, "Press E to panic"),
            GameObjective("rollover_option", "Rollover Offered", "'Just pay the $45 fee, extend loan 2 weeks!'", None, "Press E to consider"),
            GameObjective("rollover_accepted", "No Choice", "Pay $45 fee, still owe $300", None, "Press E to rollover"),
            
            # Month 2 - Debt Multiplication
            GameObjective("second_lender", "Second Loan", "Take loan from different lender to pay first", None, "Press E to apply"),
            GameObjective("third_lender", "Third Loan", "Now juggling loans from 3 different lenders", None, "Press E to track"),
            GameObjective("debt_calendar", "Payment Schedule", "Mark calendar with different due dates", None, "Press E to organize"),
            GameObjective("total_owed", "Do The Math", "Original $300 needed, now owe $1,247 total", None, "Press E to calculate"),
            GameObjective("work_overtime_request", "More Hours", "Beg manager for more hours to pay debts", None, "Press E to plead"),
            GameObjective("hours_denied", "No Extra Hours", "'Sorry, company policy limits part-timers to 29 hours'", None, "Press E to accept"),
            
            # Month 3 - Collections Begin
            GameObjective("first_default", "First Default", "Can't pay all three lenders, choose which to skip", None, "Press E to decide"),
            GameObjective("collection_calls_start", "Calls Begin", "Unknown numbers calling 8+ times daily", None, "Press E to ignore"),
            GameObjective("voicemail_full", "Threatening Messages", "Voicemail full of threats and legal warnings", None, "Press E to listen"),
            GameObjective("work_calls", "Calls at Work", "Collectors calling your workplace", None, "Press E to answer"),
            GameObjective("manager_complaint", "Boss Warning", "'These calls are disrupting business, fix this'", None, "Press E to apologize"),
            GameObjective("know_your_rights", "Research Rights", "Google 'debt collection harassment laws'", None, "Press E to learn"),
            GameObjective("cease_desist_letter", "Write Letter", "Draft cease and desist letter you can't afford to mail", None, "Press E to write"),
            
            # Month 4 - Banking Consequences
            GameObjective("bank_letter", "Bank Notice", "Account closed due to negative history", None, "Press E to read"),
            GameObjective("direct_deposit_lost", "No Direct Deposit", "Must receive paper paychecks now", None, "Press E to inform employer"),
            GameObjective("check_cashing_search", "Cash Checks", "Find check cashing store", None, "Press E to locate"),
            GameObjective("check_cashing_fee", "5% Gone", "$400 check becomes $380 after fees", None, "Press E to cash"),
            GameObjective("money_orders", "Bill Payment", "Buy money orders to pay rent (more fees)", None, "Press E to purchase"),
            GameObjective("cash_budgeting", "Envelope System", "Keep cash in envelopes, constantly worried about theft", None, "Press E to organize"),
            
            # Month 5 - Wage Garnishment
            GameObjective("court_summons", "Legal Papers", "Served court papers at work, embarrassing", None, "Press E to read"),
            GameObjective("court_date_work_conflict", "Court vs Work", "Court date during shift, boss won't give time off", None, "Press E to choose"),
            GameObjective("default_judgment", "Judgment Entered", "Didn't appear in court, automatic judgment against you", None, "Press E to read"),
            GameObjective("garnishment_notice", "25% Garnished", "Court orders 25% wage garnishment", None, "Press E to calculate"),
            GameObjective("new_paycheck", "Reduced Pay", "$400 paycheck now $300 after garnishment", None, "Press E to despair"),
            GameObjective("cant_afford_food", "Below Survival", "Can't afford food after rent and transport", None, "Press E to skip meals"),
            
            # Month 6 - Transportation Crisis
            GameObjective("car_payment_behind", "3 Months Behind", "Car payment 90 days overdue", None, "Press E to check"),
            GameObjective("repo_warning", "Final Notice", "Car will be repossessed without immediate payment", None, "Press E to read"),
            GameObjective("hide_car", "Hide Vehicle", "Park car at different locations to avoid repo", None, "Press E to hide"),
            GameObjective("repo_truck_arrives", "They Found It", "Wake up to repo truck taking your car", None, "Press E to watch"),
            GameObjective("plead_with_driver", "Beg Driver", "'Please, I need it for work!' 'Sorry, just doing my job'", None, "Press E to plead"),
            GameObjective("car_gone", "Transportation Lost", "Watch your only transport disappear", None, "Press E to accept"),
            
            # Month 7 - Spiraling Consequences
            GameObjective("bus_research", "Public Transit", "Research bus routes to work", None, "Press E to map"),
            GameObjective("four_hour_commute", "2 Hours Each Way", "Bus route takes 2 hours vs 25 minute drive", None, "Press E to accept"),
            GameObjective("wake_up_4am", "4AM Wakeup", "Must wake at 4AM for 7AM shift", None, "Press E to set alarm"),
            GameObjective("first_late", "Miss Bus", "Miss transfer, arrive 1 hour late", None, "Press E to run"),
            GameObjective("final_warning", "Last Warning", "'One more tardy and you're terminated'", None, "Press E to promise"),
            GameObjective("second_late", "Bus Breaks Down", "Bus breaks down, 2 hours late to work", None, "Press E to explain"),
            GameObjective("fired_attendance", "Terminated", "'We need reliable employees, collect your last check'", None, "Press E to leave"),
            
            # Month 8 - Rock Bottom
            GameObjective("unemployment_application", "File Unemployment", "Apply for unemployment benefits", None, "Press E to apply"),
            GameObjective("benefits_denied", "Claim Denied", "'Terminated for cause, no benefits'", None, "Press E to read"),
            GameObjective("sell_plasma", "Sell Plasma", "Donate plasma twice weekly for $60", None, "Press E to donate"),
            GameObjective("feel_weak", "Getting Weaker", "Dizzy and weak from frequent plasma donation", None, "Press E to continue"),
            GameObjective("bankruptcy_consultation", "Free Consultation", "Meet bankruptcy attorney at legal aid", None, "Press E to meet"),
            GameObjective("bankruptcy_fee", "$1,500 Fee", "'Bankruptcy costs $1,500 upfront' - ironic", None, "Press E to laugh bitterly"),
            GameObjective("no_escape", "Truly Trapped", "No job, no car, no bank, no bankruptcy option", None, "Press E to realize"),
            
            # Final Realization
            GameObjective("debt_total", "Final Tally", "Started needing $300, now owe $8,432", None, "Press E to calculate"),
            GameObjective("system_rigged", "The System", "Realize every 'solution' created more problems", None, "Press E to understand"),
            GameObjective("poverty_expensive", "Being Poor Costs", "Being poor is the most expensive thing in America", None, "Press E to reflect"),
            GameObjective("chapter_4_end", "Debt Prison", "Trapped in modern debtor's prison with no walls", None, "Press E to complete"),
        ]
    
    def setup_part5_objectives(self):
        """Part 5 - Healthcare & Mental Health"""
        self.objectives = [
            # Week 1 - The Pain Begins
            GameObjective("tooth_pain_starts", "Saturday Night", "Sharp pain in back molar while eating dinner", None, "Press E to continue"),
            GameObjective("inspect_tooth", "Check Mirror", "See dark spot on tooth, gum is swollen and red", None, "Press E to examine"),
            GameObjective("weekend_clinic_search", "Find Help", "Google 'emergency dentist open Sunday'", None, "Press E to search"),
            GameObjective("no_weekend_dentists", "All Closed", "Only option is hospital ER for pain", None, "Press E to continue"),
            GameObjective("otc_painkillers", "Drug Store", "Buy maximum strength ibuprofen and Orajel", None, "Press E to purchase"),
            GameObjective("temporary_relief", "Brief Relief", "Pain dulls for 3 hours, then returns worse", None, "Press E to endure"),
            
            # Week 2 - Seeking Treatment
            GameObjective("monday_calls", "Call Dentists", "Call 12 dental offices Monday morning", None, "Press E to call"),
            GameObjective("no_insurance_quotes", "Cash Prices", "'Root canal $1,400, crown $1,200, extraction $400'", None, "Press E to despair"),
            GameObjective("payment_plans_denied", "No Payment Plan", "'We require payment in full at time of service'", None, "Press E to hang up"),
            GameObjective("dental_school_option", "Dental School", "Find dental school clinic, 3-month wait for appointment", None, "Press E to continue"),
            GameObjective("pain_increasing", "Worse Daily", "Pain now constant, can't chew on left side", None, "Press E to suffer"),
            
            # Week 3 - ER Visit #1
            GameObjective("cant_sleep_pain", "3AM Crisis", "Pain so severe you can't sleep for 48 hours", None, "Press E to give up"),
            GameObjective("first_er_visit", "Emergency Room", "Drive to ER at 3AM in agony", None, "Press E to enter"),
            GameObjective("er_wait_7hours", "7 Hour Wait", "Wait in ER lobby with screaming pain", None, "Press E to wait"),
            GameObjective("er_doctor_exam", "5 Minute Exam", "'Infected tooth, needs dentist, here's antibiotics'", None, "Press E to listen"),
            GameObjective("er_prescriptions", "Scripts Given", "Antibiotics and 12 Vicodin pills prescribed", None, "Press E to receive"),
            GameObjective("er_bill_preview", "Financial Officer", "'ER visit will be approximately $2,800'", None, "Press E to sign"),
            
            # Week 4 - Addiction Risk
            GameObjective("pain_pills_work", "Sweet Relief", "First Vicodin eliminates pain completely", None, "Press E to feel relief"),
            GameObjective("pills_running_out", "Counting Pills", "8 pills left, trying to ration them", None, "Press E to count"),
            GameObjective("breakthrough_pain", "Pain Returns", "Pain breaks through even with pills", None, "Press E to take more"),
            GameObjective("pills_gone", "Supply Exhausted", "All pills gone in 5 days instead of 12", None, "Press E to panic"),
            GameObjective("withdrawal_begins", "Double Agony", "Tooth pain plus opioid withdrawal symptoms", None, "Press E to suffer"),
            
            # Month 2 - Mental Health Decline
            GameObjective("cant_eat_properly", "Liquid Diet", "Can only consume liquids and soft foods", None, "Press E to blend food"),
            GameObjective("weight_loss", "Lost 15 Pounds", "Malnutrition from inability to eat properly", None, "Press E to continue"),
            GameObjective("work_mistakes", "Can't Focus", "Making errors at work due to pain and exhaustion", None, "Press E to struggle"),
            GameObjective("supervisor_meeting", "Written Warning", "'Your performance has declined significantly'", None, "Press E to nod"),
            GameObjective("isolation_begins", "Withdrawing", "Stop socializing due to pain and embarrassment", None, "Press E to hide"),
            GameObjective("depression_sets_in", "Dark Thoughts", "'Is this my life now? Constant pain forever?'", None, "Press E to spiral"),
            
            # Month 3 - Crisis Point
            GameObjective("abscess_forms", "Face Swelling", "Wake up with face swollen like baseball", None, "Press E to panic"),
            GameObjective("fever_starts", "103° Fever", "Infection spreading, fever and chills", None, "Press E to shake"),
            GameObjective("call_in_sick", "Miss Work", "Call in sick for third time this month", None, "Press E to call"),
            GameObjective("final_warning_work", "Last Chance", "'One more absence and you're terminated'", None, "Press E to worry"),
            GameObjective("er_visit_2", "ER Again", "Return to ER with life-threatening infection", None, "Press E to go"),
            GameObjective("emergency_extraction", "Emergency Surgery", "Tooth extracted immediately to save your life", None, "Press E to consent"),
            GameObjective("post_surgery", "Aftermath", "Gap in smile, but infection finally clearing", None, "Press E to recover"),
            
            # Month 4 - Mental Health Crisis
            GameObjective("gap_tooth_shame", "Visible Gap", "Ashamed of missing tooth, avoid smiling", None, "Press E to hide smile"),
            GameObjective("panic_attack_work", "Panic Attack", "Sudden panic attack during customer interaction", None, "Press E to hyperventilate"),
            GameObjective("er_mental_health", "ER Visit #3", "Coworker calls 911 for your panic attack", None, "Press E to be transported"),
            GameObjective("psych_evaluation", "Crisis Eval", "'Severe anxiety and depression, need treatment'", None, "Press E to listen"),
            GameObjective("mental_health_referral", "Get Help", "Referred to community mental health center", None, "Press E to take paper"),
            GameObjective("six_month_wait", "Wait List", "'First available appointment in 6 months'", None, "Press E to despair"),
            
            # Month 5 - Spiraling
            GameObjective("self_medicating", "Dangerous Coping", "Start drinking to numb physical and emotional pain", None, "Press E to drink"),
            GameObjective("morning_drinks", "Can't Stop", "Need drinks to stop hands shaking before work", None, "Press E to hide flask"),
            GameObjective("caught_drinking", "Discovered", "Manager smells alcohol on your breath", None, "Press E to deny"),
            GameObjective("fired_immediately", "Terminated", "'Clean out your locker, you're done'", None, "Press E to leave"),
            GameObjective("unemployment_denied_2", "No Benefits", "Fired for cause, unemployment claim denied", None, "Press E to read"),
            
            # Month 6 - Rock Bottom
            GameObjective("medical_bills_arrive", "Bill Tsunami", "$2,800 + $4,200 + $1,900 = $8,900 in medical debt", None, "Press E to open bills"),
            GameObjective("collections_medical", "Debt Collectors", "Medical debt sold to aggressive collectors", None, "Press E to ignore calls"),
            GameObjective("eviction_again", "Losing Home", "Can't pay rent without job, eviction filed", None, "Press E to read notice"),
            GameObjective("medicaid_application", "Last Hope", "Apply for Medicaid but need documents", None, "Press E to apply"),
            GameObjective("medicaid_denied", "Denied Again", "'Made too much money last year to qualify'", None, "Press E to scream"),
            
            # Final Realization
            GameObjective("preventable_suffering", "The Truth", "All of this from one cavity that needed a $200 filling", None, "Press E to understand"),
            GameObjective("system_broken", "Healthcare Reality", "Can get emergency care but not preventive care", None, "Press E to comprehend"),
            GameObjective("permanent_damage", "Lasting Impact", "Lost tooth, lost job, gained addiction risk, PTSD", None, "Press E to reflect"),
            GameObjective("healthcare_poor_tax", "Poverty Penalty", "Being poor means waiting until you're dying for care", None, "Press E to accept"),
            GameObjective("chapter_5_complete", "Broken System", "The most expensive healthcare is no healthcare", None, "Press E to finish"),
        ]
    
    def setup_part6_objectives(self):
        """Part 6 - Education Access & Confusion"""
        self.objectives = [
            # Week 1 - The Decision
            GameObjective("dropout_regret", "Looking Back", "Dropped out at 16 to help family, now 19 without diploma", None, "Press E to reflect"),
            GameObjective("job_listings", "Dead Ends", "Every decent job requires 'High school diploma or equivalent'", None, "Press E to scroll"),
            GameObjective("ged_research", "Find Programs", "Google 'GED classes near me free'", None, "Press E to search"),
            GameObjective("adult_education_center", "Adult Ed Center", "Find local adult education center offering GED prep", None, "Press E to visit"),
            GameObjective("intake_appointment", "Orientation", "Attend mandatory orientation session", None, "Press E to attend"),
            GameObjective("placement_test", "Assessment Test", "Take 3-hour placement test to determine level", None, "Press E to take test"),
            GameObjective("test_results", "6th Grade Level", "Math: 6th grade, Reading: 8th grade, Writing: 7th grade", None, "Press E to see results"),
            GameObjective("reality_hits", "Years Behind", "Counselor: 'You'll need 12-18 months of classes'", None, "Press E to process"),
            
            # Week 2 - Schedule Nightmare
            GameObjective("class_times", "Schedule Given", "Classes: Mon/Wed/Fri 9AM-12PM, Tues/Thurs 6PM-9PM", None, "Press E to review"),
            GameObjective("work_schedule_conflict", "Impossible Fit", "Work schedule: Varies weekly, often morning shifts", None, "Press E to worry"),
            GameObjective("talk_to_manager", "Request Fixed Schedule", "Ask manager for consistent evening shifts", None, "Press E to ask"),
            GameObjective("manager_response", "Bad News", "'Full-timers get schedule preference, you get what's left'", None, "Press E to plead"),
            GameObjective("hours_cut_punishment", "Retaliation", "Next week: Only scheduled 12 hours", None, "Press E to see schedule"),
            GameObjective("choose_priority", "Hard Choice", "Can't afford less hours but need education", None, "Press E to decide"),
            
            # Week 3 - Hidden Costs
            GameObjective("free_classes_but", "'Free' Classes", "Classes free but books, supplies, tests cost money", None, "Press E to learn"),
            GameObjective("book_list", "Required Materials", "4 textbooks @ $60 each, calculator $45, workbooks $30", None, "Press E to calculate"),
            GameObjective("total_cost", "$315 Needed", "Total materials cost: $315 you don't have", None, "Press E to panic"),
            GameObjective("library_option", "Check Library", "Rush to library to borrow textbooks", None, "Press E to search"),
            GameObjective("books_unavailable", "None Available", "All GED books checked out, 3-month wait list", None, "Press E to add name"),
            GameObjective("old_edition_find", "Outdated Books", "Find 2008 edition (test changed in 2014)", None, "Press E to take anyway"),
            GameObjective("share_books", "Book Sharing", "Arrange to share books with classmate", None, "Press E to coordinate"),
            
            # Month 2 - Digital Divide
            GameObjective("online_component", "Computer Required", "Teacher: 'Complete online assignments by Sunday'", None, "Press E to worry"),
            GameObjective("no_computer_home", "No Computer", "No computer or internet at home", None, "Press E to continue"),
            GameObjective("library_computers", "Library Plan", "Plan to use library computers after work", None, "Press E to go"),
            GameObjective("library_hours_issue", "Closed Early", "Library closes at 6PM, you get off work at 5:30PM", None, "Press E to rush"),
            GameObjective("twenty_minutes", "Not Enough Time", "Only get 20 minutes before closing", None, "Press E to work fast"),
            GameObjective("assignments_incomplete", "Can't Finish", "Submit incomplete assignments week after week", None, "Press E to submit"),
            GameObjective("teacher_concern", "Falling Behind", "'You're capable but not completing the work'", None, "Press E to explain"),
            
            # Month 3 - Attendance Issues
            GameObjective("miss_monday_class", "Mandatory Overtime", "Boss demands Monday overtime, miss class", None, "Press E to work"),
            GameObjective("miss_wednesday", "Bus Breakdown", "Bus breaks down, miss Wednesday class", None, "Press E to wait"),
            GameObjective("attendance_warning", "Warning Letter", "'One more absence and you'll be dropped'", None, "Press E to read"),
            GameObjective("sick_child_roommate", "Babysitting Crisis", "Roommate's kid sick, no one else to watch", None, "Press E to stay home"),
            GameObjective("dropped_from_program", "Dismissed", "Dropped from program for attendance", None, "Press E to read email"),
            GameObjective("appeal_process", "Try Appeal", "File appeal explaining circumstances", None, "Press E to write"),
            GameObjective("appeal_denied", "No Exceptions", "'Policy applies equally to all students'", None, "Press E to accept"),
            
            # Month 4 - Second Attempt
            GameObjective("wait_period", "Wait 6 Months", "Must wait 6 months to re-enroll", None, "Press E to wait"),
            GameObjective("second_try", "Try Again", "Re-enroll with renewed determination", None, "Press E to register"),
            GameObjective("same_problems", "Nothing Changed", "Same schedule conflicts, same money issues", None, "Press E to struggle"),
            GameObjective("study_alone", "Self-Study", "Try studying with outdated books alone", None, "Press E to study"),
            GameObjective("practice_test_fail", "Not Ready", "Fail practice test by wide margin", None, "Press E to see score"),
            GameObjective("tutoring_cost", "Tutor Needed", "Need tutoring but costs $40/hour", None, "Press E to inquire"),
            GameObjective("youtube_university", "Free Resources", "Resort to random YouTube videos", None, "Press E to watch"),
            
            # Month 5 - Testing Barriers
            GameObjective("ready_to_test", "Feel Prepared", "Finally feel ready to take real GED", None, "Press E to register"),
            GameObjective("test_fee_shock", "$120 Fee", "Test costs $30 per subject x 4 subjects", None, "Press E to calculate"),
            GameObjective("save_for_test", "Save Money", "Save for 2 months to afford test", None, "Press E to save"),
            GameObjective("test_center_far", "Testing Location", "Nearest test center 45 minutes by bus", None, "Press E to map"),
            GameObjective("test_day_1", "First Test", "Take Math and Science tests", None, "Press E to test"),
            GameObjective("mixed_results", "Pass One", "Pass Science, fail Math by 2 points", None, "Press E to see results"),
            GameObjective("retake_fee", "Pay Again", "Must pay another $30 to retake Math", None, "Press E to pay"),
            
            # Month 6 - Breaking Point
            GameObjective("test_anxiety", "Test Fear", "Develop severe test anxiety from failures", None, "Press E to panic"),
            GameObjective("third_math_attempt", "Try Again", "Third attempt at Math section", None, "Press E to test"),
            GameObjective("fail_again", "Still Failing", "Fail by 1 point this time", None, "Press E to despair"),
            GameObjective("give_up_temporary", "Take Break", "Decide to 'take a break' from testing", None, "Press E to quit"),
            GameObjective("years_pass", "Time Flies", "'Temporary' break becomes 2 years", None, "Press E to realize"),
            
            # Final Realization
            GameObjective("still_no_diploma", "Still Stuck", "Still working minimum wage without diploma", None, "Press E to reflect"),
            GameObjective("systemic_barriers", "The Obstacles", "Count the barriers: time, money, transport, technology", None, "Press E to list"),
            GameObjective("not_about_intelligence", "Smart Enough", "You're smart enough - system isn't designed for you", None, "Press E to understand"),
            GameObjective("education_privilege", "Hidden Privilege", "Education access requires resources you don't have", None, "Press E to see clearly"),
            GameObjective("cycle_continues", "Poverty Trap", "Need education for better job, need better job for education", None, "Press E to accept"),
            GameObjective("chapter_6_end", "Dreams Deferred", "Another generation lost to systemic barriers", None, "Press E to complete"),
        ]
    
    def setup_part7_objectives(self):
        """Part 7 - Isolation & Lack of Support"""
        self.objectives = [
            # Week 1 - The Departure
            GameObjective("roommate_news", "Tuesday Evening", "Roommate: 'I'm moving back home this weekend'", None, "Press E to respond"),
            GameObjective("why_leaving", "The Reason", "'Can't afford this anymore, parents will let me move back'", None, "Press E to understand"),
            GameObjective("no_parents_option", "No Safety Net", "Your parents kicked you out at 18, no going back", None, "Press E to remember"),
            GameObjective("rent_panic", "Math Time", "Rent: $800 total, your half: $400, full amount: impossible", None, "Press E to calculate"),
            GameObjective("beg_roommate", "Please Stay", "Beg roommate to stay one more month", None, "Press E to plead"),
            GameObjective("final_no", "Decision Final", "'Sorry, I already told my parents. Good luck'", None, "Press E to accept"),
            GameObjective("weekend_move", "Moving Day", "Help them load boxes, then watch only friend leave", None, "Press E to help"),
            GameObjective("empty_apartment", "Alone Now", "Stand in empty apartment, their room echoing", None, "Press E to listen"),
            
            # Week 2 - Failed Connections
            GameObjective("find_new_roommate", "Post Ads", "Post on Craigslist, Facebook, everywhere", None, "Press E to post"),
            GameObjective("sketchy_responses", "Bad Options", "Only responses are scams or people who seem dangerous", None, "Press E to screen"),
            GameObjective("call_mom", "Try Family", "Swallow pride, call mom for first time in months", None, "Press E to dial"),
            GameObjective("mom_cold", "Cold Response", "'You made your choice. Figure it out yourself'", None, "Press E to hang up"),
            GameObjective("dad_disconnected", "Dad's Number", "Dad's phone disconnected, no forwarding number", None, "Press E to try"),
            GameObjective("siblings_distant", "Siblings Busy", "Sister: 'Sorry, dealing with my own stuff'", None, "Press E to understand"),
            GameObjective("extended_family", "Last Resort", "Try cousins, aunts, uncles - all 'can't help right now'", None, "Press E to give up"),
            
            # Week 3 - Work Isolation
            GameObjective("lunch_alone", "Break Room", "Eat lunch alone while coworkers chat at other table", None, "Press E to eat quietly"),
            GameObjective("try_joining", "Attempt Connection", "Try to join conversation about weekend plans", None, "Press E to speak up"),
            GameObjective("ignored_completely", "Invisible", "They continue talking as if you didn't speak", None, "Press E to shrink back"),
            GameObjective("friday_drinks", "Overhear Plans", "'We're all going to happy hour after work!'", None, "Press E to listen"),
            GameObjective("not_invited", "Not Included", "Everyone invited except you", None, "Press E to pretend not to care"),
            GameObjective("ask_why", "Brave Question", "'Can I come too?' 'Oh... it's kind of a regular group thing'", None, "Press E to understand"),
            GameObjective("eat_in_car", "New Routine", "Start eating lunch in your car to avoid rejection", None, "Press E to hide"),
            
            # Month 2 - Digital Disconnection
            GameObjective("social_media_scroll", "Instagram Pain", "See high school friends graduating college, traveling", None, "Press E to scroll"),
            GameObjective("happy_posts", "Perfect Lives", "Everyone posting happy relationships, new jobs, vacations", None, "Press E to compare"),
            GameObjective("no_posts", "Nothing to Share", "Your life: work, home, sleep, repeat. Nothing photo-worthy", None, "Press E to realize"),
            GameObjective("birthday_forgotten", "Birthday Alone", "Your birthday: 3 Facebook posts from acquaintances", None, "Press E to read"),
            GameObjective("delete_facebook", "Delete Apps", "Delete social media to stop the pain of comparison", None, "Press E to delete"),
            GameObjective("more_isolated", "Worse Isolation", "Now even more cut off from distant connections", None, "Press E to regret"),
            
            # Month 3 - Neighbor Tensions
            GameObjective("thin_walls", "Noise Complaint", "Neighbor bangs on wall: 'Turn your TV down!'", None, "Press E to lower volume"),
            GameObjective("tv_company", "Only Voices", "TV is only human voices you hear at home", None, "Press E to mute"),
            GameObjective("walking_loud", "More Complaints", "'You walk too loud!' Can't exist without bothering others", None, "Press E to tiptoe"),
            GameObjective("afraid_to_live", "Walking on Eggshells", "Afraid to cook, clean, or move in own home", None, "Press E to sit still"),
            GameObjective("complete_silence", "Silent Home", "Apartment becomes silent tomb", None, "Press E to listen to nothing"),
            
            # Month 4 - Seeking Connection
            GameObjective("support_group_search", "Find Help", "Google 'support groups for isolated adults'", None, "Press E to search"),
            GameObjective("depression_group", "Find Meeting", "Depression support group meets Wednesdays 7PM", None, "Press E to get details"),
            GameObjective("bus_routes", "Transportation", "Group meets across town, 2 buses, 90 minutes each way", None, "Press E to map"),
            GameObjective("first_meeting", "Brave Attempt", "Make journey to first meeting", None, "Press E to go"),
            GameObjective("arrive_late", "Bad Start", "Arrive 30 minutes late, everyone stares", None, "Press E to sit"),
            GameObjective("cant_speak", "Frozen", "When asked to share, throat closes up, can't speak", None, "Press E to shake head"),
            GameObjective("flee_meeting", "Escape", "Flee at break, too anxious to return", None, "Press E to leave"),
            
            # Month 5 - Online Attempts
            GameObjective("online_forums", "Internet Community", "Join online depression and anxiety forums", None, "Press E to register"),
            GameObjective("pour_heart_out", "Share Story", "Write long post about your struggles", None, "Press E to type"),
            GameObjective("no_responses", "Ignored Online Too", "12 views, 0 responses to your cry for help", None, "Press E to refresh"),
            GameObjective("internet_bill", "Final Notice", "Internet shut off for non-payment", None, "Press E to read"),
            GameObjective("last_connection", "Cut Off", "Lose last connection to outside world", None, "Press E to accept"),
            GameObjective("library_internet", "Public Access", "Use library internet but too public to access support sites", None, "Press E to close tabs"),
            
            # Month 6 - Breaking Point
            GameObjective("talk_to_self", "Only Companion", "Start having full conversations with yourself", None, "Press E to chat"),
            GameObjective("public_spaces", "Seek Humans", "Go to mall just to be around other people", None, "Press E to walk"),
            GameObjective("security_suspicious", "Loitering", "'You need to buy something or leave'", None, "Press E to leave"),
            GameObjective("park_bench", "Public Seating", "Sit in park pretending to read, just watching people", None, "Press E to observe"),
            GameObjective("someone_talks", "Human Contact!", "Elderly man asks for the time", None, "Press E to eagerly respond"),
            GameObjective("overshare", "Desperate", "Word-vomit your life story to confused stranger", None, "Press E to overshare"),
            GameObjective("backs_away", "Too Much", "He backs away slowly, you see fear in his eyes", None, "Press E to apologize"),
            
            # Crisis Point
            GameObjective("dark_thoughts", "Dangerous Mind", "'Would anyone even notice if I disappeared?'", None, "Press E to spiral"),
            GameObjective("making_plans", "Scary Planning", "Start making concrete plans to 'stop the pain'", None, "Press E to plan"),
            GameObjective("moment_clarity", "Snap Back", "See pill bottle and realize how close you are to edge", None, "Press E to put down"),
            GameObjective("crisis_hotline", "Last Resort", "Google suicide hotline on library computer", None, "Press E to search"),
            GameObjective("find_phone", "No Phone", "Need phone to call crisis line but have no service", None, "Press E to panic"),
            GameObjective("borrow_phone", "Ask Stranger", "Approach stranger: 'Emergency, can I use your phone?'", None, "Press E to ask"),
            GameObjective("make_call", "Lifeline", "Call crisis line from stranger's phone in parking lot", None, "Press E to dial"),
            
            # Brief Hope
            GameObjective("counselor_voice", "Human Warmth", "'I'm here. You matter. Let's talk'", None, "Press E to cry"),
            GameObjective("thirty_minutes", "Not Alone", "Talk for 30 minutes to first person who's listened in months", None, "Press E to talk"),
            GameObjective("resources_given", "Some Hope", "Get list of free counseling services", None, "Press E to write down"),
            GameObjective("long_waitlists", "More Waiting", "Every service has 2-6 month wait list", None, "Press E to add name"),
            GameObjective("still_alone", "Return Home", "Go back to empty, silent apartment", None, "Press E to enter"),
            GameObjective("but_alive", "Still Here", "You're still here. That's something", None, "Press E to exist"),
            GameObjective("chapter_7_end", "Isolation Kills", "Loneliness is as deadly as any disease", None, "Press E to complete"),
        ]
    
    def setup_part8_objectives(self):
        """Part 8 - Legal System Entanglements"""
        self.objectives = [
            # Day 1 - The Poverty Crime
            GameObjective("morning_routine", "5:30 AM Monday", "Wake up for 7AM shift across town", None, "Press E to get ready"),
            GameObjective("check_wallet", "Count Money", "$1.73 in wallet, bus fare is $2.50", None, "Press E to search pockets"),
            GameObjective("no_more_money", "Nothing Left", "Already borrowed from everyone, sold everything", None, "Press E to think"),
            GameObjective("walk_or_jump", "Impossible Choice", "Walk 3 hours and be fired, or jump turnstile?", None, "Press E to decide"),
            GameObjective("approach_turnstile", "Train Station", "Stand at turnstile watching people tap cards", None, "Press E to wait"),
            GameObjective("look_around", "Check for Cops", "Look around nervously for transit police", None, "Press E to scan"),
            GameObjective("jump_quick", "Make Decision", "Jump turnstile quickly, heart pounding", None, "Press E to jump"),
            GameObjective("almost_clear", "Almost Safe", "Walk quickly toward platform", None, "Press E to walk"),
            GameObjective("officer_shouts", "'STOP!'", "'Transit police! Stop right there!'", None, "Press E to freeze"),
            
            # The Arrest
            GameObjective("explain_situation", "Plead Case", "'Officer, I just need to get to work, I have $1.73...'", None, "Press E to explain"),
            GameObjective("no_sympathy", "Zero Tolerance", "'Theft of service is a crime. Hands behind your back'", None, "Press E to comply"),
            GameObjective("handcuffed_subway", "Public Shame", "Handcuffed in front of morning commuters", None, "Press E to look down"),
            GameObjective("citation_written", "Criminal Citation", "Theft of services, Fine: $250, Court date in 30 days", None, "Press E to receive"),
            GameObjective("late_to_work", "90 Minutes Late", "Process takes 90 minutes, now very late to work", None, "Press E to panic"),
            GameObjective("final_warning_job", "Last Strike", "Boss: 'This is your final warning'", None, "Press E to apologize"),
            
            # Week 2 - Court Date Conflict
            GameObjective("read_court_date", "Check Calendar", "Court date: Tuesday 9AM, you work every Tuesday", None, "Press E to worry"),
            GameObjective("request_day_off", "Ask Boss", "Request Tuesday off for court", None, "Press E to ask"),
            GameObjective("denied_time_off", "Request Denied", "'We're short staffed, find someone to cover or don't come back'", None, "Press E to plead"),
            GameObjective("no_one_covers", "No Help", "Ask 6 coworkers, all say no or can't", None, "Press E to give up"),
            GameObjective("skip_court", "Impossible Choice #2", "Skip court and keep job, or go and lose job?", None, "Press E to choose job"),
            
            # Month 2 - Warrant Issued
            GameObjective("mail_notice", "Failure to Appear", "Notice: Bench warrant issued for failure to appear", None, "Press E to read"),
            GameObjective("panic_mode", "Living in Fear", "Now have active warrant, panic at every siren", None, "Press E to worry"),
            GameObjective("avoid_police", "Route Changes", "Take longer routes to avoid police presence", None, "Press E to walk carefully"),
            GameObjective("cant_sleep", "Anxiety Insomnia", "Can't sleep, worried about arrest at any moment", None, "Press E to toss and turn"),
            
            # Month 3 - Traffic Stop
            GameObjective("friend_car", "Catching Ride", "Friend gives ride home from work at night", None, "Press E to get in"),
            GameObjective("tail_light", "Minor Violation", "Cop pulls you over for broken tail light", None, "Press E to pull over"),
            GameObjective("passenger_id", "ID Request", "'I need IDs from everyone in the vehicle'", None, "Press E to hand over"),
            GameObjective("warrant_found", "System Check", "Officer returns: 'Step out, you have a warrant'", None, "Press E to comply"),
            GameObjective("arrested_roadside", "Handcuffed Again", "Arrested on roadside for $2.50 fare from months ago", None, "Press E to be arrested"),
            
            # Jail Experience
            GameObjective("booking_process", "Booked In", "Fingerprinted, photographed, belongings taken", None, "Press E to process"),
            GameObjective("phone_call", "One Call", "One phone call - but who will help?", None, "Press E to think"),
            GameObjective("no_bail_money", "Bail Set", "Bail: $500, might as well be $5 million", None, "Press E to return to cell"),
            GameObjective("overnight_hold", "Cold Night", "Sleep on metal bench with 20 others", None, "Press E to shiver"),
            GameObjective("miss_work_call", "Can't Call Job", "No way to tell job you won't be there", None, "Press E to worry"),
            GameObjective("court_transport", "Morning Transport", "Chained to others, bus to courthouse", None, "Press E to shuffle"),
            
            # Court Appearance
            GameObjective("meet_defender", "Public Defender", "Meet lawyer 5 minutes before hearing", None, "Press E to meet"),
            GameObjective("rushed_meeting", "Speed Consultation", "'Take the plea, pay fine, get probation, or risk trial and jail'", None, "Press E to listen"),
            GameObjective("no_real_choice", "Coerced Plea", "Can't afford trial, can't risk more jail", None, "Press E to accept plea"),
            GameObjective("guilty_plea", "Criminal Record", "Plead guilty to theft, now have criminal record", None, "Press E to say guilty"),
            GameObjective("probation_terms", "12 Months", "12 months probation, $100/month fees, 40 hours community service", None, "Press E to agree"),
            
            # Release and Job Loss
            GameObjective("released_afternoon", "Released", "Released at 3PM, 32 hours after arrest", None, "Press E to exit"),
            GameObjective("phone_dead", "No Communication", "Phone dead, no way to check messages", None, "Press E to walk home"),
            GameObjective("work_voicemail", "17 Missed Calls", "Boss: 'Don't bother coming back, you're done'", None, "Press E to listen"),
            GameObjective("no_explanation", "No Chance", "Try calling back - 'Decision is final'", None, "Press E to hang up"),
            
            # Probation Trap
            GameObjective("first_meeting_po", "Report to PO", "Must report to probation officer monthly", None, "Press E to report"),
            GameObjective("probation_rules", "The Rules", "No missing meetings, pay all fees, pass drug tests", None, "Press E to understand"),
            GameObjective("job_search_requirement", "Must Work", "Required to maintain employment or violate probation", None, "Press E to worry"),
            GameObjective("application_question", "The Box", "Every application: 'Have you been convicted of a crime?'", None, "Press E to check yes"),
            GameObjective("auto_rejections", "No Callbacks", "50 applications, 50 rejections or silence", None, "Press E to keep trying"),
            
            # Violation Spiral
            GameObjective("cant_pay_fees", "No Money", "Can't pay probation fees without job", None, "Press E to stress"),
            GameObjective("first_violation", "Warning", "PO: 'This is a violation, one more and back to jail'", None, "Press E to promise"),
            GameObjective("community_service", "Free Labor", "40 hours picking up trash on highways", None, "Press E to work"),
            GameObjective("miss_service", "Transportation Issue", "Miss community service - no bus fare again", None, "Press E to violate"),
            GameObjective("violation_warrant", "New Warrant", "Probation violation warrant issued", None, "Press E to run"),
            
            # The Cycle Completes
            GameObjective("arrested_again", "Arrested Again", "Arrested at shelter for probation violation", None, "Press E to submit"),
            GameObjective("thirty_days", "Jail Sentence", "30 days in jail for technical violation", None, "Press E to serve time"),
            GameObjective("released_homeless", "Released to Streets", "Released with nowhere to go, no job, no hope", None, "Press E to walk out"),
            GameObjective("permanent_record", "Forever Marked", "Criminal record follows you forever", None, "Press E to understand"),
            
            # System Analysis
            GameObjective("poverty_crime", "Crime of Poverty", "Your crime: being too poor for bus fare", None, "Press E to reflect"),
            GameObjective("total_cost", "True Cost", "$2.50 fare became: arrest, job loss, homelessness, record", None, "Press E to calculate"),
            GameObjective("system_design", "By Design", "System designed to trap poor people permanently", None, "Press E to see clearly"),
            GameObjective("modern_slavery", "Legal Slavery", "Probation = controlled labor and revenue extraction", None, "Press E to comprehend"),
            GameObjective("no_rehabilitation", "No Help", "No rehabilitation, just punishment and profit", None, "Press E to accept"),
            GameObjective("chapter_8_end", "Justice Denied", "In America, poverty itself is criminalized", None, "Press E to complete"),
        ]


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

        # Load sprites
        self.load_animations()

    def load_animations(self):
        """Load character animations from ModernInteriors premade character spritesheet"""
        # Path to the premade character spritesheet (16x16 version)
        sprite_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
            '0_Premade_Characters', '16x16', 'Premade_Character_01.png'
        )

        try:
            # Load the entire spritesheet
            spritesheet = pygame.image.load(sprite_path)
            print(f"Loaded ModernInteriors character spritesheet (896x656, 56x41 sprites)")

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
            # Change these column numbers based on the actual spritesheet:
            idle_config = {
                'idle_down': (2, 0),   # Column 0, Row 0
                'idle_left': (3, 0),   # Column 1, Row 0
                'idle_right': (0, 0),  # Column 2, Row 0
                'idle_up': (4, 0),     # Column 3, Row 0
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
                    (6, 2), (7, 2), (8, 2),   # Row 1: frames 1-3
                    (9, 2), (10, 2), (11, 2)    # Row 2: frames 4-6
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
                self.animation_timer -= self.animation_speed
                current_anim = self.animations[self.current_animation]
                if len(current_anim) > 0:
                    self.animation_frame = (self.animation_frame + 1) % len(current_anim)

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