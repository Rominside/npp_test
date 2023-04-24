ordering = False
key_s = False
key_t = False
key = "12345"

def check_operation(id, details):
    global key_t, key_s, key
    global ordering
    authorized = False

    print(f"[info] checking policies for event {id},"\
          f" {details['source']}->{details['target']}: {details['operation']}")
    sourse = details['source']
    target = details['target']
    operation = details['operation']
    in_sourse = details['in_source']

    if not ordering:
        if sourse == "input" and target == "monitor" and operation == "pulled_out_key":
            key_t = False
            key_s = False
            authorized = True
        if sourse == "input" and target == "monitor" and operation == "insert_key":
            if in_sourse["Security"] == "connect":
                key_s = True
            if in_sourse["Technical"] == "connect":
                key_t = True
            authorized = True
        if sourse == "input" and target == "system" and operation == "update_system":
            if key == details["headers"][9][1]:
                if key_s and key_t:
                    authorized = True
        if sourse == "input" and target == "sensor_value_handler" and operation == "update_coef":
            if key_s and key_t:
                authorized = True
        if sourse == "input" and target == "sensor_value_handler" \
            and operation == "check_alarm":
                authorized = True
        if sourse == "sensor_value_handler" and target == "monitor" and operation == "alarm":
            authorized = True
        if sourse == "sensor_value_handler" and target == "monitor" and operation == "successful_check":
            authorized = True
        if sourse == "sensor_value_handler" and target == "monitor" and operation == "update_coef_complit":
            authorized = True
        if sourse == "system" and target == "monitor" and operation == "log":
             authorized = True
            
    return authorized
        
        