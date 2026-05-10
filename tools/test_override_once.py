import json
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.state import State
from app.overrides.override_manager import OverrideManager


CONFIG_PATH = PROJECT_ROOT / "app" / "config" / "overrides.json"
CALIBRATION_PATH = PROJECT_ROOT / "app" / "config" / "calibration" / "overrides_verified.json"


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


def ask_int(prompt: str, default: int) -> int:
    value = input(f"{prompt} [{default}]: ").strip()

    if not value:
        return default

    return int(value)


def find_override(overrides_config: dict, override_id: str) -> dict | None:
    for override in overrides_config.get("overrides", []):
        if override.get("id") == override_id:
            return override

    return None


def upsert_verified_record(record: dict) -> None:
    data = load_json(CALIBRATION_PATH, {"overrides": []})
    records = data.setdefault("overrides", [])

    record_id = record["id"]

    for index, existing in enumerate(records):
        if existing.get("id") == record_id:
            records[index] = record
            save_json(CALIBRATION_PATH, data)
            return

    records.append(record)
    save_json(CALIBRATION_PATH, data)


def create_manual_override(override_id: str) -> dict:
    print("\nOverride не найден в app/config/overrides.json.")
    print("Можно создать проверочную запись вручную.\n")

    name = ask_text("Название кнопки во FreeStyler", override_id)
    tab = ask_int("Номер вкладки override", 1)
    slot = ask_int("Slot / позиция кнопки", 1)
    code = ask_int("Code", 66 + (slot - 1))
    override_type = ask_text("Type: hold/toggle/pulse/timed", "toggle")
    category = ask_text("Category", "unknown")
    fixture_group = ask_text("Fixture group", "unknown")
    energy = ask_int("Energy 0-5", 3)

    override = {
        "id": override_id,
        "name": name,
        "freestyler_name": name,
        "tab": tab,
        "slot": slot,
        "type": override_type,
        "code": code,
        "category": category,
        "fixture_group": fixture_group,
        "energy": energy,
        "enabled": False,
        "notes": "Created from test_override_once.py"
    }

    if override_type == "hold":
        override["duration"] = ask_float("Default hold duration", 1.0)

    return override


def main():
    print("=== DMX Autopilot / Test Override Once ===\n")

    overrides_config = load_json(CONFIG_PATH, {"overrides": []})

    override_id = ask_text("Введите override id, например blender или gobo_3_pol")
    override = find_override(overrides_config, override_id)

    if override is None:
        override = create_manual_override(override_id)

    print("\n--- Override config ---")
    print(json.dumps(override, ensure_ascii=False, indent=2))

    state = State()
    override_manager = OverrideManager(state)

    mode = override.get("type", "toggle")
    code = override.get("code")

    if code is None:
        print("\nУ override нет code. Тест команды невозможен.")
        command_tested = False
        activated_ok = False
        deactivated_ok = False
    else:
        command_tested = ask_yes_no("\nТестировать командой Python?", True)

        activated_ok = False
        deactivated_ok = False

        if command_tested:
            if mode == "hold":
                default_duration = float(override.get("duration", override.get("duration_sec", 1.0)))
                duration = ask_float("Сколько секунд удерживать", default_duration)

                input("\nНажми Enter, чтобы УДЕРЖАТЬ override...")
                try:
                    override_manager.activate_override(override_id, duration_sec=duration)
                except TypeError:
                    print("activate_override не поддерживает duration_sec, используется duration из JSON.")
                    override_manager.activate_override(override_id)

                activated_ok = ask_yes_no("Эффект сработал правильно?", True)
                deactivated_ok = ask_yes_no("После отпускания эффект прекратился/погас правильно?", True)

            elif mode == "toggle":
                input("\nНажми Enter, чтобы ВКЛЮЧИТЬ toggle override...")
                override_manager.activate_override(override_id)
                activated_ok = ask_yes_no("Эффект включился правильно?", True)

                input("\nНажми Enter, чтобы ВЫКЛЮЧИТЬ toggle override...")
                override_manager.deactivate_override(override_id)
                deactivated_ok = ask_yes_no("Эффект выключился правильно?", True)

            else:
                print(f"\nТип '{mode}' пока тестируется как обычный activate_override.")
                input("Нажми Enter, чтобы активировать...")
                override_manager.activate_override(override_id)
                activated_ok = ask_yes_no("Сработало правильно?", True)
                deactivated_ok = ask_yes_no("Отключение/завершение корректное?", True)
        else:
            print("\nРучной режим.")
            input("Вручную проверь кнопку во FreeStyler, потом нажми Enter...")
            activated_ok = ask_yes_no("Кнопка/эффект соответствует описанию?", True)
            deactivated_ok = ask_yes_no("Отключение/завершение корректное?", True)

    verified = activated_ok and deactivated_ok
    enable_in_work_config = ask_yes_no("Можно считать кнопку проверенной и enabled=true?", verified)

    notes = ask_text("Notes", override.get("notes", ""))

    record = dict(override)
    record.update({
        "verified": verified,
        "verified_at": datetime.now().isoformat(timespec="seconds"),
        "command_tested": command_tested,
        "activated_ok": activated_ok,
        "deactivated_ok": deactivated_ok,
        "enabled_after_verification": enable_in_work_config,
        "notes": notes
    })

    upsert_verified_record(record)

    print(f"\nСохранено в: {CALIBRATION_PATH}")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()