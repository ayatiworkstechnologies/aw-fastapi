# AW Admin Backend (FastAPI + MySQL)

This is the backend API for the **AW Admin Console**.  
It provides:

- User management (CRUD)
- Role management (CRUD)
- JWT-based login
- MySQL persistence via SQLAlchemy
- Simple seeding: default roles + one Super Admin

The backend is designed to work with the Next.js admin panel at `http://localhost:3000` (or similar).

---

## 1. Tech Stack

- **Language:** Python 3.11+
- **Web Framework:** FastAPI
- **Server:** Uvicorn (ASGI)
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Auth:** JWT (JSON Web Tokens)
- **Password Hashing:** Passlib with `pbkdf2_sha256`
- **CORS:** Enabled for `http://localhost:3000` by default

---

## 2. Folder Structure

For the simple version, backend is a single file:

```bash
backend/
  main.py        # FastAPI app with all routes, models, schemas, seeding
  README.md      # (this file)


3. Requirements

Python 3.11+

MySQL server running locally (or remote)
Example DB:

host: localhost

user: root

password: ayati

database: aw_admin

Python Dependencies

Install with pip (from backend/ folder):

pip install fastapi uvicorn "sqlalchemy<2.0" pymysql passlib PyJWT python-dotenv


Note:

We use pbkdf2_sha256 (from Passlib) instead of bcrypt to avoid Windows/bcrypt issues.

pymysql is used as the MySQL driver.

4. Configuration

The backend uses these main settings:

DATABASE_URL – SQLAlchemy connection string

SECRET_KEY – for signing JWT tokens

ALGORITHM – JWT algorithm (default: HS256)

ACCESS_TOKEN_EXPIRE_HOURS – token lifetime (default: 12 hours)

4.1 Default values in main.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:ayati@localhost:3306/aw_admin?charset=utf8mb4",
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12


You can override them with environment variables.

4.2 Optional .env (if you use python-dotenv)

Create a .env file in backend/:

DATABASE_URL=mysql+pymysql://root:ayati@localhost:3306/aw_admin?charset=utf8mb4
SECRET_KEY=some-super-secret-key-change-in-prod


Make sure you load .env in main.py if you want (using python-dotenv), but the provided code works fine with pure os.getenv.

5. Database Setup

Ensure MySQL is running.

Create the database:

CREATE DATABASE aw_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


The tables are created automatically on startup via:

Base.metadata.create_all(bind=engine)


On first run, the app seeds:

Default roles: admin, employee, hr, manager

One Super Admin user:

Email: admin@example.com

Password: admin123

Role: admin

Seeding happens in seed_initial_data() during the FastAPI startup event.

6. Running the Backend

From the backend/ folder:

6.1 Development
uvicorn main:app --reload


API base URL: http://127.0.0.1:8000

API endpoints start with /api/...

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

6.2 Main block (alternate)

You can also use:

python main.py


because main.py includes:

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

7. CORS

CORS is configured to allow the Next.js frontend (http://localhost:3000) by default:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Change allow_origins if your frontend runs on a different URL.

8. Data Model
8.1 Role

Database: roles table

Fields:

id (int, PK)

name (string, unique, required)

description (string, optional)

8.2 User

Database: users table

Fields:

id (int, PK)

full_name (string, required)

email (string, unique, required)

password_hash (string, required, hashed with pbkdf2_sha256)

is_active (bool, default true)

role_id (FK → roles.id, required)

Methods on User:

set_password(password: str) → hashes and stores in password_hash

check_password(password: str) → verifies a plaintext password

9. Authentication
9.1 Login flow

Endpoint: POST /api/auth/login

Body:

{
  "email": "admin@example.com",
  "password": "admin123"
}


Response:

{
  "token": "JWT_TOKEN_HERE",
  "user": {
    "id": 1,
    "full_name": "Super Admin",
    "email": "admin@example.com",
    "is_active": true,
    "role": {
      "id": 1,
      "name": "admin",
      "description": "Full access"
    }
  }
}


The frontend:

Saves token (e.g., in localStorage under aw_admin_token)

Saves user (e.g., under aw_admin_user)

Sends Authorization: Bearer <token> for any calls where you want to restrict access (future enhancement).

9.2 JWT details

Function create_access_token(user) builds a payload:

payload = {
    "sub": str(user.id),
    "email": user.email,
    "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
}


Signed with SECRET_KEY and ALGORITHM.

10. API Endpoints

Base URL: http://127.0.0.1:8000/api

10.1 Auth
POST /api/auth/login

Login and get token + user object.

Body:

{
  "email": "admin@example.com",
  "password": "admin123"
}


Response: TokenResponse

{
  "token": "JWT_TOKEN",
  "user": {
    "id": 1,
    "full_name": "Super Admin",
    "email": "admin@example.com",
    "is_active": true,
    "role": {
      "id": 1,
      "name": "admin",
      "description": "Full access"
    }
  }
}


Note: In the current simple version, other endpoints are not using auth guards yet.
You can add role-based checks later if needed.

10.2 Roles
GET /api/roles

List all roles.

Response:

[
  {
    "id": 1,
    "name": "admin",
    "description": "Full access"
  },
  {
    "id": 2,
    "name": "employee",
    "description": "Standard employee"
  }
]

POST /api/roles

Create a new role.

Body:

{
  "name": "support",
  "description": "Customer support staff"
}


Response:

{
  "id": 5,
  "name": "support",
  "description": "Customer support staff"
}


If a role with the same name exists, returns 400:

{
  "detail": "Role already exists"
}

PUT /api/roles/{role_id}

Update an existing role (name / description).

Body (partial):

{
  "name": "manager",
  "description": "Team manager – updated"
}


Response:

{
  "id": 3,
  "name": "manager",
  "description": "Team manager – updated"
}

10.3 Users
GET /api/users

List all users.

Response:

[
  {
    "id": 1,
    "full_name": "Super Admin",
    "email": "admin@example.com",
    "is_active": true,
    "role": {
      "id": 1,
      "name": "admin",
      "description": "Full access"
    }
  }
]

POST /api/users

Create a new user.

Body:

{
  "full_name": "Test User",
  "email": "test@example.com",
  "password": "test123",
  "role_id": 2
}


Response:

{
  "id": 2,
  "full_name": "Test User",
  "email": "test@example.com",
  "is_active": true,
  "role": {
    "id": 2,
    "name": "employee",
    "description": "Standard employee"
  }
}


If email already in use → 400:

{
  "detail": "Email already in use"
}

GET /api/users/{user_id}

Get a single user by ID.

Response:

{
  "id": 2,
  "full_name": "Test User",
  "email": "test@example.com",
  "is_active": true,
  "role": {
    "id": 2,
    "name": "employee",
    "description": "Standard employee"
  }
}

PUT /api/users/{user_id}

Partial update of a user.

You can send any combination of:

full_name

email

password (new password)

is_active

role_id

Examples:

Update profile info:

{
  "full_name": "New Name",
  "email": "new-email@example.com"
}


Change role only:

{
  "role_id": 3
}


Change password only:

{
  "password": "newStrongPassword123"
}


Deactivate user:

{
  "is_active": false
}


Response:

{
  "id": 2,
  "full_name": "New Name",
  "email": "new-email@example.com",
  "is_active": false,
  "role": {
    "id": 3,
    "name": "manager",
    "description": "Team manager"
  }