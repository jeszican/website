from database import get_search_history
from flask import Flask, render_template, redirect, url_for, abort, session, request
from flask.helpers import make_response
from form import SearchForm
from database import get_search_history, insert_search_history

from time import sleep

app = Flask(__name__)
app.secret_key = "thisIsSuperSecure!!"

search_history = []


@app.route('/', methods=["GET", "POST"])
def search():
    form = SearchForm()
    search_history = get_search_history()
    search_history.reverse()
    # if the request is local host, set a session cookie with the flag
    if form.validate_on_submit():
        search_history = insert_search_history(form.search_term.data)
        results = "Sorry, there are no results for '%s'" % (form.search_term.data)
        return render_template("index.html", form=form, results=results, search_history=search_history)

    resp = make_response(render_template("index.html", form=form, search_history=search_history))

    if request.remote_addr == "127.0.0.1":
        resp.set_cookie('flag', 'CTF{th1si5fl4g2__!}')

    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
