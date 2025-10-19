import os
import pygame

from shared.initial_room_interior import InitialRoomInterior


class DummyObjective:
    def __init__(self, obj_id):
        self.id = obj_id


class DummyManager:
    def __init__(self, obj_id):
        self.obj = DummyObjective(obj_id)

    def get_current_objective(self):
        return self.obj

    def advance_to_next_objective(self):
        print("advance called")

    def show_notification(self, text, color=(255, 255, 255)):
        print("NOTIFY:", text)


class DummyGame:
    def __init__(self, obj_id):
        self.objective_manager = DummyManager(obj_id)


def main():
    pygame.init()
    room_data = {"width": 16, "height": 12, "layers": {}}

    ir = InitialRoomInterior(DummyGame("cash_reality"), room_data, (8, 11))
    ir.conversation_active = False
    ir.events_started.add("packed_belongings")
    ir.mark_event_completed("packed_belongings")

    ir.player_x = ir.wallet_pos[0]
    ir.player_y = ir.wallet_pos[1]

    print("trigger returns:", ir._try_trigger_interaction())
    print("active_event", ir.active_event)


if __name__ == "__main__":
    main()

