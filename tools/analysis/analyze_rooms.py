import json

with open('interior_rooms.json', 'r') as f:
    data = json.load(f)

# Access the rooms data
room_data = data['rooms']

# Check all available rooms
print("Available rooms:", list(room_data.keys()))

# Room types we're interested in
target_rooms = ['burger_room', 'classroom', 'community_center', 'community_center_workshop', 
                'foster_classroom', 'foster_home', 'groccery_store', 'housing_office', 
                'japenese_home', 'pizzaplace', 'tlp_apartment']

# Common furniture and decor items based on typical game tilesets
room_essentials = {
    'burger_room': {
        'expected': ['tables', 'chairs', 'counter', 'kitchen equipment', 'menu boards'],
        'floor': 'restaurant/kitchen flooring',
        'walls': 'interior walls'
    },
    'classroom': {
        'expected': ['desks', 'chairs', 'blackboard/whiteboard', 'teacher desk', 'bookshelf'],
        'floor': 'classroom flooring',
        'walls': 'interior walls with windows'
    },
    'community_center': {
        'expected': ['seating areas', 'tables', 'reception desk', 'notice board'],
        'floor': 'public building flooring',
        'walls': 'interior walls'
    },
    'community_center_workshop': {
        'expected': ['workbenches', 'tool storage', 'chairs/stools', 'equipment'],
        'floor': 'workshop flooring',
        'walls': 'interior walls'
    },
    'foster_classroom': {
        'expected': ['desks', 'chairs', 'teaching materials', 'storage'],
        'floor': 'classroom flooring',
        'walls': 'interior walls'
    },
    'foster_home': {
        'expected': ['beds', 'dressers', 'living room furniture', 'kitchen items', 'dining table'],
        'floor': 'home flooring',
        'walls': 'interior walls'
    },
    'groccery_store': {
        'expected': ['shelves', 'freezers', 'checkout counter', 'shopping baskets/carts'],
        'floor': 'store flooring',
        'walls': 'interior walls'
    },
    'housing_office': {
        'expected': ['desks', 'chairs', 'filing cabinets', 'waiting area seating'],
        'floor': 'office flooring',
        'walls': 'interior walls'
    },
    'japenese_home': {
        'expected': ['tatami mats', 'low tables', 'futons', 'sliding doors', 'traditional decor'],
        'floor': 'traditional Japanese flooring',
        'walls': 'traditional walls/screens'
    },
    'pizzaplace': {
        'expected': ['tables', 'chairs', 'pizza oven', 'counter', 'kitchen equipment'],
        'floor': 'restaurant flooring',
        'walls': 'interior walls'
    },
    'tlp_apartment': {
        'expected': ['bed', 'dresser', 'desk', 'chair', 'kitchen appliances', 'bathroom fixtures'],
        'floor': 'apartment flooring',
        'walls': 'interior walls'
    }
}

for room_name in target_rooms:
    if room_name in room_data:
        room = room_data[room_name]
        print(f'\n{"="*60}')
        print(f'{room_name.upper()}')
        print(f'Size: {room.get("width", "?")} x {room.get("height", "?")}')
        print(f'{"="*60}')
        
        if 'layers' in room:
            layers = room['layers']
            
            # Analyze each layer
            for layer_name in ['floor', 'walls', 'furniture', 'decor']:
                if layer_name in layers:
                    layer_data = layers[layer_name]
                    if 'data' in layer_data:
                        tiles = layer_data['data']
                        non_null = sum(1 for tile in tiles if tile is not None and tile != -1)
                        unique_tiles = sorted(set(tile for tile in tiles if tile is not None and tile != -1))
                        
                        print(f'\n{layer_name.upper()} LAYER:')
                        if non_null > 0:
                            print(f'  - Tiles placed: {non_null}')
                            print(f'  - Unique tile IDs: {unique_tiles[:10]}{"..." if len(unique_tiles) > 10 else ""}')
                            print(f'  - Total unique tiles: {len(unique_tiles)}')
                        else:
                            print(f'  - EMPTY LAYER')
                    else:
                        print(f'\n{layer_name.upper()} LAYER: NO DATA')
                else:
                    print(f'\n{layer_name.upper()} LAYER: MISSING')
            
            # Recommendations
            if room_name in room_essentials:
                print(f'\nEXPECTED ITEMS FOR {room_name.upper()}:')
                essentials = room_essentials[room_name]
                print(f'  - Floor type: {essentials["floor"]}')
                print(f'  - Wall type: {essentials["walls"]}')
                print(f'  - Essential furniture/items: {", ".join(essentials["expected"])}')
        else:
            print('  - NO LAYERS DATA')
    else:
        print(f'\n{room_name.upper()}: NOT FOUND IN FILE')