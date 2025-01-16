#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.0.0
# ==================================================

import socket
import requests
from colors import Colors
from settings import LLM_API_URL

def get_ip_address():
    """Получает локальный IP-адрес."""
    return socket.gethostbyname(socket.gethostname())

def check_tor_ip():
    """Возвращает текущий IP-адрес, используемый TOR."""
    try:
        response = requests.get("https://api.ipify.org", proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"})
        return response.text
    except Exception as e:
        return f"{Colors.RED}Ошибка получения IP TOR: {str(e)}{Colors.RESET}"

def check_llm_api_status():
    """Проверяет доступность API LLM."""
    try:
        response = requests.get(LLM_API_URL, timeout=5)
        if response.status_code == 200:
            return f"{Colors.GREEN}Доступен{Colors.RESET}"
        return f"{Colors.YELLOW}Ошибка: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Недоступен: {str(e)}{Colors.RESET}"

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
            # Проверяем существование файла
            absolute_path = Path(path).resolve()
            if not absolute_path.is_file():
                raise FileNotFoundError(f"Файл {absolute_path} не найден.")

            # Читаем файл и ищем версию
            with open(absolute_path, "r", encoding="utf-8") as file:
                for line in file:
                    if "Версия:" in line or "Version:" in line:
                        versions[name] = line.strip().split(":")[1].strip()
                        break
                else:
                    versions[name] = f"{Colors.YELLOW}Версия не указана{Colors.RESET}"
        except FileNotFoundError as e:
            versions[name] = f"{Colors.RED}Файл не найден: {str(e)}{Colors.RESET}"
        except Exception as e:
            versions[name] = f"{Colors.RED}Ошибка: {str(e)}{Colors.RESET}"
    return versions


def show_info(use_tor, log_level):
    """Отображает информацию об агенте."""
    print(Colors.CYAN + Colors.BOLD)
    print("╔═══════════════════════════════════════════════╗")
    print("║          Информация о текущих режимах         ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f"{Colors.GREEN}Текущий режим логирования: {Colors.RESET}{log_level}")
    print(f"{Colors.GREEN}Режим TOR: {Colors.RESET}{'Включен' if use_tor else 'Отключен'}")
    print(f"{Colors.GREEN}Локальный IP-адрес: {Colors.RESET}{get_ip_address()}")
    print(f"{Colors.GREEN}IP TOR: {Colors.RESET}{check_tor_ip()}")
    print(f"{Colors.GREEN}Доступность LLM API: {Colors.RESET}{check_llm_api_status()}")

    print(f"\n{Colors.BOLD}Версии скриптов:{Colors.RESET}")
    for script, version in get_script_versions().items():
        print(f"{Colors.YELLOW}{script}: {Colors.RESET}{version}")

    print(Colors.GRAY + Colors.HORIZONTAL_LINE + Colors.RESET)

if __name__ == "__main__":
    # Заглушки для демонстрации
    USE_TOR = True  # Или False
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
