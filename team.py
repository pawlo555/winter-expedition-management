import sys
import pika

from threading import Thread
from settings import *
from agent import Agent


class Team(Agent):
    def __init__(self, name: str):
        super().__init__(name)
        self.prepare_queue()
        self.channel.exchange_declare(DELIVERY_EXCHANGE, "topic")
        self.sending_thread = Thread(target=self.sending_thread_run)

    def prepare_queue(self):
        self.channel.queue_declare(self.name)
        self.channel.exchange_declare(TEAM_EXCHANGE, "topic")
        self.channel.queue_bind(self.name, TEAM_EXCHANGE, self.name)

        self.channel.exchange_declare(ADMINISTRATOR_TEAM_EXCHANGE, "fanout")
        self.channel.queue_bind(self.name, ADMINISTRATOR_TEAM_EXCHANGE)

    def callback(self, ch, method: pika.spec.Basic.Deliver, properties, body):
        if method.exchange == TEAM_EXCHANGE:
            print(f"Received order confirmation: {body.decode()}")
        else:
            print(f"Received message from administration: " + body.decode(CODING))
        self.channel.basic_ack(method.delivery_tag)

    def sending_thread_run(self):
        try:
            while True:
                message = input()
                to_send = self.name+"."+message
                self.channel.basic_publish(DELIVERY_EXCHANGE, to_send, to_send.encode(CODING))
        except KeyboardInterrupt:
            print("Interrupted")

    def run(self):
        self.sending_thread.start()
        self.channel.basic_consume(queue=self.name, on_message_callback=self.callback, auto_ack=False)
        self.channel.start_consuming()

    def on_exit(self):
        self.sending_thread.join()
        print('Interrupted')
        sys.exit(0)
