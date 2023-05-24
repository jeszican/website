from flask import Flask, render_template, redirect, url_for, abort, session
from form import LoginForm
from database import get_user_or_abort

app = Flask(__name__)
app.secret_key = "thisIsSuperSecure!!"


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        valid, user = get_user_or_abort(form.username.data, form.password.data)
        if not valid:
            return render_template("login.html", form=form, error="Access denied..")
        session["LOGGED_IN"] = 1
        session["USER"] = user
        return redirect(url_for('admin'))
    return render_template("login.html", form=form)


@app.route('/')
def admin():
    if session.get("LOGGED_IN", 0) != 1:
        return redirect(url_for("login"))
    return render_template("index.html", user=session.get("USER", {"username":"testuser", "password":"password123"}))


if __name__ == "__main__":
    app.run()
