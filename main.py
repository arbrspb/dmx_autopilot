from app.core.state import State
from app.scenes.scene_manager import SceneManager
from app.overrides.override_manager import OverrideManager
from app.autopilot.autopilot_engine import AutopilotEngine


state = State()

scene_manager = SceneManager(state)
override_manager = OverrideManager(state)

autopilot = AutopilotEngine(
    state=state,
    scene_manager=scene_manager,
    override_manager=override_manager,
)

# Тест 1:
# Сцена -> Blender hold на 3 секунды -> стоп сцены
autopilot.run_scene_once(
    scene_id="pr11_speed_max",
    scene_duration_sec=10,
    override_id="blender_strobe_min",
    override_delay_sec=1,
    override_duration_sec=1,
)

# Тест 2 для toggle, потом можно раскомментировать:
# autopilot.run_scene_once(
#     scene_id="blue",
#     scene_duration_sec=10,
#     override_id="gobo_3_pol",
#     override_delay_sec=2,
#     override_duration_sec=4,
# )