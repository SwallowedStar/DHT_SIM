# DHT_SIM
Ce projet a pour but de réaliser une simulation d'une DHT en python avec simpy. Nous allons voir dans la suite qu'est ce que nous avons fait et comment.

# Les bases du code
Dans cette partie , nous allons revenir sur les différentes classes présentes dans notre projet.

## La classe Queue
La classe Queue est une implémentation d'une file d'attente  pour gérer les messages entre les nœuds d'une DHT. Cette classe permet de stocker et de gérer les messages en attente d'être traités par les nœuds.

Nous retrouvons d'abord des méthodes classiques,c.a.d le constructeur ainsi qu'une methode append et remove pour ajouter / enlever des messages de la QUEUE.


Ensuite, nous avons la méthode blocking_operation_occuring qui vérifie si des opérations bloquantes sont en cours dans la file d'attente. Elle retourne True si des messages de type SET_LEFT_NEIGHBOUR ou SET_RIGHT_NEIGHBOUR sont en attente, sinon False. Elle permet d'éviter que deux nodes cherchent à s'insérer en meme temps.

```py
    def blocking_operation_occuring(self, emitter):
        q = self.messages_for(emitter.label)
        
        connection_requests = [m for m in q if m.message_type == MessageType.SET_LEFT_NEIGHBOUR or m.message_type == MessageType.SET_RIGHT_NEIGHBOUR ]
        return len(connection_requests) > 0
    
```

Enfin,nous avons la méthode find_all qui recherche et retourne les messages dans la file d'attente selon certains critéres, comme le type de message. Elle agit comme un filtre.

```py
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
```

## La classe Message
La classe Message représente un message échangé entre les nœuds dans le réseau DHT. Les messages sont utilisés pour gérer la communication entre les nœuds, notamment pour la connexion, la mise à jour des voisins et l'envoi d'ACK.

Elle possède un constructeur,ainsi que la méthode surchargé __eq__ qui va permettre de comparer deux Messages.

```py
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Message) and __value is not None:
            bo = self.receiver == __value.receiver
            bo = bo and self.emitter == __value.emitter
            bo = bo and self.original_emitter == __value.original_emitter
            bo = bo and self.message_content == __value.message_content
            return  bo
        else : 
            return False
```

Il y a aussi la méthode set_emitter qui permet de définir l'émetteur du message et la méthode surchargé __str__.

```py
    def set_emitter(self, emitter):
        self.emitter : Node = emitter
        if not self.original_emitter:
            self.original_emitter = self.emitter 
```

## La classe MessageType
La classe MessageType est une énumération qui permet de représenter les différents types de messages qui peuvent être envoyés entre les nœuds du réseau DHT.
Dans le code, les différents types de messages sont les suivants:

    -SET_LEFT_NEIGHBOUR : ce type de message est utilisé pour définir le nœud voisin de gauche d'un nœud.
    -SET_RIGHT_NEIGHBOUR : ce type de message est utilisé pour définir le nœud voisin de droite d'un nœud.
    -CONNECTION : ce type de message est utilisé pour demander la connexion d'un nouveau nœud a la DHT.
    -ACK : ce type de message est utilisé pour confirmer la réception d'un message par un nœud.
    -LEAVE : ce type de message est utilisé pour notifier un nœud qu'un autre nœud est sur le point de quitter la DHT.


## La classe Node 
C'est la classe la plus importante de l'application et la plus grande, elle réprésente un noeud dans une DHT. Le code de certaines méthodes ne seront pas affiché ici car trop grand ou pas pertinent.

Elle va etre définie de cette façon :

    -label : une étiquette (label) unique pour le noeud.
    -env : une instance de la classe Environment de SimPy.
    -primary : le noeud primaire de la DHT.
    -left_neighbour : le voisin gauche du noeud, s'il existe.
    -right_neighbour : le voisin droit du noeud, s'il existe.

Nous avons ensuite la méthode set_right_neighbour et set_left_neighbour qui vont permettre de définir le voisin droit et gauche du noeud, ainsi que la méthode get_hash , la méthode surchargé __str__ et __eq__.

Ensuite, nous avons send_messages qui permet d'envoyer un message à une autre node, en l'ajoutant dans la Queue. Un logger est utuilise pour conserver tous les messages envoyés pendant ka simulation.
```py
    def send_message(self, message: Message):
        logging.info(f"Send message at time {env.now}")
        message.set_emitter(self)
        logging.info(f"Message {message}")
        if not message.message_type == MessageType.ACK:
            self.waiting_for_ack.append(message)
        QUEUE.append(message)
```

Nous avons aussi la méthode run, qui est la méthode principal du noeud et meme de la simulation. Elle est exécutée en boucle et effectue les actions nécessaires pour maintenir le réseau DHT. Elle attend également les messages qui lui sont destinés. 

Une autre méthode importante est le create_link, qui crée un lien entre le noeud courant et un autre noeud. Elle est utiliser pour pouvoir insérer un noeud dans une DHT et creer les liens entre les noeuds.


Enfin, la dernière méthode est leave, qui permet au noeud de quitter la DHT. Elle informe ses voisins qu'il va quitter le réseau et met à jour la liste des noeuds du réseau en conséquence.



# Comment fonctionne le programme 



# Les difficultés rencontrées

Dans ce projet, nous avons eu deux grandes difficultés. D'abord , il a fallu réussir à comprendre simpy et à l'utiliser, ce qui n'était pas simple, au vu du peu d'informations présent sur internet. C'est meme la plus grande diffuclté, de réussir à l'utiliser et à penser en mode "simulation" et pas en mode "normale".

L'autre grande difficultés, cela a été d'implémenté le système d'ACK. Sur le papier, ça paraissait simple, mais nous avons passés beaucoup,beaucoup de temps à mettre en place ce système. Nous avons plus passés de temps sur les ACK que sur le reste.

# Conclusion


