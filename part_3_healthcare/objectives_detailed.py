"""Part 3: Healthcare Maze - Sick Without Coverage"""

from src.core.game_world import GameObjective

def get_part3_objectives():
    """Healthcare access barriers for youth aging out"""
    return [
        # === LOSING COVERAGE ===
        GameObjective(
            "medicaid_notice",
            "Coverage Ending",
            "Letter: 'Your Medicaid ends in 30 days. You must reapply.'",
            None,
            "Press E to read"
        ),
        
        GameObjective(
            "reapply_confusion",
            "42-Page Application",
            "Income verification? Tax returns? You work under the table...",
            None,
            "Press E to attempt"
        ),
        
        GameObjective(
            "documents_needed",
            "Missing Documents",
            "Need: Birth certificate ($25), State ID ($30), Proof of address (homeless)",
            None,
            "Press E to give up"
        ),
        
        # === MENTAL HEALTH CRISIS ===
        GameObjective(
            "anxiety_worsening",
            "Can't Breathe",
            "Panic attacks daily. Were managing with meds. Prescription expired.",
            None,
            "Press E to cope"
        ),
        
        GameObjective(
            "medication_cost",
            "Pharmacy Price",
            "'Without insurance? $247 for 30 days.' You have $31.",
            None,
            "Press E to leave empty"
        ),
        
        GameObjective(
            "emergency_room",
            "ER at 3 AM",
            "Can't stop shaking. Heart racing. They have to treat you... right?",
            None,
            "Press E to wait"
        ),
        
        GameObjective(
            "er_discharge",
            "Discharged at 7 AM",
            "'Anxiety attack. Follow up with psychiatrist.' What psychiatrist?",
            None,
            "Press E to leave"
        ),
        
        GameObjective(
            "er_bill",
            "ER Bill Arrives",
            "$3,847 for 4 hours. 'Payment plan available.' You're homeless.",
            None,
            "Press E to laugh"
        ),
        
        # === PHYSICAL HEALTH DECLINING ===
        GameObjective(
            "tooth_pain",
            "Infected Tooth",
            "Week 3 of pain. Face swollen. Can't afford dentist.",
            None,
            "Press E to endure"
        ),
        
        GameObjective(
            "urgent_care",
            "Urgent Care Visit",
            "'$150 upfront.' You leave. Infection spreading to jaw.",
            None,
            "Press E to suffer"
        ),
        
        GameObjective(
            "free_clinic_search",
            "Finding Free Clinic",
            "Calling clinics: 'Income proof?' 'Address?' 'Insurance?' No, no, no.",
            None,
            "Press E to keep calling"
        ),
        
        GameObjective(
            "clinic_found",
            "Sliding Scale Clinic",
            "Found one! Next appointment... in 6 weeks. Antibiotics NOW.",
            None,
            "Press E to wait"
        ),
        
        # === MEDICATION STRUGGLES ===
        GameObjective(
            "rationing_meds",
            "Making Meds Last",
            "5 pills left. Taking half doses. Brain fog getting worse.",
            None,
            "Press E to split pills"
        ),
        
        GameObjective(
            "withdrawal_symptoms",
            "Out of Medication",
            "Day 3 no meds. Dizzy. Nauseous. 'Brain zaps.' Can't work.",
            None,
            "Press E to push through"
        ),
        
        GameObjective(
            "fired_for_absence",
            "Lost Job",
            "'Too many sick days.' How do you explain untreated mental illness?",
            None,
            "Press E to pack locker"
        ),
        
        # === SELF MEDICATION ===
        GameObjective(
            "street_solutions",
            "Dangerous Choices",
            "Someone offers anxiety meds. No prescription. $5 each. But...",
            None,
            "Press E to decide"
        ),
        
        GameObjective(
            "alcohol_coping",
            "Liquid Courage",
            "Alcohol stops the shaking. Temporarily. Making everything worse.",
            None,
            "Press E to numb"
        ),
        
        # === PREGNANCY SCARE ===
        GameObjective(
            "pregnancy_fear",
            "Late Period",
            "2 weeks late. Stressed? Pregnant? Test costs $15 you don't have.",
            None,
            "Press E to worry"
        ),
        
        GameObjective(
            "planned_parenthood",
            "Clinic Appointment",
            "Planned Parenthood. Protesters outside. You just need help.",
            None,
            "Press E to enter"
        ),
        
        GameObjective(
            "birth_control",
            "Prevention Access",
            "'Free with insurance.' You aged out. Now it's $50/month.",
            None,
            "Press E to calculate"
        ),
        
        # === CHRONIC CONDITIONS ===
        GameObjective(
            "asthma_attack",
            "Can't Breathe",
            "Inhaler empty. Refill needs doctor visit. No doctor.",
            None,
            "Press E to wheeze"
        ),
        
        GameObjective(
            "diabetes_supplies",
            "Insulin Rationing",
            "3 days of insulin left. $340 for refill. Choosing: food or medicine?",
            None,
            "Press E to ration"
        ),
        
        # === THERAPY NEEDS ===
        GameObjective(
            "trauma_therapy",
            "Need to Talk",
            "'Process your trauma.' Where? With what money? While homeless?",
            None,
            "Press E to stuff down"
        ),
        
        GameObjective(
            "crisis_hotline",
            "Calling for Help",
            "'We can't prescribe medication.' You need more than talk.",
            None,
            "Press E to hang up"
        ),
        
        GameObjective(
            "group_therapy",
            "Free Support Group",
            "Tuesdays 2 PM. You work Tuesdays. Always during work hours.",
            None,
            "Press E to miss out"
        ),
        
        # === WORKPLACE ISSUES ===
        GameObjective(
            "hiding_symptoms",
            "Pretending Normal",
            "Smile. Don't shake. Don't cry. They can't know you're sick.",
            None,
            "Press E to fake it"
        ),
        
        GameObjective(
            "bathroom_breakdown",
            "Panic at Work",
            "Hiding in bathroom stall. Manager knocking. 'Break's over!'",
            None,
            "Press E to compose"
        ),
        
        # === CASCADING EFFECTS ===
        GameObjective(
            "cant_focus",
            "School Suffering",
            "Failed 2 classes. Can't concentrate. Depression isn't an 'excuse.'",
            None,
            "Press E to drop out"
        ),
        
        GameObjective(
            "relationship_strain",
            "Pushing People Away",
            "'You're different lately.' Can't explain your brain is broken.",
            None,
            "Press E to isolate"
        ),
        
        # === EMERGENCY AGAIN ===
        GameObjective(
            "suicide_ideation",
            "Dark Thoughts",
            "What's the point? Every system failed. Nobody cares if you die.",
            None,
            "Press E to..."
        ),
        
        GameObjective(
            "involuntary_hold",
            "72-Hour Hold",
            "Said the wrong thing at ER. Now locked up 'for your safety.'",
            None,
            "Press E to wait"
        ),
        
        GameObjective(
            "discharge_nowhere",
            "Released to Streets",
            "'Stable for discharge.' To where? With what support?",
            None,
            "Press E to leave"
        ),
        
        # === FIGHTING THE SYSTEM ===
        GameObjective(
            "advocacy_attempt",
            "Demanding Care",
            "'I NEED HELP!' They hand you pamphlets. Useless pamphlets.",
            None,
            "Press E to scream"
        ),
        
        GameObjective(
            "social_worker",
            "Case Worker Maybe?",
            "Found someone who listens. Gets you emergency Medicaid. Finally.",
            None,
            "Press E to cry relief"
        ),
        
        # === REFLECTION ===
        GameObjective(
            "medication_stable",
            "First Month Stable",
            "Proper meds. Clear thoughts. You could've died waiting.",
            None,
            "Press E to breathe"
        ),
        
        GameObjective(
            "others_suffering",
            "Looking Around",
            "ER waiting room full. How many won't make it?",
            None,
            "Press E to witness"
        ),
        
        GameObjective(
            "part3_complete",
            "Healthcare Maze Survived",
            "Healthcare is a human right. Profit over people kills.",
            None,
            "Press SPACE to continue"
        )
    ]