#!/usr/bin/env python3
# LLMCAN/agents/menu.py
# ==================================================
# Главное меню для проекта LLMCAN
# Версия: 1.0.1
# ==================================================

import os
import sys
from agents.colors import Colors
import logging

# Настройка логгирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

# Путь к скриптам проекта
SCRIPTS = {
    "1": "agents/cognitive_interface_agent_v2.py",
    "2": "agents/cognitive_interface_agent.py",
    "3": "agents/chat_with_ddgr_context.py",
    "4": "agents/ddgr_agent.py",
    "5": "agents/install_tor.py",
}

def show_menu():
    print(f"{Colors.CYAN}\n=== Главное меню LLMCAN ==={Colors.RESET}")
    print(f"{Colors.GREEN}1.{Colors.RESET} Запустить cognitive_interface_agent_v2.py")
    print(f"{Colors.GREEN}2.{Colors.RESET} Запустить cognitive_interface_agent.py")
    print(f"{Colors.GREEN}3.{Colors.RESET} Запустить chat_with_ddgr_context.py")
    print(f"{Colors.GREEN}4.{Colors.RESET} Запустить ddgr_agent.py")
    print(f"{Colors.GREEN}5.{Colors.RESET} Запустить install_tor.py")
    print(f"{Colors.RED}q или exit{Colors.RESET} - Выйти из программы\n")

def execute_script(choice):
    script_path = SCRIPTS.get(choice)
    if script_path:
        print(f"{Colors.YELLOW}[INFO] Запуск: {script_path}{Colors.RESET}")
        try:
            os.system(f"python3 {script_path}")
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Не удалось запустить {script_path}: {e}{Colors.RESET}")
    else:
        print(f"{Colors.RED}[ERROR] Некорректный выбор. Попробуйте снова.{Colors.RESET}")

if __name__ == "__main__":
    try:
        while True:
            show_menu()
            choice = input(f"{Colors.CYAN}Выберите действие (1-5, q/exit): {Colors.RESET}").strip().lower()
            if choice in ["q", "exit"]:
                print(f"{Colors.GREEN}\n[INFO] Выход из программы. До свидания!{Colors.RESET}")
                sys.exit(0)
            else:
                execute_script(choice)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting.")
        print(f"{Colors.RED}\nСеанс прерван пользователем.{Colors.RESET}")
        sys.exit(0)  # Завершение программы с кодом 0 (успешно)
