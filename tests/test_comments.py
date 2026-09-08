import pytest
from app.models.models import User, Post, Comment

async def test_create_comment(authed_client, test_user):
    response = await authed_client.post("/api/v1/posts", json = {
        "content_type" : "Test Content",
        "title" : "Test title",
        "post" : "Test post",
    })
    assert response.status_code == 200
    post_id = response.json()["post_id"]

    comment = await authed_client.post(f"/api/v1/posts/{post_id}/comments", json={
        "comment" : "Test comment 1"
    })
    assert comment.status_code == 200
    assert comment.json()["user_id"] == test_user.user_id

async def test_create_comment_US(authed_client):
    response = await authed_client.post("/api/v1/posts/55/comments", json={
        "comment" : "Test comment 1"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Post does not exist"


async def test_get_comments_success(authed_client):
    post_resp = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", 
        "title": "Test title", 
        "post": "Test post",
    })
    post_id = post_resp.json()["post_id"]

    for i in range(5):
        await authed_client.post(f"/api/v1/posts/{post_id}/comments", json={
            "comment": f"Test Comment"
        })

    res = await authed_client.get(f"/api/v1/posts/{post_id}/comments")
    assert res.status_code == 200

    data = res.json()
    assert "comments" in data
    assert isinstance(data["comments"], list)
    assert len(data["comments"]) >= 1  


async def test_get_comments_post_not_found(authed_client):
    res = await authed_client.get("/api/v1/posts/99999/comments")
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"


async def test_update_comment_success(authed_client, test_user):
    post_response = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", "title": "Test title", "post": "Test post",
    })
    post_id = post_response.json()["post_id"]
 
    comment_response = await authed_client.post(f"/api/v1/posts/{post_id}/comments", json={
        "comment": "Original comment"
    })
    comments_id = comment_response.json()["comments_id"]   # UUID string
 
    res = await authed_client.patch(f"/api/v1/comments/{comments_id}", json={
        "comment": "Edited comment"
    })
    assert res.status_code == 200
    assert res.json()["comment"] == "Edited comment"
 
 
async def test_update_comment_not_found(authed_client):
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    res = await authed_client.patch(f"/api/v1/comments/{fake_uuid}", json={
        "comment": "Edited comment"
    })
    assert res.status_code == 404
    assert res.json()["detail"] == "Comment not found"
 
 
async def test_update_comment_unauthorized(authed_client, client, other_user):
    post_resp = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", "title": "Test title", "post": "Test post",
    })
    post_id = post_resp.json()["post_id"]
 
    comment_resp = await authed_client.post(f"/api/v1/posts/{post_id}/comments", json={
        "comment": "Original comment"
    })
    comments_id = comment_resp.json()["comments_id"]
 
    from app.main import app
    from app.core.gate import current_user
 
    async def fake_other_user():
        return {"user": other_user, "role": "user", "payload": {}}
 
    app.dependency_overrides[current_user] = fake_other_user
 
    res = await client.patch(f"/api/v1/comments/{comments_id}", json={
        "comment": "Hacked comment"
    })
    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to update comment"
 
 
async def test_delete_comment_success(authed_client, test_user):
    post_resp = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", "title": "Test title", "post": "Test post",
    })
    post_id = post_resp.json()["post_id"]
 
    comment_resp = await authed_client.post(f"/api/v1/posts/{post_id}/comments", json={
        "comment": "To be deleted"
    })
    comments_id = comment_resp.json()["comments_id"]
 
    res = await authed_client.delete(f"/api/v1/comments/{comments_id}")
    assert res.status_code == 200
    assert res.json()["message"] == "Comment deleted successfully"
 
 
async def test_delete_comment_not_found(authed_client):
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    res = await authed_client.delete(f"/api/v1/comments/{fake_uuid}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Comment not found"
 
 
async def test_delete_comment_unauthorized(authed_client, client, other_user):
    post_resp = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", "title": "Test title", "post": "Test post",
    })
    post_id = post_resp.json()["post_id"]
 
    comment_resp = await authed_client.post(f"/api/v1/posts/{post_id}/comments", json={
        "comment": "Original comment"
    })
    comments_id = comment_resp.json()["comments_id"]
 
    from app.main import app
    from app.core.gate import current_user
 
    async def fake_other_user():
        return {"user": other_user, "role": "user", "payload": {}}
 
    app.dependency_overrides[current_user] = fake_other_user
 
    res = await client.delete(f"/api/v1/comments/{comments_id}")
    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized"
 