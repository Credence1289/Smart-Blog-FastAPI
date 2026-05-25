# Smart Blog API

A modular blogging backend API built using **FastAPI** with JWT Authentication, SQLAlchemy ORM, API versioning, and clean architecture principles.

Designed as a portfolio-ready backend engineering project for learning scalable API development and modern backend structuring.

---

# Features

* JWT Authentication
* User Registration & Login
* CRUD Operations for Blog Posts
* API Versioning using `/api/v1`
* SQLAlchemy ORM Integration
* Modular Backend Architecture
* Environment Variable Management using `.env`
* Swagger/OpenAPI Documentation
* PostgreSQL-ready Structure

---

# Tech Stack

| Technology | Purpose              |
| ---------- | -------------------- |
| FastAPI    | Backend Framework    |
| SQLAlchemy | ORM                  |
| Postgresql | Database             |
| JWT        | Authentication       |
| Pydantic   | Data Validation      |
| Uvicorn    | ASGI Server          |
| Python     | Programming Language |

---

# Project Structure

```txt
SmartBlog/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── routers/
│   │           ├── auth.py
│   │           └── posts.py
│   │
│   ├── core/
│   │   ├── gate.py
│   │   ├── hashing.py
│   │   └── token.py
│   │
│   ├── db/
│   │   ├── create_table.py
│   │   ├── dbengine.py
│   │   └── session.py
│   │
│   ├── models/
│   │   └── models.py
│   │
│   ├── schemas/
│   │   ├── posts_schema.py
│   │   └── users_schema.py
│   │
│   └── main.py
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Credence1289/Smart-Blog-FastAPI.git
```

Move into project directory:

```bash
cd Smart-Blog-FastAPI
```

Create virtual environment:

```bash
python -m venv myenv
```

Activate virtual environment:

### Windows

```bash
myenv\Scripts\activate
```

### Linux/Mac

```bash
source myenv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Setup

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=sqlite:///./smartblog.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# Run Locally

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Server will run on:

```txt
http://127.0.0.1:8000
```

---

# API Documentation

Swagger UI:

```txt
http://127.0.0.1:8000/api/v1/docs
```


Because modern backend developers apparently require auto-generated documentation to remember what they themselves built three hours earlier.

---

# Example API Endpoints

| Method | Endpoint             | Description   |
| ------ | -------------------- | ------------- |
| POST   | `/api/v1/register`   | Register User |
| POST   | `/api/v1/login`      | Login User    |
| GET    | `/api/v1/posts`      | Get All Posts |
| POST   | `/api/v1/posts`      | Create Post   |
| PUT    | `/api/v1/posts/{id}` | Update Post   |
| DELETE | `/api/v1/posts/{id}` | Delete Post   |

---

# Sample cURL Request

## Register User

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/register" \
-H "Content-Type: application/json" \
-d "{\"username\":\"vinayak\",\"email\":\"vinayak@example.com\",\"password\":\"password123\"}"
```

---

# Deployment (Optional)

This project can be deployed on:

* Render
* Railway
* Docker
* VPS Servers

Example Render Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

---

# Future Improvements

* Alembic Database Migrations
* Docker Support
* Pagination
* Async Database Support
* Unit Testing
* CI/CD Integration
* Rate Limiting
* Role-Based Access Control

---

# Author

**Vinayak Dewoolkar**

GitHub Repository:
https://github.com/Credence1289/Smart-Blog-FastAPI

---

# Project Goal

This project was built to strengthen backend development skills by implementing authentication, database management, API structuring, and scalable FastAPI architecture in a real-world style project.
