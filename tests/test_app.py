import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Verify health endpoint responds with 200 OK and expected JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "devsecops-demo-pipeline"


def test_index_dashboard(client):
    """Verify landing page loads properly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"DevSecOps CI/CD Security Pipeline" in response.data


def test_vulnerable_sql_endpoint(client):
    """Verify vulnerable SQL endpoint responds with dummy records."""
    response = client.get("/api/vulnerable/users?role=developer")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert any(user["username"] == "alice" for user in data["data"])


def test_secure_sql_endpoint(client):
    """Verify secure parameterized SQL endpoint works as intended."""
    response = client.get("/api/secure/users?role=devsecops")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "secure_parameterized_query"
    assert any(user["username"] == "bob" for user in data["data"])


def test_vulnerable_greet(client):
    """Verify vulnerable greet endpoint reflects input."""
    response = client.get("/vulnerable/greet?name=SecurityStudent")
    assert response.status_code == 200
    assert b"Hello, SecurityStudent!" in response.data


def test_secure_greet(client):
    """Verify secure greet endpoint renders and escapes safely."""
    response = client.get("/secure/greet?name=Alice")
    assert response.status_code == 200
    assert b"Hello, Alice!" in response.data
