import random
from simpy import Environment
from enum import Enum
import logging
import networkx as nx
import matplotlib.pyplot as plt

logging.basicConfig(filename="messages.log", encoding="utf-8", level=logging.DEBUG, filemode="w")

class Queue:
    def __init__(self) -> None:
        self.queue = []
    
    def blocking_operation_occuring(self, emitter):
        q = self.messages_for(emitter.label)
        
        connection_requests = [m for m in q if m.message_type == MessageType.SET_LEFT_NEIGHBOUR or m.message_type == MessageType.SET_RIGHT_NEIGHBOUR ]
        return len(connection_requests) > 0
    
    def messages_for(self, label: str) -> list:
        return [m for m in self.queue if m.receiver.label == label]
    
    def append(self, value):
        self.queue.append(value)

    def remove(self, value):
        self.queue.remove(value)
    
    def find_all(self, emitter, receiver, message_type = None, message_content = None):
        temp_queue = self.queue.copy()
        if emitter:
            temp_queue = [m for m in temp_queue if m.emitter == emitter]
        if receiver : 
            temp_queue = [m for m in temp_queue if m.receiver == receiver]
        if message_type : 
            temp_queue = [m for m in temp_queue if m.message_type == message_type]
        if message_content : 
            temp_queue = [m for m in temp_queue if m.message_content == message_content]
        
        return temp_queue

QUEUE = Queue()

class MessageType(Enum):
    SET_LEFT_NEIGHBOUR = 1
    SET_RIGHT_NEIGHBOUR = 2
    CONNECTION = 3
    ACK_CONNECTION = 4
    ACK = 5
    LEAVE = 6
    
class Message:
    def __init__(self, receiver, message_type : MessageType, message_content = None, original_emitter = None, emitter=None):
        self.emitter : Node = emitter
        self.original_emitter : Node = original_emitter if original_emitter is not None else self.emitter
        self.receiver : Node = receiver
        self.message_content = message_content
        self.message_type : MessageType = message_type

    def set_emitter(self, emitter):
        self.emitter : Node = emitter
        if not self.original_emitter:
            self.original_emitter = self.emitter 
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Message) and __value is not None:
            bo = self.receiver == __value.receiver
            bo = bo and self.emitter == __value.emitter
            bo = bo and self.original_emitter == __value.original_emitter
            bo = bo and self.message_content == __value.message_content
            return  bo
        else : 
            return False
    
    def __str__(self) -> str:
        if type(self.message_content) == dict:
            if "right" in self.message_content.keys():
                return f"({self.message_type}) {self.emitter.label} -> {self.receiver.label} right : {self.message_content['right'].label}, original_emitter : {self.original_emitter.label}"
            elif "left" in self.message_content.keys():
                return f"({self.message_type}) {self.emitter.label} -> {self.receiver.label} left : {self.message_content['left'].label}, original_emitter : {self.original_emitter.label}"
        elif type(self.message_content) == Message:
            return f"({self.message_type}) {self.emitter.label} -> {self.receiver.label} for {self.message_content.message_type}(original_emitter : {self.original_emitter.label}, {self.receiver.label})"
        else :
            return f"({self.message_type}) {self.emitter.label} -> {self.receiver.label} original_emitter : {self.original_emitter.label}"

