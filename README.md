Project overview

Small FastAPI backend for AW Admin (users, roles, blogs, authors, categories).
Features:

SQLAlchemy models + DB seeding

JWT auth

Blog/Author/Category CRUD

Sections stored as JSON per blog

Uses a .env style DATABASE_URL and other config

Quick folder structure (recommended single-file view)
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
├─ README.md   <-- (this file)
└─ venv/


Adjust names/paths if your project differs. The venv/ folder should be excluded from git.

.env example (create .env in project root)
# .env.example -> copy to .env and edit
DATABASE_URL=mysql+pymysql://awadmin:ayati123@localhost:3306/aw_admin?charset=utf8mb4
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_HOURS=12

requirements.txt (minimum)
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


Install with pip install -r requirements.txt.

Local development: step-by-step
1. Clone & cd
git clone <repo-url>
cd aw-fastapi

2. Create virtualenv & activate
macOS / Linux
python3 -m venv venv
source venv/bin/activate

Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
# or: venv\Scripts\activate

3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

4. Create .env from example
cp .env.example .env
# edit .env and set real DB password + SECRET_KEY

5. Create MySQL database (local or remote)

Use MySQL client or phpMyAdmin:

CREATE DATABASE aw_admin CHARACTER SET utf8mb4;
CREATE USER 'awadmin'@'localhost' IDENTIFIED BY 'ayati123';
GRANT ALL PRIVILEGES ON aw_admin.* TO 'awadmin'@'localhost';
FLUSH PRIVILEGES;

6. Run the app (dev)
# ensure venv is active
uvicorn app.main:app --reload


Open docs:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

The app will run startup tasks that create tables and seed initial data (roles, admin user, sample blog/author/category) if seed/init_data.py is present.

Running against a live (remote) DB

Recommended (secure): SSH Tunnel

From your local machine:

ssh -i path/to/key.pem -L 3307:localhost:3306 ubuntu@EC2_IP


Then use in local .env:

DATABASE_URL=mysql+pymysql://awadmin:ayati123@localhost:3307/aw_admin?charset=utf8mb4


Not recommended: open port 3306 to the world. If you must, restrict security group to your IP only.

Production deployment (basic)
Option A — systemd + uvicorn + Apache (reverse proxy)

Create systemd service file /etc/systemd/system/fastapi.service:

[Unit]
Description=FastAPI app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/aw-fastapi
ExecStart=/var/www/aw-fastapi/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target


sudo systemctl daemon-reload && sudo systemctl enable fastapi && sudo systemctl start fastapi

Configure Apache (or Nginx) reverse proxy to http://127.0.0.1:8000/. Example Apache vhost:

<VirtualHost *:80>
    ServerName your-domain.com
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>

Option B — use Docker (recommended for portability)

I can give a Dockerfile + docker-compose.yml if you want.

DB migrations

This project uses SQLAlchemy Base.metadata.create_all() by default for dev. For production, use Alembic:

pip install alembic
alembic init alembic
# configure env.py to use your SQLALCHEMY DATABASE_URL, generate migrations, apply

Seed data

If present, app/seed/init_data.py runs on startup and seeds:

roles (admin, employee, hr, manager)

super admin user (username & emp_id created)

sample authors, categories, and a sample blog

If you change models, re-run DB or run migration.

Using the API (endpoints summary)

Auth:

POST /api/auth/login (email + password) → JWT token

Users:

GET /api/users

POST /api/users

GET /api/users/{id}

PUT /api/users/{id}

Roles:

GET /api/roles

POST /api/roles

Blogs:

GET /api/blogs (filters: ?skip=0&limit=10&category=slug&author=slug&q=text)

GET /api/blogs/{slug}

POST /api/blogs (admin only recommended)

PUT /api/blogs/{slug}

DELETE /api/blogs/{slug}

Authors:

GET /api/authors, POST /api/authors, PUT /api/authors/{id}, DELETE /api/authors/{id}

Categories:

GET /api/categories, POST /api/categories, PUT /api/categories/{id}, DELETE /api/categories/{id}

Use Swagger at /docs for full spec and example bodies.

Example create-blog JSON
{
  "title": "Why Chennai Brands Grow Faster",
  "slug": "why-chennai-brands-grow-faster",
  "deck": "Five reasons local agencies outperform",
  "banner_img": "https://.../banner.jpg",
  "banner_title": "Why Chennai Brands Grow Faster",
  "author_id": 1,
  "category_id": 1,
  "read_mins": 8,
  "sections": [
    { "title": "Intro", "text": "Intro text", "order": 1 },
    { "title": "Reason 1", "text": "Details...", "img": "https://.../img1.jpg", "order": 2 }
  ]
}