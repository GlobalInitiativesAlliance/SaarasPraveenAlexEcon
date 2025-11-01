"""
Scene Generator - Automated Scene Creation System
Transforms GameObjectives into playable narrative scenes
"""

import json
import os
from typing import Dict, List, Tuple

class SceneGenerator:
    """Generates narrative interior files from objective specifications"""

    def __init__(self):
        self.template = self.load_template()
        self.existing_activities = self.scan_activities()
        self.room_mappings = self.load_room_mappings()

    def load_template(self) -> str:
        """Base template for narrative interior files"""
        return '''"""
{description}
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class {class_name}(NarrativeInterior):
    """{doc_string}"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/{room_json}.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {{
{content}
        }}
'''

    def scan_activities(self) -> List[str]:
        """Scan existing activities to avoid duplicates"""
        activities_path = "/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon/src/activities"
        if os.path.exists(activities_path):
            return [f.replace('.py', '') for f in os.listdir(activities_path) if f.endswith('.py')]
        return []

    def load_room_mappings(self) -> Dict[str, str]:
        """Map location types to existing room JSON files"""
        return {
            'studio_apartment': 'bad_studio',
            'legal_aid': 'housing_office',
            'tenant_meeting': 'library',
            'courthouse': 'rental_office',
            'new_apartment': 'alex_apartment',
            'hospital': 'hospital',
            'bank': 'bank',
            'grocery_store': 'grocery_store',
            'emergency_shelter': 'emergency_shelter'
        }

    def generate_scene(self, scene_config: Dict) -> str:
        """Generate a complete narrative interior file from config"""

        # Parse scene configuration
        location_name = scene_config['location_name']
        class_name = self.to_class_name(location_name)
        description = scene_config.get('description', f'{location_name} interior')
        objectives = scene_config['objectives']

        # Get the room JSON file to use
        room_json = self.room_mappings.get(location_name, location_name)

        # Build content for each objective
        content_blocks = []
        for obj_id, obj_data in objectives.items():
            content = self.generate_objective_content(obj_id, obj_data)
            content_blocks.append(content)

        # Fill template
        scene_file = self.template.format(
            description=description,
            class_name=class_name,
            doc_string=f"{location_name} with narrative sequences",
            room_json=room_json,
            content='\n'.join(content_blocks)
        )

        return scene_file

    def generate_objective_content(self, obj_id: str, obj_data: Dict) -> str:
        """Generate content block for a single objective"""

        # Build NPC list
        npcs = obj_data.get('npcs', [])
        npc_str = self.format_npcs(npcs)

        # Build dialogue sequence
        dialogue = obj_data.get('dialogue', [])
        dialogue_str = self.format_dialogue(dialogue)

        # Build interactions
        interactions = obj_data.get('interactions', {})
        interactions_str = self.format_interactions(interactions)

        # Combine into objective block
        content = f"""            '{obj_id}': {{
                'npcs': {npc_str},
                'dialogue_sequence': {dialogue_str},
                'interactions': {interactions_str}
            }},"""

        return content

    def format_npcs(self, npcs: List[Dict]) -> str:
        """Format NPC list for Python code"""
        if not npcs:
            return "[]"

        npc_strs = []
        for npc in npcs:
            npc_str = f"{{'name': '{npc['name']}', 'x': {npc['x']}, 'y': {npc['y']}}}"
            npc_strs.append(npc_str)

        joined = ',\n                    '.join(npc_strs)
        return f"[\n                    {joined}\n                ]"

    def format_dialogue(self, dialogue: List[Tuple]) -> str:
        """Format dialogue sequence for Python code"""
        if not dialogue:
            return "[]"

        dialogue_strs = []
        for speaker, text in dialogue:
            if speaker is None:
                dialogue_strs.append(f'(None, "{text}")')
            else:
                dialogue_strs.append(f'("{speaker}", "{text}")')

        joined = ',\n                    '.join(dialogue_strs)
        return f"[\n                    {joined}\n                ]"

    def format_interactions(self, interactions: Dict) -> str:
        """Format interactions dictionary for Python code"""
        if not interactions:
            return "{}"

        interaction_strs = []
        for obj_name, obj_data in interactions.items():
            interaction_str = f"""'{obj_name}': {{
                        'position': {obj_data['position']},
                        'prompt': '{obj_data['prompt']}',"""

            if 'trigger_activity' in obj_data:
                interaction_str += f"\n                        'trigger_activity': '{obj_data['trigger_activity']}',"

            if 'dialogue' in obj_data:
                if obj_data['dialogue']:
                    dialogue_items = [f'"{d}"' for d in obj_data['dialogue']]
                    interaction_str += f"\n                        'dialogue': [{', '.join(dialogue_items)}],"
                else:
                    interaction_str += "\n                        'dialogue': None,"

            interaction_str += "\n                    }"
            interaction_strs.append(interaction_str)

        joined = ',\n                    '.join(interaction_strs)
        return f"{{\n                    {joined}\n                }}"

    def to_class_name(self, location_name: str) -> str:
        """Convert location name to Python class name"""
        parts = location_name.replace('_', ' ').title().split()
        return ''.join(parts) + 'Narrative'

    def validate_scene(self, scene_file: str) -> List[str]:
        """Validate generated scene for common issues"""
        issues = []

        # Check for syntax issues
        if scene_file.count('{') != scene_file.count('}'):
            issues.append("Mismatched braces")

        if scene_file.count('[') != scene_file.count(']'):
            issues.append("Mismatched brackets")

        if scene_file.count('(') != scene_file.count(')'):
            issues.append("Mismatched parentheses")

        # Check for required imports
        if 'from src.interiors.narrative_interior import NarrativeInterior' not in scene_file:
            issues.append("Missing NarrativeInterior import")

        return issues


