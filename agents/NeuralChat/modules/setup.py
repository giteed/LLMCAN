#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/modules/setup.py
# ==================================================
# Модуль для проверки и установки зависимостей для NeuralChat.
# Версия: 1.0.2
# - Добавлена сборка SQLite из исходников.
# ==================================================

import sys
import os
import subprocess
import tempfile
import shutil

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

from LLMCAN.agents.NeuralChat.modules.logging import logger

def check_sqlite_in_python():
    """Проверяет версию SQLite, используемую в Python."""
    try:
        import sqlite3
        logger.info(f"Версия SQLite в Python: {sqlite3.sqlite_version}")

        # Проверяем, совпадает ли версия SQLite в Python с системной
        result = subprocess.run(["sqlite3", "--version"], capture_output=True, text=True)
        system_sqlite_version = result.stdout.strip().split()[0]

        if sqlite3.sqlite_version != system_sqlite_version:
            logger.warning(f"Версия SQLite в Python ({sqlite3.sqlite_version}) не совпадает с системной ({system_sqlite_version}).")
            logger.warning("Для использования новой версии SQLite пересоберите Python или используйте внешнюю библиотеку.")
        else:
            logger.info("Версия SQLite в Python совпадает с системной.")

    except Exception as e:
        logger.error(f"Ошибка при проверке версии SQLite в Python: {e}")
        raise


def check_sqlite_in_python():
    """Проверяет версию SQLite, используемую в Python."""
    try:
        import sqlite3
        logger.info(f"Версия SQLite в Python: {sqlite3.sqlite_version}")
    except Exception as e:
        logger.error(f"Ошибка при проверке версии SQLite в Python: {e}")
        raise
