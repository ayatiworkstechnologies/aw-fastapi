# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, SessionLocal, Base
from . import models
from .routers import auth, users, roles
from .core.security import get_password_hash


app = FastAPI(title="AW Admin API")

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # adjust if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- DB + seed -----
def seed_initial_data(db: Session):
    # Seed roles
    if db.query(models.Role).count() == 0:
        default_roles = [
            ("admin", "Full access"),
            ("employee", "Standard employee"),
            ("hr", "HR staff"),
            ("manager", "Team manager"),
        ]
        for name, desc in default_roles:
            db.add(models.Role(name=name, description=desc))
        db.commit()

    # Seed super admin
    if db.query(models.User).count() == 0:
        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        if admin_role:
            admin = models.User(
                full_name="Super Admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                is_active=True,
                role=admin_role,
            )
            db.add(admin)
            db.commit()


@app.on_event("startup")
def on_startup():
    # create tables
    Base.metadata.create_all(bind=engine)

    # seed data
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()


# ----- Routers -----
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)


# ----- Local dev run -----
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
