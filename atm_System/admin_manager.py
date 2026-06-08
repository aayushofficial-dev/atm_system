from atm import TRANSACTIONS_FILE, save_users


class AdminManager:

    def __init__(self, users):
        self.users = users

    def view_users(self):
        return self.users

    def view_transactions(self):
        try:
            with open(TRANSACTIONS_FILE, "r") as file:
                return [line.strip() for line in file]
        except FileNotFoundError:
            return []

    def suspend_user(self, username):
        self._set_status(username, "suspended")

    def reactivate_user(self, username):
        self._set_status(username, "active")

    def ban_user(self, username):
        self._set_status(username, "banned")

    def unban_user(self, username):
        self._set_status(username, "active")

    def system_stats(self):
        transactions = self.view_transactions()
        return {
            "total_users": len(self.users),
            "active_users": self._count_status("active"),
            "suspended_users": self._count_status("suspended"),
            "banned_users": self._count_status("banned"),
            "total_transactions": len(transactions),
        }

    def _set_status(self, username, status):
        if username not in self.users:
            raise ValueError("Account not found.")

        self.users[username]["status"] = status
        save_users(self.users)

    def _count_status(self, status):
        return sum(
            1
            for user in self.users.values()
            if user["status"] == status
        )
