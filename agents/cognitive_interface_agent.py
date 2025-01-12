#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent.py
# ==================================================
# Когнитивный интерфейсный агент для проекта LLMCAN
# Версия: 2.1
# ==================================================

import sys
from pathlib import Path
import readline

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from settings import BASE_DIR, LLM_API_URL
from cognitive_interface_agent_functions import *

def check_tor_connection():
    try:
        result = subprocess.run(["torsocks", "curl", "https://check.torproject.org/api/ip"], capture_output=True, text=True, timeout=10)
        if "IsTor\":true" in result.stdout:
            print(f"{Colors.GREEN}Отладка: TOR соединение активно{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}Отладка: TOR соединение неактивно{Colors.RESET}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Отладка: Ошибка проверки TOR соединения: {e}{Colors.RESET}")
        return False
        
check_tor_connection() 

def main():
    load_dialog_history()
    check_tor_settings()
    print(f"{Colors.YELLOW}Добро пожаловать в Когнитивный Интерфейсный Агент!{Colors.RESET}")
    print(f"{Colors.YELLOW}Введите 'выход', '/q' или Ctrl+C для завершения.{Colors.RESET}")
    print(f"{Colors.YELLOW}Для поиска используйте ключевые слова 'поищи' или 'найди'.{Colors.RESET}")
    print(f"{Colors.YELLOW}Используйте /toron для включения TOR и /toroff для выключения.{Colors.RESET}")

    try:
        while True:
            user_input = get_multiline_input()
            
            if user_input.lower() in ['/q', 'выход']:
                print(f"{Colors.GREEN}Сеанс завершен. История сохранена.{Colors.RESET}")
                break
            elif user_input.startswith('/'):
                handle_command(user_input.lower())
                continue
            
            print(f"{Colors.YELLOW}Обрабатываю запрос пользователя...{Colors.RESET}")
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
