#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/tests/test_logging.py
# ==================================================
# Скрипт для тестирования логирования в NeuralChat.
# Версия: 1.0.8
# - Исправлен импорт модуля LLMCAN.
# ==================================================


import os
import sys
import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import readline  # Для поддержки навигации и редактирования в консоли
import re





import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

# Импортируем BASE_DIR и logger
from settings import BASE_DIR
from agents.NeuralChat.modules.logging import logger

logger.info("Тестовое сообщение: Логирование работает!")
logger.error("Тестовое сообщение: Ошибка!")
