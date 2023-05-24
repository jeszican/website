import sqlite3


def get_cur():
    conn = sqlite3.connect('users.db', isolation_level=None)
    return conn.cursor()


def get_user_or_abort(username, password):
    # Substiture the values into the query
    results = get_cur().execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username":username, "password":password}).fetchall()
    # If theres 1 result
    if len(results) > 0:
        # Create the user object from the first user
        user = {"username": results[0][0], "password": results[0][1]}
        # Return him!
        return True, user
    else:
        # Return false
        return False, ""


def insert_new_user(username, password):
    # Substiture the values into the query
    get_cur().execute('INSERT INTO users values ("'+username+'","'+password+'");');
    # check the user was created
    return get_user_or_abort(username, password)
