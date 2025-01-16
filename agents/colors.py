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
    print(Colors.format_message(Colors.GREEN, "Это зеленое сообщение!", bold=True))
    print(Colors.format_message(Colors.RED, "Это красное сообщение с подчеркиванием!", underline=True))
    Colors.print_with_divider("Это сообщение с разделителем")
    print(Colors.HEART, "Любовь", Colors.SMILE)
