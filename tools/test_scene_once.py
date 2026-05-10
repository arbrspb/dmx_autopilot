import json
import sys
import time
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.state import State
from app.scenes.scene_manager import SceneManager


CONFIG_PATH = PROJECT_ROOT / "app" / "config" / "scenes.json"
CALIBRATION_PATH = PROJECT_ROOT / "app" / "config" / "calibration" / "scenes_verified.json"


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


def ask_int(prompt: str, default: int) -> int:
    value = input(f"{prompt} [{default}]: ").strip()

    if not value:
        return default

    return int(value)


def ask_float(prompt: str, default: float) -> float:
    value = input(f"{prompt} [{default}]: ").strip()

    if not value:
        return default

    return float(value.replace(",", "."))


def find_scene(scenes_config: dict, scene_id: str) -> dict | None:
    for scene in scenes_config.get("scenes", []):
        if scene.get("id") == scene_id:
            return scene

    return None


def upsert_verified_record(record: dict) -> None:
    data = load_json(CALIBRATION_PATH, {"scenes": []})
    records = data.setdefault("scenes", [])

    record_id = record["id"]

    for index, existing in enumerate(records):
        if existing.get("id") == record_id:
            records[index] = record
            save_json(CALIBRATION_PATH, data)
            return

    records.append(record)
    save_json(CALIBRATION_PATH, data)


def create_manual_scene(scene_id: str) -> dict:
    print("\nСцена не найдена в app/config/scenes.json.")
    print("Можно создать проверочную запись вручную.\n")

    name = ask_text("Название сцены во FreeStyler", scene_id)
    page = ask_text("Page / вкладка", "ALL")
    slot = ask_int("Slot / позиция сцены", 1)

    start_code = ask_int("Start code", 505 + (slot - 1))
    stop_code = ask_int("Stop code", start_code + 20)

    program_type = ask_text("Program type: movement/color/strobe/combo/utility", "movement")
    fixture_group = ask_text("Fixture group", "unknown")
    movement = ask_text("Movement", "")
    color = ask_text("Color", "")
    energy = ask_int("Energy 0-5", 3)
    default_duration_sec = ask_float("Default duration sec", 10.0)

    return {
        "id": scene_id,
        "name": name,
        "freestyler_name": name,
        "page": page,
        "slot": slot,
        "type": "sequence",
        "program_type": program_type,
        "fixture_group": fixture_group,
        "movement": movement or None,
        "color": color or None,
        "strobe": program_type == "strobe",
        "energy": energy,
        "start_code": start_code,
        "stop_code": stop_code,
        "default_duration_sec": default_duration_sec,
        "enabled": False,
        "notes": "Created from test_scene_once.py"
    }


def main():
    print("=== DMX Autopilot / Test Scene Once ===\n")

    scenes_config = load_json(CONFIG_PATH, {"scenes": []})

    scene_id = ask_text("Введите scene id, например pr11_speed_max")
    scene = find_scene(scenes_config, scene_id)

    if scene is None:
        scene = create_manual_scene(scene_id)

    print("\n--- Scene config ---")
    print(json.dumps(scene, ensure_ascii=False, indent=2))

    state = State()
    scene_manager = SceneManager(state)

    command_tested = ask_yes_no("\nТестировать командой Python?", True)

    started_ok = False
    stopped_ok = False

    if command_tested:
        input("\nНажми Enter, чтобы ЗАПУСТИТЬ сцену...")
        scene_manager.start_scene(scene_id)

        started_ok = ask_yes_no("Запустилась правильная сцена?", True)

        wait_sec = ask_float("Сколько секунд подержать перед остановкой", 3.0)
        print(f"Ждём {wait_sec} сек...")
        time.sleep(wait_sec)

        input("\nНажми Enter, чтобы ОСТАНОВИТЬ сцену...")
        scene_manager.stop_scene(scene_id)

        stopped_ok = ask_yes_no("Сцена остановилась правильно?", True)
    else:
        print("\nРучной режим.")
        input("Вручную запусти сцену во FreeStyler, потом нажми Enter...")
        started_ok = ask_yes_no("Запустилась правильная сцена?", True)

        input("Вручную останови сцену во FreeStyler, потом нажми Enter...")
        stopped_ok = ask_yes_no("Сцена остановилась правильно?", True)

    verified = started_ok and stopped_ok
    enable_in_work_config = ask_yes_no("Можно считать сцену проверенной и enabled=true?", verified)

    program_type = ask_text("Program type", scene.get("program_type", "movement"))
    fixture_group = ask_text("Fixture group", scene.get("fixture_group", "unknown"))
    energy = ask_int("Energy 0-5", int(scene.get("energy", 3)))
    notes = ask_text("Notes", scene.get("notes", ""))

    record = dict(scene)
    record.update({
        "program_type": program_type,
        "fixture_group": fixture_group,
        "energy": energy,
        "verified": verified,
        "verified_at": datetime.now().isoformat(timespec="seconds"),
        "command_tested": command_tested,
        "started_ok": started_ok,
        "stopped_ok": stopped_ok,
        "enabled_after_verification": enable_in_work_config,
        "notes": notes
    })

    upsert_verified_record(record)

    print(f"\nСохранено в: {CALIBRATION_PATH}")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()