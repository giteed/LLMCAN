#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/modules/logging.py
# ==================================================
# Модуль для централизованного логирования в NeuralChat.
# Версия: 1.0.1
# - Исправлен импорт модуля LLMCAN.
# ==================================================

import sys
import os

# Добавляем путь к корневой папке проекта для корректного импорта
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

import logging
from LLMCAN.settings import LOGGING_CONFIG

# Применяем конфигурацию логирования из основного проекта
logging.config.dictConfig(LOGGING_CONFIG)

# Создаем логгер для NeuralChat
logger = logging.getLogger("NeuralChat")
