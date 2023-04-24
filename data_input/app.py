import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
import threading
import base64
from urllib.request import urlopen

host_name = "0.0.0.0"
port = 5002

app = Flask(__name__)             # create an app instance

APP_VERSION = "1.0.2"

_requests_queue: multiprocessing.Queue = None





@app.route("/ingest", methods=['POST'])
def update():
    # часть, отвечающая за авторизацию 
    # UDP думаю стоит сделать проверки на ключи опратора-технолога/оператора-безопасника/счётчика
    content = request.json
    auth = request.headers['auth']
    if auth != 'very-secure-token':
        return "unauthorized", 401
    # конец

    req_id = uuid4().__str__() # 

    try:
        update_details = {
            "id": req_id,
            "url": content['url'],               # адрес внешнего интерфейса
            "value": content['value'],           # значение радиоционного фона
            "in_source": content['in_source'],      # имя внешнего интерфейса техник/архитектор/сенсор
            "target": content['target'],         # имя сущности, которой адресован реквест
            "digest": content['digest'],         # хеш
            "operation": content['operation'],   # вид операции вставить ключ/вытащить ключ/
                                                 # обновить систему/изменить параметры/принять данные
            "digest_alg": content['digest_alg'], # алгоритм хеширования
            }
        update_details.update({"source": "input"})
        if update_details["url"] == "http://file_server:6001":
            request_url = 'http://file_server:6001/download-update/new.txt'
            response = urlopen(request_url)
            headers = response.getheaders()
            data = response.read()
            payload_n = base64.b64encode(data).decode('ascii')
            print(payload_n)
            print(headers)
            request_url = 'http://file_server:6001/download-update/settings.txt'
            response = urlopen(request_url)
            data = response.read()
            payload_s = base64.b64encode(data).decode('ascii')
            print(payload_s)
            update_details.update({"payload_n": payload_n, "payload_s": payload_s, "headers": headers})
            # del update_details["url"]

        _requests_queue.put(update_details)
        print(f"new data event: {update_details}")
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "new data received", "id": req_id})

def start_rest(requests_queue):
    global _requests_queue 
    _requests_queue = requests_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()