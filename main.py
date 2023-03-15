import random
import simpy
from enum import Enum

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

class Node:
    def __init__(self, label, env, left_neighbour = None, right_neighbour = None):
        self.env = env
        self.label = label
        self.hash = hash_function(self.label)
        self.left_neighbour : Node = self if not left_neighbour else left_neighbour
        self.right_neighbour : Node = self if not right_neighbour else right_neighbour
        self.messages = []
        # self.messages = simpy.Store(env)
    
    def receive_message(self, message):
        print("Receive message at time", env.now) 
        self.messages.append(message)
        self.queue()
        print(1)
        

    def send_message(self, message: Message):
        print("Send message at time", env.now)
        message.set_emitter(self)
        message.receiver.receive_message(message)

    def get_righ_neighbour(self):
        return self.right_neighbour
    
    def get_left_neighbour(self):
        return self.left_neighbour
    
    def get_name(self):
        return self.label
    
    def set_hash(self,hash):
        self.hash = hash
    
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

    def queue(self):
        mess=self.messages.pop()
        type_mess=mess.message_type
        if self.label == "1" and type_mess == MessageType.CONNECTION:
            pass
        if(type_mess==MessageType.CONNECTION):
            self.create_link(mess.original_emitter)
        elif type_mess == MessageType.LEAVE:
            pass
        elif type_mess == MessageType.ACK_CONNECTION:
            pass
        elif type_mess == MessageType.ACK_MESSAGE:
            pass
        elif type_mess == MessageType.SET_RIGHT_NEIGHBOUR:
            self.set_right_neighbour(mess.message_content["right"])
        elif type_mess == MessageType.SET_LEFT_NEIGHBOUR:
            self.set_left_neighbour(mess.message_content["left"])
    
    def create_link(self, node):

        if node.get_hash() > self.hash:
            if self.right_neighbour.get_hash() > node.get_hash() or self.right_neighbour.get_hash() <= self.hash:
                message = Message(receiver=node, message_content={"right": self.right_neighbour}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)

                message = Message(receiver=node, message_content={"left": self}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)

                # node.set_right_neighbour(self.right_neighbour) # Remplacer avec un send message
                # node.set_left_neighbour(self) # Remplacer avec un send message

                message = Message(receiver=self.right_neighbour, message_content={"left": node}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)

                # self.right_neighbour.set_left_neighbour(node) # Remplacer avec un send message
                self.right_neighbour = node
            else : 
                message = Message(original_emitter=node, receiver=self.right_neighbour, message_type=MessageType.CONNECTION)
                self.send_message(message)
                
                # self.right_neighbour.create_link(node) # Remplacer avec un send message
        elif node.get_hash() < self.hash:
            if self.left_neighbour.get_hash() < node.get_hash() or self.right_neighbour.get_hash() == self.hash:
                message = Message(receiver=node, message_content={"left": self.left_neighbour}, message_type=MessageType.SET_LEFT_NEIGHBOUR)
                self.send_message(message)

                message = Message(receiver=node, message_content={"right": self}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)
                
                # node.set_left_neighbour(self.left_neighbour) # Remplacer avec un send message
                # node.set_right_neighbour(self) # Remplacer avec un send message

                message = Message(receiver=self.left_neighbour, message_content={"right": node}, message_type=MessageType.SET_RIGHT_NEIGHBOUR)
                self.send_message(message)

                # self.left_neighbour.set_right_neighbour(node) # Remplacer avec un send message
                self.left_neighbour = node
            else : 
                message = Message(original_emitter=node, receiver=self.left_neighbour, message_type=MessageType.CONNECTION)
                self.send_message(message)

                # self.left_neighbour.create_link(node) # Remplacer avec un send message


def hash_function(text):
    return sum(ord(character) for character in text)

def createNode(label, env, dht_nodes: list):
    n = Node(label, env)
    node = random.choice(dht_nodes)
    message = Message(receiver=node, message_content="connection", message_type=MessageType.CONNECTION)
    yield env.process(n.send_message(message))


env = simpy.Environment()
random.seed(10)

n1 = Node("1", env)
dht_nodes = [n1]

nodes_to_add = []
NB_NODES = 5
for i in range(NB_NODES):
    label =  str(random.randint(0, 100))
    while label in nodes_to_add:
        label =  str(random.randint(0, 100))
    nodes_to_add.append(label)

for label in nodes_to_add:
    env.process(createNode(label, env, dht_nodes))

env.run(until=20)

