# LLMCAN/agents/cognitive_interface_agent_functions.py
# ==================================================
# Функции для Когнитивного интерфейсного агента
# ==================================================

import os
import sys
import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import re
import time
import uuid
import socket
import socks
import readline

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
original_socket = None

# === Функции ===
def check_tor_connection():
    try:
        result = subprocess.run(["torsocks", "curl", "https://check.torproject.org/api/ip"], capture_output=True, text=True, timeout=10)
        if "IsTor\":true" in result.stdout:
            print(f"{Colors.GREEN}Отладка: TOR соединение активно{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}Отладка: TOR соединение неактивно{Colors.RESET}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Отладка: Ошибка проверки TOR соединения: {e}{Colors.RESET}")
        return False

def handle_command(command):
    global USE_TOR
    if command.lower() == '/tor':
        status = "включен" if USE_TOR else "выключен"
        print(f"Режим опроса через TOR: {status}")
    elif command.lower() == '/toron':
        USE_TOR = True
        print("Режим опроса через TOR включен.")
    elif command.lower() == '/toroff':
        USE_TOR = False
        print("Режим опроса через TOR выключен.")
    else:
        print(f"{Colors.RED}Неизвестная команда: {command}{Colors.RESET}")



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

def get_local_ip():
    try:
        return subprocess.check_output("hostname -I | awk '{print $1}'", shell=True).decode().strip()
    except subprocess.CalledProcessError:
        return "Не удалось получить локальный IP"

def check_tor_status():
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

def enable_tor():
    global USE_TOR, original_socket
    if not USE_TOR:
        original_socket = socket.socket
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
        socket.socket = socks.socksocket
        USE_TOR = True
        print("TOR включен.")

def disable_tor():
    global USE_TOR, original_socket
    if USE_TOR and original_socket:
        socket.socket = original_socket
        USE_TOR = False
        print("TOR выключен.")
    else:
        print("TOR уже выключен или не был включен.")

def check_tor_settings():
    try:
        with open('/etc/tor/torrc', 'r') as f:
            content = f.read()
            if 'ExcludeExitNodes' in content:
                print("TOR настроен для исключения определенных выходных узлов.")
        # Проверка настроек torsocks
        torsocks_output = subprocess.check_output(['torsocks', 'show_conf'], universal_newlines=True)
        if 'local = 127.0.0.0/255.0.0.0' in torsocks_output:
            print("torsocks настроен для пропуска локальных адресов.")
    except Exception as e:
        print(f"Не удалось проверить настройки TOR: {e}")


def query_ddgr(search_query):
    global USE_TOR
    command = ["torsocks", "ddgr", "--json", search_query] if USE_TOR else ["ddgr", "--json", search_query]
    
    print(f"{Colors.YELLOW}Отладка: Использование TOR: {'Да' if USE_TOR else 'Нет'}{Colors.RESET}")
    print(f"{Colors.YELLOW}Отладка: Выполняемая команда: {' '.join(command)}{Colors.RESET}")
    
    try:
        result = subprocess.check_output(command, universal_newlines=True)
        print(f"{Colors.GREEN}Отладка: Запрос успешно выполнен{Colors.RESET}")
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении ddgr: {e}")
        print(f"{Colors.RED}Отладка: Ошибка выполнения команды: {e}{Colors.RESET}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при разборе JSON от ddgr: {e}")
        print(f"{Colors.RED}Отладка: Ошибка разбора JSON: {e}{Colors.RESET}")
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
        # Всегда используем прямое соединение для LLM API
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
    if response is None:
        print(f"{Colors.RED}Не удалось получить ответ от LLM. Использую исходный запрос пользователя.{Colors.RESET}")
        return {"queries": [user_input], "instruction": "Обработайте результаты поиска и предоставьте краткий ответ."}
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
    if result and isinstance(result, list) and len(result) > 0:
        print(f"Найдено {len(result)} результатов:")
        for i, item in enumerate(result[:3], 1):  # Выводим первые 3 результата
            title = item.get('title', 'Без названия')
            url = item.get('url', 'URL отсутствует')
            print(f"{i}. {title}\n   {url}\n")
    else:
        print("Нет доступных промежуточных результатов для отображения.")

def process_search_results(results, instruction, user_language):
    print(f"{Colors.YELLOW}Начинаю обобщение и конечный анализ данных...{Colors.RESET}")
    context = f"""Инструкция: {instruction}

Результаты поиска:
{json.dumps(results, ensure_ascii=False, indent=2)}

Обработай результаты согласно инструкции и сформируй ответ в формате Markdown на языке пользователя: {user_language}."""

    response = query_llm(context, include_history=True)
    if response is None:
        print(f"{Colors.RED}Не удалось получить ответ от LLM. Возвращаю необработанные результаты поиска.{Colors.RESET}")
        return json.dumps(results, ensure_ascii=False, indent=2)
    print(f"{Colors.GREEN}Анализ завершен. Формирую ответ...{Colors.RESET}")
    return response

def get_multiline_input():
    prefix = "Вы(tor): " if USE_TOR else "Вы: "
    print(f"{Colors.BLUE}{prefix}{Colors.RESET}", end="")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)

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
    prefix = "Вы(tor): " if USE_TOR else "Вы: "
    print(f"{Colors.BLUE}{prefix}{Colors.RESET}", end="")
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


if __name__ == "__main__":
    main()
