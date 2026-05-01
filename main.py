from app.core.state import State
from app.scenes.scene_manager import SceneManager
from app.overrides.override_manager import OverrideManager
import time

state = State()
scene_manager = SceneManager(state)
override_manager = OverrideManager(state)

print("=== Test Scenes ===")
scene_manager.start_scene("warm_static")
time.sleep(2)
override_manager.activate_override("strobe")
time.sleep(2)
scene_manager.stop_scene("warm_static")
override_manager.activate_override("blackout")  # toggle example
time.sleep(2)
override_manager.deactivate_override("blackout")

print("=== Test Sequences ===")
scene_manager.start_scene("blue_move")
time.sleep(2)
scene_manager.stop_scene("blue_move")