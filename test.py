import random
class Node:

    def __init__(self, label, left_neighbour=None, right_neighbour=None):
        self.label = label
        self.left_neighbour = []
        self.right_neighbour = []
        self.known_left_neighbour=[]
        self.known_right_neighbour=[]
        self.hash=0

    def get_righ_neighbour(self):
        return self.right_neighbour
    
    def get_left_neighbour(self):
        return self.left_neighbour
    
    def get_known_left_neighbour(self):
        return self.known_left_neighbour
    def get_known_right_neighbour(self):
        return self.known_right_neighbour
    
    def get_name(self):
        return self.label
    
    def set_hash(self,hash):
        self.hash=hash
    
    def get_hash(self):
        return self.hash

    def set_right_neighbour(self,nodes):
        self.right_neighbour=[]
        self.right_neighbour.append(nodes)
        self.add_known_right_neighbour(nodes)

    def set_left_neighbour(self,nodes):
        self.left_neighbour=[]
        self.left_neighbour.append(nodes)
        self.add_known_left_neighbour(nodes)
    def __str__(self) -> str:
        res_str="Voisin de gauche :  "
        res_str+=self.left_neighbour[0].get_name()+" "
        res_str+=" ///// Voisin de droite : "


        res_str+=self.right_neighbour[0].get_name()+" "
        return res_str
    

    def add_known_right_neighbour(self,neighbours):
        len_add=len(neighbours)
        if(len(self.right_neighbour)<3 and (len(self.right_neighbour)+len_add)<=3):
             for x in neighbours:
                 self.known_right_neighbour.append(x)

    def add_known_left_neighbour(self,neighbours):
        len_add=len(neighbours)
        if(len(self.left_neighbour)<3 and (len(self.left_neighbour)+len_add)<=3):
             for x in neighbours:
                 self.known_left_neighbour.append(x)

    def affich_neighbour(self): 
        res_str="Node connus a Left= "
        for x in self.known_left_neighbour:
            res_str+=x.get_name()+" "
        res_str+=" /////// Nodes connus a Right= "

        for x in self.known_right_neighbour:
            res_str+=x.get_name()+" "

        return res_str


def hash_function(text):
    return sum(ord(character) for character in text)


n1=Node("test1")
n2=Node("test2")
n3=Node("test3")
n4=Node("test45343543543543")
n5=Node("test5")
n6=Node("54354353")
n7=Node("53")
n8=Node("test84")
is_empty=True

n1.set_hash(hash_function(n1.get_name()))
n2.set_hash(hash_function(n2.get_name()))
n3.set_hash(hash_function(n3.get_name()))
n4.set_hash(hash_function(n4.get_name()))
n5.set_hash(hash_function(n5.get_name()))
n6.set_hash(hash_function(n6.get_name()))
n7.set_hash(hash_function(n7.get_name()))
n8.set_hash(hash_function(n8.get_name()))

"""
n1.add_left_neighbour(n2)
n1.add_right_neighbour(n3)

n1.add_known_left_neighbour([n7,n8])
n1.add_known_right_neighbour([n5])
print(n1)

print(n1.affich_neighbour())

"""

l_all_nodes=[]




"""
def link_nodes(n,l_all_nodes):
    hash_node=hash_function(n.get_name())
    if(n1.get_left_neighbour()==[] and n1.get_righ_neighbour()==[]):
        rand=random.randint(1,2)
        if(rand==1):
            n1.add_left_neighbour(n)
        else:
            n1.add_right_neighbour(n)
    else:
        right_neighbour=n1.get_known_right_neighbour()
        len_neighbour=len(right_neighbour)
        for x in range(0,len_neighbour):
            hash_x=right_neighbour[x].get_hash()
            if(hash_node<hash_x):

"""        




def link_nodes(n, all_nodes):
    hash_node = hash_function(n.get_name())
    if all_nodes == []:
        # if there are no other nodes in the network, set this node as its own neighbour

        l_all_nodes.append(n)
    elif len(all_nodes) == 1:
        # if there is only one node in the network, set it as the neighbour of this node
        n.set_left_neighbour(all_nodes[0])
        n.set_right_neighbour(all_nodes[0])
        all_nodes[0].set_left_neighbour(n)
        all_nodes[0].set_right_neighbour(n)
        l_all_nodes.append(n)
    else:
        # find the correct position for this node in the ring
        right_neighbour = None
        for node in all_nodes:

            if node.get_hash() > hash_node:
             
                right_neighbour = node
                break
        if right_neighbour is None:
            # if this node has the highest hash value, set the first node as its neighbour
            right_neighbour = all_nodes[0]
        # set this node's neighbours
        print(right_neighbour)
        left_neighbour = right_neighbour.get_left_neighbour()
        print(left_neighbour)
        n.set_left_neighbour(left_neighbour[0])
        n.set_right_neighbour(right_neighbour)
        # update the neighbours' pointers
        
        left_neighbour[0].set_right_neighbour(n)
        right_neighbour.set_left_neighbour(n)
        l_all_nodes.append(n)



# This is the way 
# Boi 
        
link_nodes(n2,l_all_nodes)
print("turn2")
link_nodes(n1,l_all_nodes)
print("turn3")

link_nodes(n3,l_all_nodes)
print("turn4")

link_nodes(n4,l_all_nodes)
print("turn5")

link_nodes(n6,l_all_nodes)
print(n1)


