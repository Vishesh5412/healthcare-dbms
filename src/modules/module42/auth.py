import os
import datetime
import bcrypt
import jwt
from streamlit_cookies_controller import CookieController
from database import get_users_collection

JWT_SECRET    = os.getenv("JWT_SECRET", "clinical-summary-dev-secret-key-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXP_HOURS = 24
COOKIE_NAME   = "auth_token"

_controller = None

def get_controller():
    global _controller
    if _controller is None:
        _controller = CookieController()
    return _controller

def verify_user(username: str, password: str):
    user = get_users_collection().find_one({"username": username})
    if user is None:
        return None
    stored = user["password"]
    if isinstance(stored, str):
        stored = stored.encode("utf-8")
    return user if bcrypt.checkpw(password.encode("utf-8"), stored) else None

def create_jwt(user: dict) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "user_id":   str(user["_id"]),
        "username":  user["username"],
        "role":      user.get("role", "Clinical"),
        "full_name": user.get("full_name", ""),
        "exp": now + datetime.timedelta(hours=JWT_EXP_HOURS),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_current_user() -> dict | None:
    controller = get_controller()
    token = controller.get(COOKIE_NAME)
    return decode_jwt(token) if token else None

def set_auth_cookie(token: str):
    controller = get_controller()
    controller.set(COOKIE_NAME, token, max_age=JWT_EXP_HOURS * 3600, path="/")

def remove_auth_cookie():
    controller = get_controller()
    controller.set(
        COOKIE_NAME,
        "",
        max_age=0,   # expire immediately
        path="/"
    )