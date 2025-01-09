#!/usr/bin/env python3
# ai_assistant/scripts/chat_with_ddgr_context.py
# ==================================================
# Скрипт для взаимодействия с LLM-моделью с учетом
# сохранения контекста диалога и использования ddgr.
# Версия: 2.0
# ==================================================

import requests
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import readline  # Для поддержки навигации и редактирования в консоли

import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from myproject import settings



# === Настройка путей ===
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Импорт настроек проекта
try:
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    print(f"Ошибка импорта settings: {e}")
    sys.exit(1)

# === Настройки ===
MODEL = "qwen2:7b"  # Имя модели для обработки
HISTORY_FILE = BASE_DIR / "ai_assistant/context/context_history.txt"
MAX_HISTORY_LENGTH = 50  # Максимальное количество сообщений в истории

# Цвета для чата
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    RESET = "\033[0m"

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/chat_with_context_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# === Глобальная переменная для хранения истории ===
dialog_history = []

# === Функции ===
def save_dialog_history():
    """Сохраняет историю диалога в текстовый файл."""
    try:
        with open(HISTORY_FILE, "w") as file:
            file.write("\n".join(dialog_history))
        logger.info(f"История диалога сохранена в {HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения истории диалога: {e}")

def load_dialog_history():
    """Загружает историю диалога из текстового файла."""
    global dialog_history
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        try:
            with open(HISTORY_FILE, "r") as file:
                dialog_history = file.read().splitlines()
            logger.info(f"История диалога загружена из {HISTORY_FILE}")
        except Exception as e:
            logger.error(f"Ошибка загрузки истории диалога: {e}")
            dialog_history = []
    else:
        dialog_history = []

def query_ddgr(search_query):
    """Выполняет поиск с помощью ddgr и возвращает результаты в формате JSON."""
    command = ["ddgr", "--json", search_query]
    try:
        result = subprocess.check_output(command, universal_newlines=True)
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении ddgr: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при разборе JSON от ddgr: {e}")
        return None

def query_llm_with_context(user_input, search_results=None):
    """Отправляет запрос в LLM с учетом истории диалога и результатов поиска."""
    global dialog_history

    # Если есть результаты поиска, добавляем их в начало истории
    if search_results:
        dialog_history.insert(0, f"Результаты поиска: {json.dumps(search_results, ensure_ascii=False)}")

    # Добавляем сообщение пользователя в историю
    dialog_history.append(f"Вы: {user_input}")
    if len(dialog_history) > MAX_HISTORY_LENGTH * 2:
        dialog_history = dialog_history[-MAX_HISTORY_LENGTH * 2:]

    payload = {
        "model": MODEL,
        "prompt": "\n".join(dialog_history),
        "stream": False
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()

        # Получаем ответ от модели
        model_response = response.json().get("response", "<Нет ответа>")
        dialog_history.append(f"Ассистент: {model_response}")

        # Сохраняем историю
        save_dialog_history()

        return model_response
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к модели: {e}")
        return None

# === Основной процесс ===
if __name__ == "__main__":
    load_dialog_history()

    print("Добро пожаловать в чат с LLM! Введите 'выход' для завершения.")

    try:
        while True:
            search_query = input(f"{Colors.BLUE}Введите поисковый запрос (или 'пропустить'): {Colors.WHITE}")
            if search_query.lower() == "выход":
                print(f"{Colors.GREEN}Чат завершен. История сохранена.{Colors.RESET}")
                break
            
            search_results = None
            if search_query.lower() != "пропустить":
                search_results = query_ddgr(search_query)
                if search_results:
                    print(f"{Colors.GREEN}Результаты поиска получены.{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Не удалось получить результаты поиска.{Colors.RESET}")

            user_input = input(f"{Colors.BLUE}Вы: {Colors.WHITE}")
            if user_input.lower() == "выход":
                print(f"{Colors.GREEN}Чат завершен. История сохранена.{Colors.RESET}")
                break

            response = query_llm_with_context(user_input, search_results)
            if response:
                print(f"{Colors.GREEN}Ассистент:{Colors.GRAY} {response}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}Ассистент:{Colors.GRAY} Ошибка: ответ от модели отсутствует.{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Чат прерван пользователем. История сохранена.{Colors.RESET}")
        save_dialog_history()
        sys.exit(0)
