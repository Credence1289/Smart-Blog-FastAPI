from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, func
from datetime import datetime
from uuid import UUID, uuid4

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    content_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(20))
    post: Mapped[str] = mapped_column(String(5000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="posts")
    votes = relationship("Vote", back_populates="post")

class Vote(Base):
    __tablename__ = "votes"

    upvote_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))

    vote: Mapped[int] = mapped_column(Integer, unique=False)  # 1 or -1

    user = relationship("User", back_populates="votes")
    post = relationship("Post", back_populates="votes")