from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_health(): assert client.get('/health').json()['status'] == 'ok'
def test_overview(): assert client.get('/api/overview').status_code == 200
