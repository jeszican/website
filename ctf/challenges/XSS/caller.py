import threading, requests
from time import sleep


# this is a thread to request the page every 10 seconds
def request_page():
    while True:
        try:
            requests.get("http://127.0.0.1:5000/")
        except: pass
        sleep(10)


if __name__ == "__main__":
    # start the requestor thread
    th = threading.Thread(target=request_page)
    th.start()
