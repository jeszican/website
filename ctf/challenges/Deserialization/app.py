from flask import Flask, render_template, redirect, url_for, abort, session
from form import SecretForm
from serializer import store_secret, retrieve_secret_from_file
import base64

app = Flask(__name__)
app.secret_key = "thisIsSuperSecure!!"


@app.route('/', methods=["GET", "POST"])
def submit():
    form = SecretForm()
    if form.validate_on_submit():
        # try and base64
        try: base64.urlsafe_b64decode(form.secret.data)
        except: return render_template("index.html", form=form, error="You should base64 your secret first")
        secret_id = store_secret(form.name.data, form.secret.data)
        return render_template("index.html", form=form, message="Thanks for your secret, your secret id is %s" % (secret_id))
    return render_template("index.html", form=form)


@app.route('/retrieve/<secret_id>', methods=["GET"])
def retrieve_secret(secret_id):
    return retrieve_secret_from_file(secret_id)


if __name__ == "__main__":
    app.run()
