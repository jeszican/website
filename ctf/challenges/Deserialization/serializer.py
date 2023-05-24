import pickle
import random, string, os, base64


def store_secret(name, secret):
    secret_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    secret = base64.urlsafe_b64decode(secret)

    with open(os.path.join("secrets", secret_id), 'wb') as f:
        f.write(pickle.dumps(secret))

    return secret_id


def retrieve_secret_from_file(secret_id):
    with open(os.path.join("secrets", secret_id), 'rb') as f:
        data = pickle.loads(f.read())

    dd = pickle.loads(data)
    return data