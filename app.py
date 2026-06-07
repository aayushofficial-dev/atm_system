from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import backend

app = Flask(__name__)
app.secret_key = "change-me"


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ok, msg = backend.authenticate(username, password)
        if ok:
            session['user'] = username
            return redirect(url_for('dashboard'))
        flash(msg)
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    balance = backend.get_balance(user)
    transactions = backend.get_transactions(user)
    return render_template('dashboard.html', user=user, balance=balance, transactions=transactions)


@app.route('/deposit', methods=['POST'])
def deposit():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    # support both form and AJAX (JSON)
    try:
        amount = float(request.form.get('amount', request.json.get('amount', 0)))
    except Exception:
        amount = 0
    ok, msg = backend.deposit(user, amount)
    if request.is_json:
        balance = backend.get_balance(user)
        return jsonify(success=ok, message=msg, balance=balance)
    flash(msg)
    return redirect(url_for('dashboard'))


@app.route('/withdraw', methods=['POST'])
def withdraw():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    try:
        amount = float(request.form.get('amount', request.json.get('amount', 0)))
    except Exception:
        amount = 0
    ok, msg = backend.withdraw(user, amount)
    if request.is_json:
        balance = backend.get_balance(user)
        return jsonify(success=ok, message=msg, balance=balance)
    flash(msg)
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        recovery = request.form.get('recovery')
        ok, msg = backend.create_account(username, password, recovery)
        if ok:
            flash(msg)
            return redirect(url_for('login'))
        flash(msg)
    return render_template('register.html')


@app.route('/api/transactions')
def api_transactions():
    user = session.get('user')
    if not user:
        return jsonify(success=False, message='Not logged in'), 401
    tx = backend.get_transactions(user)
    return jsonify(success=True, transactions=tx)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
