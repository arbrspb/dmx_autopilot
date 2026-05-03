import json
from pathlib import Path
from typing import Optional

from app.freestyler import adapter
from app.core.state import State


class OverrideManager:
    def __init__(self, state: State):
        self.state = state
        self.overrides = {}
        self.load_overrides()

    def load_overrides(self):
        """Загружает override-кнопки из JSON-файла конфигурации."""
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

    def _get_duration(self, override: dict, duration_sec: Optional[float] = None) -> float:
        """
        Возвращает длительность удержания/импульса.
        duration_sec из кода имеет приоритет над JSON.
        """
        if duration_sec is None:
            duration = override.get("duration_sec", override.get("duration", 1.0))
        else:
            duration = duration_sec

        min_duration = override.get("min_duration")
        max_duration = override.get("max_duration")

        if min_duration is not None:
            duration = max(float(duration), float(min_duration))

        if max_duration is not None:
            duration = min(float(duration), float(max_duration))

        return float(duration)

    def activate_override(self, override_id: str, duration_sec: Optional[float] = None):
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
        duration = self._get_duration(override, duration_sec)

        if override_type == "hold":
            print(f"[OverrideManager] Hold START: {override_id}, code={code}, duration={duration}")
            adapter.hold_button(code, duration)
            print(f"[OverrideManager] Hold END: {override_id}")

        elif override_type == "toggle":
            current = self.state.is_override_active(override_id)
            adapter.press_button(code)

            if current:
                self.state.deactivate_override(override_id)
                print(f"[OverrideManager] Toggle OFF: {override_id}, code={code}")
            else:
                self.state.activate_override(override_id)
                print(f"[OverrideManager] Toggle ON: {override_id}, code={code}")

        elif override_type == "pulse":
            print(f"[OverrideManager] Pulse: {override_id}, code={code}, duration={duration}")
            adapter.pulse_button(code, duration)

        elif override_type == "timed":
            print(f"[OverrideManager] Timed ON: {override_id}, code={code}, duration={duration}")
            adapter.press_button(code)
            self.state.activate_override(override_id)

            import time
            time.sleep(duration)

            adapter.press_button(code)
            self.state.deactivate_override(override_id)
            print(f"[OverrideManager] Timed OFF: {override_id}, code={code}")

        else:
            print(f"[OverrideManager] Unknown override type: {override_type}")

    def activate_intensity(self, override_id: str, intensity: str):
        """
        Запуск hold-override по профилю интенсивности из JSON:
        soft / medium / strong.
        """
        override = self.overrides.get(override_id)

        if not override:
            print(f"[OverrideManager] Override '{override_id}' not found")
            return

        profiles = override.get("intensity_profiles", {})
        duration = profiles.get(intensity)

        if duration is None:
            print(f"[OverrideManager] Intensity '{intensity}' not found for '{override_id}'")
            return

        self.activate_override(override_id, duration_sec=duration)

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
                print(f"[OverrideManager] OFF: {override_id}, code={code}")
            else:
                print(f"[OverrideManager] Already OFF: {override_id}")

        elif override_type == "hold":
            print(f"[OverrideManager] Hold override '{override_id}' already released automatically")

        elif override_type == "pulse":
            print(f"[OverrideManager] Pulse override '{override_id}' does not need deactivate")

        else:
            print(f"[OverrideManager] Unknown override type: {override_type}")

    def disable_all_overrides(self):
        for override_id in list(self.overrides.keys()):
            if self.state.is_override_active(override_id):
                self.deactivate_override(override_id)