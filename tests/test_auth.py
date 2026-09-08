from app.models.models import User
import pytest

async def test_register_user(client):
    response = await client.post("/api/v1/register", json = {
        "name": "Test User 2",
        "email": "testuser2@gmail.com",
        "username": "testuser2",
        "password": "Testuser@123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser2@gmail.com"


async def test_dup_register_user(client, test_user):
    response = await client.post("/api/v1/register", json = {
        "name" : "Test User 2",
        "email" : test_user.email,
        "username" : "testuser3",
        "password" : "Testuser@123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "User is already registered"

async def test_login_success(client, test_user):
    response = await client.post("/api/v1/login", data={
        "username": test_user.username,
        "password": "correctpassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"

    
#/login uses OAuth2PasswordRequestForm, not JSON — 
# that's why the test uses client.post(..., data={...}) (form-encoded), not json={...}.
async def test_wrong_login(client, test_user):
    response = await client.post("/api/v1/login", data={
        "username" : test_user.username,
        "password" : "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Credentials"
