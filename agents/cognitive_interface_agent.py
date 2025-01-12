#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 1.3
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
MODEL = "llama3:latest"
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

def query_ddgr(search_query):
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

def generate_system_instruction(context):
    return ("Ты когнитивный агент, способный анализировать информацию и отвечать на вопросы пользователя. "
            "Всегда учитывай текущую дату и время при анализе информации. "
            "Если ты чувствуешь, что информация может быть устаревшей, рассмотри необходимость ее обновления через поиск.")

def get_current_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def query_llm_with_context(user_input, search_results=None):
    global dialog_history
    
    current_datetime = get_current_datetime()
    system_instruction = generate_system_instruction(dialog_history)
    
    context = f"Текущая дата и время: {current_datetime}\n"
    context += f"Инструкция: {system_instruction}\n"
    
    if search_results:
        context += f"Результаты поиска: {json.dumps(search_results, ensure_ascii=False)}\n"
    
    context += f"Запрос пользователя: {user_input}"
    
    dialog_history.append({"role": "user", "content": user_input})
    
    payload = {
        "model": MODEL,
        "prompt": context,
        "stream": False
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()
        model_response = response.json().get("response", "<Нет ответа>")
        dialog_history.append({"role": "assistant", "content": model_response})
        save_dialog_history()
        return model_response
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к модели: {e}")
        return None

def is_search_query(user_input):
    search_keywords = ["поищи", "найди", "search", "find", "look up", "google"]
    return any(keyword in user_input.lower() for keyword in search_keywords)

def print_message(role, message):
    color = Colors.BLUE if role == "Вы" else Colors.GREEN
    print(f"\n{color}┌─ {role}:{Colors.RESET}")
    print(f"│ {message}")
    print("└" + "─" * 50)

def get_multiline_input():
    print(f"{Colors.BLUE}Вы (введите пустую строку для завершения ввода):{Colors.RESET}")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)

def needs_update(response):
    update_keywords = ["устарело", "неактуально", "нужно обновить", "требует проверки"]
    return any(keyword in response.lower() for keyword in update_keywords)

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
