# app/__init__.py
"""Инициализация пакета app для DMX Autopilot"""

# Импорт основных подмодулей для удобного доступа
from .core.state import State
from .scenes.scene_manager import SceneManager
from .overrides.override_manager import OverrideManager

# Глобальные объекты или настройки
GLOBAL_CONFIG = {}
def init_globals():
    """Инициализация глобальных переменных и настроек"""
    GLOBAL_CONFIG["start_time"] = "not_started"