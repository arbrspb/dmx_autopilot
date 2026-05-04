import socket
import time


HOST = "127.0.0.1"
PORT = 3332

DEFAULT_PRESS_SEC = 0.1


def send_fs(code: int, value: int = 255, arg: int = 0) -> bool:
    """
    Отправляет команду FreeStyler TCP.

    Формат:
    FSOC + code(3) + value(3) + arg(3)

    Пример:
    FSOC066255000
    """
    cmd = f"FSOC{int(code):03d}{int(value):03d}{int(arg):03d}"

    try:
        with socket.create_connection((HOST, PORT), timeout=2) as s:
            s.sendall(cmd.encode("ascii"))
        print(f"[FreeStylerAdapter] Sent: {cmd}")
        return True
    except Exception as e:
        print(f"[FreeStylerAdapter] Error sending command {cmd}: {e}")
        return False


def press_button(code: int, press_sec: float = DEFAULT_PRESS_SEC) -> None:
    """
    Короткое нажатие кнопки:
    нажать -> подождать -> отпустить.
    """
    send_fs(code, 255)
    time.sleep(press_sec)
    send_fs(code, 0)


def hold_button(code: int, duration: float) -> None:
    """
    Удержание кнопки:
    нажать -> держать duration секунд -> отпустить.
    """
    duration = max(0.0, float(duration))

    send_fs(code, 255)
    time.sleep(duration)
    send_fs(code, 0)


def pulse_button(code: int, duration: float = DEFAULT_PRESS_SEC) -> None:
    """
    Короткий импульс. Пока то же самое, что hold_button,
    но оставляем отдельной функцией для будущей логики pulse.
    """
    hold_button(code, duration)


def start_sequence(start_code: int) -> None:
    """
    Запуск sequence/cuelist по точному start_code.
    """
    send_fs(start_code, 255)


def stop_sequence(stop_code: int) -> None:
    """
    Остановка sequence/cuelist по точному stop_code.

    В текущей схеме stop_code обычно = start_code + 20.
    Но вычислять это лучше выше, в SceneManager.
    """
    send_fs(stop_code, 255)