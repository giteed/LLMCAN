#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/tests/test_logging.py
# ==================================================
# Скрипт для тестирования логирования в NeuralChat.
# Версия: 1.0.2
# - Исправлен импорт модуля modules.
# ==================================================

import sys
import os

# Добавляем путь к папке modules для корректного импорта
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from modules.logging import logger

logger.info("Тестовое сообщение: Логирование работает!")
logger.error("Тестовое сообщение: Ошибка!")
