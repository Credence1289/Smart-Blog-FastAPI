# Smart Blog API
<img width="741" height="636" alt="image" src="https://github.com/user-attachments/assets/6d78daaf-4a7a-433d-8450-461a4ba9f5b3" />


**[View on GitHub](https://github.com/Credence1289/Smart-Blog-FastAPI)** | **[Live API Docs]([#api-documentation)](https://smart-blog-fastapi.onrender.com)**

---

## 📋 Overview

SmartBlog API is a fully-featured blogging platform backend that showcases:

- **Secure Authentication**: JWT-based access/refresh token system with strong password validation
- **Social Features**: Comments and upvote/downvote system for community engagement
- **Database Management**: SQLAlchemy ORM with Alembic for version-controlled migrations
- **RESTful API Design**: API versioning, proper HTTP methods, comprehensive validation
- **Modular Architecture**: Separation of concerns across routers, schemas, models, and services
- **DevOps**: Docker and Docker Compose for consistent development and deployment
- **Observability**: Health check endpoint and structured logging throughout
---

## ✨ Features

### Authentication & User Management
- **User Registration** with email validation and strong password requirements
  - Minimum 8 characters
  - At least one uppercase letter, one lowercase letter, one digit
  - Secure password hashing using bcrypt
- **Login System** with JWT access and refresh tokens
- **Token Refresh Mechanism** for seamless session renewal without re-login
- **Access Control** ensuring users can only modify their own posts and comments

### Blog Post Management
- **Create Posts** with customizable content types (article, tutorial, opinion, etc.)
- **Read Operations**
  - Retrieve all posts with optional content-type filtering
  - View specific post by ID
  - Access only current user's posts
- **Update Posts** with partial updates (PATCH)
- **Delete Operations**
  - Delete individual posts
  - Delete all user's posts at once
- **Ownership Verification** preventing unauthorized modifications

### Social Engagement System
- **Comments**
  - Add comments to any post
  - View all comments on a post with user and timestamp information
  - Update own comments
  - Delete own comments
  - Automatic ownership validation
  
- **Voting System**
  - Upvote posts (vote: 1)
  - Downvote posts (vote: -1)
  - Toggle votes (voting same way again removes the vote)
  - View real-time vote counts per post
  - One vote per user per post

### API Design
- **RESTful Architecture** with proper HTTP methods (GET, POST, PATCH, DELETE)
- **API Versioning** (`/api/v1`) for future compatibility
- **Comprehensive Input Validation** using Pydantic with detailed error messages
- **Auto-generated OpenAPI/Swagger Documentation**
- **Proper Status Codes** (201 Created, 404 Not Found, 403 Forbidden, etc.)

### Database & Migrations
- **SQLAlchemy ORM** for database abstraction and type safety
- **Alembic Integration** for version-controlled schema management
- **Relational Schema** with proper foreign keys and cascade delete rules
- **PostgreSQL Support** for production environments
- **SQLite Support** for local development

### DevOps & Infrastructure
- **Docker Containerization** for consistent local and production environments
- **Docker Compose** for multi-service orchestration (API + PostgreSQL + PgAdmin)
- **Environment Management** using `.env` files and Pydantic Settings
- **Health Check Endpoint** for service monitoring and load balancer integration
- **Structured Logging** for debugging and production monitoring
- **Ready for Cloud Deployment** (Render, Railway, AWS, DigitalOcean, etc.)

---

## 🛠️ Tech Stack

| Technology     | Purpose                              | Version  |
|----------------|--------------------------------------|----------|
| **FastAPI**    | Web framework & API routing          | 0.104+   |
| **Uvicorn**    | ASGI server                          | 0.24+    |
| **SQLAlchemy** | Object-relational mapper (ORM)       | 2.0+     |
| **Alembic**    | Database schema versioning           | 1.12+    |
| **PostgreSQL** | Production relational database       | 14+      |
| **PyJWT**      | JWT token creation & validation      | 2.8+     |
| **Pydantic**   | Data validation & settings           | 2.0+     |
| **Bcrypt**     | Password hashing & verification      | 4.0+     |
| **Email-validator** | Email validation                 | 2.0+     |
| **Python**     | Programming language                 | 3.10+    |
| **Docker**     | Containerization                     | Latest   |

---

## 🏗️ Architecture & Design

### Layered Architecture

```
┌─────────────────────────────────────────┐
│      FastAPI Application (main.py)      │
├─────────────────────────────────────────┤
│  API Routers (v1) - Endpoint Handlers   │
│  ├─ /auth - User authentication         │
│  ├─ /posts - Blog post CRUD ops         │
│  ├─ /comments - Comment management      │
│  ├─ /votes - Upvote/downvote system     │
│  └─ /health - Health checks             │
├─────────────────────────────────────────┤
│  Core Services - Business Logic         │
│  ├─ config.py - Configuration mgmt      │
│  ├─ gate.py - Authorization & auth      │
│  ├─ hashing.py - Password operations    │
│  └─ token.py - JWT token management
|  └─ logger.py - logging      │
├─────────────────────────────────────────┤
│  Data Layer - Schemas & Models          │
│  ├─ Pydantic Schemas (validation)       │
│  ├─ SQLAlchemy Models (ORM)             │
│  └─ Database Session Management         │
├─────────────────────────────────────────┤
│  Database (PostgreSQL / SQLite)         │
│  ├─ users table                         │
│  ├─ posts table                         │
│  ├─ comments table                      │
│  └─ votes table                         │
└─────────────────────────────────────────┘
```

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                          User                               │
├─────────────────────────────────────────────────────────────┤
│ user_id (PK) │ name │ username │ email │ hashed_password   │
└─────────────────────────────────────────────────────────────┘
        ↓ 1:N      ↓ 1:N      ↓ 1:N
        │           │          │
    [posts]     [votes]    [comments]
        │           │          │
        ↓           ↓          ↓
┌──────────────┐ ┌────────┐ ┌──────────────┐
│   Post       │ │ Vote   │ │  Comment     │
├──────────────┤ ├────────┤ ├──────────────┤
│ post_id (PK) │ │upvote  │ │comments_id   │
│ user_id (FK) │ │_id(PK) │ │(PK)          │
│ title        │ │post_id │ │post_id(FK)   │
│ post (content)│ │(FK)    │ │user_id(FK)   │
│ content_type │ │user_id │ │comment       │
│ created_at   │ │(FK)    │ │created_at    │
└──────────────┘ │vote(1) │ └──────────────┘
                 │or(-1)  │
                 └────────┘
```

### Key Design Decisions

- **JWT with Refresh Tokens**: Access tokens are short-lived (15 min), refresh tokens long-lived (7 days)
- **Cascade Delete**: Deleting a user removes all their posts, votes, and comments
- **Ownership Validation**: Users can only modify content they created
- **Stateless Authentication**: No sessions stored; JWT tokens are self-contained
- **Content Type Flexibility**: Posts can be categorized by type (article, tutorial, news, opinion, etc.)
- **Vote Toggle Logic**: Voting the same way again removes the vote for clean UX

---

## 📁 Project Structure

```
SmartBlog/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py                       # API router aggregation
│   │       └── routers/
│   │           ├── auth.py                  # User registration & login
│   │           ├── posts.py                 # Blog post CRUD operations
│   │           ├── comments.py              # Comment management
│   │           ├── votes.py                 # Upvote/downvote system
│   │           └── health_check.py          # Health & status checks
│   │
│   ├── core/
│   │   ├── config.py                        # Pydantic Settings for env vars
│   │   ├── gate.py                          # Authentication & authorization
│   │   ├── hashing.py                       # Password hashing utilities
│   │   └── token.py                         # JWT token operations
|   |   └─ logger.py                         #logging
│   │
│   ├── db/
│   │   ├── dbengine.py                      # Database engine setup
│   │   ├── session.py                       # Database session factory
│   │   └── create_table.py                  # Table initialization
│   │
│   ├── models/
│   │   └── models.py                        # SQLAlchemy ORM models
│   │                                         # - User, Post, Comment, Vote
│   │
│   ├── schemas/
│   │   ├── users_schema.py                  # Pydantic schemas: UserIn, UserOut
│   │   ├── posts_schema.py                  # Pydantic schemas: PostCreate, PostShow
│   │   ├── comments_schema.py               # Pydantic schemas: CommentsIn/Out
│   │   ├── upvote_schema.py                 # Pydantic schema: VoteCreate
│   │   └── refresh_token_schema.py          # Pydantic schema: RefreshTokenReq
│   │
│   └── main.py                              # FastAPI app initialization
│
├── alembic/                                 # Database migrations
│   ├── versions/                            # Migration files (auto-generated)
│   ├── env.py                               # Alembic environment config
│   └── script.py.mako                       # Migration template
│
|
├── Dockerfile                               # Dokcer file 
├── .env.example                             # Environment variables template
├── .dockerignore                            # Files excluded from Docker build
├── docker-compose.yml                       # Multi-service orchestration
├── requirements.txt                         # Python dependencies
├── README.md                                # Project documentation
└── .gitignore                               # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Docker & Docker Compose** (optional, for containerized setup)
- **Git**

### Option 1: Local Development (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Credence1289/Smart-Blog-FastAPI.git
   cd Smart-Blog-FastAPI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (optional for local dev)
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   API available at: `http://127.0.0.1:8000`

### Option 2: Docker Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Credence1289/Smart-Blog-FastAPI.git
   cd Smart-Blog-FastAPI
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```

3. **Start services**
   ```bash
   docker-compose up --build
   ```

4. **Apply database migrations** (in another terminal)
   ```bash
   docker-compose exec web alembic upgrade head
   ```

5. **Access the API**
   - API: `http://127.0.0.1:8000`
   - Swagger Docs: `http://127.0.0.1:8000/api/v1/docs`
   - ReDoc: `http://127.0.0.1:8000/api/v1/redoc`
   - PgAdmin: `http://localhost:5050`

6. **Stop services**
   ```bash
   docker-compose down
   ```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite:///./smartblog.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/smartblog

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRY=7

# Server Configuration
DEBUG=True
API_V1_PREFIX=/api/v1
HOST=127.0.0.1
PORT=8000
```

### Configuration for Docker

When using Docker, update `.env` for container networking:

```env
DATABASE_URL=postgresql://smartblog_user:smartblog_pass@db:5432/smartblog
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRY=7
DEBUG=False
```

**Important Notes:**
- `SECRET_KEY` must be a strong, random string in production
- Use PostgreSQL for production environments
- SQLite is suitable for local development only
- `ACCESS_TOKEN_EXPIRE_MINUTES` controls how long tokens are valid
- `REFRESH_TOKEN_EXPIRY` is in days

---

## 📖 API Documentation

### Interactive Swagger UI

```
http://127.0.0.1:8000/api/v1/docs
```

### ReDoc Alternative

```
http://127.0.0.1:8000/api/v1/redoc
```

All endpoints are documented with request/response schemas and examples.

---

## 🔌 Complete API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint              | Description                      | Auth Required |
|--------|----------------------|----------------------------------|---------------|
| POST   | `/api/v1/register`    | Register new user account        | ❌ No         |
| POST   | `/api/v1/login`       | Login and receive tokens         | ❌ No         |
| POST   | `/api/v1/user/refresh`| Refresh access token             | ❌ No         |

### Blog Post Endpoints

| Method | Endpoint                    | Description                    | Auth Required |
|--------|----------------------------|--------------------------------|---------------|
| POST   | `/api/v1/posts`            | Create a new blog post         | ✅ Yes        |
| GET    | `/api/v1/posts`            | Get all posts (with filtering) | ✅ Yes        |
| GET    | `/api/v1/posts/me`         | Get current user's posts       | ✅ Yes        |
| GET    | `/api/v1/posts/{post_id}`  | Get a specific post            | ✅ Yes        |
| PATCH  | `/api/v1/posts/{post_id}`  | Update a post (owner only)     | ✅ Yes        |
| DELETE | `/api/v1/posts/{post_id}`  | Delete a post (owner only)     | ✅ Yes        |
| DELETE | `/api/v1/posts`            | Delete all user's posts        | ✅ Yes        |

### Comment Endpoints

| Method | Endpoint                          | Description                    | Auth Required |
|--------|----------------------------------|--------------------------------|---------------|
| POST   | `/api/v1/posts/{post_id}/comments`    | Add comment to post           | ✅ Yes        |
| GET    | `/api/v1/posts/{post_id}/comments`    | Get all comments on post      | ❌ No         |
| PATCH  | `/api/v1/comments/{comment_id}`       | Update comment (owner only)   | ✅ Yes        |
| DELETE | `/api/v1/comments/{comment_id}`       | Delete comment (owner only)   | ✅ Yes        |

### Vote/Upvote Endpoints

| Method | Endpoint                     | Description                    | Auth Required |
|--------|------------------------------|--------------------------------|---------------|
| POST   | `/api/v1/post/{post_id}/vote`| Upvote/downvote post or toggle| ✅ Yes        |
| GET    | `/api/v1/post/{post_id}/vote`| Get vote counts for post       | ✅ Yes        |

### Health Check

| Method | Endpoint        | Description              | Auth Required |
|--------|-----------------|--------------------------|---------------|
| GET    | `/api/v1/health`| Service health status    | ❌ No         |

---

## 📡 API Examples

### 1. User Registration

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)

**Response:**
```json
{
  "Message": "User successfully created!!"
}
```

---

### 2. User Login

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "username": "johndoe",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Expiry:**
- `access_token`: Valid for 15 minutes (configurable)
- `refresh_token`: Valid for 7 days (configurable)

---

### 3. Refresh Access Token

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/user/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 4. Create a Blog Post

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/posts" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with FastAPI",
    "content_type": "tutorial",
    "post": "FastAPI is a modern web framework for building APIs with Python 3.7+..."
  }'
```

**Valid Content Types:** `article`, `tutorial`, `news`, `opinion`, `guide`, etc. (any string)

**Response:**
```json
{
  "Message": "Post successfully created!!!"
}
```

---

### 5. Get All Blog Posts

**Request:**
```bash
# Get all posts
curl -X GET "http://127.0.0.1:8000/api/v1/posts?content_type=all" \
  -H "Authorization: Bearer <access_token>"

# Get posts of specific type
curl -X GET "http://127.0.0.1:8000/api/v1/posts?content_type=tutorial" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
[
  {
    "post_id": 1,
    "username": "johndoe",
    "content_type": "tutorial",
    "title": "Getting Started with FastAPI",
    "post": "FastAPI is a modern web framework...",
    "created_at": "2024-06-01T10:30:00"
  },
  {
    "post_id": 2,
    "username": "janedoe",
    "content_type": "article",
    "title": "Best Practices in API Design",
    "post": "When designing an API, consider...",
    "created_at": "2024-06-02T14:15:00"
  }
]
```

---

### 6. Get Current User's Posts

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/posts/me" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
[
  {
    "post_id": 1,
    "username": "johndoe",
    "content_type": "tutorial",
    "title": "Getting Started with FastAPI",
    "post": "FastAPI is a modern web framework...",
    "created_at": "2024-06-01T10:30:00"
  }
]
```

---

### 7. Get Specific Post

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/posts/1" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "post_id": 1,
  "username": "johndoe",
  "content_type": "tutorial",
  "title": "Getting Started with FastAPI",
  "post": "FastAPI is a modern web framework for building APIs with Python 3.7+...",
  "created_at": "2024-06-01T10:30:00"
}
```

---

### 8. Update a Post

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/posts/1" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with FastAPI - Updated",
    "post": "Updated content here..."
  }'
