from app.models.models import User

async def test_session_work(db_session):
    user = User(
        name="Test User1",
        username="testuser1",
        email="testuser1@gmail.com",
        hashed_password="TestUser@123",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.user_id is not None
    assert user.username == "testuser1"