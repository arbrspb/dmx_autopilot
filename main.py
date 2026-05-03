import time

from app import State, SceneManager, OverrideManager, init_globals


init_globals()

state = State()
scene_manager = SceneManager(state)
override_manager = OverrideManager(state)


print("=== Test Scenes From Config ===")

scene_manager.start_scene("pr1_plus_plus_plus")
time.sleep(5)
scene_manager.stop_scene("pr1_plus_plus_plus")

time.sleep(1)

# Эта сцена пока не запустится, потому что start_code = null.
# Но это нормальная проверка обработки ошибки.
scene_manager.start_scene("pr1_plus")
time.sleep(1)
scene_manager.stop_scene("pr1_plus")


print("=== Test Overrides From Config ===")

override_manager.activate_override("blender")

time.sleep(7)

override_manager.activate_override("blackout")
time.sleep(2)
override_manager.deactivate_override("blackout")