```

**Notes:**
- Only the post owner can update
- You can update any combination of fields (title, post, content_type)
- Omitted fields are not modified

**Response:**
```json
{
  "Message": "Post Updated"
}
```

---

### 9. Delete a Post

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/posts/1" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "Message": "Post Deleted"
}
```

---

### 10. Add a Comment to a Post

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/posts/1/comments" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Great tutorial! This really helped me understand FastAPI better."
  }'
```

**Validation:**
- Comment must be 1-500 characters

**Response:**
```json
{
  "message": "Comment created successfully",
  "comment_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

---

### 11. Get All Comments on a Post

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/posts/1/comments"
```

**Response:**
```json
[
  {
    "user_id": 2,
    "post_id": 1,
    "comments_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "comment": "Great tutorial! This really helped me understand FastAPI better.",
    "created_at": "2024-06-02T11:45:00"
  },
  {
    "user_id": 3,
    "post_id": 1,
    "comments_id": "b2c3d4e5-f6a7-1234-5678-90abcdef1234",
    "comment": "Could you also cover async functions?",
    "created_at": "2024-06-02T15:30:00"
  }
]
```

---

### 12. Update a Comment

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/comments/a1b2c3d4-e5f6-7890-1234-567890abcdef" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Great tutorial! I really found this helpful."
  }'
```

**Response:**
```json
{
  "message": "Comment updated successfully"
}
```

---

### 13. Delete a Comment

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/comments/a1b2c3d4-e5f6-7890-1234-567890abcdef" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "message": "Comment deleted successfully"
}
```

---

### 14. Upvote/Downvote a Post

**Request - Upvote:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/post/1/vote" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "vote": 1
  }'
```

