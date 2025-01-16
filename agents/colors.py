# colors.py

class Colors:
    # Основные цвета
    BLACK = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Темные цвета
    DARK_BLACK = "\033[30m"
    DARK_RED = "\033[31m"
    DARK_GREEN = "\033[32m"
    DARK_YELLOW = "\033[33m"
    DARK_BLUE = "\033[34m"
    DARK_MAGENTA = "\033[35m"
    DARK_CYAN = "\033[36m"
    DARK_WHITE = "\033[37m"

    # Стили
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    REVERSED = "\033[7m"
    RESET = "\033[0m"

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
    styled_message = Colors.format_message(Colors.MAGENTA,

