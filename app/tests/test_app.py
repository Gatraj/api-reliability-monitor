import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_metrics_returns_text_plain(client):
    response = client.get("/metrics")
    assert response.content_type == "text/plain; charset=utf-8"

def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
