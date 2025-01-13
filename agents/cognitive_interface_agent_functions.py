#!/usr/bin/env python3
# LLMCAN/agents/cognitive_interface_agent_functions.py
# ==================================================
# Функции для Когнитивного интерфейсного агента
# ==================================================

import os
import sys
import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import re
import time
import uuid

from settings import BASE_DIR, LLM_API_URL
from agents.install_tor import restart_tor_and_check_ddgr

# === Настройки ===
MODEL = "qwen2:7b"
HISTORY_FILE = BASE_DIR / "data" / "cognitive_agent_history.txt"
TEMP_DIR = BASE_DIR / "temp"
REPORT_FILE = BASE_DIR / "data" / "cognitive_agent_reports.txt"
MAX_HISTORY_LENGTH = 50
LOG_DIR = BASE_DIR / 'logs'
DELAY_BETWEEN_REQUESTS = 5  # секунды

# === Настройка логирования ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

LOG_DIR.mkdir(exist_ok=True)
file_handler = logging.FileHandler(LOG_DIR / f'cognitive_agent_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# === Цвета для консоли ===
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

# === Глобальные переменные ===
dialog_history = []
USE_TOR = False

# === Функции ===
def check_tor_connection():
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True, timeout=10)
        if result.stdout.strip() == "active":
            print(f"{Colors.BLUE}TOR сервис активен в системе.{Colors.RESET}")
            return True
        else:
            print(f"{Colors.YELLOW}TOR сервис неактивен в системе.{Colors.RESET}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Ошибка при проверке статуса TOR: {e}{Colors.RESET}")
        return False

def handle_command(command):
    global USE_TOR
    if command in ['/tor', '/t']:
        tor_status = "включен" if USE_TOR else "выключен"
        print(f"Режим опроса через TOR: {tor_status}")
        if not USE_TOR:
            print(f"{Colors.YELLOW}Включить TOR режим: /tn{Colors.RESET}")
    elif command in ['/toron', '/tn']:
        USE_TOR = True
        print(f"{Colors.GREEN}Режим опроса через TOR включен.{Colors.RESET}")
    elif command in ['/toroff', '/tf']:
        USE_TOR = False
        print(f"{Colors.YELLOW}Режим опроса через TOR выключен.{Colors.RESET}")
    else:
        print(f"{Colors.RED}Неизвестная команда: {command}{Colors.RESET}")

def save_dialog_history():
    global dialog_history
    try:
        if len(dialog_history) > MAX_HISTORY_LENGTH:
            dialog_history = dialog_history[-MAX_HISTORY_LENGTH:]
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding='utf-8') as file:
            json.dump(dialog_history, file, ensure_ascii=False, indent=2)
        logger.info(f"История диалога сохранена в {HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения истории диалога: {e}")

def load_dialog_history():
    global dialog_history
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        try:
            with open(HISTORY_FILE, "r", encoding='utf-8') as file:
                dialog_history = json.load(file)
            logger.info(f"История диалога загружена из {HISTORY_FILE}")
        except Exception as e:
            logger.error(f"Ошибка загрузки истории диалога: {e}")
            dialog_history = []
    else:
        dialog_history = []

def query_ddgr(search_query):
    global USE_TOR
    cleaned_query = clean_query(search_query)
    command = ["torsocks", "ddgr", "--json", cleaned_query] if USE_TOR else ["ddgr", "--json", cleaned_query]
    
    print(f"{Colors.YELLOW}Отладка: Использование TOR: {'Да' if USE_TOR else 'Нет'}{Colors.RESET}")
    print(f"{Colors.YELLOW}Отладка: Выполняемая команда: {' '.join(command)}{Colors.RESET}")
    
    try:
        result = subprocess.check_output(command, universal_newlines=True)
        if "[ERROR]" in result:
            print(f"{Colors.RED}Отладка: Получена ошибка: {result}{Colors.RESET}")
            return None
        print(f"{Colors.GREEN}Отладка: Запрос успешно выполнен{Colors.RESET}")
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Отладка: Ошибка выполнения команды: {e}{Colors.RESET}")
        return None
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Отладка: Ошибка разбора JSON: {e}{Colors.RESET}")
        return None

def perform_search(queries):
    results = []
    for i, query in enumerate(queries, 1):
        for attempt in range(3):
            if USE_TOR:
                print("Отладка: Проверка и перезапуск TOR перед запросом ddgr...")
                restart_tor_and_check_ddgr()
            result = query_ddgr(query)
            if result:
                results.append(result)
                print(f"Ответ на запрос {i} получен. Обрабатываю...")
                print_intermediate_result(result)
                break
            else:
                print(f"Попытка {attempt + 1} не удалась. {'Повторяю запрос...' if attempt < 2 else 'Переход к следующему запросу.'}")
                time.sleep(2)
        if not result:
            print(f"Не удалось получить результаты для запроса {i} после 3 попыток")
    return results

def print_intermediate_result(result):
    if isinstance(result, list) and len(result) > 0:
        print(f"Найдено {len(result)} результатов:")
        for i, item in enumerate(result[:3], 1):  # Выводим первые 3 результата
            title = item.get('title', 'Без названия')
            url = item.get('url', 'URL отсутствует')
            print(f"{i}. {title}\n   {url}\n")
    else:
        print("Нет доступных промежуточных результатов для отображения.")

