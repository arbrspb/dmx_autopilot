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

def press_override_button(code: int):
    # нажать кнопку
    send_fs(code, 255)
    time.sleep(0.1)  # пауза 100 мс, FreeStyler успевает зарегистрировать нажатие
    # отпустить кнопку
    send_fs(code, 0)

def start_sequence(code: int):
    """Старт Sequence — используем код как есть"""
    send_fs(code)

def stop_sequence(code: int):
    """Стоп Sequence — к коду добавляем 20 для FreeStyler TCP"""
    send_fs(code + 20)