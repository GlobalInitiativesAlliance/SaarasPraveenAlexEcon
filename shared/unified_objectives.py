"""Unified Objectives System - Maps objectives to reusable interiors and tasks"""

from src.core.game_world import GameObjective
from typing import Dict, List

class UnifiedObjectiveSystem:
    """Maps objectives to interiors and tasks across all parts"""
    
    def __init__(self):
        # Map building types to specific interior classes
        self.interior_mappings = {
            'office': 'MultiPurposeOffice',
            'home': 'MultiPurposeHome', 
            'store': 'MultiPurposeStore',
            'restaurant': 'MultiPurposeWorkplace',
            'medical': 'MultiPurposeMedical'
        }
        
    def get_part1_objectives_unified(self):
        """Part 1 objectives using unified interior system"""
        return [
            GameObjective(
                "day_1_morning",
                "Day 1: Pack Your Life", 
                "You have 2 hours to pack. Foster parents are waiting.",
                'home',  # Any home interior
                "Press E to start packing",
                task_id="pack_belongings"
            ),
            
            GameObjective(
                "day_1_evening",
                "Find Tonight's Shelter",
                "It's 6 PM. Where will you sleep?",
                'home',  # Friend's house
                "Press E to ask Sarah",
                task_id="couch_surf_request"
            ),
            
            GameObjective(
                "day_2_morning",
                "Shower Crisis",
                "Haven't showered in 3 days. Find somewhere.",
                'store',  # Store becomes gym
                "Press E for day pass ($15)",
                task_id="shower_at_gym"
            ),
            
            GameObjective(
                "day_3_housing",
                "Housing Office Visit",
                "Apply for transitional housing program",
                'office',  # Office becomes housing office
                "Press E to enter office",
                task_id="apply_for_housing"
            ),
            
            GameObjective(
                "day_5_work",
                "Work Your Shift",
                "Can't miss work or you'll be fired",
                'restaurant',
                "Press E to clock in",
                task_id="work_shift"
            ),
            
            GameObjective(
                "day_7_conflict",
                "Court vs Work",
                "Court hearing at 9 AM. Scheduled to work.",
                'office',  # Office becomes courtroom
                "Choose: Court or Work",
                task_id="court_appearance"
            ),
            
            GameObjective(
                "day_10_shelter",
                "Emergency Shelter",
                "Kicked out of friend's place. Find shelter.",
                'office',  # Office becomes shelter at night
                "Press E to check in",
                task_id="sleep_shelter"
            ),
            
            GameObjective(
                "day_15_food",
                "Food Bank Wednesday", 
                "No money for food. Wait in line.",
                'office',  # Office becomes food bank
                "Press E to get in line",
                task_id="food_bank"
            )
        ]
        
    def get_part3_objectives_unified(self):
        """Part 3 healthcare objectives using unified interiors"""
        return [
            GameObjective(
                "medicaid_loss",
                "Coverage Ending",
                "Your Medicaid ends in 30 days. Must reapply.",
                'office',  # Benefits office
                "Press E to get forms",
                task_id="medicaid_application"
            ),
            
            GameObjective(
                "anxiety_crisis",
                "Panic Attack",
                "Can't breathe. Need help NOW.",
                'medical',  # Hospital ER
                "Press E for emergency care",
                task_id="er_visit"
            ),
            
            GameObjective(
                "prescription_needed",
                "Out of Medication",
                "Anxiety meds ran out. Need refill.",
                'store',  # Store becomes pharmacy
                "Press E at pharmacy counter",
                task_id="pharmacy_meds"
            ),
            
            GameObjective(
                "free_clinic_search",
                "Find Free Clinic",
                "Can't afford doctor. Search for free care.",
                'medical',  # Medical becomes free clinic
                "Press E to wait (3+ hours)",
                task_id="free_clinic_wait"
            )
        ]
        
    def get_part5_objectives_unified(self):
        """Part 5 education objectives"""
        return [
            GameObjective(
                "ged_enrollment",
                "GED Classes",
                "Need diploma for better jobs",
                'office',  # Office becomes education center
                "Press E to enroll",
                task_id="ged_enrollment"
            ),
            
            GameObjective(
                "morning_class",
                "Attend Class",
                "GED class 9 AM. Work starts at 10 AM.",
                'office',
                "Press E to attend class",
                task_id="ged_class"
            ),
            
            GameObjective(
                "fafsa_confusion",
                "Financial Aid Forms",
                "FAFSA requires parents' tax info. You have none.",
                'office',
                "Press E for help",
                task_id="fafsa_help"
            ),
            
            GameObjective(
                "computer_access",
                "Online Application", 
                "Need computer for college app. Don't have one.",
                'office',  # Library computer lab
                "Press E to use computer",
                task_id="use_computer"
            )
        ]
        
    def get_part7_objectives_unified(self):
        """Part 7 legal system objectives"""
        return [
            GameObjective(
                "fare_evasion",
                "Transit Ticket",
                "Caught without $2.50 fare. Court summons.",
                'office',  # Becomes courtroom
                "Press E to appear",
                task_id="court_appearance"
            ),
            
            GameObjective(
                "public_defender",
                "Meet Your Lawyer",
                "5 minutes with overworked defender",
                'office',  # Legal aid office
                "Press E to meet",
                task_id="public_defender"
            ),
            
            GameObjective(
                "bench_warrant",
                "Missed Court Date",
                "Worked instead of court. Now there's a warrant.",
                'office',
                "Press E to turn yourself in",
                task_id="warrant_resolution"
            )
        ]

def create_objective_with_interior(obj_id: str, title: str, description: str, 
                                 interior_type: str, task_id: str,
                                 interaction_text: str = "Press E") -> GameObjective:
    """Helper to create objectives with proper interior mappings"""
    
    # Map interior types to actual building types on map
    building_mappings = {
        'office': ['bank', 'office'],
        'home': ['house', 'apartment'],
        'store': ['store', 'grocery'],
        'restaurant': ['burger', 'pizza'],
        'medical': ['hospital', 'office']  # Some offices serve as clinics
    }
    
    objective = GameObjective(
        obj_id,
        title,
        description,
        None,  # Position set by objective manager
        interaction_text
    )
    
    # Store metadata for interior selection
    objective.interior_type = interior_type
    objective.building_types = building_mappings.get(interior_type, ['building'])
    objective.task_id = task_id
    
    return objective