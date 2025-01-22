#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/modules/logging.py
# ===========================================
# Модуль для централизованного логирования в NeuralChat.
# Использует настройки из LLMCAN/settings.py.
# ===========================================
# Версия: 1.0 (2023-10-10)
# - Первоначальная реализация.
# ===========================================

import logging
from LLMCAN.settings import LOGGING_CONFIG

# Применяем конфигурацию логирования из основного проекта
logging.config.dictConfig(LOGGING_CONFIG)

# Создаем логгер для NeuralChat
logger = logging.getLogger("NeuralChat")

# Пример использования:
# logger.info("Это тестовое сообщение.")
