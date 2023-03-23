import random
import simpy
from enum import Enum

class Queue:
    def __init__(self) -> None:
        self.queue = []
    
    def connection_occuring(self):
        connection_requests = [m for m in self.queue if m.message_type == MessageType.SET_LEFT_NEIGHBOUR or m.message_type == MessageType.SET_RIGHT_NEIGHBOUR ]
        return len(connection_requests) > 0
    
    def messages_for(self, label: str):
        return [m for m in self.queue if m.receiver.label == label]
    
    def append(self, value):
        self.queue.append(value)

    def remove(self, value):
        self.queue.remove(value)

QUEUE = Queue()

CONNECTION_OCCURING = False
class MessageType(Enum):
    CONNECTION = 1
    ACK_CONNECTION = 2
    ACK_MESSAGE = 3
    LEAVE = 4
    SET_LEFT_NEIGHBOUR = 5
    SET_RIGHT_NEIGHBOUR = 6

class Message:
    def __init__(self, receiver, message_type : MessageType, message_content = None, original_emitter = None):
        self.emitter : Node = None
        self.original_emitter : Node = original_emitter if original_emitter is not None else self.emitter
        self.receiver : Node = receiver
        self.message_content = message_content
        self.message_type : MessageType = message_type

    def set_emitter(self, emitter):
        self.emitter : Node = emitter
        if not self.original_emitter:
            self.original_emitter = self.emitter 
    
    def __str__(self) -> str:
        if type(self.message_content) == dict:
            if "right" in self.message_content.keys():
                return f"({self.message_type}) {self.emitter.label} -> {self.receiver.label} right : {self.message_content['right'].label}, original_emitter : {self.original_emitter.label}"
            elif "left" in self.message_content.keys():
                return f"({self.message_type}) {self.emitter.label} -> {self.receiver.label} left : {self.message_content['left'].label}, original_emitter : {self.original_emitter.label}"
                
        else :
            return f"({self.message_type}) {self.emitter.label} -> {self.receiver.label} original_emitter : {self.original_emitter.label}"

class Node:
    def __init__(self, label, env, primary, left_neighbour = None, right_neighbour = None):
        self.env = env
        self.label = label
        self.hash = hash_function(self.label)
        self.left_neighbour : Node = self if not left_neighbour else left_neighbour
        self.right_neighbour : Node = self if not right_neighbour else right_neighbour
        self.primary = primary
    
    def send_message(self, message: Message):
        print("Send message at time", env.now)
        print(f"I am {self.label}")
        message.set_emitter(self)
        QUEUE.append(message)

        for m in QUEUE.queue:
            print(m)

    def get_name(self):
        return self.label
    
    def get_hash(self):
        return self.hash

    def set_right_neighbour(self,node):
        self.right_neighbour=node

    def set_left_neighbour(self,node):
        self.left_neighbour=node

    def __str__(self) -> str:
        res_str="Voisin de gauche : "
        res_str += self.left_neighbour.get_name()+" "
        res_str += " ///// Voisin de droite : "

        res_str += self.right_neighbour.get_name()+" "
        return res_str
    
    def run(self):
        global CONNECTION_OCCURING
        if(self.primary is not None):
            message = Message(receiver=self.primary, message_content="connection", message_type=MessageType.CONNECTION)
            self.send_message(message)
        while True:
            
            my_messages = QUEUE.messages_for(self.label) 
            if len(my_messages) > 0:
                mess = my_messages.pop()
                type_mess=mess.message_type
                if(type_mess==MessageType.CONNECTION):
                    
                    while QUEUE.connection_occuring():
                        yield self.env.timeout(1)
                    CONNECTION_OCCURING = True
                    self.create_link(mess.original_emitter)
                    QUEUE.remove(mess)
                    CONNECTION_OCCURING = False

                elif type_mess == MessageType.LEAVE:
                    pass
                    QUEUE.remove(mess)
                elif type_mess == MessageType.ACK_CONNECTION:
                    pass
                    QUEUE.remove(mess)
                elif type_mess == MessageType.ACK_MESSAGE:
                    pass
                    QUEUE.remove(mess)
                elif type_mess == MessageType.SET_RIGHT_NEIGHBOUR:
                    self.set_right_neighbour(mess.message_content["right"])
                    QUEUE.remove(mess)
                elif type_mess == MessageType.SET_LEFT_NEIGHBOUR:
                    self.set_left_neighbour(mess.message_content["left"])
                    QUEUE.remove(mess)

                
            yield self.env.timeout(1)
    
    def create_link(self, node):
        if node.get_hash() > self.hash:
            if self.right_neighbour.get_hash() > node.get_hash() or self.right_neighbour.get_hash() <= self.hash:
                message = Message(receiver=node, message_content={"right": self.right_neighbour}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)

                message = Message(receiver=node, message_content={"left": self}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)
                
                message = Message(receiver=self.right_neighbour, message_content={"left": node}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)

                self.right_neighbour = node
            else : 
                message = Message(original_emitter=node, receiver=self.right_neighbour, message_type=MessageType.CONNECTION)
                self.send_message(message)

        elif node.get_hash() < self.hash:
            if self.left_neighbour.get_hash() < node.get_hash() or self.left_neighbour.get_hash() == self.hash:
                message = Message(receiver=node, message_content={"left": self.left_neighbour}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)

                message = Message(receiver=node, message_content={"right": self}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)

                message = Message(receiver=self.left_neighbour, message_content={"right": node}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)

                self.left_neighbour = node
            else : 
                message = Message(original_emitter=node, receiver=self.left_neighbour, message_type=MessageType.CONNECTION)
                self.send_message(message)
    def __eq__(self, __value: object) -> bool:
        return self.label == __value.label

def hash_function(text):
    # return sum(ord(character) for character in text)
    return int(text)

env = simpy.Environment()
random.seed(10)

n1 = Node("1", env, primary=None)
env.process(n1.run())

dht_nodes = [n1]

nodes_to_add = []
NB_NODES = 5
for i in range(NB_NODES):
    label =  str(random.randint(2, 1000))
    while label in nodes_to_add:
        label =  str(random.randint(2, 1000))
    nodes_to_add.append(label)

print(nodes_to_add)

for label in nodes_to_add:
    node = n1
    n = Node(label, env, primary=node)
    env.process(n.run())
    dht_nodes.append(n)

env.run(until=10000)

print(len(QUEUE.queue))

for n in dht_nodes:
    print(f"{n.left_neighbour.label} -- {n.label} -- {n.right_neighbour.label}")

for message in QUEUE.queue:
    print(message)