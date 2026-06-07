# ATM Project - Flask UI Scaffold

This adds a minimal Flask-based UI that integrates with the existing backend.

Quick start:

```bash
python -m pip install -r requirements.txt
python -m py_compile app.py backend.py  # quick syntax check
FLASK_APP=app.py flask run
```

Open http://127.0.0.1:5000 in your browser. Use existing `users.txt` accounts or create accounts via the CLI (`python atm.py`).
