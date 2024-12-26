#!/bin/bash
# run_llmcan.sh
## Скрипт установки и запуска для проекта LLMCAN

# Название репозитория и директории
GITHUB_REPO="https://github.com/giteed/LLMCAN.git"
PROJECT_DIR="LLMCAN"
VENV_DIR="venv" # Путь для виртуального окружения

# Цвета для вывода
RESET='\033[0m'
RED='\033[1;31m'
GREEN='\033[1;32m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

# Приветствие
echo -e "\n=== Установка проекта LLMCAN ===\n"
echo "Using Python version:"
python3 --version

# Проверяем запуск с правами суперпользователя
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED} ❌ Пожалуйста, запустите скрипт с правами суперпользователя (sudo).${RESET}"
    echo "Например: sudo $0"
    exit 1
fi

# Проверяем наличие Git
if ! command -v git &>/dev/null; then
  echo -e "${RED} ❌ Git не установлен. Установите его и повторите попытку.${RESET}"
  exit 1
fi

# Проверяем наличие Python 3.8 или выше
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_MAJOR=3
REQUIRED_MINOR=8

IFS='.' read -r MAJOR MINOR <<< "$PYTHON_VERSION"

if (( MAJOR < REQUIRED_MAJOR || (MAJOR == REQUIRED_MAJOR && MINOR < REQUIRED_MINOR) )); then
    echo -e "${RED} ❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию.${RESET}"
    exit 1
else
    echo -e "${GREEN} ✅ Обнаружен Python версии $PYTHON_VERSION${RESET}"
fi

# Клонируем или обновляем репозиторий
if [ ! -d "$PROJECT_DIR" ]; then
  echo " 🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO" || { echo -e "${RED} ❌ Ошибка при клонировании репозитория.${RESET}"; exit 1; }
  FIRST_INSTALL=true
else
  echo " 🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull || { echo -e "${RED} ❌ Ошибка при обновлении репозитория.${RESET}"; exit 1; }
  FIRST_INSTALL=false
fi

# Переходим в папку проекта
cd "$PROJECT_DIR" || exit

# Создаем и активируем виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo " 🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR" || { echo -e "${RED} ❌ Ошибка при создании виртуального окружения.${RESET}"; exit 1; }
fi

# Активируем виртуальное окружение
source "$VENV_DIR/bin/activate" || { echo -e "${RED} ❌ Не удалось активировать виртуальное окружение.${RESET}" ; exit 1; }

# Устанавливаем зависимости
echo " 📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r "requirements.txt" || { echo -e "${RED} ❌ Ошибка при установке зависимостей.${RESET}"; exit 1; }

# Проверяем и создаем недостающие папки
REQUIRED_DIRS=("agents" "core" "data" "parsers" "scripts" "temp" "tests")
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo " 📂 Создание отсутствующей папки: $dir"
    mkdir -p "$dir"
  fi
done

# Уведомление об успешной установке
echo -e "\n ✅ Установка завершена. Проект готов к работе."

# Инструкция для пользователя
echo -e "\n=== Инструкция ==="
echo -e " 🌐 Репозиторий: ${GITHUB_REPO}"
echo -e " 🔄 Для активации окружения используйте: source $PROJECT_DIR/$VENV_DIR/bin/activate"
echo -e " 🛠️  Для запуска проекта используйте: python3 scripts/start.py\n"
