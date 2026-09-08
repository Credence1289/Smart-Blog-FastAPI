import pytest


async def test_vote_create(authed_client):
    post_resp = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", "title": "Test title", "post": "Test post",
    })
    post_id = post_resp.json()["post_id"]

    res = await authed_client.post(f"/api/v1/posts/{post_id}/vote", json={"vote": 1})
    assert res.status_code == 200
    assert res.json()["Message"] == f"Vote created for {post_id}"


async def test_vote_toggle_removes_same_vote(authed_client):
    post_resp = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", "title": "Test title", "post": "Test post",
    })
    post_id = post_resp.json()["post_id"]

    # first upvote creates it
    await authed_client.post(f"/api/v1/posts/{post_id}/vote", json={"vote": 1})
    # same vote again should remove it
    res = await authed_client.post(f"/api/v1/posts/{post_id}/vote", json={"vote": 1})
    assert res.status_code == 200
    assert res.json()["Message"] == f"Vote removed for {post_id}"


async def test_vote_change_updates_existing(authed_client):
    post_resp = await authed_client.post("/api/v1/posts", json={
        "content_type": "Test Content", "title": "Test title", "post": "Test post",
    })
    post_id = post_resp.json()["post_id"]

    # upvote first
    await authed_client.post(f"/api/v1/posts/{post_id}/vote", json={"vote": 1})

    res = await authed_client.post(f"/api/v1/posts/{post_id}/vote", json={"vote": -1})
    assert res.status_code == 200
    assert res.json()["Message"] == f"Vote updated for {post_id}"


async def test_vote_post_not_found(authed_client):
    res = await authed_client.post("/api/v1/posts/99999/vote", json={"vote": 1})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"