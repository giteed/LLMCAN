#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.2.0
# ==================================================

import socket
import requests
from pathlib import Path
from colors import Colors
from settings import LLM_API_URL

def get_ip_address():
    """Получает локальный IP-адрес."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        return f"{Colors.RED}Ошибка получения IP: {str(e)}{Colors.RESET}"

def check_tor_ip():
    """Возвращает текущий IP-адрес через TOR."""
    try:
        response = requests.get(
            "https://api.ipify.org",
            proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
            timeout=10
        )
        return response.text
    except Exception as e:
        return f"{Colors.RED}Ошибка получения IP через TOR: {str(e)}{Colors.RESET}"

def ping_server(server_url, count=3):
    """Пингует сервер и возвращает статистику."""
    import subprocess
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), server_url.split("//")[-1].split("/")[0]],
            text=True, capture_output=True
        )
        return result.stdout if result.returncode == 0 else f"{Colors.RED}Сервер недоступен{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка выполнения пинга: {str(e)}{Colors.RESET}"

def list_available_models():
    """Выводит список доступных моделей API Ollama."""
    try:
        response = requests.get(f"{LLM_API_URL}models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return models if models else f"{Colors.YELLOW}Нет доступных моделей{Colors.RESET}"
        return f"{Colors.RED}Ошибка получения моделей: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка при запросе моделей: {str(e)}{Colors.RESET}"

def test_model_request():
    """Тестовый запрос к модели."""
    try:
        payload = {"model": "default", "prompt": "Привет, как дела?"}
        response = requests.post(LLM_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json().get("response", f"{Colors.YELLOW}Ответа нет{Colors.RESET}")
        return f"{Colors.RED}Ошибка тестового запроса: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка выполнения тестового запроса: {str(e)}{Colors.RESET}"

def show_info(use_tor, log_level):
    """Отображает информацию об агенте."""
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
    print(f"{Colors.GREEN}Доступность LLM API: {Colors.RESET}{ping_server(LLM_API_URL)}")
    print(f"{Colors.GREEN}Модели Ollama: {Colors.RESET}{list_available_models()}")
    print(f"{Colors.GREEN}Тестовый запрос к модели: {Colors.RESET}{test_model_request()}")

    print(Colors.YELLOW + Colors.BOLD)
    print("\n╔═══════════════════════════════════════════════╗")
    print("║       Информация о скриптах и настройках      ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    script_files = {
        "cognitive_interface_agent_v2.py": "./agents/cognitive_interface_agent_v2.py",
        "cognitive_logic.py": "./agents/cognitive_logic.py",
        "data_management.py": "./agents/data_management.py",
        "preprocess_query.py": "./agents/preprocess_query.py",
    }
    for script, path in script_files.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                version = next((line.split(":")[1].strip() for line in f if "Версия:" in line), "Версия не указана")
                print(f"{Colors.YELLOW}{script}: {Colors.RESET}{version}")
        except FileNotFoundError:
            print(f"{Colors.RED}{script}: Файл не найден{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}{script}: Ошибка: {str(e)}{Colors.RESET}")

    print(Colors.GRAY + Colors.HORIZONTAL_LINE + Colors.RESET)

if __name__ == "__main__":
    USE_TOR = True
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
