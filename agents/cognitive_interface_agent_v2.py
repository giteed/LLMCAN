#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent_v2.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 2.8 (с улучшениями)
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

def show_help():
    print(f"{Colors.CYAN}Доступные команды:{Colors.RESET}")
    print(f"  {Colors.CYAN}/help, /h{Colors.RESET} - показать эту справку")
    print(f"  {Colors.CYAN}/tor, /t{Colors.RESET} - показать статус TOR")
    print(f"  {Colors.CYAN}/toron, /tn{Colors.RESET} - включить TOR")
    print(f"  {Colors.CYAN}/toroff, /tf{Colors.RESET} - выключить TOR")
    print(f"  {Colors.CYAN}/exit, /q{Colors.RESET} - выйти из программы")
    print(f"{Colors.CYAN}Для ввода запроса нажмите Enter дважды.{Colors.RESET}")

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

def main():
    global USE_TOR
    dialog_history = load_dialog_history()  # Load once to avoid duplication
    
    print_header()
    
    tor_installed = check_tor_installation()
    if tor_installed:
        tor_active = check_tor_connection()
        if tor_active:
            print(f"{Colors.BLUE}✓ TOR сервис активен в системе.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠ TOR сервис неактивен в системе.{Colors.RESET}")
        print(f"{Colors.YELLOW}ℹ Режим опроса через TOR по умолчанию выключен. Включить: /tn{Colors.RESET}")
        USE_TOR = False
    else:
        USE_TOR = False
    
    print(f"{Colors.GRAY}----------------------------------------------{Colors.RESET}")
    print(f"{Colors.CYAN}Введите /help для справки по командам.{Colors.RESET}")
    print(f"{Colors.GRAY}----------------------------------------------{Colors.RESET}")

    try:
        while True:
            user_input = get_multiline_input()
            user_input = user_input.strip().lower()
            
            if user_input in ['/q', '/exit', 'выход']:
                print(f"{Colors.GREEN}Сеанс завершен. История сохранена.{Colors.RESET}")
                if not save_dialog_history(dialog_history):
                    logger.error("Failed to save dialog history. Check permissions and file path.")
                break
            elif user_input in ['/h', '/help']:
                show_help()
                continue
            elif user_input.startswith('/'):
                handle_command(user_input)
                continue
            
            if not user_input:
                continue
            
            print(f"{Colors.BLUE}Обрабатываю запрос пользователя...{Colors.RESET}")
            append_to_dialog_history({"role": "user", "content": user_input})  # Log added user input
            preprocessed = preprocess_query(user_input)
            logger.debug(f"Preprocessed query: {preprocessed}")
            search_results = perform_search(preprocessed['queries'])
            
            if search_results:
                user_language = detect_language(user_input)
                logger.debug(f"Detected user language: {user_language}")
                response = process_search_results(search_results, preprocessed['instruction'], user_language)
                if response:
                    references = [result['url'] for result in search_results[0] if 'url' in result]
                    formatted_response = format_response_with_references(response, references)
                    print(f"{Colors.GREEN}Ответ готов:{Colors.RESET}")
                    print_message("Агент", formatted_response)
                    append_to_dialog_history({"role": "assistant", "content": formatted_response})  # Log added assistant response
                else:
                    print_message("Агент", "Не удалось обработать результаты поиска. Пожалуйста, попробуйте еще раз.")
            else:
                logger.warning("No results found for user query.")
                print_message("Агент", "Извините, не удалось найти информацию по вашему запросу.")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Сеанс прерван пользователем. История сохранена.{Colors.RESET}")
        save_dialog_history(dialog_history)
    finally:
        save_dialog_history(dialog_history)

if __name__ == "__main__":
    main()
