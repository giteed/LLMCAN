import os
import sys
import logging
import readline

# Добавляем путь к корневой папке проекта для корректного импорта
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from agents.colors import Colors

# Настройка логирования для меню
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

import subprocess

import subprocess

def ensure_tmux():
    try:
        # Получаем версию tmux
        version_output = subprocess.check_output(['tmux', '-V'], stderr=subprocess.STDOUT)
        print(f"tmux версия: {version_output.decode().strip()}")
    except subprocess.CalledProcessError:
        # Если tmux не установлен, выполняем скрипт для установки
        print("tmux не установлен. Устанавливаем...")
        install_script = (
            "hash -r && "
            "command -v tmux >/dev/null 2>&1 || { "
            "sudo dnf install -y tmux && echo 'tmux установлен.'; } && "
            "mkdir -p ~/.tmux && "
            "touch ~/.tmux.conf && "
            "grep -qxF 'set-option -g history-limit 10000' ~/.tmux.conf || "
            "echo 'set-option -g history-limit 10000' >> ~/.tmux.conf"
        )
        subprocess.run(install_script, shell=True, check=True)

        # Проверяем, установлен ли tmux после установки
        try:
            subprocess.check_output(['tmux', '-V'], stderr=subprocess.STDOUT)
            print("tmux успешно установлен.")
        except subprocess.CalledProcessError:
            print("Ошибка: tmux не удалось установить.")
            return

    # Перезапускаем tmux
    #print("Перезапускаем tmux...")
    #subprocess.run(['tmux'], check=True)




def print_tmux_help():

    # Вызов функции проверки наличия tmux
    ensure_tmux()

    help_text = f"""
{Colors.WHITE}{Colors.BOLD}Основные команды tmux:{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}1. Создание новой сессии{Colors.RESET}
   {Colors.GRAY}tmux new -s имя_сессии{Colors.RESET}
   {Colors.GRAY}Создает новую сессию с указанным именем.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}2. Подключение к существующей сессии{Colors.RESET}
   {Colors.GRAY}tmux attach -t имя_сессии{Colors.RESET}
   {Colors.GRAY}Подключает вас к существующей сессии с указанным именем.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}3. Список сессий{Colors.RESET}
   {Colors.GRAY}tmux list-sessions{Colors.RESET}
   {Colors.GRAY}Показывает список всех активных сессий.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}4. Отсоединение от сессии{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем d.{Colors.RESET}
   {Colors.GRAY}Это отсоединит вас от текущей сессии, но она останется активной.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}5. Закрытие сессии{Colors.RESET}
   {Colors.GRAY}exit{Colors.RESET}
   {Colors.GRAY}Введите эту команду в командной строке внутри сессии, чтобы закрыть ее.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}Работа с окнами и панелями:{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}1. Создание нового окна{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем c.{Colors.RESET}
   {Colors.GRAY}Это создаст новое окно в текущей сессии.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}2. Переключение между окнами{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем n (следующее окно) или p (предыдущее окно).{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}3. Список окон{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем w.{Colors.RESET}
   {Colors.GRAY}Это покажет список всех окон в текущей сессии.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}4. Закрытие окна{Colors.RESET}
   {Colors.GRAY}exit{Colors.RESET}
   {Colors.GRAY}Введите эту команду в командной строке окна или нажмите Ctrl + b, затем & и подтвердите.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}5. Создание панели{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем % (вертикальная панель) или " (горизонтальная панель).{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}6. Переключение между панелями{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем используйте стрелки (вверх, вниз, влево, вправо).{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}7. Закрытие панели{Colors.RESET}
   {Colors.GRAY}exit{Colors.RESET}
   {Colors.GRAY}Введите эту команду в командной строке панели или нажмите Ctrl + b, затем x и подтвердите.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}Настройки и управление:{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}1. Настройка конфигурации{Colors.RESET}
   {Colors.GRAY}Файл конфигурации tmux обычно находится по пути ~/.tmux.conf. Вы можете добавлять свои настройки и команды.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}2. Перезагрузка конфигурации{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем : и введите source-file ~/.tmux.conf, чтобы применить изменения в конфигурации.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}3. Выход из tmux{Colors.RESET}
   {Colors.GRAY}Нажмите Ctrl + b, затем : и введите kill-server, чтобы завершить все сессии и выйти из tmux.{Colors.RESET}

{Colors.WHITE}{Colors.BOLD}Полезные команды:{Colors.RESET}

{Colors.WHITE}- Показать текущую версию tmux{Colors.RESET}
  {Colors.GRAY}tmux -V{Colors.RESET}

{Colors.WHITE}- Получить помощь по командам{Colors.RESET}
  {Colors.GRAY}Нажмите Ctrl + b, затем ? для отображения списка доступных команд.{Colors.RESET}
"""
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "print_tmux_help":
        print_tmux_help()
    else:
        print("Используйте 'print_tmux_help' в качестве параметра для получения справки по tmux.")
