import ollama
import time
import subprocess
import os
import glob
import sys
import signal
import datetime
import traceback

# Цветовые коды ANSI
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
GRAY = "\033[37m"
WHITE = "\033[97m"

# 🛠 НАСТРОЙКИ 🛠
OLLAMA_HOST = "http://10.0.1.31:11434"
MODEL_NAME = None  # Выбор модели в меню
USER_MESSAGE_FILE = None  # Файл с сообщениями
RESPONSE_FILE = None  # Файл для записи ответов
START_LINE = 0  # С какой строки начинать обработку
LAST_PROCESSED_LINE = 0  # Последняя обработанная строка

# Файлы с данными
SYS_PROMPT_FILE = "02_sys_prompt.txt"
RESPONSE_TEMPLATE_FILE = "03_response_template.txt"

# ====== ОБРАБОТКА ВЫХОДА ПО CTRL+C (ВОЗВРАТ В МЕНЮ) ======
def signal_handler(sig, frame):
    print(f"\n{YELLOW}Скрипт приостановлен. Возвращаемся в меню...{RESET}")
    raise KeyboardInterrupt  # Искусственно вызываем исключение

signal.signal(signal.SIGINT, signal_handler)

# ====== ОТОБРАЖЕНИЕ ТЕКУЩЕГО СОСТОЯНИЯ ======
def show_status():
    """Выводит текущее состояние переменных"""
    print("\n" + "-" * 60)
    print(f"{WHITE}Главное меню Генерации текстового контента{RESET}")
    print("-" * 60)
    print(f"{WHITE}Текущая конфигурация:{RESET}")
    print(f"Модель: {GREEN + MODEL_NAME + RESET if MODEL_NAME else RED + 'НЕ ОПРЕДЕЛЕНА' + RESET}")
    print(f"Файл сообщений: {GREEN + USER_MESSAGE_FILE + RESET if USER_MESSAGE_FILE else RED + 'НЕ ОПРЕДЕЛЕН' + RESET}")
    print(f"Файл записи ответов: {GREEN + RESPONSE_FILE + RESET if RESPONSE_FILE else RED + 'НЕ ОПРЕДЕЛЕН' + RESET}")
    print(f"Строка начала обработки: {GREEN}{START_LINE}{RESET}")
    print(f"Последняя обработанная строка: {YELLOW}{LAST_PROCESSED_LINE if LAST_PROCESSED_LINE else 'ЕЩЁ НЕ ОБРАБАТЫВАЛИСЬ'}{RESET}")
    print("-" * 60)

# ====== ФУНКЦИЯ ВЫБОРА МОДЕЛИ ======
def get_model_list():
    """Получает список доступных моделей Ollama"""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        models = client.list()["models"]
        return [m["model"] for m in models]
    except Exception as e:
        print(f"{RED}Ошибка при получении списка моделей: {e}{RESET}")
        return []

