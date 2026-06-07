import time
from pathlib import Path
from datetime import datetime
import atm

USERS_FILE = atm.USERS_FILE
TRANSACTIONS_FILE = atm.TRANSACTIONS_FILE
LOCK_TIME = atm.LOCK_TIME


def authenticate(username, password):
    users = atm.load_users()

    if username not in users:
        return False, "Account not found"

    user = users[username]

    if user["status"] == "banned":
        return False, "Account banned"

    if user["status"] == "suspended":
        return False, "Account suspended"

    if time.time() < user["lock_until"]:
        return False, "Account temporarily locked"

    if atm.hash_password(password, user["salt"]) == user["password_hash"]:
        user["attempts"] = 0
        atm.save_users(users)
        return True, "Login successful"

    user["attempts"] += 1
    if user["attempts"] >= 3:
        user["lock_until"] = time.time() + LOCK_TIME
    atm.save_users(users)
    return False, "Invalid password"


def get_balance(username):
    users = atm.load_users()
    if username not in users:
        return None
    return users[username]["balance"]


def get_transactions(username):
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            for line in f:
                if f"| {username} |" in line:
                    transactions.append(line.strip())
    except FileNotFoundError:
        pass
    return transactions


def deposit(username, amount):
    users = atm.load_users()
    if username not in users:
        return False, "Account not found"
    if amount <= 0:
        return False, "Invalid amount"

    users[username]["balance"] += float(amount)
    atm.log_transaction(username, "DEPOSIT", amount)
    atm.save_users(users)
    try:
        atm.notify_user(username, f"Deposit completed: {amount}")
    except Exception:
        pass
    return True, "Deposit successful"


def withdraw(username, amount):
    users = atm.load_users()
    if username not in users:
        return False, "Account not found"
    if amount <= 0:
        return False, "Invalid amount"

    if amount > users[username]["balance"]:
        return False, "Insufficient funds"

    users[username]["balance"] -= float(amount)
    atm.log_transaction(username, "WITHDRAW", amount)
    atm.save_users(users)
    try:
        atm.notify_user(username, f"Withdrawal completed: {amount}")
    except Exception:
        pass
    return True, "Withdrawal successful"


def create_account(username, password, recovery):
    users = atm.load_users()
    if username in users:
        return False, "Username exists"
    if not atm.password_strength(password):
        return False, "Weak password"

    salt = atm.generate_salt()
    password_hash = atm.hash_password(password, salt)

    users[username] = {
        "salt": salt,
        "password_hash": password_hash,
        "balance": 0.0,
        "status": "active",
        "attempts": 0,
        "lock_until": 0,
        "recovery": recovery
    }

    atm.save_users(users)
    try:
        atm.notify_user(username, "Account created successfully.")
    except Exception:
        pass
    return True, "Account created"


def list_users():
    return atm.load_users()