**Request - Downvote:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/post/1/vote" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "vote": -1
  }'
```

**Vote Logic:**
- `vote: 1` = Upvote
- `vote: -1` = Downvote
- Voting the same way again **removes** the vote
- Changing from upvote to downvote (or vice versa) updates the vote

**Response:**
```json
{
  "Message": "Vote created for 1"
}
```

or (if removing):

```json
{
  "Message": "Vote removed for 1"
}
```

or (if updating):

```json
{
  "Message": "Vote updated for 1"
}
```

---

### 15. Get Vote Counts for a Post

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/post/1/vote" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "upvotes": 42,
  "downvotes": 3
}
```

---

### 16. Health Check

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/health"
```

**Response (Healthy):**
```json
{
  "status": "healthy",
  "service": "SmartBlog",
  "database": "connected"
}
```

**Response (Database Down):**
```json
{
  "status": "failed",
  "database": "unavailable"
}
```

---

## 🗄️ Database Schema & Models

### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    user_id: int              # Primary key, auto-increment
    name: str                 # User's full name
    username: str             # Unique username for login
    email: str                # Unique email address
    hashed_password: str      # Bcrypt hashed password
    
    # Relationships
    posts: List[Post]         # 1:N relationship with posts
    votes: List[Vote]         # 1:N relationship with votes
    comments: List[Comment]   # 1:N relationship with comments
```

