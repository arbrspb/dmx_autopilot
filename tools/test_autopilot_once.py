import json
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.state import State
from app.scenes.scene_manager import SceneManager
from app.overrides.override_manager import OverrideManager
from app.autopilot.autopilot_engine import AutopilotEngine


SCENES_CONFIG_PATH = PROJECT_ROOT / "app" / "config" / "scenes.json"
OVERRIDES_CONFIG_PATH = PROJECT_ROOT / "app" / "config" / "overrides.json"
CALIBRATION_PATH = PROJECT_ROOT / "app" / "config" / "calibration" / "looks_verified.json"


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{suffix}]: ").strip().lower()

    if not value:
        return default

    return value in ("y", "yes", "д", "да")


def ask_text(prompt: str, default: str = "") -> str:
    value = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return value if value else default


def ask_float(prompt: str, default: float) -> float:
    value = input(f"{prompt} [{default}]: ").strip()

    if not value:
        return default

    return float(value.replace(",", "."))


def find_by_id(items: list[dict], item_id: str) -> dict | None:
    for item in items:
        if item.get("id") == item_id:
            return item

    return None


def upsert_verified_record(record: dict) -> None:
    data = load_json(CALIBRATION_PATH, {"looks": []})
    records = data.setdefault("looks", [])

    record_id = record["id"]

    for index, existing in enumerate(records):
        if existing.get("id") == record_id:
            records[index] = record
            save_json(CALIBRATION_PATH, data)
            return

    records.append(record)
    save_json(CALIBRATION_PATH, data)


def main():
    print("=== DMX Autopilot / Test Autopilot Once ===\n")

    scenes_config = load_json(SCENES_CONFIG_PATH, {"scenes": []})
    overrides_config = load_json(OVERRIDES_CONFIG_PATH, {"overrides": []})

    scene_id = ask_text("Scene id", "pr11_speed_max")
    scene = find_by_id(scenes_config.get("scenes", []), scene_id)

    if scene is None:
        print(f"ВНИМАНИЕ: scene_id '{scene_id}' не найден в scenes.json.")
    else:
        print("\n--- Scene ---")
        print(json.dumps(scene, ensure_ascii=False, indent=2))

    scene_duration_sec = ask_float("Scene duration sec", 10.0)

    override_id = ask_text("Override id или пусто без override", "blender_strobe_min")
    override_id = override_id if override_id else None

    override = None
    override_delay_sec = None
    override_duration_sec = None

    if override_id:
        override = find_by_id(overrides_config.get("overrides", []), override_id)

        if override is None:
            print(f"ВНИМАНИЕ: override_id '{override_id}' не найден в overrides.json.")
        else:
            print("\n--- Override ---")
            print(json.dumps(override, ensure_ascii=False, indent=2))

        override_delay_sec = ask_float("Override delay sec", 1.0)

        default_override_duration = 1.0
        if override:
            default_override_duration = float(
                override.get("duration", override.get("duration_sec", 1.0))
            )

        override_duration_sec = ask_float("Override duration sec", default_override_duration)

    look_id_default = scene_id if not override_id else f"{scene_id}__{override_id}"
    look_id = ask_text("Calibration look id", look_id_default)
    look_name = ask_text("Calibration look name", look_id)

    print("\n--- Test plan ---")
    print(f"Scene: {scene_id}")
    print(f"Scene duration: {scene_duration_sec}")
    print(f"Override: {override_id}")
    print(f"Override delay: {override_delay_sec}")
    print(f"Override duration: {override_duration_sec}")

    input("\nНажми Enter, чтобы запустить тест автопилота...")

    state = State()
    scene_manager = SceneManager(state)
    override_manager = OverrideManager(state)

    autopilot = AutopilotEngine(
        state=state,
        scene_manager=scene_manager,
        override_manager=override_manager,
    )

    kwargs = {
        "scene_id": scene_id,
        "scene_duration_sec": scene_duration_sec,
    }

    if override_id:
        kwargs.update({
            "override_id": override_id,
            "override_delay_sec": override_delay_sec,
            "override_duration_sec": override_duration_sec,
        })

    autopilot.run_scene_once(**kwargs)

    worked_ok = ask_yes_no("\nВесь сценарий отработал правильно?", True)
    scene_ok = ask_yes_no("Сцена была правильная?", True)
    override_ok = True

    if override_id:
        override_ok = ask_yes_no("Override был правильный?", True)

    timing_ok = ask_yes_no("Тайминги были нормальные?", True)
    energy = input("Energy 0-5 или пусто: ").strip()
    notes = ask_text("Notes", "")

    record = {
        "id": look_id,
        "name": look_name,
        "type": "autopilot_test",
        "scene_id": scene_id,
        "scene_duration_sec": scene_duration_sec,
        "override_id": override_id,
        "override_delay_sec": override_delay_sec,
        "override_duration_sec": override_duration_sec,
        "verified": worked_ok and scene_ok and override_ok and timing_ok,
        "verified_at": datetime.now().isoformat(timespec="seconds"),
        "worked_ok": worked_ok,
        "scene_ok": scene_ok,
        "override_ok": override_ok,
        "timing_ok": timing_ok,
        "energy": int(energy) if energy else None,
        "enabled_after_verification": ask_yes_no("Можно использовать этот look в будущем автопилоте?", worked_ok),
        "notes": notes
    }

    upsert_verified_record(record)

    print(f"\nСохранено в: {CALIBRATION_PATH}")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()