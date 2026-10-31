import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if not DATABASE_URL or not TURSO_AUTH_TOKEN:
    raise ValueError(
        "Missing TURSO_DATABASE_URL or TURSO_AUTH_TOKEN in environment"
    )

engine = create_engine(
    f"sqlite+libsql://{DATABASE_URL}?secure=true",
    connect_args={"auth_token": TURSO_AUTH_TOKEN},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
