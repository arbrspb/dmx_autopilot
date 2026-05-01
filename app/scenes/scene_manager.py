# app/scenes/scene_manager.py
from app.freestyler import adapter
from app.core.state import State
import time

# Пример сцен
SCENES = {
    "warm_static": {"type": "sequence", "start_code": 505, "stop_code": 525, "duration": 10},
    "blue_move": {"type": "sequence", "start_code": 506, "stop_code": 526, "duration": 12},
}

class SceneManager:
    def __init__(self, state: State):
        self.state = state

    def start_scene(self, scene_id):
        scene = SCENES.get(scene_id)
        if not scene:
            print(f"Scene {scene_id} not found")
            return
        if scene["type"] == "sequence":
            adapter.start_sequence(scene["start_code"])
        self.state.current_scene = scene_id
        print(f"Started scene {scene_id}")

    def stop_scene(self, scene_id):
        scene = SCENES.get(scene_id)
        if not scene:
            return
        if scene["type"] == "sequence":
            adapter.stop_sequence(scene["start_code"])
        if self.state.current_scene == scene_id:
            self.state.current_scene = None
        print(f"Stopped scene {scene_id}")

    def stop_all_scenes(self):
        for scene_id in SCENES.keys():
            self.stop_scene(scene_id)