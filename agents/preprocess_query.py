#!/usr/bin/env python3
# LLMCAN/agents/preprocess_query.py
# ==================================================
# Модуль для обработки пользовательских запросов
# Версия: 1.0.1
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
MODEL = "qwen2:7b"
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
    command = command.strip().lower()  # Приводим команду к нижнему регистру для унификации

    if command in ["/tor", "/t", ".т", ".е", ".тор"]:
        # Показать текущий статус TOR
        status = "включен" if use_tor else "выключен"
        print(f"Режим опроса через TOR: {status}")

    elif command in ["/tn", ".ет", ".тв", ".твк", ".твкл"]:
        # Включение TOR
        if not use_tor:
            use_tor = True
            logger.info("TOR mode enabled")  # Логирование
            print(f"{Colors.GREEN}Режим опроса через TOR включён.{Colors.RESET}")

    elif command in ["/tf", ".еа", ".твы", ".твык", ".твыкл"]:
        # Выключение TOR
        if use_tor:
            use_tor = False
            logger.info("TOR mode disabled")  # Логирование
            print(f"{Colors.YELLOW}Режим опроса через TOR отключён.{Colors.RESET}")

    elif command in ["/debug", "/d", "/info", "/i", "/error", "/e", ".дебаг", ".д", ".инфо", ".и", ".ошибка", ".о", ".ошибки"]:
        # Установка уровня логирования
        levels = {
            "/debug": logging.DEBUG,
            "/d": logging.DEBUG,
            "/info": logging.INFO,
            "/i": logging.INFO,
            "/error": logging.ERROR,
            "/e": logging.ERROR,
            ".дебаг": logging.DEBUG,
            ".д": logging.DEBUG,
            ".инфо": logging.INFO,
            ".и": logging.INFO,
            ".ошибка": logging.ERROR,
            ".о": logging.ERROR,
            ".ошибки": logging.ERROR,
        }
        level = levels.get(command.lower(), logging.INFO)
        set_log_level(level)

    elif command in ["/log", "/l", ".лог", ".л", ".д", ".дщп"]:
        # Показ текущего уровня логирования
        current_level = logging.getLevelName(logger.level)
        print(f"{Colors.CYAN}Текущий уровень логирования: {Colors.BOLD}{current_level}{Colors.RESET}")

    elif command in ["/help", "/h", ".р", ".х", ".п", ".с", ".помощь", ".справка"]:
        # Показать справку
        show_help()

    elif command in ["/exit", "/q", ".й", ".в", ".выход"]:
        # Выход из программы
        save_dialog_history(load_dialog_history())
        print(f"{Colors.GREEN}Сеанс завершен.{Colors.RESET}")
        sys.exit()

    elif command in ["/show", "/s", ".покажи", ".п", ".покаж"]:
        # Показать дополнительную информацию о системе
        from agents.show_info_cognitive_interface_agent_v2 import show_info
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

from datetime import datetime

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

        # Декодируем JSON и фильтруем данные
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



from datetime import datetime

def preprocess_query(user_input):
    print(f"{Colors.YELLOW}Запрос пользователя получен. Начинаю анализ и формирование поисковых запросов...{Colors.RESET}")

    # Получаем текущую дату и время
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Системная инструкция модели с учётом текущей даты и времени
    system_prompt = f"""Проанализируй запрос пользователя, исправь возможные ошибки и сформулируй до трех связанных поисковых запросов для расширения контекста, при этом ориентируясь в текущем времени и дате, которая получена тобой на ввод. Текущие время: {current_datetime}. Учитывай их при анализе запроса пользователя и отталкивайся от этих данных при составлении инструкций. Также в отдельной секции создай инструкцию для обработки результатов поиска "Инструкция для обработки данных для LLM модели".

Формат ответа:
Основной запрос: [исправленный запрос пользователя]
Дополнительные запросы:
1. [запрос 1]
2. [запрос 2]
3. [запрос 3]

Инструкция для обработки результатов:
[Детальная инструкция по обработке и форматированию результатов поиска. В начале инструкции передай в системный промпт модели текущую дату и время {current_datetime} чтобы модель их точно знала]"""

    context = f"Запрос пользователя: {user_input}\n\n{system_prompt}"
    response = query_llm(context, include_history=False)

    if response is None:
        logger.debug("Ответ от LLM отсутствует или некорректен. Используется исходный запрос.")
        print(f"{Colors.RED}Не удалось получить ответ от LLM. Использую исходный запрос пользователя.{Colors.RESET}")
        return {"queries": [user_input], "instruction": "Обработайте результаты поиска и предоставьте краткий ответ."}

    preprocessed = parse_preprocessing_response(response)

    if not preprocessed['queries']:
        logger.debug("Сформированный запрос пуст. Проверьте ввод пользователя.")
        print(f"{Colors.RED}Не удалось сформировать поисковые запросы. Проверьте ввод.{Colors.RESET}")
        return {"queries": [user_input], "instruction": "Обработайте результаты поиска и предоставьте краткий ответ."}

    logger.info(f"Запрос обработан. Сформировано {len(preprocessed['queries'])} поисковых запросов.")

    # Добавляем пропуск строки для читаемости
    print("\nАнализ завершен. Сформированы следующие запросы:")
    for i, query in enumerate(preprocessed['queries'], 1):
        print(f"{Colors.YELLOW}{i}. {query}{Colors.RESET}")

    return preprocessed
