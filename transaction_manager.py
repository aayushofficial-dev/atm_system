from atm import TRANSACTIONS_FILE, log_transaction, save_users


class TransactionManager:

    def __init__(self, users):
        self.users = users

    def deposit(self, username, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        self.users[username]["balance"] += amount
        log_transaction(username, "DEPOSIT", amount)
        save_users(self.users)
        return self.users[username]["balance"]

    def withdraw(self, username, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if amount > self.users[username]["balance"]:
            raise ValueError("Insufficient funds.")

        self.users[username]["balance"] -= amount
        log_transaction(username, "WITHDRAW", amount)
        save_users(self.users)
        return self.users[username]["balance"]

    def transfer(self, from_user, to_user, amount):
        if to_user not in self.users:
            raise ValueError("Recipient account not found.")

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if amount > self.users[from_user]["balance"]:
            raise ValueError("Insufficient funds.")

        self.users[from_user]["balance"] -= amount
        self.users[to_user]["balance"] += amount
        log_transaction(from_user, f"TRANSFER_TO:{to_user}", amount)
        log_transaction(to_user, f"TRANSFER_FROM:{from_user}", amount)
        save_users(self.users)
        return self.users[from_user]["balance"]

    def balance(self, username):
        return self.users[username]["balance"]

    def mini_statement(self, username, limit=5):
        history = self.full_history(username)
        return history[-limit:]

    def full_history(self, username):
        try:
            with open(TRANSACTIONS_FILE, "r") as file:
                return [
                    line.strip()
                    for line in file
                    if f"| {username} |" in line
                ]
        except FileNotFoundError:
            return []

    def receipt(self, username):
        history = self.mini_statement(username, limit=1)
        return history[0] if history else "No transactions found."
