import os

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        # "mysql+pymysql://awadmin:ayati123@localhost:3306/aw_admin?charset=utf8mb4"
        "mysql+pymysql://root:ayati@localhost:3306/aw_admin?charset=utf8mb4"
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 12

settings = Settings()
