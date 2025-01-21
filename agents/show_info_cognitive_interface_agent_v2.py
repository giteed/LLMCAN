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
from settings import LLM_API_HEALTH, LLM_API_TAGS, LLM_API_GENERATE, LLM_API_BASE
import time

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
            return f"{Colors.GREEN}API доступен. Ollama работает.{Colors.RESET}"
        return f"{Colors.YELLOW}Базовый URL доступен, но эндпоинт вернул код {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}API недоступен: {str(e)}{Colors.RESET}"

def get_ollama_version():
    """Получает версию Ollama API."""
    try:
        response = requests.get(f"{LLM_API_BASE}/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            return f"{Colors.GREEN}Версия Ollama: {Colors.RESET}{version_info.get('version', 'Не указано')}"
        return f"{Colors.RED}Ошибка получения версии Ollama: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка получения версии Ollama: {str(e)}{Colors.RESET}"

def check_ollama_update():
    """Проверяет, доступна ли новая версия Ollama."""
    try:
        current_version = requests.get(f"{LLM_API_BASE}/api/version", timeout=5).json().get("version", "0.0.0")
        latest_version = requests.get("https://ollama.ai/api/latest-version", timeout=5).json().get("latest", "0.0.0")

        if current_version < latest_version:
            return (
                f"{Colors.YELLOW}Ваша версия: {current_version}{Colors.RESET}\n"
                f"{Colors.GREEN}Доступна новая версия: {latest_version}{Colors.RESET}\n"
                f"{Colors.MAGENTA}Рекомендуется обновить Ollama:{Colors.RESET}\n"
                f"1. Загрузите новую версию с {Colors.UNDERLINE}https://ollama.ai/downloads{Colors.RESET}\n"
                f"2. Следуйте инструкциям для обновления."
            )
        return f"{Colors.GREEN}Вы используете последнюю версию Ollama ({current_version}).{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка проверки обновлений: {str(e)}{Colors.RESET}"

def get_ollama_models():
    """Получает список доступных моделей Ollama и форматирует их."""
    try:
        response = requests.get(LLM_API_TAGS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            models_list = data.get("models", [])
            if not models_list:
                return f"{Colors.YELLOW}Список моделей пуст.{Colors.RESET}"

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
                    f"Модель: {Colors.BOLD}{name}{Colors.RESET}\n"
                    f"  - Семейство: {family}\n"
                    f"  - Параметры: {param_size}\n"
                    f"  - Квант.: {quant_level}\n"
                    f"  - Размер: {size}\n"
                    f"  - Изменено: {modified}\n"
                )

            pretty_output = "\n".join(lines)
            return (
                f"{Colors.GREEN}Список моделей Ollama:{Colors.RESET}\n{pretty_output}\n"
                f"{Colors.MAGENTA}Как скачать новые модели?{Colors.RESET}\n"
                f"1. Откройте URL для загрузки: {Colors.UNDERLINE}http://ollama.ai/models{Colors.RESET}\n"
                f"2. Загрузите модель в формате GGUF.\n"
                f"3. Переместите её в директорию Ollama."
            )

        else:
            return f"{Colors.RED}Ошибка получения моделей: {response.status_code}, {response.text}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка получения моделей: {str(e)}{Colors.RESET}"

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
                f"{Colors.GREEN}Тестовый запрос к модели: {Colors.RESET}{model_name}\n"
                f"{Colors.MAGENTA}Запрос (prompt):{Colors.RESET} {prompt_text}\n"
                f"{Colors.CYAN}Ответ (response):{Colors.RESET} {answer_text}\n"
                f"{Colors.YELLOW}Время ответа: {elapsed_time:.2f} сек.{Colors.RESET}"
            )
            return output
        else:
            return f"{Colors.RED}Ошибка тестового запроса: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка тестового запроса: {str(e)}{Colors.RESET}"

def show_info(use_tor, log_level):
    """Отображает информацию об агенте в разделах."""
    print(Colors.CYAN + Colors.BOLD)
    print("╔═══════════════════════════════════════════════╗")
    print("║                Информация о сервере           ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f"{Colors.GREEN}Локальный IP-адрес: {Colors.RESET}{get_ip_address()}")
    print(f"{Colors.GREEN}IP TOR: {Colors.RESET}{check_tor_ip()}")
    print(f"{Colors.GREEN}Режим TOR: {Colors.RESET}{'Включен' if use_tor else 'Отключен'}")
    print(f"{Colors.GREEN}Текущий режим логирования: {Colors.RESET}{log_level}")

    print(Colors.BLUE + Colors.BOLD)
    print("\n╔═══════════════════════════════════════════════╗")
    print("║              Информация о LLM и API           ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f"{Colors.GREEN}Доступность LLM API: {Colors.RESET}{check_llm_api_status()}")
    print(f"{Colors.GREEN}Версия Ollama: {Colors.RESET}{get_ollama_version()}")
    print(f"{Colors.GREEN}Проверка обновлений: {Colors.RESET}{check_ollama_update()}")
    print(f"{Colors.GREEN}Модели Ollama: {Colors.RESET}{get_ollama_models()}")
    print(f"{Colors.GREEN}Тестовый запрос к модели: {Colors.RESET}{test_ollama_query()}")

if __name__ == "__main__":
    USE_TOR = True
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
