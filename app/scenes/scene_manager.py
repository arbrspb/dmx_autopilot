import json
import os
from app.freestyler import adapter
from app.core.state import State

class SceneManager:
    def __init__(self, state: State):
        self.state = state
        self.scenes = {}
        self.load_scenes()

    def load_scenes(self):
        """Загружает сцены из JSON-файла конфигурации."""
        config_path = os.path.join(os.path.dirname(__file__), '../config/scenes.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for scene in data['scenes']:
            self.scenes[scene['id']] = scene

    def start_scene(self, scene_id):
        scene = self.scenes.get(scene_id)
        if not scene:
            print(f"Scene {scene_id} not found")
            return
        if scene.get("type") == "sequence":
            adapter.start_sequence(scene["start_code"])
        self.state.current_scene = scene_id
        print(f"Started scene {scene_id}")

    def stop_scene(self, scene_id):
        scene = self.scenes.get(scene_id)
        if not scene:
            return
        if scene.get("type") == "sequence":
            adapter.stop_sequence(scene["start_code"])
        if self.state.current_scene == scene_id:
            self.state.current_scene = None
        print(f"Stopped scene {scene_id}")

    def stop_all_scenes(self):
        for scene_id in list(self.scenes.keys()):
            self.stop_scene(scene_id)