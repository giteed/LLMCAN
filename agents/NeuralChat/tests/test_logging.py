#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/tests/test_logging.py
# ==================================================
# Скрипт для тестирования логирования в NeuralChat.
# Версия: 1.0.8
# - Исправлен импорт модуля LLMCAN.
# ==================================================

import sys
import os

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

# Импортируем BASE_DIR и logger
from settings import BASE_DIR  # Импортируем BASE_DIR из settings.py
from NeuralChat.modules.logging import logger  # Измените импорт на NeuralChat.modules.logging

logger.info("Тестовое сообщение: Логирование работает!")
logger.error("Тестовое сообщение: Ошибка!")




print("Project root:", project_root)
print("sys.path:", sys.path)

