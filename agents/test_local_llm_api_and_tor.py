import requests
import socks
import socket
import logging
import subprocess

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
LLM_API_URL = "http://10.67.67.2:11434/api/generate"
USE_TOR = True
original_socket = None

def toggle_tor(enable=True):
    global USE_TOR, original_socket
    if enable:
        if not USE_TOR:
            original_socket = socket.socket
            socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
            socket.socket = socks.socksocket
            USE_TOR = True
            logger.info("TOR включен")
    else:
        if USE_TOR and original_socket:
            socket.socket = original_socket
            socks.set_default_proxy()
            USE_TOR = False
            logger.info("TOR выключен")

def test_llm_connection():
    logger.info("Начало теста подключения к LLM API")
    
    payload = {
        "model": "qwen2:7b",
        "prompt": "Тестовый запрос",
        "stream": False
    }

    try:
        logger.info(f"Отправка запроса к {LLM_API_URL}")
        with requests.Session() as session:
            if USE_TOR:
                session.proxies = {
                    'http': 'socks5h://localhost:9050',
                    'https': 'socks5h://localhost:9050'
                }
            else:
                session.proxies = {}
            response = session.post(LLM_API_URL, json=payload, timeout=10)
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Содержимое ответа: {response.text[:100]}...")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return None

def check_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        logger.info(f"Текущий IP-адрес: {ip}")
    except requests.RequestException as e:
        logger.error(f"Не удалось получить IP-адрес: {e}")

def check_tor_status():
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    logger.info("Проверка статуса TOR")
    tor_status = check_tor_status()
    logger.info(f"Статус TOR: {'включен' if tor_status else 'выключен'}")

    logger.info("Тест без использования TOR")
    toggle_tor(False)
    check_ip()
    result = test_llm_connection()
    if result:
        logger.info("Тест без TOR успешно завершен")
    else:
        logger.error("Тест без TOR завершился с ошибкой")

    logger.info("Включение TOR")
    toggle_tor(True)
    check_ip()
    result = test_llm_connection()
    if result:
        logger.info("Тест с TOR успешно завершен")
    else:
        logger.error("Тест с TOR завершился с ошибкой")

    logger.info("Выключение TOR")
    toggle_tor(False)
    check_ip()
import requests
import socks
import socket
import logging
import subprocess

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
LLM_API_URL = "http://10.67.67.2:11434/api/generate"
USE_TOR = True

def toggle_tor(enable=True):
    global USE_TOR
    if enable:
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
        socket.socket = socks.socksocket
        USE_TOR = True
        logger.info("TOR включен")
    else:
        socket.socket = socket._real_socket
        USE_TOR = False
        logger.info("TOR выключен")

def test_llm_connection():
    logger.info("Начало теста подключения к LLM API")
    
    payload = {
        "model": "qwen2:7b",
        "prompt": "Тестовый запрос",
        "stream": False
    }

    try:
        logger.info(f"Отправка запроса к {LLM_API_URL}")
        with requests.Session() as session:
            if USE_TOR:
                session.proxies = {
                    'http': 'socks5h://localhost:9050',
                    'https': 'socks5h://localhost:9050'
                }
            else:
                session.proxies = {}
            response = session.post(LLM_API_URL, json=payload, timeout=10)
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Содержимое ответа: {response.text[:100]}...")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return None

def check_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        logger.info(f"Текущий IP-адрес: {ip}")
    except requests.RequestException as e:
        logger.error(f"Не удалось получить IP-адрес: {e}")

def check_tor_status():
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    logger.info("Проверка статуса TOR")
    tor_status = check_tor_status()
    logger.info(f"Статус TOR: {'включен' if tor_status else 'выключен'}")

    logger.info("Тест без использования TOR")
    toggle_tor(False)
    check_ip()
    result = test_llm_connection()
    if result:
        logger.info("Тест без TOR успешно завершен")
    else:
        logger.error("Тест без TOR завершился с ошибкой")

    logger.info("Включение TOR")
    toggle_tor(True)
    check_ip()
    result = test_llm_connection()
    if result:
        logger.info("Тест с TOR успешно завершен")
    else:
        logger.error("Тест с TOR завершился с ошибкой")

    logger.info("Выключение TOR")
    toggle_tor(False)
    check_ip()