### Post Model

```python
class Post(Base):
    __tablename__ = "posts"
    
    post_id: int              # Primary key, auto-increment
    user_id: int              # Foreign key to users
    title: str                # Post title (max 200 chars)
    post: str                 # Post content (max 50000 chars)
    content_type: str         # Type: article, tutorial, news, etc.
    created_at: datetime      # Server timestamp
    
    # Relationships
    users: User               # N:1 relationship with user
    votes: List[Vote]         # 1:N relationship with votes
    comments: List[Comment]   # 1:N relationship with comments
```

### Comment Model

```python
class Comment(Base):
    __tablename__ = "comments"
    
    comments_id: UUID         # Primary key, auto-generated UUID
    post_id: int              # Foreign key to posts
    user_id: int              # Foreign key to users
    comment: str              # Comment text (max 256 chars)
    created_at: datetime      # Server timestamp
    
    # Relationships
    users: User               # N:1 relationship with user
    posts: Post               # N:1 relationship with post
```

### Vote Model

```python
class Vote(Base):
    __tablename__ = "votes"
    
    upvote_id: UUID           # Primary key, auto-generated UUID
    post_id: int              # Foreign key to posts
    user_id: int              # Foreign key to users
    vote: int                 # 1 for upvote, -1 for downvote
    
    # Relationships
    users: User               # N:1 relationship with user
    posts: Post               # N:1 relationship with post
```

