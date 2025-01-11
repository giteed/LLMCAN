# ... (предыдущий код остается без изменений)

def get_multiline_input():
    print(f"{Colors.BLUE}Вы (введите пустую строку для завершения ввода):{Colors.RESET}")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)

# ... (остальной код остается без изменений)

def main():
    load_dialog_history()
    
    print(f"{Colors.YELLOW}Добро пожаловать в Когнитивный Интерфейсный Агент!{Colors.RESET}")
    print(f"{Colors.YELLOW}Введите 'выход', '/q' или Ctrl+C для завершения.{Colors.RESET}")
    print(f"{Colors.YELLOW}Для поиска используйте ключевые слова 'поищи' или 'найди'.{Colors.RESET}")

    try:
        while True:
            user_input = get_multiline_input()
            
            # ... (остальной код main() функции остается без изменений)

if __name__ == "__main__":
    main()
