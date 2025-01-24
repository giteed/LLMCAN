import sys

# ANSI escape codes for colors
WHITE = "\033[1;37m"  # Жирный белый
GRAY = "\033[0;37m"   # Серый
RESET = "\033[0m"     # Сброс цвета

def print_tmux_help():
    help_text = f"""
{WHITE}Основные команды tmux:{RESET}

{WHITE}1. Создание новой сессии{RESET}
   {GRAY}tmux new -s имя_сессии{RESET}
   {GRAY}Создает новую сессию с указанным именем.{RESET}

{WHITE}2. Подключение к существующей сессии{RESET}
   {GRAY}tmux attach -t имя_сессии{RESET}
   {GRAY}Подключает вас к существующей сессии с указанным именем.{RESET}

{WHITE}3. Список сессий{RESET}
   {GRAY}tmux list-sessions{RESET}
   {GRAY}Показывает список всех активных сессий.{RESET}

{WHITE}4. Отсоединение от сессии{RESET}
   {GRAY}Нажмите Ctrl + b, затем d.{RESET}
   {GRAY}Это отсоединит вас от текущей сессии, но она останется активной.{RESET}

{WHITE}5. Закрытие сессии{RESET}
   {GRAY}exit{RESET}
   {GRAY}Введите эту команду в командной строке внутри сессии, чтобы закрыть ее.{RESET}

{WHITE}Работа с окнами и панелями:{RESET}

{WHITE}1. Создание нового окна{RESET}
   {GRAY}Нажмите Ctrl + b, затем c.{RESET}
   {GRAY}Это создаст новое окно в текущей сессии.{RESET}

{WHITE}2. Переключение между окнами{RESET}
   {GRAY}Нажмите Ctrl + b, затем n (следующее окно) или p (предыдущее окно).{RESET}

{WHITE}3. Список окон{RESET}
   {GRAY}Нажмите Ctrl + b, затем w.{RESET}
   {GRAY}Это покажет список всех окон в текущей сессии.{RESET}

{WHITE}4. Закрытие окна{RESET}
   {GRAY}exit{RESET}
   {GRAY}Введите эту команду в командной строке окна или нажмите Ctrl + b, затем & и подтвердите.{RESET}

{WHITE}5. Создание панели{RESET}
   {GRAY}Нажмите Ctrl + b, затем % (вертикальная панель) или " (горизонтальная панель).{RESET}

{WHITE}6. Переключение между панелями{RESET}
   {GRAY}Нажмите Ctrl + b, затем используйте стрелки (вверх, вниз, влево, вправо).{RESET}

{WHITE}7. Закрытие панели{RESET}
   {GRAY}exit{RESET}
   {GRAY}Введите эту команду в командной строке панели или нажмите Ctrl + b, затем x и подтвердите.{RESET}

{WHITE}Настройки и управление:{RESET}

{WHITE}1. Настройка конфигурации{RESET}
   {GRAY}Файл конфигурации tmux обычно находится по пути ~/.tmux.conf. Вы можете добавлять свои настройки и команды.{RESET}

{WHITE}2. Перезагрузка конфигурации{RESET}
   {GRAY}Нажмите Ctrl + b, затем : и введите source-file ~/.tmux.conf, чтобы применить изменения в конфигурации.{RESET}

{WHITE}3. Выход из tmux{RESET}
   {GRAY}Нажмите Ctrl + b, затем : и введите kill-server, чтобы завершить все сессии и выйти из tmux.{RESET}

{WHITE}Полезные команды:{RESET}

{WHITE}- Показать текущую версию tmux{RESET}
  {GRAY}tmux -V{RESET}

{WHITE}- Получить помощь по командам{RESET}
  {GRAY}Нажмите Ctrl + b, затем ? для отображения списка доступных команд.{RESET}
"""
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "print_tmux_help":
        print_tmux_help()
    else:
        print("Используйте 'print_tmux_help' в качестве параметра для получения справки по tmux.")
