from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    roles: list[str]
    display_name: str


class CurrentUser(BaseModel):
    email: str
    display_name: str
    roles: list[str]


def get_db() -> sqlite3.Connection:
    settings = get_settings()
    Path(settings.ledger_db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.ledger_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_access_token(email: str, roles: list[str]) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/api/auth/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1", (body.email,)
        ).fetchone()
    finally:
        conn.close()

    # Same "invalid credentials" message whether the email doesn't exist or the
    # password is wrong -- distinguishing the two would tell an attacker which
    # emails are valid accounts.
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    if row is None:
        raise invalid
    if not bcrypt.checkpw(body.password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        raise invalid

    roles = json.loads(row["roles"])
    token = create_access_token(row["email"], roles)
    return LoginResponse(access_token=token, roles=roles, display_name=row["display_name"])


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1", (payload["sub"],)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")

    return CurrentUser(email=row["email"], display_name=row["display_name"], roles=json.loads(row["roles"]))