# Scene configurations for Part 2
PART2_SCENES = {
    'studio_apartment': {
        'location_name': 'studio_apartment',
        'description': 'Crappy studio apartment from Part 1 ending',
        'objectives': {
            'studio_day_one': {
                'npcs': [
                    {'name': 'Landlord', 'x': 5, 'y': 6},
                    {'name': 'Neighbor', 'x': 10, 'y': 4}
                ],
                'dialogue': [
                    ('Landlord', "Rent's due on the first. Don't be late."),
                    ('You', "What about the broken heater you promised to fix?"),
                    ('Landlord', "I'll get to it when I get to it."),
                    (None, "He leaves without another word. You're on your own."),
                    ('Neighbor', "Hey, new tenant? Word of advice - document everything."),
                    ('Neighbor', "Take photos, save texts. You'll need evidence."),
                    (None, "The apartment is worse than you thought. Roaches scatter as you walk.")
                ],
                'interactions': {
                    'heater': {
                        'position': (3, 8),
                        'prompt': 'Examine broken heater',
                        'dialogue': ["It hasn't worked in months.", "Ice cold to the touch.", "Landlord knew about this."]
                    },
                    'window': {
                        'position': (12, 5),
                        'prompt': 'Check window locks',
                        'dialogue': ["The lock is broken.", "Anyone could get in.", "No wonder there were break-ins."]
                    },
                    'phone': {
                        'position': (7, 7),
                        'prompt': 'Document problems',
                        'trigger_activity': 'document_violations'
                    }
                }
            },
            'document_problems': {
                'npcs': [],
                'dialogue': [
                    (None, "Time to build your case. Document everything."),
                    (None, "Take photos of every violation, every broken thing."),
                    (None, "This evidence might save you later.")
                ],
                'interactions': {
                    'camera': {
                        'position': (7, 7),
                        'prompt': 'Start documenting',
                        'trigger_activity': 'document_violations'
                    }
                }
            },
            'first_repair_request': {
                'npcs': [],
                'dialogue': [
                    (None, "You text the landlord about the heater."),
                    (None, "He reads it immediately. The 'read' receipt shows."),
                    (None, "No response. Hours pass. Still nothing."),
                    (None, "You'll freeze tonight. Again.")
                ],
                'interactions': {}
            }
        }
    },

    'legal_aid': {
        'location_name': 'legal_aid',
        'description': 'Free legal aid office for tenant rights',
        'objectives': {
            'legal_aid_visit': {
                'npcs': [
                    {'name': 'Lawyer', 'x': 8, 'y': 5},
                    {'name': 'Receptionist', 'x': 4, 'y': 3}
                ],
                'dialogue': [
                    ('Receptionist', "Sign in and take a number. Wait time is about 2 hours."),
                    ('You', "I can wait. I need help with my landlord."),
                    (None, "Two hours later..."),
                    ('Lawyer', "I've reviewed your documentation. You have a strong case."),
                    ('Lawyer', "Your landlord is violating at least 12 housing codes."),
                    ('You', "Can he evict me if I complain?"),
                    ('Lawyer', "Not legally. That would be retaliation, which is illegal."),
                    ('Lawyer', "But document everything. They might try anyway.")
                ],
                'interactions': {
                    'desk': {
                        'position': (8, 6),
                        'prompt': 'Show evidence',
                        'dialogue': ["You spread out your photos.", "The lawyer takes notes.", "This is worse than most cases."]
                    },
                    'pamphlets': {
                        'position': (3, 7),
                        'prompt': 'Read tenant rights',
                        'trigger_activity': 'research_rights'
                    }
                }
            },
            'withholding_threat': {
                'npcs': [
                    {'name': 'Lawyer', 'x': 8, 'y': 5}
                ],
                'dialogue': [
                    ('Lawyer', "I'll send a demand letter to your landlord."),
                    ('Lawyer', "Fix the violations or you can legally withhold rent."),
                    ('You', "Won't that make things worse?"),
                    ('Lawyer', "Maybe. But freezing in an unsafe apartment is already worse."),
                    ('Lawyer', "You have rights. It's time to use them.")
                ],
                'interactions': {
                    'letter': {
                        'position': (8, 6),
                        'prompt': 'Review demand letter',
                        'dialogue': ["It lists every violation.", "The legal language is intimidating.", "This might actually work."]
                    }
                }
            }
        }
    }
}


def generate_all_scenes():
    """Generate all scene files for Part 2"""
    generator = SceneGenerator()

    for location, config in PART2_SCENES.items():
        print(f"Generating {location}_narrative.py...")

        # Generate the scene file
        scene_content = generator.generate_scene(config)

        # Validate
        issues = generator.validate_scene(scene_content)
        if issues:
            print(f"  Validation issues: {issues}")

        # Save the file
        output_path = f"/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon/src/interiors/narratives/{location}_narrative.py"

        with open(output_path, 'w') as f:
            f.write(scene_content)

        print(f"  Saved to: {output_path}")
        print(f"  Size: {len(scene_content)} characters")
        print()

    return True


if __name__ == "__main__":
    print("Scene Generator - Part 2 Housing")
    print("-" * 40)
    generate_all_scenes()