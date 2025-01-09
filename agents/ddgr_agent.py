#!/usr/bin/env python3
# ddgr_agent.py
# v. 1.0
# Этот скрипт выполняет следующие действия:
# Запрашивает у пользователя поисковый запрос.
# Формирует команду для ddgr, используя флаг --json для получения результатов в формате JSON.
# Выполняет команду ddgr с помощью subprocess.check_output().
# Записывает полученный результат в файл "search_results.txt".
# Обрабатывает возможные ошибки и выводит соответствующие сообщения.
import subprocess
import sys

# Получаем поисковый запрос от пользователя
search_query = input("Введите поисковый запрос: ")

# Формируем команду для ddgr
command = ["ddgr", "--json", search_query]

try:
    # Выполняем команду и получаем результат
    result = subprocess.check_output(command, universal_newlines=True)

    # Записываем результат в файл
    with open("search_results.txt", "w", encoding="utf-8") as file:
        file.write(result)

    print("Результаты поиска сохранены в файл 'search_results.txt'")

except subprocess.CalledProcessError as e:
    print(f"Произошла ошибка при выполнении ddgr: {e}")
except IOError as e:
    print(f"Произошла ошибка при записи в файл: {e}")
except Exception as e:
    print(f"Произошла неизвестная ошибка: {e}")
