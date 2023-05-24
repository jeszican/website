from flask import Flask, render_template, redirect, url_for, abort, session
from form import LoginForm
from database import get_user_or_abort, get_user_balance

app = Flask(__name__)
app.secret_key = "thisIsSuperSecure!!"


@app.route('/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        valid, user = get_user_or_abort(form.username.data, form.password.data)
        if not valid:
            return render_template("login.html", form=form, error="Access denied..")
        session["LOGGED_IN"] = 1
        session["USER"] = user
        return redirect(url_for('balance', user_account_number=1))
    return render_template("login.html", form=form)


@app.route('/account/<user_account_number>')
def balance(user_account_number):
    if session.get("LOGGED_IN", 0) != 1:
        return redirect(url_for("login"))
    balance = get_user_balance(user_account_number)
    return render_template("index.html", user=session.get("USER", {"username":"testuser"}), balance=balance)


if __name__ == "__main__":
    app.run()
