import json
import sqlite3
from pathlib import Path

import bcrypt

from app.core.config import get_settings

# Demo project, synthetic users -- one shared password is fine here and keeps
# the login demo simple. Never do this for real accounts.
DEMO_PASSWORD = "pkc123"

USERS = [
    ("ravi@pkc.com", "Ravi Kumar", ["employee"]),
    ("neha@pkc.com", "Neha Gupta", ["hr_manager"]),
    ("arjun@pkc.com", "Arjun Rao", ["finance_analyst"]),
    ("divya@pkc.com", "Divya Menon", ["sales_lead"]),
    ("karan@pkc.com", "Karan Malhotra", ["engineering_lead"]),
    ("meera@pkc.com", "Meera Iyer", ["c_level"]),
]


def seed_users() -> None:
    settings = get_settings()
    Path(settings.ledger_db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.ledger_db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            roles TEXT NOT NULL,
            daily_token_budget INTEGER DEFAULT 50000,
            is_active BOOLEAN DEFAULT 1
        )
        """
    )
    password_hash = bcrypt.hashpw(DEMO_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    for email, display_name, roles in USERS:
        conn.execute(
            "INSERT OR IGNORE INTO users (email, display_name, password_hash, roles) VALUES (?, ?, ?, ?)",
            (email, display_name, password_hash, json.dumps(roles)),
        )
    conn.commit()
    conn.close()
    print(f"Seeded {len(USERS)} users into {settings.ledger_db_path}. Demo password for all: '{DEMO_PASSWORD}'")


if __name__ == "__main__":
    seed_users()
