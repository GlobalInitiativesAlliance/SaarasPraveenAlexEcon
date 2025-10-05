"""Part 1 Employment Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part1_objectives():
    """Return all Part 1 objectives - Employment Rights storyline"""
    print("*** LOADING OBJECTIVES FROM NEW ORGANIZED FOLDER: part_1_employment/objectives.py ***")
    return [
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