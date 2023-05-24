import sqlite3

def get_cur():
    conn = sqlite3.connect('users.db')
    return conn.cursor()

def get_user_or_abort(username, password):
    # Substiture the values into the query
    results = get_cur().execute("SELECT * FROM users WHERE username = '"+username+"' AND password = '"+password+"'").fetchall()
    # If theres 1 result
    if len(results) > 0:
        # Create the user object from the first user
        user = {"username": results[0][0], "password": results[0][1]}
        # Return him!
        return True, user
    else:
        # Return false
        return False, ""

def get_user_balance(account_number):
    # Substiture the values into the query
    results = get_cur().execute("SELECT * FROM users WHERE username = 'user"+account_number+"'").fetchall()
    # If theres 1 result
    if len(results) > 0:
        # Return him!
        return results[0][2]
    else:
        # Return false
        return "Account doesn't exist.."