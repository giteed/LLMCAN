#!/usr/bin/env python3
# LLMCAN/agents/preprocess_query.py
# ==================================================
# Модуль для обработки пользовательских запросов
# Версия: 1.0.2 (тест)
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
import pprint
import readline

from settings import BASE_DIR, LLM_API_URL, LOGGING_CONFIG
from agents.install_tor import restart_tor_and_check_ddgr
from colors import Colors
from agents.data_management import save_dialog_history, load_dialog_history
from agents.show_info_cognitive_interface_agent_v2 import show_info

# === Настройка логирования ===
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# === Настройки ===
# Хорошо понимают поисковые результаты от ggdr
# MODEL = "llama3:latest"
MODEL = "gemma:7b"
# Слабые ответы:
# MODEL = "qwen2:7b"
LOG_DIR = BASE_DIR / 'logs'
ENV_FILE = Path(".env")

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
        elif line.startswith("4. "):
            instruction = line.split(". ", 1)[1].strip()
        elif parsing_instruction:
            instruction += line + "\n"

    return {
        "queries": queries[:4],
        "instruction": instruction.strip()
    }

def handle_command(command, use_tor):
    """
    Обработка команды пользователя.
    """
    command = command.strip().lower()

    if command in ["/tor", "/t", ".т", ".е", ".тор"]:
        status = "включен" if use_tor else "выключен"
        print(f"Режим опроса через TOR: {status}")
    elif command in ["/tn", ".ет", ".тв", ".твк", ".твкл"]:
        if not use_tor:
            use_tor = True
            logger.info("TOR mode enabled")
            print(f"{Colors.GREEN}Режим опроса через TOR включён.{Colors.RESET}")
    elif command in ["/tf", ".еа", ".твы", ".твык", ".твыкл"]:
        if use_tor:
            use_tor = False
            logger.info("TOR mode disabled")
            print(f"{Colors.YELLOW}Режим опроса через TOR отключён.{Colors.RESET}")
    elif command in ["/debug", "/d", "/info", "/i", "/error", "/e", ".дебаг", ".д", ".инфо", ".и", ".ошибка", ".о", ".ошибки"]:
        levels = {
            "/debug": logging.DEBUG, "/d": logging.DEBUG,
            "/info": logging.INFO, "/i": logging.INFO,
            "/error": logging.ERROR, "/e": logging.ERROR,
            ".дебаг": logging.DEBUG, ".д": logging.DEBUG,
            ".инфо": logging.INFO, ".и": logging.INFO,
            ".ошибка": logging.ERROR, ".о": logging.ERROR, ".ошибки": logging.ERROR
        }
        level = levels.get(command, logging.INFO)
        set_log_level(level)
    elif command in ["/log", "/l", ".лог", ".л", ".д", ".дщп"]:
        current_level = logging.getLevelName(logger.level)
        print(f"{Colors.CYAN}Текущий уровень логирования: {Colors.BOLD}{current_level}{Colors.RESET}")
    elif command in ["/help", "/h", ".р", ".х", ".п", ".с", ".помощь", ".справка"]:
        show_help()
    elif command in ["/exit", "/q", ".й", ".в", ".выход"]:
        save_dialog_history(load_dialog_history())
        print(f"{Colors.GREEN}Сеанс завершен.{Colors.RESET}")
        sys.exit()
    elif command in ["/show", "/s", ".покажи", ".п", ".покаж"]:
        log_level = logging.getLevelName(logger.level)
        show_info(use_tor, log_level)
    else:
        print(f"{Colors.RED}Неизвестная команда: {command}{Colors.RESET}")

    return use_tor

def pretty_print(data):
    """
    Выводит данные в читаемом формате в консоли.
    """
    print(json.dumps(data, ensure_ascii=False, indent=2, separators=(',', ': ')))

def get_current_datetime():
    """
    Возвращает текущую дату и время в удобном формате.
    """
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime

