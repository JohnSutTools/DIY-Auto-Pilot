"""Lightweight mock cereal messaging for Pi 2 (ARMv7) compatibility"""
import time
import json

class SubSocket:
    def __init__(self, topics):
        self.topics = topics if isinstance(topics, list) else [topics]
        self.data = {}
        print(f'[MOCK CEREAL] SubSocket created for topics: {self.topics}')
    
    def receive(self, non_blocking=False):
        # Return None to simulate no messages
        # In real use, this would receive from ZMQ
        return None

class PubSocket:
    def __init__(self, topic):
        self.topic = topic
        print(f'[MOCK CEREAL] PubSocket created for topic: {topic}')
    
    def send(self, data):
        print(f'[MOCK CEREAL] Send on {self.topic}: {data}')

def sub_sock(topics, timeout=None, conflate=False, addr=None):
    """Create a subscriber socket"""
    return SubSocket(topics)

def pub_sock(topic):
    """Create a publisher socket"""
    return PubSocket(topic)

print('[MOCK CEREAL] Mock cereal.messaging loaded (Pi 2 ARMv7 compatibility mode)')
