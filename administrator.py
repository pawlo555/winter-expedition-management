import pika
import sys

from threading import Thread

from settings import *
from agent import Agent

TEAM_QUEUE = "TEAM_QUEUE"
DELIVER_QUEUE = "DELIVERS_QUEUE"


def print_info():
    print("Message options:")
    print("A [message] - message to all")
    print("T [message] - message to all teams")
    print("D [message] - message to all delivers")


class Administrator(Agent):
    def __init__(self, name: str = "Administrator"):
        super().__init__(name)

        self.channel.exchange_declare(ADMINISTRATOR_TEAM_EXCHANGE, "fanout")
        self.channel.exchange_declare(ADMINISTRATOR_DELIVER_EXCHANGE, "fanout")
        self.prepare_queue(TEAM_EXCHANGE, TEAM_QUEUE, self.team_callback)
        self.prepare_queue(DELIVERY_EXCHANGE, DELIVER_QUEUE, self.delivery_callback)

        self.sending_thread = Thread(target=self.sending_thread_run)

    def prepare_queue(self, exchange: str, queue: str, callback):
        self.channel.queue_declare(queue)
        self.channel.queue_bind(queue, exchange, "#")
        self.channel.basic_consume(queue, callback, auto_ack=False)

    def sending_thread_run(self):
        try:
            while True:
                message = input()
                if len(message) > 2:
                    self.send_message(message)
                else:
                    print("Wrong message - too short")
        except KeyboardInterrupt or UnicodeDecodeError:
            print("Interrupted")

    def send_message(self, message: str):
        body = message[2:].encode(CODING)
        if message[0] == "A":
            self.channel.basic_publish(ADMINISTRATOR_TEAM_EXCHANGE, "", body)
            self.channel.basic_publish(ADMINISTRATOR_DELIVER_EXCHANGE, "", body)
        elif message[0] == "T":
            self.channel.basic_publish(ADMINISTRATOR_TEAM_EXCHANGE, "", body)
        elif message[0] == "D":
            self.channel.basic_publish(ADMINISTRATOR_DELIVER_EXCHANGE, "", body)
        else:
            print("Wrong command")
            print_info()

    def team_callback(self, ch, method: pika.spec.Basic.Deliver, properties, body):
        message = body.decode()
        print(f"Received order confirmation: {message}")
        self.channel.basic_ack(method.delivery_tag)

    def delivery_callback(self, ch, method: pika.spec.Basic.Deliver, properties, body):
        message = body.decode()
        print(f"Received order : {message}")
        self.channel.basic_ack(method.delivery_tag)

    def run(self):
        print_info()
        self.sending_thread.start()
        self.channel.start_consuming()

    def on_exit(self):
        self.sending_thread.join()
        sys.exit(0)
