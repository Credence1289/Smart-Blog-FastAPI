from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, func
from datetime import datetime
from uuid import UUID, uuid4

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    posts:Mapped[list["Post"]] = relationship(back_populates="users", cascade="all, delete-orphan")
    votes:Mapped[list["Vote"]] = relationship(back_populates="users", cascade="all, delete-orphan")
    comments:Mapped[list["Comment"]] = relationship(back_populates="users", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200))
    post: Mapped[str] = mapped_column(String(50000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    users:Mapped["User"] = relationship(back_populates="posts")
    votes:Mapped["Vote"]= relationship(back_populates="posts", cascade="all, delete-orphan")
    comments:Mapped["Comment"] = relationship(back_populates="posts", cascade="all, delete-orphan")

class Vote(Base):
    __tablename__ = "votes"

    upvote_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    vote: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 or -1

    users:Mapped["User"] = relationship(back_populates="votes")
    posts:Mapped["Post"] = relationship(back_populates="votes")


class Comment(Base):
    __tablename__ = "comments"

    comments_id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    post_id:Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    comment:Mapped[str] = mapped_column(String(256), nullable = False)
    created_at:Mapped[datetime] = mapped_column(DateTime, server_default=func.now() )

    users:Mapped["User"] = relationship(back_populates="comments")
    posts:Mapped["Post"] = relationship(back_populates="comments")