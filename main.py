import time
# Вместо отдельных импортов — импорт из пакета app
from app import State, SceneManager, OverrideManager, init_globals

# Инициализируем глобальные настройки (заполняет GLOBAL_CONFIG и т.д.)
init_globals()

# Создаём объекты (порядок важен: сначала State, потом менеджеры)
state = State()
scene_manager = SceneManager(state)
override_manager = OverrideManager(state)

print("=== Test Scenes ===")
scene_manager.start_scene("PR1+++")
time.sleep(5)
scene_manager.stop_scene("PR1+++")
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