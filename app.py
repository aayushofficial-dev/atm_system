from flask import Flask, render_template, request, redirect, url_for, session, flash
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
    amount = float(request.form.get('amount', 0))
    ok, msg = backend.deposit(user, amount)
    flash(msg)
    return redirect(url_for('dashboard'))


@app.route('/withdraw', methods=['POST'])
def withdraw():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    amount = float(request.form.get('amount', 0))
    ok, msg = backend.withdraw(user, amount)
    flash(msg)
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
