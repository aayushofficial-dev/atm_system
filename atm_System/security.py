import hashlib
import secrets
import string


class SecurityManager:

    @staticmethod
    def generate_salt():
        return secrets.token_hex(16)

    @staticmethod
    def hash_password(password, salt):
        return hashlib.sha256(
            (password + salt).encode()
        ).hexdigest()

    @staticmethod
    def verify_password(password, salt, stored_hash):
        return (
            SecurityManager.hash_password(
                password,
                salt
            )
            == stored_hash
        )

    @staticmethod
    def password_strength(password):

        if len(password) < 8:
            return False

        upper = any(c.isupper() for c in password)
        lower = any(c.islower() for c in password)
        digit = any(c.isdigit() for c in password)
        special = any(
            c in string.punctuation
            for c in password
        )

        return upper and lower and digit and special

    @staticmethod
    def generate_password():
        chars = (
            string.ascii_letters
            + string.digits
            + string.punctuation
        )

        return ''.join(
            secrets.choice(chars)
            for _ in range(12)
        )