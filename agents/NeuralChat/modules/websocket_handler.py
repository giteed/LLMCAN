#!/usr/bin/env python3
# LLMCAN/agents/NeuralChat/modules/websocket_handler.py
# ===========================================
# Модуль для обработки WebSocket в NeuralChat.
# ===========================================
# Версия: 1.0 (2023-10-10)
# - Первоначальная реализация.
# ===========================================

import asyncio
import websockets
from .logging import logger  # Импортируем логгер

async def handle_connection(websocket, path):
    logger.info("Новое подключение через WebSocket.")
    async for message in websocket:
        logger.info(f"Получено сообщение: {message}")
        await websocket.send(f"Эхо: {message}")

# Пример использования:
# start_server = websockets.serve(handle_connection, "0.0.0.0", 8765)
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