**Cascade Behavior:**
- Deleting a user deletes all their posts, votes, and comments
- Deleting a post deletes all associated votes and comments

---

## 🗃️ Pydantic Schemas (Data Validation)

### User Registration Schema

```python
class UserIn(BaseModel):
    name: str
    email: EmailStr          # Validates email format
    username: str
    password: str            # Must be 8+ chars with uppercase, lowercase, digit
```

### Post Creation Schema

```python
class PostCreate(BaseModel):
    title: str
    post: str
    content_type: str
```

### Post Response Schema

```python
class PostShow(BaseModel):
    post_id: int
    username: str
    content_type: str
    title: str
    post: str
    created_at: datetime
```

### Comment Schemas

```python
class CommentsIn(BaseModel):
    comment: str             # 1-500 characters

class CommentsOut(BaseModel):
    user_id: int
    post_id: int
    comments_id: UUID
    comment: str
    created_at: datetime
```

### Vote Schema

```python
class VoteCreate(BaseModel):
    vote: Literal[1, -1]     # Only 1 (upvote) or -1 (downvote)
```

---

## 🐳 Docker & Docker Compose

### Docker Setup

The `docker-compose.yml` orchestrates:
- **web**: FastAPI application server
- **db**: PostgreSQL database
- **pgadmin**: pgAdmin for database administration

