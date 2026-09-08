from app.models.models import User, Post
from app.main import app
from app.core.gate import current_user
import pytest


async def test_post_create(authed_client, test_user):
    response = await authed_client.post("/api/v1/posts", json = {
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test title"
    assert data["username"] == test_user.username
    
async def test_post_get_success(authed_client):
    create_response = await authed_client.post("/api/v1/posts", json={
        "content_type" : "Test Content1",
        "title" : "Test title1",
        "post" : "Test post1",        
    })
    assert create_response.status_code == 200
    created_post = create_response.json()
    post_id = created_post["post_id"]

    get_response = await authed_client.get(f"/api/v1/posts/{post_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["title"] == "Test title1"
    assert data["post_id"] == post_id   


async def test_get_post_not_found(client):
    response = await client.get("/api/v1/posts/45")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

async def test_post_get_all_post(authed_client):
    for i in range(10):
        response = await authed_client.post("/api/v1/posts", json = {
            "content_type" : "Test Content",
            "title" : "Test title",
            "post" : "Test post",
        })
    assert response.status_code == 200

    get_response = await authed_client.get("/api/v1/posts")
    assert get_response.status_code == 200

    data = get_response.json()
    assert "posts" in data                # it's an object with a "posts" key
    assert isinstance(data["posts"], list)
    assert data["has_more"] is True  

async def test_post_get_my_posts(authed_client, test_user):
    for i in range(5):
        response = await authed_client.post("api/v1/posts", json = {
            "content_type" : "Test Content",
            "title" : "Test title",
            "post" : "Test post",
        })
    assert response.status_code == 200

    my_posts = await authed_client.get("api/v1/posts/me")
    assert my_posts.status_code == 200

    data = my_posts.json()
    assert "posts" in data                # it's an object with a "posts" key
    assert isinstance(data["posts"], list)
    assert data["has_more"] is True  
    assert data["posts"][0]["username"] == test_user.username 

async def test_post_delete_A(authed_client, test_user):
    response = await authed_client.post("/api/v1/posts", json={
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",        
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username

    post_id = data["post_id"]
    res = await authed_client.delete(f"/api/v1/posts/{post_id}")
    assert res.status_code == 200

async def test_post_delete_UA(authed_client, client, other_user):
    response = await authed_client.post("/api/v1/posts", json={
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",       
    })
    assert response.status_code == 200
    post_id = response.json()["post_id"]

    async def fake_other_user():
        return {"user": other_user, "role": "user", "payload": {}}

    app.dependency_overrides[current_user] = fake_other_user

    res = await client.delete(f"/api/v1/posts/{post_id}")
    assert res.json()["detail"] == "Not authorized to delete this post"

async def test_post_delete(authed_client):
    response = await authed_client.post("/api/v1/posts", json={
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",       
    })
    assert response.status_code == 200

    res = await authed_client.delete("/api/v1/posts/5465")
    assert res.json()["detail"] == "Post not found"

async def test_delete_all_post(authed_client):
    for i in range(5):
        response = await authed_client.post("/api/v1/posts", json={
            "content_type" : "Test Content",
            "title" : "Test title",
            "post" : "Test post",                  
        })
    assert response.status_code == 200

    res = await authed_client.delete("/api/v1/posts")
    assert res.status_code == 200


async def test_post_update_A(authed_client):
    response = await authed_client.post("/api/v1/posts", json={
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",        
    })
    assert response.status_code == 200

    post_id = response.json()["post_id"]

    res = await authed_client.patch(f"/api/v1/posts/{post_id}", json={
        "title": "Updated title"
    })
    assert res.status_code == 200


async def test_post_update(authed_client, client):
    response = await authed_client.post("/api/v1/posts", json={
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",        
    })
    assert response.status_code == 200

    res = await authed_client.patch("/api/v1/posts/545", json={"title": "Updated title"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"


async def test_post_update_UA(authed_client, client, other_user):
    response = await authed_client.post("/api/v1/posts", json={
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",        
    })
    post_id = response.json()["post_id"]
    assert response.status_code == 200

    async def fake_other_user():
        return {"user": other_user, "role": "user", "payload": {}}

    app.dependency_overrides[current_user] = fake_other_user   

    res = await client.patch(f"/api/v1/posts/{post_id}", json={"title": "Hacked title"})
    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to edit this post"  
