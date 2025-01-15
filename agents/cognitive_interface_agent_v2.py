#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent_v2.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 2.8.2
# ==================================================

import sys
from pathlib import Path
import readline
import subprocess
import logging

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from settings import BASE_DIR, LLM_API_URL
from cognitive_interface_agent_functions import *
from agents.install_tor import restart_tor_and_check_ddgr
from agents.data_management import append_to_dialog_history, save_dialog_history, load_dialog_history

# Обновленный класс Colors
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Глобальная переменная для режима TOR
USE_TOR = True

def show_help():
    print(f"{Colors.CYAN}Доступные команды:{Colors.RESET}")
    print(f"  {Colors.CYAN}/help, /h{Colors.RESET} - показать эту справку")
    print(f"  {Colors.CYAN}/tor, /t{Colors.RESET} - показать статус TOR")
    print(f"  {Colors.CYAN}/tn{Colors.RESET} - включить TOR")
    print(f"  {Colors.CYAN}/tf{Colors.RESET} - отключить TOR")
    print(f"  {Colors.CYAN}/exit, /q{Colors.RESET} - выйти из программы")
    print(f"{Colors.CYAN}Для ввода запроса нажмите Enter.{Colors.RESET}")

def check_tor_installation():
    try:
        subprocess.run(["torsocks", "--version"], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        print(f"{Colors.RED}torsocks не найден. Установите его для использования TOR.{Colors.RESET}")
Сеанс прерван пользователем. История сохранена.{Colors.RESET}")torsocks не найден. Установите его для использования TOR.{Colors.RESET}")
        return False

def print_header():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════╗")
    print("║                                               ║")
    print("║        Интерфейс Агентского Поиска            ║")
    print("║                                               ║")
    print("╚═══════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def handle_command(command):
    global USE_TOR
    if command in ["/tor", "/t"]:
        status = "включен" if USE_TOR else "выключен"
        print(f"Режим опроса через TOR: {status}")
    elif command == "/tn":
        USE_TOR = True
        print(f"{Colors.GREEN}Режим опроса через TOR включён.{Colors.RESET}")
        logger.info("TOR mode enabled")
    elif command == "/tf":
        USE_TOR = False
        print(f"{Colors.YELLOW}Режим опроса через TOR отключён.{Colors.RESET}")
        logger.info("TOR mode disabled")
    elif command in ["/help", "/h"]:
        show_help()
    elif command in ["/exit", "/q"]:
        finalize_history_saving()
        print(f"{Colors.GREEN}Сеанс завершен.{Colors.RESET}")
        sys.exit()
    else:
        print(f"{Colors.RED}Неизвестная команда: {command}{Colors.RESET}")

def get_multiline_input():
    print(f"{Colors.CYAN}Введите ваш запрос. Для завершения ввода нажмите Enter на пустой строке.{Colors.RESET}")
    lines = []
    while True:
        line = input().strip()
        if line.startswith("/"):
            handle_command(line)
            print(f"{Colors.CYAN}Вы: {Colors.RESET}", end="")
            continue
        if line == "":
            break
        lines.append(line)
    return " ".join(lines)

def perform_search(queries, use_tor):
    results = []
    for query in queries:
        command = ["torsocks", "ddgr", "--json", query] if use_tor else ["ddgr", "--json", query]
        logger.info(f"Executing command: {' '.join(command)}")
        try:
            output = subprocess.check_output(command, universal_newlines=True)
            logger.debug(f"Search output for query '{query}': {output[:500]}")
            logger.debug(f"Search output (partial) for query '{query}': {output[:500]}")
            results.append(output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Search command failed: {e}")
            results.append(None)
    return results

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
            logger.debug(f"Search results (partial): {search_results[:2]}")  # Log only the first two results for brevity
            if search_results:
                user_language = detect_language(user_input)
                logger.debug(f"Processing search results: {search_results[:2]} with instruction: {preprocessed['instruction']} and language: {user_language}")
                response = process_search_results(search_results, preprocessed['instruction'], user_language)
                append_to_dialog_history({"role": "assistant", "content": response})
                print_message("Агент", response)
            else:
                print_message("Агент", "Извините, не удалось найти информацию по вашему запросу.")
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Saving dialog history and exiting.")
        print(f"{Colors.RED}
Сеанс прерван пользователем. История сохранена.{Colors.RESET}")
        finalize_history_saving()

if __name__ == "__main__":
    main()
