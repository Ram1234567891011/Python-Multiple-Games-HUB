import random
import time
import os
import html
import requests
import json
from colorama import init, Fore

init(autoreset=True)

LEADERBOARD_FILE = "leaderboard.json"
CREDENTIALS_FILE = "credentials.json"

if not os.path.exists(LEADERBOARD_FILE):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({}, f)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_score(name, score, streak, total_time):
    with open(LEADERBOARD_FILE, "r") as f:
        leaderboard = json.load(f)
    leaderboard.append({
        "name": name,
        "score": score,
        "streak": streak,
        "time_played": f"{int(total_time // 60)}m {int(total_time % 60)}s"
    })
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=2)

def show_leaderboard():
    print(Fore.YELLOW + "\n\U0001F3C6 TOP 10 LEADERBOARD \U0001F3C6")
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard = json.load(f)
        if not leaderboard:
            print(Fore.RED + "No scores recorded yet.")
            return
        for i, entry in enumerate(leaderboard, 1):
            name = entry.get("name", "Unknown")
            score = entry.get("score", 0)
            time_played = entry.get("time_played", "N/A")
            streak = entry.get("streak", 0)
            print(f"{i}. {name} - {score} pts | \U0001F551 {time_played} | \U0001F525 Streak: {streak}")
    except (FileNotFoundError, json.JSONDecodeError):
        print(Fore.RED + "Leaderboard file is missing or corrupted.")

def choose_difficulty():
    print(Fore.GREEN + "Choose Difficulty Level:")
    print(Fore.BLUE + "1 - Basic")
    print(Fore.YELLOW + "2 - Intermediate")
    print(Fore.RED + "3 - Hard")
    level = input(Fore.CYAN + "\U0001F522 Choose (1-3): ")
    if level == "1":
        return (1, 10)
    elif level == "2":
        return (10, 50)
    elif level == "3":
        return (50, 100)
    else:
        print(Fore.RED + "❌ Invalid choice. Defaulting to Basic.")
        return (1, 10)

def generate_math_question(operation, min_val, max_val):
    num1 = random.randint(min_val, max_val)
    num2 = random.randint(min_val, max_val)
    if operation == "1":
        return f"{num1} + {num2} = ", num1 + num2
    elif operation == "2":
        num1, num2 = max(num1, num2), min(num1, num2)
        return f"{num1} - {num2} = ", num1 - num2
    elif operation == "3":
        return f"{num1} × {num2} = ", num1 * num2
    elif operation == "4":
        num1 = num1 * num2 if num2 != 0 else num1
        return f"{num1} ÷ {num2} = ", round(num1 / num2, 2)
    return None, None

def input_continue_or_quit():
    choice = input(Fore.LIGHTYELLOW_EX + "Press Enter to continue or Q to quit: ").strip().lower()
    return choice == "q"

def register():
    clear()
    print(Fore.CYAN + "\U0001F511 Register")
    username = input("Enter new username: ").strip()
    password = input("Enter password: ").strip()
    with open(CREDENTIALS_FILE, "r") as f:
        users = json.load(f)
    if username in users:
        print(Fore.RED + "❌ Username already exists.")
        time.sleep(2)
        return None
    users[username] = password
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(users, f, indent=2)
    print(Fore.GREEN + "✅ Registration successful!")
    time.sleep(2)
    return username

def login():
    clear()
    print(Fore.CYAN + "\U0001F511 Login")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    with open(CREDENTIALS_FILE, "r") as f:
        users = json.load(f)
    if users.get(username) == password:
        print(Fore.GREEN + "✅ Login successful!")
        time.sleep(1)
        return username
    else:
        print(Fore.RED + "❌ Invalid credentials.")
        time.sleep(2)
        return None

def math_game(name):
    clear()
    print(Fore.MAGENTA + "\U0001F3AE MATH GAME MENU \U0001F3AE")
    print(Fore.CYAN + "1 - Addition\n2 - Subtraction\n3 - Multiplication\n4 - Division")
    operation = input(Fore.GREEN + "🟢 Choose Operation (1-4): ")
    if operation not in ["1", "2", "3", "4"]:
        print(Fore.RED + "❌ Invalid choice.")
        return
    min_val, max_val = choose_difficulty()
    score, streak = 0, 0
    start_time = time.time()

    while True:
        question, answer = generate_math_question(operation, min_val, max_val)
        print(Fore.BLUE + f"\n\U0001F9EE Q: {question}")
        try:
            user_ans = input(Fore.CYAN + "Your answer: ")
            if float(user_ans) == answer:
                print(Fore.GREEN + "✅ Correct!")
                score += 1
                streak += 1
            else:
                print(Fore.RED + f"❌ Wrong. Correct: {answer}")
                streak = 0
        except:
            print(Fore.RED + f"❌ Invalid input. Correct: {answer}")
            streak = 0
        time.sleep(1)

        if input_continue_or_quit():
            break

    total_time = time.time() - start_time
    print(Fore.MAGENTA + f"\n\U0001F3AF Final Score: {score} | \U0001F525 Highest Streak: {streak}")
    save_score(name, score, streak, total_time)
    input(Fore.LIGHTBLACK_EX + "\nPress Enter to return to menu...")

