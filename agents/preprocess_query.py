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
import logging.config
import re
import time
import uuid
import socket
import socks
import readline

from settings import BASE_DIR, LLM_API_URL, LOGGING_CONFIG
from agents.install_tor import restart_tor_and_check_ddgr
from colors import Colors  # Используем Colors из внешнего файла
from agents.data_management import save_dialog_history, load_dialog_history
from agents.show_info_cognitive_interface_agent_v2 import show_info

# Настройка логирования
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# === Настройки ===
MODEL = "qwen2:7b"

def set_log_level(level):
    """
    Устанавливает уровень логирования для всех обработчиков.
    """
    logger.setLevel(level)
    level_name = logging.getLevelName(level)
    if level == logging.DEBUG:
        print(f"{Colors.YELLOW}Уровень логирования установлен на DEBUG.{Colors.RESET}")
    elif level == logging.INFO:
        print(f"{Colors.GREEN}Уровень логирования установлен на INFO.{Colors.RESET}")
    elif level == logging.ERROR:
        print(f"{Colors.RED}Уровень логирования установлен на ERROR.{Colors.RESET}")
    else:
        print(f"{Colors.CYAN}Уровень логирования установлен на {Colors.BOLD}{level_name}{Colors.RESET}")
    logger.debug(f"Текущий уровень логирования: {level_name}")

def show_help():
    """
    Отображает справку по доступным командам.
    """
    logger.info("Отображение справки пользователю.")
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
    Парсинг ответа от модели для получения поисковых запросов и инструкции.
    """
    lines = response.split('\n')
    queries = []
    instruction = ""
    parsing_instruction = False

    for line in lines:
        if line.startswith("Основной запрос:"):
            queries.append(line.split(": ", 1)[1].strip())
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
    logger.debug(f"Обработка команды: {command}")

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
        level = levels.get(command, logging.INFO)
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

def preprocess_query(user_input):
    """
    Обработка запроса пользователя для формирования поисковых запросов.
    """
    logger.info("Начало обработки пользовательского запроса.")
    print(f"{Colors.YELLOW}Запрос пользователя получен. Начинаю анализ...{Colors.RESET}")
    system_prompt = """Проанализируй запрос пользователя и создай до трех связанных поисковых запросов."""
    context = f"Запрос пользователя: {user_input}\n\n{system_prompt}"
    response = query_llm(context)
    if response is None:
        logger.error("Не удалось получить ответ от модели.")
        return {"queries": [user_input], "instruction": ""}
    preprocessed = parse_preprocessing_response(response)
    logger.info("Запрос успешно обработан.")
    return preprocessed

def query_llm(prompt):
    """
    Выполняет запрос к LLM.
    """
    logger.info("Выполнение запроса к LLM.")
    payload = {"model": MODEL, "prompt": prompt}
    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к LLM: {e}")
        return None
