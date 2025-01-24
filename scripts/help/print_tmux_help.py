import sys

def print_tmux_help():
    help_text = """
Основные команды tmux:

1. Создание новой сессии
   tmux new -s имя_сессии
   Создает новую сессию с указанным именем.

2. Подключение к существующей сессии
   tmux attach -t имя_сессии
   Подключает вас к существующей сессии с указанным именем.

3. Список сессий
   tmux list-sessions
   Показывает список всех активных сессий.

4. Отсоединение от сессии
   Нажмите Ctrl + b, затем d.
   Это отсоединит вас от текущей сессии, но она останется активной.

5. Закрытие сессии
   exit
   Введите эту команду в командной строке внутри сессии, чтобы закрыть ее.

Работа с окнами и панелями:

1. Создание нового окна
   Нажмите Ctrl + b, затем c.
   Это создаст новое окно в текущей сессии.

2. Переключение между окнами
   Нажмите Ctrl + b, затем n (следующее окно) или p (предыдущее окно).

3. Список окон
   Нажмите Ctrl + b, затем w.
   Это покажет список всех окон в текущей сессии.

4. Закрытие окна
   exit
   Введите эту команду в командной строке окна или нажмите Ctrl + b, затем & и подтвердите.

5. Создание панели
   Нажмите Ctrl + b, затем % (вертикальная панель) или " (горизонтальная панель).

6. Переключение между панелями
   Нажмите Ctrl + b, затем используйте стрелки (вверх, вниз, влево, вправо).

7. Закрытие панели
   exit
   Введите эту команду в командной строке панели или нажмите Ctrl + b, затем x и подтвердите.

Настройки и управление:

1. Настройка конфигурации
   Файл конфигурации tmux обычно находится по пути ~/.tmux.conf. Вы можете добавлять свои настройки и команды.

2. Перезагрузка конфигурации
   Нажмите Ctrl + b, затем : и введите source-file ~/.tmux.conf, чтобы применить изменения в конфигурации.

3. Выход из tmux
   Нажмите Ctrl + b, затем : и введите kill-server, чтобы завершить все сессии и выйти из tmux.

Полезные команды:

- Показать текущую версию tmux
  tmux -V

- Получить помощь по командам
  Нажмите Ctrl + b, затем ? для отображения списка доступных команд.
"""
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "print_tmux_help":
        print_tmux_help()
    else:
        print("Используйте 'print_tmux_help' в качестве параметра
