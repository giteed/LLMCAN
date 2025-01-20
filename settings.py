#!/usr/bin/env python3
# LLMCAN/settings.py
# ===========================================
# Настройки проекта LLMCAN
# ===========================================
# Этот файл содержит основные настройки проекта, включая пути к файлам,
# директориям, конфигурациям, а также глобальные параметры.
# Он централизует все важные переменные для упрощения поддержки проекта.
# ВАЖНО: Все пути и параметры следует указывать относительно BASE_DIR.
# ===========================================
# Логирование:
# Для управления логированием в проекте используется модуль logging.
# Вы можете изменить уровень логирования через переменную LOG_LEVEL:
# - DEBUG: Вывод всех сообщений, включая отладочные.
# - INFO: Основные действия без отладочных сообщений.
# - WARNING: Только предупреждения и ошибки.
# - ERROR: Только ошибки.
# Логи записываются как в консоль, так и в файл, путь к которому указан в LOG_FILE_PATH.
#
# Версия: 1.2 (2025-01-09)

import logging
import os
from pathlib import Path


# Определяем базовый путь к корню проекта LLMCAN
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR  # Путь к директории LLMCAN

# URL для API LLM модели
LLM_API_URL = "http://10.67.67.2:11434/api/generate"

# Указать путь для логов
LOG_FILE_PATH = os.getenv("LLMCAN_LOG_PATH", "./data/logs/llmcan.log")

# Конфигурация логирования
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': logging.DEBUG,
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': LOG_FILE_PATH,
            'level': logging.DEBUG,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': logging.DEBUG,
    },
}

# Применение конфигурации
logging.config.dictConfig(LOGGING_CONFIG)

# Указание уровня логирования для дополнительных модулей
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Проверка логгера
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Логирование успешно настроено.")
