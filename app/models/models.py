from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, func,CheckConstraint,UniqueConstraint
from datetime import datetime
from uuid import UUID, uuid4

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    posts:Mapped[list["Post"]] = relationship(back_populates="users", cascade="all, delete-orphan")
    votes:Mapped[list["Vote"]] = relationship(back_populates="users", cascade="all, delete-orphan")
    comments:Mapped[list["Comment"]] = relationship(back_populates="users", cascade="all, delete-orphan")
    profile:Mapped["Profile"] = relationship(back_populates="users", cascade="all, delete-orphan",uselist=True)

class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    user_id :Mapped[int]= mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(200))
    post: Mapped[str] = mapped_column(String(50000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    users:Mapped["User"] = relationship(back_populates="posts")
    votes:Mapped[list["Vote"]]= relationship(back_populates="posts", cascade="all, delete-orphan")
    comments:Mapped[list["Comment"]] = relationship(back_populates="posts", cascade="all, delete-orphan")

    @property
    def username(self):
        return self.users.username
        
class Vote(Base):
    __tablename__ = "votes"

    _table_args__ = (
        UniqueConstraint( #prevents a user from voting multiple times on the same post.  
            "user_id",
            "post_id",
            name="uq_votes_user_post",
        ),
        CheckConstraint(  #ensures only valid vote values are stored.
            "vote IN (-1, 1)",
            name="ck_votes_value",
        ),
    )

    vote_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4,index=True, unique=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    vote: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 or -1

    users:Mapped["User"] = relationship(back_populates="votes")
    posts:Mapped["Post"] = relationship(back_populates="votes")


class Comment(Base):
    __tablename__ = "comments"

    comments_id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4,index=True, unique=True)
    post_id:Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    comment:Mapped[str] = mapped_column(String(500), nullable = False)
    created_at:Mapped[datetime] = mapped_column(DateTime, server_default=func.now() )

    users:Mapped["User"] = relationship(back_populates="comments")
    posts:Mapped["Post"] = relationship(back_populates="comments")

    @property
    def username(self):
        return self.users.username

class Profile(Base):
    __tablename__ = "profile"

    profile_id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4,index=True, unique=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), unique=True,nullable=False)
    bio:Mapped[str|None] = mapped_column(String(200), nullable=True)

    users:Mapped["User"] = relationship(back_populates="profile")

    @property
    def username(self):
        return self.users.username