def trivia_game(name, category):
    clear()
    print(Fore.YELLOW + f"\n\U0001F9E0 {category.upper()} TRIVIA MODE \U0001F9E0")
    cat_map = {
        "english": 10,
        "science": 17,
        "history": 23,
        "general": 9
    }
    score, streak = 0, 0
    start_time = time.time()

    while True:
        url = f"https://opentdb.com/api.php?amount=1&category={cat_map[category]}&difficulty=medium&type=multiple"
        response = requests.get(url).json()
        if not response.get("results"):
            print(Fore.RED + "❌ Failed to load question.")
            continue
        question = html.unescape(response["results"][0]["question"])
        correct = html.unescape(response["results"][0]["correct_answer"])
        options = [correct] + [html.unescape(opt) for opt in response["results"][0]["incorrect_answers"]]
        random.shuffle(options)

        print(Fore.CYAN + f"\n❓ {question}")
        for idx, opt in enumerate(options):
            print(f"{idx+1}. {opt}")

        try:
            user_input = input(Fore.CYAN + "👉 Your answer (1-4): ")
            if not user_input.isdigit() or int(user_input) not in range(1, 5):
                print(Fore.RED + f"❌ Invalid choice. Correct: {correct}")
                streak = 0
            elif options[int(user_input)-1] == correct:
                print(Fore.GREEN + "✅ Correct!")
                score += 1
                streak += 1
            else:
                print(Fore.RED + f"❌ Wrong. You chose: {options[int(user_input)-1]} | Correct: {correct}")
                streak = 0
        except:
            print(Fore.RED + f"❌ Invalid input. Correct: {correct}")
            streak = 0
        time.sleep(1)

        if input_continue_or_quit():
            break

    total_time = time.time() - start_time
    print(Fore.MAGENTA + f"\n\U0001F3AF Final Score: {score} | \U0001F525 Highest Streak: {streak}")
    save_score(name, score, streak, total_time)
    input(Fore.LIGHTBLACK_EX + "\nPress Enter to return to menu...")

def main_menu():
    while True:
        clear()
        print(Fore.CYAN + "\n\U0001F3AE WELCOME TO THE LEARNING GAME HUB!")
        print(Fore.YELLOW + "1. Login")
        print(Fore.GREEN + "2. Register")
        print(Fore.LIGHTWHITE_EX + "3. Exit")
        choice = input(Fore.LIGHTYELLOW_EX + "Enter your choice (1-3): ")
        if choice == '3':
            print(Fore.CYAN + "\U0001F44B Goodbye!")
            break
        elif choice == '2':
            name = register()
        elif choice == '1':
            name = login()
        else:
            print(Fore.RED + "❌ Invalid choice.")
            continue

        if not name:
            continue

        while True:
            clear()
            print(Fore.YELLOW + "1. Math Game")
            print(Fore.GREEN + "2. English Trivia")
            print(Fore.BLUE + "3. Science Trivia")
            print(Fore.MAGENTA + "4. History Trivia")
            print(Fore.CYAN + "5. General Knowledge")
            print(Fore.RED + "6. Leaderboard")
            print(Fore.LIGHTWHITE_EX + "7. Logout")
            inner_choice = input(Fore.LIGHTYELLOW_EX + "Enter your choice (1-7): ")
            if inner_choice == '7':
                break
            elif inner_choice == '6':
                clear()
                show_leaderboard()
                input(Fore.LIGHTBLACK_EX + "\nPress Enter to return to menu...")
                continue
            elif inner_choice == '1': math_game(name)
            elif inner_choice == '2': trivia_game(name, "english")
            elif inner_choice == '3': trivia_game(name, "science")
            elif inner_choice == '4': trivia_game(name, "history")
            elif inner_choice == '5': trivia_game(name, "general")
            else:
                print(Fore.RED + "❌ Invalid choice.")
            time.sleep(2)

if __name__ == "__main__":
    main_menu()