def choose_model():
    """Меню выбора модели"""
    global MODEL_NAME
    models = get_model_list()

    if not models:
        print(f"{RED}Нет доступных моделей! Возможно, Ollama не запущена.{RESET}")
        return

    print("\n=== Доступные модели Ollama ===")
    for idx, model in enumerate(models, start=1):
        print(f"{WHITE}{idx}. {model}{RESET}")

    while True:
        choice = input("\nВведите номер модели для использования: ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(models):
                MODEL_NAME = models[choice_idx]
                print(f"\n{GREEN}Выбрана модель: {MODEL_NAME}{RESET}")
                return
            else:
                print(f"{YELLOW}Некорректный ввод, попробуйте снова.{RESET}")
        except ValueError:
            print(f"{YELLOW}Введите номер модели из списка!{RESET}")

# ====== ФУНКЦИЯ ВЫБОРА ФАЙЛОВ ======
def choose_message_file():
    """Позволяет пользователю выбрать файл с сообщениями"""
    global USER_MESSAGE_FILE
    message_files = glob.glob("01_user_message*.txt")

    if not message_files:
        print(f"{RED}Файл с сообщениями не найден!{RESET}")
        sys.exit(1)

    print("\n=== Доступные файлы сообщений ===")
    for idx, filename in enumerate(message_files, start=1):
        print(f"{WHITE}{idx}. {filename}{RESET}")

    while True:
        choice = input("\nВведите номер файла с сообщениями: ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(message_files):
                USER_MESSAGE_FILE = message_files[choice_idx]
                print(f"\n{GREEN}Файл сообщений выбран: {USER_MESSAGE_FILE}{RESET}")
                return
            else:
                print(f"{YELLOW}Некорректный ввод, попробуйте снова.{RESET}")
        except ValueError:
            print(f"{YELLOW}Введите номер файла из списка!{RESET}")

def choose_response_file():
    """Позволяет пользователю выбрать файл для записи или создать новый"""
    global RESPONSE_FILE
    response_files = glob.glob("04_model_response*.txt")

    print("\n=== Доступные файлы записи ответов ===")
    for idx, filename in enumerate(response_files, start=1):
        print(f"{WHITE}{idx}. {filename}{RESET}")

    choice = input("\nВведите номер файла для записи или 'n' для создания нового: ").strip()
    if choice.lower() == 'n' or not response_files:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        RESPONSE_FILE = f"04_model_response_{timestamp}.txt"
        print(f"{GREEN}Создан новый файл: {RESPONSE_FILE}{RESET}")
    else:
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(response_files):
                RESPONSE_FILE = response_files[choice_idx]
                print(f"\n{GREEN}Файл записи ответов выбран: {RESPONSE_FILE}{RESET}")
            else:
                print(f"{YELLOW}Некорректный ввод, попробуйте снова.{RESET}")
                choose_response_file()
        except ValueError:
            print(f"{YELLOW}Введите номер файла из списка или 'n' для нового!{RESET}")
            choose_response_file()

# ====== ФУНКЦИЯ ГЕНЕРАЦИИ ======
def process_generation():
    """Основной процесс генерации"""
    global START_LINE, LAST_PROCESSED_LINE

    total_lines = sum(1 for _ in open(USER_MESSAGE_FILE))

    while True:
        start_input = input(f"\nВведите номер строки, с которой начать или 'q' для выхода в меню (1 - {total_lines}, Enter = {START_LINE+1}): ").strip()
        if start_input.lower() == "q":
            print(f"\n{YELLOW}Возвращаемся в меню...{RESET}")
            return  # Возвращаемся в меню

        if start_input.isdigit():
            START_LINE = max(0, int(start_input) - 1)
            break  # Выход из цикла после корректного ввода

    print(f"\n{GREEN}Запущена обработка с использованием модели `{MODEL_NAME}`...{RESET}")

    client = ollama.Client(host=OLLAMA_HOST)

    try:
        for idx, message in enumerate(open(USER_MESSAGE_FILE).readlines()[START_LINE:], start=START_LINE + 1):
            response = client.chat(model=MODEL_NAME, messages=[
                {"role": "system", "content": open(SYS_PROMPT_FILE).read().strip()},
                {"role": "user", "content": message.strip()}
            ])
            model_answer = response["message"]["content"]

            print(f"\n{GREEN}Ответ #{idx}:{RESET}\n{GRAY}{model_answer}{RESET}\n" + "-" * 50)
            LAST_PROCESSED_LINE = idx

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Скрипт приостановлен. Возвращаемся в меню...{RESET}")
        return  # Вернуться в меню

# ====== ОСНОВНОЙ ЦИКЛ ======
def main_loop():
    while True:
        show_status()
        action = input("\n1 - Начать генерацию\n2 - Выбрать модель\n3 - Выбрать файлы\n4 - Перезапустить Ollama\n5 - Выход\nВыберите действие: ").strip()
        if action == "1":
            process_generation()
        elif action == "2":
            choose_model()
        elif action == "3":
            choose_message_file()
            choose_response_file()
        elif action == "4":
            subprocess.run(["python", "restart_ollama.py", "--auto"])
        elif action == "5":
            print(f"{GREEN}Выход из программы.{RESET}")
            sys.exit(0)

# ====== ФУНКЦИЯ ПРОВЕРКИ ИНИЦИАЛЬНЫХ ПЕРЕМЕННЫХ ======
def check_initial_variables():
    """Проверяет, что все необходимые переменные заданы при старте.
    Если какая-либо из них пуста, предлагает заполнить их (сначала модель, затем файлы),
    после чего возвращает управление в главное меню."""
    global MODEL_NAME, USER_MESSAGE_FILE, RESPONSE_FILE

    if not MODEL_NAME:
        choose_model()
    if not USER_MESSAGE_FILE:
        choose_message_file()
    if not RESPONSE_FILE:
        choose_response_file()
    print(f"\n{GREEN}Начальная конфигурация установлена. Возвращаемся в главное меню...{RESET}")

# ====== ОСНОВНОЙ ЦИКЛ ======
def main_loop():
    while True:
        show_status()
        action = input("\n1 - Начать генерацию\n2 - Выбрать модель\n3 - Выбрать файлы\n4 - Перезапустить Ollama\n5 - Выход\nВыберите действие: ").strip()
        if action == "1":
            process_generation()
        elif action == "2":
            choose_model()
        elif action == "3":
            choose_message_file()
            choose_response_file()
        elif action == "4":
            subprocess.run(["python", "restart_ollama.py", "--auto"])
        elif action == "5":
            print(f"{GREEN}Выход из программы.{RESET}")
            sys.exit(0)

# При запуске скрипта проверяем, заданы ли переменные, и если нет – предлагаем заполнить их
check_initial_variables()

main_loop()
