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
from agents.install_tor import restart_tor_and_check_ddgr
from colors import Colors  # Используем Colors из внешнего файла
from agents.data_management import save_dialog_history, load_dialog_history

# === Настройки ===
MODEL = "qwen2:7b"
LOG_DIR = BASE_DIR / 'logs'
# Настройка логирования
#DEFAULT_LOG_LEVEL = "INFO"
ENV_FILE = Path(".env")


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



def set_log_level(level):
    global logger
    logging.getLogger().setLevel(level)
    logger.info(f"Уровень логирования установлен на {level}")
    # Сохраняем настройку в .env
    with open(ENV_FILE, "w") as file:
        file.write(f"LOG_LEVEL={level}\n")


def show_help():
    print(f"{Colors.CYAN}Доступные команды:{Colors.RESET}")
    print(f"  {Colors.CYAN}/help, /h{Colors.RESET} - показать эту справку")
    print(f"  {Colors.CYAN}/tor, /t{Colors.RESET} - показать статус TOR")
    print(f"  {Colors.CYAN}/tn{Colors.RESET} - включить TOR")
    print(f"  {Colors.CYAN}/tf{Colors.RESET} - отключить TOR")
    print(f"  {Colors.CYAN}/DEBUG, /INFO, /ERROR{Colors.RESET} - установить уровень логирования")
    print(f"  {Colors.CYAN}/exit, /q{Colors.RESET} - выйти из программы")
    print(f"{Colors.CYAN}Для ввода запроса нажмите Enter.{Colors.RESET}")

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
        "queries": queries[:3],
        "instruction": instruction.strip()
    }



def handle_command(command):
    global USE_TOR
    if command in ["/tor", "/t", ".т", ".е"]:
        status = "включен" if USE_TOR else "выключен"
        print(f"Режим опроса через TOR: {status}")
    elif command in ["/tn", ".ет", ".тв", ".твк", ".твкл"]:
        if not USE_TOR:  # Только если режим действительно меняется
            USE_TOR = True
            print(f"{Colors.GREEN}Режим опроса через TOR включён.{Colors.RESET}")
            logger.info("TOR mode enabled")
    elif command in ["/tf", ".еа", ".твы", ".твык", ".твыкл"]:
        if USE_TOR:  # Только если режим действительно меняется
            USE_TOR = False
            print(f"{Colors.YELLOW}Режим опроса через TOR отключён.{Colors.RESET}")
            logger.info("TOR mode disabled")
    elif command.upper() in ["/DEBUG", "/INFO", "/ERROR"]:
        level = command.upper().lstrip("/")
        set_log_level(getattr(logging, level, logging.INFO))
    elif command in ["/help", "/h", ".р", ".х", ".п", ".с"]:
        show_help()
    elif command in ["/exit", "/q", ".й", ".в"]:
        save_dialog_history(load_dialog_history())
        print(f"{Colors.GREEN}Сеанс завершен.{Colors.RESET}")
        sys.exit()
    else:
        print(f"{Colors.RED}Неизвестная команда: {command}{Colors.RESET}")


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
    if response is None:
        print(f"{Colors.RED}Не удалось получить ответ от LLM. Использую исходный запрос пользователя.{Colors.RESET}")
        return {"queries": [user_input], "instruction": "Обработайте результаты поиска и предоставьте краткий ответ."}
    preprocessed = parse_preprocessing_response(response)
    
    print(f"{Colors.YELLOW}Анализ завершен. Сформированы следующие запросы:{Colors.RESET}")
    for i, query in enumerate(preprocessed['queries'], 1):
        print(f"{Colors.YELLOW}{i}. {query}{Colors.RESET}")
    return preprocessed
