# main.py
from fs_tcp import press_override_button, start_sequence, stop_sequence
from scenes import SCENES
import time


def test_override_buttons():
    print("Тест Override Buttons:")
    for name in ["speech", "soft_background", "heads_slow"]:
        print(f"Включаем {name}")
        press_override_button(SCENES[name])
        time.sleep(1)


def test_sequences():
    print("Тест Sequences:")
    print("Старт Sequence 1")
    start_sequence(SCENES["sequence1"])
    time.sleep(2)
    print("Стоп Sequence 1")
    stop_sequence(SCENES["sequence1"])

    print("Старт Sequence 2")
    start_sequence(SCENES["sequence2"])
    time.sleep(2)
    print("Стоп Sequence 2")
    stop_sequence(SCENES["sequence2"])


if __name__ == "__main__":
    test_override_buttons()
    test_sequences()