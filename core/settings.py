import os
from pathlib import Path
from dotenv import load_dotenv

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Пути к важным папкам
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
PARSERS_DIR = os.path.join(BASE_DIR, "parsers")
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Файл .env
ENV_FILE = os.path.join(BASE_DIR, ".env")

# Проверка и создание необходимых папок
def create_required_dirs():
    required_dirs = [
        AGENTS_DIR, PARSERS_DIR, DATA_DIR, RAW_DATA_DIR,
        PROCESSED_DATA_DIR, LOGS_DIR, TEMP_DIR
    ]
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)

create_required_dirs()

# Проверка и создание .env файла, если он не существует
def create_env_file():
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            f.write("# Default configuration\n")
            f.write("DATABASE_URL=sqlite:///data/project.db\n")
            f.write("DEBUG=True\n")
        print(".env file created with default settings.")

# Загрузка переменных окружения из .env
create_env_file()
load_dotenv(ENV_FILE)

# Пример получения переменных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/project.db")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
