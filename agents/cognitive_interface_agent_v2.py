#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent_v2.py
# Версия: 3.1.0

import sys
from pathlib import Path
import readline
import subprocess
import os
import json
import time
import re
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from settings import BASE_DIR, LLM_API_URL
from agents.install_tor import restart_tor_and_check_ddgr
from agents.data_management import append_to_dialog_history, save_dialog_history, load_dialog_history, detect_language
from agents.colors import Colors
from cognitive_logic import print_message, process_search_results
from preprocess_query import preprocess_query, handle_command, show_help, set_log_level

# Глобальная переменная для режима TOR
USE_TOR = True
MAX_RETRIES = 3

def check_tor_installation():
    try:
        subprocess.run(["torsocks", "--version"], check=True, capture_output=True)
        logger.info("TORSocks установлен и готов к использованию.")
        return True
    except FileNotFoundError:
        logger.warning("TORSocks не найден. TOR недоступен.")
        print(f"{Colors.RED}torsocks не найден. Установите его для использования TOR.{Colors.RESET}")
        return False

def print_header():
    logger.info("Вывод заголовка интерфейса.")
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

def get_multiline_input():
    global USE_TOR
    logger.info("Получение ввода от пользователя.")
    print(f"{Colors.CYAN}Введите ваш запрос. Для завершения ввода нажмите Enter на пустой строке.{Colors.RESET}")
    lines = []
    while True:
        line = input(f"{Colors.CYAN}Вы: {Colors.RESET}").strip()
        if line.startswith(("/", ".")):
            logger.debug(f"Обработка команды пользователя: {line}")
            USE_TOR = handle_command(line, USE_TOR)
            continue
        if line == "":
            break
        lines.append(line)
    return " ".join(lines)

def perform_search(queries, use_tor, max_retries=3):
    """
    Выполняет поиск для каждого запроса. Добавляет повторные попытки при ошибке.
    """
    results = []
    if not queries:
        logger.warning("Список запросов пуст. Поиск не будет выполнен.")
        return results

    for query in queries:
        logger.info(f"Начинаю обработку запроса: {query}")
        retries = 0
        while retries < max_retries:
            try:
                command = ["torsocks", "ddgr", "--json", query] if use_tor else ["ddgr", "--json", query]
                logger.debug(f"Выполняется команда поиска: {' '.join(command)} (попытка {retries + 1})")
                output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
                logger.debug(f"Вывод команды ddgr: {output}")
                if output.strip():
                    json_results = json.loads(output)
                    if isinstance(json_results, list) and json_results:
                        results.extend(json_results)
                        logger.info(f"Успешно выполнен поиск по запросу: {query}")
                        break
                    else:
                        logger.warning(f"Некорректный формат или пустой результат для запроса: {query}")
                else:
                    logger.warning(f"Пустой результат для запроса: {query}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Ошибка выполнения команды: {e}. Попытка {retries + 1}/{max_retries}")
                retries += 1
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка декодирования JSON: {e}. Попытка {retries + 1}/{max_retries}")
                retries += 1
            except Exception as e:
                logger.error(f"Неизвестная ошибка: {e}. Попытка {retries + 1}/{max_retries}")
                print(f"Неизвестная ошибка: {Colors.RED} {e}. Попытка {retries + 1}/{max_retries}{Colors.RESET}")
                retries += 1
            time.sleep(2)  # Задержка перед повторной попыткой
        else:
            logger.error(f"Не удалось найти информацию по запросу: {query} после {max_retries} попыток.")
            print(f"{Colors.RED}Не удалось найти информацию по запросу: {query} после {max_retries} попыток.{Colors.RESET}")
            results.append(None)

    if not any(results):
        logger.warning("Все поисковые запросы вернули пустые результаты.")
    else:
        logger.debug(f"Итоговые результаты поиска: {results}")
    return results


def main():
    global USE_TOR
    dialog_history = load_dialog_history()
    logger.info("Запуск основного цикла программы.")
    print_header()
    tor_installed = check_tor_installation()
    if not tor_installed:
        USE_TOR = False
        logger.warning("TOR не установлен. Все запросы будут выполняться без TOR.")
    else:
        logger.info("TOR установлен. Использование TOR включено по умолчанию.")
        print(f"{Colors.BLUE}TOR готов к использованию.{Colors.RESET}")
        print(f"{Colors.YELLOW}ℹ Режим опроса через TOR по умолчанию {'включен' if USE_TOR else 'выключен'}.{Colors.RESET}")

    try:
        while True:
            user_input = get_multiline_input()
            if not user_input:
                logger.info("Пустой ввод пользователя. Ожидание следующего ввода.")
                continue

            logger.info(f"Получен пользовательский запрос: {user_input}")
            print(f"{Colors.BLUE}Обрабатываю запрос пользователя...{Colors.RESET}")
            append_to_dialog_history({"role": "user", "content": user_input})

            try:
                preprocessed = preprocess_query(user_input)
                logger.debug(f"Предобработанный запрос: {preprocessed}")

                logger.info("Попытка выполнения поиска.")
                search_results = perform_search(preprocessed['queries'], use_tor=USE_TOR)
                #print("\n### Данные для передачи в модель ###")
                #print(f"Инструкция для обработки: {preprocessed['instruction']}")
                #print(f"Результаты поиска: {search_results}")

                # Обязательный вывод перед отправкой в модель
                print("\n### Данные для передачи в модель ###")
                print(f"Инструкция для обработки: {preprocessed['instruction']}")
                print(f"Результаты поиска: {search_results}\n")

                if any(search_results):
                    logger.info("Информация найдена. Формируется ответ...")
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

                    logger.info("Ответ успешно сформирован.")
                    print_message("Агент", report)
                    append_to_dialog_history({"role": "assistant", "content": report})
                else:
                    logger.warning("Поиск завершён без результата.")
                    print_message("Агент", "Извините, не удалось найти информацию по вашему запросу.")
            except Exception as e:
                logger.error(f"Ошибка обработки запроса: {e}")
                print_message("Агент", "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова.")
    except KeyboardInterrupt:
        logger.info("Сеанс завершён пользователем.")
        print(f"{Colors.RED}\nСеанс прерван пользователем. История сохранена.{Colors.RESET}")
        save_dialog_history(dialog_history)


if __name__ == "__main__":
    main()
