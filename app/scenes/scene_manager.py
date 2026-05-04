import json
from pathlib import Path

from app.freestyler import adapter
from app.core.state import State


class SceneManager:
    def __init__(self, state: State):
        self.state = state
        self.scenes = {}
        self.load_scenes()

    def load_scenes(self):
        config_path = Path(__file__).resolve().parents[1] / "config" / "scenes.json"

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Поддерживаем оба варианта:
        # новый/текущий на GitHub: "programs"
        # будущий/логичный: "scenes"
        items = data.get("scenes") or data.get("programs")

        if items is None:
            raise ValueError("В scenes.json должен быть ключ 'scenes' или 'programs'")

        for scene in items:
            scene_id = scene.get("id")
            if not scene_id:
                raise ValueError(f"У сцены нет id: {scene}")

            self.scenes[scene_id] = scene

        print(f"[SceneManager] Loaded scenes: {list(self.scenes.keys())}")

    def get_scene(self, scene_id: str):
        return self.scenes.get(scene_id)

    def _get_start_code(self, scene: dict):
        start_code = scene.get("start_code")

        if start_code is not None:
            return int(start_code)

        slot = scene.get("slot")
        if slot is None:
            return None

        # Текущая схема страницы ALL:
        # slot 1 = 505
        # slot 2 = 506
        # ...
        return 505 + (int(slot) - 1)

    def _get_stop_code(self, scene: dict):
        stop_code = scene.get("stop_code")

        if stop_code is not None:
            return int(stop_code)

        start_code = self._get_start_code(scene)

        if start_code is None:
            return None

        # Текущая договорённость:
        # stop_code = start_code + 20
        return start_code + 20

    def start_scene(self, scene_id: str) -> bool:
        scene = self.get_scene(scene_id)

        if not scene:
            print(f"[SceneManager] Scene '{scene_id}' not found")
            return False

        if not scene.get("enabled", True):
            print(f"[SceneManager] Scene '{scene_id}' disabled")
            return False

        start_code = self._get_start_code(scene)

        if start_code is None:
            print(f"[SceneManager] Scene '{scene_id}' has no start_code and no slot")
            return False

        adapter.start_sequence(start_code)
        self.state.set_current_scene(scene_id)

        print(f"[SceneManager] Started scene: {scene_id} / code {start_code}")
        return True

    def stop_scene(self, scene_id: str) -> bool:
        scene = self.get_scene(scene_id)

        if not scene:
            print(f"[SceneManager] Scene '{scene_id}' not found")
            return False

        stop_code = self._get_stop_code(scene)

        if stop_code is None:
            print(f"[SceneManager] Scene '{scene_id}' has no stop_code")
            return False

        adapter.stop_sequence(stop_code)
        self.state.clear_current_scene(scene_id)

        print(f"[SceneManager] Stopped scene: {scene_id} / code {stop_code}")
        return True

    def stop_current_scene(self) -> None:
        if self.state.current_scene:
            self.stop_scene(self.state.current_scene)

    def stop_all_scenes(self) -> None:
        for scene_id in list(self.scenes.keys()):
            self.stop_scene(scene_id)