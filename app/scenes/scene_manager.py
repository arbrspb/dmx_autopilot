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

        # Поддерживаем оба варианта на будущее:
        # "programs" — как сейчас у тебя
        # "scenes" — если позже переименуем
        items = data.get("programs") or data.get("scenes")

        if items is None:
            raise ValueError(
                "В scenes.json должен быть ключ 'programs' или 'scenes'"
            )

        for scene in items:
            scene_id = scene.get("id")

            if not scene_id:
                raise ValueError(f"У сцены нет id: {scene}")

            self.scenes[scene_id] = scene

        print(f"[SceneManager] Loaded scenes: {list(self.scenes.keys())}")

    def start_scene(self, scene_id: str):
        scene = self.scenes.get(scene_id)

        if not scene:
            print(f"[SceneManager] Scene '{scene_id}' not found")
            return

        if not scene.get("enabled", True):
            print(f"[SceneManager] Scene '{scene_id}' disabled")
            return

        start_code = scene.get("start_code")

        if start_code is None:
            print(f"[SceneManager] Scene '{scene_id}' has no start_code")
            return

        adapter.start_sequence(start_code)

        self.state.current_scene = scene_id
        print(f"[SceneManager] Started scene: {scene_id}")

    def stop_scene(self, scene_id: str):
        scene = self.scenes.get(scene_id)

        if not scene:
            print(f"[SceneManager] Scene '{scene_id}' not found")
            return

        start_code = scene.get("start_code")

        if start_code is None:
            print(f"[SceneManager] Scene '{scene_id}' has no start_code")
            return

        # Если stop_code есть в JSON — используем его.
        # Если нет — считаем по правилу FreeStyler: stop = start + 20.
        stop_code = scene.get("stop_code", start_code + 20)

        adapter.stop_sequence(stop_code)

        if self.state.current_scene == scene_id:
            self.state.current_scene = None

        print(f"[SceneManager] Stopped scene: {scene_id}")

    def stop_all_scenes(self):
        for scene_id in list(self.scenes.keys()):
            self.stop_scene(scene_id)