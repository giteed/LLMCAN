# agents/LLaMa_generator/restart_ollama.py
import paramiko
import ollama
import time
import os

# 🛠 НАСТРОЙКИ 🛠
OLLAMA_SSH_HOST = "IP-адрес сервера с Ollama"  # IP-адрес сервера с Ollama
SSH_USER = "Логин для SSH"  # Логин для SSH
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")  # Или ~/.ssh/id_ed25519

OLLAMA_HOST = "http://"IP-адрес сервера с Ollama":11434"  # API Ollama
TEST_MODEL = "openchat:latest"  # Модель для теста
TEST_PROMPT = "Привет, как дела?"  # Сообщение для теста

# Функция перезапуска Ollama через SSH
def restart_ollama():
    print("🔄 Перезапуск Ollama через SSH...")

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"🔑 Подключение к {OLLAMA_SSH_HOST} как {SSH_USER}...")

        # Пробуем загрузить ключ
        try:
            pkey = paramiko.RSAKey(filename=SSH_KEY_PATH)  # Принудительно загружаем RSA-ключ
        except paramiko.ssh_exception.SSHException:
            print("⚠️ Не удалось загрузить RSA-ключ, пробуем ED25519...")
            try:
                pkey = paramiko.Ed25519Key(filename=SSH_KEY_PATH)  # Пробуем Ed25519
            except paramiko.ssh_exception.SSHException:
                print("❌ Ошибка загрузки SSH-ключа! Проверьте файл.")
                return

        # Подключаемся по ключу
        client.connect(OLLAMA_SSH_HOST, username=SSH_USER, pkey=pkey, timeout=10)

        # Команда для принудительного завершения Ollama
        kill_command = "sudo pkill -9 ollama"  # Принудительное убийство процессов
        serve_command = "nohup ollama serve > /dev/null 2>&1 &"  # Запуск Ollama в фоне

        # Получаем PID запущенной Ollama (если работает)
        stdin, stdout, stderr = client.exec_command("pgrep ollama")
        pids = stdout.read().decode().strip()
        
        if pids:
            print(f"🔍 Найдены запущенные процессы Ollama: {pids}")
            print("🛑 Завершаем Ollama...")
            stdin, stdout, stderr = client.exec_command(kill_command)
            time.sleep(2)  # Ждём завершения

        print("🚀 Запускаем Ollama...")
        stdin, stdout, stderr = client.exec_command(serve_command)

        # Проверяем статус Ollama
        time.sleep(5)  # ⏳ Даем время на старт
        stdin, stdout, stderr = client.exec_command("curl -s http://10.0.1.31:11434/api/tags")
        output = stdout.read().decode()

        if "models" in output:
            print("✅ Ollama успешно запущена!")
        else:
            print("❌ Ollama не отвечает! Проверьте вручную.")

        client.close()

    except Exception as e:
        print(f"❌ Ошибка при подключении к SSH: {e}")

# Функция для тестирования Ollama после перезапуска
def test_ollama():
    print("🚀 Отправляем тестовый запрос в Ollama...")
    client = ollama.Client(host=OLLAMA_HOST)

    try:
        start_time = time.time()
        response = client.chat(model=TEST_MODEL, messages=[{"role": "user", "content": TEST_PROMPT}])
        response_time = time.time() - start_time

        print(f"✅ Ollama ответила за {response_time:.2f} секунд.")
        print(f"📝 Ответ: {response['message']['content']}\n{'-'*50}")

    except Exception as e:
        print(f"❌ Ошибка при тестировании Ollama: {e}")

# Главное меню
def main():
    while True:
        print("\n=== Меню ===")
        print("1. Перезапустить Ollama")
        print("2. Выйти")
        choice = input("Выберите действие: ")

        if choice == "1":
            restart_ollama()
            test_ollama()
        elif choice == "2":
            print("🚪 Выход из программы.")
            break
        else:
            print("⚠️ Некорректный ввод! Попробуйте снова.")

if __name__ == "__main__":
    main()
