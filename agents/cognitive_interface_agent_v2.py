#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent_v2.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 2.9.6
# ==================================================

import sys
from pathlib import Path
import readline
import subprocess
import logging
import os
import json
import time
import re

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from settings import BASE_DIR, LLM_API_URL
from agents.install_tor import restart_tor_and_check_ddgr
from agents.data_management import append_to_dialog_history, save_dialog_history, load_dialog_history, detect_language
from colors import Colors  # Используем Colors из внешнего файла
from cognitive_logic import print_message, process_search_results

# Настройка логирования
DEFAULT_LOG_LEVEL = "INFO"
ENV_FILE = Path(".env")

# Загрузка уровня логирования из .env
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as file:
        for line in file:
            if line.startswith("LOG_LEVEL"):
                DEFAULT_LOG_LEVEL = line.strip().split("=")[1]
                break

logging.basicConfig(level=getattr(logging, DEFAULT_LOG_LEVEL, logging.INFO),
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Глобальная переменная для режима TOR
USE_TOR = True
MAX_RETRIES = 3  # Максимальное количество попыток для запросов

def show_help():
    print(f"{Colors.CYAN}Доступные команды:{Colors.RESET}")
    print(f"  {Colors.CYAN}/help, /h{Colors.RESET} - показать эту справку")
    print(f"  {Colors.CYAN}/tor, /t{Colors.RESET} - показать статус TOR")
    print(f"  {Colors.CYAN}/tn{Colors.RESET} - включить TOR")
    print(f"  {Colors.CYAN}/tf{Colors.RESET} - отключить TOR")
    print(f"  {Colors.CYAN}/DEBUG, /INFO, /ERROR{Colors.RESET} - установить уровень логирования")
    print(f"  {Colors.CYAN}/exit, /q{Colors.RESET} - выйти из программы")
    print(f"{Colors.CYAN}Для ввода запроса нажмите Enter.{Colors.RESET}")

def set_log_level(level):
    global logger
    logging.getLogger().setLevel(level)
    logger.info(f"Уровень логирования установлен на {level}")
    # Сохраняем настройку в .env
    with open(ENV_FILE, "w") as file:
        file.write(f"LOG_LEVEL={level}\n")

def check_tor_installation():
    try:
        subprocess.run(["torsocks", "--version"], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        print(f"{Colors.RED}torsocks не найден. Установите его для использования TOR.{Colors.RESET}")
        return False

def print_header():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════╗")
    print("║                                               ║")
    print("║        Интерфейс Агентского Поиска            ║")
    print("║                                               ║")
    print("╚═══════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    print(f"{Colors.GRAY}----------------------------------------------{Colors.RESET}")
    print(f"{Colors.CYAN}Введите /help для справки по командам.{Colors.RESET}")
    print(f"{Colors.GRAY}----------------------------------------------{Colors.RESET}")

def preprocess_query(user_input):
    """
    Генерирует три связанных запроса на основе пользовательского ввода.
    """
    logger.debug(f"Preprocessing user input: {user_input}")
    queries = [
        user_input,
        f"{user_input} - связанные темы",
        f"Актуальная информация по запросу: {user_input}"
    ]
    instruction = "Анализируйте запросы и предоставьте структурированную информацию на основе результатов поиска."
    logger.debug(f"Generated queries: {queries}, Instruction: {instruction}")
    return {"queries": queries, "instruction": instruction}

def perform_search(queries, use_tor):
    """
    Выполняет поисковые запросы с использованием ddgr через TOR или напрямую.
    Перезапускает TOR при возникновении ошибок и повторяет запросы.
    """
    results = []
    for query in queries:
        retries = 0
        while retries < MAX_RETRIES:
            command = ["torsocks", "ddgr", "--json", query] if use_tor else ["ddgr", "--json", query]
            logger.info(f"Executing command: {' '.join(command)} (Attempt {retries + 1})")
            try:
                output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
                logger.debug(f"Search output for query '{query}': {output[:500]}")
                results.extend(json.loads(output) if output else [])
                break  # Успешное выполнение команды
            except subprocess.CalledProcessError as e:
                logger.error(f"Search command failed with CalledProcessError: {e.output}")
            except Exception as e:
                logger.error(f"Search command failed with exception: {e}")
            retries += 1
            if use_tor:
                logger.info("Restarting TOR and trying again.")
                restart_tor_and_check_ddgr()
            time.sleep(1)  # Задержка перед повтором
        else:
            logger.error(f"Failed to complete search for query: {query} after {MAX_RETRIES} attempts.")
            results.append(None)
    return results

def get_multiline_input():
    prefix = "Вы(tor): " if USE_TOR else "Вы: "
    lines = []
    while True:
        print(f"{Colors.BLUE}{prefix}{Colors.RESET}", end="")
        line = input()
        if line.strip() == "" and not lines:
            continue  # Игнорируем пустой ввод в первой строке
        if line.strip() == "" and lines:
            break  # Завершаем ввод, если введена пустая строка после непустых строк
        lines.append(line)
    return "\n".join(lines)

def main():
    global USE_TOR
    dialog_history = load_dialog_history()
    print_header()
    tor_installed = check_tor_installation()
    if not tor_installed:
        USE_TOR = False
    else:
        print(f"{Colors.BLUE}TOR готов к использованию.{Colors.RESET}")
    print(f"{Colors.YELLOW}ℹ Режим опроса через TOR по умолчанию {'включен' if USE_TOR else 'выключен'}.{Colors.RESET}")

    try:
        while True:
            user_input = get_multiline_input()
            if not user_input:
                continue

            print(f"{Colors.BLUE}Обрабатываю запрос пользователя...{Colors.RESET}")
            append_to_dialog_history({"role": "user", "content": user_input})
            preprocessed = preprocess_query(user_input)
            search_results = perform_search(preprocessed['queries'], use_tor=USE_TOR)
            logger.info(f"Total search results obtained: {len(search_results)}")
            if search_results:
                user_language = detect_language(user_input)
                response = process_search_results(preprocessed['instruction'], search_results, user_language)
                references = [result.get('url', '') for result in search_results if isinstance(result, dict) and 'url' in result]
                report = f"""
### Тема ответа пользователю:
{response}

## Вывод:
На основе полученных данных можно сделать следующие выводы...

## Интересные моменты:
1. Выделены ключевые аспекты анализа...

## Источники:
""" + "\n".join([f"{i + 1}. {url}" for i, url in enumerate(references[:15])])
                print_message("Агент", report)
                append_to_dialog_history({"role": "assistant", "content": report})
            else:
                print_message("Агент", "Извините, не удалось найти информацию по вашему запросу.")
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Saving dialog history and exiting.")
        print(f"{Colors.RED}\nСеанс прерван пользователем. История сохранена.{Colors.RESET}")
        save_dialog_history(dialog_history)

if __name__ == "__main__":
    main()
