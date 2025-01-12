import requests
import socks
import socket
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
LLM_API_URL = "http://10.67.67.2:11434/api/generate"
USE_TOR = True

def test_llm_connection():
    logger.info("Начало теста подключения к LLM API")
    
    if USE_TOR:
        logger.info("Настройка TOR соединения")
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
        socket.socket = socks.socksocket
    
    payload = {
        "model": "qwen2:7b",
        "prompt": "Тестовый запрос",
        "stream": False
    }

    try:
        logger.info(f"Отправка запроса к {LLM_API_URL}")
        response = requests.post(LLM_API_URL, json=payload, timeout=10)
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Содержимое ответа: {response.text[:100]}...")  # Выводим первые 100 символов ответа
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return None

if __name__ == "__main__":
    result = test_llm_connection()
    if result:
        logger.info("Тест успешно завершен")
    else:
        logger.error("Тест завершился с ошибкой")
