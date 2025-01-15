#!/usr/bin/env python3
# agents/data_management.py
# Version: 1.3.0
# Purpose: Handle data and dialog history management for the cognitive agent.

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
HISTORY_FILE = Path("history/dialog_history.json")
MAX_HISTORY_LENGTH = 100


def save_dialog_history(dialog_history):
    try:
        if not isinstance(dialog_history, list):
            logger.error("Invalid dialog history format. Expected a list.")
            return False

        if len(dialog_history) > MAX_HISTORY_LENGTH:
            dialog_history = dialog_history[-MAX_HISTORY_LENGTH:]

        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(dialog_history, file, ensure_ascii=False, indent=2)
        logger.info(f"Dialog history successfully saved to {HISTORY_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving dialog history: {e}")
        return False


def load_dialog_history():
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)
                if isinstance(history, list):
                    logger.info(f"Loaded dialog history from {HISTORY_FILE}")
                    return history
                else:
                    logger.warning("Invalid format in dialog history file. Resetting to empty list.")
        except json.JSONDecodeError:
            logger.error("Failed to decode dialog history file. Resetting to empty list.")
        except Exception as e:
            logger.error(f"Error loading dialog history: {e}")
    else:
        logger.warning("No dialog history found or file is empty.")
    return []


def verify_history_saved():
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        logger.info(f"Verified that dialog history exists at {HISTORY_FILE}.")
        return True
    else:
        logger.error(f"Dialog history verification failed: File {HISTORY_FILE} is missing or empty.")
        return False


def save_temp_result(result, query_number, temp_dir=Path("temp")):
    try:
        temp_dir.mkdir(exist_ok=True)
        file_path = temp_dir / f"result_{query_number}.json"
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
        logger.info(f"Temporary result saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving temporary result: {e}")


def detect_language(text):
    import re
    logger.debug(f"Detecting language for text: {text[:30]}...")
    if re.search('[а-яА-Я]', text):
        logger.info("Detected language: Russian")
        return 'ru'
    else:
        logger.info("Detected language: English")
        return 'en'


def print_message(role, message):
    color = "\033[94m" if role == "User" else "\033[92m"
    reset = "\033[0m"
    logger.debug(f"{role}: {message}")
    print(f"{color}{role}: {message}{reset}")
