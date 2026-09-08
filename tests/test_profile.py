import pytest


async def test_create_profile_success(authed_client):
    res = await authed_client.post("/api/v1/me", json={"bio": "I am a test user 1"})
    assert res.status_code == 201
    assert res.json()["bio"] == "I am a test user 1"


async def test_create_profile_duplicate(authed_client):
    await authed_client.post("/api/v1/me", json={"bio": "First bio"})
    res = await authed_client.post("/api/v1/me", json={"bio": "Second bio"})
    assert res.status_code == 409
    assert res.json()["detail"] == "Profile already created."


async def test_get_my_profile_success(authed_client):
    await authed_client.post("/api/v1/me", json={"bio": "Hello there"})
    res = await authed_client.get("/api/v1/me")
    assert res.status_code == 200
    assert res.json()["bio"] == "Hello there"


async def test_get_my_profile_not_found(authed_client):
    # no profile created for this user 
    res = await authed_client.get("/api/v1/me")
    assert res.status_code == 404
    assert res.json()["detail"] == "Profile not found"


async def test_get_profile_by_username(authed_client, test_user):
    await authed_client.post("/api/v1/me", json={"bio": "Public bio"})
    res = await authed_client.get(f"/api/v1/{test_user.username}")
    assert res.status_code == 200
    assert res.json()["bio"] == "Public bio"


async def test_get_profile_by_username_not_found(authed_client):
    res = await authed_client.get("/api/v1/nonexistentuser")
    assert res.status_code == 404
    assert res.json()["detail"] == "Profile not found."


async def test_update_profile_success(authed_client):
    await authed_client.post("/api/v1/me", json={"bio": "Old bio"})
    res = await authed_client.patch("/api/v1/me", json={"bio": "New bio"})
    assert res.status_code == 200
    assert res.json()["bio"] == "New bio"


async def test_update_profile_not_found(authed_client):
    res = await authed_client.patch("/api/v1/me", json={"bio": "New bio"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Profile not found."