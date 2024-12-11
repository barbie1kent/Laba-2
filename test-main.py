from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["username"] == "string"

def test_create_user():
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

def test_register_duplicate_username():
    response = client.post(
        "/register/",
        json={"username": "duplicateuser", "email": "first@example.com", "full_name": "First User", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

    response = client.post(
        "/register/",
        json={"username": "duplicateuser", "email": "second@example.com", "full_name": "Second User", "password": "password123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or Email already registered!"


def test_login_success():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User",
              "password": "password123"}
    )

    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "password123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_with_expired_token():
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]

    expired_token = token[:-1] + "1"

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_login_with_invalid_token():
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_get_all_users():
    response = client.get("/users/")

    assert response.status_code == 200


def test_get_users_correct_data():
    response = client.get("/users/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0

    assert "username" in data[0]
    assert "email" in data[0]

    assert data[0]["username"] == "Fabon"
    assert data[0]["email"] == "fabon@mail.ru"


def test_get_current_user():
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User",
              "password": "password123"}
    )
    assert response.status_code == 200

    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"