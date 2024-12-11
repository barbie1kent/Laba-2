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
        json={"username": "usertest", "email": "usertest@gmail.com", "full_name": "User Test", "password": "password1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "usertest"
    assert data["email"] == "usertest@gmail.com"

def test_register_duplicate_username():
    response = client.post(
        "/register/",
        json={"username": "duplicateuser", "email": "first@gmail.com", "full_name": "First User", "password": "password1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "usertest"
    assert data["email"] == "usertest@gmail.com"

    response = client.post(
        "/register/",
        json={"username": "duplicateuser", "email": "second@gmail.com", "full_name": "Second User", "password": "password1"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or Email already registered!"


def test_login_success():
    client.post(
        "/register/",
        json={"username": "usertest", "email": "usertest@gmial.com", "full_name": "User Test",
              "password": "password1"}
    )

    response = client.post(
        "/token",
        data={"username": "usertest", "password": "password1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "password1"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

    response = client.post(
        "/token",
        data={"username": "usertest", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_with_expired_token():
    response = client.post(
        "/register/",
        json={"username": "usertest", "email": "usertest@gmail.com", "full_name": "User Test", "password": "password1"}
    )
    response = client.post(
        "/token",
        data={"username": "usertest", "password": "password1"}
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

    assert data[0]["username"] == "Danya"
    assert data[0]["email"] == "danya@gmail.ru"


def test_get_current_user():
    response = client.post(
        "/register/",
        json={"username": "usertest", "email": "usertest@gmail.com", "full_name": "User Test",
              "password": "password1"}
    )
    assert response.status_code == 200

    response = client.post(
        "/token",
        data={"username": "usertest", "password": "password1"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "usertest"
    assert data["email"] == "usertest@gmial.com"
    assert data["full_name"] == "User User"
