#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/server/nc_can_server.py
# ==================================================
# Серверная часть NeuralChat (CAN).
# Версия: 1.0.4
# - Исправлен импорт модуля LLMCAN.
# ==================================================

import sys
import os

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

from LLMCAN.agents.NeuralChat.modules.logging import logger

logger.info("Сервер NeuralChat запущен.")
