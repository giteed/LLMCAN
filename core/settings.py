import os
from pathlib import Path
from dotenv import load_dotenv

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Пути к важным папкам
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
PARSERS_DIR = os.path.join(BASE_DIR, "parsers")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Файл .env
ENV_FILE = os.path.join(BASE_DIR, ".env")

# Проверка и создание .env файла, если он не существует
def create_env_file():
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            f.write("# Default configuration\n")
            f.write("API_KEY=your_default_api_key\n")
            f.write("DEBUG=True\n")
            f.write("DATABASE_URL=sqlite:///data/project.db\n")
        print(".env file created with default settings.")

# Загрузка переменных окружения из .env
create_env_file()
load_dotenv(ENV_FILE)

# Пример получения переменных
API_KEY = os.getenv("API_KEY", "default_api_key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/project.db")