### Build and Run

```bash
# Build images and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs in real-time
docker-compose logs -f web

# View specific service logs
docker-compose logs -f db
```

### Database Access

**pgAdmin (Database Admin UI):**
- URL: `http://localhost:5050`
- Default Email: `admin@admin.com`
- Default Password: `admin`

**PostgreSQL Connection:**
- Host: `db` (from within containers) or `localhost` (from host)
- Port: `5432`
- Username: `smartblog_user`
- Password: `smartblog_pass`
- Database: `smartblog`

### Essential Docker Commands

```bash
# Stop all services
docker-compose down

# Stop and remove all volumes (wipes data)
docker-compose down -v

# Run a single command in container
docker-compose exec web alembic upgrade head

# Access container bash shell
docker-compose exec web bash

# Rebuild a specific service
docker-compose build web

# View network
docker network ls
docker network inspect smartblog_default
```

---

## 🗂️ Database Migrations with Alembic

Alembic manages database schema changes in a version-controlled, safe manner.

### Generate a New Migration

When you modify SQLAlchemy models, create a migration:

```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "Add new column to posts table"

# This creates a file in alembic/versions/
```

### Apply Migrations

```bash
# Apply all pending migrations to latest
alembic upgrade head

# Apply a specific number of migrations
alembic upgrade +2

# Apply to a specific version
alembic upgrade abc123def

# Downgrade to previous version
alembic downgrade -1

# View all migrations
alembic history
```

### Migration Files

Migrations are stored in `alembic/versions/` with structure:

```python
def upgrade() -> None:
    # Forward migration: apply changes
    op.add_column('posts', sa.Column('new_field', sa.String()))

def downgrade() -> None:
    # Backward migration: revert changes
    op.drop_column('posts', 'new_field')
```

### Best Practices

- **Always review auto-generated migrations** before committing
- **Test migrations** on a copy of production data
- **Include migration files in version control**
- **Never manually modify production database**
- **Document complex migrations** with comments

### Docker Migrations

```bash
# Run migrations inside Docker container
docker-compose exec web alembic upgrade head

# Generate migration inside Docker
docker-compose exec web alembic revision --autogenerate -m "Your message"
```

---

## 💻 Development Workflow

### Local Development

1. **Start development server with auto-reload**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Code changes are reflected automatically** due to hot reload

3. **Make database model changes**
   ```bash
   # Modify app/models/models.py
   alembic revision --autogenerate -m "Description"
   alembic upgrade head
   ```

