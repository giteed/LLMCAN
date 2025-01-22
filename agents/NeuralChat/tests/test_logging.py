#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/tests/test_logging.py
# ==================================================
# Скрипт для тестирования логирования в NeuralChat.
# Версия: 1.0.7
# - Использование BASE_DIR из settings.py.
# ==================================================

import sys
import os

# Добавляем путь к корневой папке проекта для корректного импорта
from LLMCAN.settings import BASE_DIR
sys.path.append(str(BASE_DIR))

# Импортируем logger из вашего модуля logging
from agents.NeuralChat.modules.logging import logger

logger.info("Тестовое сообщение: Логирование работает!")
logger.error("Тестовое сообщение: Ошибка!")
