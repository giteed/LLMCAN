Вот полный код скрипта cognitive_interface_agent.py с учетом предыдущего варианта и внесенных изменений:

```python
#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 2.1
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
import time
import uuid
import stem
import stem.connection
from stem import Signal
from stem.control import Controller
import socks

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from settings import BASE_DIR, LLM_API_URL

# === Настройки ===
MODEL = "qwen2:7b"
HISTORY_FILE = BASE_DIR / "data" / "cognitive_agent_history.txt"
TEMP_DIR = BASE_DIR / "temp"
REPORT_FILE = BASE_DIR / "data" / "cognitive_agent_reports.txt"
MAX_HISTORY_LENGTH = 50
LOG_DIR = BASE_DIR / 'logs'
DELAY_BETWEEN_REQUESTS = 5  # секунды

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
USE_TOR = False

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

def setup_tor_session():
    session = requests.session()
    session.proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }
    return session

def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def query_ddgr_tor(search_query):
    session = setup_tor_session()
    try:
        response = session.get(f"https://ddg-api.herokuapp.com/search?q={search_query}")
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса через TOR: {e}")
        return None

def query_ddgr(search_query):
    if USE_TOR:
        return query_ddgr_tor(search_query)
    else:
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
    current_datetime = get_current_datetime()
    return (f"Ты когнитивный агент, работающий в режиме реального времени. "
            f"Текущая дата и время: {current_datetime}. "
            f"Всегда используй эту информацию при ответах на вопросы, связанные с временем. "
            f"Если тебе нужно уточнить время, ты можешь запросить его у системы. "
            f"Анализируй информацию и отвечай на вопросы пользователя. "
            f"Если ты чувствуешь, что информация может быть устаревшей, рассмотри необходимость ее обновления через поиск.")

def get_current_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')

def query_llm(prompt, include_history=True):
    global dialog_history
    
    current_datetime = get_current_datetime()
    
    if include_history:
        context = "\n".join([f"{entry['role']}: {entry['content']}" for entry in dialog_history[-5:]])
        full_prompt = f"Текущая дата и время: {current_datetime}\n\n{context}\n\nСистемная инструкция: {generate_system_instruction(dialog_history)}\n\nТекущий запрос: {prompt}"
    else:
        full_prompt = f"Текущая дата и время: {current_datetime}\n\n{prompt}"

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "<Нет ответа>")
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к модели: {e}")
        return None

def preprocess_query(user_input):
    print(f"{Colors.YELLOW}Запрос пользователя получен. Начинаю анализ и формирование поисковых запросов...{Colors.RESET}")
    system_prompt = """Проанализируй запрос пользователя, исправь возможные ошибки и сформулируй до трех связанных поисковых запросов для расширения контекста. Также создай инструкцию для обработки результатов поиска.

Формат ответа:
Основной запрос: [исправленный запрос пользователя]
Дополнительные запросы:
1. [запрос 1]
2. [запрос 2]
3. [запрос 3] (если необходимо)

Инструкция для обработки результатов:
[Детальная инструкция по обработке и форматированию результатов поиска]"""

    context = f"Запрос пользователя: {user_input}\n\n{system_prompt}"
    response = query_llm(context, include_history=False)
    preprocessed = parse_preprocessing_response(response)
    
    print(f"{Colors.YELLOW}Анализ завершен. Сформированы следующие запросы:{Colors.RESET}")
    for i, query in enumerate(preprocessed['queries'], 1):
        print(f"{Colors.YELLOW}{i}. {query}{Colors.RESET}")
    return preprocessed

def parse_preprocessing_response(response):
    lines = response.split('\n')
    queries = []
    instruction = ""
    parsing_instruction = False

    for line in lines:
        if line.startswith("Основной запрос:"):
            queries.append(line.split(": ", 1)[1].strip())
        elif line.startswith("Дополнительные запросы:"):
            continue
        elif line.startswith(("1. ", "2. ", "3. ")):
            queries.append(line.split(". ", 1)[1].strip())
        elif line.startswith("Инструкция для обработки результатов:"):
            parsing_instruction = True
        elif parsing_instruction:
            instruction += line + "\n"

    return {
        "queries": queries[:3],  # Ограничиваем количество запросов до 3
        "instruction": instruction.strip()
    }

def perform_search(queries):
    results = []
    for i, query in enumerate(queries, 1):
        print(f"{Colors.YELLOW}Отправляю запрос {i}: {query}{Colors.RESET}")
        result = query_ddgr(query)
        if result:
            print(f"{Colors.GREEN}Ответ на запрос {i} получен. Обрабатываю...{Colors.RESET}")
            results.append(result)
            save_temp_result(result, i)
            process_intermediate_result(result, i)
        else:
            print(f"{Colors.RED}Не удалось получить результаты для запроса {i}{Colors.RESET}")
        if i < len(queries):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    return results

def save_temp_result(result, query_number):
    TEMP_DIR.mkdir(exist_ok=True)
    file_path = TEMP_DIR / f"result_{query_number}_{uuid.uuid4()}.json"
    with open(file_path, "w", encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

def process_intermediate_result(result, query_number):
    print(f"{Colors.GREEN}Промежуточный результат для запроса {query_number}:{Colors.RESET}")
    # Здесь можно добавить логику обработки промежуточных результатов
    # Например, вывести краткую сводку или наиболее релевантные данные

def process_search_results(results, instruction, user_language):
    print(f"{Colors.YELLOW}Начинаю обобщение и конечный анализ данных...{Colors.RESET}")
    context = f"""Инструкция: {instruction}

Результаты поиска:
{json.dumps(results, ensure_ascii=False, indent=2)}

Обработай результаты согласно инструкции и сформируй ответ в формате Markdown на языке пользователя: {user_language}."""

    response = query_llm(context, include_history=True)
    print(f"{Colors.GREEN}Анализ завершен. Формирую ответ...{Colors.RESET}")
    return response

def format_response_with_references(response, references):
    formatted_response = response
    for i, ref in enumerate(references, 1):
        formatted_response = formatted_response.replace(f'[{i}]', f'[{i}]({ref})')
    
    formatted_response += "\n\n**Источники:**\n"
    for i, ref in enumerate(references, 1):
        formatted_response += f"{i}. {ref}\n"
    
    return formatted_response

def print_message(role, message):
    color = Colors.BLUE if role == "Вы" else Colors.GREEN
    print(f"\n{color}┌─ {role}:{Colors.RESET}")
    print(f"│ {message.replace('  ', '  │ ')}")
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

def save_report(preprocessed, response):
    with open(REPORT_FILE, "a", encoding='utf-8') as file:
        file.write(f"Дата и время: {get_current_datetime()}\n")
        file.write(f"Запросы:\n{json.dumps(preprocessed['queries'], ensure_ascii=False, indent=2)}\n")
        file.write(f"Инструкция:\n{preprocessed['instruction']}\n")
        file.write(f"Ответ модели:\n{response}\n")
        file.write("-" * 50 + "\n")

def detect_language(text):
    if re.search('[а-яА-Я]', text):
        return 'ru'
    else:
        return 'en'

# === Основной процесс ===
def main():
    global USE_TOR
    load_dialog_history()
    
    print(f"{Colors.YELLOW}Добро пожаловать в Когнитивный Интерфейсный Агент!{Colors.RESET}")
    print(f"{Colors.YELLOW}Введите 'выход', '/q' или Ctrl+C для завершения.{Colors.RESET}")
    print(f"{Colors.YELLOW}Для поиска используйте ключевые слова 'поищи' или 'найди'.{Colors.RESET}")
    print(f"{Colors.YELLOW}Используйте /toron для включения TOR и /toroff для выключения.{Colors.RESET}")

    try:
        while True:
            user_input = get_multiline_input()
            
            if user_input.lower() in ['/q', 'выход']:
                print(f"{Colors.GREEN}Сеанс завершен. История сохранена.{Colors.RESET}")
                break
            elif user_input.lower() == '/toron':
                USE_TOR = True
                print(f"{Colors.GREEN}TOR включен.{Colors.RESET}")
                continue
            elif user_input.lower() == '/toroff':
                USE_TOR = False
                print(f"{Colors.GREEN}TOR выключен.{Colors.RESET}")
                continue
            
            print(f"{Colors.YELLOW}Обрабатываю запрос пользователя...{Colors.RESET}")
            preprocessed = preprocess_query(user_input)

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45218807/79479645-1870-4208-b17b-a7c7a41bd8a8/paste.txt
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45218807/3ecd27c9-966a-4339-8cdc-b9577c1dc8e1/paste-2.txt
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45218807/e3853535-0d6c-40ac-913d-40def3e91e43/paste-3.txt
