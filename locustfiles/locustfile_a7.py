"""
Locustfile for load testing order creation (activité 7)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import random
from locust import HttpUser, task, between

class OrderCreationUser(HttpUser):
    # Wait time between requests (1-2 seconds)
    wait_time = between(1, 2)

    @task(1)
    def create_order(self):
        """Test POST /orders : création de commande (Store Manager -> KrakenD -> paiement)"""
        payload = {
            "user_id": random.randint(1, 3),
            "items": [{"product_id": random.randint(1, 4), "quantity": random.randint(1, 10)}]
        }

        with self.client.post("/orders", json=payload, catch_response=True) as response:
            if response.status_code == 201 and "order_id" in response.json():
                response.success()
            else:
                response.failure(f"Erreur : {response.status_code} - {response.text[:100]}")
