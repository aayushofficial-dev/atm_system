import csv
from datetime import datetime
from pathlib import Path

from atm import TRANSACTIONS_FILE


class ReportManager:

    def __init__(self, transactions_file=TRANSACTIONS_FILE):
        self.transactions_file = Path(transactions_file)

    def monthly_report(self, username, year=None, month=None):
        """Generate a monthly report for a user."""
        now = datetime.now()
        year = year or now.year
        month = month or now.month

        return [
            transaction
            for transaction in self._user_transactions(username)
            if (
                transaction["date"].year == year
                and transaction["date"].month == month
            )
        ]

    def export_csv(self, username, output_file=None):
        """Export a user's transactions to CSV."""
        output_path = Path(output_file or f"{username}_transactions.csv")
        transactions = self._user_transactions(username)

        with open(output_path, "w", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["date", "username", "action", "amount"]
            )
            writer.writeheader()

            for transaction in transactions:
                row = transaction.copy()
                row["date"] = row["date"].isoformat(sep=" ")
                writer.writerow(row)

        return output_path

    def analytics(self, username):
        """Display analytics for a user's transactions."""
        transactions = self._user_transactions(username)
        deposits = self._total_for_action(transactions, "DEPOSIT")
        withdrawals = self._total_for_action(transactions, "WITHDRAW")

        return {
            "transaction_count": len(transactions),
            "total_deposits": deposits,
            "total_withdrawals": withdrawals,
            "net_change": deposits - withdrawals,
        }

    def _user_transactions(self, username):
        try:
            with open(self.transactions_file, "r") as file:
                return [
                    transaction
                    for line in file
                    if (transaction := self._parse_line(line))
                    and transaction["username"] == username
                ]
        except FileNotFoundError:
            return []

    def _parse_line(self, line):
        parts = [part.strip() for part in line.split("|")]

        if len(parts) != 4:
            return None

        date_text, username, action, amount_text = parts

        try:
            amount = float(amount_text)
            date = datetime.fromisoformat(date_text)
        except ValueError:
            return None

        return {
            "date": date,
            "username": username,
            "action": action,
            "amount": amount,
        }

    def _total_for_action(self, transactions, action):
        return sum(
            transaction["amount"]
            for transaction in transactions
            if transaction["action"] == action
        )
