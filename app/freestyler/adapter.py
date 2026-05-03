import socket
import time

HOST = "127.0.0.1"
PORT = 3332


def send_fs(code: int, value: int = 255, arg: int = 0):
    cmd = f"FSOC{code:03d}{value:03d}{arg:03d}"

    try:
        with socket.create_connection((HOST, PORT), timeout=2) as s:
            s.sendall(cmd.encode("ascii"))

        print("Sent:", cmd)

    except Exception as e:
        print("Error sending command:", e)


def press_button(code: int, press_sec: float = 0.1):
    send_fs(code, 255)
    time.sleep(press_sec)
    send_fs(code, 0)


def hold_button(code: int, duration_sec: float):
    send_fs(code, 255)
    time.sleep(duration_sec)
    send_fs(code, 0)


def pulse_button(code: int, duration_sec: float = 0.1):
    press_button(code, duration_sec)


def start_sequence(start_code: int):
    send_fs(start_code, 255)


def stop_sequence(stop_code: int):
    send_fs(stop_code, 255)