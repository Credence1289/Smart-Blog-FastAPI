from app.models.models import User, Post, Vote, Comment, Profile, ProfilePic

def post_key(post_id: int) -> str:
    return f"post:{post_id}"

def user_posts_key(
    user_id: int,
    page: int,
    size: int
) -> str:
    return f"posts:user:{user_id}:page:{page}:size:{size}"

def comments_key(
    post_id: int,
    page: int,
    size: int) -> str:
    return f"comments:post:{post_id}:page:{page}:size:{size}"


def comment_key(comment_id: int) -> str:
    return f"comment:{comment_id}"


def likes_key(post_id: int) -> str:
    return f"likes:post:{post_id}"


def profile_key(user_id: int) -> str:
    return f"profile:{user_id}"

