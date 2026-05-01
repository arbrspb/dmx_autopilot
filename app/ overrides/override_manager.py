# app/overrides/override_manager.py
from app.freestyler import adapter
from app.core.state import State
import time

# Пример override-кнопок
OVERRIDES = {
    "strobe": {"type": "hold", "code": 72, "duration": 1.5},
    "blackout": {"type": "toggle", "code": 73},
}

class OverrideManager:
    def __init__(self, state: State):
        self.state = state

    def activate_override(self, override_id):
        override = OVERRIDES.get(override_id)
        if not override:
            print(f"Override {override_id} not found")
            return
        if override["type"] == "hold":
            adapter.hold_button(override["code"], override["duration"])
        elif override["type"] == "toggle":
            current = self.state.is_override_active(override_id)
            adapter.press_button(override["code"])
            self.state.active_overrides[override_id] = not current
        print(f"Activated override {override_id}")

    def deactivate_override(self, override_id):
        override = OVERRIDES.get(override_id)
        if not override:
            return
        if override["type"] == "hold":
            print(f"Cannot deactivate hold override {override_id} manually")
        elif override["type"] == "toggle" and self.state.is_override_active(override_id):
            adapter.press_button(override["code"])
            self.state.active_overrides[override_id] = False
        print(f"Deactivated override {override_id}")

    def disable_all_overrides(self):
        for override_id in OVERRIDES.keys():
            if self.state.is_override_active(override_id):
                self.deactivate_override(override_id)