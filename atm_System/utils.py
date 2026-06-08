from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.txt"
TRANSACTIONS_FILE = BASE_DIR / "transactions.txt"
NOTIFICATIONS_FILE = BASE_DIR / "notifications.txt"


def current_time():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def notify(username, message):

    with open(
        NOTIFICATIONS_FILE,
        "a"
    ) as file:

        file.write(
            f"{current_time()} | "
            f"{username} | "
            f"{message}\n"
        )


def read_notifications(username):
    found = False

    try:
        with open(
            NOTIFICATIONS_FILE,
            "r"
        ) as file:

            for line in file:
                if f"| {username} |" in line:
                    found = True
                    print(line.strip())

    except FileNotFoundError:
        print("No notifications found.")
        return

    if not found:
        print("No notifications found.")
