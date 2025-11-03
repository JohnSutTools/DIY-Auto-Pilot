"""Lightweight mock cereal messaging for Pi 2 (ARMv7) compatibility"""
import time
import json

class MockMessage:
    """Mock message class"""
    def __init__(self):
        self.valid = True
        
    class Actuators:
        def __init__(self):
            self.steer = 0.0
    
    class CarControl:
        def __init__(self):
            self.actuators = MockMessage.Actuators()
    
    class ControlsState:
        def __init__(self):
            self.steer = 0.0

class SubMaster:
    """Mock SubMaster that simulates openpilot messaging"""
    def __init__(self, topics, addr=None):
        self.topics = topics if isinstance(topics, list) else [topics]
        self.addr = addr
        self.frame = 0
        self.updated = {topic: False for topic in self.topics}
        self.valid = {topic: True for topic in self.topics}
        
        # Create mock messages
        self._carControl = MockMessage.CarControl()
        self._controlsState = MockMessage.ControlsState()
        
        print(f'[MOCK CEREAL] SubMaster created for topics: {self.topics}')
        if addr:
            print(f'[MOCK CEREAL] Remote address: {addr}')
    
    def update(self, timeout=None):
        """Update messages - in mock mode, does nothing"""
        self.frame += 1
        # Simulate occasional updates
        if self.frame % 10 == 0:
            for topic in self.topics:
                self.updated[topic] = True
        return True
    
    def __getitem__(self, key):
        """Get message by topic name"""
        if key == 'carControl':
            return self._carControl
        elif key == 'controlsState':
            return self._controlsState
        return MockMessage()

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
