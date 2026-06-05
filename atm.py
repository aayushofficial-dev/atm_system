import hashlib
import secrets
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.txt"
TRANSACTIONS_FILE = BASE_DIR / "transactions.txt"

LOCK_TIME = 60  
ADMIN_PASSWORD = "admin123"

def load_users():
    users = {}

    try:
        with open(USERS_FILE, "r") as f:
            for line in f:
                data = line.strip().split("|")

                if len(data) == 8:
                    username, salt, password_hash, balance, status, attempts, lock_until, recovery = data

                    users[username] = {
                        "salt": salt,
                        "password_hash": password_hash,
                        "balance": float(balance),
                        "status": status,
                        "attempts": int(attempts),
                        "lock_until": float(lock_until),
                        "recovery": recovery
                    }
    except FileNotFoundError:
        pass

    return users


def save_users(users):
    with open(USERS_FILE, "w") as f:
        for username, data in users.items():
            line = (
                f"{username}|{data['salt']}|{data['password_hash']}|"
                f"{data['balance']}|{data['status']}|"
                f"{data['attempts']}|{data['lock_until']}|"
                f"{data['recovery']}\n"
            )
            f.write(line)


def log_transaction(username, action, amount=0):
    with open(TRANSACTIONS_FILE, "a") as f:
        f.write(
            f"{datetime.now()} | {username} | "
            f"{action} | {amount}\n"
        )


def read_positive_amount():
    try:
        amount = float(input("Amount: "))
    except ValueError:
        print("Please enter a valid number.")
        return None

    if amount <= 0:
        print("Amount must be greater than zero.")
        return None

    return amount

def hash_password(password, salt):
    return hashlib.sha256(
        (password + salt).encode()
    ).hexdigest()


def generate_salt():
    return secrets.token_hex(16)


def password_strength(password):
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    return has_upper and has_lower and has_digit and has_symbol


def generate_password():
    return secrets.token_urlsafe(10)

def create_account(users):
    username = input("Username: ")

    if username in users:
        print("Username already exists.")
        return

    password = input("Password: ")

    if not password_strength(password):
        print("Weak password.")
        return

    recovery = input("Recovery answer: ")

    salt = generate_salt()
    password_hash = hash_password(password, salt)

    users[username] = {
        "salt": salt,
        "password_hash": password_hash,
        "balance": 0.0,
        "status": "active",
        "attempts": 0,
        "lock_until": 0,
        "recovery": recovery
    }

    save_users(users)
    notify_user(username, "Account created successfully.")
    print("Account created successfully.")


def login(users):
    username = input("Username: ")

    if username not in users:
        print("Account not found.")
        return None

    user = users[username]

    if user["status"] == "banned":
        print("Account is banned.")
        return None

    if user["status"] == "suspended":
        print("Account is suspended.")
        return None

    if time.time() < user["lock_until"]:
        print("Account temporarily locked.")
        return None

    password = input("Password: ")

    hashed = hash_password(password, user["salt"])

    if hashed == user["password_hash"]:
        user["attempts"] = 0
        save_users(users)
        print("Login successful.")
        return username

    user["attempts"] += 1

    if user["attempts"] >= 3:
        user["lock_until"] = time.time() + LOCK_TIME
        print("Account locked.")

    save_users(users)
    print("Invalid password.")
    return None


def reset_password(users):
    username = input("Username: ")

    if username not in users:
        print("Account not found.")
        return

    answer = input("Recovery answer: ")

    if answer != users[username]["recovery"]:
        print("Recovery failed.")
        return

    new_password = generate_password()

    salt = generate_salt()

    users[username]["salt"] = salt
    users[username]["password_hash"] = hash_password(
        new_password,
        salt
    )

    save_users(users)
    notify_user(username, "Your password was reset.")

    print("Temporary password:", new_password)


def change_password(users, username):
    confirm = input(
        "Confirm password change? (y/n): "
    )

    if confirm.lower() != "y":
        return

    new_password = input("New password: ")

    if not password_strength(new_password):
        print("Weak password.")
        return

    salt = generate_salt()

    users[username]["salt"] = salt
    users[username]["password_hash"] = hash_password(
        new_password,
        salt
    )

    save_users(users)
    notify_user(username, "Your password was changed.")
    print("Password changed.")


def delete_account(users, username):
    confirm = input(
        "Delete account permanently? (y/n): "
    )

    if confirm.lower() == "y":
        del users[username]
        save_users(users)
        print("Account deleted.")
        return True

    return False

def check_balance(users, username):
    print("Balance:", users[username]["balance"])


def notify_user(username, message):
    try:
        from utils import notify

        notify(username, message)
    except OSError:
        pass


def deposit(users, username):
    amount = read_positive_amount()

    if amount is None:
        return

    confirm = input(
        "Confirm deposit? (y/n): "
    )

    if confirm.lower() != "y":
        return

    users[username]["balance"] += amount

    log_transaction(
        username,
        "DEPOSIT",
        amount
    )

    save_users(users)
    notify_user(username, f"Deposit completed: {amount}")
    print("Deposit successful.")


def withdraw(users, username):
    amount = read_positive_amount()

    if amount is None:
        return

    if amount > users[username]["balance"]:
        print("Insufficient funds.")
        return

    confirm = input(
        "Confirm withdrawal? (y/n): "
    )

    if confirm.lower() != "y":
        return

    users[username]["balance"] -= amount

    log_transaction(
        username,
        "WITHDRAW",
        amount
    )

    save_users(users)
    notify_user(username, f"Withdrawal completed: {amount}")
    print("Withdrawal successful.")


