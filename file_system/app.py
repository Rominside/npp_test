import time

# логгирование событий
def storage(details):
    try:
        t = time.time()
        if details["opretion"] == "alarm":
            alarm_value = details["value"]
            with open("/storage/alarm_log.txt", "a+") as f:
                f.write(f"{t} : Alarm was detectes: {alarm_value}\n")

        if details["operation"] == "log":
            sys_log = details["sys_log"]
            with open("/storage/sys_log.txt", "a+") as f:
                f.write(f"{t} : System log: {sys_log}\n")
                
        if details["peration"] == "update_coef_complit":
            update_coef = details["value"]
            with open("/storage/update_coef_log.txt", "a+") as f:
                f.write(f"{t} : update_coef: {update_coef}\n")

    except Exception as e:
        print(f'[error] log failed, exception {e}')