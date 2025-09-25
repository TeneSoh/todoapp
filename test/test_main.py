from fastapi.testclient import TestClient
from fastapi import status
from main import app

client = TestClient(app)
def test_check_api_is_working():
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Api is working'}