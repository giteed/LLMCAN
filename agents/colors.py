# colors.py

class Colors:
    # Основные цвета
    BLACK = "\033[90m"      # Черный
    DARK_GRAY = "\033[90m"  # Темно-серый
    GRAY = "\033[37m"       # Светло-серый
    RED = "\033[91m"        # Красный
    GREEN = "\033[92m"      # Зеленый
    YELLOW = "\033[93m"     # Желтый
    BLUE = "\033[94m"       # Синий
    MAGENTA = "\033[95m"    # Магента
    CYAN = "\033[96m"       # Циан
    WHITE = "\033[97m"      # Белый

    # Темные цвета
    DARK_BLACK = "\033[30m"      # Темный черный
    DARK_RED = "\033[31m"        # Темный красный
    DARK_GREEN = "\033[32m"      # Темный зеленый
    DARK_YELLOW = "\033[33m"     # Темный желтый
    DARK_BLUE = "\033[34m"       # Темный синий
    DARK_MAGENTA = "\033[35m"    # Темная магента
    DARK_CYAN = "\033[36m"       # Темный циан
    DARK_WHITE = "\033[37m"      # Темный белый

    # Стили
    BOLD = "\033[1m"          # Жирный текст
    UNDERLINE = "\033[4m"     # Подчеркнутый текст
    REVERSED = "\033[7m"      # Инвертированные цвета
    RESET = "\033[0m"         # Сброс цвета и стиля

    # Эмодзи
    HEART = "❤️"
    SMILE = "😊"
    THUMBS_UP = "👍"
    FIRE = "🔥"
    STAR = "⭐"
    CHECK_MARK = "✔️"
    CROSS_MARK = "❌"
    WARNING = "⚠️"
    QUESTION = "❓"

    # Разделители
    HORIZONTAL_LINE = "-" * 50
    EQUALS_LINE = "=" * 50
    ASTERISK_LINE = "*" * 50

    @staticmethod
    def format_message(color, message, bold=False, underline=False):
        """Форматирует сообщение с заданным цветом и стилем."""
        style = ""
        if bold:
            style += Colors.BOLD
        if underline:
            style += Colors.UNDERLINE
        return f"{style}{color}{message}{Colors.RESET}"

    @staticmethod
    def print_with_divider(message, divider=HORIZONTAL_LINE):
        """Печатает сообщение с разделителем."""
        print(divider)
        print(message)
        print(divider)









# Пример использования
if __name__ == "__main__":
    # Примеры использования серого цвета
    print(Colors.format_message(Colors.GRAY, "Это светло-серое сообщение."))
    print(Colors.format_message(Colors.DARK_GRAY, "Это темно-серое сообщение."))

