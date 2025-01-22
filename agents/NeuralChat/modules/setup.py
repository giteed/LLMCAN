#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/modules/setup.py
# ==================================================
# Модуль для проверки и установки зависимостей для NeuralChat.
# Версия: 1.0.1
# - Исправлена обработка ошибок при отсутствии SQLite.
# ==================================================

import sys
import os
import subprocess

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

from LLMCAN.agents.NeuralChat.modules.logging import logger

def check_and_install_sqlite():
    """Проверяет и устанавливает SQLite, если версия ниже 3.37.0 или SQLite отсутствует."""
    try:
        # Проверяем, установлен ли SQLite
        try:
            result = subprocess.run(["sqlite3", "--version"], capture_output=True, text=True)
            sqlite_version = result.stdout.strip().split()[0]
            logger.info(f"Текущая версия SQLite: {sqlite_version}")

            # Сравниваем версию
            required_version = "3.37.0"
            if sqlite_version < required_version:
                logger.warning(f"Версия SQLite ниже {required_version}. Начинаем обновление...")
                
                # Обновляем SQLite (для CentOS Stream 8)
                subprocess.run(["sudo", "dnf", "install", "-y", "epel-release"], check=True)
                subprocess.run(["sudo", "dnf", "install", "-y", "sqlite"], check=True)
                
                # Проверяем версию после обновления
                result = subprocess.run(["sqlite3", "--version"], capture_output=True, text=True)
                sqlite_version = result.stdout.strip().split()[0]
                logger.info(f"Обновленная версия SQLite: {sqlite_version}")

            else:
                logger.info("Версия SQLite соответствует требованиям.")

        except FileNotFoundError:
            logger.warning("SQLite не установлен. Начинаем установку...")
            
            # Устанавливаем SQLite (для CentOS Stream 8)
            subprocess.run(["sudo", "dnf", "install", "-y", "epel-release"], check=True)
            subprocess.run(["sudo", "dnf", "install", "-y", "sqlite"], check=True)
            
            # Проверяем версию после установки
            result = subprocess.run(["sqlite3", "--version"], capture_output=True, text=True)
            sqlite_version = result.stdout.strip().split()[0]
            logger.info(f"Установленная версия SQLite: {sqlite_version}")

    except Exception as e:
        logger.error(f"Ошибка при проверке или установке SQLite: {e}")
        raise

def check_sqlite_in_python():
    """Проверяет версию SQLite, используемую в Python."""
    try:
        import sqlite3
        logger.info(f"Версия SQLite в Python: {sqlite3.sqlite_version}")
    except Exception as e:
        logger.error(f"Ошибка при проверке версии SQLite в Python: {e}")
        raise
