#!/usr/bin/env python3
# LLMCAN/agents/menu.py
# ==================================================
# Главное меню для проекта LLMCAN
# Версия: 1.0.3
# ==================================================

import os
import sys
from agents.colors import Colors
import logging
import readline

# Настройка логирования для меню
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

# Путь к скриптам проекта
SCRIPTS = {
    "1": "agents/cognitive_interface_agent_v2.py",
    "2": "agents/cognitive_interface_agent.py",
    "3": "agents/chat_with_ddgr_context.py",
    "4": "agents/ddgr_agent.py",
    "5": "agents/test_local_llm_api_and_tor.py",  # <-- новый пункт (перед установкой TOR)
    "6": "agents/install_tor.py",
    "s": "settings.py",
}

def show_menu():
    print(f"{Colors.CYAN}\n=== Главное меню LLMCAN ==={Colors.RESET}")
    for key, script in SCRIPTS.items():
        print(f"{Colors.GREEN}{key}.{Colors.RESET} Запустить {script}")
    print(f"{Colors.RED}q или exit{Colors.RESET} - Выйти из программы\n")

def execute_script(choice):
    script_path = SCRIPTS.get(choice)
    if script_path:
        log_level = os.getenv("LOG_LEVEL", "INFO")
        print(f"{Colors.YELLOW}[INFO] Запуск: {script_path}{Colors.RESET}")
        try:
            os.system(f"python3 {script_path} --log-level={log_level}")
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Не удалось запустить {script_path}: {e}{Colors.RESET}")
    else:
        print(f"{Colors.RED}[ERROR] Некорректный выбор. Попробуйте снова.{Colors.RESET}")

if __name__ == "__main__":
    try:
        while True:
            show_menu()
            choice = input(f"{Colors.CYAN}Выберите действие (1-6, s, q/exit): {Colors.RESET}").strip().lower()
            if choice in ["q", "exit", ".й", "0"]:
                print(f"{Colors.GREEN}\n[INFO] Выход из программы. До свидания!{Colors.RESET}")
                sys.exit(0)
            else:
                execute_script(choice)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting.")
        print(f"{Colors.RED}\nСеанс прерван пользователем.{Colors.RESET}")
        sys.exit(0)
