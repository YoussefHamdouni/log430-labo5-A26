"""
Locustfile for load testing store_manager.py
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import random
import uuid
from locust import HttpUser, task, between

class FlaskAPIUser(HttpUser):
    # Wait time between requests (1-3 seconds)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called every time a Locust user spawns"""
        print("Welcome, user!")

    @task(1)
    def test_rate_limit(self):
        """Test pour vérifier le rate limiting"""
        payload = {
            "user_id": random.randint(1, 3),
            "items": [{"product_id": random.randint(1, 4), "quantity": random.randint(1, 10)}]
        }

        response = self.client.post(
            "/store-manager-api/orders",
            json=payload
        )

        if response.status_code == 503:  # HTTP 503 Service Unavailable
            print("Rate limit atteint!")


class UserLifecycleUser(HttpUser):
    """Labo 7, activité 8 : création et suppression d'utilisateurs (à lancer avec --host=http://store_manager:5000)"""
    # Temps d'attente entre les requêtes (1 à 2 secondes), comme au labo 4
    wait_time = between(1, 2)

    def on_start(self):
        """Chaque utilisateur Locust ne supprime que les utilisateurs qu'il a créés"""
        self.created_user_ids = []

    @task(2)
    def create_user(self):
        """Test POST /users (publie UserCreated dans Kafka)"""
        # Courriel unique : la colonne email de la table users est UNIQUE
        payload = {"name": "Locust User", "email": f"locust-{uuid.uuid4().hex}@test.ca"}

        with self.client.post("/users", json=payload, catch_response=True) as response:
            if response.status_code == 201:
                self.created_user_ids.append(response.json()["user_id"])
                response.success()
            else:
                response.failure(f"Erreur : {response.status_code} - {response.text[:100]}")

    @task(1)
    def delete_user(self):
        """Test DELETE /users/<id> sur un utilisateur créé par ce même utilisateur Locust"""
        if not self.created_user_ids:
            return
        user_id = self.created_user_ids.pop(0)

        with self.client.delete(f"/users/{user_id}", name="/users/[id]", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Erreur : {response.status_code} - {response.text[:100]}")