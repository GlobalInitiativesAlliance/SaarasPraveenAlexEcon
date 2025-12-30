"""
Building Manager - Handles building detection and interior loading
"""
import json
import os
import time
import threading
import pygame
from shared.constants import TILE_SIZE
from src.core.debug_logger import debug_logger, dprint

def timeout_operation(timeout_seconds):
    """Decorator to add timeout protection to operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)

            if thread.is_alive():
                debug_logger.log_timeout(f"{func.__name__}", timeout_seconds)
                return None
            elif exception[0]:
                raise exception[0]
            else:
                return result[0]
        return wrapper
    return decorator

class BuildingManager:
    def __init__(self, game):
        self.game = game
        self.building_interiors = {}
        self.cached_interiors = {}  # Cache for interior instances
        self.building_positions_cache = {}  # Spatial cache: (tile_x, tile_y) -> (building_pos, building_name, room_name)
        self._room_data_cache = {}  # PERFORMANCE: Cache loaded JSON room data
        self.load_building_interiors()

    def load_building_interiors(self):
        """Load building-interior mappings from file"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        mappings_file = os.path.join(base_dir, "data", "maps", "building_interiors.json")

        if os.path.exists(mappings_file):
            try:
                with open(mappings_file, 'r') as f:
                    self.building_interiors = json.load(f)
                print(f"Loaded {len(self.building_interiors)} building-interior mappings")
                self._build_position_cache()
            except Exception as e:
                print(f"Error loading building interiors: {e}")
                self.building_interiors = {}
        else:
            print("No building-interior mappings found")
            self.building_interiors = {}

    def _build_position_cache(self):
        """Pre-cache all building positions for O(1) lookup.

        This is called once at startup. Instead of searching every frame,
        we cache which buildings have interiors and their positions.
        """
        self.building_positions_cache = {}

        # Cache all buildings that have interior mappings
        for pos_key, room_name in self.building_interiors.items():
            try:
                x, y = map(int, pos_key.split(','))
                # Store in cache for fast lookup
                self.building_positions_cache[(x, y)] = {
                    'pos': (x, y),
                    'room_name': room_name
                }
            except (ValueError, AttributeError):
                continue

        dprint(f"[PERF] Cached {len(self.building_positions_cache)} building positions")

    def get_building_at_position(self, world_x, world_y):
        """Check if there's a building at the given world position"""
        # Convert world coordinates to tile coordinates
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        # Check if position is within map bounds
        if 0 <= tile_x < self.game.city_map.width and 0 <= tile_y < self.game.city_map.height:
            # Get the tile data at this position
            tile_data = self.game.city_map.map_data[tile_y][tile_x]


            # Handle both tuple and dict formats
            if tile_data:
                building_name = None
                offset_x = 0
                offset_y = 0

                if isinstance(tile_data, dict):
                    # New dictionary format
                    tile_type = tile_data.get('type', '')
                    if tile_type in ['building', 'building_with_bg', 'building_part_with_bg']:
                        building_name = tile_data.get('building_name', '')
                        offset_x = tile_data.get('offset_x', 0)
                        offset_y = tile_data.get('offset_y', 0)

                elif isinstance(tile_data, tuple):
                    # Old tuple format
                    if tile_data[0] in ['building', 'building_with_bg']:
                        if tile_data[0] == 'building_with_bg':
                            _, building_name, offset_x, offset_y, _ = tile_data
                        else:
                            _, building_name, offset_x, offset_y = tile_data

                if building_name:
                    # Filter out non-building objects like trees
                    building_name_lower = building_name.lower()
                    non_buildings = ['tree', 'bush', 'flower', 'plant', 'grass', 'rock', 'stone']
                    if any(nb in building_name_lower for nb in non_buildings):
                        return None, None

                    # Calculate base position
                    base_x = tile_x - offset_x
                    base_y = tile_y - offset_y

                    return (base_x, base_y), building_name

        return None, None

    def check_player_near_building(self, player_x, player_y, range_tiles=2):
        """Check if player is near any building with an assigned interior.

        OPTIMIZED: Uses pre-cached building positions instead of O(n²) search.
        Only iterates through buildings that actually have interiors assigned.
        """
        player_tile_x = int(player_x)
        player_tile_y = int(player_y)

        # Fast path: Check cached building positions (much smaller list than all tiles)
        for (bx, by), building_data in self.building_positions_cache.items():
            # Simple distance check instead of nested loop search
            if abs(player_tile_x - bx) <= range_tiles and abs(player_tile_y - by) <= range_tiles:
                # Found a nearby building with an interior
                room_name = building_data['room_name']
                building_pos = building_data['pos']

                # Get building name from map data (only when needed)
                _, building_name = self.get_building_at_position(
                    bx * TILE_SIZE, by * TILE_SIZE
                )

                return building_pos, building_name or f"Building_{bx}_{by}", room_name

        return None, None, None

    def load_interior_room(self, room_name, building_pos):
        """Load an interior room with scene-specific awareness"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Get the appropriate room data file
        room_data = self.get_room_data_for_interior(room_name, base_dir)
        if not room_data:
            return None

        # Create scene-specific interior instance
        try:
            interior = self.create_scene_specific_interior(room_name, room_data, building_pos)
            return interior
        except Exception as e:
            print(f"Error loading interior room {room_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_room_data_for_interior(self, room_name, base_dir):
        """Get appropriate room data file for interior type"""
        # Check for objective-specific room overrides first
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id == "mike_floor" and room_name == "crappy_apartment":
            # Load mike.json for mike_floor objective instead of bad_studio.json
            json_file = "mike.json"
        else:
            # Scene-specific interiors use base room layouts
            room_data_map = {
                'foster_home_aging_out': 'foster_home.json',
                'tlp_housing_early_stage': 'foster_home.json',
                'tlp_housing_late_stage': 'foster_home.json',
                'tlp_housing_final': 'foster_home.json',
                'studio_apartment_part1': 'bad_studio.json',
                'studio_apartment_part2': 'bad_studio.json',
                'studio_apartment': 'bad_studio.json',  # Fallback
                'legal_aid': 'housing_office.json',  # Reuse housing office layout
                'community_center': 'community_center.json',
                'classroom': 'classroom.json',
                'crappy_apartment': 'bad_studio.json',  # Reuse bad studio layout
                'tlp_housing_dynamic': 'foster_home.json',  # Uses foster home layout
                'housing_office': 'rental.json'  # Use furnished rental layout for housing office
            }
            # Get the JSON file to load
            json_file = room_data_map.get(room_name, f"{room_name}.json")

        room_file = os.path.join(base_dir, "data", "interiors", "rooms", json_file)

        # PERFORMANCE: Check cache first
        if json_file in self._room_data_cache:
            return self._room_data_cache[json_file]

        if os.path.exists(room_file):
            try:
                with open(room_file, 'r') as f:
                    room_data = json.load(f)
                    # Cache for future use
                    self._room_data_cache[json_file] = room_data
                    return room_data
            except Exception as e:
                print(f"Error loading room data from {room_file}: {e}")
        else:
            print(f"Room data file not found: {room_file}")

        return None

    def create_scene_specific_interior(self, room_name, room_data, building_pos):
        """Create scene-specific interior instance"""

        # Scene-specific interior classes
        if room_name == "foster_home_aging_out":
            from src.interiors.narratives.foster_home_aging_out import FosterHomeAgingOut
            return FosterHomeAgingOut(self.game, room_data, building_pos)

        elif room_name == "tlp_housing_early_stage":
            from src.interiors.narratives.tlp_housing_early_stage import TLPHousingEarlyStage
            return TLPHousingEarlyStage(self.game, room_data, building_pos)

        elif room_name == "tlp_housing_late_stage":
            from src.interiors.narratives.tlp_housing_late_stage import TLPHousingLateStage
            return TLPHousingLateStage(self.game, room_data, building_pos)

        elif room_name == "tlp_housing_final":
            from src.interiors.narratives.tlp_housing_final_narrative import TLPHousingFinalNarrative
            return TLPHousingFinalNarrative(self.game, room_data, building_pos)

        elif room_name == "studio_apartment_part1":
            from src.interiors.narratives.studio_apartment_part1 import StudioApartmentPart1
            return StudioApartmentPart1(self.game, room_data, building_pos)

        elif room_name == "studio_apartment_part2":
            from src.interiors.narratives.studio_apartment_narrative import StudioApartmentNarrative
            return StudioApartmentNarrative(self.game, room_data, building_pos)

        elif room_name == "community_center":
            from src.interiors.narratives.community_center_narrative import CommunityCenterNarrative
            return CommunityCenterNarrative(self.game, room_data, building_pos)

        elif room_name == "classroom":
            # Check if this should be Part 3 school
            if self.game.objective_manager.game_part == 3:
                current_obj = self.game.objective_manager.get_current_objective()
                if current_obj and current_obj.id in ['walk_to_school', 'class_distraction']:
                    from part_3_legal_system.interiors.school_part3 import SchoolPart3
                    return SchoolPart3(self.game, room_data, building_pos)
            from src.interiors.narratives.classroom_narrative import ClassroomNarrative
            return ClassroomNarrative(self.game, room_data, building_pos)

        elif room_name == "crappy_apartment":
            # Check if this should be Part 4 TLP apartment (Healthcare)
            if self.game.objective_manager.game_part == 4:
                current_obj = self.game.objective_manager.get_current_objective()
                part4_apartment_objectives = [
                    'morning_mail', 'sort_mail', 'medicaid_notice',
                    'therapy_reminder', 'therapy_decision', 'missed_appointment',
                    'caseworker_call', 'navigator_quiz', 'coverage_active',
                    'healthcare_reflection'
                ]
                if current_obj and current_obj.id in part4_apartment_objectives:
                    from part_4_healthcare.interiors.apartment_part4 import ApartmentPart4
                    return ApartmentPart4(self.game, room_data, building_pos)
            # Check if this should be Part 3 TLP apartment
            if self.game.objective_manager.game_part == 3:
                current_obj = self.game.objective_manager.get_current_objective()
                if current_obj and current_obj.id in ['mail_on_floor', 'read_court_notice', 'go_home']:
                    from part_3_legal_system.interiors.tlp_apartment_part3 import TLPApartmentPart3
                    return TLPApartmentPart3(self.game, room_data, building_pos)
            # Check if this should be healthcare apartment for Part 2
            if self.game.objective_manager.game_part == 2:
                from part_2_healthcare.interiors.healthcare_apartment_interior import HealthcareApartmentInterior
                return HealthcareApartmentInterior(self.game, room_data, building_pos)
            # Check if this should be Mike's place based on current objective
            current_obj = self.game.objective_manager.get_current_objective()
            if current_obj and current_obj.id == "mike_floor":
                from src.interiors.narratives.mikes_place_narrative import MikesPlaceNarrative
                return MikesPlaceNarrative(self.game, room_data, building_pos)
            # Part 2 Healthcare - use healthcare apartment interior
            elif hasattr(self.game, 'objective_manager') and self.game.objective_manager.game_part == 2:
                part2_healthcare_objectives = [
                    'start_apartment_morning', 'check_mailbox', 'medicaid_notice',
                    'therapy_reminder', 'insurance_panic', 'travel_to_clinic',
                    'therapist_call_options', 'therapy_payment_decision',
                    'caseworker_guidance', 'navigator_questions', 'coverage_restored',
                    'part2_healthcare_complete'
                ]
                if current_obj and current_obj.id in part2_healthcare_objectives:
                    from part_2_healthcare.interiors.healthcare_apartment_interior import HealthcareApartmentInterior
                    return HealthcareApartmentInterior(self.game, room_data, building_pos)
                else:
                    from src.interiors.narratives.crappy_apartment_narrative import CrappyApartmentNarrative
                    return CrappyApartmentNarrative(self.game, room_data, building_pos)
            else:
                from src.interiors.narratives.crappy_apartment_narrative import CrappyApartmentNarrative
                return CrappyApartmentNarrative(self.game, room_data, building_pos)

        elif room_name == "tlp_housing_dynamic":
            # Dynamic TLP housing - choose room based on current objective
            current_obj = self.game.objective_manager.get_current_objective()
            if current_obj:
                if current_obj.id == "tlp_rules":
                    from src.interiors.narratives.tlp_housing_early_stage import TLPHousingEarlyStage
                    return TLPHousingEarlyStage(self.game, room_data, building_pos)
                elif current_obj.id == "eighteen_months":
                    from src.interiors.narratives.tlp_housing_late_stage import TLPHousingLateStage
                    return TLPHousingLateStage(self.game, room_data, building_pos)
                elif current_obj.id == "not_alone":
                    # If it's the community center objective, load that instead
                    from src.interiors.narratives.community_center_narrative import CommunityCenterNarrative
                    return CommunityCenterNarrative(self.game, room_data, building_pos)
                elif current_obj.id == "housing_intro":
                    # Foster home aging out
                    from src.interiors.narratives.foster_home_aging_out import FosterHomeAgingOut
                    return FosterHomeAgingOut(self.game, room_data, building_pos)
            # Default to foster home aging out
            from src.interiors.narratives.foster_home_aging_out import FosterHomeAgingOut
            return FosterHomeAgingOut(self.game, room_data, building_pos)

        # Legacy interior handling
        elif room_name == "studio_apartment":
            # Use Part 2 narrative by default for legacy support
            from src.interiors.narratives.studio_apartment_narrative import StudioApartmentNarrative
            return StudioApartmentNarrative(self.game, room_data, building_pos)

        elif room_name == "legal_aid":
            from src.interiors.narratives.legal_aid_narrative import LegalAidNarrative
            return LegalAidNarrative(self.game, room_data, building_pos)

        # Standard narrative interiors
        elif room_name == "emergency_shelter":
            from src.interiors.narratives.emergency_shelter_narrative import EmergencyShelterNarrative
            return EmergencyShelterNarrative(self.game, room_data, building_pos)

        elif room_name == "library":
            from src.interiors.narratives.library_narrative import LibraryNarrative
            return LibraryNarrative(self.game, room_data, building_pos)

        elif room_name == "rental_office":
            from src.interiors.narratives.rental_office_narrative import RentalOfficeNarrative
            return RentalOfficeNarrative(self.game, room_data, building_pos)

        elif room_name == "alex_apartment":
            from src.interiors.narratives.alex_apartment_narrative import AlexApartmentNarrative
            return AlexApartmentNarrative(self.game, room_data, building_pos)

        elif room_name == "sarahs_place":
            from src.interiors.narratives.sarahs_place_narrative import SarahsPlaceNarrative
            return SarahsPlaceNarrative(self.game, room_data, building_pos)

        elif room_name == "mike":
            from src.interiors.narratives.mikes_place_narrative import MikesPlaceNarrative
            return MikesPlaceNarrative(self.game, room_data, building_pos)

        elif room_name == "grocery_store":
            # Check if this should be Part 4 workplace (Healthcare)
            if self.game.objective_manager.game_part == 4:
                current_obj = self.game.objective_manager.get_current_objective()
                part4_workplace_objectives = [
                    'work_anxiety', 'breathing_game', 'work_warning'
                ]
                if current_obj and current_obj.id in part4_workplace_objectives:
                    from part_4_healthcare.interiors.workplace_part4 import WorkplacePart4
                    return WorkplacePart4(self.game, room_data, building_pos)
            # Check if this should be Part 3 workplace
            if self.game.objective_manager.game_part == 3:
                current_obj = self.game.objective_manager.get_current_objective()
                if current_obj and current_obj.id in ['morning_shift', 'missed_court_notice']:
                    from part_3_legal_system.interiors.workplace_part3 import WorkplacePart3
                    return WorkplacePart3(self.game, room_data, building_pos)
            # Check if this should be workplace interior for Part 2 Healthcare work_day_anxiety
            if self.game.objective_manager.game_part == 2:
                current_obj = self.game.objective_manager.get_current_objective()
                if current_obj and current_obj.id == "work_day_anxiety":
                    from part_2_healthcare.interiors.workplace_interior import WorkplaceInterior
                    return WorkplaceInterior(self.game, room_data, building_pos)
            from src.interiors.narratives.grocery_store_narrative import GroceryStoreNarrative
            return GroceryStoreNarrative(self.game, room_data, building_pos)

        elif room_name == "housing_office":
            # Check if this should be Part 4 clinic (Healthcare)
            if self.game.objective_manager.game_part == 4:
                current_obj = self.game.objective_manager.get_current_objective()
                part4_clinic_objectives = [
                    'visit_clinic', 'document_check', 'medicaid_form', 'coverage_delay'
                ]
                if current_obj and current_obj.id in part4_clinic_objectives:
                    from part_4_healthcare.interiors.clinic_part4 import ClinicPart4
                    return ClinicPart4(self.game, room_data, building_pos)
            # Check if this should be Part 3 courthouse
            if self.game.objective_manager.game_part == 3:
                current_obj = self.game.objective_manager.get_current_objective()
                courthouse_objectives = ['courthouse_queue', 'court_forms', 'wrong_courtroom',
                                        'face_judge', 'court_fine', 'dispute_denied', 'courthouse_reflection']
                if current_obj and current_obj.id in courthouse_objectives:
                    from part_3_legal_system.interiors.courthouse_part3 import CourthousePart3
                    return CourthousePart3(self.game, room_data, building_pos)
            from src.interiors.narratives.housing_office_narrative import HousingOfficeNarrative
            return HousingOfficeNarrative(self.game, room_data, building_pos)

        elif room_name == "government_office":
            # Check if this should be Part 3 government office (includes police encounter)
            if self.game.objective_manager.game_part == 3:
                current_obj = self.game.objective_manager.get_current_objective()
                # Police encounter objectives now happen at government office
                gov_office_objectives = ['police_stop', 'stay_calm', 'court_citation',
                                        'gov_office_queue', 'document_sorting', 'paperwork_rejection']
                if current_obj and current_obj.id in gov_office_objectives:
                    from part_3_legal_system.interiors.government_office_part3 import GovernmentOfficePart3
                    return GovernmentOfficePart3(self.game, room_data, building_pos)
            from src.interiors.generic_interior import GenericInterior
            return GenericInterior(self.game, room_data, building_pos)

        elif room_name == "courthouse":
            # Part 3 courthouse for legal system objectives
            if self.game.objective_manager.game_part == 3:
                current_obj = self.game.objective_manager.get_current_objective()
                courthouse_objectives = ['courthouse_queue', 'court_forms', 'wrong_courtroom',
                                        'face_judge', 'court_fine', 'dispute_denied', 'courthouse_reflection']
                if current_obj and current_obj.id in courthouse_objectives:
                    from part_3_legal_system.interiors.courthouse_part3 import CourthousePart3
                    return CourthousePart3(self.game, room_data, building_pos)
            from src.interiors.generic_interior import GenericInterior
            return GenericInterior(self.game, room_data, building_pos)

        elif room_name == "pharmacy":
            # Part 4 pharmacy for healthcare objectives
            if self.game.objective_manager.game_part == 4:
                current_obj = self.game.objective_manager.get_current_objective()
                pharmacy_objectives = ['pharmacy_visit', 'select_medication']
                if current_obj and current_obj.id in pharmacy_objectives:
                    from part_4_healthcare.interiors.pharmacy_part4 import PharmacyPart4
                    return PharmacyPart4(self.game, room_data, building_pos)
            from src.interiors.generic_interior import GenericInterior
            return GenericInterior(self.game, room_data, building_pos)

        elif room_name == "trade_school":
            from src.interiors.narratives.trade_school_narrative import TradeSchoolNarrative
            return TradeSchoolNarrative(self.game, room_data, building_pos)

        elif room_name == "hospital":
            # Check if this is Part 2 emergency room scene
            current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
            if current_obj and current_obj.id == 'emergency_room':
                from src.interiors.narratives.hospital_narrative import HospitalNarrative
                return HospitalNarrative(self.game, room_data, building_pos)
            elif current_obj and current_obj.id == 'missed_work':
                from src.interiors.narratives.hospital_er_narrative import HospitalERNarrative
                return HospitalERNarrative(self.game, room_data, building_pos)
            # Part 2 Healthcare - use clinic interior for healthcare objectives
            elif hasattr(self.game, 'objective_manager') and self.game.objective_manager.game_part == 2:
                clinic_objectives = [
                    'travel_to_clinic', 'clinic_checklist', 'foster_youth_application',
                    'application_approved', 'appointment_outcome'
                ]
                if current_obj and current_obj.id in clinic_objectives:
                    from part_2_healthcare.interiors.enhanced_clinic_interior import EnhancedClinicInterior
                    return EnhancedClinicInterior(self.game, room_data, building_pos)
                else:
                    from src.interiors.generic_interior import GenericInterior
                    return GenericInterior(self.game, room_data, building_pos)
            else:
                from src.interiors.generic_interior import GenericInterior
                return GenericInterior(self.game, room_data, building_pos)

        else:
            # Create a generic interior handler
            from src.interiors.generic_interior import GenericInterior
            return GenericInterior(self.game, room_data, building_pos)

    def cleanup_interior_cache(self):
        """Clean up all cached interior instances"""
        print("[CLEANUP] Clearing interior cache...")

        for cache_key, interior in self.cached_interiors.items():
            if interior:
                # Clear interior state
                if hasattr(interior, 'active'):
                    interior.active = False

                # Clear dialogue state
                if hasattr(interior, 'dialogue_box') and interior.dialogue_box:
                    interior.dialogue_box.hide()

                # Clear narrative state
                if hasattr(interior, 'narrative_active'):
                    interior.narrative_active = False

                # Clear completed interactions
                if hasattr(interior, 'completed_interactions'):
                    interior.completed_interactions.clear()

                # Clear interactive objects
                if hasattr(interior, 'interactive_objects'):
                    interior.interactive_objects.clear()

        # Clear the cache
        self.cached_interiors.clear()

    def get_clean_interior_instance(self, room_name, building_pos):
        """Get a fresh, clean interior instance (no caching for scene separation)"""
        # Always create fresh instances to avoid state contamination
        # This ensures each scene starts with clean state
        return self.load_interior_room(room_name, building_pos)

    @timeout_operation(3.0)  # 3 second timeout
    def enter_building(self, building_pos, building_name, room_name):
        """Enter a building with the specified interior room"""
        start_time = time.time()

        # Get current objective for context
        current_obj = self.game.objective_manager.get_current_objective()
        objective_id = current_obj.id if current_obj else None

        debug_logger.log_room_entry(room_name, building_pos, objective_id)

        try:
            # Always get fresh interior instance to avoid state contamination
            interior = self.get_clean_interior_instance(room_name, building_pos)

            if interior:
                # Clean up previous interior if any
                if hasattr(self.game, 'current_interior') and self.game.current_interior:
                    self.cleanup_current_interior()

                self.game.current_interior = interior
                interior.enter()

                load_time = time.time() - start_time
                debug_logger.log_room_success(room_name, load_time)
                return True
            else:
                error_msg = f"Failed to create interior instance for {room_name}"
                debug_logger.log_room_failure(room_name, error_msg)
                return False

        except Exception as e:
            error_msg = f"Exception during room entry: {str(e)}"
            debug_logger.log_room_failure(room_name, error_msg)
            print(f"Error entering building: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_current_interior(self):
        """Clean up the current interior instance"""
        if not hasattr(self.game, 'current_interior') or not self.game.current_interior:
            return

        current_interior = self.game.current_interior

        # Clear dialogue state
        if hasattr(current_interior, 'dialogue_box') and current_interior.dialogue_box:
            current_interior.dialogue_box.hide()

        # Clear narrative state
        if hasattr(current_interior, 'narrative_active'):
            current_interior.narrative_active = False

        # Clear activity state
        if hasattr(current_interior, 'current_activity'):
            current_interior.current_activity = None

        # Deactivate
        if hasattr(current_interior, 'active'):
            current_interior.active = False

        print("[CLEANUP] Current interior cleaned up")