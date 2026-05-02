# app/__init__.py
"""Инициализация пакета app для DMX Autopilot"""

# Импортируем основные подмодули, чтобы можно было импортировать из app сразу
from .core.state import State
from .scenes.scene_manager import SceneManager
from .overrides.override_manager import OverrideManager

# Тут можно добавлять глобальные объекты, логирование или функции инициализации