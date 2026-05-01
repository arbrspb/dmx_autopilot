class State:
    def __init__(self):
        self.current_scene = None
        self.active_overrides = {}
        self.autopilot_running = False
        self.last_action_time = None

    def activate_override(self, override_id):
        self.active_overrides[override_id] = True

    def deactivate_override(self, override_id):
        self.active_overrides[override_id] = False

    def is_override_active(self, override_id):
        return self.active_overrides.get(override_id, False)