import os
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.getenv("TURSO_DATABASE_URL")
token = os.getenv("TURSO_AUTH_TOKEN")

if not url or not token:
    raise ValueError("Missing Turso configuration")

# Convert libsql:// to sqlite+libsql://
url = url.replace("libsql://", "sqlite+libsql://", 1)

engine = create_engine(
    url,
    connect_args={"auth_token": token}
)

test_id = str(uuid4())

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS _connection_test (
            id TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """))

    conn.execute(
        text("INSERT INTO _connection_test (id, value) VALUES (:id, :value)"),
        {"id": test_id, "value": "Turso is working"}
    )

    result = conn.execute(
        text("SELECT value FROM _connection_test WHERE id = :id"),
        {"id": test_id}
    ).scalar_one()

    print("Database read/write successful:", result)

    conn.execute(
        text("DELETE FROM _connection_test WHERE id = :id"),
        {"id": test_id}
    )

engine.dispose()