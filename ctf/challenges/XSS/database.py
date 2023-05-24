import sqlite3


def get_cur():
    conn = sqlite3.connect('search_history.db', isolation_level=None)
    return conn.cursor()


def insert_search_history(value):
    # Add the search term to the db
    get_cur().execute('INSERT INTO history values ("'+value+'");')
    return get_search_history()


def get_search_history():
    # Get the search history from the db
    sh = []
    results = get_cur().execute("SELECT * FROM history;").fetchall()
    for r in results:
        sh.append(r[0])
    return sh

