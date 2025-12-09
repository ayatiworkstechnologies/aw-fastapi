from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.api.routes_auth import router as auth_router
from app.api.routes_roles import router as roles_router
from app.api.routes_users import router as users_router
from app.seed.init_data import seed_initial_data

app = FastAPI(title="Simple AW Admin API")

# ------------------------------
# CORS Configuration
# ------------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://54.147.145.228",
    "https://54.147.145.228",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Startup
# ------------------------------
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()

# ------------------------------
# Routes
# ------------------------------
app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(users_router)
