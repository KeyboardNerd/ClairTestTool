# simple web hook for notification
from multiprocessing import Process, Queue
from flask import Flask, request, make_response
import requests
import time
import json

def hookNotification(q):
    app = Flask("notification hook")
    @app.route("/", methods=["POST"])
    def recv():
        # receive web hook's hook
        q.put(request.get_json()["Notification"]["Name"])
        return "", 200
    app.run(port=7070)

def getNotification(q):
    print "Waiting to get vulnerability notifications"
    with open("notification_log", "a+") as f:
        while True:
            time.sleep(0.001)
            noti_name = q.get()
            oldPage = ""
            newPage = ""
            para = {
                "old_vulnerability_page": oldPage,
                "new_vulnerability_page": newPage,
                "limit": 1,
            }
            r = requests.get("http://127.0.0.1:6080/notifications/"+noti_name, params=para)
            if r.status_code != 200:
                print "some error when get noti"
                continue
            f.write(json.dumps(r.json()))
            f.flush()
            # remove the notification
            r = requests.delete("http://127.0.0.1:6080/notifications/"+noti_name)
            if r.status_code != 200:
                print "some error when delete noti"
        f.close()

if __name__ == "__main__":
    q = Queue()
    p1 = Process(target=getNotification, args=(q,))
    # run on local host with port 7070
    p2 = Process(target=hookNotification, args=(q,))
    p1.start()
    p2.start()
    # it's not safe to send kill signal, queue might be broken. This is just for
    # testing.
    p1.join()
    p2.join()