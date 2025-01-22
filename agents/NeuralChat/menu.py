#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/menu.py
# ==================================================
# Подменю NeuralChat (CAN) для проекта LLMCAN
# Версия: 1.0.1
# - Исправлен путь для возврата в главное меню.
# ==================================================

import os
import sys
import logging

# Добавляем путь к корневой папке проекта для корректного импорта
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from agents.colors import Colors

# Настройка логирования для меню
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

# Словарь «номер -> скрипт»
SCRIPTS = {
    "1": "agents/NeuralChat/server/main.py",  # Запуск сервера
    "2": "agents/NeuralChat/client/main.py",  # Запуск клиента
    "3": "agents/NeuralChat/tests/test_logging.py",  # Тестирование логирования
    "b": "menu.py",  # Возврат в главное меню
}

def show_menu():
    # ASCII-баннер в стиле рамки
    print(Colors.BLUE + """
╔══════════════════════════════════════════════════════════╗
║                  NeuralChat (CAN) - МЕНЮ                 ║
║     (Децентрализованный чат с поддержкой ИИ)             ║
╚══════════════════════════════════════════════════════════╝
""" + Colors.RESET)

    print(Colors.MAGENTA + "Доступные скрипты проекта:\n" + Colors.RESET)

    # Перебираем скрипты в порядке их ключей (1,2,3,...)
    for key in sorted(SCRIPTS.keys(), key=lambda x: (x.isdigit(), x)):
        script = SCRIPTS[key]
        # Пример вывода: [1] agents/NeuralChat/server/main.py
        print(f"{Colors.GREEN}[{key}]{Colors.RESET} - {Colors.YELLOW}{script}{Colors.RESET}")

    # Дополнительные опции
    print(f"\n{Colors.GREEN}b{Colors.RESET} - Возврат в главное меню")
    print(f"{Colors.GREEN}q или exit{Colors.RESET} - Выйти из программы\n")

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
                Colors.CYAN + "Выберите действие (1-3, b) или q/exit: " + Colors.RESET
            ).strip().lower()

            if choice in ["q", "exit", ".й", "0"]:
                print(f"{Colors.GREEN}\n[INFO] Выход из программы. До свидания!{Colors.RESET}")
                sys.exit(0)
            elif choice == "b":
                print(f"{Colors.GREEN}\n[INFO] Возврат в главное меню.{Colors.RESET}")
                # Получаем абсолютный путь к menu.py
                main_menu_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../menu.py"))
                os.system(f"python3 {main_menu_path}")
                sys.exit(0)
            else:
                execute_script(choice)

    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting.")
        print(f"{Colors.RED}\nСеанс прерван пользователем.{Colors.RESET}")
        sys.exit(0)
