import time

from app.core.state import State
from app.scenes.scene_manager import SceneManager
from app.overrides.override_manager import OverrideManager


class AutopilotEngine:
    def __init__(
        self,
        state: State,
        scene_manager: SceneManager,
        override_manager: OverrideManager,
    ):
        self.state = state
        self.scene_manager = scene_manager
        self.override_manager = override_manager

    def run_scene_once(
        self,
        scene_id: str,
        scene_duration_sec=None,
        override_id=None,
        override_delay_sec: float = 2.0,
        override_duration_sec=None,
    ) -> bool:
        """
        Первая простая логика автопилота:

        1. Запустить сцену.
        2. Подождать override_delay_sec.
        3. Если задан override_id — выполнить override.
        4. Додержать сцену до scene_duration_sec.
        5. Остановить сцену.
        """

        scene = self.scene_manager.get_scene(scene_id)

        if not scene:
            print(f"[Autopilot] Scene '{scene_id}' not found")
            return False

        duration = float(
            scene_duration_sec
            if scene_duration_sec is not None
            else scene.get("default_duration_sec", 10)
        )

        duration = max(0.1, duration)
        override_delay_sec = max(0.0, float(override_delay_sec))

        self.state.autopilot_running = True

        print(
            f"[Autopilot] Start scene_once: scene={scene_id}, "
            f"duration={duration}, override={override_id}"
        )

        started = False

        try:
            started = self.scene_manager.start_scene(scene_id)

            if not started:
                return False

            scene_started_at = time.time()

            if override_id:
                wait_before_override = min(override_delay_sec, duration)
                time.sleep(wait_before_override)

                self._run_override_for_autopilot(
                    override_id=override_id,
                    duration_sec=override_duration_sec,
                )

            elapsed = time.time() - scene_started_at
            remaining = duration - elapsed

            if remaining > 0:
                time.sleep(remaining)

            return True

        except KeyboardInterrupt:
            print("[Autopilot] Interrupted by user")
            self.panic_stop()
            return False

        except Exception as e:
            print(f"[Autopilot] Error: {e}")
            self.state.error_state = str(e)
            self.panic_stop()
            return False

        finally:
            if started:
                self.scene_manager.stop_scene(scene_id)

            self.state.autopilot_running = False
            print("[Autopilot] Finished scene_once")

    def _run_override_for_autopilot(self, override_id: str, duration_sec=None) -> bool:
        override = self.override_manager.get_override(override_id)

        if not override:
            print(f"[Autopilot] Override '{override_id}' not found")
            return False

        override_type = override.get("type")

        if override_type in ("hold", "pulse", "timed"):
            return self.override_manager.activate_override(
                override_id,
                duration_sec=duration_sec,
            )

        if override_type == "toggle":
            duration = float(
                duration_sec
                if duration_sec is not None
                else override.get("duration_sec", override.get("duration", 1.0))
            )

            self.override_manager.activate_override(override_id)
            time.sleep(duration)
            self.override_manager.deactivate_override(override_id)
            return True

        print(f"[Autopilot] Unknown override type: {override_type}")
        return False

    def stop_autopilot(self) -> None:
        print("[Autopilot] Stop autopilot")
        self.state.autopilot_running = False
        self.override_manager.disable_all_overrides()
        self.scene_manager.stop_current_scene()

    def panic_stop(self) -> None:
        print("[Autopilot] PANIC STOP")

        self.state.autopilot_running = False

        try:
            self.override_manager.disable_all_overrides()
        finally:
            self.scene_manager.stop_current_scene()