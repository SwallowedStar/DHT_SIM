# DHT_SIM
Ce projet a pour but de réaliser une simulation d'une DHT en python avec simpy. Nous allons voir dans la suite qu'est ce que nous avons fait et comment.

# Sommaire
Voici tous les sujet abordé dans ce README : 
- [Lancer le programme](#lancer-le-programme)
- [Ce que nous avons faits ](#ce-que-nous-avons-faits)
- [La structure du code](#la-structure-du-code)
    - [La classe Queue](#la-classe-queue)
    - [La classe Message](#la-classe-message)
    - [La classe MessageType](#la-classe-messagetype)
    - [La classe Node](#la-classe-Node)
- [Le fonctionnement du programme](#le-fonctionnement-du-programme)
    - [Initialisation](#initialisation)
    - [Un noeud peut quitter la DHT](#un-noeud-peut-quitter-la-dht)
    - [Intégration de nouveaux noeuds de manière concurente ](#intégration-de-nouveaux-noeuds-de-manière-concurente)
    - [Envoie de messages](#envoie-de-messages)
- [Les difficultés rencontrées](#les-difficultés-rencontrées)
- [Conclusion](#conclusion)

# Lancer le programme 
Pour lancer le programme, vous aurez besoins de plusieurs choses. \

Tout d'abord, vous devez installer les dependencies via le `requirements.txt` : 

```sh
pip3 install -r requirements.txt
```

Ensuite, vous pouvez lancer le programme : 
```sh
python3 main.py
```

Vous pourrez ensuite voir l'image de la DHT finale sur matplotlib, ou alors vous pouvez la visualiser dans l'image "test.png".
# Ce que nous avons faits 

Voici, pour résumer, ce que nous avons faits : 

- Créations de plusieurs classes et méthodes pour réaliser la DHT.
- On peut insérer un noeud dans la DHT.
- On peut retirer un noeud de la DHT
- Un système d'ACK est mis en place
- Les messages passent par une QUEUE globale ( on a "triché" pour simplifier un peu la gestion des messages )
- Pour insérer un noeud, on tourne dans les deux sens


# La structure du code
Dans cette partie , nous allons revenir sur les différentes classes présentes dans notre projet.


## La classe Queue
La classe Queue est une implémentation d'une file d'attente  pour gérer les messages entre les nœuds d'une DHT. \
C'est un singleton qui stocke et de gérer les messages en attente d'être traités par les nœuds.

Nous retrouvons d'abord des méthodes classiques, c.a.d le constructeur ainsi qu'une methode send et consume pour ajouter / enlever des messages de la queue.

Enfin,nous avons la méthode messages_for qui renvoie tout les messages qui sont dirigé à un certain noeud. C'est cette méthode qui est utilisé par chaque noeud pour aller chercher tous les messages qui lui sont destinés.

```py
    def messages_for(self, label: str) -> list:
        return [m for m in self.queue if m.receiver.label == label]
```

[Retour au sommaire](#sommaire)

## La classe Message

La classe Message représente un message échangé entre les nœuds dans le réseau DHT. Les messages sont utilisés pour gérer la communication entre les nœuds, notamment pour la connexion, la mise à jour des voisins et l'envoi d'ACK.

Un message possède : 
- Un emetteur `emitter: Node`
- Un recepteur `receiver: Node` 
- Un contenu `message_content: Any`
- Un type `message_type: MessageType`
- Un emetteur original `original_emitter`. Cette propriété permet de connaitre l'origine d'un message qui doit passer par plusieurs noeuds. 

Elle possède un constructeur, ainsi que la méthode surchargé __eq__ qui va permettre de comparer deux Messages.

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
[Retour au sommaire](#sommaire)

## La classe MessageType
La classe MessageType est une énumération qui permet de représenter les différents types de messages qui peuvent être envoyés entre les nœuds du réseau DHT.
Dans le code, les différents types de messages sont les suivants:

- `SET_LEFT_NEIGHBOUR` : ce type de message est utilisé pour définir le nœud voisin de gauche d'un nœud.
- `SET_RIGHT_NEIGHBOUR` : ce type de message est utilisé pour définir le nœud voisin de droite d'un nœud.
- `CONNECTION` : ce type de message est utilisé pour demander la connexion d'un nouveau nœud a la DHT.
- `ACK` : ce type de message est utilisé pour confirmer la réception d'un message par un nœud.
- `LEAVE` : ce type de message est utilisé pour notifier un nœud qu'un autre nœud est sur le point de quitter la DHT.
- `TEXT_MESSSAGE` : ce type de message est utilisé pour envoyer du texte à un autre noeud.

[Retour au sommaire](#sommaire)

## La classe Node 
C'est la classe la plus importante de l'application et la plus grande, elle réprésente un noeud dans une DHT. Le code de certaines méthodes ne seront pas affiché ici car trop grand ou pas pertinent.

Elle va etre définie de cette façon :

- label : une étiquette (label) unique pour le noeud.
- hash : un hash unique pour le noeud.
- env : une instance de la classe Environment de SimPy.
- primary : la porte d'entrée de la DHT (mis à None si le noeud fait déja partie d'une DHT).
- left_neighbour : le voisin gauche du noeud (self à l'initialisation).
- right_neighbour : le voisin droit du noeud, (self à l'initialisation).

Nous avons ensuite la méthode `set_right_neighbour` et `set_left_neighbour` qui vont permettre de définir le voisin droit et gauche du noeud, ainsi que la méthode get_hash , la méthode surchargé __str__ et __eq__.

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

La méthode `run` est la méthode génératrice qui est utilisé par simpy pour la simulation. Elle est exécutée en boucle et effectue les actions nécessaires pour maintenir le réseau DHT. Elle attend également les messages qui lui sont destinés. 

Une autre méthode importante est le `create_link`, qui crée un lien entre le noeud courant et un autre noeud. Elle est utiliser pour pouvoir insérer un noeud dans une DHT et creer les liens entre les noeuds.

Enfin, la dernière méthode est `leave`, qui permet au noeud de quitter la DHT. Elle informe ses voisins qu'il va quitter le réseau et met à jour la liste des noeuds du réseau en conséquence.

Les méthodes "send_text_message" et "deliver_message" sont toutes les 2 utilisées pour transmettre des messages textuels dans la dht. 

[Retour au sommaire](#sommaire)


# Le fonctionnement du programme 

Dans cette partie, nous allons vous décrire la conduite du programme et comment les noeuds intéragissent entre eux.

Nous avons effectué la simulation en 4 temps : 
1. Initialisation du noeud 1 et la connection de tous les noeuds via le noeud 1
2. Un noeud au hasard quitte la DHT
3. Intégration de nouveaux noeuds de manière concurente
4. Envoie de message entre 2 noeuds au hasard

## Initialisation 

Lors de l'initialisation, seule le noeud 1 est intégré à la DHT, et c'est le seul qui va permettre aux autres de se connecter.

Un noeud est considéré comme "hors de la DHT" si la propriété "primary" est défini. Cette propriété défini le point d'entrée d'une DHT déja existante. 

```py
n1 = Node("40", env, primary=None) # Ce noeud fait partie de la DHT
n = Node(label, env, primary=n1) # Ce noeud va se connecter à une DHT avec la porte d'entrée n1
```

Ce système peut nous permettre de simuler plusieurs DHT en même temps, bien que ce n'est pas le but de l'exercice.

La connexion d'un nouveau nouveau **N4** noeud via le noeud **N1** se passe de la manière suivante : 

(imaginons : **N1** -> **N3** -> **N5**)

1. **N4** envoie un message de type MessageType.CONNECTION à **N1**. A ce moment, **N4** est bloqué tant qu'il ne reçoit pas de ACKde **N1**.

2. **N1** renvoie un ack, puis détermine que **N4** ne va pas être un de ses voisins. \
Il renvoit donc la demande de connexion à **N3**.

3. **N3** renvoie un ack, puis détermine que **N4** va être son voisin de droite. \
Il bloque toutes les autres demandes de connexions à venir avec le booléen *connecting*. \
Il envoie donc un message SET_LEFT_NEIGHBOR à **N4**.

4. **N4** renvoie un ack, puis set son voisin gauche à **N3**.

5. **N3** envoie un message SET_RIGHT_NEIGHBOR à **N4**.

6. **N4** renvoie un ack, puis set son voisin droit à **N5**.

7. **N3** envoie un message à SET_LEFT_NEIGHBOR à **N5**.

8. **N5** renvoie un ack, puis set son voisin de gauche à **N4**. 

9. **N3** set son voisin de gauche à **N4**.

[Retour au sommaire](#sommaire)
## Un noeud peut quitter la DHT

Nous avons vu ci-dessus comment nous construisons la DHT. Nous avons aussi ajouté la possibilité qu'un noeud puisse quiter la DHT. Imaginons que c'est le noeud **N4** qui veut quitter la DHT, et qu'il est entre le noeud **N3** et **N5**.Le système d'ACK a déjà été expliqué ci-dessus et ce que font les SET_XXX, nous ne le re-mettrons pas par la suite, car à chaque fois, c'est la meme chose.
Voici les différents étapes:

1. Un noeud (qu'on appelle "traitre") veut quitter la DHT,**N4**,et appelle donc la méthode leave().

2. Dans cette méthode,**N4** récupère ses voisins.

3. Ensuite, **N4** envoie un message SET_RIGHT_NEIGHBOUR à **N3**.

4. Ensuite, **N4** envoie un message SET_LEFT_NEIGHBOUR à **N4**.

5. Suite à cela, **N4** se déconnecte lui meme en mettant à jour son voisin de gauche et de droite comme lui meme.

6. **N4** se supprime de la liste dht_nodes.

7. Enfin, la simulation continue , en mettant un temps d'attente avec :
```py
yield self.env.timeout(random.random())
```

[Retour au sommaire](#sommaire)

## Intégration de nouveaux noeuds de manière concurente : 

Dans cette partie, nous choisisons labels au hasard, puis nous les connectons à des noeuds au hasards appartenant à la DHT.

Cette partie ne pose pas problème grace au système mentionné dans la partie "Initialisation".

[Retour au sommaire](#sommaire)

## Envoie de messages

Pour cette partie, nous choisissons 1 sender et 1 receiver au hasard dans a DHT.

Le sender va envoyer le message "Hello world" au receiver. \
Ce message sera encapsulé dans un message de type "TEXT_MESSAGE". \
Le contenu sera fait de cette manière : 
```js
{
    "receiver": 3 // hash du recever
    "content" : "Hello world" // le message que l'on souhaite envoyer
}
``` 

Pour simuler cette évènement, nous créont un nouveau processus, dont "send_text_message" est la méthode génératrice. 

 Cette fonction, à chaque fois qu'elle est appelée, cherche son voisin le plus proche du recepteur, puis lui envoie le message pour continuer la chaine.  

 A la réception d'un message de type "TEXT_MESSAGE", la méthode "deliver_message". \
 Cette méthode, dans un premier temps, vérifie qu'elle est bien la destination finale du message. Si ce n'est pas le cas, la méthode "send_text_message" est de nouveau appelée.


[Retour au sommaire](#sommaire)

# Les difficultés rencontrées

Dans ce projet, nous avons eu deux grandes difficultés. D'abord , il a fallu réussir à comprendre simpy et à l'utiliser, ce qui n'était pas simple, au vu du peu d'informations présent sur internet. C'est meme la plus grande diffuclté, de réussir à l'utiliser et à penser en mode "simulation" et pas en mode "normale".

L'autre grande difficultés, cela a été d'implémenté le système d'ACK. Sur le papier, ça paraissait simple, mais nous avons passés beaucoup,beaucoup de temps à mettre en place ce système. Nous avons plus passés de temps sur les ACK que sur le reste. Et encore, nous avons un peu "triché" en faisant une QUEUE globale.

[Retour au sommaire](#sommaire)

# Conclusion
Pour conclure,ce projet fut intéressant, bien que pas simple. Nous avons réussis à aller jusqu'a l'etape 2 , en parti à causes des difficultés rencontrés lors de la mise en place des ACK et de comprendre simpy. Malgré cela, ce projet nous a permis de mieux comprendre les réseaux distribué et la difficulté de leur implémentations . C'est quelque chose qui, sur le papier, ne parait pas si compliquer que cela, mais quand nous avons commencés à coder, nous nous sommes vite rendu compte que ce n'était pas aussi simple. C'était aussi intéressant de découvrir simpy,que nous ne connaissions pas du tout. Enfin, il serait intéressant pour nous de continuer le projet et de voir le stockage des données ou des méthodes de construction de DHT plus efficaces

[Retour au sommaire](#sommaire)