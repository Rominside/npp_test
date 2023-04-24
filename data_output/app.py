import json
import requests
from flask import Flask
import multiprocessing
import threading

host_name = "0.0.0.0"
port = 5002

app = Flask(__name__)             # create an app instance

APP_VERSION = "1.0.2"

_requests_queue: multiprocessing.Queue = None

CONTENT_HEADER = {"Content-Type": "application/json"}

#аналоговый выходной порт
def out_a(value):
    data = {"value": value}
    requests.post(
        "http://scada:6069/data_a",
        data=json.dumps(data),
        headers=CONTENT_HEADER,
    )


#порт контакта с защитой
def out_b():
    data = {"status": True}
    requests.post(
        "http://protection:6068/alarm",
        data=json.dumps(data),
        headers=CONTENT_HEADER,
    )


#цифровой порт
def out_d(operation, msg):
    if operation == 'send_data':
        data = {"value": msg}
        requests.post(
            "http://scada:6069/data_d",
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )

    elif operation == 'send_diagnostic':
        data = {"status": msg}
        requests.post(
            "http://scada:6069/diagnostic",
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )

    elif operation == 'send_key':
        data = {"key": msg}
        requests.post(
            "http://scada:6069/key",
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )

    elif operation == 'send_error':
        data = {"error": msg}
        requests.post(
            "http://scada:6069/error",
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )


def start_rest(requests_queue):
    global _requests_queue 
    _requests_queue = requests_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()