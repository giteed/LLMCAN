# menu.py
# Заглушка меню для проекта LLMCAN

def show_menu():
    print("\n=== Меню LLMCAN ===")
    print("1. Запустить обработку данных")
    print("2. Посмотреть логи")
    print("3. Выход")

    choice = input("\nВыберите действие (1-3): ")
    if choice == "1":
        print("\n[INFO] Обработка данных запущена...")
        # Заглушка для обработки данных
    elif choice == "2":
        print("\n[INFO] Открытие логов...")
        # Заглушка для просмотра логов
    elif choice == "3":
        print("\n[INFO] Выход из программы. До свидания!")
        exit(0)
    else:
        print("\n[ERROR] Некорректный выбор. Попробуйте снова.")

if __name__ == "__main__":
    while True:
        show_menu()
