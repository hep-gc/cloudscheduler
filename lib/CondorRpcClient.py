import pika
import uuid


class CondorRpcClient(object):

    # Need to pass in all config parameters: Host, port, routing key, queue name
    #    routing key and queue name could be the same
    #    instead of key/queuename perhaps just host and prefix (prefix defiend in config + relevant condor host)
    def __init__(self, host, port, routing_key, queue_name):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host, port))
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

    # perhaps make individual functions for different commands
    def call(self, yaml):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange=self.queue_name,
            routing_key=self.routing_key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=yaml)
        while self.response is None:
            self.connection.process_data_events()
        # Process responce
        # for a retire it will be a list: [rc, msg]
        # for invalidating classads list will be: [rc, master_result, startd_result]
        # on a failure rc will be 1, and second list member will be error/msg
        return list(self.response)


condor_rpc = CondorRpcClient(host="", port=99999999, routing_key="", queue_name="")

yaml_dict = {
    'command': "retire",
    'machine': "OTTERMACHINE12345",
    'hostname': "OTTERHOST12345"
}

yaml = yaml.dump(yaml_dict)
response = condor_rpc.call(yaml)
