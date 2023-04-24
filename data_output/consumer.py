# implements Kafka topic consumer functionality


import threading
from app import out_a, out_b, out_d
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json

def handle_event(id: str, details: dict):
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['target']}: {details['operation']}")

    if details["operation"] == "update_coef_complit":
        out_a(details["value"])
    if details["operation"] == "alarm":
        out_b()
        out_a(details["value"])
    if details["operation"] == "log":
        out_d("send_data", details["value"])
        out_d("send_diagnostic", details["sys_log"]["cron"])
        out_d("send_key", details["sys_log"]["key"])
        out_d("send_error", details["sys_log"]["start"])
    if details["operation"] == "successful_check":
        out_a(details["value"])

    
def consumer_job(args, config):

    # Create Consumer instance
    manager_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(manager_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            manager_consumer.assign(partitions)

    # Subscribe to topic
    topic = "output"
    manager_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = manager_consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                # print("Waiting...")
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    id = msg.key().decode('utf-8')
                    details = json.loads(msg.value().decode('utf-8'))
                    handle_event(id, details)
                except Exception as e:
                    print(
                        f"[error] malformed event received from topic {topic}: {msg.value()}. {e}")    
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        manager_consumer.close()

def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()
    
if __name__ == '__main__':
    start_consumer(None)
