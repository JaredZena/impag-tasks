from functools import wraps
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from config import google_client_id, allowed_emails


def require_auth(f):
    """Decorator that verifies Google OAuth token and checks email whitelist."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"detail": "Missing or invalid authorization header"}), 401

        token = auth_header.split("Bearer ")[1]

        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), google_client_id
            )
        except Exception:
            return jsonify({"detail": "Invalid or expired token"}), 401

        email = idinfo.get("email", "").lower()
        if email not in allowed_emails:
            return jsonify({"detail": "Email not authorized"}), 403

        request.user_info = {
            "email": email,
            "name": idinfo.get("name", ""),
            "picture": idinfo.get("picture", ""),
            "user_id": idinfo.get("sub", ""),
        }
        return f(*args, **kwargs)
    return decorated
