import json
from pathlib import Path

from app.freestyler import adapter
from app.core.state import State


class OverrideManager:
    def __init__(self, state: State):
        self.state = state
        self.overrides = {}
        self.load_overrides()

    def load_overrides(self):
        config_path = Path(__file__).resolve().parents[1] / "config" / "overrides.json"

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data.get("overrides")

        if items is None:
            raise ValueError("В overrides.json должен быть ключ 'overrides'")

        for override in items:
            override_id = override.get("id")

            if not override_id:
                raise ValueError(f"У override нет id: {override}")

            self.overrides[override_id] = override

        print(f"[OverrideManager] Loaded overrides: {list(self.overrides.keys())}")

    def activate_override(self, override_id: str):
        override = self.overrides.get(override_id)

        if not override:
            print(f"[OverrideManager] Override '{override_id}' not found")
            return

        if not override.get("enabled", True):
            print(f"[OverrideManager] Override '{override_id}' disabled")
            return

        code = override.get("code")

        if code is None:
            print(f"[OverrideManager] Override '{override_id}' has no code")
            return

        override_type = override.get("type")
        duration = override.get("duration_sec", override.get("duration", 1.0))

        if override_type == "hold":
            adapter.hold_button(code, duration)
            print(f"[OverrideManager] Hold override: {override_id}")

        elif override_type == "toggle":
            current = self.state.is_override_active(override_id)
            adapter.press_button(code)

            if current:
                self.state.deactivate_override(override_id)
                print(f"[OverrideManager] Toggle OFF: {override_id}")
            else:
                self.state.activate_override(override_id)
                print(f"[OverrideManager] Toggle ON: {override_id}")

        elif override_type == "pulse":
            adapter.pulse_button(code, duration)
            print(f"[OverrideManager] Pulse override: {override_id}")

        elif override_type == "timed":
            adapter.press_button(code)
            self.state.activate_override(override_id)
            print(f"[OverrideManager] Timed ON: {override_id}")

        else:
            print(f"[OverrideManager] Unknown override type: {override_type}")

    def deactivate_override(self, override_id: str):
        override = self.overrides.get(override_id)

        if not override:
            print(f"[OverrideManager] Override '{override_id}' not found")
            return

        code = override.get("code")

        if code is None:
            print(f"[OverrideManager] Override '{override_id}' has no code")
            return

        override_type = override.get("type")

        if override_type in ("toggle", "timed"):
            if self.state.is_override_active(override_id):
                adapter.press_button(code)
                self.state.deactivate_override(override_id)
                print(f"[OverrideManager] OFF: {override_id}")
            else:
                print(f"[OverrideManager] Already OFF: {override_id}")

        elif override_type == "hold":
            print(f"[OverrideManager] Hold override '{override_id}' already released")

        elif override_type == "pulse":
            print(f"[OverrideManager] Pulse override '{override_id}' does not need deactivate")

        else:
            print(f"[OverrideManager] Unknown override type: {override_type}")

    def disable_all_overrides(self):
        for override_id in list(self.overrides.keys()):
            if self.state.is_override_active(override_id):
                self.deactivate_override(override_id)