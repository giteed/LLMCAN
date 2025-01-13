#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 2.6
# ==================================================

import sys
from pathlib import Path
import readline
import subprocess

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from settings import BASE_DIR, LLM_API_URL
from cognitive_interface_agent_functions import *
from agents.install_tor import restart_tor_and_check_ddgr, perform_search

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
    load_dialog_history()
    
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
            preprocessed = preprocess_query(user_input)
            search_results = perform_search(preprocessed['queries'])
            
            if search_results:
                user_language = detect_language(user_input)
                response = process_search_results(search_results, preprocessed['instruction'], user_language)
                if response:
                    references = [result['url'] for result in search_results[0] if 'url' in result]
                    formatted_response = format_response_with_references(response, references)
                    print(f"{Colors.GREEN}Ответ готов:{Colors.RESET}")
                    print_message("Агент", formatted_response)
                    
                    dialog_history.append({"role": "user", "content": user_input})
                    dialog_history.append({"role": "assistant", "content": formatted_response})
                    save_dialog_history()
                    save_report(preprocessed, formatted_response)
                else:
                    print_message("Агент", "Не удалось обработать результаты поиска. Пожалуйста, попробуйте еще раз.")
            else:
                print_message("Агент", "Извините, не удалось найти информацию по вашему запросу.")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Сеанс прерван пользователем. История сохранена.{Colors.RESET}")
    finally:
        save_dialog_history()

if __name__ == "__main__":
    main()
