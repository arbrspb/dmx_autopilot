import time

from app.core.state import State
from app.overrides.override_manager import OverrideManager

state = State()
override_manager = OverrideManager(state)

# Blender мягко
override_manager.activate_override("blender", duration_sec=2.0)
time.sleep(1)

# Blender средне
override_manager.activate_override("blender", duration_sec=4.0)
time.sleep(1)

# Blender сильно
override_manager.activate_override("blender", duration_sec=7.0)
time.sleep(1)

# Или через профили из JSON
override_manager.activate_intensity("blender", "soft")
time.sleep(1)
override_manager.activate_intensity("blender", "medium")
time.sleep(1)
override_manager.activate_intensity("blender", "strong")