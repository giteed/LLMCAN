#!/usr/bin/env python3
# LLMCAN/agents/preprocess_query.py
# ==================================================
# Модуль для обработки пользовательских запросов
# Версия: 1.1.0
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
from colors import Colors
from agents.data_management import save_dialog_history, load_dialog_history
from agents.show_info_cognitive_interface_agent_v2 import show_info

# === Настройки ===
MODEL = "qwen2:7b"
LOG_DIR = BASE_DIR / 'logs'
ENV_FILE = Path(".env")

# === Настройка логирования ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
    """
    Устанавливает уровень логирования.
    """
    logger.setLevel(level)
    if level == logging.DEBUG:
        print(f"{Colors.YELLOW}Уровень логирования установлен на DEBUG.{Colors.RESET}")
    elif level == logging.INFO:
        print(f"{Colors.GREEN}Уровень логирования установлен на INFO.{Colors.RESET}")
    elif level == logging.ERROR:
        print(f"{Colors.RED}Уровень логирования установлен на ERROR.{Colors.RESET}")


def show_help():
    """
    Отображает справку по доступным командам.
    """
    print(f"{Colors.CYAN}Доступные команды:{Colors.RESET}")
    print(f"  {Colors.CYAN}/help, /h{Colors.RESET} - показать эту справку")
    print(f"  {Colors.CYAN}/tor, /t{Colors.RESET} - показать статус TOR")
    print(f"  {Colors.CYAN}/tn{Colors.RESET} - включить TOR")
    print(f"  {Colors.CYAN}/tf{Colors.RESET} - отключить TOR")
    print(f"  {Colors.CYAN}/DEBUG, /INFO, /ERROR{Colors.RESET} - установить уровень логирования")
    print(f"  {Colors.CYAN}/log, /l{Colors.RESET} - показать текущий уровень логирования")
    print(f"  {Colors.CYAN}/show, .покажи{Colors.RESET} - показать информацию о системе и текущих режимах")
    print(f"  {Colors.CYAN}/exit, /q{Colors.RESET} - выйти из программы")
    print(f"{Colors.CYAN}Для ввода запроса нажмите Enter.{Colors.RESET}")


def parse_preprocessing_response(response):
    """
    Парсинг ответа от модели для получения поисковых запросов.
    """
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


def handle_command(command, use_tor):
    """
    Обработка команды пользователя.
    """
    command = command.strip().lower()

    if command in ["/tor", "/t"]:
        status = "включен" if use_tor else "выключен"
        print(f"Режим опроса через TOR: {status}")

    elif command in ["/tn"]:
        if not use_tor:
            use_tor = True
            logger.info("TOR mode enabled")
            print(f"{Colors.GREEN}Режим опроса через TOR включён.{Colors.RESET}")

    elif command in ["/tf"]:
        if use_tor:
            use_tor = False
            logger.info("TOR mode disabled")
            print(f"{Colors.YELLOW}Режим опроса через TOR отключён.{Colors.RESET}")

    elif command in ["/debug", "/info", "/error"]:
        levels = {
            "/debug": logging.DEBUG,
            "/info": logging.INFO,
            "/error": logging.ERROR,
        }
        level = levels.get(command.lower(), logging.INFO)
        set_log_level(level)

    elif command in ["/log", "/l"]:
        current_level = logging.getLevelName(logger.level)
        print(f"{Colors.CYAN}Текущий уровень логирования: {Colors.BOLD}{current_level}{Colors.RESET}")

    elif command in ["/help", "/h"]:
        show_help()

    elif command in ["/exit", "/q"]:
        save_dialog_history(load_dialog_history())
        print(f"{Colors.GREEN}Сеанс завершен.{Colors.RESET}")
        sys.exit()

    elif command in ["/show", "/s"]:
        log_level = logging.getLevelName(logger.level)
        show_info(use_tor, log_level)

    else:
        print(f"{Colors.RED}Неизвестная команда: {command}{Colors.RESET}")

    return use_tor


def query_llm(prompt, include_history=True):
    """
    Выполняет запрос к LLM и возвращает ответ.
    """
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(LLM_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        logger.debug(f"Ответ от LLM: {response.text}")
        return response.json().get("response", "<Нет ответа>")
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к модели: {e}")
        return None


def preprocess_query(user_input):
    """
    Обработка пользовательского запроса.
    """
    print(f"{Colors.YELLOW}Запрос пользователя получен. Начинаю анализ...{Colors.RESET}")
    system_prompt = """Проанализируй запрос пользователя, исправь возможные ошибки и сформулируй до трех связанных поисковых запросов."""
    context = f"Запрос пользователя: {user_input}\n\n{system_prompt}"
    response = query_llm(context, include_history=False)
    if response is None:
        print(f"{Colors.RED}Не удалось получить ответ от LLM. Использую исходный запрос пользователя.{Colors.RESET}")
        return {"queries": [user_input], "instruction": ""}
    preprocessed = parse_preprocessing_response(response)
    logger.info(f"Запрос обработан. Сформировано {len(preprocessed['queries'])} поисковых запросов.")
    return preprocessed
