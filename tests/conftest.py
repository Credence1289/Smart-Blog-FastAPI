import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.core.hashing import hash_password, verify_password
from app.main import app
from app.rate_limit.limiter import limiter
from app.models.models import User
from app.core.gate import current_user
from app.db.session import get_db
from app.models.models import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:Qwert%40123@localhost:5432/smartblog_test"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db(test_engine):
    #create all tables at once strat of the session
    async with test_engine.begin() as conn:
        #creates tables 
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        #drop all tables
        await conn.run_sync(Base.metadata.drop_all)
    # await test_engine.dispose()


#this fixture creates a fresh database session for each test 
# and then rolls back everything that test did.
@pytest_asyncio.fixture
async def db_session(test_engine):
    #gets a database connection from your test database's connection pool.
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)

        yield session

        await session.close()
        await trans.rollback()

#Every test opens a transaction, does whatever inserts/updates it wants, 
#and at the end we roll it back instead of committing. Next test starts clean, without needing to truncate tables manually.


## --- Step 1: test_user fixture ---
@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(
        name="Test User",
        username="testuser",
        email="test@example.com",
        hashed_password= hash_password("testuser1pass"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user



#-----mock_redis, rate_limit, client

@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.get.return_value = None
    return mock

@pytest.fixture(autouse=True)
def disable_rate_limit():
    limiter.enabled = False
    yield
    limiter.enabled = True

@pytest_asyncio.fixture
#Injects the test DB session, fake Redis instance, and 
# Pytest's tool for temporary code modifications.
async def client(db_session, mock_redis, monkeypatch):
    #"Whenever any API route asks for get_db, do not open a real database connection. 
    # Run _get_test_db() instead, which gives them our isolated test db_session."
    async def _get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_test_db
    monkeypatch.setattr("app.api.v1.routers.posts.redis_client", mock_redis)
    monkeypatch.setattr("app.api.v1.routers.votes.redis_client", mock_redis)
    monkeypatch.setattr("app.api.v1.routers.profile.redis_client", mock_redis)
    monkeypatch.setattr("app.api.v1.routers.comments.redis_client", mock_redis)
    
        # welcome email — fires from register endpoint (auth.py)
    monkeypatch.setattr(
        "app.api.v1.routers.auth.send_welcome_email",
        lambda *args, **kwargs: None
    )

    # password reset email — fires from forgot-password endpoint (auth.py)
    monkeypatch.setattr(
        "app.api.v1.routers.auth.send_password_reset_email",
        MagicMock()   # supports .delay(...) since it's a Mock, unlike a plain lambda
    )

    # first-post congrats email — fires from create_post endpoint (posts.py)
    monkeypatch.setattr(
        "app.api.v1.routers.posts.send_first_post_congrats_email",
        lambda *args, **kwargs: None
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authed_client(client, test_user, monkeypatch):
    async def fake_current_user():
        return {"user": test_user, "role": "user", "payload": {}}

    app.dependency_overrides[current_user] = fake_current_user
    yield client



@pytest_asyncio.fixture
async def other_user(db_session):
    user = User(
        name="Other User",
        username="otheruser",
        email="other@example.com",
        hashed_password="irrelevant",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user