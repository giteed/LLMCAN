#!/usr/bin/env python3
# agents/data_management.py
# Version: 1.0.0
# Purpose: Handle data and dialog history management for the cognitive agent.

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
HISTORY_FILE = Path("history/dialog_history.json")
MAX_HISTORY_LENGTH = 100

def save_dialog_history(dialog_history):
    try:
        if len(dialog_history) > MAX_HISTORY_LENGTH:
            dialog_history = dialog_history[-MAX_HISTORY_LENGTH:]
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(dialog_history, file, ensure_ascii=False, indent=2)
        logger.info(f"Dialog history saved to {HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Error saving dialog history: {e}")

def load_dialog_history():
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Error loading dialog history: {e}")
    return []

def save_temp_result(result, query_number, temp_dir=Path("temp")):
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / f"result_{query_number}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

def detect_language(text):
    import re
    if re.search('[а-яА-Я]', text):
        return 'ru'
    else:
        return 'en'

def print_message(role, message):
    color = "\033[94m" if role == "User" else "\033[92m"
    reset = "\033[0m"
    print(f"{color}{role}: {message}{reset}")