class Node:
    def __init__(self, label, env, primary, left_neighbour = None, right_neighbour = None):
        self.env : Environment = env
        self.label : str = label
        self.hash : int = hash_function(self.label)
        self.left_neighbour : Node = self if not left_neighbour else left_neighbour
        self.right_neighbour : Node = self if not right_neighbour else right_neighbour
        self.primary = primary
        self.waiting_for_ack: list(Message) = []
        self.connection_timeout = 5
        self.leaving = False
        self.connecting = False
        self.sent_ack_to = []
    
    def send_message(self, message: Message):
        logging.info(f"Send message at time {env.now}")
        message.set_emitter(self)
        logging.info(f"Message {message}")
        if not message.message_type == MessageType.ACK:
            self.waiting_for_ack.append(message)
        QUEUE.append(message)
    
    def get_hash(self):
        return self.hash

    def set_right_neighbour(self,node):
        self.right_neighbour=node

    def set_left_neighbour(self,node):
        self.left_neighbour=node

    def __str__(self) -> str:
        return self.label
    
    def run(self):
        if(self.primary is not None):

            if self.label == "1" or self.label == "15":
                pass
            message = Message(receiver=self.primary, message_content="connection", message_type=MessageType.CONNECTION)
            self.send_message(message)
            ack = QUEUE.find_all(emitter=self.primary, receiver=self, message_content=message, message_type=MessageType.ACK)
            while len(ack) < 1 :
                yield self.env.timeout(1)
                ack = QUEUE.find_all(emitter=self.primary, receiver=self, message_content=message, message_type=MessageType.ACK)
            QUEUE.remove(ack[0])

        while True:
            my_messages: list(Message) = QUEUE.messages_for(self.label)

            for m in my_messages:
                if m not in self.sent_ack_to and m.message_type != MessageType.ACK:
                    ack_message = Message(receiver = m.emitter, message_type= MessageType.ACK, message_content = m)
                    self.send_message(ack_message)
                    self.sent_ack_to.append(m)

            if self.connecting:
                my_messages = [m for m in my_messages if m.message_type != MessageType.CONNECTION]

            if len(my_messages) > 0 and not self.leaving:
                message_received = None

                for m in my_messages:
                    if m.message_type == MessageType.CONNECTION:
                        message_received = m
                        break
                
                if not message_received:
                    message_received = my_messages[0]

                type_mess = message_received.message_type

                if(type_mess==MessageType.CONNECTION):
                    QUEUE.remove(message_received)

                    while QUEUE.blocking_operation_occuring(self) and self.connecting:
                        yield self.env.timeout(1)

                    env.process(self.create_link(message_received.original_emitter))
                
                elif type_mess == MessageType.ACK:
                    if message_received.message_content in self.waiting_for_ack:
                        self.waiting_for_ack.remove(message_received.message_content)
                        QUEUE.remove(message_received)

                elif type_mess == MessageType.SET_RIGHT_NEIGHBOUR:
                    self.set_right_neighbour(message_received.message_content["right"])
                    QUEUE.remove(message_received)

                elif type_mess == MessageType.SET_LEFT_NEIGHBOUR:
                    self.set_left_neighbour(message_received.message_content["left"])
                    QUEUE.remove(message_received)
                
            yield self.env.timeout(1)

    def create_link(self, node):
        self.connecting = True
        if node.get_hash() > self.hash:
            if self.right_neighbour.get_hash() > node.get_hash() or self.right_neighbour.get_hash() <= self.hash:
                message = Message(receiver=node, message_content={"right": self.right_neighbour}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)
                while message in self.waiting_for_ack :
                    yield self.env.timeout(1)

                message = Message(receiver=node, message_content={"left": self}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)
                while message in self.waiting_for_ack :
                    yield self.env.timeout(1)

                if self.left_neighbour == self:
                    self.left_neighbour = node
                else : 
                    message = Message(receiver=self.right_neighbour, message_content={"left": node}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                    self.send_message(message)
                    while message in self.waiting_for_ack :
                        yield self.env.timeout(1)

                self.right_neighbour = node
            else : 
                message = Message(original_emitter=node, receiver=self.right_neighbour, message_type=MessageType.CONNECTION)
                self.send_message(message)
                while message in self.waiting_for_ack :
                    yield self.env.timeout(1)

        elif node.get_hash() < self.hash:
            if self.left_neighbour.get_hash() < node.get_hash() or self.left_neighbour.get_hash() >= self.hash:
                message = Message(receiver=node, message_content={"left": self.left_neighbour}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)
                while message in self.waiting_for_ack :
                    yield self.env.timeout(1)

                message = Message(receiver=node, message_content={"right": self}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)
                while message in self.waiting_for_ack :
                    yield self.env.timeout(1)

                if self.right_neighbour == self:
                    self.right_neighbour = node
                else : 
                    message = Message(receiver=self.left_neighbour, message_content={"right": node}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                    self.send_message(message)
                    while message in self.waiting_for_ack :
                        yield self.env.timeout(1)

                self.left_neighbour = node
            else : 
                message = Message(original_emitter=node, receiver=self.left_neighbour, message_type=MessageType.CONNECTION)
                self.send_message(message)
                while message in self.waiting_for_ack :
                    yield self.env.timeout(1)
        
        self.connecting = False

    def __eq__(self, __value: object) -> bool:
        return self.label == __value.label
    
    def leave(self):
        logging.info(f"Node {self.label} Quitting the DHT")
        left_node = self.left_neighbour
        right_node = self.right_neighbour

        message = Message(receiver=left_node, message_content={"right": right_node}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
        self.send_message(message)
        while message in self.waiting_for_ack :
            yield self.env.timeout(1)

        message = Message(receiver=right_node, message_content={"left": left_node}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
        self.send_message(message)
        while message in self.waiting_for_ack :
            yield self.env.timeout(1)

        self.left_neighbour = self
        self.right_neighbour = self
        
        dht_nodes.remove(self)
        yield self.env.timeout(1)
 
def hash_function(text):
    return int(text)

env = Environment()
random.seed(10)

n1 = Node("40", env, primary=None)
env.process(n1.run())

dht_nodes = [n1]

nodes_to_add = ["74", "5", "2", "62", "54"]

print(nodes_to_add)

for label in nodes_to_add:
    node = n1
    n = Node(label, env, primary=node)
    env.process(n.run())
    dht_nodes.append(n)

traitor = random.choice(dht_nodes)

print("TRAITOR")
print(traitor)

env.run(until=100)
env.process(traitor.leave())

env.run(until=400)

nodes_to_add = ["1", "15"]
for label in nodes_to_add:
    node = random.choice(dht_nodes)
    print("Node", label, "will be connecting to", node)
    n = Node(label, env, primary=node)
    env.process(n.run())
    dht_nodes.append(n)

env.run(until=900)


print("Queue length:", len(QUEUE.queue))

for n in dht_nodes:
    print(f"{n.left_neighbour.label} -- {n.label} -- {n.right_neighbour.label}")

for message in QUEUE.queue:
    print(message)
    
dht_graph = nx.Graph()
for node in dht_nodes:
    dht_graph.add_node(node.label)

for node in dht_nodes:
    dht_graph.add_edge(node.label, node.left_neighbour.label)
    dht_graph.add_edge(node.label, node.right_neighbour.label)
nx.draw(dht_graph, with_labels=True)
# plt.show(block=False)
plt.savefig("Graph.png", format="PNG")