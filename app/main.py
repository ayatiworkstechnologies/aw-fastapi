from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.api.routes_auth import router as auth_router
from app.api.routes_roles import router as roles_router
from app.api.routes_users import router as users_router
from app.seed.init_data import seed_initial_data

app = FastAPI(title="Simple AW Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()

# include routers
app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(users_router)
