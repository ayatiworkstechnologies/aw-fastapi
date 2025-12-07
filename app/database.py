# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Change this if your DB user/pass are different
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:ruban@localhost:3306/aw_admin?charset=utf8mb4",
    #             ^^^^
    # empty password for root. If you use a password, put it here.
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency to get a DB session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