# Пример использования
if __name__ == "__main__":
    # 1. Простое сообщение в зеленом цвете
    print(Colors.format_message(Colors.GREEN, "1. Это зеленое сообщение!", bold=True))

    # 2. Красное сообщение с подчеркиванием
    print(Colors.format_message(Colors.RED, "2. Это красное сообщение с подчеркиванием!", underline=True))

    # 3. Синее сообщение с жирным текстом
    print(Colors.format_message(Colors.BLUE, "3. Это синее сообщение с жирным текстом!", bold=True))

    # 4. Желтое сообщение с инвертированными цветами
    print(Colors.format_message(Colors.YELLOW, "4. Это желтое сообщение с инвертированными цветами!", bold=True))

    # 5. Сообщение с эмодзи
    print(f"{Colors.CYAN}5. Это сообщение с эмодзи: {Colors.HEART} {Colors.SMILE}{Colors.RESET}")

    # 6. Печать сообщения с разделителем
    Colors.print_with_divider("6. Это сообщение с разделителем")

    # 7. Сообщение с предупреждением
    print(Colors.format_message(Colors.YELLOW, "7. Внимание! Это предупреждение ⚠️", bold=True))

    # 8. Сообщение с галочкой
    print(f"{Colors.GREEN}8. Успех! {Colors.CHECK_MARK} Операция выполнена успешно!{Colors.RESET}")

    # 9. Сообщение с ошибкой
    print(Colors.format_message(Colors.RED, "9. Ошибка! ❌ Что-то пошло не так.", bold=True))

    # 10. Подсказка с вопросом
    print(f"{Colors.BLUE}10. Подсказка: Как вы себя чувствуете? {Colors.QUESTION}{Colors.RESET}")

    # 11. Сообщение с огнем
    print(f"{Colors.RED}11. Внимание! {Colors.FIRE} Это сообщение с огнем!{Colors.RESET}")

        # 12. Сообщение с звездой
    print(f"{Colors.YELLOW}12. Поздравляем! {Colors.STAR} Вы выиграли приз!{Colors.RESET}")

    # 13. Сообщение с разделителем из звездочек
    Colors.print_with_divider("13. Сообщение с разделителем из звездочек", divider=Colors.ASTERISK_LINE)

    # 14. Сообщение с темным цветом
    print(Colors.format_message(Colors.DARK_GREEN, "14. Это сообщение в темно-зеленом цвете."))

    # 15. Сообщение с использованием всех стилей
    styled_message = Colors.format_message(Colors.MAGENTA, "15. Это сообщение с жирным и подчеркнутым текстом!", bold=True, underline=True)
    print(styled_message)

    # 16. Сообщение с инвертированными цветами
    print(Colors.format_message(Colors.WHITE, "16. Это сообщение с инвертированными цветами!", bold=True))

    # 17. Сообщение с использованием нескольких эмодзи
    print(f"{Colors.CYAN}17. Ура! {Colors.THUMBS_UP} {Colors.HEART} {Colors.SMILE} Это отличное сообщение!{Colors.RESET}")

    # 18. Сообщение с предупреждением и разделителем
    Colors.print_with_divider("18. Внимание! Это важное сообщение!", divider=Colors.EQUALS_LINE)

    # 19. Сообщение с использованием темных цветов
    print(Colors.format_message(Colors.DARK_RED, "19. Это сообщение в темно-красном цвете."))

    # 20. Сообщение с использованием всех доступных цветов
    print(f"{Colors.RED}20. Красный текст{Colors.RESET}, {Colors.GREEN}зеленый текст{Colors.RESET}, {Colors.BLUE}синий текст{Colors.RESET}, {Colors.YELLOW}желтый текст{Colors.RESET}, {Colors.CYAN}циановый текст{Colors.RESET}, {Colors.MAGENTA}магентовый текст{Colors.RESET}, {Colors.WHITE}белый текст{Colors.RESET}.")

    # 21. Сообщение с использованием жирного текста и эмодзи
    print(f"{Colors.BOLD}{Colors.GREEN}21. Это жирное зеленое сообщение с эмодзи {Colors.SMILE}{Colors.RESET}")

    # 22. Сообщение с использованием подчеркивания и эмодзи
    print(f"{Colors.UNDERLINE}{Colors.BLUE}22. Это подчеркнутое синее сообщение с эмодзи {Colors.HEART}{Colors.RESET}")

    # 23. Сообщение с использованием всех стилей и эмодзи
    print(f"{Colors.BOLD}{Colors.UNDERLINE}{Colors.RED}23. Это жирное и подчеркнутое красное сообщение с эмодзи {Colors.WARNING}{Colors.RESET}")

    # 24. Сообщение с использованием разделителей и эмодзи
    Colors.print_with_divider(f"{Colors.CYAN}24. Это сообщение с разделителем и эмодзи {Colors.THUMBS_UP}{Colors.RESET}")

    # 25. Сообщение с использованием всех цветов в одном
    print(f"{Colors.RED}25. Красный {Colors.GREEN}Зеленый {Colors.YELLOW}Желтый {Colors.BLUE}Синий {Colors.MAGENTA}Магента {Colors.CYAN}Циан {Colors.WHITE}Белый{Colors.RESET}")
