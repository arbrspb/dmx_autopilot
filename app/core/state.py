class State:
    def __init__(self):
        self.current_scene = None
        self.previous_scene = None
        self.active_overrides = {}
        self.autopilot_running = False
        self.last_action_time = None
        self.error_state = None

    def set_current_scene(self, scene_id):
        self.previous_scene = self.current_scene
        self.current_scene = scene_id

    def clear_current_scene(self, scene_id=None):
        if scene_id is None or self.current_scene == scene_id:
            self.previous_scene = self.current_scene
            self.current_scene = None

    def activate_override(self, override_id):
        self.active_overrides[override_id] = True

    def deactivate_override(self, override_id):
        self.active_overrides[override_id] = False

    def is_override_active(self, override_id):
        return self.active_overrides.get(override_id, False)

    def get_active_overrides(self):
        return [
            override_id
            for override_id, is_active in self.active_overrides.items()
            if is_active
        ]