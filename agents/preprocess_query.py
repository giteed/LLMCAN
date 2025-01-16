from colors import Colors  # Используем Colors из внешнего файла

def preprocess_query(user_input):
    print(f"{Colors.YELLOW}Запрос пользователя получен. Начинаю анализ и формирование поисковых запросов...{Colors.RESET}")
    system_prompt = """Проанализируй запрос пользователя, исправь возможные ошибки и сформулируй до трех связанных поисковых запросов для расширения контекста. Также создай инструкцию для обработки результатов поиска.

Формат ответа:
Основной запрос: [исправленный запрос пользователя]
Дополнительные запросы:
1. [запрос 1]
2. [запрос 2]
3. [запрос 3] (если необходимо)

Инструкция для обработки результатов:
[Детальная инструкция по обработке и форматированию результатов поиска]"""

    context = f"Запрос пользователя: {user_input}\n\n{system_prompt}"
    response = query_llm(context, include_history=False)
    if response is None:
        print(f"{Colors.RED}Не удалось получить ответ от LLM. Использую исходный запрос пользователя.{Colors.RESET}")
        return {"queries": [user_input], "instruction": "Обработайте результаты поиска и предоставьте краткий ответ."}
    preprocessed = parse_preprocessing_response(response)
    
    print(f"{Colors.YELLOW}Анализ завершен. Сформированы следующие запросы:{Colors.RESET}")
    for i, query in enumerate(preprocessed['queries'], 1):
        print(f"{Colors.YELLOW}{i}. {query}{Colors.RESET}")
    return preprocessed