def get_local_ip():
    try:
        return subprocess.check_output("hostname -I | awk '{print $1}'", shell=True).decode().strip()
    except subprocess.CalledProcessError:
        return "Не удалось получить локальный IP"

def check_tor_status():
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

def check_tor_settings():
    try:
        with open('/etc/tor/torrc', 'r') as f:
            content = f.read()
            if 'ExcludeExitNodes' in content:
                print("TOR настроен для исключения определенных выходных узлов.")
                
        torsocks_output = subprocess.check_output(['torsocks', 'show_conf'], universal_newlines=True)
        
        if 'local = 127.0.0.0/255.0.0.0' in torsocks_output:
            print("torsocks настроен для пропуска локальных адресов.")
            
    except Exception as e:
        print(f"Не удалось проверить настройки TOR: {e}")

def clean_query(query):
    return query.replace('"', '')

def get_current_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')

def query_llm(prompt, include_history=True):
    global dialog_history
    
    current_datetime = get_current_datetime()
    
    if include_history:
        context = "\n".join([f"{entry['role']}: {entry['content']}" for entry in dialog_history[-5:]])
        
        full_prompt = f"Текущая дата и время: {current_datetime}\n\n{context}\n\nТекущий запрос: {prompt}"
        
    else:
        full_prompt = f"Текущая дата и время: {current_datetime}\n\n{prompt}"

   payload = {
       "model": MODEL,
       "prompt": full_prompt,
       "stream": False,
   }

   try:
       response = requests.post(LLM_API_URL, json=payload)
       response.raise_for_status()
       return response.json().get("response", "<Нет ответа>")
   except requests.RequestException as e:
       logger.error(f"Ошибка запроса к модели: {e}")
       return None

def preprocess_query(user_input):
   system_prompt = """Проанализируй запрос пользователя и сформулируй до трех связанных поисковых запросов для расширения контекста."""

   context = f"Запрос пользователя: {user_input}\n\n{system_prompt}"
   response = query_llm(context, include_history=False)

   if response is None:
       return {"queries": [user_input], "instruction": "Обработайте результаты поиска и предоставьте краткий ответ."}
   
   preprocessed_data = parse_preprocessing_response(response)

   return preprocessed_data

def parse_preprocessing_response(response):
   lines = response.split('\n')
   queries = []
   instruction_lines=[]
   
   for line in lines:

       # Извлекаем основной запрос и дополнительные запросы из ответа модели.
       if line.startswith("Основной запрос:"):
           queries.append(line.split(": ", 1)[1].strip())
       elif line.startswith(("1. ", "2. ", "3. ")) and len(queries) > 0 :
           queries.append(line.split(". ", 1)[1].strip())
       elif line.startswith("Инструкция для обработки результатов:"):
           instruction_lines.append(line.split(": ", 1)[1].strip())

   instruction=" ".join(instruction_lines).strip()

   return {
       "queries": queries[:3],
       "instruction": instruction,
   }

def process_search_results(search_results, instruction, user_language):
   if not search_results or len(search_results) == 0:
       return "К сожалению, не удалось найти информацию по вашему запросу."

   context=f"""Инструкция: {instruction}

Результаты поиска:{json.dumps(search_results, ensure_ascii=False, indent=2)}

Текущая дата и время:{get_current_datetime()}

Пожалуйста, проанализируйте предоставленные результаты поиска и сформируйте ответ на вопрос пользователя."""

   response=query_llm(context, include_history=True)

   # Обработка ответа от модели.
   if response is None or response.strip() == "":
       return ("Извините, не удалось обработать результаты поиска. "
               "Пожалуйста, попробуйте еще раз или переформулируйте запрос.")
   
   return response

def save_temp_result(result, query_number):
   TEMP_DIR.mkdir(exist_ok=True)
   file_path = TEMP_DIR / f"result_{query_number}_{uuid.uuid4()}.json"
   with open(file_path, "w", encoding='utf-8') as file:
       json.dump(result, file, ensure_ascii=False, indent=2)

def process_intermediate_result(result, query_number):
   print(f"{Colors.GREEN}Промежуточный результат для запроса {query_number}:{Colors.RESET}")
   if result and isinstance(result, list) and len(result) > 0:
       print(f"Найдено {len(result)} результатов:")
       for i, item in enumerate(result[:3], 1):  # Выводим первые 3 результата
           title = item.get('title', 'Без названия')
           url = item.get('url', 'URL отсутствует')
           print(f"{i}. {title}\n   {url}\n")
   else:
       print("Нет доступных промежуточных результатов для отображения.")

def save_report(preprocessed, response):
   with open(REPORT_FILE, "a", encoding='utf-8') as file:
       file.write(f"Дата и время: {get_current_datetime()}\n")
       file.write(f"Запросы:\n{json.dumps(preprocessed['queries'], ensure_ascii=False, indent=2)}\n")
       file.write(f"Инструкция:\n{preprocessed['instruction']}\n")
       file.write(f"Ответ модели:\n{response}\n")
       file.write("-" * 50 + "\n")

def detect_language(text):
   if re.search('[а-яА-Я]', text):
       return 'ru'
   else:
       return 'en'
