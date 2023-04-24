import base64
import hashlib
import json
import os
import random
import subprocess
import time
from flask import jsonify
import threading


key_t = False
key_s = False
level = -1
key = '12345'
event = threading.Event()
url = ''
sys_log = {}

NEW_FW_PATHNAME = "system/storage/new.txt"


def log(funk_name: str, funk_log : str):
    global sys_log
    sys_log.update({funk_name: funk_log})

#вычислитель хеша
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(1024), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# заглушка логики контроля параметров прикладной программы
def settings_sanity_check():
    result = random.choices([True, False], weights=[90, 10])
    log("settings_sanity_check", "Diagnostic ended with status: " + str(result))
    return result


#основная система, которая периодически выдает ключи и проводит диагностику
def cron(t):
    global key, event
    while not event.is_set():
        time.sleep(t)
        check_status = settings_sanity_check()
        check_status = str(check_status)
        log("cron", "send_diagnostic " + "Checked with status: " + check_status)


#запись обновления -- здесь записываются обновления ОС
def commit(name, payload):
    stored = False
    update_payload = base64.b64decode(payload)
    try:
        with open("system/storage/" + name, "wb") as f:
            f.write(update_payload)
        stored = True
    except Exception as e:
        print(f'[error] failed to store blob in {os.getcwd()}: {e}')
    return stored


def stop():
    global event
    try:
        event.set()
        log("stop", "Stopped") 
    except Exception as e:
        log("stop", f"exception raised {e}") 
        error_message = f"malformed request"
        return error_message, 400
    return jsonify({"operation": "stopped"})


def start():
    global event, key_s, key_t, level, key, url
    try:
        event = threading.Event()

        if os.path.exists(NEW_FW_PATHNAME) and (
                os.stat(NEW_FW_PATHNAME).st_mtime !=
                os.stat("system/storage/old.txt").st_mtime):
            version = open(NEW_FW_PATHNAME, mode="r")
        else:
            version = open("system/storage/old.txt", mode="r")
        version = version.readline()

        settings = open('system/storage/settings.txt', 'r')
        data = json.load(settings)
        url = data['output']

        check_success = settings_sanity_check()
        log("key", key)

        #успешная загрузка
        if check_success:
            log("start", "Loaded version: " + str(version))

            key_t = False
            key_s = False
            key = '12345'
            level = data['alarm_level']

            threading.Thread(
                target=lambda: cron(3 * data['timeout'] + 1)).start()

            old_hash = md5(NEW_FW_PATHNAME)
            subprocess.call('cp system/storage/new.txt system/storage/old.txt', shell=True)
            new_hash = md5(NEW_FW_PATHNAME)
            if old_hash != new_hash:
                print("[rewriting] error in sources found")

        #неуспешная загрузка
        else:
            event.set()
            print("[reloading] stopping all systems")
            os.remove(NEW_FW_PATHNAME)
            print("[reloading] new sources was rejected")
            start()

    except Exception as e:
        log("start", f"exception raised {e}")
        print("[error] during loading!")
        return "Error during loading", 400
    return jsonify({"operation": "start requested", "status": True})