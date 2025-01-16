#!/usr/bin/env python3
# agents/cognitive_logic.py
# Version: 1.2.1
# Purpose: Define cognitive logic and LLM interaction for the agent.

import json
import logging
from datetime import datetime
from colors import Colors  # Импортируем Colors из внешнего файла

logger = logging.getLogger(__name__)

def generate_system_instruction():
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    instruction = f"""You are a cognitive agent. Current date and time: {current_datetime}.
Your task is to provide a structured response based on a user query and an array of 20-30 links with descriptions. Follow these guidelines:

1. Analyze the user query and relevant sources from the provided links.
2. Generate a comprehensive, structured answer based on the information found.
3. Format your response as follows:

   ### Тема ответа пользователю:
   [Brief formulation of the response topic]

   [Detailed answer to the user's query]

   ## Вывод:
   На основе полученных данных можно сделать следующие выводы:
   [List 3-5 key conclusions based on the provided information]

   ## Интересные моменты:
   1. [First interesting aspect or fact from the analysis]
   2. [Second interesting aspect or fact from the analysis]
   3. [Third interesting aspect or fact from the analysis]

   ## Источники:
   [List of sources used, formatted as: Brief description of the source (Link)]

4. Ensure the answer is logically structured, informative, and relevant to the user's query.
5. Use a professional and neutral tone in your response.
6. Do not use tables in your response.
7. For the sources section, provide a brief description of each used source, followed by its link in parentheses. Each source should be on a new line.
8. If you lack sufficient information for a complete answer, state this in the "Вывод" section.
9. Do not use phrases like "According to the search results" or "Based on the provided information".

Remember to adapt your response to the specific query and available information."""
    logger.debug(f"Generated system instruction: {instruction}")
    return instruction


def preprocess_query(user_input):
    logger.debug(f"Preprocessing user input: {user_input}")
    queries = [user_input]
    instruction = "Process results and provide a summary."
    logger.debug(f"Generated queries: {queries}, Instruction: {instruction}")
    return {"queries": queries, "instruction": instruction}

def process_search_results(instruction, search_results, user_language):
    """
    Обрабатывает результаты поиска и возвращает сформулированный ответ.
    
    Args:
        instruction (str): Инструкция для обработки.
        search_results (list): Список результатов поиска.
        user_language (str): Язык пользователя ('ru' или 'en').
    
    Returns:
        str: Сформулированный ответ.
    """
    try:
        if not search_results:
            return "Результаты поиска отсутствуют." if user_language == 'ru' else "No search results found."

        # Формирование ответа
        response = []
        for i, result in enumerate(search_results[:10], start=1):
            title = result.get("title", "Без названия") if user_language == 'ru' else result.get("title", "No title")
            url = result.get("url", "URL отсутствует") if user_language == 'ru' else result.get("url", "URL missing")
            response.append(f"{i}. {title} - {url}")

        formatted_response = "\n".join(response)
        if user_language == 'ru':
            return f"Обработанные результаты:\n{formatted_response}"
        else:
            return f"Processed results:\n{formatted_response}"
    except Exception as e:
        logger.error(f"Ошибка обработки результатов: {e}")
        return "Ошибка обработки данных." if user_language == 'ru' else "Error processing data."


def print_message(role, message):
    """
    Выводит сообщение с ролью и текстом, форматированным с использованием цветов.
    """
    try:
        color = Colors.BLUE if role == "Вы" else Colors.GREEN
        print(f"\n{color}┌─ {role}:{Colors.RESET}")
        print(f"│ {message.replace('  ', '  │ ')}")
        print("└" + "─" * 50)
    except AttributeError as e:
        logger.error(f"Ошибка при выводе сообщения: {e}")
        print(f"{Colors.RED}Ошибка в выводе сообщения.{Colors.RESET}")
