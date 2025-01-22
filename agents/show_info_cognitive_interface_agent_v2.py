#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.3.0
# ==================================================

import socket
import requests
from pathlib import Path
from colors import Colors
import time

# Импорт из settings
from settings import (
    LLM_API_HEALTH,
    LLM_API_TAGS,
    LLM_API_GENERATE,
    LLM_API_BASE
)

def get_ip_address():
    """Получает локальный IP-адрес."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        return f"{Colors.RED}Ошибка получения IP: {str(e)}{Colors.RESET}"

def check_tor_ip():
    """Возвращает текущий IP-адрес, используемый TOR."""
    try:
        response = requests.get(
            "https://api.ipify.org",
            proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
            timeout=10
        )
        return response.text
    except Exception as e:
        return f"{Colors.RED}Ошибка получения IP TOR: {str(e)}{Colors.RESET}"

def check_llm_api_status():
    """Проверяет доступность API LLM."""
    try:
        response = requests.get(LLM_API_HEALTH, timeout=5)
        if response.status_code == 200:
            return f"{Colors.WHITE}API доступен.\n Ollama работает.{Colors.RESET}"
        return (
            f"{Colors.YELLOW}Базовый URL доступен, но эндпоинт вернул код "
            f"{response.status_code}{Colors.RESET}"
        )
    except Exception as e:
        return f"{Colors.RED}API недоступен: {str(e)}{Colors.RESET}"

def get_ollama_version():
    """Получает версию Ollama API."""
    try:
        response = requests.get(f"{LLM_API_BASE}/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            return f"{Colors.GREEN} - {Colors.RESET}{version_info.get('version', 'Не указано')}"
        return f"{Colors.RED}Ошибка получения версии Ollama: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка получения версии Ollama: {str(e)}{Colors.RESET}"

def get_ollama_models():
    """Получает список доступных моделей Ollama и форматирует их."""
    try:
        response = requests.get(LLM_API_TAGS, timeout=5)
        if response.status_code == 200:
            data = response.json()  # {'models': [ {...}, {...}, ... ] }
            models_list = data.get("models", [])

            if not models_list:
                return f" {Colors.YELLOW}Список моделей пуст.{Colors.RESET}"

            lines = []
            for model_info in models_list:
                name = model_info.get("name", "—")
                size = model_info.get("size", "—")
                modified = model_info.get("modified_at", "—")

                details = model_info.get("details", {})
                family = details.get("family", "—")
                param_size = details.get("parameter_size", "—")
                quant_level = details.get("quantization_level", "—")

                lines.append(
                    f" Модель: {Colors.BOLD}{name}{Colors.RESET}\n"
                    f"   - Семейство: {family}\n"
                    f"   - Параметры: {param_size}\n"
                    f"   - Квант.: {quant_level}\n"
                    f"   - Размер: {size}\n"
                    f"   - Изменено: {modified}\n"
                )

            pretty_output = "\n".join(lines)
            return (
                f" {Colors.RED}  ------------------------------- {Colors.RESET}\n{pretty_output}\n"
                f" {Colors.BLUE + Colors.BOLD}\n"
                f" ╔═══════════════════════════════════════════════╗\n"
                f" ║       Как скачать новые модели?               ║\n"
                f" ╚═══════════════════════════════════════════════╝\n"
                f" {Colors.RESET}1. Перейдите на {Colors.UNDERLINE}https://ollama.ai/models{Colors.RESET}.\n"
                f" 2. Загрузите модели в формате GGUF.\n"
                f" 3. Скопируйте их в директорию Ollama.\n\n"
                f" {Colors.BOLD}Инструкция по локальной установке (Ubuntu 22-24)\n и использованию Ollama:{Colors.RESET}\n\n"
                f" {Colors.UNDERLINE}Шаг 1: Установка Ollama{Colors.RESET}\n"
                f" sudo apt update\n"
                f" sudo apt install -y curl\n"
                f" curl -sSL https://ollama.com/download.sh | sh\n\n"
                f" {Colors.UNDERLINE}Шаг 2: Скачивание сразу нескольких моделей (пример){Colors.RESET}\n"
                f" ollama pull deepseek-r1:1.5b & \\\n"
                f" ollama pull deepseek-r1:8b & \\\n"
                f" ollama pull deepseek-r1:14b & \\\n"
                f" ollama pull deepseek-r1:70b &\n\n"
                f" {Colors.UNDERLINE}Шаг 3: Проверка доступных моделей{Colors.RESET}\n"
                f" ollama list\n\n"
                f" {Colors.UNDERLINE}Примечание:{Colors.RESET} \n{Colors.DARK_GRAY} Для получения дополнительной информации о командах{Colors.RESET}\n"
                f" ollama help\n\n"
                f" {Colors.UNDERLINE}Дополнительные шаги:{Colors.RESET}\n"
                f" {Colors.RESET}1. Перейдите на {Colors.UNDERLINE}https://ollama.ai/models{Colors.RESET}.\n"
                f" 2. Загрузите модели в формате GGUF.\n"
                f" 3. Скопируйте их в директорию Ollama."
            )
        else:
            return (
                f" {Colors.RED}Ошибка получения моделей: "
                f"{response.status_code}, {response.text}{Colors.RESET}"
            )
    except Exception as e:
        return f" {Colors.RED}Ошибка получения моделей: {str(e)}{Colors.RESET}"

def test_ollama_query():
    """Выполняет тестовый запрос к API LLM и красиво выводит результат."""
    import json
    try:
        payload = {
            "model": "qwen2:7b",
            "prompt": "Готов к работе?",
            "stream": False
        }
        start_time = time.time()
        response = requests.post(LLM_API_GENERATE, json=payload, timeout=5)
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            model_name = payload.get("model", "—")
            prompt_text = payload.get("prompt", "—")
            answer_text = data.get("response", "Нет ответа")

            output = (
                f" {Colors.BLUE + Colors.BOLD}\n"
                f" ╔═══════════════════════════════════════════════╗\n"
                f" ║           Тестовый запрос к модели            ║\n"
                f" ╚═══════════════════════════════════════════════╝\n"
                f" {Colors.RESET}{Colors.GREEN}Модель: {Colors.RESET}{model_name}\n"
                f" {Colors.MAGENTA}Запрос (prompt):{Colors.RESET} {prompt_text}\n"
                f" {Colors.CYAN}Ответ (response):{Colors.RESET} {answer_text}\n"
                f" {Colors.YELLOW}Время выполнения: {elapsed_time:.2f} сек.{Colors.RESET}"
            )
            return output
        else:
            return f" {Colors.RED}Ошибка тестового запроса: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f" {Colors.RED}Ошибка тестового запроса: {str(e)}{Colors.RESET}"


def get_script_versions():
    """Возвращает версии скриптов из их заголовков."""
    script_files = {
        "cognitive_interface_agent_v2.py": "./agents/cognitive_interface_agent_v2.py",
        "cognitive_logic.py": "./agents/cognitive_logic.py",
        "data_management.py": "./agents/data_management.py",
        "preprocess_query.py": "./agents/preprocess_query.py"
    }
    versions = {}
    for name, path in script_files.items():
        try:
            with open(Path(path).resolve(), "r", encoding="utf-8") as file:
                for line in file:
                    if "Версия:" in line or "Version:" in line:
                        versions[name] = line.strip().split(":")[1].strip()
                        break
                else:
                    versions[name] = f"{Colors.YELLOW}Версия не указана{Colors.RESET}"
        except FileNotFoundError:
            versions[name] = f"{Colors.RED}Файл не найден{Colors.RESET}"
        except Exception as e:
            versions[name] = f"{Colors.RED}Ошибка: {str(e)}{Colors.RESET}"
    return versions

def show_info(use_tor, log_level):
    """Отображает информацию об агенте в разделах."""
    print(" " + Colors.CYAN + Colors.BOLD)
    print(" ╔═══════════════════════════════════════════════╗")
    print(" ║                Информация о сервере           ║")
    print(" ╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f" {Colors.GREEN}Локальный IP-адрес: {Colors.RESET}{get_ip_address()}")
    print(f" {Colors.GREEN}IP TOR: {Colors.RESET}{check_tor_ip()}")
    print(f" {Colors.GREEN}Режим TOR: {Colors.RESET}{'Включен' if use_tor else 'Отключен'}")
    print(f" {Colors.GREEN}Текущий режим логирования: {Colors.RESET}{log_level}")

    print(" " + Colors.BLUE + Colors.BOLD)
    print(" ╔═══════════════════════════════════════════════╗")
    print(" ║              Информация о LLM и API           ║")
    print(" ╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f" {Colors.GREEN}Доступность LLM API: {Colors.RESET}\n {check_llm_api_status()}")
    print(f" {Colors.GREEN}Версия Ollama: {Colors.RESET}{get_ollama_version()}")
    print(f" {Colors.GREEN}Модели Ollama: {Colors.RESET}{get_ollama_models()}")
    print(" " + test_ollama_query())

    print(" " + Colors.YELLOW + Colors.BOLD)
    print(" ╔═══════════════════════════════════════════════╗")
    print(" ║       Информация о скриптах и настройках      ║")
    print(" ╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f" {Colors.BOLD}Версии скриптов:{Colors.RESET}")
    for script, version in get_script_versions().items():
        print(f" {Colors.YELLOW}{script}: {Colors.RESET}{version}")

    print(" " + Colors.GRAY + Colors.HORIZONTAL_LINE + Colors.RESET)

if __name__ == "__main__":
    USE_TOR = True  # Или False
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
