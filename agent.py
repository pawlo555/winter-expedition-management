import pika
import sys

from pika import channel
from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, name: str):
        self.name = name
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel: pika.channel = connection.channel()

    def start(self):
        try:
            self.run()
        except KeyboardInterrupt:
            self.on_exit()

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @abstractmethod
    def on_exit(self):
        raise NotImplementedError
