import json
import time
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

    def get_override(self, override_id: str):
        return self.overrides.get(override_id)

    def _get_duration(self, override: dict, duration_sec=None) -> float:
        if duration_sec is not None:
            return float(duration_sec)

        return float(override.get("duration_sec", override.get("duration", 1.0)))

    def activate_override(self, override_id: str, duration_sec=None) -> bool:
        override = self.get_override(override_id)

        if not override:
            print(f"[OverrideManager] Override '{override_id}' not found")
            return False

        if not override.get("enabled", True):
            print(f"[OverrideManager] Override '{override_id}' disabled")
            return False

        code = override.get("code")

        if code is None:
            print(f"[OverrideManager] Override '{override_id}' has no code")
            return False

        override_type = override.get("type")
        duration = self._get_duration(override, duration_sec)

        if override_type == "hold":
            adapter.hold_button(code, duration)
            print(f"[OverrideManager] Hold override: {override_id} / {duration} sec")
            return True

        if override_type == "toggle":
            current = self.state.is_override_active(override_id)

            adapter.press_button(code)

            if current:
                self.state.deactivate_override(override_id)
                print(f"[OverrideManager] Toggle OFF: {override_id}")
            else:
                self.state.activate_override(override_id)
                print(f"[OverrideManager] Toggle ON: {override_id}")

            return True

        if override_type == "pulse":
            adapter.pulse_button(code, duration)
            print(f"[OverrideManager] Pulse override: {override_id} / {duration} sec")
            return True

        if override_type == "timed":
            adapter.press_button(code)
            self.state.activate_override(override_id)
            print(f"[OverrideManager] Timed ON: {override_id} / {duration} sec")

            time.sleep(duration)

            adapter.press_button(code)
            self.state.deactivate_override(override_id)
            print(f"[OverrideManager] Timed OFF: {override_id}")
            return True

        print(f"[OverrideManager] Unknown override type: {override_type}")
        return False

    def deactivate_override(self, override_id: str) -> bool:
        override = self.get_override(override_id)

        if not override:
            print(f"[OverrideManager] Override '{override_id}' not found")
            return False

        code = override.get("code")

        if code is None:
            print(f"[OverrideManager] Override '{override_id}' has no code")
            return False

        override_type = override.get("type")

        if override_type in ("toggle", "timed"):
            if self.state.is_override_active(override_id):
                adapter.press_button(code)
                self.state.deactivate_override(override_id)
                print(f"[OverrideManager] OFF: {override_id}")
            else:
                print(f"[OverrideManager] Already OFF: {override_id}")

            return True

        if override_type == "hold":
            print(f"[OverrideManager] Hold override '{override_id}' already released")
            return True

        if override_type == "pulse":
            print(f"[OverrideManager] Pulse override '{override_id}' does not need deactivate")
            return True

        print(f"[OverrideManager] Unknown override type: {override_type}")
        return False

    def activate_intensity(self, override_id: str, profile_name: str) -> bool:
        override = self.get_override(override_id)

        if not override:
            print(f"[OverrideManager] Override '{override_id}' not found")
            return False

        profiles = override.get("intensity_profiles", {})
        duration = profiles.get(profile_name)

        if duration is None:
            print(
                f"[OverrideManager] Intensity profile '{profile_name}' "
                f"not found for '{override_id}'"
            )
            return False

        return self.activate_override(override_id, duration_sec=duration)

    def disable_all_overrides(self) -> None:
        for override_id in list(self.overrides.keys()):
            if self.state.is_override_active(override_id):
                self.deactivate_override(override_id)