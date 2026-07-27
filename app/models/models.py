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

    post:Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    vote:Mapped[list["Vote"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comment:Mapped[list["Comment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    profile:Mapped["Profile"] = relationship(back_populates="user", cascade="all, delete-orphan")
    profile_pic:Mapped["ProfilePic"] = relationship(back_populates="user", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    user_id :Mapped[int]= mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(200))
    post: Mapped[str] = mapped_column(String(50000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user:Mapped["User"] = relationship(back_populates="post")
    vote:Mapped[list["Vote"]]= relationship(back_populates="post", cascade="all, delete-orphan")
    comment:Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")

    @property
    def username(self):
        return self.user.username
        
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

    user:Mapped["User"] = relationship(back_populates="vote")
    post:Mapped["Post"] = relationship(back_populates="vote")


class Comment(Base):
    __tablename__ = "comments"

    comments_id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4,index=True, unique=True)
    post_id:Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    comment:Mapped[str] = mapped_column(String(500), nullable = False)
    created_at:Mapped[datetime] = mapped_column(DateTime, server_default=func.now() )

    user:Mapped["User"] = relationship(back_populates="comment")
    post:Mapped["Post"] = relationship(back_populates="comment")

    @property
    def username(self):
        return self.user.username

class Profile(Base):
    __tablename__ = "profile"

    profile_id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4,index=True, unique=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), unique=True,nullable=False)
    bio:Mapped[str|None] = mapped_column(String(200), nullable=True)

    user:Mapped["User"] = relationship(back_populates="profile")
    profile_pic:Mapped["ProfilePic"] = relationship(back_populates="profile",cascade="all, delete-orphan")

    @property
    def username(self):
        return self.user.username

    @property
    def name(self):
        return self.user.name

    @property
    def email(self):
        return self.user.email


class ProfilePic(Base):
    __tablename__ = "profile_pic"

    pic_id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4,index=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), unique=True,nullable=False)
    profile_id:Mapped[UUID] = mapped_column(ForeignKey("profile.profile_id", ondelete="CASCADE"), unique=True,nullable=False)
    original_name:Mapped[str] = mapped_column(String(200), nullable=False)
    saved_as: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    folder:Mapped[str] = mapped_column(String(200), nullable=False)
    size:Mapped[int] = mapped_column(default=0, nullable=False)
    uploaded_at:Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())

    user:Mapped["User"] = relationship(back_populates="profile_pic")
    profile:Mapped["Profile"] = relationship(back_populates="profile_pic")
