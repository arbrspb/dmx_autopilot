import time

from app.core.state import State
from app.overrides.override_manager import OverrideManager

state = State()
override_manager = OverrideManager(state)


override_manager.activate_override("gobo_3_pol")
time.sleep(6)
override_manager.activate_override("gobo_3_pol")
