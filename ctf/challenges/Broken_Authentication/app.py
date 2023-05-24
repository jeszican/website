from flask import Flask, render_template, redirect, url_for, abort, session, request, make_response
from form import LoginForm
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

app = Flask(__name__)

number_of_users = 1

@app.route('/login', methods=["GET", "POST"])
@csrf.exempt
def login():
    global number_of_users
    form = LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        return render_template("login.html", form=form, error="Access denied..")
    # increment number of users
    number_of_users = number_of_users + 1
    resp = make_response(render_template("login.html", form=form))
    resp.set_cookie('SESSION_ID', 'user%d' % number_of_users)
    return resp


@app.route('/')
@csrf.exempt
def admin():
    if request.cookies.get('SESSION_ID') != 'user1':
        return redirect(url_for("login"))
    return render_template("index.html", flag="CTF{th1si5fl4g3__!}'")


if __name__ == "__main__":
    app.run()