4. **Test API endpoints**
   - Swagger UI: `http://127.0.0.1:8000/api/v1/docs`
   - Use cURL/Postman/ThunderClient
   - Check logs in console

5. **Debug issues**
   ```bash
   # Enable debug mode in .env
   DEBUG=True
   
   # Add print statements for debugging
   # Or use IDE debugger with breakpoints
   ```

### Docker Development Workflow

1. **Start containerized environment**
   ```bash
   docker-compose up --build
   ```

2. **Apply migrations**
   ```bash
   docker-compose exec web alembic upgrade head
   ```

3. **Access API**
   ```
   http://127.0.0.1:8000/api/v1/docs
   ```

4. **Code changes** are reflected via volume mounting

5. **View logs**
   ```bash
   docker-compose logs -f web
   docker-compose logs -f db
   ```

6. **Database operations**
   ```bash
   # Create new migration
   docker-compose exec web alembic revision --autogenerate -m "message"
   
   # Apply migrations
   docker-compose exec web alembic upgrade head
   ```

7. **Clean up**
   ```bash
   docker-compose down -v  # Removes volumes
   ```

### Testing the API

**Using cURL:**
```bash
# Register
curl -X POST http://127.0.0.1:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","username":"test","password":"Test123"}'

# Login
curl -X POST http://127.0.0.1:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123"}'

# Create post
curl -X POST http://127.0.0.1:8000/api/v1/posts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content_type":"article","post":"Content"}'
```

**Using Swagger UI:**
1. Visit `http://127.0.0.1:8000/api/v1/docs`
2. Click "Authorize" and enter your access token
3. Try endpoints directly from UI

---

## 🎓 Learning Objectives & Project Goals

This project demonstrates real-world backend engineering practices:

### Authentication & Security
- Implementing JWT with access and refresh tokens
- Secure password hashing using bcrypt
- Token validation and expiration handling
- Authorization checks for protected resources
- Strong password validation requirements

### Social Features & Database Design
- One-to-many relationships (User → Posts, Comments, Votes)
- Many-to-one relationships (Posts → User)
- Cascade deletes for data consistency
- Vote toggle logic for better UX
- Comment creation with ownership validation

### API Design & RESTful Architecture
- HTTP method semantics (POST, GET, PATCH, DELETE)
- Proper status codes (201 Created, 404 Not Found, 403 Forbidden)
- Request/response validation with Pydantic
- API versioning for backward compatibility
- Query parameters for filtering (content_type)

### Database Management
- SQLAlchemy ORM for type-safe database operations
- Alembic for version-controlled migrations
- Database schema design and relationships
- Session management and connection pooling
- Transaction handling (commit/rollback)

### Software Architecture
- Layered architecture (routers → services → database)
- Separation of concerns (models, schemas, routers)
- Dependency injection with FastAPI
- Configuration management with environment variables
- Logging for debugging and monitoring

### DevOps & Deployment
- Docker containerization and composition
- Multi-service orchestration
- Environment-based configuration
- Health check endpoints for monitoring
- Local vs. containerized development

### Code Quality & Best Practices
- Meaningful error messages and logging
- Input validation and sanitization
- Ownership verification for data operations
- Clean code organization and naming
- SOLID principles applied to code structure

---

## 📋 Future Improvements

These enhancements align with real-world production requirements:

### Testing & Quality Assurance
- **Unit Tests**
  - Test password hashing and verification
  - Test token generation and validation
  - Test vote toggle logic
  - Use `pytest` with 80%+ coverage target
  
- **Integration Tests**
  - Test complete user flows (register → login → post → comment → vote)
  - Test authorization for owned resources
  - Test cascade deletes
  - Test database rollbacks
  
- **Code Quality**
  - Pre-commit hooks (black, flake8, mypy)
  - GitHub Actions CI/CD pipeline
  - Automated testing on pull requests

### Advanced Features
- **Post Features**
  - Rich text editing with Markdown support
  - Post drafts and scheduling
  - Categories and tags system
  - Search functionality with full-text search
  - Post trending/popular endpoint
  
