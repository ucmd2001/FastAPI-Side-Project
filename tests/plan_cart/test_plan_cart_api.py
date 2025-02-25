import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_calculate_cart_total_valid_input():
    payload = {"data": "2015.11.11|0.7|電子\n\n1*ipad:2399.00\n1*顯示器:1799.00\n12*啤酒:25.00\n5*麵包:9.00\n\n2015.11.11\n\n2016.3.2 1000 200"}

    response = client.post("/Web_Project/Plan_cart", json=payload)
    assert response.status_code == 200
    assert response.json()["total_price"] == 3083.60


def test_api_calculate_cart_total_invalid_format():
    payload = { "data": "Invalid format"}

    response = client.post("/Web_Project/Plan_cart", json=payload)
    assert response.status_code == 400
    assert "Invalid input format" in response.json()["detail"]
