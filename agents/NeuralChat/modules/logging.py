#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/modules/logging.py
# ==================================================
# Модуль для централизованного логирования в NeuralChat.
# Версия: 1.0.6
# - Исправлен импорт модуля LLMCAN.
# ==================================================

import sys
import os

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

import logging
from LLMCAN.settings import LOGGING_CONFIG

# Применяем конфигурацию логирования из основного проекта
logging.config.dictConfig(LOGGING_CONFIG)

# Создаем логгер для NeuralChat
logger = logging.getLogger("NeuralChat")