def preprocess_user_query(user_input):
    """
    Обрабатывает пользовательский запрос и добавляет текущую дату и время, если требуется.
    """
    current_datetime = get_current_datetime()
    user_input_with_datetime = (
        f"Текущая дата и время: {current_datetime}\n\n{user_input}"
    )
    return user_input_with_datetime

def query_llm(prompt, include_history=True):
    """
    Выполняет запрос к LLM и возвращает отфильтрованный ответ.
    """
    current_datetime = get_current_datetime()
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(LLM_API_URL, json=payload, timeout=10)
        response.raise_for_status()

        response_data = response.json()
        filtered_response = {
            "response": response_data.get("response", "<Нет ответа>"),
            "done_reason": response_data.get("done_reason", "Неизвестно")
        }

        logger.debug(f"Фильтрованный ответ от LLM: {filtered_response}")
        logger.info(f"Ответ модели: {response_data.get('response', '<Нет ответа>')}")
        return response_data.get("response", "<Нет ответа>")
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к модели: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        return None

def preprocess_query(user_input):
    print(f"{Colors.YELLOW}Запрос пользователя получен. Начинаю анализ и формирование поисковых запросов...{Colors.RESET}")

    current_datetime = get_current_datetime()

    system_prompt = f"""Проанализируй запрос пользователя, исправь возможные ошибки и сформулируй до четырех связанных поисковых запросов для расширения контекста, учитывая текущую дату и время: {current_datetime}.

Формат ответа:
Основной запрос: [исправленный запрос пользователя]
Дополнительные запросы:
1. [запрос 1]
2. [запрос 2]
3. [запрос 3]
4. [Детальная инструкция по обработке и форматированию результатов поиска для LLM модели]"""

    context = f"Запрос пользователя: {user_input}\n\n{system_prompt}"
    
    logger.debug(f"Сгенерированный системный промпт:\n{system_prompt}")

    response = query_llm(context, include_history=False)

    if response is None:
        logger.warning("Ответ от LLM отсутствует или некорректен. Используется исходный запрос.")
        print(f"{Colors.RED}Не удалось получить ответ от LLM. Использую исходный запрос пользователя.{Colors.RESET}")
        return {"queries": [user_input], "instruction": f"Обработайте результаты поиска и предоставьте краткий ответ на дату {current_datetime}."}

    preprocessed = parse_preprocessing_response(response)

    if not preprocessed['queries']:
        logger.warning("Сформированный запрос пуст. Проверьте ввод пользователя.")
        print(f"{Colors.RED}Не удалось сформировать поисковые запросы. Проверьте ввод.{Colors.RESET}")
        return {"queries": [user_input], "instruction": f"Обработайте результаты поиска и предоставьте краткий ответ на дату {current_datetime}."}

    logger.info(f"Запрос обработан. Сформировано {len(preprocessed['queries'])} поисковых запросов.")

    print("\nАнализ завершен. Сформированы следующие запросы:")
    for i, query in enumerate(preprocessed['queries'], 1):
        print(f"{Colors.YELLOW}{i}. {query}{Colors.RESET}")

    return preprocessed

def query_ddgr(queries):
    results = []
    for query in queries:
        result = ddgr_search(query)  # Предполагаемая функция для работы с ddgr
        if result:
            results.append(result)
        else:
            logger.warning(f"Получен пустой ответ от ddgr для запроса: {query}")
    return results

# Основная логика работы
if __name__ == "__main__":
    use_tor = False
    while True:
        user_input = input(f"{Colors.GREEN}Введите запрос или команду: {Colors.RESET}")
        if user_input.startswith(("/", ".")):
            use_tor = handle_command(user_input, use_tor)
        else:
            preprocessed = preprocess_query(user_input)
            search_results = query_ddgr(preprocessed['queries'])
            if search_results:
                final_response = process_search_results(search_results, preprocessed['instruction'])
                print(f"{Colors.GREEN}Финальный ответ:{Colors.RESET}\n{final_response}")
            else:
                print(f"{Colors.RED}Не удалось получить результаты поиска. Попробуйте другой запрос.{Colors.RESET}")
