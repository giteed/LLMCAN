#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/client/nc_can_client.py
# ==================================================
# Клиентская часть NeuralChat (CAN).
# Версия: 1.0.5
# - Добавлена проверка зависимостей.
# ==================================================

import sys
import os

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

from LLMCAN.agents.NeuralChat.modules.logging import logger
from LLMCAN.agents.NeuralChat.modules.setup import check_and_install_sqlite, check_sqlite_in_python

# Проверяем и устанавливаем зависимости
check_and_install_sqlite()
check_sqlite_in_python()

logger.info("Клиент NeuralChat запущен.")
