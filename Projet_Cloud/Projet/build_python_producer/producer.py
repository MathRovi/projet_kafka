from kafka import KafkaProducer  # Permet de produire des messages Kafka
import json  # Bibliothèque pour travailler avec le format JSON
import datetime  # Utilisé pour ajouter une date/heure aux tickets
import time  # Pour introduire des pauses entre les envois de tickets
import random  # Pour générer des articles et des tickets aléatoires

# Fonction pour créer un producteur Kafka
def create_producer():
    for _ in range(10):  # Essayer de se connecter pendant 10 tentatives
        try:
            producer = KafkaProducer(
                bootstrap_servers=['broker:9092'],  # Adresse du broker Kafka
                value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Sérialiser les messages en JSON avant de les envoyer
            )
            print("Kafka Producer connecté avec succès.")
            return producer
        except Exception as e:
            print(f"Tentative de connexion échouée : {e}. Retente dans 5 secondes.")
            time.sleep(5)
    raise Exception("Impossible de se connecter au broker Kafka après 10 tentatives.")

# Initialisation du producteur Kafka
producer = create_producer()

# Liste des articles disponibles
articles = [
    'Pommes', 'Poires', 'Clémentines',
    'Oranges', 'Jus de pomme', 'Jus de cassis',
    'Sac de patate', 'Poireau', 'Carrottes', 'Miel'
]

# Fonction pour générer un article aléatoire
def gen_article():
    nom = random.choice(articles)
    prix = int(round(random.uniform(5, 40)))
    quantite = random.randint(1, 5)
    return (nom, prix, quantite)

# Fonction pour générer un ticket contenant plusieurs articles
def gen_ticket_random():
    num_articles = random.randint(1, 10)
    ticket = []
    for _ in range(num_articles):
        nom, prix, quantite = gen_article()
        found = False
        for item in ticket:
            if item[0] == nom:
                # On met à jour le prix et la quantité dans le ticket
                item[1] += prix
                item[2] += quantite
                found = True
                break
        if not found:
            ticket.append([nom, prix, quantite])
    return ticket

# Classe pour représenter un ticket
class Ticket:
    def __init__(self):
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.article = gen_ticket_random()
        self.total = sum(a[1] * a[2] for a in self.article)
        # Ajout de l'ID de magasin (1, 2 ou 3)
        self.magasin_id = random.choice([1, 2, 3])

# Fonction pour envoyer des tickets par lot de 10
def send_ticket_to_kafka():
    tickets_buffer = []  # Liste pour stocker temporairement les tickets

    while True:
        # Générer un nouveau ticket
        ticket = Ticket()
        ticket_data = {
            "date": ticket.date,
            "articles": [
                {"Product": a[0], "price": a[1], "quantity": a[2]}
                for a in ticket.article
            ],
            "total": round(ticket.total, 2),
            "magasin_id": ticket.magasin_id  # <-- Ajout du champ magasin_id dans la structure du ticket
        }

        # Ajouter le ticket au buffer
        tickets_buffer.append(ticket_data)
        print(f"Ticket généré (non envoyé) : {ticket_data}")

        # Vérifier si le buffer a atteint 10 tickets
        if len(tickets_buffer) >= 10:
            # Envoyer chaque ticket du buffer au topic Kafka
            for td in tickets_buffer:
                producer.send('caisse', td)

            # Message indiquant l'envoi du lot de 10
            print(f"{len(tickets_buffer)} tickets envoyés : {tickets_buffer}")

            # Vider le buffer
            tickets_buffer.clear()

        # Pause de 2 secondes avant de générer le ticket suivant
        time.sleep(2)

# Lancer l'envoi continu par lot de 10 tickets si le script est exécuté directement
if __name__ == '__main__':
    send_ticket_to_kafka()
