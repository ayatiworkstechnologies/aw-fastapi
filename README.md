# AW FastAPI – Admin Backend

A small, clean **FastAPI backend** powering the AW Admin panel.  
Manages **users, roles, blogs, authors, and categories** with JWT-based authentication.

---

## ✨ Features

- FastAPI + SQLAlchemy
- MySQL support (via PyMySQL)
- JWT authentication
- User & role management
- Blog / Author / Category CRUD
- Blog sections stored as JSON
- Database seeding on startup
- Environment-based configuration (`.env`)
- Swagger & ReDoc auto-generated APIs

---

## 📁 Project Structure

```text
aw-fastapi/
├─ app/
│  ├─ api/
│  │  ├─ routes_auth.py
│  │  ├─ routes_users.py
│  │  ├─ routes_roles.py
│  │  ├─ routes_blogs.py
│  │  ├─ routes_authors.py
│  │  └─ routes_categories.py
│  ├─ schemas/
│  │  ├─ user.py
│  │  ├─ role.py
│  │  ├─ blog.py
│  │  ├─ author.py
│  │  └─ category.py
│  ├─ models/
│  │  ├─ user.py
│  │  ├─ role.py
│  │  ├─ blog.py
│  │  ├─ author.py
│  │  └─ category.py
│  ├─ db/
│  │  ├─ base.py
│  │  └─ session.py
│  ├─ utils/
│  │  ├─ slugify.py
│  │  └─ formatting.py
│  ├─ seed/
│  │  └─ init_data.py
│  └─ main.py
├─ requirements.txt
├─ .env.example
├─ install.md
├─ README.md
└─ venv/            # excluded from git


## ⚙️ Environment Variables

Create a .env file in the project root.

``` bash
DATABASE_URL=mysql+pymysql://awadmin:ayati123@localhost:3306/aw_admin?charset=utf8mb4
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_HOURS=12
```

## 📦 Requirements

requirements.txt (minimum)

```bash 
fastapi
uvicorn
python-dotenv
sqlalchemy
pymysql
passlib
PyJWT
email-validator
python-multipart
markdown
bleach
cryptography

```

## Install dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Local Development Setup

## 1. Clone the repository

```bash
git clone <repo-url>
cd aw-fastapi
```

## 2. Create & activate virtual environment

```bash
##macOS / Linux

python3 -m venv venv
source venv/bin/activate

```

```bash

##Windows (PowerShell)

python -m venv venv
venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Create .env

```bash
cp .env.example .env
```

Edit values as needed.

## 5. Create MySQL Database

```bash
CREATE DATABASE aw_admin CHARACTER SET utf8mb4;
CREATE USER 'awadmin'@'localhost' IDENTIFIED BY 'ayati123';
GRANT ALL PRIVILEGES ON aw_admin.* TO 'awadmin'@'localhost';
FLUSH PRIVILEGES;
```

## 6. Run the application

```bash
uvicorn app.main:app --reload
```

## Access API documentation

```bash
Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc
```

On startup, the app auto-creates tables and seeds initial data if seed/init_data.py exists.

## 🌍 Using a Remote Database (Recommended)

SSH Tunnel (Secure)
ssh -i key.pem -L 3307:localhost:3306 ubuntu@EC2_IP

Update .env:

DATABASE_URL=mysql+pymysql://awadmin:ayati123@localhost:3307/aw_admin?charset=utf8mb4

Avoid opening port 3306 publicly