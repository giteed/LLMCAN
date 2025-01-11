#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 1.2
# ==================================================

import os
import sys
import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import readline
import re

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from settings import BASE_DIR, LLM_API_URL

# === Настройки ===
MODEL = "qwen2:7b"
HISTORY_FILE = BASE_DIR / "data" / "cognitive_agent_history.txt"
MAX_HISTORY_LENGTH = 50
LOG_DIR = BASE_DIR / 'logs'

# === Настройка логирования ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

LOG_DIR.mkdir(exist_ok=True)
file_handler = logging.FileHandler(LOG_DIR / f'cognitive_agent_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# === Цвета для консоли ===
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# === Глобальные переменные ===
dialog_history = []

# === Функции ===
def save_dialog_history():
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding='utf-8') as file:
            json.dump(dialog_history, file, ensure_ascii=False, indent=2)
        logger.info(f"История диалога сохранена в {HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения истории диалога: {e}")

def load_dialog_history():
    global dialog_history
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        try:
            with open(HISTORY_FILE, "r", encoding='utf-8') as file:
                dialog_history = json.load(file)
            logger.info(f"История диалога загружена из {HISTORY_FILE}")
        except Exception as e:
            logger.error(f"Ошибка загрузки истории диалога: {e}")
            dialog_history = []
    else:
        dialog_history = []

# Остальные функции остаются без изменений

# === Основной процесс ===
def main():
    load_dialog_history()
    
    print(f"{Colors.YELLOW}Добро пожаловать в Когнитивный Интерфейсный Агент!{Colors.RESET}")
    print(f"{Colors.YELLOW}Введите 'выход', '/q' или Ctrl+C для завершения.{Colors.RESET}")
    print(f"{Colors.YELLOW}Для поиска используйте ключевые слова 'поищи' или 'найди'.{Colors.RESET}")

    try:
        while True:
            user_input = get_multiline_input()
            
            if user_input.lower() in ['/q', 'выход']:
                print(f"{Colors.GREEN}Сеанс завершен. История сохранена.{Colors.RESET}")
                break
            
            search_results = None
            if is_search_query(user_input):
                search_query = re.sub(r'^(поищи|найди|search|find|look up|google)\s*', '', user_input, flags=re.IGNORECASE)
                search_results = query_ddgr(search_query)
                if search_results:
                    print(f"{Colors.GREEN}Результаты поиска получены.{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Не удалось получить результаты поиска.{Colors.RESET}")

            print_message("Вы", user_input)

            response = query_llm_with_context(user_input, search_results)
            if response:
                print_message("Агент", response)
                
                if needs_update(response):
                    print(f"{Colors.YELLOW}Агент инициирует обновление информации...{Colors.RESET}")
                    search_results = query_ddgr(user_input)
                    if search_results:
                        print(f"{Colors.GREEN}Получена обновленная информация.{Colors.RESET}")
                        response = query_llm_with_context(user_input, search_results)
                        print_message("Агент (обновлено)", response)
            else:
                print_message("Агент", "Извините, произошла ошибка при обработке запроса.")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Сеанс прерван пользователем. История сохранена.{Colors.RESET}")
    finally:
        save_dialog_history()

if __name__ == "__main__":
    main()
