import json
import os
from app.freestyler import adapter
from app.core.state import State

class OverrideManager:
    def __init__(self, state: State):
        self.state = state
        self.overrides = {}
        self.load_overrides()

    def load_overrides(self):
        """Загружает оверрайды из JSON-файла конфигурации."""
        config_path = os.path.join(os.path.dirname(__file__), '../config/overrides.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for ovr in data['overrides']:
            self.overrides[ovr['id']] = ovr

    def activate_override(self, override_id):
        override = self.overrides.get(override_id)
        if not override:
            print(f"Override {override_id} not found")
            return

        # Берём duration, если есть; если нет — дефолт 1 сек
        duration = override.get("duration", override.get("duration_sec", 1.0))

        if override["type"] == "hold":
            adapter.hold_button(override["code"], duration)
        elif override["type"] == "toggle":
            current = self.state.is_override_active(override_id)
            adapter.press_button(override["code"])
            self.state.active_overrides[override_id] = not current
        elif override["type"] == "pulse":
            adapter.pulse_button(override["code"], duration)

        print(f"Activated override {override_id}")

    def deactivate_override(self, override_id):
        override = self.overrides.get(override_id)
        if not override:
            return
        if override["type"] == "hold":
            print(f"Cannot manually deactivate hold override {override_id}")
        elif override["type"] == "toggle" and self.state.is_override_active(override_id):
            adapter.press_button(override["code"])
            self.state.active_overrides[override_id] = False
        print(f"Deactivated override {override_id}")

    def disable_all_overrides(self):
        for override_id in list(self.overrides.keys()):
            if self.state.is_override_active(override_id):
                self.deactivate_override(override_id)