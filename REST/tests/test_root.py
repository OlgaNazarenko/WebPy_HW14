import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient

import main

client = TestClient(main.app, base_url="http://127.0.0.1")


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "REST APP v1.2"}