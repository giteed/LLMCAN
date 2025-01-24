#!/usr/bin/env python3
# LLMCAN/menu.py
# ==================================================
# Главное меню для проекта LLMCAN (улучшенная версия)
# Версия: 1.2.0
# - Добавлено подменю NeuralChat (CAN).
# ==================================================

import os
import sys
import logging
import readline  # Для истории ввода (если поддерживается в окружении)
from agents.colors import Colors
from scripts.help import print_tmux_help


# Настройка логирования для меню
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

# Словарь «номер -> скрипт»
SCRIPTS = {
    "1": "agents/cognitive_interface_agent_v2.py",
    "2": "agents/cognitive_interface_agent.py",
    "3": "agents/chat_with_ddgr_context.py",
    "4": "agents/ddgr_agent.py",                # добавлен ddgr_agent
    "5": "agents/test_local_llm_api_and_tor.py",
    "6": "agents/install_tor.py",
    "7": "agents/NeuralChat/nc_can_menu.py",           # Подменю NeuralChat
    "s": "settings.py",
    "ht": "scripts/help/print_tmux_help.py print_tmux_help"
}

def show_menu():
    # ASCII-баннер в стиле рамки
    print(Colors.CYAN + """
╔══════════════════════════════════════════════════════════╗
║                  LLMCAN - ГЛАВНОЕ МЕНЮ                   ║
║     (Language & Logic Model Cognitive Agent Network)     ║
╚══════════════════════════════════════════════════════════╝
""" + Colors.RESET)

    print(Colors.MAGENTA + "Доступные скрипты проекта:\n" + Colors.RESET)

    # Перебираем скрипты в порядке их ключей (1,2,3,4,5,6,...)
    for key in sorted(SCRIPTS.keys(), key=lambda x: (x.isdigit(), x)):
        script = SCRIPTS[key]
        # Пример вывода: [1] agents/cognitive_interface_agent_v2.py
        print(f"{Colors.GREEN}[{key}]{Colors.RESET} - {Colors.YELLOW}{script}{Colors.RESET}")

    # Дополнительные опции
    print(f"\n{Colors.GREEN}q или exit{Colors.RESET} - Выйти из программы\n")

def execute_script(choice):
    """Запуск выбранного скрипта из словаря SCRIPTS."""
    script_path = SCRIPTS.get(choice)
    if script_path:
        log_level = os.getenv("LOG_LEVEL", "INFO")
        print(f"{Colors.BOLD}{Colors.YELLOW}[INFO] Запуск: {script_path}{Colors.RESET}")
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
            choice = input(
                Colors.CYAN + "Выберите действие (1-7, или буквы) или q/exit: " + Colors.RESET
            ).strip().lower()

            if choice in ["q", "exit", ".й", "0"]:
                print(f"{Colors.GREEN}\n[INFO] Выход из программы. До свидания!{Colors.RESET}")
                sys.exit(0)
            else:
                execute_script(choice)

    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting.")
        print(f"{Colors.RED}\nСеанс прерван пользователем.{Colors.RESET}")
        sys.exit(0)