def transfer(users, username):
    recipient = input("Recipient username: ")

    if recipient not in users:
        print("Recipient account not found.")
        return

    if recipient == username:
        print("You cannot transfer to your own account.")
        return

    if users[recipient]["status"] != "active":
        print("Recipient account is not active.")
        return

    amount = read_positive_amount()

    if amount is None:
        return

    if amount > users[username]["balance"]:
        print("Insufficient funds.")
        return

    confirm = input(
        "Confirm transfer? (y/n): "
    )

    if confirm.lower() != "y":
        return

    users[username]["balance"] -= amount
    users[recipient]["balance"] += amount

    log_transaction(
        username,
        f"TRANSFER_TO:{recipient}",
        amount
    )
    log_transaction(
        recipient,
        f"TRANSFER_FROM:{username}",
        amount
    )

    save_users(users)
    notify_user(username, f"Transfer sent to {recipient}: {amount}")
    notify_user(recipient, f"Transfer received from {username}: {amount}")
    print("Transfer successful.")


def transaction_history(username):
    found = False

    try:
        with open(
            TRANSACTIONS_FILE,
            "r"
        ) as f:

            for line in f:
                if f"| {username} |" in line:
                    found = True
                    print(line.strip())

    except FileNotFoundError:
        print("No transactions found.")
        return

    if not found:
        print("No transactions found.")


def mini_statement(username, limit=5):
    transactions = []

    try:
        with open(
            TRANSACTIONS_FILE,
            "r"
        ) as f:

            for line in f:
                if f"| {username} |" in line:
                    transactions.append(line.strip())

    except FileNotFoundError:
        print("No transactions found.")
        return

    if not transactions:
        print("No transactions found.")
        return

    for transaction in transactions[-limit:]:
        print(transaction)


def show_notifications(username):
    try:
        from utils import read_notifications

        read_notifications(username)
    except OSError:
        print("No notifications found.")


def admin_login():
    password = input("Admin password: ")

    if password != ADMIN_PASSWORD:
        print("Invalid admin password.")
        return False

    print("Admin login successful.")
    return True


def show_users(users):
    if not users:
        print("No users found.")
        return

    for username, data in users.items():
        print(
            f"{username} | balance: {data['balance']} | "
            f"status: {data['status']}"
        )


def update_user_status(users, status):
    username = input("Username: ")

    if username not in users:
        print("Account not found.")
        return

    users[username]["status"] = status
    save_users(users)
    notify_user(username, f"Your account status changed to {status}.")
    print("User status updated.")


def system_stats(users):
    status_counts = {
        "active": 0,
        "suspended": 0,
        "banned": 0
    }

    for user in users.values():
        status = user["status"]
        if status in status_counts:
            status_counts[status] += 1

    transaction_count = 0

    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            transaction_count = sum(1 for _ in f)
    except FileNotFoundError:
        pass

    print("Total users:", len(users))
    print("Active users:", status_counts["active"])
    print("Suspended users:", status_counts["suspended"])
    print("Banned users:", status_counts["banned"])
    print("Total transactions:", transaction_count)


def admin_menu(users):
    if not admin_login():
        return

    while True:

        print("\n=== Admin ===")
        print("1. View Users")
        print("2. View Transactions")
        print("3. Suspend User")
        print("4. Reactivate User")
        print("5. Ban User")
        print("6. System Stats")
        print("7. Back")

        choice = input("Choose: ")

        if choice == "1":
            show_users(users)

        elif choice == "2":
            try:
                with open(TRANSACTIONS_FILE, "r") as f:
                    for line in f:
                        print(line.strip())
            except FileNotFoundError:
                print("No transactions found.")

        elif choice == "3":
            update_user_status(users, "suspended")

        elif choice == "4":
            update_user_status(users, "active")

        elif choice == "5":
            update_user_status(users, "banned")

        elif choice == "6":
            system_stats(users)

        elif choice == "7":
            break

        else:
            print("Invalid option.")

def user_menu(users, username):

    while True:

        print("\n1. Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Mini Statement")
        print("6. Full History")
        print("7. Notifications")
        print("8. Change Password")
        print("9. Delete Account")
        print("10. Logout")

        choice = input("Choose: ")

        if choice == "1":
            check_balance(users, username)

        elif choice == "2":
            deposit(users, username)

        elif choice == "3":
            withdraw(users, username)

        elif choice == "4":
            transfer(users, username)

        elif choice == "5":
            mini_statement(username)

        elif choice == "6":
            transaction_history(username)

        elif choice == "7":
            show_notifications(username)

        elif choice == "8":
            change_password(
                users,
                username
            )

        elif choice == "9":
            if delete_account(
                users,
                username
            ):
                break

        elif choice == "10":
            confirm = input(
                "Logout? (y/n): "
            )

            if confirm.lower() == "y":
                break

        else:
            print("Invalid option.")

def main():

    users = load_users()

    while True:

        print("\n=== ATM ===")
        print("1. Create Account")
        print("2. Login")
        print("3. Reset Password")
        print("4. Admin")
        print("5. Exit")

        choice = input("Choose: ")

        if choice == "1":
            create_account(users)

        elif choice == "2":
            user = login(users)

            if user:
                user_menu(users, user)

        elif choice == "3":
            reset_password(users)

        elif choice == "4":
            admin_menu(users)

        elif choice == "5":
            confirm = input(
                "Exit? (y/n): "
            )

            if confirm.lower() == "y":
                break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
