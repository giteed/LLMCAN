#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/modules/mqtt_handler.py
# ===========================================
# Модуль для обработки MQTT в NeuralChat.
# ===========================================
# Версия: 1.0 (2023-10-10)
# - Первоначальная реализация.
# ===========================================

import paho.mqtt.client as mqtt
from .logging import logger  # Импортируем логгер

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Успешное подключение к MQTT-брокеру.")
    else:
        logger.error(f"Ошибка подключения к MQTT-брокеру: Код {rc}")

def on_message(client, userdata, message):
    logger.info(f"Получено сообщение: {message.payload.decode()}")

# Пример использования:
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect("mqtt_broker_address", 1883, 60)
# client.loop_forever()
