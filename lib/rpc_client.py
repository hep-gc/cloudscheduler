import pika
import time
import uuid
import yaml


class RPC(object):

    # Need to pass in all config parameters: Host, port, routing key, queue name
    #    routing key and queue name could be the same
    #    instead of key/queuename perhaps just host and prefix (prefix defiend in config + relevant condor host)
    def __init__(self, host, port, routing_key, queue_name):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.routing_key = routing_key

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, msg, timeout=30):
        if isinstance(msg, str):
            body = msg
        else:
            body = yaml.dump(msg)

        self.response = None
        self.corr_id = str(uuid.uuid4())
        call_time = time.time()
        self.channel.basic_publish(
            exchange="",
            routing_key=self.routing_key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                ),
            body=body)
        while self.response is None:
            if time.time() - call_time >= timeout:
                # call timed out return a failure
                return None
            self.connection.process_data_events()
        # Process responce
        # for a retire it will be a list: [rc, msg]
        # for invalidating classads list will be: [rc, master_result, startd_result]
        # on a failure rc will be 1, and second list member will be error/msg
        #return self.response
        if hasattr(yaml, 'full_load'):
            return yaml.full_load(self.response.decode('utf-8'))
        else:
            return yaml.load(self.response.decode('utf-8'))

    def signal(self, msg):
        if isinstance(msg, str):
            body = msg
        else:
            body = yaml.dump(msg)

        self.channel.basic_publish(
            exchange="",
            routing_key=self.routing_key,
            body=body)
