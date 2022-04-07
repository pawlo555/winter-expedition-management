from typing import List

import pika
import sys

from settings import *
from agent import Agent


def administration_callback(ch, method: pika.spec.Basic.Deliver, properties, body):
    print(f"Received message from administration: " + body.decode(CODING))
    ch.basic_ack(method.delivery_tag)


class Deliver(Agent):
    def __init__(self, name: str, produced_goods: List[str]):
        super().__init__(name)
        self.processed_orders = 0
        self.produced_goods = produced_goods

        self.channel.exchange_declare(TEAM_EXCHANGE, "topic")
        self.prepare_administration_queue()
        self.prepare_order_queues()

    def prepare_administration_queue(self):
        self.channel.exchange_declare(ADMINISTRATOR_DELIVER_EXCHANGE, "fanout")
        self.channel.queue_declare(self.name)
        self.channel.queue_bind(self.name, ADMINISTRATOR_DELIVER_EXCHANGE)
        self.channel.basic_consume(self.name, administration_callback, auto_ack=False)

    def prepare_order_queues(self):
        self.channel.exchange_declare(DELIVERY_EXCHANGE, "topic")
        for produced_good in self.produced_goods:
            self.channel.queue_declare(produced_good)
            self.channel.queue_bind(produced_good, DELIVERY_EXCHANGE, "*."+produced_good)
            self.channel.basic_consume(queue=produced_good, on_message_callback=self.callback, auto_ack=False)

    def callback(self, ch, method: pika.spec.Basic.Deliver, properties, body):
        team, confirmation_message = self.process_order(body)
        self.channel.basic_publish(TEAM_EXCHANGE, team, confirmation_message.encode(CODING))
        self.channel.basic_ack(method.delivery_tag)
        print(f"Order processing finish, to team {team} was send such confirmation: {confirmation_message}")

    def process_order(self, body: bytes):
        message = body.decode(CODING)
        team, good = message.split(".")
        print(f"Received order from team: {team} for {good}")
        order_id = self.name + "-" + str(self.processed_orders)
        self.processed_orders += 1
        confirmation_message = team + "." + good + "." + order_id
        return team, confirmation_message

    def run(self):
        print("Waiting for orders")
        self.channel.start_consuming()

    def on_exit(self):
        print("Interrupted")
        sys.exit(0)
