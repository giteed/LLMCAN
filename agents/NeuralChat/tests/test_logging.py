#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/tests/test_logging.py
# ===========================================
# Скрипт для тестирования логирования в NeuralChat.
# ===========================================
# Версия: 1.0 (2023-10-10)
# - Первоначальная реализация.
# ===========================================

import sys
import os

# Добавляем путь к корневой папке проекта для корректного импорта
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from modules.logging import logger

logger.info("Тестовое сообщение: Логирование работает!")
logger.error("Тестовое сообщение: Ошибка!")
