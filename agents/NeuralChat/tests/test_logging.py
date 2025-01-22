#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/tests/test_logging.py
# ==================================================
# Скрипт для тестирования логирования в NeuralChat.
# Версия: 1.0.4
# - Исправлен путь к папке modules.
# ==================================================

import sys
import os

# Добавляем абсолютный путь к папке modules для корректного импорта
modules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules"))
sys.path.append(modules_path)

from logging import logger

logger.info("Тестовое сообщение: Логирование работает!")
logger.error("Тестовое сообщение: Ошибка!")
