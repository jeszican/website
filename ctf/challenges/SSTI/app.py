from flask import Flask, render_template, redirect, url_for, abort, session
from flask.templating import render_template_string
from jinja2 import Environment, BaseLoader
from form import LoginForm, RegistrationForm
from database import get_user_or_abort, insert_new_user

app = Flask(__name__)
app.secret_key = "CTF{th1si5fl4g5__!}"

# @app.template_filter('t')
# def trenderiza(value, obj):
#     rtemplate = render_template_string(value)
#     # return rtemplate.render(**obj)


@app.route('/', methods=["GET", "POST"])
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


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        valid, user = insert_new_user(form.username.data, form.password.data)
        if not valid:
            return render_template("register.html", form=form, error="Something went wrong..")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)


@app.route('/user/profile')
def admin():
    if session.get("LOGGED_IN", 0) != 1:
        return redirect(url_for("login"))
    return render_template_string("""
        <!DOCTYPE html>
        <html>

        <head>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@100;400&display=swap" rel="stylesheet">

            <title>Dashboard | Admin</title>
            <link rel="stylesheet" href="/static/css/main.css">
        </head>

        <body>
            <div class="container">
                Welcome to your profile,&nbsp;<span style="color:tomato">"""+session.get("USER", {"username": "testuser", "password": "password123"})["username"]+"""</span>
            </div>
        </body>

        </html>
    """, )


if __name__ == "__main__":
    app.run()