- **Social Features**
  - Follow/unfollow users
  - User profiles with post count, follower count
  - Nested comments (replies to comments)
  - Comment voting
  - User mentions with @username notifications
  - Bookmark posts feature
  
- **Engagement**
  - Email notifications for comments and upvotes
  - User feed showing followed users' posts
  - Trending posts based on engagement
  - Leaderboard for top contributors

### Security Enhancements
- **Rate Limiting**
  - Per-user rate limits on API endpoints
  - DDoS protection
  - Prevent brute force attacks on login
  
- **Advanced Auth**
  - Two-factor authentication (2FA)
  - OAuth2 with Google/GitHub login
  - Email verification on registration
  - Password reset functionality
  
- **Data Protection**
  - HTTPS/SSL enforcement in production
  - CORS configuration for web clients
  - Input sanitization and SQL injection prevention
  - Audit logging for sensitive operations

### Performance Optimization
- **Caching**
  - Redis caching for frequently accessed posts
  - Cache invalidation strategies
  - User session caching
  
- **Database Optimization**
  - Query optimization with proper indexing
  - Lazy loading vs eager loading strategies
  - Pagination for large result sets
  - Aggregation queries for vote counts
  
- **Async Operations**
  - Async database queries with async SQLAlchemy
  - Background tasks (Celery) for notifications
  - Async file uploads for post images
  - Scheduled tasks (APScheduler)

### Observability & Monitoring
- **Logging**
  - Structured logging (Python logging or Loguru)
  - Log aggregation (ELK stack, CloudWatch)
  - Correlation IDs for request tracing
  
- **Metrics**
  - Application metrics with Prometheus
  - Request latency monitoring
  - Database query performance metrics
  - Error rate tracking
  
- **Tracing**
  - Distributed tracing with Jaeger
  - Request flow visualization
  - Performance bottleneck identification

### Deployment & Infrastructure
- **Containerization**
  - Multi-stage Docker builds for smaller images
  - Docker registry integration
  - Container security scanning
  
- **Orchestration**
  - Kubernetes manifests for scaling
  - Helm charts for deployment management
  - ConfigMaps for configuration
  - Secrets management
  
- **Infrastructure as Code**
  - Terraform for AWS/cloud infrastructure
  - CI/CD with GitHub Actions, GitLab CI, or Jenkins
  - Automated testing before deployment
  - Blue-green deployments

### API Enhancements
- **Pagination**
  - Offset/limit pagination
  - Cursor-based pagination for large datasets
  - Default pagination size enforcement
  
- **Filtering & Sorting**
  - Advanced filtering (date range, content type)
  - Multiple sort options
  - Complex queries support
  
- **Response Format**
  - Consistent error response format
  - Response metadata (total count, pagination info)
  - API versioning headers

---

## 🤝 Contributing

Found a bug or have a suggestion? Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Author

**Vinayak Dewoolkar**

- GitHub: [@Credence1289](https://github.com/Credence1289)
- Repository: [Smart-Blog-FastAPI](https://github.com/Credence1289/Smart-Blog-FastAPI)

---

## 🙏 Acknowledgments

Built with these amazing open-source technologies:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Python-JWT](https://github.com/jpadilla/pyjwt) - JWT implementation
- [Bcrypt](https://github.com/pyca/bcrypt) - Password hashing
- [Docker](https://www.docker.com/) - Containerization
- [PostgreSQL](https://www.postgresql.org/) - Production database


1. Check the [API Documentation]([http://127.0.0.1:8000/api/v1/docs](https://smart-blog-fastapi.onrender.com))
2. Review the cURL examples above
3. Open an issue on GitHub
4. Check Docker Compose setup if running containerized

👨‍💻 Author
Vinayak Dewoolkar
Backend Developer | FastAPI | API Architecture

# Project Goal

This project was built to strengthen backend development skills by implementing authentication, database management, API structuring, and scalable FastAPI architecture in a real-world style project.
